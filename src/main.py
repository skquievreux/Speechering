"""
Voice Transcriber - Hauptmodul (Orchestrator)
Koordiniert alle Komponenten der Anwendung.
"""

import logging
import sys
import threading
import winsound
from typing import Optional

import keyboard
import pystray
from PIL import Image

from audio_recorder import AudioRecorder
from clipboard_injector import ClipboardInjector
from config import config
from hotkey_listener import HotkeyListener
from settings_gui import SettingsGUI
from text_processor import TextProcessor
from transcription import TranscriptionService

logger = logging.getLogger(__name__)

class VoiceTranscriberApp:
    """Hauptklasse der Voice Transcriber Anwendung"""

    def __init__(self):
        self.tray_icon = None
        self.hotkey_listener = None
        self.audio_recorder = None
        self.transcription_service = None
        self.text_processor = None
        self.clipboard_injector = None

        self.is_recording = False
        self.recording_thread = None

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
            def on_settings(icon, item):
                self.show_settings()

            def on_quit(icon, item):
                self.quit_application()

            menu = pystray.Menu(
                pystray.MenuItem("Status: Bereit", lambda icon, item: None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Einstellungen", on_settings),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Beenden", on_quit)
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
            audio_path = self.audio_recorder.start_recording()  # type: ignore
            if not audio_path:
                logger.error("Audio-Aufnahme fehlgeschlagen")
                return

            logger.info(f"Audio aufgezeichnet: {audio_path}")

            # Warten bis Hotkey losgelassen wird
            while self.is_recording:
                import time
                time.sleep(0.01)  # Kurze Pause

            # Stoppe Aufnahme und erstelle Datei
            final_audio_path = self.audio_recorder.stop_recording()  # type: ignore
            if not final_audio_path:
                logger.error("Audio-Stopp fehlgeschlagen")
                return

            logger.info(f"Audio-Datei erstellt: {final_audio_path}")

            # Transkribieren
            raw_text = self.transcription_service.transcribe(final_audio_path)  # type: ignore
            if not raw_text:
                logger.error("Transkription fehlgeschlagen")
                return

            logger.info(f"Transkribierter Text: {raw_text[:50]}...")

            # Text korrigieren
            corrected_text = self.text_processor.process_text(raw_text)  # type: ignore
            if not corrected_text:
                logger.warning("Text-Korrektur fehlgeschlagen, verwende Original")
                corrected_text = raw_text

            logger.info(f"Korrigierter Text: {corrected_text[:50]}...")

            # Text einfügen
            success = self.clipboard_injector.inject_text(corrected_text)  # type: ignore
            if success:
                logger.info("Text erfolgreich eingefügt")
            else:
                logger.warning("Text-Einfügung fehlgeschlagen")

        except Exception as e:
            logger.error(f"Fehler während der Verarbeitung: {e}")

        finally:
            # Cleanup wird bereits in stop_recording gemacht
            pass

    def play_beep(self, frequency: int):
        """Spielt einen Beep-Ton"""
        try:
            winsound.Beep(frequency, config.BEEP_DURATION)
        except Exception as e:
            logger.warning(f"Beep konnte nicht abgespielt werden: {e}")

    def show_settings(self, icon=None, item=None):
        """Zeigt Einstellungen"""
        try:
            logger.info("Einstellungs-GUI wird geöffnet")

            # Verwende threading um tkinter in separatem Thread zu starten
            import threading
            settings_thread = threading.Thread(target=self._open_settings_window, daemon=True)
            settings_thread.start()

        except Exception as e:
            logger.error(f"Fehler beim Öffnen der Einstellungen: {e}")

    def _open_settings_window(self):
        """Öffnet das Einstellungsfenster in separatem Thread"""
        try:
            import tkinter as tk

            # Erstelle neues root window für diesen Thread
            root = tk.Tk()
            root.title(f"{config.APP_NAME} - Einstellungen")
            root.geometry("600x500")

            # Icon setzen (falls verfügbar)
            try:
                root.iconbitmap("assets/icon.ico")
            except:
                pass

            # Erstelle SettingsGUI ohne parent (damit sie das root window verwendet)
            settings_gui = SettingsGUI()
            settings_gui.window = root  # Verwende direkt das root window
            settings_gui._create_widgets()
            settings_gui._load_current_settings()

            # Starte tkinter mainloop
            root.mainloop()

        except Exception as e:
            logger.error(f"Fehler im Einstellungs-Thread: {e}")
            # Fallback: Zeige einfache MessageBox
            try:
                import tkinter as tk
                from tkinter import messagebox

                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("Einstellungen",
                    "Einstellungs-GUI konnte nicht geöffnet werden.\n"
                    "Bitte bearbeiten Sie die .env Datei manuell.")
                root.destroy()
            except:
                logger.error("Auch Fallback-MessageBox fehlgeschlagen")

    def quit_application(self, icon=None, item=None):
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
        self.tray_icon.run()  # type: ignore

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