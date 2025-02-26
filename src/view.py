import os
import json
import webbrowser
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
    QSize,
    Qt,
    QEasingCurve,
    pyqtProperty,
    QCoreApplication,
)
from PyQt6.QtGui import (
    QIcon,
    QCursor,
    QShortcut,
    QKeySequence,
    QPainter,
    QColor,
    QPen,
    QBrush,
    QPainterPath,
)
from src.backend import (
    get_word_packet,
    resource_path,
    play_word,
    search_oxford_dictionary,
)
from src.anki import FlashcardApp


# Worker signals to communicate between the worker thread and the UI thread.
class WorkerSignals(QObject):
    finished = pyqtSignal(str, object)
    error = pyqtSignal(str)


class Worker(QRunnable):
    def __init__(self, word: str, func):
        super().__init__()
        self.word = word
        self.func = func
        self.signals = WorkerSignals()

    def run(self):
        try:
            output = self.func(self.word)
        except Exception as e:
            self.signals.error.emit(str(e))
            return
        self.signals.finished.emit(self.word, output)


class ThemeToggleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set initial state
        self.dark_mode = True
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Size configurations
        self.setFixedSize(56, 24)

        # Colors for both themes
        self.light_bg = QColor(230, 230, 230)
        self.light_fg = QColor(250, 250, 250)
        self.light_icon_color = QColor(240, 170, 50)  # Sun/light golden

        self.dark_bg = QColor(50, 50, 70)
        self.dark_fg = QColor(70, 70, 100)
        self.dark_icon_color = QColor(200, 210, 255)  # Moon/star bluish

        # Animation properties
        self._toggle_position = 1.0  # 0.0 = light mode, 1.0 = dark mode

        # Set up the animation
        self.animation = QPropertyAnimation(self, b"togglePosition")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Connect signals
        self.clicked.connect(self.toggle_theme)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode

        # Run animation
        target_pos = 1.0 if self.dark_mode else 0.0
        self.animation.setStartValue(self._toggle_position)
        self.animation.setEndValue(target_pos)
        self.animation.start()

    # Define property for the animation
    def get_toggle_position(self):
        return self._toggle_position

    def set_toggle_position(self, pos):
        self._toggle_position = pos
        self.update()  # Trigger a repaint

    togglePosition = pyqtProperty(float, get_toggle_position, set_toggle_position)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Calculate interpolated colors based on animation position
        bg_color = QColor(
            int(
                self.light_bg.red() * (1 - self._toggle_position)
                + self.dark_bg.red() * self._toggle_position
            ),
            int(
                self.light_bg.green() * (1 - self._toggle_position)
                + self.dark_bg.green() * self._toggle_position
            ),
            int(
                self.light_bg.blue() * (1 - self._toggle_position)
                + self.dark_bg.blue() * self._toggle_position
            ),
        )

        fg_color = QColor(
            int(
                self.light_fg.red() * (1 - self._toggle_position)
                + self.dark_fg.red() * self._toggle_position
            ),
            int(
                self.light_fg.green() * (1 - self._toggle_position)
                + self.dark_fg.green() * self._toggle_position
            ),
            int(
                self.light_fg.blue() * (1 - self._toggle_position)
                + self.dark_fg.blue() * self._toggle_position
            ),
        )

        icon_color = QColor(
            int(
                self.light_icon_color.red() * (1 - self._toggle_position)
                + self.dark_icon_color.red() * self._toggle_position
            ),
            int(
                self.light_icon_color.green() * (1 - self._toggle_position)
                + self.dark_icon_color.green() * self._toggle_position
            ),
            int(
                self.light_icon_color.blue() * (1 - self._toggle_position)
                + self.dark_icon_color.blue() * self._toggle_position
            ),
        )

        # Draw the background track
        track_path = QPainterPath()
        track_path.addRoundedRect(0, 0, width, height, height / 2, height / 2)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawPath(track_path)

        # Calculate the thumb/knob position
        thumb_size = height - 8
        thumb_x = 4 + (width - thumb_size - 8) * self._toggle_position

        # Draw the thumb/knob
        painter.setBrush(QBrush(fg_color))
        painter.drawEllipse(int(thumb_x), 4, thumb_size, thumb_size)

        # Draw icon inside the thumb
        icon_size = thumb_size - 12
        icon_x = thumb_x + 6
        icon_y = 10

        painter.setPen(QPen(icon_color, 2))

        # Draw either sun or moon icon based on the animation position
        if self._toggle_position < 0.5:
            # Sun icon
            sun_radius = icon_size / 2
            sun_center_x = icon_x + sun_radius
            sun_center_y = icon_y + sun_radius

            # Draw sun circle
            painter.setBrush(QBrush(icon_color))
            painter.drawEllipse(
                int(icon_x), int(icon_y), int(icon_size), int(icon_size)
            )

            # Draw sun rays
            painter.setPen(QPen(icon_color, 1.5))
            ray_length = 3

            # Adjust ray visibility based on animation
            ray_opacity = 1.0 - (self._toggle_position * 2)
            ray_color = QColor(icon_color)
            ray_color.setAlphaF(ray_opacity)
            painter.setPen(QPen(ray_color, 1.5))

            if ray_opacity > 0:
                for i in range(8):
                    start_x = sun_center_x + (sun_radius - 1) * 0.8 * 1.414 * 0.5 * (
                        1 if i % 2 == 0 else 0.707
                    ) * (1 if i < 4 else -1) * (1 if i % 4 < 2 else -1)
                    start_y = sun_center_y + (sun_radius - 1) * 0.8 * 1.414 * 0.5 * (
                        1 if i % 2 == 1 else 0.707
                    ) * (1 if i < 2 or i > 5 else -1) * (1 if i % 4 < 2 else 1)
                    end_x = start_x + ray_length * 1.414 * 0.5 * (
                        1 if i % 2 == 0 else 0.707
                    ) * (1 if i < 4 else -1) * (1 if i % 4 < 2 else -1)
                    end_y = start_y + ray_length * 1.414 * 0.5 * (
                        1 if i % 2 == 1 else 0.707
                    ) * (1 if i < 2 or i > 5 else -1) * (1 if i % 4 < 2 else 1)

                    painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))
        else:
            # Moon icon
            painter.setBrush(QBrush(icon_color))

            # Draw crescent moon shape
            moon_path = QPainterPath()

            # Outer circle (full moon)
            moon_path.addEllipse(
                int(icon_x), int(icon_y), int(icon_size), int(icon_size)
            )

            # Inner circle (shadow part) - slightly offset
            shadow_size = icon_size * 0.8
            shadow_offset = icon_size * 0.3
            moon_path.addEllipse(
                int(icon_x + shadow_offset),
                int(icon_y),
                int(shadow_size),
                int(shadow_size),
            )

            # Create the crescent shape by using fillRule Odd-Even
            moon_path.setFillRule(Qt.FillRule.WindingFill)

            # Apply the path to the painter
            painter.drawPath(moon_path)

            # Add a star when in full dark mode
            star_opacity = (self._toggle_position - 0.5) * 2
            if star_opacity > 0:
                star_color = QColor(icon_color)
                star_color.setAlphaF(star_opacity)
                painter.setPen(QPen(star_color, 1))
                painter.setBrush(QBrush(star_color))

                # Small star near moon
                star_size = 2 + 1 * star_opacity
                star_x = icon_x - 5
                star_y = icon_y + 5
                painter.drawEllipse(
                    int(star_x), int(star_y), int(star_size), int(star_size)
                )


