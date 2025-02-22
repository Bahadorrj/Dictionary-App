import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.view import DictionaryApp
from src.backend import resource_path

MODE = "dark"  # or "light"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open(resource_path(f"resources/{MODE}_mode.qss"), "r") as file:
        style = file.read()
        app.setStyleSheet(style)
    icon = QIcon(resource_path("resources/app.jpeg"))
    app.setWindowIcon(icon)
    window = DictionaryApp()
    window.show()
    sys.exit(app.exec())
