.. _contracts:

Contracts
=========

.. py:module:: web3.contract

Smart contracts are programs deployed to the Ethereum network. See the
`ethereum.org docs <https://ethereum.org/en/developers/docs/smart-contracts>`_
for a proper introduction.

Interacting with deployed contracts
-----------------------------------

In order to use an existing contract, you'll need its deployed address and its ABI.
Both can be found using block explorers, like Etherscan. Once you instantiate a contract
instance, you can read data and execute transactions.

.. code-block:: python

    # Configure w3, e.g., w3 = Web3(...)
    address = '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F988'
    abi = '[{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"address","name":"minter_","type":"address"},...'
    contract_instance = w3.eth.contract(address=address, abi=abi)

    # read state:
    contract_instance.functions.storedValue().call()
    # 42

    # update state:
    tx_hash = contract_instance.functions.updateValue(43).transact()

.. _contract_example:

Contract Deployment Example
---------------------------

To run this example, you will need to install a few extra features:

- The sandbox node provided by eth-tester. You can install it with:

.. code-block:: bash

    $ pip install -U "web3[tester]"

- ``py-solc-x``. This is the supported route to installing the solidity compiler ``solc``. You can install it with:

.. code-block:: bash

    $ pip install py-solc-x

After ``py-solc-x`` is installed, you will need to install a version of ``solc``. You can install the latest version via a new REPL with:

.. code-block:: python

    >>> from solcx import install_solc
    >>> install_solc(version='latest')

You should now be set up to compile and deploy a contract.

The following example runs through these steps:

#. Compile Solidity contract into bytecode and an ABI
#. Initialize a Contract instance
#. Deploy the contract using the Contract instance to initiate a transaction
#. Interact with the contract functions using the Contract instance

.. code-block:: python

    >>> from web3 import Web3
    >>> from solcx import compile_source

    # Solidity source code
    >>> compiled_sol = compile_source(
    ...     '''
    ...     pragma solidity >0.5.0;
    ...
    ...     contract Greeter {
    ...         string public greeting;
    ...
    ...         constructor() public {
    ...             greeting = 'Hello';
    ...         }
    ...
    ...         function setGreeting(string memory _greeting) public {
    ...             greeting = _greeting;
    ...         }
    ...
    ...         function greet() view public returns (string memory) {
    ...             return greeting;
    ...         }
    ...     }
    ...     ''',
    ...     output_values=['abi', 'bin']
    ... )

    # retrieve the contract interface
    >>> contract_id, contract_interface = compiled_sol.popitem()

    # get bytecode / bin
    >>> bytecode = contract_interface['bin']

    # get abi
    >>> abi = contract_interface['abi']

    # web3.py instance
    >>> w3 = Web3(Web3.EthereumTesterProvider())

    # set pre-funded account as sender
    >>> w3.eth.default_account = w3.eth.accounts[0]

    >>> Greeter = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Submit the transaction that deploys the contract
    >>> tx_hash = Greeter.constructor().transact()

    # Wait for the transaction to be mined, and get the transaction receipt
    >>> tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    >>> greeter = w3.eth.contract(
    ...     address=tx_receipt.contractAddress,
    ...     abi=abi
    ... )

    >>> greeter.functions.greet().call()
    'Hello'

    >>> tx_hash = greeter.functions.setGreeting('Nihao').transact()
    >>> tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    >>> greeter.functions.greet().call()
    'Nihao'


Contract Factories
------------------

These factories are not intended to be initialized directly.
Instead, create contract objects using the :meth:`w3.eth.contract() <web3.eth.Eth.contract>`
method. By default, the contract factory is :class:`Contract`.

.. py:class:: Contract(address)

    Contract provides a default interface for deploying and interacting with
    Ethereum smart contracts.

    The address parameter can be a hex address or an ENS name, like ``mycontract.eth``.


Properties
----------

Each Contract Factory exposes the following properties.


.. py:attribute:: Contract.address

    The hexadecimal encoded 20-byte address of the contract, or an ENS name.
    May be ``None`` if not provided during factory creation.


.. py:attribute:: Contract.abi

    The contract ``abi``, or Application Binary Interface, specifies how a contract can
    be interacted with. Without an ``abi``, the contract cannot be decoded. The ``abi``
    enables the Contract instance to expose functions and events as object properties.

    For further details, see the `Solidity ABI specification <https://docs.soliditylang.org/en/develop/abi-spec.html>`_.


.. py:attribute:: Contract.bytecode

    The contract bytecode string.  May be ``None`` if not provided during
    factory creation.


.. py:attribute:: Contract.bytecode_runtime

    The runtime part of the contract bytecode string.  May be ``None`` if not
    provided during factory creation.


.. py:attribute:: Contract.decode_tuples

    If a Tuple/Struct is returned by a contract function, this flag defines whether
    to apply the field names from the ABI to the returned data.
    If False, the returned value will be a normal Python ``Tuple``. If True, the returned
    value will be a Python ``NamedTuple`` of the class ``ABIDecodedNamedTuple``.

    NamedTuples have some restrictions regarding field names.
    web3.py sets ``NamedTuple``'s ``rename=True``, so disallowed field names may be
    different than expected. See the `Python docs <https://docs.python.org/3/library/collections.html#collections.namedtuple>`_
    for more information.

    Defaults to ``False`` if not provided during factory creation.


.. py:attribute:: Contract.functions

    This provides access to contract functions as attributes.  For example:
    ``myContract.functions.MyMethod()``.  The exposed contract functions are classes of the
    type :py:class:`ContractFunction`.


.. py:attribute:: Contract.events

    This provides access to contract events as attributes.  For example:
    ``myContract.events.MyEvent()``.  The exposed contract events are classes of the
    type :py:class:`ContractEvent`.

Methods
-------

Method doctests use the following ABI and bytecode.

