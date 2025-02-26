import json
import datetime
import random
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QStackedWidget,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

from src.backend import resource_path


class Card:
    """Represents a flashcard with spaced repetition data."""

    def __init__(self, word, definitions):
        self.word = word
        self.definitions = definitions
        self.ease_factor = 2.5  # Initial ease factor (SM-2 algorithm)
        self.interval = 0  # Days between reviews
        self.repetitions = 0  # Number of successful reviews
        self.next_review = datetime.datetime.now().date()
        self.last_review = None

    def process_response(self, quality):
        """
        Update card based on response quality (0-5):
        0-2: Incorrect (start over)
        3: Correct but difficult
        4: Correct
        5: Correct and easy
        """
        self.last_review = datetime.datetime.now().date()

        if quality < 3:
            # Failed, reset
            self.repetitions = 0
            self.interval = 0
        else:
            # Correct response
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 3
            else:
                self.interval = round(self.interval * self.ease_factor)

            # Increase repetition counter
            self.repetitions += 1

            # Update ease factor (SM-2 algorithm)
            self.ease_factor += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
            if self.ease_factor < 1.3:
                self.ease_factor = 1.3

        # Set next review date
        self.next_review = datetime.datetime.now().date() + datetime.timedelta(
            days=self.interval
        )

        return self.interval

    def is_due(self):
        """Check if card is due for review."""
        return self.next_review <= datetime.datetime.now().date()

    def get_formatted_definitions(self):
        """Format all definitions for display."""
        result = ""
        for i, definition_dict in enumerate(self.definitions, 1):
            result += f"<p><b>{i}. ({definition_dict['part_of_speech']})</b> {definition_dict['definition']}</p>"
            if definition_dict["example"] and definition_dict["example"] != "null":
                result += f"<p><i>Example:</i> {definition_dict['example']}</p>"
        return result


