"""
Hotkey Listener - Globale Tastenkombination-Erkennung
Erkennt Ctrl+Win Hotkey für Push-to-Talk Funktionalität.
"""

import logging
from typing import Callable, Optional

import keyboard

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

        # Registriere Hotkey: Funktionierende Kombinationen
        hotkey_variants = [
            'f12',                    # F12 (funktioniert immer)
            'f11',                    # F11
            'f10',                    # F10
            'ctrl+shift+s',           # Ctrl+Shift+S
            'alt+shift+s',            # Alt+Shift+S
        ]

        for hotkey in hotkey_variants:
            try:
                keyboard.on_press_key(hotkey, self._on_press_handler)
                keyboard.on_release_key(hotkey, self._on_release_handler)
                self.hotkey_registered = True
                logger.info(f"Hotkey '{hotkey}' erfolgreich registriert")
                break
            except Exception as e:
                logger.warning(f"Hotkey '{hotkey}' nicht verfügbar: {e}")
                continue

        if not self.hotkey_registered:
            logger.error("Kein Hotkey konnte registriert werden")
            raise RuntimeError("Hotkey-Registrierung fehlgeschlagen")

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
        """Prüft ob irgendein Hotkey aktuell gedrückt ist"""
        # Diese Methode ist nicht mehr zuverlässig mit variablen Hotkeys
        # Die keyboard-Bibliothek handhabt das intern
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