import pytest
import asyncio
import json
from unittest.mock import (
    AsyncMock,
    Mock,
    patch,
)

from eth_utils import (
    to_bytes,
)
from websockets import (
    ConnectionClosed,
    ConnectionClosedOK,
)
from websockets.protocol import (
    State,
)

from web3 import (
    AsyncWeb3,
)
from web3._utils.caching import (
    RequestInformation,
    generate_cache_key,
)
from web3._utils.module_testing.module_testing_utils import (
    WebSocketMessageStreamMock,
)
from web3.exceptions import (
    TimeExhausted,
    Web3RPCError,
)
from web3.providers.persistent import (
    WebSocketProvider,
)
from web3.types import (
    RPCEndpoint,
)
from web3.utils import (
    EthSubscription,
)


def _mock_ws(provider):
    provider._ws = AsyncMock()
    provider._ws.state = State.OPEN


async def _mocked_ws_conn():
    _conn = AsyncMock()
    _conn.state = State.OPEN
    return _conn


class WSException(Exception):
    pass


GET_BLOCK_JSON_MESSAGE = {
    "id": 0,
    "jsonrpc": "2.0",
    "method": "eth_getBlockByNumber",
    "params": ["latest", False],
}


def test_get_endpoint_uri_or_ipc_path_returns_endpoint_uri():
    provider = WebSocketProvider("ws://mocked")
    assert (
        provider.get_endpoint_uri_or_ipc_path()
        == "ws://mocked"
        == provider.endpoint_uri
    )


# -- async -- #


def test_websocket_provider_default_values():
    ws_uri = "ws://127.0.0.1:1337"
    with patch.dict("os.environ", {"WEB3_WS_PROVIDER_URI": ws_uri}):
        provider = WebSocketProvider()
        assert provider.endpoint_uri == ws_uri
        assert provider.use_text_frames is False


@pytest.mark.asyncio
async def test_disconnect_cleanup():
    provider = WebSocketProvider("ws://mocked")

    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: _mocked_ws_conn(),
    ):
        await provider.connect()

    assert provider._ws is not None
    assert provider._message_listener_task is not None

    # put some items in each cache
    provider._request_processor._request_response_cache.cache("0", "0x1337")
    provider._request_processor._request_information_cache.cache("0", "0x1337")
    provider._request_processor._subscription_response_queue.put_nowait({"id": "0"})
    provider._request_processor._handler_subscription_queue.put_nowait({"id": "0"})
    assert len(provider._request_processor._request_response_cache) == 1
    assert len(provider._request_processor._request_information_cache) == 1
    assert provider._request_processor._subscription_response_queue.qsize() == 1
    assert provider._request_processor._handler_subscription_queue.qsize() == 1

    await provider.disconnect()

    assert provider._ws is None
    assert len(provider._request_processor._request_response_cache) == 0
    assert len(provider._request_processor._request_information_cache) == 0
    assert provider._request_processor._subscription_response_queue.empty()
    assert provider._request_processor._handler_subscription_queue.empty()


@pytest.mark.asyncio
async def test_async_make_request_returns_desired_response():
    provider = WebSocketProvider("ws://mocked")

    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: _mocked_ws_conn(),
    ):
        await provider.connect()

    _mock_ws(provider)
    method_under_test = provider.make_request

    undesired_responses_count = 10
    ws_messages = [
        to_bytes(
            text=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "eth_subscription",
                    "params": {"subscription": "0x1", "result": f"0x{i}"},
                }
            )
        )
        for i in range(undesired_responses_count)
    ]
    # The first request we make should have an id of `0`, expect the response to match
    # that id. Append it as the last response in the list.
    ws_messages.append(b'{"jsonrpc": "2.0", "id": 0, "result": "0x1337"}')
    provider._ws = WebSocketMessageStreamMock(messages=ws_messages)

    response = await method_under_test(RPCEndpoint("some_method"), ["desired_params"])
    assert response == json.loads(ws_messages.pop())

    qsize = provider._request_processor._subscription_response_queue.qsize()
    assert qsize == len(ws_messages) == undesired_responses_count

    for _ in range(qsize):
        cached_response = (
            await provider._request_processor._subscription_response_queue.get()
        )
        # assert all cached responses are in the list of responses we received
        assert to_bytes(text=json.dumps(cached_response)) in ws_messages

    assert provider._request_processor._subscription_response_queue.empty()
    assert len(provider._request_processor._request_response_cache) == 0

    await provider.disconnect()


