import requests
import aqt
from anki import hooks
from aqt.utils import showInfo
from aqt.qt import *
from aqt.editor import Editor
from anki import sound
from shutil import copyfile
from .lib.forvo import Forvo
from .config import CONFIG


def doPaste(self, html, internal, extended=False):
    target_field_index = CONFIG.get("PASTE_TARGET_FIELD_INDEX", None)

    if target_field_index is None or target_field_index == self.currentField:
        find_pronunciations(self, True, True)


if CONFIG.get("AUTO_ADD_AUDIO_ON_PASTE", False):
    Editor.doPaste = hooks.wrap(Editor.doPaste, doPaste)


sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))


FORVO_API_KEY = CONFIG.get("FORVO_API_KEY", None)
FORVO_FAVORITE_USERS = CONFIG.get("FORVO_FAVORITE_USERS", [])
OUTPUT_FIELD_INDEX = CONFIG.get("OUTPUT_FIELD_INDEX", 0)
AUDIO_FILE_FORMAT = "mp3"


class PlayButton(QPushButton):
    def __init__(self, pron):
        QPushButton.__init__(self, "Play")
        self.pron = pron
        self.clicked.connect(self.play)

    def play(self):
        filename = download_pronunciation(self.pron)
        sound.clearAudioQueue()
        sound.play(filename)


class ChooseButton(QPushButton):
    def __init__(self, editor, dialog, pron):
        QPushButton.__init__(self, "Choose")
        self.pron = pron
        self.dialog = dialog
        self.editor = editor
        self.clicked.connect(self.choose)

    def choose(self):
        download_and_add_pronunciation(self.editor, self.pron)
        self.dialog.accept()


def file_exists(filename):
    return os.path.isfile(filename)


def download_file(url, filename):
    response = requests.get(url)

    with open(filename, 'wb') as f:
        f.write(response.content)


def download_pronunciation(pron):
    filename_with_username = get_pronunciation_filename(pron["word"], pron["username"])
    filename = get_pronunciation_filename(pron["word"], None)

    if not file_exists(filename_with_username):
        download_file(pron["pathmp3"], filename_with_username)

    copyfile(filename_with_username, filename)

    return filename


def get_pronunciation_filename(word, username=None):
    return "{}{}.{}".format(word, "" if not username else "_" + username, AUDIO_FILE_FORMAT)


def pronunciation_exists_for_word(word):
    return file_exists(get_pronunciation_filename(word, None))


def add_pronunciation(editor, filename):
    editor.web.eval("caretToEnd(); focusField({})".format(OUTPUT_FIELD_INDEX))
    editor.addMedia(filename)


def download_and_add_pronunciation(editor, pron):
    filename = download_pronunciation(pron)
    add_pronunciation(editor, filename)


def filter_favorites(prons):
    favorites = []

    for username in FORVO_FAVORITE_USERS:
        for pron in prons:
            if pron["username"] == username:
                favorites.append(pron)

    return favorites


def find_pronunciations_for_word(word):
    key = CONFIG.get("FORVO_API_KEY", None)
    if not key:
        showInfo("FORVO_API_KEY is required in config.py")
        return []

    forvo = Forvo(api_key=key)

    return forvo.get_word_pronunciations(word,
                                         limit=CONFIG.get("FORVO_MAX_RESULTS", None),
                                         language=CONFIG.get("FORVO_LANGUAGE", None))


def add_pronunciation_from_list(editor, pronunciations):
    parent = aqt.mw.app.activeWindow()
    dialog = QDialog(parent)
    dialog.setWindowTitle("Choose pronunciation")
    dialog.setWindowModality(Qt.WindowModal)
    dialog.setLayout(QVBoxLayout())

    for pron in pronunciations:
        layout1 = QVBoxLayout()
        layout1.addWidget(QLabel(pron["username"]))
        layout2 = QHBoxLayout()
        play_button = PlayButton(pron)
        choose_button = ChooseButton(editor, dialog, pron)
        layout2.addWidget(play_button)
        layout2.addWidget(choose_button)
        layout1.addLayout(layout2)
        dialog.layout().addLayout(layout1)

    dialog.exec_()


def find_pronunciations(editor, autoadd_enabled=False, use_clipboard=False):
    word = str(editor.web.selectedText()).strip()

    if not word and use_clipboard:
        # Use clipboard if nothing is selected
        word = QApplication.clipboard().text()

    if not word:
        return

    if " " in word:
        showInfo("Sorry, singular words only.")
        return

    if autoadd_enabled and pronunciation_exists_for_word(word):
        add_pronunciation(editor, get_pronunciation_filename(word))
        return

    prons = find_pronunciations_for_word(word)

    if not prons:
        showInfo("No pronunciations available for " + word)
        return

    if autoadd_enabled:
        if len(prons) == 1:
            download_and_add_pronunciation(editor, prons[0])
            return

        favorites = filter_favorites(prons)

        if len(favorites) > 0:
            download_and_add_pronunciation(editor, favorites[0])
            return

    add_pronunciation_from_list(editor, prons)


def setup_shortcuts(shortcuts, editor):
    use_clipboard = CONFIG.get("USE_CLIPBOARD_IF_NO_SELECTION", False)

    shortcuts.append((CONFIG.get("FIND_PRONUNCIATIONS_HOTKEY", "Ctrl+Shift+F"),
                      lambda e=editor: find_pronunciations(editor, use_clipboard=use_clipboard)))
    shortcuts.append((CONFIG.get("FIND_PRONUNCIATIONS_WITH_AUTOADD_HOTKEY", "Ctrl+F"),
                      lambda e=editor: find_pronunciations(editor, autoadd_enabled=True, use_clipboard=use_clipboard)))


hooks.addHook("setupEditorShortcuts", setup_shortcuts)
