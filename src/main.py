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
    from .exceptions import (
        AudioRecordingError,
        AudioCompressionError,
        TranscriptionError,
        TextProcessingError,
        ClipboardError,
        NetworkError,
        APIError,
        RETRYABLE_EXCEPTIONS,
        CRITICAL_EXCEPTIONS
    )
    from .hotkey_listener import HotkeyListener
    from .mouse_integration import MouseWheelIntegration
    from .notification import notification_service
    from .settings_gui import SettingsGUI
    from .text_processor import TextProcessor
    from .transcription import TranscriptionService
except ImportError:
    # Fallback für direkte Ausführung oder PyInstaller
    from audio_recorder import AudioRecorder
    from clipboard_injector import ClipboardInjector
    from config import config
    from exceptions import (
        AudioRecordingError,
        AudioCompressionError,
        TranscriptionError,
        TextProcessingError,
        ClipboardError,
        NetworkError,
        APIError,
        RETRYABLE_EXCEPTIONS,
        CRITICAL_EXCEPTIONS
    )
    from hotkey_listener import HotkeyListener
    from mouse_integration import MouseWheelIntegration
    from notification import notification_service
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
        self.recording_stop_event = threading.Event()  # Event für Thread-Koordination
        self.last_recording_start_time = 0.0  # Verhindert doppelte Aufnahmen

        # Debug-Datei für Transkriptionsergebnisse
        self.debug_file_path = None

        # Singleton-Instanz des TranscriptionService
        self._transcription_service_instance = None

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
        time_since_last = current_time - self.last_recording_start_time
        if time_since_last < 0.5:  # Mindestens 0.5s zwischen Aufnahmen
            logger.debug(f"Aufnahme zu schnell: {time_since_last:.2f}s seit letzter Aufnahme - ignoriere")
            return

        logger.info("Hotkey gedrückt - Starte Aufnahme")
        self.is_recording = True
        self.recording_stop_event.clear()  # Event zurücksetzen
        self.last_recording_start_time = current_time

        # Akustisches Feedback
        self.play_beep(config.BEEP_FREQUENCY_START)

        # Starte Aufnahme in separatem Thread
        self.recording_thread = threading.Thread(target=self._perform_recording)
        self.recording_thread.daemon = True
        self.recording_thread.start()

    def on_hotkey_release(self):
        """Callback bei Hotkey-Loslassen (Stopp Aufnahme)"""
        # Wir setzen nur das Event, der Thread kümmert sich um den Rest
        if not self.is_recording:
             logger.debug("Ignoriere Release: Keine Aufnahme aktiv")
             return
             
        logger.info("Hotkey losgelassen - Signalisiere Stop")
        self.recording_stop_event.set()

        # Akustisches Feedback (kurz)
        self.play_beep(config.BEEP_FREQUENCY_STOP)

    def _perform_recording(self):
        """Führt die komplette Aufnahme- und Verarbeitung durch"""
        final_wav_path = None
        
        try:
            # 1. Aufnahme starten
            if not self.audio_recorder.start_recording():
                raise AudioRecordingError("Konnte Aufnahme nicht starten")

            # 2. Warten bis Hotkey losgelassen wird (oder Timeout)
            # wait gibt True zurück wenn Event gesetzt wurde, False bei Timeout
            event_is_set = self.recording_stop_event.wait(timeout=config.MAX_RECORDING_DURATION)
            
            if not event_is_set:
                 logger.info("Maximale Aufnahmedauer erreicht")
                 self.play_beep(config.BEEP_FREQUENCY_STOP)

            # 3. Aufnahme stoppen
            final_wav_path = self.audio_recorder.stop_recording()
            
            # Reset Status so früh wie möglich, damit neue Aufnahmen möglich sind
            self.is_recording = False
            
            if not final_wav_path or not os.path.exists(final_wav_path):
                 raise AudioRecordingError("Keine Audio-Datei erzeugt")

            # 4. Validierung der Dauer
            duration = self.audio_recorder.last_recording_duration
            if duration < 0.3: # Etwas toleranter sein
                logger.info(f"Aufnahme zu kurz ({duration:.2f}s) - ignoriere")
                return

            # 5. Daten laden / Komprimieren
            compressed_data = None
            try:
                # Prüfe ob pydub verfügbar
                try:
                    from .audio_recorder import PYDUB_AVAILABLE
                except ImportError:
                    from audio_recorder import PYDUB_AVAILABLE

                if PYDUB_AVAILABLE and config.AUDIO_COMPRESSION_ENABLED:
                    logger.info("Komprimiere Audio...")
                    compressed_data = self.audio_recorder.compress_audio(final_wav_path)
                    
                    if not compressed_data:
                        logger.warning("Komprimierung lieferte leere Daten - Fallback auf WAV")
                        compressed_data = None
                
                # Fallback: WAV lesen wenn keine Komprimierung oder fehlgeschlagen
                if compressed_data is None:
                    with open(final_wav_path, 'rb') as f:
                        compressed_data = f.read()

            except Exception as e:
                logger.error(f"Fehler bei Audio-Verarbeitung: {e}")
                # Versuch WAV direkt zu lesen als letzter Rettungsanker
                try:
                    with open(final_wav_path, 'rb') as f:
                        compressed_data = f.read()
                except:
                    raise AudioRecordingError("Konnte Audio-Datei nicht lesen")

            # 6. Transkription
            if not self._transcription_service_instance:
                raise TranscriptionError("TranscriptionService nicht bereit")

            logger.info(f"Sende Audio zur Transkription ({len(compressed_data)} bytes)...")
            
            # Bestimme Dateinamen für API (wichtig für Whisper Verarbeitungshinweise)
            filename = "audio.mp3" if (PYDUB_AVAILABLE and config.AUDIO_COMPRESSION_ENABLED) else "audio.wav"
            
            raw_text = self._transcription_service_instance.transcribe_audio_data(
                compressed_data, filename
            )

            if not raw_text:
                logger.info("Kein Text erkannt")
                return

            logger.info(f"Erkannt: {raw_text[:50]}...")
            
            # 7. Text verarbeiten & Einfügen
            self._process_and_inject_text(raw_text)

        except AudioRecordingError as e:
            logger.error(f"Aufnahme-Fehler: {e}")
            notification_service.notify_warning(str(e), title="Aufnahme")
        except TranscriptionError as e:
            logger.error(f"Transkriptions-Fehler: {e}")
            notification_service.notify_error(str(e), title="Transkription")
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {e}", exc_info=True)
            notification_service.notify_error("Systemfehler aufgetreten", title="Fehler")
        finally:
            # Aufräumen
            self.is_recording = False
            self.recording_stop_event.clear()
            
            # Temp File löschen? Das macht der AudioRecorder beim nächsten Start oder Cleanup
            
    def _process_and_inject_text(self, raw_text):
        """Hilfsmethode für Textverarbeitung und Injection"""
        try:
            # Text korrigieren
            corrected_text = raw_text
            try:
                processed = self.text_processor.process_text(raw_text)
                if processed:
                    corrected_text = processed
            except Exception as e:
                logger.warning(f"Text-Korrektur fehlgeschlagen: {e}")

            self._write_debug_entry(f"Transkript: {corrected_text}")

            # Text einfügen
            success = self.clipboard_injector.inject_text(corrected_text)
            if success:
                logger.info("Text eingefügt")
                notification_service.notify_success("Eingefügt", title="Info")
            else:
                import pyperclip
                pyperclip.copy(corrected_text)
                notification_service.notify_warning(
                    "Konnte nicht tippen - Text in Zwischenablage", 
                    title="Clipboard"
                )
        except Exception as e:
            logger.error(f"Fehler bei Text-Injection: {e}")

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
        # Kein sys.exit() hier, damit pystray sauber beendet ohne Traceback

    def _init_debug_file(self):
        """Initialisiert die Debug-Datei für Transkriptionsergebnisse"""
        try:
            import os
            from pathlib import Path

            # Erstelle Debug-Datei im AppData-Verzeichnis (konsistent mit Logs)
            from .user_config import user_config
            user_dir = user_config.get_appdata_dir()
            user_dir.mkdir(parents=True, exist_ok=True)
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