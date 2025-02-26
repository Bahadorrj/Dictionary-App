import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.view import DictionaryApp
from src.backend import resource_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon = QIcon(resource_path("resources/app.jpeg"))
    app.setWindowIcon(icon)
    window = DictionaryApp()
    window.show()
    sys.exit(app.exec())
