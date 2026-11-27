"""pywinauto owns window/control automation; this adapter handles Scintilla messages."""
import ctypes
import subprocess

from pywinauto import Application
from pywinauto.remote_memory_block import RemoteMemoryBlock
from pywinauto.timings import wait_until
from win32con import IDOK, WM_COMMAND


def press_dialog_button(dialog, control_id):
    button = dialog.child_window(control_id=control_id, class_name="Button").wait("ready", timeout=10)
    # A button click notifies its parent with WM_COMMAND and BN_CLICKED (zero).
    button.parent().post_message(WM_COMMAND, control_id, button.handle)


class Editor:
    def __init__(self, executable, ini, document=None, scheme="cpp"):
        self.executable, self.ini, self.document, self.scheme = executable, ini, document, scheme
        self.launch()

    def launch(self):
        args = [str(self.executable), "/n", "/f", str(self.ini), "/s", self.scheme]
        if self.document:
            args.append(str(self.document))
        startup = subprocess.STARTUPINFO()
        startup.dwFlags = subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        self.process = subprocess.Popen(args, startupinfo=startup)
        try:
            self.app = Application(backend="win32").connect(process=self.process.pid, timeout=60)
            self.main = self.app.window(class_name_re="Notepad2.*", visible_only=False)
            self.main.wait("exists", timeout=60)
            control = self.main.child_window(class_name="Scintilla")
            control.wait("exists", timeout=60)
            self.editor = control.wrapper_object()
        except BaseException:
            self.close()
            raise

    def sci(self, message, w=0, l=0):
        return self.editor.send_message_timeout(message, w, l, timeout=10)

    def add_bytes(self, data):
        if data:
            buffer = ctypes.create_string_buffer(data)
            remote = RemoteMemoryBlock(self.editor, size=len(buffer))
            try:
                remote.Write(buffer)
                self.sci(2001, len(data), remote.Address())
            finally:
                remote.CleanUp()

    def read_bytes(self):
        size = self.sci(2006)
        buffer = ctypes.create_string_buffer(size + 1)
        remote = RemoteMemoryBlock(self.editor, size=size + 1)
        try:
            self.sci(2182, size + 1, remote.Address())
            remote.Read(buffer)
            return buffer.raw[:size]
        finally:
            remote.CleanUp()

    def command(self, command):
        self.main.send_message_timeout(0x111, command, 0, timeout=10)

    def post_command(self, command):
        self.main.post_message(0x111, command, 0)

    def post_close(self):
        self.main.post_message(0x10)

    def dialog(self):
        if not self.is_running():
            return None
        windows = self.app.windows(class_name="#32770", visible_only=False)
        return self.app.window(handle=windows[0].handle) if windows else None

    def submit_save_dialog(self, path, command=40005):
        self.post_command(command)
        dialog = self.app.window(title="Save As", class_name="#32770")
        dialog.wait("ready", timeout=10)
        # The address bar also has an Edit control. Target the file-name field.
        filename = dialog.child_window(control_id=1001, class_name="Edit").wait("ready", timeout=10)
        filename.set_edit_text(str(path))
        assert filename.window_text() == str(path)
        press_dialog_button(dialog, IDOK)

    def is_running(self):
        return self.process.poll() is None

    def theme(self, dark):
        self.command(40981 if dark else 40980)

    def customize(self):
        self.post_command(40402)
        wait_until(10, 0.05, lambda: self.dialog() is not None and self.dialog().is_visible())
        dialog = self.dialog()
        tree = dialog.child_window(control_id=100).wrapper_object()
        wait_until(10, 0.05, lambda: tree.item_count() > 38)
        tree.get_item([0, 0]).select()
        return dialog

    def exit(self):
        self.sci(2014)  # Tests decide what to save; never leave an unsaved prompt.
        self.post_close()
        self.process.wait(timeout=10)
        assert self.process.returncode == 0

    def close(self):
        if self.is_running():
            self.process.terminate()
            self.process.wait(timeout=10)
