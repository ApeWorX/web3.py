.. _contributing:

Contributing
------------

Thanks for your interest in contributing to web3.py! Read on to learn what
would be helpful and how to go about it. If you get stuck along the way, reach
for help in the `Python Discord server`_.


How to Help
~~~~~~~~~~~

Without code:

* Answer user questions within GitHub issues, Stack Overflow, or the `Python Discord server`_.
* Write or record tutorial content.
* Improve our documentation (including typo fixes).
* `Open an issue <https://github.com/ethereum/web3.py/issues/new>`_ on GitHub to document a bug. Include as much detail as possible, e.g., how to reproduce the issue and any exception messages.

With code:

* Fix a bug that has been reported in an issue.
* Add a feature that has been documented in an issue.
* Add a missing test case.

.. warning::

  **Before you start:** always ask if a change would be desirable or let us know that
  you plan to work on something! We don't want to waste your time on changes we can't
  accept or duplicated effort.


Your Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

  Use of a virtual environment is strongly advised for minimizing dependency issues. See
  `this article <https://realpython.com/effective-python-environment/#virtual-environments>`_
  for usage patterns.

All pull requests are made from a fork of the repository; use the GitHub UI to create a fork.
web3.py depends on `submodules <https://gist.github.com/gitaarik/8735255>`_, so when you clone
your fork to your local machine, include the ``--recursive`` flag:

.. code:: sh

    $ git clone --recursive https://github.com/<your-github-username>/web3.py.git
    $ cd web3.py


Finally, install all development dependencies:

.. code:: sh

    $ python -m pip install -e ".[dev]"
    $ pre-commit install


Using Docker
^^^^^^^^^^^^

Developing within Docker is not required, but if you prefer that workflow, use
the *sandbox* container provided in the **docker-compose.yml** file.

To start up the test environment, run:

.. code:: sh

    $ docker compose up -d


This will build a Docker container set up with an environment to run the
Python test code.

To run the core tests from your local machine:

.. code:: sh

    $ docker compose exec sandbox bash -c 'pytest tests/core'


The container does not have ``go-ethereum`` installed, so you can exclude those tests
by using the ``-k "not goethereum"`` flag.

.. code:: sh

    $ docker compose exec sandbox bash -c 'pytest tests/integration -k "not goethereum"'


You can run arbitrary commands inside the Docker container by using the
``bash -c`` prefix.

.. code:: sh

    $ docker compose exec sandbox bash -c 'pwd && ls'


Or, if you would like to open a session to the container, run:

.. code:: sh

    $ docker compose exec sandbox bash


Running The Tests
~~~~~~~~~~~~~~~~~

A great way to explore the code base is to run the tests.


First, install the test dependencies:

.. code:: sh

    $ python -m pip install -e ".[test]"


You can run all tests with:

.. code:: sh

    $ pytest


However, running the entire test suite takes a very long time and is generally impractical.
Typically, you'll just want to run a subset instead, like:

.. code:: sh

    $ pytest tests/core/eth-module/test_accounts.py


Linting is also performed by the CI and locally with each commit. You can save yourself
some time by checking for linting errors manually:

.. code:: sh

   $ make lint


It is important to understand that each pull request must pass the full test
suite as part of the CI check. This test suite will run in the CI anytime a
pull request is opened or updated.


Writing Tests
~~~~~~~~~~~~~

We strongly encourage contributors to write good tests for their code as
part of the code review process. This helps ensure that your code is doing
what it should be doing.

We strongly encourage you to use our existing tests for both guidance and
homogeneity / consistency across our tests. We use ``pytest`` for our tests.
For more specific pytest guidance, please refer to the `pytest documentation`_.

Within the ``pytest`` scope, :file:`conftest.py` files are used for common code
shared between modules that exist within the same directory as that particular
:file:`conftest.py` file.


