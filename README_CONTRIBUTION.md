# Python-Native Ethereum Interaction: Enhancing Async Test Coverage in Web3.py

**Nirwaan Azhar | University of Oklahoma | CS4273**  
**GitHub Issue:** https://github.com/ApeWorX/web3.py/issues/3835  
**Draft PR:** https://github.com/ApeWorX/web3.py/pull/3836  
**Video Demo:** [Link coming soon]

---

## Project Overview

This project contributes to [web3.py](https://github.com/ApeWorX/web3.py), the primary
Python library for interacting with the Ethereum blockchain. The contribution focuses on
closing the async/sync test parity gap in `AsyncEthModuleTest` — specifically adding
async test coverage for methods that existed in the synchronous suite but had no async
equivalent.

---

## What Was Changed

### 1. `web3/_utils/module_testing/eth_module.py`
Added 3 new async test methods to `AsyncEthModuleTest`:

| Test | What It Validates |
|------|-------------------|
| `test_eth_block_number` | `async_w3.eth.block_number` returns a valid integer |
| `test_eth_get_block_number` | `async_w3.eth.get_block_number()` returns a valid integer |
| `test_eth_get_balance_with_block_identifier` | Balance differs between genesis and latest block |

### 2. `tests/core/eth-tester-api/test_async_eth_module.py` *(new file)*
A standalone pytest-asyncio test file that validates all 3 new async methods
against the `AsyncEthereumTesterProvider` backend (local simulated EVM).

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Git
- Windows/Mac/Linux

### Clone and Install

```bash
git clone https://github.com/YOUR_USERNAME/web3.py.git
cd web3.py
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -e ".[dev]"
pip install cached_property eth-account
```

---

## Running the Tests

### Run the new async tests
```bash
python -m pytest tests/core/eth-tester-api/test_async_eth_module.py -v
```

### Expected output
```
tests/core/eth-tester-api/test_async_eth_module.py::test_eth_block_number PASSED
tests/core/eth-tester-api/test_async_eth_module.py::test_eth_get_block_number PASSED
tests/core/eth-tester-api/test_async_eth_module.py::test_eth_get_balance_with_block_identifier PASSED
3 passed in 2.78s
```

### Run the existing core tests
```bash
python -m pytest tests/core/eth-module/test_block_api.py -v
python -m pytest tests/core/eth-module/test_eth_properties.py -v
```

---

## Motivation

The `AsyncEthModuleTest` class had ~120 async tests while the synchronous
`EthModuleTest` had ~140 additional tests with no async equivalent. Silent
failures in async code are harder to catch than sync failures. This contribution
closes three of those gaps and provides a reproducible local setup for validating them.

---

## Tools & Technologies

- Python 3.11
- web3.py (ApeWorX/web3.py)
- pytest + pytest-asyncio
- eth-tester / AsyncEthereumTesterProvider
- GitHub Actions (CI/CD on fork)