.. code-block:: python

    >>> bytecode = '6060604052341561000c57fe5b604051602080610acb833981016040528080519060200190919050505b620f42408114151561003b5760006000fd5b670de0b6b3a76400008102600281905550600254600060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055505b505b610a27806100a46000396000f30060606040523615610097576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806306fdde0314610099578063095ea7b31461013257806318160ddd1461018957806323b872dd146101af578063313ce5671461022557806370a082311461025157806395d89b411461029b578063a9059cbb14610334578063dd62ed3e1461038b575bfe5b34156100a157fe5b6100a96103f4565b60405180806020018281038252838181518152602001915080519060200190808383600083146100f8575b8051825260208311156100f8576020820191506020810190506020830392506100d4565b505050905090810190601f1680156101245780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561013a57fe5b61016f600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803590602001909190505061042e565b604051808215151515815260200191505060405180910390f35b341561019157fe5b610199610521565b6040518082815260200191505060405180910390f35b34156101b757fe5b61020b600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff16906020019091908035906020019091905050610527565b604051808215151515815260200191505060405180910390f35b341561022d57fe5b610235610791565b604051808260ff1660ff16815260200191505060405180910390f35b341561025957fe5b610285600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610796565b6040518082815260200191505060405180910390f35b34156102a357fe5b6102ab6107e0565b60405180806020018281038252838181518152602001915080519060200190808383600083146102fa575b8051825260208311156102fa576020820191506020810190506020830392506102d6565b505050905090810190601f1680156103265780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561033c57fe5b610371600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803590602001909190505061081a565b604051808215151515815260200191505060405180910390f35b341561039357fe5b6103de600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610973565b6040518082815260200191505060405180910390f35b604060405190810160405280600981526020017f54657374546f6b656e000000000000000000000000000000000000000000000081525081565b600081600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925846040518082815260200191505060405180910390a3600190505b92915050565b60025481565b600081600060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205410806105f1575081600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054105b156105fc5760006000fd5b81600060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254019250508190555081600060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254039250508190555081600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825403925050819055508273ffffffffffffffffffffffffffffffffffffffff168473ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a3600190505b9392505050565b601281565b6000600060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490505b919050565b604060405190810160405280600481526020017f544553540000000000000000000000000000000000000000000000000000000081525081565b600081600060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205410156108695760006000fd5b81600060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254039250508190555081600060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825401925050819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a3600190505b92915050565b6000600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490505b929150505600a165627a7a723058205071371ee2a4a1be3c96e77d939cdc26161a256fdd638efc08bd33dfc65d3b850029'
    >>> abi = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function","stateMutability":"nonpayable"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function","stateMutability":"nonpayable"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function","stateMutability":"nonpayable"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function","stateMutability":"view"},{"inputs":[{"name":"_totalSupply","type":"uint256"}],"payable":false,"type":"constructor","stateMutability":"nonpayable"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"}]'
    >>> contract = w3.eth.contract(abi=abi, bytecode=bytecode)

Each Contract Factory exposes the following methods.

.. testsetup:: contractmethods

    from web3 import Web3
    w3 = Web3(Web3.EthereumTesterProvider())
    bytecode = '6060604052341561000c57fe5b604051602080610acb833981016040528080519060200190919050505b620f42408114151561003b5760006000fd5b670de0b6b3a76400008102600281905550600254600060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055505b505b610a27806100a46000396000f30060606040523615610097576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806306fdde0314610099578063095ea7b31461013257806318160ddd1461018957806323b872dd146101af578063313ce5671461022557806370a082311461025157806395d89b411461029b578063a9059cbb14610334578063dd62ed3e1461038b575bfe5b34156100a157fe5b6100a96103f4565b60405180806020018281038252838181518152602001915080519060200190808383600083146100f8575b8051825260208311156100f8576020820191506020810190506020830392506100d4565b505050905090810190601f1680156101245780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561013a57fe5b61016f600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803590602001909190505061042e565b604051808215151515815260200191505060405180910390f35b341561019157fe5b610199610521565b6040518082815260200191505060405180910390f35b34156101b757fe5b61020b600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff16906020019091908035906020019091905050610527565b604051808215151515815260200191505060405180910390f35b341561022d57fe5b610235610791565b604051808260ff1660ff16815260200191505060405180910390f35b341561025957fe5b610285600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610796565b6040518082815260200191505060405180910390f35b34156102a357fe5b6102ab6107e0565b60405180806020018281038252838181518152602001915080519060200190808383600083146102fa575b8051825260208311156102fa576020820191506020810190506020830392506102d6565b505050905090810190601f1680156103265780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561033c57fe5b610371600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803590602001909190505061081a565b604051808215151515815260200191505060405180910390f35b341561039357fe5b6103de600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610973565b6040518082815260200191505060405180910390f35b604060405190810160405280600981526020017f54657374546f6b656e000000000000000000000000000000000000000000000081525081565b600081600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925846040518082815260200191505060405180910390a3600190505b92915050565b60025481565b600081600060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205410806105f1575081600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054105b156105fc5760006000fd5b81600060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254019250508190555081600060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254039250508190555081600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825403925050819055508273ffffffffffffffffffffffffffffffffffffffff168473ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a3600190505b9392505050565b601281565b6000600060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490505b919050565b604060405190810160405280600481526020017f544553540000000000000000000000000000000000000000000000000000000081525081565b600081600060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205410156108695760006000fd5b81600060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254039250508190555081600060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825401925050819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a3600190505b92915050565b6000600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490505b929150505600a165627a7a723058205071371ee2a4a1be3c96e77d939cdc26161a256fdd638efc08bd33dfc65d3b850029'
    abi = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function","stateMutability":"nonpayable"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function","stateMutability":"nonpayable"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function","stateMutability":"nonpayable"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function","stateMutability":"view"},{"inputs":[{"name":"_totalSupply","type":"uint256"}],"payable":false,"type":"constructor","stateMutability":"nonpayable"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"}]'
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

.. py:classmethod:: Contract.constructor(*args, **kwargs).transact(transaction=None)

    Construct and deploy a contract by sending a new public transaction.

    If provided ``transaction`` should be a dictionary conforming to the
    ``web3.eth.send_transaction(transaction)`` method.  This value may not
    contain the keys ``data`` or ``to``.

    If the contract takes constructor parameters they should be provided as
    positional arguments or keyword arguments.

    If any of the arguments specified in the ABI are an ``address`` type, they
    will accept ENS names.

    If a ``gas`` value is not provided, then the ``gas`` value for the
    deployment transaction will be created using the ``web3.eth.estimate_gas()``
    method.

    Returns the transaction hash for the deploy transaction.

    .. doctest:: contractmethods

        >>> deploy_txn = contract.constructor(1000000).transact({'from': w3.eth.accounts[0], 'gas': 899000, 'gasPrice': Web3.to_wei(1, 'gwei')})
        >>> txn_receipt = w3.eth.get_transaction_receipt(deploy_txn)
        >>> txn_receipt['contractAddress']
        '0xF2E246BB76DF876Cef8b38ae84130F4F55De395b'


.. py:classmethod:: Contract.constructor(*args, **kwargs).estimate_gas(transaction=None, block_identifier=None)
    :noindex:

    Estimate gas for constructing and deploying the contract.

    This method behaves the same as the
    :py:meth:`Contract.constructor(*args, **kwargs).transact` method,
    with transaction details being passed into the end portion of the
    function call, and function arguments being passed into the first portion.

    The ``block_identifier`` parameter is passed directly to the call at the end portion
    of the function call.

    Returns the amount of gas consumed which can be used as a gas estimate for
    executing this transaction publicly.

    Returns the gas needed to deploy the contract.

    .. doctest:: contractmethods

        >>> contract.constructor(1000000).estimate_gas()
        664971

.. py:classmethod:: Contract.constructor(*args, **kwargs).build_transaction(transaction=None)
    :noindex:

    Construct the contract deploy transaction bytecode data.

    If the contract takes constructor parameters they should be provided as
    positional arguments or keyword arguments.

    If any of the ``args`` specified in the ABI are an ``address`` type, they
    will accept ENS names.

    Returns the transaction dictionary that you can pass to send_transaction method.

    .. doctest:: contractmethods

        >>> transaction = {
        ...   'gas': 664971,
        ...   'chainId': 131277322940537
        ... }
        >>> contract_data = contract.constructor(1000000).build_transaction(transaction)
        >>> w3.eth.send_transaction(contract_data)
        HexBytes('0x40c51804800dee88e14e69826cfe51bc5f25f61935331e8aa6d8d7771fb36350')

.. _contract_create_filter:

.. py:classmethod:: Contract.events.your_event_name.create_filter(from_block=None, to_block="latest", argument_filters={}, topics=[])

    Creates a new event filter, an instance of :py:class:`web3.utils.filters.LogFilter`.

    - ``from_block`` is a mandatory field. Defines the starting block (exclusive) filter block range. It can be either the starting block number, or 'latest' for the last mined block, or 'pending' for unmined transactions. In the case of ``from_block``, 'latest' and 'pending' set the 'latest' or 'pending' block as a static value for the starting filter block.
    - ``to_block`` optional. Defaults to 'latest'. Defines the ending block (inclusive) in the filter block range.  Special values 'latest' and 'pending' set a dynamic range that always includes the 'latest' or 'pending' blocks for the filter's upper block range.
    - ``address`` optional. Defaults to the contract address. The filter matches the event logs emanating from ``address``.
    - ``argument_filters``, optional. Expects a dictionary of argument names and values. When provided event logs are filtered for the event argument values. Event arguments can be both indexed or unindexed. Indexed values will be translated to their corresponding topic arguments. Unindexed arguments will be filtered using a regular expression.
    - ``topics`` optional, accepts the standard JSON-RPC topics argument.  See the JSON-RPC documentation for `eth_newFilter <https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newfilter>`_ more information on the ``topics`` parameters.

    .. doctest:: contractmethods

        >>> filter = contract.events.Transfer.create_filter(from_block='latest')

.. py:classmethod:: Contract.events.your_event_name.build_filter()

    Creates a EventFilterBuilder instance with the event abi, and the contract address if called from a deployed contract instance.  The EventFilterBuilder provides a convenient way to construct the filter parameters with value checking against the event abi. It allows for defining multiple match values or of single values through the match_any and match_single methods.

    .. doctest:: contractmethods

        >>> filter_builder = contract.events.Transfer.build_filter()
        >>> filter_builder.from_block = "latest"
        >>> filter_builder.args['from'].match_any(w3.eth.accounts[0])
        >>> filter_builder.args['to'].match_single(w3.eth.accounts[1])
        >>> filter_builder.args['value'].match_single(10000)
        >>> filter_instance = filter_builder.deploy(w3)

    The ``deploy`` method returns a :py:class:`web3.utils.filters.LogFilter` instance from the filter parameters generated by the filter builder. Defining multiple match values for array arguments can be accomplished easily with the filter builder:

    .. doctest:: contractmethods

        >>> filter_builder = contract.events.Transfer.build_filter()
        >>> filter_builder.args['to'].match_any(w3.eth.accounts[0], w3.eth.accounts[1])

    The filter builder blocks already defined filter parameters from being changed.

    .. doctest:: contractmethods

        >>> filter_builder = contract.events.Transfer.build_filter()
        >>> filter_builder.from_block = "latest"
        >>> filter_builder.from_block = 0
        Traceback (most recent call last):
        web3.exceptions.Web3ValueError: from_block is already set to 'latest'. Resetting filter parameters is not permitted

.. py:classmethod:: Contract.encode_abi(abi_element_identifier, args=None, kwargs=None, data=None)

    Encodes the arguments using the Ethereum ABI for the contract function that
    matches the given ``abi_element_identifier`` and arguments ``args``. The ``data`` parameter
    defaults to the function selector.

    .. doctest:: contractmethods

      >>> contract.encode_abi("approve", args=[w3.eth.accounts[0], 10])
      '0x095ea7b30000000000000000000000007e5f4552091a69125d5dfcb7b8c2659029395bdf000000000000000000000000000000000000000000000000000000000000000a'

.. py:classmethod:: Contract.all_events()

    Returns a list of all the events present in a Contract where every event is
    an instance of :py:class:`ContractEvent`.

    .. doctest:: contractmethods

        >>> contract.all_events()
        [<Event Transfer(address,address,uint256)>, <Event Approval(address,address,uint256)>]


.. py:classmethod:: Contract.get_event_by_signature(signature)

    Searches for a distinct event with matching signature. Returns an instance of
    :py:class:`ContractEvent` upon finding a match. Raises ``Web3ValueError`` if no
    match is found.

    .. doctest:: contractmethods

        >>> contract.get_event_by_signature('Transfer(address,address,uint256)')
        <Event Transfer(address,address,uint256)>


.. py:classmethod:: Contract.find_events_by_name(name)

    Searches for all events matching the provided name. Returns a list of matching
    events where every event is an instance of :py:class:`ContractEvent`. Returns an
    empty list when no match is found.

    .. doctest:: contractmethods

        >>> contract.find_events_by_name('Transfer')
        [<Event Transfer(address,address,uint256)>]


.. py:classmethod:: Contract.get_event_by_name(name)

    Searches for a distinct event matching the name. Returns an instance of
    :py:class:`ContractEvent` upon finding a match. Raises ``Web3ValueError`` if no
    match is found or if multiple matches are found.

    .. doctest:: contractmethods

        >>> contract.get_event_by_name('Approval')
        <Event Approval(address,address,uint256)>

.. py:classmethod:: Contract.find_events_by_selector(selector)

    Searches for all events matching the provided selector. Returns a list of matching
    events where every event is an instance of :py:class:`ContractEvent`. Returns an
    empty list when no match is found.

    .. doctest:: contractmethods

        >>> contract.find_events_by_selector('0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925')
        [<Event Approval(address,address,uint256)>]

.. py:classmethod:: Contract.get_event_by_selector(selector)

    Searches for a distinct event with matching selector.
    The selector can be a hexadecimal string, bytes or int.
    Returns an instance of :py:class:`ContractEvent` upon finding a match.
    Raises ``Web3ValueError`` if no match is found.

    .. doctest:: contractmethods

        >>> contract.get_event_by_selector('0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925')
        <Event Approval(address,address,uint256)>
        >>> contract.get_event_by_selector(b'\x8c[\xe1\xe5\xeb\xec}[\xd1OqB}\x1e\x84\xf3\xdd\x03\x14\xc0\xf7\xb2)\x1e[ \n\xc8\xc7\xc3\xb9%')
        <Event Approval(address,address,uint256)>
        >>> contract.get_event_by_selector(0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925)
        <Event Approval(address,address,uint256)>

.. py:classmethod:: Contract.find_events_by_topic(topic)

    Searches for all events matching the provided topic. Returns a list of matching
    events where every event is an instance of :py:class:`ContractEvent`. Returns an
    empty list when no match is found.

    .. doctest:: contractmethods

        >>> contract.find_events_by_topic('0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925')
        [<Event Approval(address,address,uint256)>]

.. py:classmethod:: Contract.get_event_by_topic(topic)

    Searches for a distinct event with matching topic.
    The topic is a hexadecimal string.
    Returns an instance of :py:class:`ContractEvent` upon finding a match.
    Raises ``Web3ValueError`` if no match is found.

    .. doctest:: contractmethods

        >>> contract.get_event_by_topic('0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925')
        <Event Approval(address,address,uint256)>

.. py:classmethod:: Contract.all_functions()

    Returns a list of all the functions present in a Contract where every function is
    an instance of :py:class:`ContractFunction`.

    .. doctest:: contractmethods

        >>> contract.all_functions()
        [<Function allowance(address,address)>, <Function approve(address,uint256)>, <Function balanceOf(address)>, <Function decimals()>, <Function name()>, <Function symbol()>, <Function totalSupply()>, <Function transfer(address,uint256)>, <Function transferFrom(address,address,uint256)>]


.. py:classmethod:: Contract.get_function_by_signature(signature)

    Searches for a distinct function with matching signature. Returns an instance of
    :py:class:`ContractFunction` upon finding a match. Raises ``Web3ValueError`` if no
    match is found.

    .. doctest:: contractmethods

        >>> contract.get_function_by_signature('approve(address,uint256)')
        <Function approve(address,uint256)>


.. py:classmethod:: Contract.find_functions_by_name(name)

    Searches for all functions matching the name. Returns a list of matching functions
    where every function is an instance of :py:class:`ContractFunction`. Returns an empty
    list when no match is found.

    .. doctest:: contractmethods

        >>> contract.find_functions_by_name('transferFrom')
        [<Function transferFrom(address,address,uint256)>]


.. py:classmethod:: Contract.get_function_by_name(name)

    Searches for a distinct function with matching name. Returns an instance of
    :py:class:`ContractFunction` upon finding a match. Raises ``Web3ValueError`` if no
    match is found or if multiple matches are found.

    .. doctest:: contractmethods

        >>> contract.get_function_by_name('decimals')
        <Function decimals()>


.. py:classmethod:: Contract.get_function_by_selector(selector)

    Searches for a distinct function with matching selector.
    The selector can be a hexadecimal string, bytes or int.
    Returns an instance of :py:class:`ContractFunction` upon finding a match.
    Raises ``Web3ValueError`` if no match is found.

    .. doctest:: contractmethods

        >>> contract.get_function_by_selector('0xdd62ed3e')
        <Function allowance(address,address)>
        >>> contract.get_function_by_selector(b'\xddb\xed>')
        <Function allowance(address,address)>
        >>> contract.get_function_by_selector(0xdd62ed3e)
        <Function allowance(address,address)>


.. py:classmethod:: Contract.find_functions_by_args(*args)

    Searches for all function with matching args. Returns a list of matching functions
    where every function is an instance of :py:class:`ContractFunction`. Returns an empty
    list when no match is found.

    .. doctest:: contractmethods

        >>> contract.find_functions_by_args(w3.eth.accounts[0], 10000)
        [<Function approve(address,uint256)>, <Function transfer(address,uint256)>]


.. py:classmethod:: Contract.get_function_by_args(*args)

    Searches for a distinct function with matching args. Returns an instance of
    :py:class:`ContractFunction` upon finding a match. Raises ``ValueError`` if no
    match is found or if multiple matches are found.

    .. doctest:: contractmethods

        >>> contract.get_function_by_args(w3.eth.accounts[0], w3.eth.accounts[1], 10000)
        <Function transferFrom(address,address,uint256)>


.. note::
    ``Contract`` methods ``all_functions``, ``get_function_by_signature``, ``find_functions_by_name``,
    ``get_function_by_name``, ``get_function_by_selector``, ``find_functions_by_args`` and
    ``get_function_by_args`` can only be used when abi is provided to the contract.


.. note::
    web3.py rejects the initialization of contracts that have more than one function
    with the same selector or signature.
    eg. ``blockHashAddendsInexpansible(uint256)`` and ``blockHashAskewLimitary(uint256)`` have the
    same selector value equal to ``0x00000000``. A contract containing both of these functions
    will be rejected.


.. _disable-strict-byte-check:

Disabling Strict Checks for Bytes Types
---------------------------------------

By default, web3 is strict when it comes to hex and bytes values, as of ``v6``.
If an abi specifies a byte size, but the value that gets passed in is not the specified
size, web3 will invalidate the value. For example, if an abi specifies a type of
``bytes4``, web3 will invalidate the following values:

.. list-table:: Invalid byte and hex strings with strict (default) bytes4 type checking
   :widths: 25 75
   :header-rows: 1

   * - Input
     - Reason
   * - ``''``
     - Needs to be prefixed with a "0x" to be interpreted as an empty hex string
   * - ``2``
     - Wrong type
   * - ``'ah'``
     - String is not valid hex
   * - ``'1234'``
     - Needs to either be a bytestring (b'1234') or be a hex value of the right size, prefixed with 0x (in this case: '0x31323334')
   * - ``b''``
     - Needs to have exactly 4 bytes
   * - ``b'ab'``
     - Needs to have exactly 4 bytes
   * - ``'0xab'``
     - Needs to have exactly 4 bytes
   * - ``'0x6162636464'``
     - Needs to have exactly 4 bytes

However, you may want to be less strict with acceptable values for bytes types.
This may prove useful if you trust that values coming through are what they are
meant to be with respect to the ABI. In this case, the automatic padding might be
convenient for inferred types. For this, you can set the
:meth:`w3.strict_bytes_type_checking` flag to ``False``, which is available on the
Web3 instance. A Web3 instance which has this flag set to ``False`` will have a less
strict set of rules on which values are accepted. A ``bytes`` type will allow values as
a hex string, a bytestring, or a regular Python string that can be decoded as a hex.
0x-prefixed hex strings are also not required.

 - A Python string that is not prefixed with ``0x`` is valid.
 - A bytestring whose length is less than the specified byte size is valid.

.. list-table:: Valid byte and hex strings for a non-strict bytes4 type
   :widths: 25 75
   :header-rows: 1

   * - Input
     - Normalizes to
   * - ``''``
     - ``b'\x00\x00\x00\x00'``
   * - ``'0x'``
     - ``b'\x00\x00\x00\x00'``
   * - ``b''``
     - ``b'\x00\x00\x00\x00'``
   * - ``b'ab'``
     - ``b'ab\x00\x00'``
   * - ``'0xab'``
     - ``b'\xab\x00\x00\x00'``
   * - ``'1234'``
     - ``b'\x124\x00\x00'``
   * - ``'0x61626364'``
     - ``b'abcd'``
   * - ``'1234'``
     - ``b'1234'``


Taking the following contract code as an example:

.. testsetup:: arrayscontract

    from web3 import Web3
    w3 = Web3(Web3.EthereumTesterProvider())
    bytecode = "608060405234801561001057600080fd5b506040516106103803806106108339810180604052602081101561003357600080fd5b81019080805164010000000081111561004b57600080fd5b8281019050602081018481111561006157600080fd5b815185602082028301116401000000008211171561007e57600080fd5b5050929190505050806000908051906020019061009c9291906100a3565b505061019c565b82805482825590600052602060002090600f0160109004810192821561015a5791602002820160005b8382111561012a57835183826101000a81548161ffff02191690837e010000000000000000000000000000000000000000000000000000000000009004021790555092602001926002016020816001010492830192600103026100cc565b80156101585782816101000a81549061ffff021916905560020160208160010104928301926001030261012a565b505b509050610167919061016b565b5090565b61019991905b8082111561019557600081816101000a81549061ffff021916905550600101610171565b5090565b90565b610465806101ab6000396000f3fe608060405260043610610051576000357c0100000000000000000000000000000000000000000000000000000000900480633b3230ee14610056578063d7c8a410146100e7578063dfe3136814610153575b600080fd5b34801561006257600080fd5b5061008f6004803603602081101561007957600080fd5b8101908080359060200190929190505050610218565b60405180827dffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff19167dffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff1916815260200191505060405180910390f35b3480156100f357600080fd5b506100fc61026c565b6040518080602001828103825283818151815260200191508051906020019060200280838360005b8381101561013f578082015181840152602081019050610124565b505050509050019250505060405180910390f35b34801561015f57600080fd5b506102166004803603602081101561017657600080fd5b810190808035906020019064010000000081111561019357600080fd5b8201836020820111156101a557600080fd5b803590602001918460208302840111640100000000831117156101c757600080fd5b919080806020026020016040519081016040528093929190818152602001838360200280828437600081840152601f19601f820116905080830192505050505050509192919290505050610326565b005b60008181548110151561022757fe5b9060005260206000209060109182820401919006600202915054906101000a90047e010000000000000000000000000000000000000000000000000000000000000281565b6060600080548060200260200160405190810160405280929190818152602001828054801561031c57602002820191906000526020600020906000905b82829054906101000a90047e01000000000000000000000000000000000000000000000000000000000000027dffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff1916815260200190600201906020826001010492830192600103820291508084116102a95790505b5050505050905090565b806000908051906020019061033c929190610340565b5050565b82805482825590600052602060002090600f016010900481019282156103f75791602002820160005b838211156103c757835183826101000a81548161ffff02191690837e01000000000000000000000000000000000000000000000000000000000000900402179055509260200192600201602081600101049283019260010302610369565b80156103f55782816101000a81549061ffff02191690556002016020816001010492830192600103026103c7565b505b5090506104049190610408565b5090565b61043691905b8082111561043257600081816101000a81549061ffff02191690555060010161040e565b5090565b9056fea165627a7a72305820a8f9f1f4815c1eedfb8df31298a5cd13b198895de878871328b5d96296b69b4e0029"
    abi = '''
      [
        {
          "constant": true,
          "inputs": [
            {
              "name": "",
              "type": "uint256"
            }
          ],
          "name": "bytes2Value",
          "outputs": [
            {
              "name": "",
              "type": "bytes2"
            }
          ],
          "payable": false,
          "stateMutability": "view",
          "type": "function"
        },
        {
          "constant": true,
          "inputs": [],
          "name": "getBytes2Value",
          "outputs": [
            {
              "name": "",
              "type": "bytes2[]"
            }
          ],
          "payable": false,
          "stateMutability": "view",
          "type": "function"
        },
        {
          "constant": false,
          "inputs": [
            {
              "name": "_bytes2Value",
              "type": "bytes2[]"
            }
          ],
          "name": "setBytes2Value",
          "outputs": [],
          "payable": false,
          "stateMutability": "nonpayable",
          "type": "function"
        },
        {
          "inputs": [
            {
              "name": "_bytes2Value",
              "type": "bytes2[]"
            }
          ],
          "payable": false,
          "stateMutability": "nonpayable",
          "type": "constructor"
        }
      ]
     '''.strip()

.. code-block:: python

    >>> #  pragma solidity >=0.4.22 <0.6.0;
    ...
    ... #   contract ArraysContract {
    ... #      bytes2[] public bytes2Value;

    ... #      constructor(bytes2[] memory _bytes2Value) public {
    ... #          bytes2Value = _bytes2Value;
    ... #      }

    ... #      function setBytes2Value(bytes2[] memory _bytes2Value) public {
    ... #          bytes2Value = _bytes2Value;
    ... #      }

    ... #      function getBytes2Value() public view returns (bytes2[] memory) {
    ... #          return bytes2Value;
    ... #      }
    ... #  }

    >>> # abi = "..."
    >>> # bytecode = "6080..."

.. doctest:: arrayscontract

    >>> arrays_contract_instance = w3.eth.contract(abi=abi, bytecode=bytecode)

    >>> tx_hash = arrays_contract_instance.constructor([b'bb']).transact()
    >>> tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    >>> arrays_contract = w3.eth.contract(
    ...     address=tx_receipt.contractAddress,
    ...     abi=abi
    ... )
    >>> arrays_contract.functions.getBytes2Value().call()
    [b'bb']

    >>> # set value with appropriate byte size
    >>> arrays_contract.functions.setBytes2Value([b'aa']).transact({'gas': 420000, "maxPriorityFeePerGas": 10 ** 9, "maxFeePerGas": 10 ** 9})
    HexBytes('0xcb95151142ea56dbf2753d70388aef202a7bb5a1e323d448bc19f1d2e1fe3dc9')
    >>> # check value
    >>> arrays_contract.functions.getBytes2Value().call()
    [b'aa']

    >>> # trying to set value without appropriate size (bytes2) is not valid
    >>> arrays_contract.functions.setBytes2Value([b'b']).transact()
    Traceback (most recent call last):
       ...
    web3.exceptions.MismatchedABI:
    Could not identify the intended function with name
    >>> # check value is still b'aa'
    >>> arrays_contract.functions.getBytes2Value().call()
    [b'aa']

    >>> # disabling strict byte checking...
    >>> w3.strict_bytes_type_checking = False

    >>> tx_hash = arrays_contract_instance.constructor([b'b']).transact()
    >>> tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    >>> arrays_contract = w3.eth.contract(
    ...     address=tx_receipt.contractAddress,
    ...     abi=abi
    ... )
    >>> # check value is zero-padded... i.e. b'b\x00'
    >>> arrays_contract.functions.getBytes2Value().call()
    [b'b\x00']

    >>> # set the flag back to True
    >>> w3.strict_bytes_type_checking = True

    >>> arrays_contract.functions.setBytes2Value([b'a']).transact()
    Traceback (most recent call last):
       ...
    web3.exceptions.MismatchedABI:
    Could not identify the intended function with name

.. _contract-functions:

Contract Functions
------------------

The named functions exposed through the :py:attr:`Contract.functions` property are
of the ContractFunction type. This class is not to be used directly,
but instead through :py:attr:`Contract.functions`.

For example:

    .. code-block:: python

        myContract = web3.eth.contract(address=contract_address, abi=contract_abi)
        twentyone = myContract.functions.multiply7(3).call()

If you have the function name in a variable, you might prefer this alternative:

    .. code-block:: python

        func_to_call = 'multiply7'
        contract_func = myContract.functions[func_to_call]
        twentyone = contract_func(3).call()

You can also interact with contract functions without parentheses if the function doesn't
take any arguments. For example:

    .. code-block:: python

        >>> myContract.functions.return13.call()
        13
        >>> myContract.functions.return13().call()
        13

In cases where functions are overloaded and use arguments of similar types, a function
may resolve to an undesired function when using the method syntax. For example, given
two functions with the same name that take a single argument of differing types of
``bytes`` and ``bytes32``. When a reference to :meth:`contract.functions.setBytes(b'1')`
is used, the function will resolve as the one that takes ``bytes``. If a value is passed
that was meant to be 32 bytes but the given argument was off by one, the function
reference will still use the one that takes ``bytes``.

When in doubt, use explicit function references to the signature. Use bracket notation
(:meth:`contract.functions["setBytes(bytes32)"](b'')`) or the contract API
`contract.get_function_by_signature("setBytes(bytes32)")` to retrieve the desired
function. This will ensure an exception is raised if the argument is not strictly
32 bytes in length.

.. py:class:: ContractFunction

Attributes
~~~~~~~~~~

The :py:class:`ContractFunction` class provides attributes for each function. Access the function attributes through `Contract.functions.myMethod`.

.. py:attribute:: ContractFunction.myMethod(*args, **kwargs).abi_element_identifier

    The signature of the function assigned to the class ``__name__`` during initialization.
    Fallback and Receive functions will be assigned as classes :py:class:`FallbackFn` or
    :py:class:`ReceiveFn` respectively.

.. py:attribute:: ContractFunction.myMethod(*args, **kwargs).name

    A string representing the function, receive or fallback name.

    Use :py:attr:`ContractFunction.signature` when the function arguments are needed.

    This is an alias of :py:attr:`ContractFunction.fn_name`.

.. py:attribute:: ContractFunction.myMethod(*args, **kwargs).signature

    A string representing the function, receive or fallback signature.

.. py:attribute:: ContractFunction.myMethod(*args, **kwargs).selector

    A HexStr encoded from the first four bytes of the function signature.

.. py:attribute:: ContractFunction.myMethod(*args, **kwargs).abi

    The function ABI with the type, name, inputs and outputs.

.. py:attribute:: ContractFunction.myMethod(*args, **kwargs).arguments

    A tuple of all function inputs, normalized so that `kwargs` themselves are
    flattened into a tuple as returned by :py:meth:`eth_utils.abi.get_normalized_abi_inputs`.

.. py:attribute:: ContractFunction.myMethod(*args, **kwargs).argument_names

    The function input names.

.. py:attribute:: ContractFunction.myMethod(*args, **kwargs).argument_types

    The function input types.

Methods
~~~~~~~

:py:class:`ContractFunction` provides methods to interact with contract functions.
Positional and keyword arguments supplied to the contract function subclass
will be used to find the contract function by signature,
and forwarded to the contract function when applicable.

`EIP-3668 <https://eips.ethereum.org/EIPS/eip-3668>`_ introduced support for the ``OffchainLookup`` revert /
CCIP Read support. CCIP Read is set to ``True`` for calls by default, as recommended in EIP-3668. This is done via a
global ``global_ccip_read_enabled`` flag on the provider. If raising the ``OffchainLookup`` revert is preferred for a
specific call, the ``ccip_read_enabled`` flag on the call may be set to ``False``.

    .. code-block:: python

        >>> # raises the revert instead of handling the offchain lookup
        >>> myContract.functions.revertsWithOffchainLookup(myData).call(ccip_read_enabled=False)
        *** web3.exceptions.OffchainLookup

Disabling CCIP Read support can be useful if a transaction needs to be sent to the callback function. In such cases,
"preflighting" with an ``eth_call``, handling the ``OffchainLookup``, and sending the data via a transaction may be
necessary. See :ref:`ccip-read-example` in the examples section for how to preflight a transaction with a contract call.

Similarly, if CCIP Read is globally set to ``False`` via the ``global_ccip_read_enabled`` flag on the provider, it may be
enabled on a per-call basis - overriding the global flag. This ensures only explicitly enabled calls will handle the
``OffchainLookup`` revert appropriately.

    .. code-block:: python

        >>> # global flag set to `False`
        >>> w3.provider.global_ccip_read_enabled = False

        >>> # does not raise the revert since explicitly enabled on the call:
        >>> response = myContract.functions.revertsWithOffchainLookup(myData).call(ccip_read_enabled=True)

If the function called results in a ``revert`` error, a ``ContractLogicError`` will be raised.
If there is an error message with the error, web3.py attempts to parse the
message that comes back and return it to the user as the error string.
As of v6.3.0, the raw data is also returned and
can be accessed via the ``data`` attribute on ``ContractLogicError``.

.. py:method:: ContractFunction.transact(transaction)

    Execute the specified function by sending a new public transaction.

    Refer to the following invocation:

    .. code-block:: python

        myContract.functions.myMethod(*args, **kwargs).transact(transaction)

    The first portion of the function call ``myMethod(*args, **kwargs)``
    selects the appropriate contract function based on the name and provided
    argument.  Arguments can be provided as positional arguments, keyword
    arguments, or a mix of the two.

    The end portion of this function call ``transact(transaction)`` takes a
    single parameter which should be a python dictionary conforming to
    the same format as the ``web3.eth.send_transaction(transaction)`` method.
    This dictionary may not contain the keys ``data``.

    If any of the ``args`` or ``kwargs`` specified in the ABI are an ``address`` type, they
    will accept ENS names.

    If a ``gas`` value is not provided, then the ``gas`` value for the
    method transaction will be created using the ``web3.eth.estimate_gas()``
    method.

    Returns the transaction hash.

    .. code-block:: python

        >>> token_contract.functions.transfer(web3.eth.accounts[1], 12345).transact()
        "0x4e3a3754410177e6937ef1f84bba68ea139e8d1a2258c5f85db9f1cd715a1bdd"


.. py:method:: ContractFunction.call(transaction, block_identifier='latest')

    Call a contract function, executing the transaction locally using the
    ``eth_call`` API.  This will not create a new public transaction.

    Refer to the following invocation:

    .. code-block:: python

        myContract.functions.myMethod(*args, **kwargs).call(transaction)

    This method behaves the same as the :py:meth:`ContractFunction.transact` method,
    with transaction details being passed into the end portion of the
    function call, and function arguments being passed into the first portion.

    Returns the return value of the executed function.

    .. code-block:: python

        >>> my_contract.functions.multiply7(3).call()
        21
        >>> token_contract.functions.myBalance().call({'from': web3.eth.accounts[0]})
        12345  # the token balance for `web3.eth.accounts[0]`
        >>> token_contract.functions.myBalance().call({'from': web3.eth.accounts[1]})
        54321  # the token balance for the account `web3.eth.accounts[1]`

    You can call the method at a historical block using ``block_identifier``. Some examples:

    .. code-block:: python

        # You can call your contract method at a block number:
        >>> token_contract.functions.myBalance().call(block_identifier=10)

        # or a number of blocks back from pending,
        # in this case, the block just before the latest block:
        >>> token_contract.functions.myBalance().call(block_identifier=-2)

        # or a block hash:
        >>> token_contract.functions.myBalance().call(block_identifier='0x4ff4a38b278ab49f7739d3a4ed4e12714386a9fdf72192f2e8f7da7822f10b4d')
        >>> token_contract.functions.myBalance().call(block_identifier=b'O\xf4\xa3\x8b\'\x8a\xb4\x9fw9\xd3\xa4\xedN\x12qC\x86\xa9\xfd\xf7!\x92\xf2\xe8\xf7\xdax"\xf1\x0bM')

        # Latest is the default, so this is redundant:
        >>> token_contract.functions.myBalance().call(block_identifier='latest')

        # You can check the state after your pending transactions (if supported by your node):
        >>> token_contract.functions.myBalance().call(block_identifier='pending')

    Passing the ``block_identifier`` parameter for past block numbers requires that your Ethereum API node
    is running in the more expensive archive node mode. Normally synced Ethereum nodes will fail with
    a "missing trie node" error, because Ethereum node may have purged the past state from its database.
    `More information about archival nodes here <https://ethereum.stackexchange.com/a/84200/620>`_.

.. py:method:: ContractFunction.estimate_gas(transaction, block_identifier=None)

    Call a contract function, executing the transaction locally using the
    ``eth_call`` API.  This will not create a new public transaction.

    Refer to the following invocation:

    .. code-block:: python

        myContract.functions.myMethod(*args, **kwargs).estimate_gas(transaction)

    This method behaves the same as the :py:meth:`ContractFunction.transact` method,
    with transaction details being passed into the end portion of the
    function call, and function arguments being passed into the first portion.

    Returns the amount of gas consumed which can be used as a gas estimate for
    executing this transaction publicly.

    .. code-block:: python

        >>> my_contract.functions.multiply7(3).estimate_gas()
        42650

    .. note::
        The parameter ``block_identifier`` is not enabled in geth nodes,
        hence passing a value of ``block_identifier`` when connected to a geth
        nodes would result in an error like:  ``ValueError: {'code': -32602, 'message': 'too many arguments, want at most 1'}``

.. py:method:: ContractFunction.build_transaction(transaction)

    Builds a transaction dictionary based on the contract function call specified.

    Refer to the following invocation:

    .. code-block:: python

        myContract.functions.myMethod(*args, **kwargs).build_transaction(transaction)

    This method behaves the same as the :py:meth:`Contract.transact` method,
    with transaction details being passed into the end portion of the
    function call, and function arguments being passed into the first portion.

    .. note::
        `nonce` is not returned as part of the transaction dictionary unless it is
        specified in the first portion of the function call:

        .. code-block:: python

            >>> math_contract.functions.increment(5).build_transaction({'nonce': 10})

        You may use :meth:`~web3.eth.Eth.getTransactionCount` to get the current nonce
        for an account. Therefore a shortcut for producing a transaction dictionary with
        nonce included looks like:

        .. code-block:: python

            >>> math_contract.functions.increment(5).build_transaction({'nonce': web3.eth.get_transaction_count('0xF5...')})

    Returns a transaction dictionary. This transaction dictionary can then be sent using
    :meth:`~web3.eth.Eth.send_transaction`.

    Additionally, the dictionary may be used for offline transaction signing using
    :meth:`~web3.eth.account.Account.sign_transaction`.

    .. code-block:: python

        >>> math_contract.functions.increment(5).build_transaction({'maxFeePerGas': 2000000000, 'maxPriorityFeePerGas': 1000000000})
        {
            'to': '0x582AC4D8929f58c217d4a52aDD361AE470a8a4cD',
            'data': '0x7cf5dab00000000000000000000000000000000000000000000000000000000000000005',
            'value': 0,
            'gas': 43242,
            'maxFeePerGas': 2000000000,
            'maxPriorityFeePerGas': 1000000000,
            'chainId': 1
        }

.. _fallback-function:

Fallback Function
~~~~~~~~~~~~~~~~~

    The Contract Factory also offers an API to interact with the fallback function, which supports four methods like
    normal functions:

.. py:method:: Contract.fallback.call(transaction)

    Call fallback function, executing the transaction locally using the
    ``eth_call`` API.  This will not create a new public transaction.

.. py:method:: Contract.fallback.estimate_gas(transaction)

    Call fallback function and return the gas estimation.

.. py:method:: Contract.fallback.transact(transaction)

    Execute fallback function by sending a new public transaction.

.. py:method:: Contract.fallback.build_transaction(transaction)

    Builds a transaction dictionary based on the contract fallback function call.

Contract Events
---------------

The named events exposed through the :py:attr:`Contract.events` property are of the ContractEvent type. This class is not to be used directly, but instead through :py:attr:`Contract.events`.

For example:

    .. code-block:: python

        myContract = web3.eth.contract(address=contract_address, abi=contract_abi)
        tx_hash = myContract.functions.myFunction().transact()
        receipt = web3.eth.get_transaction_receipt(tx_hash)
        myContract.events.MyEvent().process_receipt(receipt)

.. py:class:: ContractEvent

Attributes
~~~~~~~~~~

The :py:class:`ContractEvent` class provides attributes for each event. Access the event attributes through `Contract.events.MyEvent`.

.. py:attribute:: ContractEvent.MyEvent(*args, **kwargs).abi_element_identifier

    The signature of the event assigned to the class ``__name__`` during initialization.

.. py:attribute:: ContractEvent.MyEvent(*args, **kwargs).name

    A string representing the event, receive or fallback name.

    Use :py:attr:`ContractEvent.MyEvent(*args, **kwargs).signature` when the event arguments are needed.

    This is an alias of :py:attr:`ContractEvent.MyEvent(*args, **kwargs).event_name`.

.. py:attribute:: ContractEvent.MyEvent(*args, **kwargs).signature

    A string representing the event signature.

.. py:attribute:: ContractEvent.MyEvent(*args, **kwargs).abi

    The event ABI with the type, name, inputs.

.. py:attribute:: ContractEvent.MyEvent(*args, **kwargs).argument_names

    The event input names.

.. py:attribute:: ContractEvent.MyEvent(*args, **kwargs).argument_types

    The event input types.

.. py:attribute:: ContractEvent.MyEvent(*args, **kwargs).topic

    The event topic represented by a hex encoded string from the keccak signature.

Methods
~~~~~~~

:py:class:`ContractEvent` provides methods to interact with contract events. Positional and keyword arguments supplied to the contract event subclass will be used to find the contract event by signature.

.. _contract_get_logs:

.. py:method:: ContractEvent.get_logs(from_block=None, to_block="latest", block_hash=None, argument_filters={})
   :noindex:

   Fetches all logs for a given event within the specified block range or block hash.

   Returns a list of decoded event logs sorted by ``logIndex``.

    ``argument_filters`` is an optional dictionary argument that can be used to filter
    for logs where the event's argument values match the values provided in the
    dictionary. The keys must match the event argument names as they exist in the ABI.
    The values can either be a single value or a list of values to match against. If a
    list is provided, the logs will be filtered for any logs that match any of the
    values in the list. Indexed arguments are filtered pre-call by building specific
    ``topics`` to filter for. Non-indexed arguments are filtered by the library after
    the logs are fetched from the node.

    .. code-block:: python

        my_contract = web3.eth.contract(address=contract_address, abi=contract_abi)

        # get ``MyEvent`` logs from block 1337 to block 2337 where the value for the
        # event argument "eventArg1" is either 1, 2, or 3
        my_contract.events.MyEvent().get_logs(
            argument_filters={"eventArg1": [1, 2, 3]},
            from_block=1337,
            to_block=2337,
        )

.. _process_receipt:

.. py:method:: ContractEvent.process_receipt(transaction_receipt, errors=WARN)
   :noindex:

   Extracts the pertinent logs from a transaction receipt.

   If there are no errors, ``process_receipt`` returns a tuple of :ref:`Event Log Objects <event-log-object>`, emitted from the event (e.g. ``MyEvent``),
   with decoded output.

   .. code-block:: python

       >>> tx_hash = contract.functions.myFunction(12345).transact({'to':contract_address})
       >>> tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
       >>> rich_logs = contract.events.MyEvent().process_receipt(tx_receipt)
       >>> rich_logs[0]['args']
       {'myArg': 12345}

   If there are errors, the logs will be handled differently depending on the flag that is passed in:

     - ``WARN`` (default) - logs a warning to the console for the log that has an error, and discards the log. Returns any logs that are able to be processed.
     - ``STRICT`` - stops all processing and raises the error encountered.
     - ``IGNORE`` - returns any raw logs that raised an error with an added "errors" field, along with any other logs were able to be processed.
     - ``DISCARD`` - silently discards any logs that have errors, and returns processed logs that don't have errors.

   An event log error flag needs to be imported from ``web3/logs.py``.

   .. code-block:: python

       >>> tx_hash = contract.functions.myFunction(12345).transact({'to':contract_address})
       >>> tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
       >>> processed_logs = contract.events.MyEvent().process_receipt(tx_receipt)
       >>> processed_logs
       (
          AttributeDict({
              'args': AttributeDict({}),
              'event': 'MyEvent',
              'logIndex': 0,
              'transactionIndex': 0,
              'transactionHash': HexBytes('0xfb95ccb6ab39e19821fb339dee33e7afe2545527725b61c64490a5613f8d11fa'),
              'address': '0xF2E246BB76DF876Cef8b38ae84130F4F55De395b',
              'blockHash': HexBytes('0xd74c3e8bdb19337987b987aee0fa48ed43f8f2318edfc84e3a8643e009592a68'),
              'blockNumber': 3
          })
       )


       # Or, if there were errors encountered during processing:
       >>> from web3.logs import STRICT, IGNORE, DISCARD, WARN
       >>> processed_logs = contract.events.MyEvent().process_receipt(tx_receipt, errors=IGNORE)
       >>> processed_logs
       (
           AttributeDict({
               'type': 'mined',
               'logIndex': 0,
               'transactionIndex': 0,
               'transactionHash': HexBytes('0x01682095d5abb0270d11a31139b9a1f410b363c84add467004e728ec831bd529'),
               'blockHash': HexBytes('0x92abf9325a3959a911a2581e9ea36cba3060d8b293b50e5738ff959feb95258a'),
               'blockNumber': 5,
               'address': '0xF2E246BB76DF876Cef8b38ae84130F4F55De395b',
               'data': '0x0000000000000000000000000000000000000000000000000000000000003039',
               'topics': [
                   HexBytes('0xf70fe689e290d8ce2b2a388ac28db36fbb0e16a6d89c6804c461f65a1b40bb15')
               ],
               'errors': LogTopicError('Expected 1 log topics.  Got 0')})
          })
       )
       >>> processed_logs = contract.events.MyEvent().process_receipt(tx_receipt, errors=DISCARD)
       >>> assert processed_logs == ()
       True

