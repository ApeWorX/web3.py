
# web3.py on Windows

## Developer Setup

### Option 1: Native Windows setup

1. **Install Python 3.9+**  
   Download from [python.org](https://www.python.org/downloads/windows/).  
   Make sure to check **"Add Python to PATH"** during installation.

2. **Clone the repository and create a virtual environment**:

```powershell
cd %USERPROFILE%
````
```powershell
git clone https://github.com/ethereum/web3.py.git
````
```powershell
cd web3.py
````
```powershell
python -m venv venv
````
```powershell
venv\Scripts\activate
````

3. **Upgrade pip and install development dependencies**:

```powershell
pip install --upgrade pip
```
```powershell
pip install -e ".[dev]"
```

4. **(Optional) Install `leveldb` binaries if needed**:

```powershell
pip install plyvel-binary
```

> ⚠️ Note: `leveldb` is not required for most users.
> If installation fails, you can safely skip this step.

---

### Option 2: Recommended (via WSL)

Many Ethereum developers prefer using
[WSL (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/install)
to avoid dependency issues.

With WSL you can run a Linux distribution (Ubuntu/Debian/Fedora, etc.) directly on Windows.
After installing WSL, follow the Linux setup guide: [README-linux.md](./README-linux.md).

---
