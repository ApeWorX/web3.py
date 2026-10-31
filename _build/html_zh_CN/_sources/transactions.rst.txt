Transactions
============

There are a handful of ways to interact with transactions in web3.py. See the
:ref:`Web3.eth module <web3-eth-methods>` for a full list of transaction-related methods. Note that you may also :ref:`batch requests <batch_requests>` that read transaction data, but not send new transactions in a batch request.

The rest of this guide covers the decision tree for how to send a transaction.

.. note::

  Prefer to view this code in a Jupyter Notebook? View the repo `here <https://github.com/wolovim/ethereum-notebooks/blob/master/Sending%20Transactions.ipynb>`_.

There are two methods for sending transactions using web3.py: :meth:`~web3.eth.Eth.send_transaction` and :meth:`~web3.eth.Eth.send_raw_transaction`. A brief guide:

#. Want to sign a transaction offline or send pre-signed transactions?

   * use :meth:`sign_transaction <eth_account.account.Account.sign_transaction>` + :meth:`~web3.eth.Eth.send_raw_transaction`

#. Are you primarily using the same account for all transactions and would you prefer to save a few lines of code?

   * configure the ``build`` method for :class:`~web3.middleware.SignAndSendRawMiddlewareBuilder`, then
   * use :meth:`~web3.eth.Eth.send_transaction`

#. Otherwise:

   * load account via eth-account (:meth:`w3.eth.account.from_key(pk) <eth_account.account.Account.from_key>`), then
   * use :meth:`~web3.eth.Eth.send_transaction`

Interacting with or deploying a contract?

* Option 1: :meth:`~web3.contract.ContractFunction.transact` uses :meth:`~web3.eth.Eth.send_transaction` under the hood
* Option 2: :meth:`~web3.contract.ContractFunction.build_transaction` + :meth:`sign_transaction <eth_account.account.Account.sign_transaction>` + :meth:`~web3.eth.Eth.send_raw_transaction`

An example for each can be found below.


Chapter 0: ``w3.eth.send_transaction`` with ``eth-tester``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Many tutorials use ``eth-tester`` (via EthereumTesterProvider) for convenience and speed
of conveying ideas/building a proof of concept. Transactions sent by test accounts are
auto-signed.

.. code-block:: python

  from web3 import Web3, EthereumTesterProvider

  w3 = Web3(EthereumTesterProvider())

  # eth-tester populates accounts with test ether:
  acct1 = w3.eth.accounts[0]

  some_address = "0x0000000000000000000000000000000000000000"

  # when using one of its generated test accounts,
  # eth-tester signs the tx (under the hood) before sending:
  tx_hash = w3.eth.send_transaction({
      "from": acct1,
      "to": some_address,
      "value": 123123123123123
  })

  tx = w3.eth.get_transaction(tx_hash)
  assert tx["from"] == acct1


Chapter 1: ``w3.eth.send_transaction`` + signer middleware
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :meth:`~web3.eth.Eth.send_transaction` method is convenient and to-the-point.
If you want to continue using the pattern after graduating from ``eth-tester``, you can
utilize web3.py middleware to sign transactions from a particular account:

.. code-block:: python

  from web3.middleware import SignAndSendRawMiddlewareBuilder
  import os

  # Note: Never commit your key in your code! Use env variables instead:
  pk = os.environ.get('PRIVATE_KEY')

  # Instantiate an Account object from your key:
  acct2 = w3.eth.account.from_key(pk)

  # For the sake of this example, fund the new account:
  w3.eth.send_transaction({
      "from": acct1,
      "value": w3.to_wei(3, 'ether'),
      "to": acct2.address
  })

  # Add acct2 as auto-signer:
  w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(acct2), layer=0)
  # pk also works: w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(pk), layer=0)

  # Transactions from `acct2` will then be signed, under the hood, in the middleware:
  tx_hash = w3.eth.send_transaction({
      "from": acct2.address,
      "value": 3333333333,
      "to": some_address
  })

  tx = w3.eth.get_transaction(tx_hash)
  assert tx["from"] == acct2.address

  # Optionally, you can set a default signer as well:
  # w3.eth.default_account = acct2.address
  # Then, if you omit a "from" key, acct2 will be used.


Chapter 2: ``w3.eth.send_raw_transaction``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if you don't opt for the middleware, you'll need to:

- build each transaction,
- :meth:`sign_transaction <eth_account.account.Account.sign_transaction>`, and
- then use :meth:`~web3.eth.Eth.send_raw_transaction`.

.. code-block:: python

  # 1. Build a new tx
  transaction = {
      'from': acct2.address,
      'to': some_address,
      'value': 1000000000,
      'nonce': w3.eth.get_transaction_count(acct2.address),
      'gas': 200000,
      'maxFeePerGas': 2000000000,
      'maxPriorityFeePerGas': 1000000000,
  }

  # 2. Sign tx with a private key
  signed = w3.eth.account.sign_transaction(transaction, pk)

  # 3. Send the signed transaction
  tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
  tx = w3.eth.get_transaction(tx_hash)
  assert tx["from"] == acct2.address


Chapter 3: Contract transactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same concepts apply for contract interactions, at least under the hood.

Executing a function on a smart contract requires sending a transaction, which is typically done in one of two ways:

- executing the :meth:`~web3.contract.ContractFunction.transact` function, or
- :meth:`~web3.contract.ContractFunction.build_transaction`, then signing and sending the raw transaction.

.. code-block:: python

  #########################################
  #### SMOL CONTRACT FOR THIS EXAMPLE: ####
  #########################################
  # // SPDX-License-Identifier: MIT
  # pragma solidity 0.8.17;
  #
  # contract Billboard {
  #     string public message;
  #
  #     constructor(string memory _message) {
  #         message = _message;
  #     }
  #
  #     function writeBillboard(string memory _message) public {
  #         message = _message;
  #     }
  # }

  # After compiling the contract, initialize the contract factory:
  init_bytecode = "60806040523480156200001157600080fd5b5060..."
  abi = '[{"inputs": [{"internalType": "string","name": "_message",...'
  Billboard = w3.eth.contract(bytecode=init_bytecode, abi=abi)

  # Deploy a contract using `transact` + the signer middleware:
  tx_hash = Billboard.constructor("gm").transact({"from": acct2.address})
  receipt = w3.eth.get_transaction_receipt(tx_hash)
  deployed_addr = receipt["contractAddress"]

  # Reference the deployed contract:
  billboard = w3.eth.contract(address=deployed_addr, abi=abi)

  # Manually build and sign a transaction:
  unsent_billboard_tx = billboard.functions.writeBillboard("gn").build_transaction({
      "from": acct2.address,
      "nonce": w3.eth.get_transaction_count(acct2.address),
  })
  signed_tx = w3.eth.account.sign_transaction(unsent_billboard_tx, private_key=acct2.key)

  # Send the raw transaction:
  assert billboard.functions.message().call() == "gm"
  tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
  w3.eth.wait_for_transaction_receipt(tx_hash)
  assert billboard.functions.message().call() == "gn"
