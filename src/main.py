"""
Voice Transcriber - Hauptmodul (Orchestrator)
Koordiniert alle Komponenten der Anwendung.
"""

import logging
import os
import sys
import threading
import time
import warnings
import winsound
from pathlib import Path
from typing import Optional

import keyboard
import pystray
from PIL import Image

try:
    # Versuche relative Imports (für python -m src)
    from .audio_recorder import AudioRecorder
    from .clipboard_injector import ClipboardInjector
    from .config import config
    from .hotkey_listener import HotkeyListener
    from .mouse_integration import MouseWheelIntegration
    from .settings_gui import SettingsGUI
    from .text_processor import TextProcessor
    from .transcription import TranscriptionService
except ImportError:
    # Fallback für direkte Ausführung oder PyInstaller
    from audio_recorder import AudioRecorder
    from clipboard_injector import ClipboardInjector
    from config import config
    from hotkey_listener import HotkeyListener
    from mouse_integration import MouseWheelIntegration
    from settings_gui import SettingsGUI
    from text_processor import TextProcessor
    from transcription import TranscriptionService

logger = logging.getLogger(__name__)

def check_single_instance() -> bool:
    """Prüft, ob bereits eine Instanz der Anwendung läuft"""
    try:
        # Verwende AppData-Verzeichnis für Lock-Datei
        if getattr(sys, 'frozen', False):
            # Wir sind in einer EXE
            appdata = Path(os.environ.get('APPDATA', '')) / 'VoiceTranscriber'
        else:
            # Entwicklung: Verwende temp-Verzeichnis
            appdata = Path.home() / '.voice_transcriber'

        appdata.mkdir(exist_ok=True)
        lock_file = appdata / 'app.lock'

        # Prüfe ob Lock-Datei existiert
        if lock_file.exists():
            logger.warning("Eine Instanz der Anwendung läuft bereits")
            return False

        # Erstelle Lock-Datei
        lock_file.write_text(str(os.getpid()))
        logger.info(f"Lock-Datei erstellt: {lock_file}")

        # Registriere Cleanup-Funktion
        import atexit
        atexit.register(lambda: lock_file.unlink(missing_ok=True))

        return True

    except Exception as e:
        logger.warning(f"Single-Instance-Überprüfung fehlgeschlagen: {e}")
        # Bei Fehler trotzdem starten (fail-safe)
        return True

