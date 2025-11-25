# Prompt-Launcher

Ein schlankes Windows-Tool, um häufig genutzte KI-Prompts per Tastaturkürzel schnell einzufügen.

## Features

- Systemweiter Hotkey: **Ctrl+Ctrl** öffnet den Launcher
- Suche nach Prompts (Name + Tags) mit Fuzzy-Suche
- Prompts werden automatisch kopiert und mit **Ctrl+V** eingefügt
- Eigene Prompts hinzufügen und bearbeiten (werden in `data/user_prompts.json` gespeichert)
- Externe JSON-Promptbibliotheken importieren

Erstellt von **Sebastian Kühnrich**.

## Installation (Windows)

Voraussetzungen:

- Windows 10/11
- Python 3.10 oder höher installiert

### 1. Projektordner vorbereiten

Lade den Projektordner (z.B. als ZIP) auf den Zielrechner und entpacke ihn, z.B. nach:

```cmd
C:\Tools\prompt-launcher
```

### 2. Virtuelle Umgebung anlegen

Öffne eine Eingabeaufforderung (cmd) und führe aus:

```cmd
cd C:\Tools\prompt-launcher
python -m venv venv
venv\Scripts\activate
```

### 3. Abhängigkeiten installieren

```cmd
pip install -r requirements.txt
```

### 4. Prompt-Launcher starten

```cmd
cd C:\Tools\prompt-launcher
venv\Scripts\activate
python main.py
```

In der Konsole erscheint ein Hinweis, dass der Hotkey-Listener läuft.

## Schnelleinstieg (ohne Konsole)

Für Nutzer, die keine Befehle eingeben möchten:

1. Projektordner (z.B. `prompt-launcher`) an einen Ort wie `C:\Tools\prompt-launcher` kopieren.
2. Im Ordner **`setup_and_run.bat`** doppelklicken.
   - Das Skript richtet automatisch die Python-Umgebung ein und startet den Prompt-Launcher.
3. Für spätere Starts kann entweder erneut `setup_and_run.bat` oder **`run_launcher.bat`** verwendet werden.

### Autostart beim Windows-Login

1. `Win + R` drücken, `shell:startup` eingeben und Enter drücken.
2. Im geöffneten Autostart-Ordner eine **Verknüpfung** zu `run_launcher.bat` anlegen (Rechtsklick → Neu → Verknüpfung).
3. Beim nächsten Anmelden unter Windows wird der Prompt-Launcher automatisch gestartet (sofern er nicht manuell beendet wurde).

## Bedienung

- **Ctrl+Ctrl**: Prompt-Launcher öffnen
- Im Fenster:
  - Text im Suchfeld eingeben → passende Prompts werden angezeigt
  - Mit **↑/↓** durch die Liste navigieren
  - Mit **Enter** gewünschten Prompt auswählen → Text wird ins aktive Fenster eingefügt

### Menüleiste

- **Datei → Bibliothek importieren…**
  - JSON-Datei mit Prompts importieren (Liste oder `{ "prompts": [ ... ] }`).
- **Bearbeiten → Neuen Prompt hinzufügen…** (`Ctrl+N`)
  - Eigenen Prompt mit Name, Tags und Text anlegen.
- **Bearbeiten → Ausgewählten Prompt bearbeiten…** (`Ctrl+E`)
  - Gewählten Prompt optimieren; Änderungen werden in `data/user_prompts.json` gespeichert.
- **Datei → Beenden** oder **Ctrl+Q**
  - Anwendung beenden.

## Prompt-Daten

- Vorinstallierte Prompts: `data/prompts.json`
- Eigene Prompts: `data/user_prompts.json`

Die Struktur eines Prompt-Eintrags:

```json
{
  "id": "mein-prompt",
  "name": "Mein Prompt",
  "tags": ["tag1", "tag2"],
  "prompt": "Der eigentliche Prompt-Text",
  "placeholders": [],
  "usage_count": 0
}
```

## Weitergabe

Um das Tool weiterzugeben:

1. Kompletten Projektordner (inkl. `data/`, `main.py`, `ui.py`, `search.py`, `clipboard_manager.py`, `config.py`, `requirements.txt`) zippen.
2. ZIP auf dem Zielrechner entpacken.
3. Schritte aus **Installation** auf dem Zielrechner ausführen.

Empfehlung: Lege eine Desktop-Verknüpfung an, die ein Skript startet, das automatisch die venv aktiviert und `python main.py` ausführt.