class FlashcardManager:
    """Manages the flashcard collection and spaced repetition system."""

    def __init__(self):
        self.cards = {}
        self.current_card = None
        self.due_cards = []
        self.data_file = resource_path("data/flashcards.json")
        self.stats = {"learned": 0, "reviewing": 0, "new": 0}

    def load_cards(self, initial_data_file=resource_path("data/words.json")):
        """Load cards from JSON file or create from initial data."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    for word, card_data in data.items():
                        self.cards[word] = Card(word, card_data["definitions"])
                        self.cards[word].ease_factor = card_data["ease_factor"]
                        self.cards[word].interval = card_data["interval"]
                        self.cards[word].repetitions = card_data["repetitions"]
                        self.cards[word].next_review = datetime.datetime.strptime(
                            card_data["next_review"], "%Y-%m-%d"
                        ).date()
                        if card_data.get("last_review"):
                            self.cards[word].last_review = datetime.datetime.strptime(
                                card_data["last_review"], "%Y-%m-%d"
                            ).date()
            elif os.path.exists(initial_data_file):
                with open(initial_data_file, "r") as f:
                    words_data = json.load(f)
                    for word, definitions in words_data.items():
                        self.cards[word] = Card(word, definitions)

            self.update_due_cards()
            self.update_stats()
        except Exception as e:
            print(f"Error loading cards: {e}")
            return False
        return True

    def save_cards(self):
        """Save cards to JSON file."""
        try:
            data = {}
            for word, card in self.cards.items():
                data[word] = {
                    "definitions": card.definitions,
                    "ease_factor": card.ease_factor,
                    "interval": card.interval,
                    "repetitions": card.repetitions,
                    "next_review": card.next_review.strftime("%Y-%m-%d"),
                    "last_review": (
                        card.last_review.strftime("%Y-%m-%d")
                        if card.last_review
                        else None
                    ),
                }

            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving cards: {e}")
            return False

    def update_due_cards(self):
        """Update the list of cards due for review."""
        self.due_cards = [card for card in self.cards.values() if card.is_due()]
        random.shuffle(self.due_cards)

    def get_next_card(self):
        """Get the next card due for review."""
        if not self.due_cards:
            self.update_due_cards()
            if not self.due_cards:
                return None

        if self.due_cards:
            self.current_card = self.due_cards.pop(0)
            return self.current_card
        return None

    def process_response(self, quality):
        """Process response for current card."""
        if self.current_card:
            interval = self.current_card.process_response(quality)
            self.save_cards()
            self.update_stats()
            return interval
        return 0

    def update_stats(self):
        """Update statistics about card status."""
        today = datetime.datetime.now().date()
        self.stats = {"learned": 0, "reviewing": 0, "new": 0}

        for card in self.cards.values():
            if card.repetitions == 0:
                self.stats["new"] += 1
            elif card.interval >= 21:  # Considered "learned" if interval is 21+ days
                self.stats["learned"] += 1
            else:
                self.stats["reviewing"] += 1

        return self.stats


class FlashcardApp(QMainWindow):
    """Main application window."""

    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.manager = FlashcardManager()
        self.card_flipped = False
        self.setup_ui()

        # Load cards
        if not self.manager.load_cards():
            QMessageBox.warning(
                self, "Warning", "Failed to load cards. Starting with empty deck."
            )

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Flashcard App")
        self.setMinimumSize(800, 600)

        # Apply dark theme
        self.apply_dark_theme()

        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Stats area
        stats_layout = QHBoxLayout()
        self.new_label = QLabel("New: 0")
        self.reviewing_label = QLabel("Reviewing: 0")
        self.learned_label = QLabel("Learned: 0")

        for label in [self.new_label, self.reviewing_label, self.learned_label]:
            label.setFont(QFont("Arial", 12))
            label.setStyleSheet("color: #AAAAAA;")
            stats_layout.addWidget(label)

        main_layout.addLayout(stats_layout)

        # Card display area
        self.card_container = QFrame()
        self.card_container.setFrameShape(QFrame.Shape.StyledPanel)
        self.card_container.setStyleSheet(
            """
            QFrame {
                background-color: #2D3748;
                border-radius: 15px;
                border: 1px solid #4A5568;
            }
        """
        )
        card_layout = QVBoxLayout(self.card_container)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)

        # Stacked widget for card front/back
        self.card_stack = QStackedWidget()

        # Front of card
        front_widget = QWidget()
        front_layout = QVBoxLayout(front_widget)
        front_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label = QLabel("Click 'Start Review' to begin")
        self.word_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.word_label.setWordWrap(True)
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label.setStyleSheet("color: #F7FAFC;")
        front_layout.addWidget(self.word_label)
        self.card_stack.addWidget(front_widget)

        # Back of card
        back_widget = QWidget()
        back_layout = QVBoxLayout(back_widget)
        back_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.word_title = QLabel()
        self.word_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.word_title.setStyleSheet("color: #F7FAFC; margin-bottom: 10px;")
        back_layout.addWidget(self.word_title)

        self.definitions_label = QLabel()
        self.definitions_label.setFont(QFont("Arial", 14))
        self.definitions_label.setWordWrap(True)
        self.definitions_label.setStyleSheet("color: #F7FAFC;")
        self.definitions_label.setTextFormat(Qt.TextFormat.RichText)
        back_layout.addWidget(self.definitions_label)

        self.card_stack.addWidget(back_widget)
        card_layout.addWidget(self.card_stack)

        main_layout.addWidget(self.card_container, 1)

        # Bottom buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        # Review start button
        self.start_button = QPushButton("Start Review")
        self.start_button.setObjectName("btn")
        self.start_button.setFont(QFont("Arial", 12))
        self.start_button.clicked.connect(self.start_review)

        # Flip button
        self.flip_button = QPushButton("Flip Card")
        self.flip_button.setObjectName("btn")
        self.flip_button.setFont(QFont("Arial", 12))
        self.flip_button.clicked.connect(self.flip_card)
        self.flip_button.setEnabled(False)

        # Response buttons layout
        self.response_layout = QHBoxLayout()
        response_buttons = [
            ("Again", 1, "#E53E3E"),
            ("Hard", 2, "#DD6B20"),
            ("Good", 4, "#38A169"),
            ("Easy", 5, "#3182CE"),
        ]

        self.response_buttons = []
        for text, quality, color in response_buttons:
            btn = QPushButton(text)
            btn.setFont(QFont("Arial", 12))
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {color}CC;
                }}
                QPushButton:pressed {{
                    background-color: {color}AA;
                }}
            """
            )
            btn.clicked.connect(lambda checked, q=quality: self.process_response(q))
            self.response_buttons.append(btn)
            self.response_layout.addWidget(btn)
            btn.hide()

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.flip_button)
        button_layout.addLayout(self.response_layout)

        main_layout.addLayout(button_layout)

        self.setCentralWidget(main_widget)
        self.update_stats_display()

    def apply_dark_theme(self):
        """Apply dark theme to the application."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 50, 50))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        QApplication.setPalette(palette)

        # Global stylesheet for buttons
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #4A5568;
                color: white;
                border-radius: 5px;
                padding: 10px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2D3748;
            }
            QPushButton:disabled {
                background-color: #718096;
                color: #CBD5E0;
            }
        """
        )

    def start_review(self):
        """Start or continue the review session."""
        card = self.manager.get_next_card()
        if card:
            self.show_card_front(card)
            self.start_button.hide()
            self.flip_button.show()
            self.flip_button.setEnabled(True)
        else:
            QMessageBox.information(
                self, "Review Complete", "You've finished reviewing all due cards!"
            )
            self.word_label.setText("All cards reviewed!")

    def show_card_front(self, card):
        """Display the front of a card."""
        self.card_flipped = False
        self.word_label.setText(card.word)
        self.word_title.setText(card.word)
        self.definitions_label.setText(card.get_formatted_definitions())
        self.card_stack.setCurrentIndex(0)

        # Hide response buttons
        for btn in self.response_buttons:
            btn.hide()

        self.flip_button.setEnabled(True)

    def flip_card(self):
        """Flip the card to show the other side."""
        if not self.card_flipped:
            # Show back of card
            self.card_stack.setCurrentIndex(1)
            self.card_flipped = True
            self.flip_button.setEnabled(False)

            # Show response buttons
            for btn in self.response_buttons:
                btn.show()
        else:
            # Show front of card
            self.card_stack.setCurrentIndex(0)
            self.card_flipped = False

            # Hide response buttons
            for btn in self.response_buttons:
                btn.hide()

    def process_response(self, quality):
        """Process the user's response to the current card."""
        interval = self.manager.process_response(quality)

        # Show brief feedback message
        feedback = ""
        if quality < 3:
            feedback = "Card will be shown again soon"
        else:
            feedback = f"Next review in {interval} day{'s' if interval != 1 else ''}"

        self.word_label.setText(feedback)
        self.update_stats_display()

        # Hide response buttons
        for btn in self.response_buttons:
            btn.hide()

        # Schedule next card after a brief delay
        QTimer.singleShot(1500, self.start_review)

    def update_stats_display(self):
        """Update the statistics display."""
        stats = self.manager.update_stats()
        self.new_label.setText(f"New: {stats['new']}")
        self.reviewing_label.setText(f"Reviewing: {stats['reviewing']}")
        self.learned_label.setText(f"Learned: {stats['learned']}")

    def closeEvent(self, event):
        """Handle window close event."""
        self.manager.save_cards()
        self.closed.emit()
        event.accept()