class VoiceTranscriberApp:
    """Hauptklasse der Voice Transcriber Anwendung"""

    def __init__(self):
        self.tray_icon = None
        self.hotkey_listener = None
        self.mouse_integration = None
        self.audio_recorder = None
        self.transcription_service = None
        self.text_processor = None
        self.clipboard_injector = None

        self.is_recording = False
        self.recording_thread = None
        self.last_recording_start_time = 0.0  # Verhindert doppelte Aufnahmen

        # Debug-Datei für Transkriptionsergebnisse
        self.debug_file_path = None

        # Singleton-Instanz des TranscriptionService
        self._transcription_service_instance = None
        self.last_recording_start_time = 0.0  # Verhindert doppelte Aufnahmen

    def initialize_components(self):
        """Initialisiert alle Anwendungskomponenten"""
        try:
            logger.info("Initialisiere Anwendungskomponenten...")

            # Komponenten erstellen
            self.hotkey_listener = HotkeyListener()
            self.mouse_integration = MouseWheelIntegration()
            self.audio_recorder = AudioRecorder()
            # TranscriptionService als Singleton initialisieren
            self._transcription_service_instance = TranscriptionService()
            logger.info("TranscriptionService Singleton initialisiert")
            self.text_processor = TextProcessor()
            self.clipboard_injector = ClipboardInjector()

            # Debug-Datei initialisieren
            self._init_debug_file()

            # Hotkey Callbacks registrieren (mit Config für benutzerspezifische Hotkeys)
            self.hotkey_listener.register_callbacks(
                on_press=self.on_hotkey_press,
                on_release=self.on_hotkey_release,
                config=config
            )

            # Mouse Wheel Integration starten falls aktiviert
            if config.is_mouse_wheel_enabled():
                logger.info("Mittleres Mausrad ist aktiviert - starte AHK-Integration")
                if not self.mouse_integration.start():
                    logger.warning("AHK-Integration konnte nicht gestartet werden")
                else:
                    logger.info("AHK-Integration erfolgreich gestartet")

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
            logger.debug("Aufnahme läuft bereits - ignoriere Hotkey-Press")
            return

        # Verhindere doppelte Aufnahmen durch zu schnelle Hotkey-Presses
        current_time = time.time()
        if current_time - self.last_recording_start_time < 0.5:  # Mindestens 0.5s zwischen Aufnahmen
            logger.debug(".2f")
            return

        logger.info("Hotkey gedrückt - Starte Aufnahme")
        self.is_recording = True
        self.last_recording_start_time = current_time

        # Akustisches Feedback
        self.play_beep(config.BEEP_FREQUENCY_START)

        # Starte Aufnahme in separatem Thread
        self.recording_thread = threading.Thread(target=self._perform_recording)
        self.recording_thread.daemon = True
        self.recording_thread.start()

    def on_hotkey_release(self):
        """Callback bei Hotkey-Loslassen (Stopp Aufnahme)"""
        if not self.is_recording:
            logger.debug("Keine Aufnahme läuft - ignoriere Hotkey-Release")
            return

        logger.info("Hotkey losgelassen - Stoppe Aufnahme")
        self.is_recording = False

        # Akustisches Feedback
        self.play_beep(config.BEEP_FREQUENCY_STOP)

    def _perform_recording(self):
        """Führt die komplette Aufnahme- und Verarbeitung durch"""
        try:
            # Prüfe Komprimierungs-Status
            from .audio_recorder import PYDUB_AVAILABLE
            if PYDUB_AVAILABLE and config.AUDIO_COMPRESSION_ENABLED:
                logger.info("Audio-Komprimierung aktiviert - verwende MP3")
                use_compression = True
            else:
                logger.info("Audio-Komprimierung deaktiviert - verwende WAV")
                use_compression = False

            if use_compression:
                # Verwende neue Komprimierungs-Methode
                logger.info("Starte Aufnahme mit Komprimierung...")

                # Audio aufnehmen und komprimieren
                audio_data = self.audio_recorder.record_and_compress()  # type: ignore
                if not audio_data:
                    logger.error("Audio-Aufnahme + Komprimierung fehlgeschlagen")
                    return

                data_size = len(audio_data)
                logger.info(f"Audio komprimiert: {data_size} bytes ({data_size/1024:.1f} KB)")

                # Transkribieren mit komprimierten Daten
                if self._transcription_service_instance:
                    raw_text = self._transcription_service_instance.transcribe_audio_data(audio_data, "audio.mp3")
                else:
                    logger.error("TranscriptionService nicht verfügbar")
                    return
                if not raw_text:
                    logger.error("Transkription fehlgeschlagen")
                    return

                logger.info(f"Transkribierter Text (MP3): {raw_text[:50]}...")

            else:
                # Fallback: Klassische WAV-Methode
                logger.info("Verwende klassische WAV-Aufnahme...")

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

                # Kurze zusätzliche Pause um sicherzustellen, dass der Audio-Thread beendet ist
                time.sleep(0.05)

                # Stoppe Aufnahme und erstelle Datei
                final_audio_path = self.audio_recorder.stop_recording()  # type: ignore
                if not final_audio_path:
                    logger.error("Audio-Stopp fehlgeschlagen")
                    return

                logger.info(f"Audio-Datei erstellt: {final_audio_path}")

                # Prüfe Mindestdauer (0.5 Sekunden für zuverlässige Transkription)
                audio_duration = self.audio_recorder.last_recording_duration if self.audio_recorder else 0.0
                if audio_duration < 0.5:
                    logger.warning(".2f")
                    return

                logger.info(".2f")

                # Transkribieren
                if self._transcription_service_instance:
                    raw_text = self._transcription_service_instance.transcribe(final_audio_path)
                    if not raw_text:
                        logger.error("Transkription fehlgeschlagen - kein Text zurückgegeben")
                        return
                else:
                    logger.error("TranscriptionService nicht verfügbar")
                    return

                logger.info(f"Transkribierter Text (WAV): {raw_text[:50]}...")

            # Text korrigieren
            corrected_text = self.text_processor.process_text(raw_text)  # type: ignore
            if not corrected_text:
                logger.warning("Text-Korrektur fehlgeschlagen, verwende Original")
                corrected_text = raw_text

            logger.info(f"Korrigierter Text: {corrected_text[:50]}...")

            # Debug-Eintrag schreiben
            self._write_debug_entry(f"Transkript: {corrected_text}")

            # Text einfügen
            success = self.clipboard_injector.inject_text(corrected_text)  # type: ignore
            if success:
                logger.info("Text erfolgreich eingefügt")
                self._write_debug_entry("Status: Erfolgreich eingefügt")
            else:
                logger.warning("Text-Einfügung fehlgeschlagen")
                self._write_debug_entry("Status: Einfügung fehlgeschlagen")

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

    def _init_debug_file(self):
        """Initialisiert die Debug-Datei für Transkriptionsergebnisse"""
        try:
            import os
            from pathlib import Path

            # Erstelle Debug-Datei im User-Verzeichnis
            user_dir = Path.home()
            self.debug_file_path = user_dir / "voice_transcriber_debug.txt"

            # Erstelle/überschreibe Datei mit Header
            with open(self.debug_file_path, 'w', encoding='utf-8-sig') as f:
                f.write("Voice Transcriber Debug Log\n")
                f.write("=" * 50 + "\n")
                f.write(f"Gestartet: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            logger.info(f"Debug-Datei initialisiert: {self.debug_file_path}")

        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der Debug-Datei: {e}")

    def _write_debug_entry(self, text: str):
        """Schreibt einen Eintrag in die Debug-Datei"""
        if self.debug_file_path:
            try:
                timestamp = time.strftime('%H:%M:%S')
                with open(self.debug_file_path, 'a', encoding='utf-8-sig') as f:
                    f.write(f"[{timestamp}] {text}\n")
            except Exception as e:
                logger.error(f"Fehler beim Schreiben in Debug-Datei: {e}")

    def cleanup(self):
        """Räumt auf"""
        logger.info("Führe Cleanup durch...")
        if self.audio_recorder:
            self.audio_recorder.cleanup()
        if self.hotkey_listener:
            self.hotkey_listener.cleanup()
        if self.mouse_integration:
            self.mouse_integration.stop()

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
    # Unterdrücke bekannte Warnungen
    warnings.filterwarnings("ignore", message=".*pkg_resources.*", category=UserWarning)

    try:
        # Prüfe Single-Instance (für Testzwecke deaktiviert)
        # if not check_single_instance():
        #     logger.warning("Eine Instanz der Anwendung läuft bereits. Beende.")
        #     sys.exit(0)

        # Single-Instance-Überprüfung für Testzwecke deaktiviert
        # if not check_single_instance():
        #     logger.warning("Eine Instanz der Anwendung läuft bereits. Beende.")
        #     sys.exit(0)
        logger.info("Single-Instance-Überprüfung übersprungen (Test-Modus)")

        app = VoiceTranscriberApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Anwendung durch Benutzer beendet")
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()