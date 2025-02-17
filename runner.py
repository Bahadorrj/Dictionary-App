import sys
from PyQt6.QtWidgets import QApplication
from src.view import DictionaryApp

MODE = "dark"  # or "light"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open(f"resources/{MODE}_mode.qss", "r") as file:
        style = file.read()
        app.setStyleSheet(style)
    window = DictionaryApp()
    window.show()
    sys.exit(app.exec())
