from .secret import FORVO_API_KEY

CONFIG = {
    "FORVO_API_KEY": FORVO_API_KEY,
    "FORVO_MAX_RESULTS": 5,
    "FORVO_LANGUAGE": "ko",

    # If provided, automatically selects pronunciations by these users (first match in the list is chosen)
    "FORVO_FAVORITE_USERS": [
        "heechang2",
        "ssoonkimi"
    ],

    # Index of the field where the audio is added. For example, in basic anki cards 0 is front and 1 is back
    "OUTPUT_FIELD_INDEX": 1,

    "FIND_PRONUNCIATIONS_HOTKEY": "Ctrl+Shift+F",
    "FIND_PRONUNCIATIONS_WITH_AUTOADD_HOTKEY": "Ctrl+F",

    "USE_CLIPBOARD_IF_NO_SELECTION": True
    "AUTO_ADD_AUDIO_ON_PASTE": True
}