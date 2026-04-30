# web3.py on Windows

## Developer Setup

There are two practical ways to contribute to `web3.py` on Windows:

- Use `conda` in a native Windows shell for a straightforward local setup.
- Use WSL for an environment that more closely matches the Linux-based contributor
  and CI workflows.

If you are unsure which path to pick, prefer WSL.

## Option 1: Native Windows with `conda`

1. Install the following tools:

   - `git`
   - Miniconda or Anaconda

1. Open **Anaconda Prompt** or **PowerShell** and create a dedicated environment:

```powershell
conda create -n web3py-dev python=3.12
conda activate web3py-dev
python -m pip install --upgrade pip
```

3. Clone your fork and enter the project directory:

```powershell
git clone --recursive https://github.com/<your-github-username>/web3.py.git
cd web3.py
```

4. Install the development dependencies:

```powershell
python -m pip install -e ".[dev]"
pre-commit install
```

5. Run a focused test target to verify the environment:

```powershell
pytest tests/core/providers/test_http_provider.py
```

### Notes for native Windows

- Native Windows is a reasonable choice for documentation updates, typing work,
  many unit tests, and general Python-only changes.
- Some integration-heavy workflows may be easier in WSL because the project's
  broader tooling and examples are primarily Linux-oriented.

## Option 2: WSL

WSL is the closest Windows experience to the standard Linux contributor setup.

1. Install WSL and a Linux distribution such as Ubuntu.

1. Open the WSL shell and install system dependencies:

```sh
sudo apt-get update
sudo apt-get install -y build-essential git libssl-dev libffi-dev autoconf automake libtool python3-dev python3-venv
```

3. Clone your fork and enter the project directory:

```sh
git clone --recursive https://github.com/<your-github-username>/web3.py.git
cd web3.py
```

4. Create and activate a virtual environment:

```sh
python3 -m venv venv
. venv/bin/activate
python -m pip install --upgrade pip
```

5. Install development dependencies and hooks:

```sh
python -m pip install -e ".[dev]"
pre-commit install
```

6. Run a focused test target to verify the environment:

```sh
pytest tests/core/providers/test_http_provider.py
```

## Troubleshooting

- If `pip install -e ".[dev]"` fails because of missing build tools, confirm
  that the compiler and Python development headers are installed for the
  environment you are using.
- If you only need to make documentation changes, you can usually validate your
  setup with a small `pytest` target instead of running the full suite.
- If you expect to work on integration tests or Linux-specific tooling, WSL is
  usually the better default choice.
