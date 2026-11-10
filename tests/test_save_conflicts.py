"""Save destination conflicts exercised through native Win32 dialogs."""
import re

import pytest
from pywinauto.timings import wait_until


def choose_destination(editor, path, command=40005):
    editor.post_command(command)
    wait_until(10, 0.05, lambda: editor.dialog() is not None)
    dialog = editor.dialog()
    dialog.child_window(class_name="Edit").wrapper_object().set_edit_text(str(path))
    dialog.child_window(control_id=1).wrapper_object().click()
    conflict = editor.app.window(title="File already exists", class_name="#32770")
    conflict.wait("visible", timeout=10)
    return conflict


@pytest.mark.parametrize("action", [1, 2, 2901, 2902, 2903])
def test_conflict_choices(editor_factory, tmp_path, action):
    target = tmp_path / "report.txt"
    target.write_bytes(b"existing")
    with editor_factory() as editor:
        editor.add_bytes(b"new")
        before = editor.read_bytes()
        conflict = choose_destination(editor, target)
        conflict.child_window(control_id=action).wrapper_object().click()
        wait_until(10, 0.05, lambda: editor.dialog() is None)
        if action == 2:
            assert target.read_bytes() == b"existing"
            assert editor.read_bytes() == before
            assert editor.sci(2159)  # SCI_GETMODIFY
        elif action == 2903:
            outputs = list(tmp_path.glob("report_*.txt"))
            assert len(outputs) == 1
            assert re.fullmatch(r"report_[a-z]{3}\.txt", outputs[0].name)
            assert outputs[0].read_bytes() == before
            assert target.read_bytes() == b"existing"
        else:
            expected = {1: before, 2901: b"existing\r\n" + before,
                        2902: before + b"\r\nexisting"}[action]
            assert target.read_bytes() == expected
            assert editor.read_bytes() == expected
            assert not editor.sci(2159)


@pytest.mark.parametrize("existing,new,expected", [
    (b"old\n", b"new", b"old\nnew"),
    (b"old\nline", b"new", b"old\nline\nnew"),
    (b"old", b"\nnew", b"old\nnew"),
    (b"", b"new", b"new"),
    (b"old", b"", b"old"),
    (b"\xef\xbb\xbfold\x00tail", b"new\x00tail", b"\xef\xbb\xbfold\x00tail\r\nnew\x00tail"),
])
def test_append_boundaries(editor_factory, tmp_path, existing, new, expected):
    target = tmp_path / "target.txt"
    target.write_bytes(existing)
    with editor_factory() as editor:
        editor.add_bytes(new)
        choose_destination(editor, target).child_window(control_id=2901).wrapper_object().click()
        wait_until(10, 0.05, lambda: editor.dialog() is None)
        assert target.read_bytes() == expected
        assert editor.read_bytes() == expected.removeprefix(b"\xef\xbb\xbf")


@pytest.mark.parametrize("codec", ["utf-8-sig", "utf-16", "utf-16-be"])
def test_destination_encoding(editor_factory, tmp_path, codec):
    target = tmp_path / "encoded.txt"
    payload = "old\nline".encode(codec)
    if codec == "utf-16-be":
        payload = b"\xfe\xff" + payload
    target.write_bytes(payload)
    with editor_factory() as editor:
        editor.sci(2037, 65001)
        editor.add_bytes("new \u00e9".encode("utf-8"))
        choose_destination(editor, target).child_window(control_id=2901).wrapper_object().click()
        wait_until(10, 0.05, lambda: editor.dialog() is None)
        expected = "old\nline\nnew \u00e9".encode(codec)
        if codec == "utf-16-be":
            expected = b"\xfe\xff" + expected
        assert target.read_bytes() == expected


def test_save_copy_keeps_document(editor_factory, tmp_path):
    target = tmp_path / "copy.txt"
    target.write_bytes(b"old")
    with editor_factory(named=True) as editor:
        editor.add_bytes(b"new")
        before = editor.read_bytes()
        choose_destination(editor, target, 40006).child_window(control_id=2901).wrapper_object().click()
        wait_until(10, 0.05, lambda: editor.dialog() is None)
        assert target.read_bytes() == b"old\r\n" + before
        assert editor.read_bytes() == before
        assert editor.sci(2159)


def test_normal_save_has_no_conflict(editor_factory):
    with editor_factory(named=True) as editor:
        editor.add_bytes(b"new")
        editor.command(40004)
        assert editor.dialog() is None
        assert editor.document.read_bytes() == editor.read_bytes()


def test_same_path_save_as(editor_factory):
    with editor_factory(named=True, content=b"old") as editor:
        editor.add_bytes(b"new")
        before = editor.read_bytes()
        choose_destination(editor, editor.document).child_window(control_id=2902).wrapper_object().click()
        wait_until(10, 0.05, lambda: editor.dialog() is None)
        assert editor.document.read_bytes() == before + b"\r\nold"
        assert editor.read_bytes() == editor.document.read_bytes()
        assert not editor.sci(2159)


def test_readonly_failure_preserves_document(editor_factory, tmp_path):
    import os
    import stat
    target = tmp_path / "readonly.txt"
    target.write_bytes(b"old")
    try:
        with editor_factory() as editor:
            editor.add_bytes(b"new")
            before = editor.read_bytes()
            conflict = choose_destination(editor, target)
            target.chmod(stat.S_IREAD)
            conflict.child_window(control_id=2901).wrapper_object().click()
            wait_until(10, 0.05, lambda: not conflict.exists())
            wait_until(10, 0.05, lambda: editor.dialog() is not None)
            dialog = editor.dialog()
            dialog.child_window(control_id=2).wrapper_object().click()
            assert target.read_bytes() == b"old"
            assert editor.read_bytes() == before
            assert editor.sci(2159)
    finally:
        os.chmod(target, stat.S_IWRITE)


def test_lossy_conversion_cancel(editor_factory, tmp_path):
    target = tmp_path / "ansi.txt"
    target.write_bytes(b"old\xe9")
    with editor_factory(settings="[Settings]\nSaveSettings=0\n[Settings2]\nLoadASCIIasUTF8=0\n") as editor:
        editor.sci(2037, 65001)
        editor.add_bytes("new \U0001f600".encode("utf-8"))
        before = editor.read_bytes()
        choose_destination(editor, target).child_window(control_id=2901).wrapper_object().click()
        wait_until(10, 0.05, lambda: editor.dialog() is not None)
        editor.dialog().child_window(control_id=2).wrapper_object().click()
        wait_until(10, 0.05, lambda: editor.dialog() is None)
        assert target.read_bytes() == b"old\xe9"
        assert editor.read_bytes() == before
        assert editor.sci(2159)
