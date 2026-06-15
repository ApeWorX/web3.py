import re


def get_pygeth_version() -> str:
    with open("pyproject.toml") as f:
        pyproject_contents = f.read()

    version_match = re.search(
        r'"py-geth\s*([><=~!]+)\s*([\d.]+)"',
        pyproject_contents,
    )
    if version_match:
        return "".join(version_match.group(1, 2))
    else:
        raise ValueError("py-geth not found in pyproject.toml")


if __name__ == "__main__":
    version = get_pygeth_version()
    print(version)
