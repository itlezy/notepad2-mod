from contextlib import contextmanager
from pathlib import Path
import sys

# OLE clipboard preservation requires STA; select it before importing pywinauto.
sys.coinit_flags = 2

import pytest

from windows_app import Editor

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