@pytest.mark.asyncio
async def test_async_make_request_times_out_of_while_loop_looking_for_response():
    timeout = 0.001
    provider = WebSocketProvider("ws://mocked", request_timeout=timeout)

    method_under_test = provider.make_request
    _mock_ws(provider)

    with pytest.raises(
        TimeExhausted,
        match=r"Timed out waiting for response with request id `0` after "
        rf"{timeout} second\(s\)",
    ):
        await method_under_test(RPCEndpoint("some_method"), ["desired_params"])


@pytest.mark.asyncio
async def test_msg_listener_task_starts_on_provider_connect_and_clears_on_disconnect():
    provider = WebSocketProvider("ws://mocked")
    _mock_ws(provider)

    assert provider._message_listener_task is None

    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: _mocked_ws_conn(),
    ):
        await provider.connect()  # connect

    assert provider._message_listener_task is not None
    assert not provider._message_listener_task.cancelled()

    await provider.disconnect()  # disconnect

    assert not provider._message_listener_task


@pytest.mark.asyncio
async def test_msg_listener_task_raises_exceptions_by_default():
    provider = WebSocketProvider("ws://mocked")
    _mock_ws(provider)

    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: _mocked_ws_conn(),
    ):
        await provider.connect()
        assert provider._message_listener_task is not None
        assert provider.silence_listener_task_exceptions is False

    provider._ws = WebSocketMessageStreamMock(
        raise_exception=WSException("test exception")
    )
    with pytest.raises(WSException, match="test exception"):
        await provider._message_listener_task

    assert provider._message_listener_task.done()


@pytest.mark.asyncio
async def test_msg_listener_task_silences_exceptions_and_error_logs_when_configured(
    caplog,
):
    provider = WebSocketProvider("ws://mocked", silence_listener_task_exceptions=True)
    _mock_ws(provider)

    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: _mocked_ws_conn(),
    ):
        await provider.connect()
        assert provider._message_listener_task is not None
        assert provider.silence_listener_task_exceptions is True

    provider._ws = WebSocketMessageStreamMock(
        raise_exception=WSException("test exception")
    )
    await asyncio.sleep(0.05)

    assert "test exception" in caplog.text
    assert (
        "Exception caught in listener, error logging and keeping listener background "
        "task alive.\n    error=WSException: test exception"
    ) in caplog.text

    # assert is still running
    assert not provider._message_listener_task.cancelled()

    # proper cleanup
    await provider.disconnect()


@pytest.mark.asyncio
async def test_listen_event_awaits_msg_processing_when_subscription_queue_is_full():
    """
    This test is to ensure that the `listen_event` method will wait for the
    `process_subscriptions` method to process a message when the subscription queue
    is full.
    """
    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: _mocked_ws_conn(),
    ):
        async_w3 = await AsyncWeb3(WebSocketProvider("ws://mocked"))

    _mock_ws(async_w3.provider)

    assert async_w3.provider._message_listener_task is not None
    assert not async_w3.provider._message_listener_task.cancelled()

    # assert queue is instance of asyncio.Queue and replace with a new queue, maxsize=1
    assert isinstance(
        async_w3.provider._request_processor._subscription_response_queue,
        type(asyncio.Queue()),
    )
    async_w3.provider._request_processor._subscription_response_queue = asyncio.Queue(
        maxsize=1
    )
    assert not async_w3.provider._request_processor._subscription_response_queue.full()

    # mock listen event
    async_w3.provider._listen_event.wait = AsyncMock()
    async_w3.provider._listen_event.set = Mock()

    # mock subscription and add to active subscriptions
    sub_id = "0x1"
    sub_request_information = RequestInformation(
        method=RPCEndpoint("eth_subscribe"),
        params=["mock"],
        response_formatters=[[], [], []],
        subscription_id=sub_id,
    )
    async_w3.provider._request_processor._request_information_cache.cache(
        generate_cache_key(sub_id),
        sub_request_information,
    )
    sub = EthSubscription()
    sub._id = sub_id
    async_w3.subscription_manager._add_subscription(sub)

    mocked_sub = {
        "jsonrpc": "2.0",
        "method": "eth_subscription",
        "params": {"subscription": sub_id, "result": "0x1337"},
    }

    # fill queue with one item so it is full
    async_w3.provider._request_processor._subscription_response_queue.put_nowait(
        mocked_sub
    )
    assert async_w3.provider._request_processor._subscription_response_queue.full()

    # wait will be called on the _listen_event when the next message comes in
    async_w3.provider._listen_event.wait.assert_not_called()

    # mock the message stream with a single message
    # the message listener task should then call the _listen_event.wait since the
    # queue is full
    async_w3.provider._ws = WebSocketMessageStreamMock(
        messages=[to_bytes(text=json.dumps(mocked_sub))]
    )
    await asyncio.sleep(0.05)
    async_w3.provider._listen_event.wait.assert_called_once()

    # set is not called until we start consuming messages
    async_w3.provider._listen_event.set.assert_not_called()

    async for message in async_w3.socket.process_subscriptions():
        # assert the very next message is the formatted mocked subscription
        assert message == mocked_sub["params"]
        break

    # assert we set the _listen_event after we consume the message
    async_w3.provider._listen_event.set.assert_called_once()

    # proper cleanup
    await async_w3.provider.disconnect()


