"""
Hotkey Listener - Globale Tastenkombination-Erkennung
Erkennt konfigurierbare Hotkeys für Push-to-Talk Funktionalität.
"""

import logging
from typing import Callable, Optional

import keyboard

logger = logging.getLogger(__name__)

class HotkeyListener:
    """Verwaltet globale Hotkey-Erkennung mit konfigurierbaren Hotkeys"""

    def __init__(self):
        self.on_press_callback: Optional[Callable] = None
        self.on_release_callback: Optional[Callable] = None
        self.hotkey_registered = False
        self.registered_hotkeys = []

    def register_callbacks(self, on_press: Callable, on_release: Callable, config=None):
        """Registriert Callbacks für Hotkey Events"""
        self.on_press_callback = on_press
        self.on_release_callback = on_release

        # Versuche benutzerspezifische Hotkeys zu laden
        hotkey_variants = []
        if config:
            # Lade benutzerspezifische Hotkeys
            hotkey_variants.extend([
                config.get_user_hotkey('primary'),
                config.get_user_hotkey('secondary'),
                config.get_user_hotkey('tertiary')
            ])

        # Fallback: Standard-Hotkeys
        if not hotkey_variants:
            hotkey_variants = [
                'f12',                    # F12 (Standard - funktioniert garantiert)
                'f11',                    # F11 (Fallback)
                'f10',                    # F10 (Fallback)
                'ctrl+f12',               # Strg + F12 (falls verfügbar)
                'alt+f12',                # Alt + F12 (falls verfügbar)
            ]

        # Entferne Duplikate
        hotkey_variants = list(dict.fromkeys(hotkey_variants))

        for hotkey in hotkey_variants:
            try:
                keyboard.on_press_key(hotkey, self._on_press_handler)
                keyboard.on_release_key(hotkey, self._on_release_handler)
                self.registered_hotkeys.append(hotkey)
                self.hotkey_registered = True
                logger.info(f"Hotkey '{hotkey}' erfolgreich registriert")
                # Registriere alle verfügbaren Hotkeys, nicht nur den ersten
            except Exception as e:
                logger.warning(f"Hotkey '{hotkey}' nicht verfügbar: {e}")
                continue

        if not self.hotkey_registered:
            logger.error("Kein Hotkey konnte registriert werden")
            raise RuntimeError("Hotkey-Registrierung fehlgeschlagen")

        logger.info(f"Insgesamt {len(self.registered_hotkeys)} Hotkeys registriert: {', '.join(self.registered_hotkeys)}")

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