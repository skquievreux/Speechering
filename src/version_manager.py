"""
Version Manager - Verwaltet Versionen heruntergeladener Dateien
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class VersionManager:
    """Verwaltet Versionsinformationen für heruntergeladene Dateien"""

    def __init__(self, version_file: str = "version_info.json"):
        self.version_file = Path(version_file)
        self.version_data: Dict[str, Any] = {}
        self.load_version_info()

    def load_version_info(self):
        """Lädt Versionsinformationen aus Datei"""
        try:
            if self.version_file.exists():
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    self.version_data = json.load(f)
                logger.info(f"Versionsinformationen geladen: {self.version_file}")
            else:
                self.version_data = {
                    "last_updated": datetime.now().isoformat(),
                    "files": {}
                }
                logger.info("Neue Versionsdatei initialisiert")
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Versionsinformationen: {e}")
            self.version_data = {
                "last_updated": datetime.now().isoformat(),
                "files": {}
            }

    def save_version_info(self):
        """Speichert Versionsinformationen in Datei"""
        try:
            self.version_data["last_updated"] = datetime.now().isoformat()
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(self.version_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Versionsinformationen gespeichert: {self.version_file}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Versionsinformationen: {e}")

    def update_file_version(self, file_path: str, version: str, size: int, checksum: Optional[str] = None):
        """Aktualisiert Versionsinformationen für eine Datei"""
        file_name = Path(file_path).name

        if "files" not in self.version_data:
            self.version_data["files"] = {}

        self.version_data["files"][file_name] = {
            "version": version,
            "size": size,
            "checksum": checksum,
            "last_downloaded": datetime.now().isoformat(),
            "path": str(file_path)
        }

        self.save_version_info()
        logger.info(f"Version für {file_name} aktualisiert: {version}")

    def get_file_version(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Gibt Versionsinformationen für eine Datei zurück"""
        file_name = Path(file_path).name

        if "files" in self.version_data and file_name in self.version_data["files"]:
            return self.version_data["files"][file_name]

        return None

    def is_file_up_to_date(self, file_path: str, remote_version: str) -> bool:
        """Prüft ob eine lokale Datei aktuell ist"""
        local_info = self.get_file_version(file_path)

        if not local_info:
            return False

        return local_info.get("version") == remote_version

    def get_installed_version(self, file_path: str) -> Optional[str]:
        """Gibt die installierte Version einer Datei zurück"""
        info = self.get_file_version(file_path)
        return info.get("version") if info else None

    def get_all_versions(self) -> Dict[str, Any]:
        """Gibt alle Versionsinformationen zurück"""
        return self.version_data.copy()

    def cleanup_old_versions(self, keep_days: int = 30):
        """Bereinigt alte Versionsinformationen"""
        try:
            from datetime import timedelta

            cutoff_date = datetime.now() - timedelta(days=keep_days)
            files_to_remove = []

            if "files" in self.version_data:
                for file_name, info in self.version_data["files"].items():
                    if "last_downloaded" in info:
                        last_downloaded = datetime.fromisoformat(info["last_downloaded"])
                        if last_downloaded < cutoff_date:
                            files_to_remove.append(file_name)

            for file_name in files_to_remove:
                del self.version_data["files"][file_name]
                logger.info(f"Alte Version entfernt: {file_name}")

            if files_to_remove:
                self.save_version_info()

        except Exception as e:
            logger.warning(f"Fehler beim Bereinigen alter Versionen: {e}")

# Globale Instanz
version_manager = VersionManager()