@pytest.mark.asyncio
async def test_async_iterator_pattern_exception_handling_for_requests():
    iterations = 1

    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: WebSocketMessageStreamMock(
            raise_exception=ConnectionClosed(None, None)
        ),
    ):
        async for w3 in AsyncWeb3(WebSocketProvider("ws://mocked")):
            try:
                await w3.eth.block_number
            except ConnectionClosed:
                if iterations == 3:
                    break
                else:
                    iterations += 1
                    continue

            pytest.fail("Expected `ConnectionClosed` exception.")

        assert iterations == 3


@pytest.mark.asyncio
async def test_async_iterator_pattern_exception_handling_for_subscriptions():
    iterations = 1

    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: WebSocketMessageStreamMock(
            raise_exception=ConnectionClosed(None, None)
        ),
    ):
        async for w3 in AsyncWeb3(WebSocketProvider("ws://mocked")):
            try:
                async for _ in w3.socket.process_subscriptions():
                    # raises exception
                    pass
            except ConnectionClosed:
                if iterations == 3:
                    break
                else:
                    iterations += 1
                    continue

            pytest.fail("Expected `ConnectionClosed` exception.")

        assert iterations == 3


@pytest.mark.asyncio
async def test_connection_closed_ok_breaks_process_subscriptions_iteration():
    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: WebSocketMessageStreamMock(
            raise_exception=ConnectionClosedOK(None, None)
        ),
    ):
        w3 = await AsyncWeb3(WebSocketProvider("ws://mocked"))
        async for _ in w3.socket.process_subscriptions():
            pytest.fail("Should not reach this point.")


@pytest.mark.asyncio
async def test_connection_closed_ok_breaks_handle_subscriptions_iteration():
    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: WebSocketMessageStreamMock(
            raise_exception=ConnectionClosedOK(None, None)
        ),
    ):
        w3 = await AsyncWeb3(WebSocketProvider("ws://mocked"))
        # would fail with a ``TimeoutError`` if the iteration did not break properly
        # on ``ConnectionClosedOK``
        await asyncio.wait_for(
            w3.subscription_manager.handle_subscriptions(run_forever=True), timeout=1
        )


@pytest.mark.asyncio
async def test_listener_task_breaks_out_of_stream_when_cancelled():
    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: _mocked_ws_conn(),
    ):
        async_w3 = await AsyncWeb3(WebSocketProvider("ws://mocked"))

    async_w3.provider._message_listener_task.cancel()
    sub = EthSubscription()
    sub._id = "0x1"
    async_w3.subscription_manager._add_subscription(sub)
    # this should hang indefinitely if the listener task does not put a
    # ``TaskNotRunning`` in the ``_subscription_response_queue`` to break out of
    # listening. The call to ``provider._handle_listener_task_exceptions`` bubbles up
    # the exception.
    with pytest.raises(asyncio.CancelledError):
        async for _ in async_w3.socket.process_subscriptions():
            ...