.. py:method:: ContractEvent.process_log(log)

   Similar to process_receipt_, but only processes one log at a time, instead of a whole transaction receipt.
   Will return a single :ref:`Event Log Object <event-log-object>` if there are no errors encountered during processing. If an error is encountered during processing, it will be raised.

   .. code-block:: python

       >>> tx_hash = contract.functions.myFunction(12345).transact({'to':contract_address})
       >>> tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
       >>> log_to_process = tx_receipt['logs'][0]
       >>> processed_log = contract.events.MyEvent().process_log(log_to_process)
       >>> processed_log
       AttributeDict({
           'args': AttributeDict({}),
           'event': 'MyEvent',
           'logIndex': 0,
           'transactionIndex': 0,
           'transactionHash': HexBytes('0xfb95ccb6ab39e19821fb339dee33e7afe2545527725b61c64490a5613f8d11fa'),
           'address': '0xF2E246BB76DF876Cef8b38ae84130F4F55De395b',
           'blockHash': HexBytes('0xd74c3e8bdb19337987b987aee0fa48ed43f8f2318edfc84e3a8643e009592a68'),
           'blockNumber': 3
       })


.. _event-log-object:

Event Log Object
~~~~~~~~~~~~~~~~

    The Event Log Object is a python dictionary with the following keys:

    * ``args``: Dictionary - The arguments coming from the event.
    * ``event``: String - The event name.
    * ``logIndex``: Number - integer of the log index position in the block.
    * ``transactionIndex``: Number - integer of the transactions index position
      log was created from.
    * ``transactionHash``: String, 32 Bytes - hash of the transactions this log
      was created from.
    * ``address``: String, 32 Bytes - address from which this log originated.
    * ``blockHash``: String, 32 Bytes - hash of the block where this log was
      in. null when it's pending.
    * ``blockNumber``: Number - the block number where this log was in. null
      when it's pending.

