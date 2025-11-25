"""
clipboard_manager.py - Clipboard-Verwaltung

Kopiert Prompts in die Zwischenablage und simuliert Ctrl+V zum Einfügen.
"""

import time

import keyboard
import pyperclip


class ClipboardManager:
    """Verwaltet Clipboard-Operationen.

    Features:
    - Text in Clipboard kopieren
    - Ctrl+V simulieren für Auto-Paste
    - Vorherigen Clipboard-Inhalt optional wiederherstellen
    """

    def __init__(self, restore_clipboard: bool = False):
        """Args:
            restore_clipboard: Wenn True, wird der vorherige Clipboard-Inhalt
                               nach dem Einfügen wiederhergestellt.
        """
        self.restore_clipboard = restore_clipboard
        self._previous_content = None

    def copy(self, text: str):
        """Kopiert Text in die Zwischenablage."""
        if self.restore_clipboard:
            try:
                self._previous_content = pyperclip.paste()
            except Exception:
                self._previous_content = None
        pyperclip.copy(text)

    def paste(self):
        """Simuliert Ctrl+V zum Einfügen."""
        time.sleep(0.05)
        keyboard.send("ctrl+v")

        if self.restore_clipboard and self._previous_content is not None:
            time.sleep(0.1)
            pyperclip.copy(self._previous_content)
            self._previous_content = None

    def get_current(self) -> str:
        """Gibt den aktuellen Clipboard-Inhalt zurück."""
        try:
            return pyperclip.paste()
        except Exception:
            return ""
