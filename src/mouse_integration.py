"""
Mittleres Mausrad Integration für Voice Transcriber.
Verwaltet AutoHotkey-Skript für mausbasierte Eingabe.
"""

import logging
import os
import subprocess
from pathlib import Path

try:
    from .resources import get_resource_path
except ImportError:
    from resources import get_resource_path

logger = logging.getLogger(__name__)

class MouseWheelIntegration:
    """Verwaltet die Integration des mittleren Mausrads über AutoHotkey"""

    def __init__(self):
        self.ahk_process: subprocess.Popen | None = None
        self.ahk_script_path: Path = self._get_ahk_script_path()

    def _get_ahk_script_path(self) -> Path:
        """Gibt den Pfad zum AHK-Skript zurück"""
        return get_resource_path('scripts/mouse_toggle.ahk')

    def is_ahk_available(self) -> bool:
        """Prüft ob AutoHotkey verfügbar ist"""
        try:
            # Suche nach AutoHotkey in verschiedenen Pfaden
            possible_paths = [
                r'C:\Program Files\AutoHotkey\AutoHotkey.exe',
                r'C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe',
                'AutoHotkey.exe',  # Im PATH
            ]

            for path in possible_paths:
                try:
                    result = subprocess.run([path, '/?'], capture_output=True, timeout=5)
                    if result.returncode == 0:
                        logger.info(f"AutoHotkey gefunden: {path}")
                        return True
                except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                    continue

            logger.warning("AutoHotkey nicht gefunden")
            return False

        except Exception as e:
            logger.error(f"Fehler bei AHK-Verfügbarkeitsprüfung: {e}")
            return False

    def start(self) -> bool:
        """Startet das AHK-Skript"""
        if not self.ahk_script_path.exists():
            logger.error(f"AHK-Skript nicht gefunden: {self.ahk_script_path}")
            return False

        if not self.is_ahk_available():
            logger.warning("AutoHotkey nicht verfügbar - mittleres Mausrad deaktiviert")
            return False

        try:
            # Starte AHK-Skript
            self.ahk_process = subprocess.Popen(
                ['AutoHotkey.exe', str(self.ahk_script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            logger.info(f"AHK-Skript gestartet: {self.ahk_script_path}")
            return True

        except Exception as e:
            logger.error(f"Fehler beim Starten des AHK-Skripts: {e}")
            return False

    def stop(self) -> bool:
        """Stoppt das AHK-Skript"""
        if self.ahk_process:
            try:
                self.ahk_process.terminate()
                self.ahk_process.wait(timeout=5)
                self.ahk_process = None
                logger.info("AHK-Skript gestoppt")
                return True
            except subprocess.TimeoutExpired:
                logger.warning("AHK-Skript konnte nicht sauber beendet werden")
                self.ahk_process.kill()
                return False
            except Exception as e:
                logger.error(f"Fehler beim Stoppen des AHK-Skripts: {e}")
                return False

        return True

    def is_running(self) -> bool:
        """Prüft ob das AHK-Skript läuft"""
        if self.ahk_process:
            return self.ahk_process.poll() is None
        return False

    def restart(self) -> bool:
        """Startet das AHK-Skript neu"""
        self.stop()
        return self.start()

    def get_script_path(self) -> Path:
        """Gibt den Pfad zum AHK-Skript zurück (für Debugging)"""
        return self.ahk_script_path

    def __del__(self):
        """Destructor - stellt sicher dass AHK gestoppt wird"""
        self.stop()