.. testsetup:: create_filter

    from web3 import Web3
    from hexbytes import HexBytes
    w3 = Web3(Web3.EthereumTesterProvider())
    bytecode = '6060604052341561000c57fe5b604051602080610acb833981016040528080519060200190919050505b620f42408114151561003b5760006000fd5b670de0b6b3a76400008102600281905550600254600060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055505b505b610a27806100a46000396000f30060606040523615610097576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806306fdde0314610099578063095ea7b31461013257806318160ddd1461018957806323b872dd146101af578063313ce5671461022557806370a082311461025157806395d89b411461029b578063a9059cbb14610334578063dd62ed3e1461038b575bfe5b34156100a157fe5b6100a96103f4565b60405180806020018281038252838181518152602001915080519060200190808383600083146100f8575b8051825260208311156100f8576020820191506020810190506020830392506100d4565b505050905090810190601f1680156101245780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561013a57fe5b61016f600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803590602001909190505061042e565b604051808215151515815260200191505060405180910390f35b341561019157fe5b610199610521565b6040518082815260200191505060405180910390f35b34156101b757fe5b61020b600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff16906020019091908035906020019091905050610527565b604051808215151515815260200191505060405180910390f35b341561022d57fe5b610235610791565b604051808260ff1660ff16815260200191505060405180910390f35b341561025957fe5b610285600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610796565b6040518082815260200191505060405180910390f35b34156102a357fe5b6102ab6107e0565b60405180806020018281038252838181518152602001915080519060200190808383600083146102fa575b8051825260208311156102fa576020820191506020810190506020830392506102d6565b505050905090810190601f1680156103265780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561033c57fe5b610371600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803590602001909190505061081a565b604051808215151515815260200191505060405180910390f35b341561039357fe5b6103de600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610973565b6040518082815260200191505060405180910390f35b604060405190810160405280600981526020017f54657374546f6b656e000000000000000000000000000000000000000000000081525081565b600081600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925846040518082815260200191505060405180910390a3600190505b92915050565b60025481565b600081600060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205410806105f1575081600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054105b156105fc5760006000fd5b81600060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254019250508190555081600060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254039250508190555081600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825403925050819055508273ffffffffffffffffffffffffffffffffffffffff168473ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a3600190505b9392505050565b601281565b6000600060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490505b919050565b604060405190810160405280600481526020017f544553540000000000000000000000000000000000000000000000000000000081525081565b600081600060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205410156108695760006000fd5b81600060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254039250508190555081600060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825401925050819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a3600190505b92915050565b6000600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490505b929150505600a165627a7a723058205071371ee2a4a1be3c96e77d939cdc26161a256fdd638efc08bd33dfc65d3b850029'
    ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function","stateMutability":"nonpayable"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function","stateMutability":"nonpayable"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function","stateMutability":"nonpayable"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function","stateMutability":"view"},{"inputs":[{"name":"_totalSupply","type":"uint256"}],"payable":false,"type":"constructor","stateMutability":"nonpayable"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"}]'
    my_token_contract = w3.eth.contract(abi=ABI, bytecode=bytecode)
    alice, bob = w3.eth.accounts[0], w3.eth.accounts[1]
    assert alice == '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf', alice
    assert bob == '0x2B5AD5c4795c026514f8317c7a215E218DcCD6cF', bob
    tx_hash = my_token_contract.constructor(1000000).transact({'from': alice, 'gas': 899000, 'gasPrice': Web3.to_wei(1, 'gwei')})
    assert tx_hash == HexBytes('0x49e3da72a95e4074a9eaea7b438c73ca154627d317e58abeae914e3769a15044'), tx_hash
    txn_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    assert txn_receipt['contractAddress'] == '0xF2E246BB76DF876Cef8b38ae84130F4F55De395b', txn_receipt['contractAddress']
    contract_address = txn_receipt['contractAddress']
    contract = w3.eth.contract(contract_address, abi=ABI)
    total_supply = contract.functions.totalSupply().call()
    decimals = 10 ** 18
    assert total_supply == 1000000 * decimals, total_supply
    tx_hash = contract.functions.transfer(alice, 10).transact({'gas': 899000, 'gasPrice': Web3.to_wei(1, 'gwei')})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

.. doctest:: create_filter

    >>> transfer_filter = my_token_contract.events.Transfer.create_filter(from_block="0x0", argument_filters={'from': '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf'})
    >>> transfer_filter.get_new_entries()
    [AttributeDict({'args': AttributeDict({'from': '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf',
     'to': '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf',
     'value': 10}),
     'event': 'Transfer',
     'logIndex': 0,
     'transactionIndex': 0,
     'transactionHash': HexBytes('0x9da859237e7259832b913d51cb128c8d73d1866056f7a41b52003c953e749678'),
     'address': '0xF2E246BB76DF876Cef8b38ae84130F4F55De395b',
     'blockHash': HexBytes('...'),
     'blockNumber': 2})]
    >>> transfer_filter.get_new_entries()
    []
    >>> tx_hash = contract.functions.transfer(alice, 10).transact({'gas': 899000, 'gasPrice': 1000000000})
    >>> tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    >>> transfer_filter.get_new_entries()
    [AttributeDict({'args': AttributeDict({'from': '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf',
     'to': '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf',
     'value': 10}),
     'event': 'Transfer',
     'logIndex': 0,
     'transactionIndex': 0,
     'transactionHash': HexBytes('...'),
     'address': '0xF2E246BB76DF876Cef8b38ae84130F4F55De395b',
     'blockHash': HexBytes('...'),
     'blockNumber': 3})]
    >>> transfer_filter.get_all_entries()
    [AttributeDict({'args': AttributeDict({'from': '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf',
     'to': '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf',
     'value': 10}),
     'event': 'Transfer',
     'logIndex': 0,
     'transactionIndex': 0,
     'transactionHash': HexBytes('...'),
     'address': '0xF2E246BB76DF876Cef8b38ae84130F4F55De395b',
     'blockHash': HexBytes('...'),
     'blockNumber': 2}),
     AttributeDict({'args': AttributeDict({'from': '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf',
     'to': '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf',
     'value': 10}),
     'event': 'Transfer',
     'logIndex': 0,
     'transactionIndex': 0,
     'transactionHash': HexBytes('...'),
     'address': '0xF2E246BB76DF876Cef8b38ae84130F4F55De395b',
     'blockHash': HexBytes('...'),
     'blockNumber': 3})]

Utils
-----

.. py:classmethod:: Contract.decode_function_input(data)

    Decodes the transaction data used to invoke a smart contract function, and returns
    :py:class:`ContractFunction` and decoded parameters as :py:class:`dict`.

    .. code-block:: python

        >>> transaction = w3.eth.get_transaction('0x5798fbc45e3b63832abc4984b0f3574a13545f415dd672cd8540cd71f735db56')
        >>> transaction.input
        '0x612e45a3000000000000000000000000b656b2a9c3b2416437a811e07466ca712f5a5b5a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000093a80000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000116c6f6e656c792c20736f206c6f6e656c7900000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
        >>> contract.decode_function_input(transaction.input)
        (<Function newProposal(address,uint256,string,bytes,uint256,bool)>,
         {'_recipient': '0xB656b2a9c3b2416437A811e07466cA712F5a5b5a',
          '_amount': 0,
          '_description': b'lonely, so lonely',
          '_transactionData': b'',
          '_debatingPeriod': 604800,
          '_newCurator': True})

ContractCaller
--------------

.. py:class:: ContractCaller

The ``ContractCaller`` class provides an API to call functions in a contract. This class
is not to be used directly, but instead through ``Contract.caller``.

There are a number of different ways to invoke the ``ContractCaller``.

For example:

.. testsetup:: contractcaller

   import json
   from web3 import Web3
   w3 = Web3(Web3.EthereumTesterProvider())
   bytecode = "0x606060405261022e806100126000396000f360606040523615610074576000357c01000000000000000000000000000000000000000000000000000000009004806316216f391461007657806361bc221a146100995780637cf5dab0146100bc578063a5f3c23b146100e8578063d09de08a1461011d578063dcf537b11461014057610074565b005b610083600480505061016c565b6040518082815260200191505060405180910390f35b6100a6600480505061017f565b6040518082815260200191505060405180910390f35b6100d26004808035906020019091905050610188565b6040518082815260200191505060405180910390f35b61010760048080359060200190919080359060200190919050506101ea565b6040518082815260200191505060405180910390f35b61012a6004805050610201565b6040518082815260200191505060405180910390f35b6101566004808035906020019091905050610217565b6040518082815260200191505060405180910390f35b6000600d9050805080905061017c565b90565b60006000505481565b6000816000600082828250540192505081905550600060005054905080507f3496c3ede4ec3ab3686712aa1c238593ea6a42df83f98a5ec7df9834cfa577c5816040518082815260200191505060405180910390a18090506101e5565b919050565b6000818301905080508090506101fb565b92915050565b600061020d6001610188565b9050610214565b90565b60006007820290508050809050610229565b91905056"
   ABI = json.loads('[{"constant":false,"inputs":[],"name":"return13","outputs":[{"name":"result","type":"int256"}],"type":"function"},{"constant":true,"inputs":[],"name":"counter","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"amt","type":"uint256"}],"name":"increment","outputs":[{"name":"result","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"a","type":"int256"},{"name":"b","type":"int256"}],"name":"add","outputs":[{"name":"result","type":"int256"}],"type":"function"},{"constant":false,"inputs":[],"name":"increment","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"a","type":"int256"}],"name":"multiply7","outputs":[{"name":"result","type":"int256"}],"type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"value","type":"uint256"}],"name":"increased","type":"event"}]')
   contract = w3.eth.contract(abi=ABI, bytecode=bytecode)
   deploy_txn = contract.constructor().transact()
   deploy_receipt = w3.eth.wait_for_transaction_receipt(deploy_txn)
   address = deploy_receipt.contractAddress

.. doctest:: contractcaller

   >>> myContract = w3.eth.contract(address=address, abi=ABI)
   >>> twentyone = myContract.caller.multiply7(3)
   >>> twentyone
   21

It can also be invoked using parentheses:

.. doctest:: contractcaller

   >>> twentyone = myContract.caller().multiply7(3)
   >>> twentyone
   21

And a transaction dictionary, with or without the ``transaction`` keyword.
You can also optionally include a block identifier. For example:

.. doctest:: contractcaller

   >>> from_address = w3.eth.accounts[1]
   >>> twentyone = myContract.caller({'from': from_address}).multiply7(3)
   >>> twentyone
   21
   >>> twentyone = myContract.caller(transaction={'from': from_address}).multiply7(3)
   >>> twentyone
   21
   >>> twentyone = myContract.caller(block_identifier='latest').multiply7(3)
   >>> twentyone
   21

Like :py:class:`ContractFunction`, :py:class:`ContractCaller`
provides methods to interact with contract functions.
Positional and keyword arguments supplied to the contract caller subclass
will be used to find the contract function by signature,
and forwarded to the contract function when applicable.


Examples
--------

Working with an ERC-20 Token Contract
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most fungible tokens on the Ethereum blockchain conform to the `ERC-20`_
standard.  This section of the guide covers interacting with an existing token
contract which conforms to this standard.

.. testsetup::

    from web3 import Web3
    from hexbytes import HexBytes
    w3 = Web3(Web3.EthereumTesterProvider())
    bytecode = '6060604052341561000c57fe5b604051602080610acb833981016040528080519060200190919050505b620f42408114151561003b5760006000fd5b670de0b6b3a76400008102600281905550600254600060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055505b505b610a27806100a46000396000f30060606040523615610097576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806306fdde0314610099578063095ea7b31461013257806318160ddd1461018957806323b872dd146101af578063313ce5671461022557806370a082311461025157806395d89b411461029b578063a9059cbb14610334578063dd62ed3e1461038b575bfe5b34156100a157fe5b6100a96103f4565b60405180806020018281038252838181518152602001915080519060200190808383600083146100f8575b8051825260208311156100f8576020820191506020810190506020830392506100d4565b505050905090810190601f1680156101245780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561013a57fe5b61016f600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803590602001909190505061042e565b604051808215151515815260200191505060405180910390f35b341561019157fe5b610199610521565b6040518082815260200191505060405180910390f35b34156101b757fe5b61020b600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff16906020019091908035906020019091905050610527565b604051808215151515815260200191505060405180910390f35b341561022d57fe5b610235610791565b604051808260ff1660ff16815260200191505060405180910390f35b341561025957fe5b610285600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610796565b6040518082815260200191505060405180910390f35b34156102a357fe5b6102ab6107e0565b60405180806020018281038252838181518152602001915080519060200190808383600083146102fa575b8051825260208311156102fa576020820191506020810190506020830392506102d6565b505050905090810190601f1680156103265780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561033c57fe5b610371600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803590602001909190505061081a565b604051808215151515815260200191505060405180910390f35b341561039357fe5b6103de600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610973565b6040518082815260200191505060405180910390f35b604060405190810160405280600981526020017f54657374546f6b656e000000000000000000000000000000000000000000000081525081565b600081600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925846040518082815260200191505060405180910390a3600190505b92915050565b60025481565b600081600060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205410806105f1575081600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054105b156105fc5760006000fd5b81600060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254019250508190555081600060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254039250508190555081600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825403925050819055508273ffffffffffffffffffffffffffffffffffffffff168473ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a3600190505b9392505050565b601281565b6000600060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490505b919050565b604060405190810160405280600481526020017f544553540000000000000000000000000000000000000000000000000000000081525081565b600081600060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205410156108695760006000fd5b81600060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254039250508190555081600060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825401925050819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a3600190505b92915050565b6000600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490505b929150505600a165627a7a723058205071371ee2a4a1be3c96e77d939cdc26161a256fdd638efc08bd33dfc65d3b850029'
    ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function","stateMutability":"nonpayable"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function","stateMutability":"nonpayable"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function","stateMutability":"view"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function","stateMutability":"nonpayable"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function","stateMutability":"view"},{"inputs":[{"name":"_totalSupply","type":"uint256"}],"payable":false,"type":"constructor","stateMutability":"nonpayable"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"}]'
    factory = w3.eth.contract(abi=ABI, bytecode=bytecode)
    alice, bob = w3.eth.accounts[0], w3.eth.accounts[1]
    assert alice == '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf', alice
    assert bob == '0x2B5AD5c4795c026514f8317c7a215E218DcCD6cF', bob
    tx_hash = factory.constructor(1000000).transact({'from': alice, 'gas': 899000, 'gasPrice': Web3.to_wei(1, 'gwei')})
    assert tx_hash == HexBytes('0x49e3da72a95e4074a9eaea7b438c73ca154627d317e58abeae914e3769a15044'), tx_hash
    txn_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    assert txn_receipt['contractAddress'] == '0xF2E246BB76DF876Cef8b38ae84130F4F55De395b', txn_receipt['contractAddress']
    contract_address = txn_receipt['contractAddress']
    contract = w3.eth.contract(contract_address, abi=ABI)
    total_supply = contract.functions.totalSupply().call()
    decimals = 10 ** 18
    assert total_supply == 1000000 * decimals, total_supply


