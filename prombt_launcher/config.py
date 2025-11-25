"""
config.py - Konfigurationsverwaltung

Lädt und speichert Benutzereinstellungen.
"""

import json
from pathlib import Path
from typing import Any, Optional


class Config:
    """Verwaltet die Anwendungskonfiguration.

    Standardwerte werden mit benutzerspezifischen Einstellungen
    aus config.json überschrieben.
    """

    DEFAULT_CONFIG = {
        "double_tap_threshold": 0.3,
        "auto_paste": True,
        "restore_clipboard": False,
        "max_results": 7,
        "window_width": 500,
        "window_height": 400,
        "library_paths": [
            "data/prompts.json",
        ],
    }

    def __init__(self, config_path: Optional[str] = None):
        """Args:
            config_path: Pfad zur Konfigurationsdatei. Standard: config.json
        """
        self.config_path = Path(config_path or "config.json")
        self.config = self.DEFAULT_CONFIG.copy()
        self._load()

    def _load(self):
        """Lädt die Konfiguration aus der Datei."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
                print(f"[INFO] Konfiguration geladen: {self.config_path}")
            except Exception as e:
                print(f"[WARNING] Fehler beim Laden der Config: {e}")
                print("[INFO] Verwende Standardkonfiguration")
        else:
            self._save()
            print(f"[INFO] Standard-Konfiguration erstellt: {self.config_path}")

    def _save(self):
        """Speichert die aktuelle Konfiguration."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Fehler beim Speichern der Config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Gibt einen Konfigurationswert zurück."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any, persist: bool = True):
        """Setzt einen Konfigurationswert."""
        self.config[key] = value
        if persist:
            self._save()