Unit Testing and eth-tester Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Our unit tests are grouped together with tests against the ``eth-tester`` library,
using the ``py-evm`` library as a backend, via the ``EthereumTesterProvider``.

These tests live under appropriately named child directories within the
``/tests`` directory. The core of these tests live under ``/tests/core``.
Do your best to follow the existing structure when adding a test and make sure
that its location makes sense.

Integration Testing
^^^^^^^^^^^^^^^^^^^

Our integration test suite setup lives under the ``/tests/integration`` directory.
The integration test suite is dependent on what we call "fixtures" (not to be
confused with pytest fixtures). These zip file fixtures, which also live in the
``/tests/integration`` directory, are configured to run the specific client we are
testing against along with a genesis configuration that gives our tests some
pre-determined useful objects (like unlocked, pre-loaded accounts) to be able to
interact with the client when we run our tests.

The parent ``/integration`` directory houses some common configuration shared across
all client tests, whereas the ``/go_ethereum`` directory houses common code to be
shared across geth-specific provider tests. Though the setup and run configurations
exist across the different files within ``/tests/integration``, our integration module
tests are written across different files within ``/web3/_utils/module_testing``.

* :file:`common.py` files within the client directories contain code that is shared across
  all provider tests (http, ipc, and ws). This is mostly used to override tests that span
  across all providers.
* :file:`conftest.py` files within each of these directories contain mostly code that
  can be *used* by all test files that exist within the same directory or subdirectories
  of the :file:`conftest.py` file. This is mostly used to house pytest fixtures to be
  shared among our tests. Refer to the `pytest documentation on fixtures`_ for more
  information.
* ``test_{client}_{provider}.py`` files (e.g. :file:`test_goethereum_http.py`) are where
  client-and-provider-specific test configurations exist. This is mostly used to
  override tests specific to the provider type for the respective client.

The integration tests are each run in insolation to prevent muddied contexts. Because
they are run in isolation, they can be parallelized with ``pytest-xdist`` in order to
speed up the test suite. To run the tests in parallel, you can use the ``-n`` flag
with ``pytest``. For example, to run the tests in parallel with 4 workers, you can
use the following command:

.. code:: sh

    $ pytest tests/integration/go_ethereum/path/to/module/or/test -n 4


Working With Test Contracts
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Contracts used for testing exist under ``web3/_utils/contract_sources``. These contracts
get compiled via the ``compile_contracts.py`` script in the same directory. To use
this script, simply pass the Solidity version to be used to compile the contracts as an
argument at the command line.

Arguments for the script are:
    -v or --version         Solidity version to be used to compile the contracts. If
                            blank, the script uses the latest available version from
                            solcx.

    -f or --filename        If left blank, all .sol files will be compiled and the
                            respective contract data will be generated. Pass in a
                            specific ``.sol`` filename here to compile just one file.


To run the script, you will need the ``py-solc-x`` library for compiling the files
as well as ``black`` for code formatting. You can install those with:

.. code:: sh

    $ python -m pip install py-solc-x black

The following example compiles all the contracts and generates their respective
contract data that is used across our test files for the test suites. This data gets
generated within the ``contract_data`` subdirectory within the ``contract_sources``
folder.

.. code-block:: bash

    $ cd ../web3.py/web3/_utils/contract_sources
    $ python compile_contracts.py -v 0.8.17
    Compiling OffchainLookup
    ...
    ...
    reformatted ...

To compile and generate contract data for only one ``.sol`` file, specify using the
filename with the ``-f`` (or ``--filename``) argument flag.

.. code-block:: bash

    $ cd ../web3.py/web3/_utils/contract_sources
    $ python compile_contracts.py -v 0.8.17 -f OffchainLookup.sol
    Compiling OffchainLookup.sol
    reformatted ...

If there is any contract data that is not generated via the script but is important
to pass on to the integration tests, the ``_custom_contract_data.py`` file within the
``contract_data`` subdirectory can be used to store that information when appropriate.

