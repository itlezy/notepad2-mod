import re
from pathlib import Path

import pytest

SETTINGS = "[Settings]\nSaveSettings=1\n[Default Text]\nDefault Style=font:Consolas; size:13; fore:#123456; back:#EEDDCC\n"
SOURCE = (Path(__file__).resolve().parents[1] / "src/Styles.c").read_text(encoding="utf-8")
SCHEMES = re.findall(r'EDITLEXER\s+\w+\s*=\s*\{[^\r\n]*?L"([^"]+)",\s*L"([^"]*)"', SOURCE)


@pytest.mark.parametrize("name,extensions", SCHEMES, ids=[entry[0] for entry in SCHEMES])
def test_scheme_round_trip(editor_factory, name, extensions):
    assert len(SCHEMES) == 38
    with editor_factory(named=True, settings=SETTINGS, scheme=extensions.split(";")[0].strip()) as e:
        original = e.sci(2482, 32)
        e.theme(True)
        assert e.sci(2482, 32) == 0x1E1E1E
        e.theme(False)
        assert e.sci(2482, 32) == original


def test_switching_preserves_document_and_preferences(editor_factory):
    with editor_factory(named=True, settings=SETTINGS) as e:
        e.sci(2645, 0, 1)
        e.sci(2160, 2, 7)
        before = e.read_bytes()
        state = [e.sci(m) for m in (2008, 2009, 2152, 2174, 4002)]
        original, font = e.sci(2482, 32), e.sci(2485, 32)
        for _ in range(20):
            e.theme(True)
            assert e.sci(2482, 32) == 0x1E1E1E
            assert e.sci(2485, 32) == font
            e.theme(False)
            assert e.sci(2482, 32) == original
        assert e.read_bytes() == before
        assert [e.sci(m) for m in (2008, 2009, 2152, 2174, 4002)] == state


@pytest.mark.parametrize("save", [True, False])
def test_selection_persistence(editor_factory, save):
    with editor_factory(named=True, settings=SETTINGS.replace("SaveSettings=1", f"SaveSettings={int(save)}")) as e:
        original = e.sci(2482, 32)
        e.theme(True)
        e.exit()
        e.launch()
        assert e.sci(2482, 32) == (0x1E1E1E if save else original)
        e.theme(False)
        assert e.sci(2482, 32) == original


@pytest.mark.parametrize("extra,expected", [
    ("[Styles]\nEditorTheme=99\n", 0xCCDDEE),
    ("[Styles]\nEditorTheme=1\n[Theme.Dark.Default Text]\nDefault Style=back:invalid\n", 0x1E1E1E),
    ("[Styles]\nEditorTheme=1\n[Theme.Dark.Default Text]\nDefault Style=font:Ignored; size:99; fore:#ABCDEF; back:#222222\n", 0x222222),
])
def test_saved_palette_defaults(editor_factory, extra, expected):
    with editor_factory(named=True, settings=SETTINGS + extra) as e:
        assert e.sci(2482, 32) == expected
        assert e.sci(2485, 32) == 13
        e.theme(False)
        assert e.sci(2482, 32) == 0xCCDDEE


def test_customize_preview_cancel_reset_and_save(editor_factory):
    with editor_factory(named=True, settings=SETTINGS) as e:
        e.theme(True)
        dialog = e.customize()
        dialog.child_window(control_id=102).set_edit_text("font:Consolas; size:15; fore:#EEEEEE; back:#111111")
        dialog.child_window(control_id=106).click()
        assert e.sci(2482, 32) == 0x111111
        dialog.child_window(control_id=107).click()
        dialog.child_window(control_id=106).click()
        assert e.sci(2482, 32) == 0x1E1E1E
        dialog.child_window(control_id=2).click()
        assert e.sci(2482, 32) == 0x1E1E1E and e.sci(2485, 32) == 13
        dialog = e.customize()
        dialog.child_window(control_id=102).set_edit_text("font:Consolas; size:15; fore:#EEEEEE; back:#111111")
        dialog.child_window(control_id=1).click()
        e.theme(False)
        assert e.sci(2485, 32) == 15 and e.sci(2482, 32) == 0xCCDDEE
        e.theme(True)
        e.command(40401)
        assert e.sci(2482, 32) == 0x1E1E1E
        e.command(40401)
        e.exit()
        e.launch()
        assert e.sci(2482, 32) == 0x111111 and e.sci(2485, 32) == 15