In this guide we will interact with an existing token contract that we have
already deployed to a local testing chain.  This guide assumes:

1. An existing token contract at a known address.
2. Access to the proper ``ABI`` for the given contract.
3. A ``web3.main.Web3`` instance connected to a provider with an unlocked account which can send transactions.


Creating the contract factory
`````````````````````````````

First we need to create a contract instance with the address of our token
contract and the ``ERC-20`` ABI.

.. doctest::

    >>> contract = w3.eth.contract(contract_address, abi=ABI)
    >>> contract.address
    '0xF2E246BB76DF876Cef8b38ae84130F4F55De395b'


Querying token metadata
```````````````````````

Each token will have a total supply which represents the total number of tokens
in circulation.  In this example we've initialized the token contract to have 1
million tokens.  Since this token contract is setup to have 18 decimal places,
the raw total supply returned by the contract is going to have 18 additional
decimal places.

.. doctest::

    >>> contract.functions.name().call()
    'TestToken'
    >>> contract.functions.symbol().call()
    'TEST'
    >>> decimals = contract.functions.decimals().call()
    >>> decimals
    18
    >>> DECIMALS = 10 ** decimals
    >>> contract.functions.totalSupply().call() // DECIMALS
    1000000


Query account balances
``````````````````````

Next we can query some account balances using the contract's ``balanceOf``
function.  The token contract we are using starts with a single account which
we'll refer to as ``alice`` holding all of the tokens.

