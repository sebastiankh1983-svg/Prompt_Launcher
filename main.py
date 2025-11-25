"""
main.py - Einstiegspunkt des Prompt-Launchers

Verantwortlichkeiten:
- Anwendung initialisieren
- Doppel-Tap Ctrl erkennen
- Such-Fenster triggern
"""

import sys
import time
import keyboard
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

from ui import SearchWindow
from config import Config


class HotkeyListener(QObject):
    """Erkennt Doppel-Tap auf Ctrl-Taste.

    Nutzt Qt-Signals um thread-sicher mit der UI zu kommunizieren.
    """
    # Signal das gefeuert wird wenn Doppel-Tap erkannt wurde
    triggered = pyqtSignal()

    def __init__(self, threshold: float = 0.3):
        """Args:
            threshold: Maximale Zeit zwischen zwei Ctrl-Taps in Sekunden
        """
        super().__init__()
        self.threshold = threshold
        self.last_ctrl_time = 0
        self.last_ctrl_event = None

    def start(self):
        """Startet den Keyboard-Listener in separatem Thread."""
        keyboard.on_release_key('ctrl', self._on_ctrl_release)
        print("[INFO] Hotkey-Listener gestartet. Drücke Ctrl+Ctrl zum Aktivieren.")

    def _on_ctrl_release(self, event):
        """Callback wenn Ctrl losgelassen wird.

        Prüft ob es ein Doppel-Tap ist basierend auf Zeitdifferenz.
        """
        current_time = time.time()
        time_diff = current_time - self.last_ctrl_time

        if time_diff < self.threshold and time_diff > 0.05:
            # Doppel-Tap erkannt! (> 0.05s um Bouncing zu vermeiden)
            print("[DEBUG] Doppel-Tap erkannt!")
            self.triggered.emit()

        self.last_ctrl_time = current_time


class PromptLauncherApp:
    """Hauptanwendungsklasse.

    Koordiniert alle Komponenten:
    - Qt Application
    - Such-Fenster
    - Hotkey-Listener
    """

    def __init__(self):
        # Qt Application initialisieren
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # Im Hintergrund laufen

        # Konfiguration laden
        self.config = Config()

        # Such-Fenster erstellen (initial versteckt)
        self.search_window = SearchWindow(self.config)

        # Hotkey-Listener erstellen und verbinden
        self.hotkey_listener = HotkeyListener(
            threshold=self.config.get('double_tap_threshold', 0.3)
        )
        self.hotkey_listener.triggered.connect(self._on_hotkey_triggered)

    def _on_hotkey_triggered(self):
        """Wird aufgerufen wenn Doppel-Tap erkannt wurde."""
        if self.search_window.isVisible():
            self.search_window.hide()
        else:
            self.search_window.show_and_focus()

    def run(self):
        """Startet die Anwendung."""
        print("=" * 50)
        print("  PROMPT-LAUNCHER")
        print("  Drücke Ctrl+Ctrl um das Suchfenster zu öffnen")
        print("  Drücke Ctrl+Q im Suchfenster zum Beenden")
        print("=" * 50)

        # Hotkey-Listener starten
        self.hotkey_listener.start()

        # Qt Event-Loop starten
        sys.exit(self.app.exec())


if __name__ == '__main__':
    app = PromptLauncherApp()
    app.run()
