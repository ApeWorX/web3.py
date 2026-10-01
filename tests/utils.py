import asyncio
import inspect
import socket

from web3._utils.threads import (
    Timeout,
)


class PollDelayCounter:
    def __init__(self, initial_delay=0, max_delay=1, initial_step=0.01):
        self.initial_delay = initial_delay
        self.initial_step = initial_step
        self.max_delay = max_delay
        self.current_delay = initial_delay

    def __call__(self):
        delay = self.current_delay

        if self.current_delay == 0:
            self.current_delay += self.initial_step
        else:
            self.current_delay *= 2
            self.current_delay = min(self.current_delay, self.max_delay)

        return delay

    def reset(self):
        self.current_delay = self.initial_delay


def get_open_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return str(port)


async def _async_wait_for_block_fixture_logic(async_w3, block_number=1, timeout=None):
    if not timeout:
        current_block_number = await async_w3.eth.block_number  # type:ignore
        timeout = (block_number - current_block_number) * 3
    poll_delay_counter = PollDelayCounter()
    with Timeout(timeout) as timeout:
        eth_block_number = await async_w3.eth.block_number
        while eth_block_number < block_number:
            await async_w3.manager.coro_request("evm_mine", [])
            await timeout.async_sleep(poll_delay_counter())
            eth_block_number = await async_w3.eth.block_number


async def _async_wait_for_transaction_fixture_logic(async_w3, txn_hash, timeout=120):
    poll_delay_counter = PollDelayCounter()
    with Timeout(timeout) as timeout:
        while True:
            txn_receipt = await async_w3.eth.get_transaction_receipt(txn_hash)
            if txn_receipt is not None:
                break
            asyncio.sleep(poll_delay_counter())
            timeout.check()

    return txn_receipt


def async_partial(f, *args, **kwargs):
    async def f2(*args2, **kwargs2):
        result = f(*args, *args2, **kwargs, **kwargs2)
        if inspect.iscoroutinefunction(f):
            result = await result
        return result

    return f2
