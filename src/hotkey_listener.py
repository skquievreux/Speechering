"""
Hotkey Listener - Globale Tastenkombination-Erkennung
Erkennt Ctrl+Win Hotkey für Push-to-Talk Funktionalität.
"""

import logging
import keyboard
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class HotkeyListener:
    """Verwaltet globale Hotkey-Erkennung"""

    def __init__(self):
        self.on_press_callback: Optional[Callable] = None
        self.on_release_callback: Optional[Callable] = None
        self.hotkey_registered = False

    def register_callbacks(self, on_press: Callable, on_release: Callable):
        """Registriert Callbacks für Hotkey Events"""
        self.on_press_callback = on_press
        self.on_release_callback = on_release

        # Registriere Hotkey: Ctrl + Left Windows
        try:
            keyboard.on_press_key('ctrl+left windows', self._on_press_handler)
            keyboard.on_release_key('ctrl+left windows', self._on_release_handler)
            self.hotkey_registered = True
            logger.info("Hotkey 'Ctrl+Win' erfolgreich registriert")
        except Exception as e:
            logger.error(f"Fehler bei Hotkey-Registrierung: {e}")
            raise

    def _on_press_handler(self, event):
        """Handler für Hotkey-Drücken"""
        if self.on_press_callback:
            try:
                self.on_press_callback()
            except Exception as e:
                logger.error(f"Fehler im on_press Callback: {e}")

    def _on_release_handler(self, event):
        """Handler für Hotkey-Loslassen"""
        if self.on_release_callback:
            try:
                self.on_release_callback()
            except Exception as e:
                logger.error(f"Fehler im on_release Callback: {e}")

    def is_hotkey_pressed(self) -> bool:
        """Prüft ob der Hotkey aktuell gedrückt ist"""
        try:
            return keyboard.is_pressed('ctrl+left windows')
        except Exception as e:
            logger.warning(f"Fehler beim Prüfen des Hotkey-Status: {e}")
            return False

    def cleanup(self):
        """Räumt Hotkey-Listener auf"""
        try:
            if self.hotkey_registered:
                keyboard.unhook_all()
                self.hotkey_registered = False
                logger.info("Hotkey-Listener aufgeräumt")
        except Exception as e:
            logger.warning(f"Fehler beim Aufräumen des Hotkey-Listeners: {e}")

    def __del__(self):
        """Destructor - stellt sicher dass aufgeräumt wird"""
        self.cleanup()