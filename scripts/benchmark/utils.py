import asyncio
import signal
import socket
import time
from typing import (
    Any,
)

import aiohttp
import requests


def wait_for_socket(ipc_path: str, timeout: int = 30) -> None:
    start = time.time()
    while time.time() < start + timeout:
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(ipc_path)
            sock.settimeout(timeout)
        except OSError:
            time.sleep(0.01)
        else:
            break


def wait_for_http(endpoint_uri: str, timeout: int = 60) -> None:
    start = time.time()
    while time.time() < start + timeout:
        try:
            requests.get(endpoint_uri)
        except requests.ConnectionError:
            time.sleep(0.01)
        else:
            break


async def wait_for_aiohttp(endpoint_uri: str, timeout: int = 60) -> None:
    start = time.time()
    while time.time() < start + timeout:
        try:
            async with aiohttp.ClientSession() as session:
                await session.get(endpoint_uri)
        except aiohttp.client_exceptions.ClientConnectorError:
            await asyncio.sleep(0.01)
        else:
            break


def wait_for_popen(proc: Any, timeout: int) -> None:
    start = time.time()
    while time.time() < start + timeout:
        if proc.poll() is None:
            time.sleep(0.01)
        else:
            break


def kill_proc_gracefully(proc: Any) -> None:
    if proc.poll() is None:
        proc.send_signal(signal.SIGINT)
        wait_for_popen(proc, 13)

    if proc.poll() is None:
        proc.terminate()
        wait_for_popen(proc, 5)

    if proc.poll() is None:
        proc.kill()
        wait_for_popen(proc, 2)