.. doctest::

    >>> alice = '0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf'
    >>> bob = '0x2B5AD5c4795c026514f8317c7a215E218DcCD6cF'
    >>> raw_balance = contract.functions.balanceOf(alice).call()
    >>> raw_balance
    1000000000000000000000000
    >>> raw_balance // DECIMALS
    1000000
    >>> contract.functions.balanceOf(bob).call()
    0


Sending tokens
``````````````

Next we can transfer some tokens from ``alice`` to ``bob`` using the contract's
``transfer`` function.


.. doctest::

    >>> tx_hash = contract.functions.transfer(bob, 100).transact({'from': alice})
    >>> tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    >>> contract.functions.balanceOf(alice).call()
    999999999999999999999900
    >>> contract.functions.balanceOf(bob).call()
    100


Creating an approval for external transfers
```````````````````````````````````````````

Alice could also *approve* someone else to spend tokens from her account using
the ``approve`` function.  We can also query how many tokens we're approved to
spend using the ``allowance`` function.

.. doctest::

    >>> contract.functions.allowance(alice, bob).call()
    0
    >>> tx_hash = contract.functions.approve(bob, 200).transact({'from': alice})
    >>> tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    >>> contract.functions.allowance(alice, bob).call()
    200


Performing an external transfer
```````````````````````````````

