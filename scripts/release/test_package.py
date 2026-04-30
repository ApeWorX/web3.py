from pathlib import (
    Path,
)
import subprocess
import sys
from tempfile import (
    TemporaryDirectory,
)
import venv


def get_pip_exe(venv_path: Path) -> Path:
    """Get the path to pip executable for the given virtual environment."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"


def create_venv(parent_path: Path) -> Path:
    venv_path = parent_path / "package-smoke-test"
    venv.create(venv_path, with_pip=True)
    pip_exe = get_pip_exe(venv_path)
    subprocess.run([pip_exe, "install", "-U", "pip", "setuptools"], check=True)
    return venv_path


def find_wheel(project_path: Path) -> Path:
    wheels = list(project_path.glob("dist/*.whl"))

    if len(wheels) != 1:
        raise ValueError(
            f"Expected one wheel. Instead found: {wheels} "
            f"in project {project_path.absolute()}"
        )

    return wheels[0]


def install_wheel(venv_path: Path, wheel_path: Path) -> None:
    pip_exe = get_pip_exe(venv_path)
    subprocess.run([pip_exe, "install", f"{wheel_path}"], check=True)


def test_install_local_wheel() -> None:
    with TemporaryDirectory() as tmpdir:
        venv_path = create_venv(Path(tmpdir))
        wheel_path = find_wheel(Path("."))
        install_wheel(venv_path, wheel_path)
        print("Installed", wheel_path.absolute(), "to", venv_path)
        if sys.platform == "win32":
            print(f"Activate with `{venv_path}\\Scripts\\activate`")
        else:
            print(f"Activate with `source {venv_path}/bin/activate`")
        input("Press enter when the test has completed. The directory will be deleted.")


if __name__ == "__main__":
    test_install_local_wheel()
