from contextlib import contextmanager
from pathlib import Path

import pytest

from windows_app import Editor

ROOT = Path(__file__).resolve().parents[1]


def pytest_addoption(parser):
    parser.addoption("--executable", default=str(ROOT / "bin/VS2022/Release_x64/Notepad2.exe"))
    parser.addoption("--architecture", choices=("x86", "x64"), default="x64")
    parser.addoption("--configuration", choices=("Release", "Debug"), default="Release")
    parser.addoption("--legacy-save-behavior", action="store_true")


@pytest.fixture
def legacy_save_behavior(request):
    return request.config.getoption("--legacy-save-behavior")


@pytest.fixture
def editor_factory(request, tmp_path):
    serial = 0

    @contextmanager
    def factory(named=False, settings=None, scheme="cpp", content=None):
        nonlocal serial
        serial += 1
        folder = tmp_path / str(serial)
        folder.mkdir()
        ini = folder / "settings.ini"
        ini.write_text(settings or "[Settings]\nSaveSettings=1\n", encoding="utf-16")
        document = folder / "sample.cpp"
        document.write_bytes(content if content is not None else b"// comment\r\nint main() { return 42; }\r\n")
        editor = Editor(Path(request.config.getoption("--executable")).resolve(), ini, document if named else None, scheme)
        try:
            yield editor
        finally:
            editor.close()

    return factory