When someone has an allowance they can transfer those tokens using the
``transferFrom`` function.

.. doctest::

    >>> contract.functions.allowance(alice, bob).call()
    200
    >>> contract.functions.balanceOf(bob).call()
    100
    >>> tx_hash = contract.functions.transferFrom(alice, bob, 75).transact({'from': bob})
    >>> tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    >>> contract.functions.allowance(alice, bob).call()
    125
    >>> contract.functions.balanceOf(bob).call()
    175


.. _ERC-20: https://github.com/ethereum/ERCs/blob/master/ERCS/erc-20.md


Using a struct as a function argument
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

web3.py accepts struct arguments as dictionaries. This format also supports nested structs.
Let's take a look at a quick example. Given the following Solidity contract:

.. code-block:: none

   contract Example {
     address addr;

     struct S1 {
       address a1;
       address a2;
     }

     struct S2 {
       bytes32 b1;
       bytes32 b2;
     }

     struct X {
       S1 s1;
       S2 s2;
       address[] users;
     }

     function update(X memory x) public {
       addr = x.s1.a2;
     }

     function retrieve() public view returns (address) {
       return addr;
     }
   }

You can interact with the web3.py contract API as follows:

.. code-block:: python

   # deploy or lookup the deployed contract, then:

   >>> deployed_contract.functions.retrieve().call()
   '0x0000000000000000000000000000000000000000'

   >>> deployed_contract.functions.update({'s1': ['0x0000000000000000000000000000000000000001', '0x0000000000000000000000000000000000000002'], 's2': [b'0'*32, b'1'*32], 'users': []}).transact()

   >>> deployed_contract.functions.retrieve().call()
   '0x0000000000000000000000000000000000000002'


