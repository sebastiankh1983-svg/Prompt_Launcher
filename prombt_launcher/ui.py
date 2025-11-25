"""
ui.py - PyQt6 Such-Fenster

Ein schlichtes Suchfenster, das:
- als normales Windows-Fenster mit Min/Max/Close erscheint
- Sucheingabe entgegennimmt
- Ergebnisliste anzeigt
- bei Enter den Prompt kopiert und einfügt
- über eine Menüleiste Import und Bearbeitung von Prompts erlaubt
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QLabel,
    QPushButton, QDialog, QFormLayout, QTextEdit, QDialogButtonBox,
    QMenuBar, QMenu, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QKeyEvent, QKeySequence, QShortcut, QAction

from search import PromptSearch
from clipboard_manager import ClipboardManager


class NewPromptDialog(QDialog):
    """Einfacher Dialog zum Anlegen oder Bearbeiten eines Prompts."""

    def __init__(self, parent=None, prompt: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Prompt bearbeiten" if prompt else "Neuen Prompt anlegen")
        self.setModal(True)
        self.setMinimumSize(400, 320)

        self._original_id = prompt.get("id") if prompt else None

        layout = QFormLayout(self)

        self.name_edit = QLineEdit(self)
        self.tags_edit = QLineEdit(self)
        self.prompt_edit = QTextEdit(self)

        if prompt:
            self.name_edit.setText(prompt.get("name", ""))
            self.tags_edit.setText(", ".join(prompt.get("tags", [])))
            self.prompt_edit.setPlainText(prompt.get("prompt", ""))

        layout.addRow("Name (Schlüsselwort)", self.name_edit)
        layout.addRow("Tags (kommagetrennt)", self.tags_edit)
        layout.addRow("Prompt-Text", self.prompt_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        name = self.name_edit.text().strip()
        tags_raw = self.tags_edit.text().strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        prompt_text = self.prompt_edit.toPlainText().strip()
        return name, tags, prompt_text, self._original_id


class SearchWindow(QWidget):
    """Hauptfenster für die Prompt-Suche.

    Features:
    - Normales Windows-Fenster mit Min/Max/Close
    - Menüleiste (Import, Hinzufügen, Bearbeiten)
    - Zentriert auf dem Bildschirm
    - Fuzzy-Search während der Eingabe
    - Tastaturnavigation
    """

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.search_engine = PromptSearch()
        self.clipboard = ClipboardManager()

        self._setup_window()
        self._setup_ui()
        self._setup_shortcuts()

    def _setup_window(self):
        """Konfiguriert Fenster-Eigenschaften."""
        # Normales Fenster, optional always-on-top
        flags = Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        # Feste oder konfigurierbare Größe
        width = int(self.config.get("window_width", 600))
        height = int(self.config.get("window_height", 450))
        self.resize(width, height)

        self.setWindowTitle("Prompt-Launcher")

    def _setup_menu(self, layout: QVBoxLayout):
        """Erstellt eine einfache Menüleiste."""
        menubar = QMenuBar(self)

        # Datei-Menü
        file_menu = QMenu("Datei", self)
        import_action = QAction("Bibliothek importieren…", self)
        import_action.triggered.connect(self._import_library)
        exit_action = QAction("Beenden", self)
        exit_action.triggered.connect(lambda: __import__("sys").exit(0))
        file_menu.addAction(import_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Bearbeiten-Menü
        edit_menu = QMenu("Bearbeiten", self)
        add_action = QAction("Neuen Prompt hinzufügen…", self)
        add_action.setShortcut("Ctrl+N")
        add_action.triggered.connect(self._on_add_prompt_clicked)
        edit_action = QAction("Ausgewählten Prompt bearbeiten…", self)
        edit_action.setShortcut("Ctrl+E")
        edit_action.triggered.connect(self._edit_selected_prompt)
        edit_menu.addAction(add_action)
        edit_menu.addAction(edit_action)

        # Hilfe-Menü
        help_menu = QMenu("Hilfe", self)
        about_action = QAction("Über…", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        menubar.addMenu(file_menu)
        menubar.addMenu(edit_menu)
        menubar.addMenu(help_menu)

        layout.setMenuBar(menubar)

    def _setup_ui(self):
        """Erstellt die UI-Elemente."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Menüleiste
        self._setup_menu(layout)

        # Titel
        title = QLabel("Prompt-Launcher")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title)

        # Suchfeld
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Prompt suchen…")
        self.search_input.setFont(QFont("Segoe UI", 11))
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)

        # Ergebnisliste
        self.results_list = QListWidget()
        self.results_list.setFont(QFont("Segoe UI", 10))
        self.results_list.itemActivated.connect(self._on_item_selected)
        layout.addWidget(self.results_list)

        # Hilfe-Text
        help_text = QLabel("↑↓ Navigieren • Enter Auswählen • Esc Schließen • Ctrl+N Neuer Prompt")
        help_text.setFont(QFont("Segoe UI", 8))
        help_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(help_text)

        # Info-Zeile
        info = QLabel("Erstellt von Sebastian Kühnrich")
        info.setFont(QFont("Segoe UI", 8))
        info.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(info)

        # Initiale Ergebnisse laden
        self._update_results("")

    def _setup_shortcuts(self):
        """Konfiguriert Tastaturkürzel."""
        # Escape zum Schließen
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.hide)

        # Ctrl+Q zum Beenden der gesamten Anwendung
        QShortcut(
            QKeySequence("Ctrl+Q"),
            self,
            lambda: __import__("sys").exit(0),
        )

    def keyPressEvent(self, event: QKeyEvent):
        """Behandelt Tastatureingaben für Navigation."""
        key = event.key()

        if key == Qt.Key.Key_Down:
            current = self.results_list.currentRow()
            if current < self.results_list.count() - 1:
                self.results_list.setCurrentRow(current + 1)
        elif key == Qt.Key.Key_Up:
            current = self.results_list.currentRow()
            if current > 0:
                self.results_list.setCurrentRow(current - 1)
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            current_item = self.results_list.currentItem()
            if current_item:
                self._on_item_selected(current_item)
        else:
            super().keyPressEvent(event)

    def _on_search_changed(self, text: str):
        """Wird aufgerufen wenn sich der Suchtext ändert."""
        self._update_results(text)

    def _update_results(self, query: str):
        """Aktualisiert die Ergebnisliste basierend auf der Suche."""
        self.results_list.clear()

        results = self.search_engine.search(
            query, limit=self.config.get("max_results", 20)
        )

        for prompt in results:
            item = QListWidgetItem()
            item.setText(prompt.get("name", "(ohne Namen)"))
            item.setData(Qt.ItemDataRole.UserRole, prompt)
            self.results_list.addItem(item)

        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

    def _on_item_selected(self, item: QListWidgetItem):
        """Wird aufgerufen wenn ein Prompt ausgewählt wurde."""
        prompt_data = item.data(Qt.ItemDataRole.UserRole)

        if prompt_data:
            self.clipboard.copy(prompt_data.get("prompt", ""))
            self.hide()
            QTimer.singleShot(100, self.clipboard.paste)
            if "id" in prompt_data:
                self.search_engine.increment_usage(prompt_data["id"])
            print(f"[INFO] Prompt eingefügt: {prompt_data.get('name')}")

    def _on_add_prompt_clicked(self):
        """Öffnet den Dialog zum Anlegen eines neuen Prompts."""
        dialog = NewPromptDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, tags, prompt_text, _ = dialog.get_data()
            if not name or not prompt_text:
                return
            new_prompt = self.search_engine.add_prompt(name, prompt_text, tags)
            print(f"[INFO] Neuer Prompt angelegt: {new_prompt.get('name')} ({new_prompt.get('id')})")
            current_query = self.search_input.text()
            self._update_results(current_query)

    def _edit_selected_prompt(self):
        """Bearbeitet den aktuell ausgewählten Prompt (User-Prompts werden ersetzt)."""
        current_item = self.results_list.currentItem()
        if not current_item:
            return
        prompt_data = current_item.data(Qt.ItemDataRole.UserRole)
        if not prompt_data:
            return

        dialog = NewPromptDialog(self, prompt=prompt_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, tags, prompt_text, original_id = dialog.get_data()
            if not name or not prompt_text or not original_id:
                return
            updated = self.search_engine.update_prompt(original_id, name, prompt_text, tags)
            if updated:
                print(f"[INFO] Prompt aktualisiert: {updated.get('name')} ({updated.get('id')})")
                current_query = self.search_input.text()
                self._update_results(current_query)

    def _import_library(self):
        """Importiert eine externe Prompt-Bibliothek (JSON)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Prompt-Bibliothek importieren",
            "",
            "JSON-Dateien (*.json)"
        )
        if not file_path:
            return
        self.search_engine.add_library(file_path)
        self._update_results(self.search_input.text())
        QMessageBox.information(
            self,
            "Import abgeschlossen",
            "Die Bibliothek wurde importiert und in die Suche aufgenommen.",
        )

    def _show_about(self):
        """Zeigt einen einfachen Info-Dialog."""
        QMessageBox.information(
            self,
            "Über Prompt-Launcher",
            "Prompt-Launcher\n\nCtrl+Ctrl öffnen • Suche tippen • Enter einfügen",
        )

    def show_and_focus(self):
        """Zeigt das Fenster und fokussiert das Suchfeld."""
        screen = self.screen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 3
        self.move(x, y)

        self.search_input.clear()
        self.show()
        self.activateWindow()
        self.search_input.setFocus()
