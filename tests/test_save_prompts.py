"""Exercise save prompting through the native UI, including embedded NUL data."""

import pytest
from pywinauto.timings import wait_until


CASES = [
    pytest.param(b"\0AB", False, True, id="leading-nul"),
    pytest.param(b" \t\r\n", False, True, id="whitespace"),
    pytest.param(b"\0A" + bytes(1020), False, True, id="1022-byte-nul"),
    pytest.param(b"\0A" + bytes(1021), False, False, id="1023-byte-nul"),
    pytest.param(b"", False, False, id="empty"),
    pytest.param(b"\0AB", True, False, id="named-nul"),
]


@pytest.mark.parametrize("payload,named,legacy_drops", CASES)
@pytest.mark.parametrize("operation", ["new", "open", "close"])
def test_nonempty_document_prompts_before_discard(
    editor_factory, legacy_save_behavior, payload, named, legacy_drops, operation
):
    with editor_factory(named=named) as editor:
        editor.add_bytes(payload)
        before = editor.read_bytes()
        if operation == "close":
            editor.post_close()
        else:
            editor.post_command(40000 if operation == "new" else 40001)

        result = {}

        def operation_reached_ui():
            if not editor.is_running():
                result["state"] = "closed"
                return True
            dialog = editor.dialog()
            if dialog is not None and dialog.is_visible():
                buttons = {
                    child.control_id()
                    for child in dialog.descendants(class_name="Button")
                }
                if {6, 7}.issubset(buttons):
                    result.update(state="save", dialog=dialog)
                    return True
                if {1, 2}.issubset(buttons):
                    result["state"] = "open-dialog"
                    return True
            if operation == "new" and editor.sci(2006) == 0:
                result["state"] = "cleared"
                return True
            return False

        wait_until(10, 0.05, operation_reached_ui)
        should_prompt = bool(before) and not (
            legacy_save_behavior and legacy_drops
        )
        assert (result["state"] == "save") is should_prompt, (
            f"{operation}: observed {result['state']}; "
            f"save prompt expected={should_prompt}"
        )
        if should_prompt:
            result["dialog"].child_window(control_id=2).wrapper_object().click()
            wait_until(5, 0.05, lambda: editor.dialog() is None)
            assert editor.read_bytes() == before, "Cancel changed document bytes"
        elif legacy_save_behavior and legacy_drops:
            expected_state = {
                "new": "cleared", "open": "open-dialog", "close": "closed"
            }[operation]
            assert result["state"] == expected_state
