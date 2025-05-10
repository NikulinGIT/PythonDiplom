import sys
import subprocess
import win32gui
import win32con
import win32process
import win32api
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer


class CMDContainer(QWidget):
    def __init__(self, pid):
        super().__init__()
        self.pid = pid
        self.cmd_hwnd = None
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.find_cmd_window)
        self.timer.start(500)

    def find_cmd_window(self):
        def enum_windows_callback(hwnd, _):
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
            if window_pid == self.pid:
                self.cmd_hwnd = hwnd
                return False
            return True

        win32gui.EnumWindows(enum_windows_callback, None)

        if self.cmd_hwnd:
            self.timer.stop()
            self.embed_cmd()

    def embed_cmd(self):
        win32gui.SetParent(self.cmd_hwnd, self.winId())

        # Убираем рамки
        style = win32gui.GetWindowLong(self.cmd_hwnd, win32con.GWL_STYLE)
        style = style & ~win32con.WS_CAPTION & ~win32con.WS_THICKFRAME
        win32gui.SetWindowLong(self.cmd_hwnd, win32con.GWL_STYLE, style)

        self.resize_cmd()

    def resize_cmd(self):
        if self.cmd_hwnd:
            rect = self.rect()
            win32gui.MoveWindow(self.cmd_hwnd, 0, 0, rect.width(), rect.height(), True)

    def resizeEvent(self, event):
        self.resize_cmd()
        super().resizeEvent(event)


class EmbeddedCMD(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Встроенный cmd.exe с масштабированием")
        self.setGeometry(100, 100, 300, 300)

        layout = QVBoxLayout(self)


        # Запуск cmd.exe
        process = subprocess.Popen("cmd.exe", creationflags=subprocess.CREATE_NEW_CONSOLE)
        self.cmd_widget = CMDContainer(process.pid)
        layout.addWidget(self.cmd_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmbeddedCMD()
    window.show()
    sys.exit(app.exec_())
