import argparse
import asyncio
from collections import (
    defaultdict,
)
from collections.abc import Callable
import logging
import sys
import timeit
from typing import (
    Any,
)

from web3 import (
    AsyncHTTPProvider,
    AsyncWeb3,
    HTTPProvider,
    Web3,
)
from web3.middleware import (
    BufferedGasEstimateMiddleware,
    GasPriceStrategyMiddleware,
)
from web3.types import (
    Wei,
)

from .node import (
    GethBenchmarkFixture,
)
from .reporting import (
    print_entry,
    print_footer,
    print_header,
)
from .utils import (
    wait_for_aiohttp,
    wait_for_http,
)

KEYFILE_PW = "web3py-test"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--num-calls",
    type=int,
    default=10,
    help="The number of RPC calls to make",
)

# TODO - layers to test:
# contract.functions.method(...).call()
# w3.eth.call(...)
# HTTPProvider.make_request(...)


def build_web3_http(endpoint_uri: str) -> Web3:
    wait_for_http(endpoint_uri)
    _w3 = Web3(
        HTTPProvider(endpoint_uri),
        middleware=[GasPriceStrategyMiddleware, BufferedGasEstimateMiddleware],
    )
    return _w3


async def build_async_w3_http(endpoint_uri: str) -> AsyncWeb3[Any]:
    await wait_for_aiohttp(endpoint_uri)
    _w3 = AsyncWeb3(
        AsyncHTTPProvider(endpoint_uri),
        middleware=[GasPriceStrategyMiddleware, BufferedGasEstimateMiddleware],
    )
    return _w3


def sync_benchmark(func: Callable[..., Any], n: int) -> float | str:
    try:
        starttime = timeit.default_timer()
        for _ in range(n):
            func()
        endtime = timeit.default_timer()
        execution_time = endtime - starttime
        return execution_time
    except Exception:
        return "N/A"


async def async_benchmark(func: Callable[..., Any], n: int) -> float | str:
    try:
        starttime = timeit.default_timer()
        for result in asyncio.as_completed([func() for _ in range(n)]):
            await result
        execution_time = timeit.default_timer() - starttime
        return execution_time
    except Exception:
        return "N/A"


def main(logger: logging.Logger, num_calls: int) -> None:
    fixture = GethBenchmarkFixture()
    for built_fixture in fixture.build():
        for _ in built_fixture:
            w3_http = build_web3_http(fixture.endpoint_uri)
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # -- sync -- #
            account = w3_http.eth.accounts[0]

            # -- async -- #
            async_w3_http = loop.run_until_complete(
                build_async_w3_http(fixture.endpoint_uri)
            )
            async_accounts = loop.run_until_complete(async_w3_http.eth.accounts)
            async_account = async_accounts[0]

            methods = [
                {
                    "name": "eth_gasPrice",
                    "params": {},
                    "exec": lambda w3_http=w3_http: w3_http.eth.gas_price,
                    "async_exec": lambda async_w3_http=async_w3_http: (
                        async_w3_http.eth.gas_price
                    ),  # noqa: E501
                },
                {
                    "name": "eth_sendTransaction",
                    "params": {},
                    "exec": lambda w3_http=w3_http, account=account: (
                        w3_http.eth.send_transaction(  # noqa: E501
                            {
                                "to": "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                                "from": account,
                                "value": Wei(1),
                            }
                        )
                    ),
                    "async_exec": lambda async_w3_http=async_w3_http, async_account=async_account: (
                        async_w3_http.eth.send_transaction(  # noqa: E501
                            {
                                "to": "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                                "from": async_account,
                                "value": Wei(1),
                            }
                        )
                    ),
                },
                {
                    "name": "eth_blockNumber",
                    "params": {},
                    "exec": lambda w3_http=w3_http: w3_http.eth.block_number,
                    "async_exec": lambda async_w3_http=async_w3_http: (
                        async_w3_http.eth.block_number
                    ),  # noqa: E501
                },
                {
                    "name": "eth_getBlock",
                    "params": {},
                    "exec": lambda w3_http=w3_http: w3_http.eth.get_block(1),
                    "async_exec": lambda async_w3_http=async_w3_http: (
                        async_w3_http.eth.get_block(  # noqa: E501
                            1
                        )
                    ),
                },
            ]

            def benchmark(
                method: dict[str, Any], loop: asyncio.AbstractEventLoop = loop
            ) -> None:
                outcomes: dict[str, str | float] = defaultdict(lambda: "N/A")
                outcomes["name"] = method["name"]
                outcomes["HTTPProvider"] = sync_benchmark(
                    method["exec"],
                    num_calls,
                )
                outcomes["AsyncHTTPProvider"] = loop.run_until_complete(
                    async_benchmark(method["async_exec"], num_calls)
                )
                print_entry(logger, outcomes)

            print_header(logger, num_calls)

            for method in methods:
                benchmark(method)

            print_footer(logger)


if __name__ == "__main__":
    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    main(logger, args.num_calls)