.. _ambiguous-contract-functions:

Invoke Ambiguous Contract Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Calling overloaded functions can be done as you would expect. Passing arguments will
disambiguate which function you want to call.

For example, if you have a contract with two functions with the name ``identity`` that
accept different types of arguments, you can call them like this:

.. code-block:: python

    >>> ambiguous_contract = w3.eth.contract(address=..., abi=...)
    >>> ambiguous_contract.functions.identity(1, True).call()
    1
    >>> ambiguous_contract.functions.identity("one", 1, True).call()
    1

If there is a need to first retrieve the function, you can use the contract instance's
``get_function_by_signature`` method to get the function you want to call.

Below is an example of a contract that has multiple functions of the same name,
and the arguments are ambiguous. You can use the :meth:`Contract.get_function_by_signature`
method to reference the intended function and call it with the correct arguments.

.. code-block:: python

        >>> contract_source_code = """
        pragma solidity ^0.8.24;
        contract AmbiguousDuo {
          function identity(uint256 input, bool uselessFlag) public pure returns (uint256) {
            return input;
          }
          function identity(int256 input, bool uselessFlag) public pure returns (int256) {
            return input;
          }
        }
        """
        # fast forward all the steps of compiling and deploying the contract.

        >>> identity_func = ambiguous_contract.get_function_by_signature('identity(uint256,bool)')
        >>> identity_func(1, True)
        <Function identity(uint256,bool) bound to (1, True)>
        >>> identity_func(1, True).call()
        1


.. _ccip-read-example:

CCIP Read support for offchain lookup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contract calls support CCIP Read by default, via a ``ccip_read_enabled`` flag on the call and, more globally, a
``global_ccip_read_enabled`` flag on the provider. The following should work by default without raising an
``OffchainLookup`` and instead handling it appropriately as per the specification outlined in
`EIP-3668 <https://eips.ethereum.org/EIPS/eip-3668>`_.

.. code-block:: python

    myContract.functions.revertsWithOffchainLookup(myData).call()

If the offchain lookup requires the user to send a transaction rather than make a call, this may be handled
appropriately in the following way:

.. code-block:: python

    from web3 import Web3, WebSocketProvider
    from web3.utils import handle_offchain_lookup

    w3 = Web3(WebSocketProvider(...))

    myContract = w3.eth.contract(address=...)
    myData = b'data for offchain lookup function call'

    # preflight with an `eth_call` and handle the exception
    try:
        myContract.functions.revertsWithOffchainLookup(myData).call(ccip_read_enabled=False)
    except OffchainLookup as ocl:
        tx = {'to': myContract.address, 'from': my_account}
        data_for_callback_function = handle_offchain_lookup(ocl.payload)
        tx['data'] = data_for_callback_function

        # send the built transaction with `eth_sendTransaction` or sign and send with `eth_sendRawTransaction`
        tx_hash = w3.eth.send_transaction(tx)

Contract Unit Tests in Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is an example of how one can use the `pytest`_ framework in python, web3.py,
eth-tester, and PyEVM to perform unit tests entirely in python without any
additional need for a full featured ethereum node/client. To install needed
dependencies you can use the pinned extra for testing:

.. _pytest: https://docs.pytest.org/en/latest/

.. code-block:: bash

    $ pip install web3[test] pytest

Once you have an environment set up for testing, you can then write your tests
like so:

.. include::  ../tests/core/contracts/test_contract_example.py
    :code: python
    :start-line: 1
