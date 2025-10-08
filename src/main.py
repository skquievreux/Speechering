"""
Voice Transcriber - Hauptmodul (Orchestrator)
Koordiniert alle Komponenten der Anwendung.
"""

import sys
import logging
import threading
from typing import Optional, Callable
import pystray
from PIL import Image
import keyboard
import winsound

from .config import config
from .hotkey_listener import HotkeyListener
from .audio_recorder import AudioRecorder
from .transcription import TranscriptionService
from .text_processor import TextProcessor
from .clipboard_injector import ClipboardInjector

logger = logging.getLogger(__name__)

class VoiceTranscriberApp:
    """Hauptklasse der Voice Transcriber Anwendung"""

    def __init__(self):
        self.tray_icon: Optional[pystray.Icon] = None
        self.hotkey_listener: Optional[HotkeyListener] = None
        self.audio_recorder: Optional[AudioRecorder] = None
        self.transcription_service: Optional[TranscriptionService] = None
        self.text_processor: Optional[TextProcessor] = None
        self.clipboard_injector: Optional[ClipboardInjector] = None

        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None

    def initialize_components(self):
        """Initialisiert alle Anwendungskomponenten"""
        try:
            logger.info("Initialisiere Anwendungskomponenten...")

            # Komponenten erstellen
            self.hotkey_listener = HotkeyListener()
            self.audio_recorder = AudioRecorder()
            self.transcription_service = TranscriptionService()
            self.text_processor = TextProcessor()
            self.clipboard_injector = ClipboardInjector()

            # Hotkey Callbacks registrieren
            self.hotkey_listener.register_callbacks(
                on_press=self.on_hotkey_press,
                on_release=self.on_hotkey_release
            )

            logger.info("Alle Komponenten erfolgreich initialisiert")
            return True

        except Exception as e:
            logger.error(f"Fehler bei der Initialisierung: {e}")
            return False

    def create_tray_icon(self):
        """Erstellt das System Tray Icon"""
        try:
            # Lade Icon (fallback auf generisches Icon)
            icon_path = "assets/icon.ico"
            try:
                icon = Image.open(icon_path)
            except FileNotFoundError:
                # Erstelle einfaches Icon
                icon = Image.new('RGB', (64, 64), color='blue')

            # Tray Menü
            menu = pystray.Menu(
                pystray.MenuItem("Status: Bereit", lambda: None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Einstellungen", self.show_settings),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Beenden", self.quit_application)
            )

            self.tray_icon = pystray.Icon(
                "voice_transcriber",
                icon,
                f"{config.APP_NAME} v{config.APP_VERSION}",
                menu
            )

            logger.info("System Tray Icon erstellt")
            return True

        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Tray Icons: {e}")
            return False

    def on_hotkey_press(self):
        """Callback bei Hotkey-Drücken (Start Aufnahme)"""
        if self.is_recording:
            return

        logger.info("Hotkey gedrückt - Starte Aufnahme")
        self.is_recording = True

        # Akustisches Feedback
        self.play_beep(config.BEEP_FREQUENCY_START)

        # Starte Aufnahme in separatem Thread
        self.recording_thread = threading.Thread(target=self._perform_recording)
        self.recording_thread.daemon = True
        self.recording_thread.start()

    def on_hotkey_release(self):
        """Callback bei Hotkey-Loslassen (Stopp Aufnahme)"""
        if not self.is_recording:
            return

        logger.info("Hotkey losgelassen - Stoppe Aufnahme")
        self.is_recording = False

        # Akustisches Feedback
        self.play_beep(config.BEEP_FREQUENCY_STOP)

    def _perform_recording(self):
        """Führt die komplette Aufnahme- und Verarbeitung durch"""
        try:
            # Audio aufnehmen
            audio_path = self.audio_recorder.start_recording()
            if not audio_path:
                logger.error("Audio-Aufnahme fehlgeschlagen")
                return

            logger.info(f"Audio aufgezeichnet: {audio_path}")

            # Transkribieren
            raw_text = self.transcription_service.transcribe(audio_path)
            if not raw_text:
                logger.error("Transkription fehlgeschlagen")
                return

            logger.info(f"Transkribierter Text: {raw_text[:50]}...")

            # Text korrigieren
            corrected_text = self.text_processor.process_text(raw_text)
            if not corrected_text:
                logger.warning("Text-Korrektur fehlgeschlagen, verwende Original")
                corrected_text = raw_text

            logger.info(f"Korrigierter Text: {corrected_text[:50]}...")

            # Text einfügen
            success = self.clipboard_injector.inject_text(corrected_text)
            if success:
                logger.info("Text erfolgreich eingefügt")
            else:
                logger.warning("Text-Einfügung fehlgeschlagen")

        except Exception as e:
            logger.error(f"Fehler während der Verarbeitung: {e}")

        finally:
            # Cleanup
            self.audio_recorder.cleanup()

    def play_beep(self, frequency: int):
        """Spielt einen Beep-Ton"""
        try:
            winsound.Beep(frequency, config.BEEP_DURATION)
        except Exception as e:
            logger.warning(f"Beep konnte nicht abgespielt werden: {e}")

    def show_settings(self):
        """Zeigt Einstellungen (noch nicht implementiert)"""
        logger.info("Einstellungen würden hier geöffnet werden")

    def quit_application(self):
        """Beendet die Anwendung"""
        logger.info("Beende Anwendung...")
        self.cleanup()
        if self.tray_icon:
            self.tray_icon.stop()
        sys.exit(0)

    def cleanup(self):
        """Räumt auf"""
        logger.info("Führe Cleanup durch...")
        if self.audio_recorder:
            self.audio_recorder.cleanup()
        if self.hotkey_listener:
            self.hotkey_listener.cleanup()

    def run(self):
        """Startet die Anwendung"""
        logger.info(f"Starte {config.APP_NAME} v{config.APP_VERSION}")

        # Komponenten initialisieren
        if not self.initialize_components():
            logger.error("Initialisierung fehlgeschlagen")
            return

        # Tray Icon erstellen
        if not self.create_tray_icon():
            logger.error("Tray Icon konnte nicht erstellt werden")
            return

        # Tray Icon starten
        logger.info("Anwendung läuft - Tray Icon verfügbar")
        self.tray_icon.run()

def main():
    """Haupteinstiegspunkt"""
    try:
        app = VoiceTranscriberApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Anwendung durch Benutzer beendet")
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()