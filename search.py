"""
search.py - Fuzzy-Search Engine für Prompts

Nutzt rapidfuzz für performantes, tippfehler-tolerantes Matching.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from rapidfuzz import fuzz, process


class PromptSearch:
    """Such-Engine für die Prompt-Bibliothek.

    Features:
    - Fuzzy-Matching mit rapidfuzz
    - Gewichtung nach Usage-Count
    - Suche in Name und Tags
    - Unterstützung für zusätzliche Bibliotheken und User-Prompts
    """

    def __init__(self, library_paths: Optional[List[str]] = None):
        """Args:
            library_paths: Liste von Pfaden zu JSON-Bibliotheken.
                           Standard: data/prompts.json und data/user_prompts.json
        """
        base_dir = Path(__file__).parent
        default_paths = [
            base_dir / "data" / "prompts.json",
            base_dir / "data" / "user_prompts.json",
        ]
        self.library_paths: List[Path] = [Path(p) for p in (library_paths or default_paths)]
        self.prompts: List[Dict] = []
        self._load_libraries()

    def _load_libraries(self):
        """Lädt alle Prompt-Bibliotheken."""
        self.prompts = []

        for path in self.library_paths:
            path = Path(path)
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        raw = f.read().strip()
                        if not raw:
                            data = []
                        else:
                            data = json.loads(raw)
                    if isinstance(data, list):
                        self.prompts.extend(data)
                    elif isinstance(data, dict) and "prompts" in data:
                        self.prompts.extend(data["prompts"])
                    print(f"[INFO] Bibliothek geladen: {path} ({len(self.prompts)} Prompts)")
                except Exception as e:
                    print(f"[ERROR] Fehler beim Laden von {path}: {e}")
            else:
                print(f"[WARNING] Bibliothek nicht gefunden: {path}")

        print(f"[INFO] Gesamt: {len(self.prompts)} Prompts geladen")

    def reload(self):
        """Lädt alle Bibliotheken neu."""
        self._load_libraries()

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Sucht Prompts basierend auf der Anfrage."""
        if not query.strip():
            return self._get_top_prompts(limit)

        searchable: List[str] = []
        for prompt in self.prompts:
            search_text = prompt.get("name", "")
            tags = prompt.get("tags") or []
            if tags:
                search_text += " " + " ".join(tags)
            searchable.append(search_text)

        if not searchable:
            return []

        results = process.extract(
            query,
            searchable,
            scorer=fuzz.WRatio,
            limit=limit * 2,
        )

        matched_prompts: List[Dict] = []
        for match_text, score, index in results:
            if score >= 50:
                prompt = self.prompts[index].copy()
                prompt["_score"] = score
                usage_bonus = min(prompt.get("usage_count", 0) * 2, 20)
                prompt["_final_score"] = score + usage_bonus
                matched_prompts.append(prompt)

        matched_prompts.sort(key=lambda x: x["_final_score"], reverse=True)
        return matched_prompts[:limit]

    def _get_top_prompts(self, limit: int) -> List[Dict]:
        """Gibt die meistgenutzten Prompts zurück."""
        sorted_prompts = sorted(
            self.prompts,
            key=lambda x: x.get("usage_count", 0),
            reverse=True,
        )
        return sorted_prompts[:limit]

    def increment_usage(self, prompt_id: str):
        """Erhöht den Usage-Counter für einen Prompt."""
        for prompt in self.prompts:
            if prompt.get("id") == prompt_id:
                prompt["usage_count"] = prompt.get("usage_count", 0) + 1
                self._save_usage_counts()
                break

    def _save_usage_counts(self):
        """Speichert die aktualisierten Usage-Counts.

        Für den MVP: schreibt alle Prompts zurück in die erste Bibliothek.
        """
        if not self.library_paths:
            return
        path = Path(self.library_paths[0])
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.prompts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] Fehler beim Speichern: {e}")

    def add_library(self, path: str):
        """Fügt eine neue Bibliothek hinzu und lädt sie."""
        p = Path(path)
        if p not in self.library_paths:
            self.library_paths.append(p)
        self._load_libraries()

    def add_prompt(self, name: str, prompt_text: str, tags: Optional[List[str]] = None) -> Dict:
        """Fügt einen neuen Prompt zur User-Bibliothek hinzu.

        - Speichert in data/user_prompts.json
        - Generiert eine einfache ID auf Basis des Namens
        """
        tags = tags or []
        prompt_id_base = name.strip().lower().replace(" ", "-")
        prompt_id = prompt_id_base
        existing_ids = {p.get("id") for p in self.prompts}
        i = 1
        while prompt_id in existing_ids:
            prompt_id = f"{prompt_id_base}-{i}"
            i += 1

        new_prompt = {
            "id": prompt_id,
            "name": name,
            "tags": tags,
            "prompt": prompt_text,
            "placeholders": [],
            "usage_count": 0,
        }

        # Im Speicher ergänzen
        self.prompts.append(new_prompt)

        # In user_prompts.json persistieren
        user_path = Path(__file__).parent / "data" / "user_prompts.json"
        try:
            if user_path.exists():
                with open(user_path, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
                    user_data = json.loads(raw) if raw else []
            else:
                user_data = []
            if isinstance(user_data, dict) and "prompts" in user_data:
                user_data = user_data["prompts"]
            user_data.append(new_prompt)
            with open(user_path, "w", encoding="utf-8") as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] Fehler beim Speichern in user_prompts.json: {e}")

        return new_prompt

    def update_prompt(self, prompt_id: str, name: str, prompt_text: str, tags: Optional[List[str]] = None) -> Optional[Dict]:
        """Aktualisiert einen bestehenden Prompt in der User-Bibliothek.

        - Sucht nach id == prompt_id in self.prompts
        - Aktualisiert Felder name, tags, prompt
        - Schreibt Änderungen nach data/user_prompts.json
        """
        tags = tags or []
        updated_prompt: Optional[Dict] = None

        # In Memory aktualisieren
        for p in self.prompts:
            if p.get("id") == prompt_id:
                p["name"] = name
                p["tags"] = tags
                p["prompt"] = prompt_text
                updated_prompt = p
                break

        if updated_prompt is None:
            return None

        # user_prompts.json aktualisieren
        user_path = Path(__file__).parent / "data" / "user_prompts.json"
        try:
            user_data: List[Dict]
            if user_path.exists():
                with open(user_path, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
                    user_data = json.loads(raw) if raw else []
            else:
                user_data = []

            if isinstance(user_data, dict) and "prompts" in user_data:
                user_data = user_data["prompts"]

            found = False
            for up in user_data:
                if up.get("id") == prompt_id:
                    up.update({
                        "name": name,
                        "tags": tags,
                        "prompt": prompt_text,
                    })
                    found = True
                    break
            if not found:
                user_data.append(updated_prompt)

            with open(user_path, "w", encoding="utf-8") as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] Fehler beim Aktualisieren in user_prompts.json: {e}")

        return updated_prompt
