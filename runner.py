import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.view import DictionaryApp
from src.backend import resource_path, get_stylesheet

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon = QIcon(resource_path("resources/icons/app.jpeg"))
    app.setWindowIcon(icon)
    app.setStyleSheet(get_stylesheet("dark"))
    window = DictionaryApp()
    window.show()
    sys.exit(app.exec())
