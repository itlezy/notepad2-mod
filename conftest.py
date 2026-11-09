"""Register CLI options before pytest resolves test paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def pytest_addoption(parser):
    parser.addoption("--executable", default=str(ROOT / "bin/VS2022/Release_x64/Notepad2.exe"))
    parser.addoption("--architecture", choices=("x86", "x64"), default="x64")
    parser.addoption("--configuration", choices=("Release", "Debug"), default="Release")
    parser.addoption("--legacy-save-behavior", action="store_true")
