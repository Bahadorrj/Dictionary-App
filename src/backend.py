import sys
import os
import requests
from gtts import gTTS
from playsound import playsound
from googlesearch import search


def get_response(word, version="v2"):
    """
    Fetch definition of a word from the Free Dictionary API.

    Args:
        word (str): The word to look up
        version (str): API version (default: 'v2')

    Returns:
        dict: JSON response from the API

    Raises:
        requests.exceptions.RequestException: If the request fails
        ValueError: If the word is not found
    """
    base_url = "https://api.dictionaryapi.dev/api"
    url = f"{base_url}/{version}/entries/en/{word}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise ValueError(f"Word '{word}' not found in dictionary")
        raise requests.exceptions.RequestException(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error making request: {e}")


def get_word_packet(word):
    packet = []
    try:
        result = get_response(word)
        if result and len(result) > 0:
            entry = result[0]
            if "meanings" in entry and len(entry["meanings"]) > 0:
                meanings = entry["meanings"]
                for meaning in meanings:
                    part_of_speech = meaning["partOfSpeech"]
                    definitions = meaning["definitions"]
                    for definition in definitions:
                        d = definition["definition"]
                        example = definition.get("example")
                        pack = {
                            "part_of_speech": part_of_speech,
                            "definition": d,
                            "example": example,
                        }
                        packet.append(pack)
    except (ValueError, requests.exceptions.RequestException) as e:
        print(f"Error: {e}")
    return packet


def play_word(word):
    # Convert the word to speech
    tts = gTTS(text=word, lang="en")
    temp_file = "temp_audio.mp3"
    tts.save(temp_file)

    # Play the audio file
    playsound(temp_file)

    # Optionally, remove the file after playing
    os.remove(temp_file)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path).replace("\\", "/")


def search_oxford_dictionary(word):
    try:
        query = f"{word} oxford dictionary"
        results = search(query, num_results=1)
        first_link = next(
            (r for r in results if "oxfordlearnersdictionaries" in r), None
        )

        if first_link:
            return first_link
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


# Example usage
if __name__ == "__main__":
    packet = get_word_packet("pristine")
    print(packet)