@pytest.mark.asyncio
async def test_listener_task_breaks_out_of_handle_subscriptions_when_cancelled():
    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: _mocked_ws_conn(),
    ):
        async_w3 = await AsyncWeb3(WebSocketProvider("ws://mocked"))

    async_w3.provider._message_listener_task.cancel()
    sub = EthSubscription(handler=AsyncMock())
    sub._id = "0x1"

    async_w3.subscription_manager._add_subscription(sub)
    # this should hang indefinitely if the listener task does not put a
    # ``TaskNotRunning`` in the ``_handler_subscription_queue`` to break out of
    # listening. The call to ``provider._handle_listener_task_exceptions`` bubbles
    # up the exception.
    with pytest.raises(asyncio.CancelledError):
        await async_w3.subscription_manager.handle_subscriptions(run_forever=True)


@pytest.mark.asyncio
async def test_persistent_connection_provider_empty_batch_response():
    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: _mocked_ws_conn(),
    ):
        with pytest.raises(Web3RPCError, match="empty batch"):
            async with AsyncWeb3(WebSocketProvider("ws://mocked")) as async_w3:
                async with async_w3.batch_requests() as batch:
                    assert async_w3.provider._is_batching
                    async_w3.provider._ws.recv = AsyncMock()
                    async_w3.provider._ws.recv.return_value = (
                        b'{"jsonrpc": "2.0","id":null,"error": {"code": -32600, '
                        b'"message": "empty batch"}}\n'
                    )
                    await batch.async_execute()

        # assert that even though there was an error, we have reset the batching
        # state
        assert not async_w3.provider._is_batching


@pytest.mark.parametrize(
    "use_text_frames, expected_send_arg",
    (
        (False, to_bytes(text=json.dumps(GET_BLOCK_JSON_MESSAGE))),
        (True, json.dumps(GET_BLOCK_JSON_MESSAGE)),
    ),
)
@pytest.mark.asyncio
async def test_websocket_provider_use_text_frames(use_text_frames, expected_send_arg):
    provider = WebSocketProvider("ws://mocked", use_text_frames=use_text_frames)
    assert provider.use_text_frames is use_text_frames

    # mock provider and add a mocked response to the cache
    _mock_ws(provider)
    provider._ws.send = AsyncMock()
    provider._request_processor._request_response_cache.cache(
        generate_cache_key(0), "0x1337"
    )

    await provider.make_request(RPCEndpoint("eth_getBlockByNumber"), ["latest", False])
    provider._ws.send.assert_called_once_with(expected_send_arg)


@pytest.mark.asyncio
async def test_websocket_provider_raises_errors_from_cache_not_tied_to_a_request():
    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: WebSocketMessageStreamMock(
            messages=[
                b'{"id": 0, "jsonrpc": "2.0", "result": "0x0"}\n',
                b'{"id": null, "jsonrpc": "2.0", "error": {"code": 21, "message": "Request shutdown"}}\n',  # noqa: E501
            ]
        ),
    ):
        async_w3 = await AsyncWeb3(WebSocketProvider("ws://mocked"))
        with pytest.raises(Web3RPCError, match="Request shutdown"):
            await asyncio.sleep(0.1)
            await async_w3.eth.block_number


@pytest.mark.asyncio
async def test_req_info_cache_size_can_be_set_and_warns_when_full(caplog):
    with patch(
        "web3.providers.persistent.websocket.connect",
        new=lambda *_1, **_2: _mocked_ws_conn(),
    ):
        async_w3 = await AsyncWeb3(
            WebSocketProvider("ws://mocked", request_information_cache_size=1)
        )
        async_w3.provider._request_processor.cache_request_information(
            RPCEndpoint("eth_getBlockByNumber"),
            ["latest"],
            tuple(),
            tuple(),
        )

        assert len(async_w3.provider._request_processor._request_information_cache) == 1
        assert (
            "Request information cache is full. This may result in unexpected "
            "behavior. Consider increasing the ``request_information_cache_size`` "
            "on the provider."
        ) in caplog.text


@pytest.mark.asyncio
async def test_raise_stray_errors_from_cache_handles_list_response_without_error():
    provider = WebSocketProvider("ws://mocked")
    _mock_ws(provider)

    bad_response = [
        {"id": None, "jsonrpc": "2.0", "error": {"code": 21, "message": "oops"}}
    ]
    provider._request_processor._request_response_cache._data["bad_key"] = bad_response

    # assert no errors raised
    provider._raise_stray_errors_from_cache()
