"""
Benutzerspezifisches Konfigurationssystem für Voice Transcriber.
Verwaltet persistente Einstellungen im AppData-Verzeichnis.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from .encryption import secure_storage
except ImportError:
    from encryption import secure_storage

logger = logging.getLogger(__name__)

class UserConfig:
    """Verwaltet benutzerspezifische Konfiguration im AppData-Verzeichnis"""

    # Standardkonfiguration
    DEFAULT_CONFIG = {
        "version": "1.0",
        "hotkeys": {
            "primary": "f12",
            "secondary": "f11",
            "tertiary": "f10"
        },
        "input_method": "hotkey",  # "hotkey" oder "mouse_wheel"
        "mouse_wheel_enabled": False,
        "ui": {
            "theme": "system",
            "minimize_to_tray": True,
            "show_notifications": True
        },
        "audio": {
            "compression_enabled": True,
            "device_index": -1
        }
    }

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._config_file: Path = self.get_config_file()
        self._loaded = False

    @staticmethod
    def get_appdata_dir() -> Path:
        """Gibt das AppData-Verzeichnis für die Anwendung zurück"""
        if os.name == 'nt':  # Windows
            appdata = os.environ.get('APPDATA', '')
            if not appdata:
                # Fallback für Windows ohne APPDATA
                appdata = Path.home() / 'AppData' / 'Roaming'
        else:
            # Unix-like Systeme (Linux, macOS)
            appdata = Path.home() / '.config'

        return Path(appdata) / 'VoiceTranscriber'

    @staticmethod
    def get_config_file() -> Path:
        """Gibt den Pfad zur Konfigurationsdatei zurück"""
        return UserConfig.get_appdata_dir() / 'config.json'

    def load(self) -> bool:
        """Lädt die Konfiguration aus der Datei"""
        try:
            # Stelle sicher, dass das Verzeichnis existiert
            self._config_file.parent.mkdir(parents=True, exist_ok=True)

            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                # Merge mit Defaults (behalte neue Defaults)
                self._config = self._merge_configs(self.DEFAULT_CONFIG, loaded_config)

                # Migriere alte Konfiguration falls nötig
                self._migrate_config()

                logger.info(f"Konfiguration geladen aus: {self._config_file}")
            else:
                # Erstelle neue Konfiguration mit Defaults
                self._config = self.DEFAULT_CONFIG.copy()
                self.save()  # Speichere Defaults
                logger.info(f"Neue Konfiguration erstellt: {self._config_file}")

            self._loaded = True
            return True

        except Exception as e:
            logger.error(f"Fehler beim Laden der Konfiguration: {e}")
            # Fallback: Verwende Defaults
            self._config = self.DEFAULT_CONFIG.copy()
            self._loaded = False
            return False

    def save(self) -> bool:
        """Speichert die Konfiguration in die Datei"""
        try:
            # Stelle sicher, dass das Verzeichnis existiert
            self._config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)

            logger.info(f"Konfiguration gespeichert: {self._config_file}")
            return True

        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Gibt einen Konfigurationswert zurück"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Setzt einen Konfigurationswert"""
        keys = key.split('.')
        config = self._config

        # Navigiere zu dem übergeordneten Dictionary
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        # Setze den Wert
        config[keys[-1]] = value

    def set_encrypted(self, key: str, value: str) -> None:
        """Setzt einen verschlüsselten Konfigurationswert"""
        encrypted_value = secure_storage.encrypt(value)
        self.set(key, encrypted_value)
        logger.debug(f"Verschlüsselter Wert für '{key}' gespeichert")

    def get_decrypted(self, key: str, default: str = "") -> str:
        """Gibt einen entschlüsselten Konfigurationswert zurück"""
        encrypted_value = self.get(key, "")
        if not encrypted_value:
            return default

        try:
            decrypted_value = secure_storage.decrypt(encrypted_value)
            if decrypted_value is None:
                return default
            return decrypted_value
        except Exception as e:
            logger.error(f"Fehler bei Entschlüsselung von '{key}': {e}")
            return default

    def get_hotkey(self, level: str = 'primary') -> str:
        """Gibt einen Hotkey zurück"""
        return self.get(f'hotkeys.{level}', self.DEFAULT_CONFIG['hotkeys'].get(level, 'f12'))

    def set_hotkey(self, level: str, hotkey: str) -> None:
        """Setzt einen Hotkey"""
        self.set(f'hotkeys.{level}', hotkey)

    def is_mouse_wheel_enabled(self) -> bool:
        """Prüft ob mittleres Mausrad aktiviert ist"""
        return self.get('mouse_wheel_enabled', False)

    def enable_mouse_wheel(self, enabled: bool) -> None:
        """Aktiviert/deaktiviert mittleres Mausrad"""
        self.set('mouse_wheel_enabled', enabled)
        if enabled:
            self.set('input_method', 'mouse_wheel')
        else:
            self.set('input_method', 'hotkey')

    def get_input_method(self) -> str:
        """Gibt die Eingabemethode zurück"""
        return self.get('input_method', 'hotkey')

    def _merge_configs(self, defaults: Dict, user_config: Dict) -> Dict:
        """Merged Defaults mit User-Konfiguration"""
        result = defaults.copy()

        for key, value in user_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def _migrate_config(self) -> None:
        """Migriert alte Konfigurationsformate"""
        # Hier können zukünftige Migrationen hinzugefügt werden
        # z.B. Umbenennung von Keys, Änderung von Datenstrukturen

        # Beispiel: Version-basiertes Migrieren
        current_version = self.get('version', '1.0')
        if current_version == '1.0':
            # Migration von 1.0 zu neuerer Version falls nötig
            pass

    def reset_to_defaults(self) -> None:
        """Setzt alle Einstellungen auf Standard zurück"""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save()

    def get_config_path(self) -> Path:
        """Gibt den Pfad zur Konfigurationsdatei zurück (für GUI)"""
        return self._config_file

    def export_config(self, filepath: Path) -> bool:
        """Exportiert die Konfiguration in eine Datei"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Fehler beim Exportieren der Konfiguration: {e}")
            return False

    def import_config(self, filepath: Path) -> bool:
        """Importiert eine Konfiguration aus einer Datei"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            # Validiere grundlegende Struktur
            if not isinstance(imported_config, dict):
                raise ValueError("Ungültiges Konfigurationsformat")

            self._config = self._merge_configs(self.DEFAULT_CONFIG, imported_config)
            self.save()
            return True

        except Exception as e:
            logger.error(f"Fehler beim Importieren der Konfiguration: {e}")
            return False

# Globale Instanz
user_config = UserConfig()