Be sure to re-generate the integration test fixture after running the script to update
the contract bytecodes for the integration test suite - see the
:ref:`generating_fixtures` section below.


Manual Testing
~~~~~~~~~~~~~~

To import and test an unreleased version of web3.py in another context,
you can install it from your development directory:

.. code:: sh

   $ python -m pip install -e ../path/to/web3py


Code Style
~~~~~~~~~~

We use `pre-commit <https://pre-commit.com/>`_ to enforce a consistent code style across
the library. This tool runs automatically with every commit, but you can also run it
manually with:

.. code:: sh

   $ make lint


If you need to make a commit that skips the ``pre-commit`` checks, you can do so with
``git commit --no-verify``.

We use Black as part of our linting. To ignore the commits that introduced Black in
git history, you can configure your git environment like so:

.. code:: sh

   $ git config blame.ignoreRevsFile .git-blame-ignore-revs


This library uses `type hints`_, which are enforced by the ``mypy`` tool (part of the
``pre-commit`` checks). All new code is required to land with type hints, with the
exception of code within the ``tests`` directory.


Documentation
~~~~~~~~~~~~~

Good documentation will lead to quicker adoption and happier users. Please
check out our guide on `how to create documentation`_ for the Python Ethereum
ecosystem.

Pull requests generate their own preview of the latest documentation at
``https://web3py--<pr-number>.org.readthedocs.build/en/<pr-number>/``.


Pull Requests
~~~~~~~~~~~~~

It's a good idea to make pull requests early on. A pull request represents the
start of a discussion, and doesn't necessarily need to be the final, finished
submission.

See GitHub's documentation for `working on pull requests`_.

Once you've made a pull request take a look at the Circle CI build status in
the GitHub interface and make sure all tests are passing. In general, pull
requests that do not pass the CI build yet won't get reviewed unless explicitly
requested.

If the pull request introduces changes that should be reflected in the release
notes, please add a **newsfragment** file as explained
`here <https://github.com/ethereum/web3.py/blob/main/newsfragments/README.md>`_.

If possible, the change to the release notes file should be included in the
commit that introduces the feature or bugfix.

.. _generating_fixtures:

Generating New Fixtures
~~~~~~~~~~~~~~~~~~~~~~~

Our integration tests make use of Geth private networks.
When new versions of the client software are introduced, new fixtures should be
generated.

Before generating new fixtures, make sure you have the test dependencies installed:

.. code:: sh

    $ python -m pip install -e ".[test]"

.. note::

    A "fixture" is a pre-synced network. It's the result of configuring and running
    a client, deploying the test contracts, and saving the resulting state for
    testing web3.py functionality against.


Geth Fixtures
^^^^^^^^^^^^^

1. Install the desired Geth version on your machine locally. We recommend `py-geth`_ for
   this purpose, because it enables you to easily manage multiple versions of Geth.

   Note that ``py-geth`` will need updating to support each new Geth version as well.
   Adding newer Geth versions to py-geth is straightforward; see past commits for a template.

   If py-geth has the Geth version you need, install that version locally. For example:

   .. code:: sh

      $ python -m geth.install v1.16.2

2. Specify the Geth binary and run the fixture creation script (from within the web3.py directory):

   .. code:: sh

      $ GETH_BINARY=~/.py-geth/geth-v1.16.2/bin/geth python ./tests/integration/generate_fixtures/go_ethereum.py

3. The output of this script is your fixture, a zip file, which is now stored in ``/tests/integration/``.
   The ``/tests/integration/go_ethereum/conftest.py`` and
   ``/web3/tools/benchmark/node.py`` files should be updated automatically to point to this new fixture.
   Delete the old fixture.

4. Run the tests. To ensure that the tests run with the correct Geth version locally,
   you may again include the ``GETH_BINARY`` environment variable.

5. The ``geth_version`` and ``pygeth_version`` parameter defaults in
   ``/.circleci/config.yml`` should be automatically updated to match the
   ``go-ethereum`` version used to generate the test fixture and the ``py-geth``
   version that supports installing it.


