# PyQt6 Dictionary Application

This is a PyQt6-based dictionary application that allows users to add words, retrieve word packets, and view their meanings and parts of speech from [FreeDictionaryAPI](https://dictionaryapi.dev/). The app supports both dark and light themes for an enhanced user experience.

---

## Features

- **Add Words:** Users can add new words to the dictionary.
- **Remove Words:** Words can be removed from the dictionary list.
- **Retrieve Word Packets:** The app uses a `get_word_packet` from `src.backend.py` function to fetch word packets via an HTTP request that connects to [FreeDictionaryAPI](https://dictionaryapi.dev/). Each packet contains the word's part of speech and definition.
- **Search Words:** Search functionality is provided for quick access to any added word.
- **Duplicate Prevention:** The app prevents duplicate words from being added.
- **Listen to pronunciation** The app playbacks words pronunciations.
- **Oxford web based search** The app searches for the word's definition in [Oxford Learner's Dictionary](https://www.oxfordlearnersdictionaries.com/).
- **ANKI word reviewing** The app has a review mechanism for the words you have added to the dictionary.
- **Error Handling:** If a word has no valid packet (empty list returned), the app shows a message box and does not add the word.
- **Persistent Storage:** Words are stored in a `data/words.json` file located in the root directory.
- **Dark and Light Modes:** The application provides QSS files for dark and light modes to enhance the UI.

---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Bahadorrj/Dictionary-App.git
   cd dictionary-app
   ```

2. **Install Dependencies:**  
   Ensure you have Python installed and install the required libraries:
   ```bash
   pip install pyqt6 requests googlesearch-python
   ```

3. **Run the Application:**  
   Execute the main script to launch the application:
   ```bash
   python runner.py
   ```

---

## Usage Instructions

1. **Add a Word:**
   - Type a word into the input field and click the "Add Word" button.
   - If the word's packet is valid, it will be added to the list.
   - If the packet is empty, a message box will inform the user, and the word will not be added.

2. **Remove a Word:**
   - Select a word from the list and click the "Remove Word" button.

3. **View Word Details:**
   - Selecting a word from the list will display its definitions and parts of speech in the table below.
   - Listen to word's pronunciation by clicking the audio icon in the top right of the window.
   - View the word's definition in [Oxford Learner's Dictionary](https://www.oxfordlearnersdictionaries.com/) by clicking the Oxford icon in the top right of the window.

4. **Reviewing:**
   - Start reviewing relevant words by selecting the `Review` button above the search bar.

5. **Search Words:**
   - Type into the search bar to filter the list of words dynamically.

6. **Theme Selection:**  
   - You can switch between dark and light theme by toggling the theme button above the search bar.

---

## Theme Files

The app includes the following theme files in `resources`:

- `dark_mode.qss` — Provides a modern, dark UI theme.
- `light_mode.qss` — Offers a bright, clean UI theme.

---

## Limitations

- The app does not allow users to edit existing words or re-fetch their packets.
- Backup and versioning are not supported.

---

## Future Enhancements

Potential future improvements may include:
- Unify theme resources amongst dictionary and anki app.
- Support for editing word definitions and parts of speech.
- Backup and version control for the `words.json` file.

---

## License

This project is open-source and licensed under the [MIT License](LICENSE).

---

## Contributions

Contributions are welcome! Feel free to fork the repository and submit pull requests for new features, bug fixes, or UI improvements.

---

## Contact

For any questions or issues, please open an issue on GitHub or contact [me](https://bahador.rj@gmail.com) directly.

---