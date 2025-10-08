"""
Clipboard Injector - Text-Einfügung
Fügt Text direkt an Cursor-Position ein oder verwendet Zwischenablage.
"""

import logging
import time
from typing import Optional

import pyautogui
import pyperclip

logger = logging.getLogger(__name__)

class ClipboardInjector:
    """Service für Text-Einfügung an Cursor-Position"""

    def __init__(self):
        self.last_clipboard_content = None
        self._backup_clipboard()

    def inject_text(self, text: str) -> bool:
        """Fügt Text an Cursor-Position ein"""
        if not self._validate_text(text):
            return False

        try:
            # Methode 1: Direkt einfügen (bevorzugt)
            success = self._inject_via_typing(text)
            if success:
                logger.info("Text erfolgreich via Tastatur eingefügt")
                return True

        except Exception as e:
            logger.warning(f"Direkte Einfügung fehlgeschlagen: {e}")

        try:
            # Methode 2: Zwischenablage (Fallback)
            success = self._inject_via_clipboard(text)
            if success:
                logger.info("Text erfolgreich via Zwischenablage eingefügt")
                return True

        except Exception as e:
            logger.error(f"Zwischenablage-Einfügung fehlgeschlagen: {e}")

        return False

    def _inject_via_typing(self, text: str) -> bool:
        """Fügt Text durch simulierte Tastatureingabe ein"""
        try:
            # Text in Zwischenablage kopieren
            original_clipboard = pyperclip.paste()
            pyperclip.copy(text)

            # Kurze Pause für Clipboard-Update
            time.sleep(0.1)

            # Ctrl+V simulieren
            pyautogui.hotkey('ctrl', 'v')

            # Kurze Pause für Einfügung
            time.sleep(0.1)

            # Original-Clipboard wiederherstellen
            pyperclip.copy(original_clipboard)

            logger.debug("Text via Tastatur-Simulation eingefügt")
            return True

        except Exception as e:
            logger.warning(f"Fehler bei Tastatur-Simulation: {e}")
            return False

    def _inject_via_clipboard(self, text: str) -> bool:
        """Fügt Text nur in Zwischenablage ein (Fallback)"""
        try:
            # Text in Zwischenablage kopieren
            pyperclip.copy(text)

            logger.info("Text in Zwischenablage kopiert (Fallback-Modus)")
            logger.info("Benutzer muss manuell Ctrl+V drücken")

            return True

        except Exception as e:
            logger.error(f"Fehler beim Kopieren in Zwischenablage: {e}")
            return False

    def _validate_text(self, text: str) -> bool:
        """Validiert den einzufügenden Text"""
        if not text:
            logger.warning("Text zum Einfügen ist leer")
            return False

        if len(text) > 10000:  # Zu langer Text
            logger.warning(f"Text zu lang zum Einfügen: {len(text)} Zeichen")
            return False

        return True

    def _backup_clipboard(self):
        """Sichert aktuellen Clipboard-Inhalt"""
        try:
            self.last_clipboard_content = pyperclip.paste()
        except Exception as e:
            logger.warning(f"Fehler beim Backup des Clipboards: {e}")
            self.last_clipboard_content = ""

    def restore_clipboard(self):
        """Stellt Clipboard wieder her"""
        try:
            if self.last_clipboard_content is not None:
                pyperclip.copy(self.last_clipboard_content)
                logger.debug("Clipboard wiederhergestellt")
        except Exception as e:
            logger.warning(f"Fehler beim Wiederherstellen des Clipboards: {e}")

    def get_clipboard_content(self) -> Optional[str]:
        """Gibt aktuellen Clipboard-Inhalt zurück"""
        try:
            return pyperclip.paste()
        except Exception as e:
            logger.warning(f"Fehler beim Lesen des Clipboards: {e}")
            return None

    def __del__(self):
        """Destructor - stellt Clipboard wieder her"""
        self.restore_clipboard()