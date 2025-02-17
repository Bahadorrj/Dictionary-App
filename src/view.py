import os
import json
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLineEdit,
    QLabel,
    QMessageBox,
    QGraphicsOpacityEffect,
    QHeaderView,
)
from PyQt6.QtCore import (
    QPropertyAnimation,
    QRunnable,
    QThreadPool,
    pyqtSignal,
    QObject,
)
from src.backend import get_word_packet, resource_path


# Worker signals to communicate between the worker thread and the UI thread.
class WorkerSignals(QObject):
    finished = pyqtSignal(str, list)  # Emits the word and its packet.
    error = pyqtSignal(str)


# Worker for fetching the word packet without blocking the UI.
class WordPacketWorker(QRunnable):
    def __init__(self, word: str):
        super().__init__()
        self.word = word
        self.signals = WorkerSignals()

    def run(self):
        try:
            packet = get_word_packet(self.word)
        except Exception as e:
            self.signals.error.emit(str(e))
            return
        self.signals.finished.emit(self.word, packet)


class DictionaryApp(QMainWindow):
    def __init__(self, json_path=resource_path("data/words.json")):
        super().__init__()
        self.json_path = json_path
        self.setWindowTitle("Dictionary Application")
        self.setGeometry(100, 100, 800, 600)
        self.words_data = {}  # Holds words and their corresponding packets.
        self.threadpool = QThreadPool()
        self.load_data()
        self.init_ui()

    def init_ui(self):
        # Main container widget and layout.
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # LEFT PANEL: Search bar and list of words.
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # Search mechanism for filtering added words.
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search words...")
        self.search_edit.textChanged.connect(self.filter_word_list)
        left_layout.addWidget(self.search_edit)

        self.word_list = QListWidget()
        self.word_list.addItems(self.words_data.keys())
        self.word_list.currentItemChanged.connect(self.display_word_packet)
        left_layout.addWidget(self.word_list)

        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(250)
        main_layout.addWidget(left_widget)

        # RIGHT PANEL: Word details and controls.
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # Label to show the selected word.
        self.word_label = QLabel("Word Details:")
        right_layout.addWidget(self.word_label)

        # Table to display details: part of speech, definition, and example.
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(3)
        self.details_table.setHorizontalHeaderLabels(
            ["Part of Speech", "Definition", "Example"]
        )
        self.details_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        self.details_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.details_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        right_layout.addWidget(self.details_table, 1)

        # Controls for adding and removing words.
        controls_layout = QHBoxLayout()
        self.add_word_edit = QLineEdit()
        self.add_word_edit.setPlaceholderText("Enter a word")
        controls_layout.addWidget(self.add_word_edit)

        self.add_word_button = QPushButton("Add Word")
        self.add_word_button.clicked.connect(self.add_word)
        controls_layout.addWidget(self.add_word_button)

        self.remove_word_button = QPushButton("Remove Word")
        self.remove_word_button.clicked.connect(self.remove_word)
        controls_layout.addWidget(self.remove_word_button)

        right_layout.addLayout(controls_layout)
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, 2)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def load_data(self):
        """Load words data from the JSON file located in the root directory."""
        if os.path.isdir(resource_path("data")) is False:
            os.mkdir(resource_path("data"))
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r") as file:
                    self.words_data = json.load(file)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error loading data: {e}")
                self.words_data = {}
        else:
            self.words_data = {}

    def save_data(self):
        """Save the current words data to the JSON file in the root directory."""
        try:
            with open(self.json_path, "w") as file:
                json.dump(self.words_data, file, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving data: {e}")

    def filter_word_list(self, text):
        """Filter the words in the list based on the search text."""
        for index in range(self.word_list.count()):
            item = self.word_list.item(index)
            item.setHidden(text.lower() not in item.text().lower())

    def display_word_packet(self, current, previous):
        """
        Display the details of the selected word's packet in the table.
        A simple fade-in animation is applied for a smooth transition.
        """
        if current:
            word = current.text()
            packet = self.words_data.get(word, [])
            self.word_label.setText(f"Details for: {word}")
            self.populate_table(packet)
        else:
            self.word_label.setText("Word Details:")
            self.details_table.setRowCount(0)

    def populate_table(self, packet):
        """Populate the table widget with the word packet details."""
        self.details_table.setRowCount(len(packet))
        for row, entry in enumerate(packet):
            pos_item = QTableWidgetItem(entry.get("part_of_speech", ""))
            definition_item = QTableWidgetItem(entry.get("definition", ""))
            example_text = entry.get("example", "")
            if example_text is None:
                example_text = ""
            example_item = QTableWidgetItem(example_text)

            self.details_table.setItem(row, 0, pos_item)
            self.details_table.setItem(row, 1, definition_item)
            self.details_table.setItem(row, 2, example_item)

        # Fade-in animation for smooth transition of word details.
        opacity_effect = QGraphicsOpacityEffect(self.details_table)
        self.details_table.setGraphicsEffect(opacity_effect)
        self.animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def add_word(self):
        """
        Retrieve a new word's packet using get_word_packet in a separate thread,
        then add it to the dictionary data and update both the UI and JSON file.
        """
        word = self.add_word_edit.text().strip()
        if not word:
            QMessageBox.information(self, "Input Error", "Please enter a valid word.")
            return
        if word in self.words_data:
            QMessageBox.information(
                self, "Duplicate", f"'{word}' is already in the dictionary."
            )
            return

        # Disable the add button while fetching to prevent multiple clicks.
        self.add_word_button.setEnabled(False)
        worker = WordPacketWorker(word)
        worker.signals.finished.connect(self.on_word_packet_fetched)
        worker.signals.error.connect(self.on_word_packet_error)
        self.threadpool.start(worker)

    def on_word_packet_fetched(self, word, packet):
        """Handle the fetched word packet."""
        self.add_word_button.setEnabled(True)
        if not packet:  # Do not add if packet is empty.
            QMessageBox.warning(self, "Not Found", f"No definition found for '{word}'.")
            return
        self.words_data[word] = packet
        self.word_list.addItem(word)
        self.save_data()
        self.add_word_edit.clear()

    def on_word_packet_error(self, error_message):
        """Handle any error during the word packet retrieval."""
        self.add_word_button.setEnabled(True)
        QMessageBox.warning(
            self, "Error", f"Error retrieving word packet: {error_message}"
        )

    def remove_word(self):
        """
        Remove the selected word from the dictionary data, update the JSON file,
        and clear the details view.
        """
        current_item = self.word_list.currentItem()
        if not current_item:
            QMessageBox.information(
                self, "Selection Error", "Please select a word to remove."
            )
            return
        word = current_item.text()
        confirmation = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove '{word}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            row = self.word_list.row(current_item)
            self.word_list.takeItem(row)
            if word in self.words_data:
                del self.words_data[word]
                self.save_data()
            self.details_table.setRowCount(0)
            self.word_label.setText("Word Details:")