CI Testing With a Nightly Geth Build
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Occasionally you'll want to have CI run the test suite against an unreleased version of
Geth - e.g. to test upcoming hard fork changes. The workflow described below is for
testing only, as updates will only be merged into main once the Geth release is
published and the test runs are updated to use the new stable version.

1. Configure ``tests/integration/generate_fixtures/go_ethereum/common.py`` as needed.

2. Geth automagically compiles new builds for every commit that gets merged into the codebase.
   Download the desired build from the `develop builds <https://geth.ethereum.org/downloads/>`_.

3. Build your test fixture, passing in the binary you just downloaded via ``GETH_BINARY``. Don't forget
   to update the ``/tests/integration/go_ethereum/conftest.py`` file to point to your new fixture.

4. Our CI runs on Ubuntu, so download the corresponding 64-bit Linux
   `develop build <https://geth.ethereum.org/downloads/>`_, then
   add it to the root of your web3.py directory. Rename the binary ``custom_geth``.

5. In ``.circleci/config.yml``, update the ``geth_version`` pipeline parameter to
   "custom". This will trigger the custom Geth build to be used in the CI test suite.

6. Create a PR and let CI do its thing.


Releasing
~~~~~~~~~

Releases are typically done from the ``main`` branch, except when releasing a beta (in
which case the beta is released from ``main``, and the previous stable branch is
released from said branch).

Final test before each release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before releasing a new version, build and test the package that will be released:

.. code:: sh

    $ git checkout main && git pull
    $ make package-test

This will build the package and install it in a temporary virtual environment. Follow
the instructions to activate the venv and test whatever you think is important.

Review the documentation that will get published:

.. code:: sh

    $ make docs

Validate and preview the release notes:

.. code:: sh

    $ make validate-newsfragments

Build the release notes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before bumping the version number, build the release notes. You must include the part of
the version to bump (see below), which changes how the version number will show in the
release notes.

.. code:: sh

    $ make notes bump=$$VERSION_PART_TO_BUMP$$

If there are any errors, be sure to re-run make notes until it works.

Push the release to github & pypi
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After confirming that the release package looks okay, release a new version:

.. code:: sh

    $ make release bump=$$VERSION_PART_TO_BUMP$$

This command will:

- Bump the version number as specified in ``.pyproject.toml`` and ``setup.py``.
- Create a git commit and tag for the new version.
- Build the package.
- Push the commit and tag to github.
- Push the new package files to pypi.

Which version part to bump
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``$$VERSION_PART_TO_BUMP$$`` must be one of: ``major``, ``minor``, ``patch``, ``stage``,
or ``devnum``.

The version format for this repo is ``{major}.{minor}.{patch}`` for stable, and
``{major}.{minor}.{patch}-{stage}.{devnum}`` for unstable (``stage`` can be alpha or
beta).

If you are in a beta version, ``make release bump=stage`` will switch to a stable.

To issue an unstable version when the current version is stable, specify the new version
explicitly, like ``make release bump="--new-version 4.0.0-alpha.1"``.

You can see what the result of bumping any particular version part would be with
``bump-my-version show-bump``.

.. _Python Discord server: https://discord.gg/GHryRvPB84
.. _style guide: https://github.com/ethereum/snake-charmers-tactical-manual/blob/main/style-guide.md
.. _type hints: https://www.python.org/dev/peps/pep-0484/
.. _how to create documentation: https://github.com/ethereum/snake-charmers-tactical-manual/blob/main/documentation.md
.. _working on pull requests: https://help.github.com/articles/about-pull-requests/
.. _py-geth: https://github.com/ethereum/py-geth
.. _pytest documentation: https://docs.pytest.org/en/latest
.. _pytest documentation on fixtures: https://docs.pytest.org/en/latest/how-to/fixtures.html
