# PyQt6 Dictionary Application

This is a PyQt6-based dictionary application that allows users to add words, retrieve word packets, and view their meanings and parts of speech from [FreeDictionaryAPI](https://dictionaryapi.dev/). The app supports both dark and light themes for an enhanced user experience.

---

## Features

- **Add Words:** Users can add new words to the dictionary.
- **Remove Words:** Words can be removed from the dictionary list.
- **Retrieve Word Packets:** The app uses a `get_word_packet` from `src.backend.py` function to fetch word packets via an HTTP request that connects to [FreeDictionaryAPI](https://dictionaryapi.dev/). Each packet contains the word's part of speech and definition.
- **Search Words:** Search functionality is provided for quick access to any added word.
- **Duplicate Prevention:** The app prevents duplicate words from being added.
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
   pip install pyqt6 requests
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

4. **Search Words:**
   - Type into the search bar to filter the list of words dynamically.

5. **Theme Selection:**  
   You can load the desired theme (dark or light) by modifying the theme loading code in `main.py`.

---

## Theme Files

The app includes the following theme files in `resources`:

- `dark_mode.qss` — Provides a modern, dark UI theme.
- `light_mode.qss` — Offers a bright, clean UI theme.

To apply a theme, modify the `MODE` attribute theme-loading in `main.py`.

---

## Limitations

- The app does not allow users to edit existing words or re-fetch their packets.
- Backup and versioning for the `words.json` file are not supported.

---

## Future Enhancements

Potential future improvements may include:
- Adding a theme-switching button to dynamically change themes at runtime.
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

For any questions or issues, please open an issue on GitHub or contact [me](bahador.rj@gmail.com) directly.

---