class DictionaryApp(QMainWindow):
    def __init__(self, json_path=resource_path("data/words.json")):
        super().__init__()
        self.json_path = json_path
        self.setWindowTitle("Dictionary Application")
        self.setMinimumSize(800, 600)
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

        h_layout = QHBoxLayout()
        h_layout.setSpacing(10)
        h_layout.setContentsMargins(0, 0, 0, 0)

        # Button to toggle between light and dark mode.
        self.toggle_button = ThemeToggleButton()
        self.toggle_button.clicked.connect(self.toggle_dark_mode)
        h_layout.addWidget(self.toggle_button)

        # ANKI App runner
        self.anki_button = QPushButton("Review")
        self.anki_button.clicked.connect(self.run_anki)
        h_layout.addWidget(self.anki_button)

        left_layout.addLayout(h_layout)

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
        self.oxford_dictionary_button = QPushButton()
        self.oxford_dictionary_button.setIcon(
            QIcon(resource_path("resources/oxford.png"))
        )
        self.oxford_dictionary_button.setIconSize(QSize(32, 32))
        self.oxford_dictionary_button.setStyleSheet("background-color: transparent;")
        self.oxford_dictionary_button.setFixedSize(32, 32)
        self.oxford_dictionary_button.setCursor(
            QCursor(Qt.CursorShape.PointingHandCursor)
        )  # Set pointer cursor
        self.oxford_dictionary_button.clicked.connect(self.show_oxford_definitions)
        self.play_sound_button = QPushButton()
        self.play_sound_button.setIcon(QIcon(resource_path("resources/sound.png")))
        self.play_sound_button.setIconSize(QSize(32, 32))
        self.play_sound_button.setStyleSheet("background-color: transparent;")
        self.play_sound_button.setFixedSize(32, 32)
        self.play_sound_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.play_sound_button.clicked.connect(self.play_word)
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.word_label)
        top_layout.addWidget(self.oxford_dictionary_button)
        top_layout.addWidget(self.play_sound_button)
        right_layout.addLayout(top_layout)

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

        add_shortcut = QShortcut(QKeySequence("Return"), self)
        add_shortcut.activated.connect(self.add_shortcut_triggered)

        remove_shortcut = QShortcut(QKeySequence("Del"), self)
        remove_shortcut.activated.connect(self.remove_shortcut_triggered)

        with open(resource_path("resources/dark_mode.qss"), "r") as file:
            style = file.read()
            self.setStyleSheet(style)

    def toggle_dark_mode(self):
        if self.toggle_button.dark_mode:
            qss_file = resource_path("resources/dark_mode.qss")
        else:
            qss_file = resource_path("resources/light_mode.qss")
        with open(qss_file, "r") as f:
            self.setStyleSheet(f.read())

    def run_anki(self):
        self.anki_app = FlashcardApp()
        self.anki_app.closed.connect(self.show)
        self.anki_app.show()
        self.hide()

    def add_shortcut_triggered(self):
        word = self.add_word_edit.text().strip()
        if word:
            self.add_word()

    def remove_shortcut_triggered(self):
        current_item = self.word_list.currentItem()
        if current_item:
            self.remove_word()

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
        worker = Worker(word, get_word_packet)
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

    def show_oxford_definitions(self):
        self.oxford_dictionary_button.setEnabled(False)
        word = self.word_list.currentItem().text()
        worker = Worker(word, search_oxford_dictionary)
        worker.signals.finished.connect(self.on_oxford_search_finished)
        worker.signals.error.connect(self.on_oxford_search_failed)
        self.threadpool.start(worker)

    def on_oxford_search_finished(self, word, link):
        self.oxford_dictionary_button.setEnabled(True)
        if link:
            webbrowser.open(link)
        else:
            QMessageBox.warning(
                self, "No Definition", f"No definition found for '{word}'."
            )

    def on_oxford_search_failed(self, error_message):
        self.oxford_dictionary_button.setEnabled(True)
        self.add_word_button.setEnabled(True)
        QMessageBox.warning(
            self, "Error", f"Error retrieving word's oxford definition: {error_message}"
        )

    def play_word(self):
        self.play_sound_button.setEnabled(False)
        current_item = self.word_list.currentItem()
        if not current_item:
            return
        word = current_item.text()
        worker = Worker(word, play_word)
        worker.signals.finished.connect(lambda: self.play_sound_button.setEnabled(True))
        worker.signals.error.connect(lambda: self.play_sound_button.setEnabled(True))
        self.threadpool.start(worker)
