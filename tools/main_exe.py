"""
Voice Transcriber - Hauptmodul (Orchestrator)
Koordiniert alle Komponenten der Anwendung.
"""

import logging
import sys
import threading
from typing import Optional

from PIL import Image

# Plattform-abhängige Imports
try:
    import winsound
    WINDOWS_PLATFORM = True
except ImportError:
    WINDOWS_PLATFORM = False

try:
    import pystray
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

# Absolute Imports für PyInstaller EXE
import sys
from pathlib import Path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

# Versuche Imports (fehlschlagen in Test-Umgebung)
try:
    from audio_recorder import AudioRecorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False

try:
    from clipboard_injector import ClipboardInjector
    CLIPBOARD_INJECTOR_AVAILABLE = True
except ImportError:
    CLIPBOARD_INJECTOR_AVAILABLE = False

try:
    from config import config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from hotkey_listener import HotkeyListener
    HOTKEY_LISTENER_AVAILABLE = True
except ImportError:
    HOTKEY_LISTENER_AVAILABLE = False

try:
    from settings_gui import SettingsGUI
    SETTINGS_GUI_AVAILABLE = True
except ImportError:
    SETTINGS_GUI_AVAILABLE = False

try:
    from text_processor import TextProcessor
    TEXT_PROCESSOR_AVAILABLE = True
except ImportError:
    TEXT_PROCESSOR_AVAILABLE = False

try:
    from transcription import TranscriptionService
    TRANSCRIPTION_AVAILABLE = True
except ImportError:
    TRANSCRIPTION_AVAILABLE = False

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

            # Komponenten erstellen (nur wenn verfügbar)
            if HOTKEY_LISTENER_AVAILABLE:
                self.hotkey_listener = HotkeyListener()
            else:
                logger.warning("HotkeyListener nicht verfügbar")

            if AUDIO_RECORDER_AVAILABLE:
                self.audio_recorder = AudioRecorder()
            else:
                logger.warning("AudioRecorder nicht verfügbar")

            if TRANSCRIPTION_AVAILABLE:
                self.transcription_service = TranscriptionService()
            else:
                logger.warning("TranscriptionService nicht verfügbar")

            if TEXT_PROCESSOR_AVAILABLE:
                self.text_processor = TextProcessor()
            else:
                logger.warning("TextProcessor nicht verfügbar")

            if CLIPBOARD_INJECTOR_AVAILABLE:
                self.clipboard_injector = ClipboardInjector()
            else:
                logger.warning("ClipboardInjector nicht verfügbar")

            # Hotkey Callbacks registrieren (nur wenn verfügbar)
            if KEYBOARD_AVAILABLE and HOTKEY_LISTENER_AVAILABLE:
                self.hotkey_listener.register_callbacks(
                    on_press=self.on_hotkey_press,
                    on_release=self.on_hotkey_release
                )
            else:
                logger.warning("Keyboard-Unterstützung nicht verfügbar - Hotkeys deaktiviert")

            logger.info("Alle verfügbaren Komponenten erfolgreich initialisiert")
            return True

        except Exception as e:
            logger.error(f"Fehler bei der Initialisierung: {e}")
            return False

    def create_tray_icon(self):
        """Erstellt das System Tray Icon"""
        try:
            if not PYSTRAY_AVAILABLE:
                logger.warning("Pystray nicht verfügbar - simuliere Tray Icon")
                print("🎤 Voice Transcriber v1.5.1 - SIMULIERTES TRAY ICON")
                print("📋 Verfügbare Befehle:")
                print("  s - Einstellungen öffnen")
                print("  q - Beenden")
                print("  h - Hilfe")
                self.tray_icon = "simulated"  # Dummy
                return True

            # Lade Icon (fallback auf generisches Icon)
            icon_path = "../assets/icon.ico"  # Relativer Pfad von tools/
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
            # Prüfe Komprimierungs-Status
            from audio_recorder import PYDUB_AVAILABLE
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
                raw_text = self.transcription_service.transcribe_audio_data(audio_data, "audio.mp3")  # type: ignore
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

                logger.info(f"Transkribierter Text (WAV): {raw_text[:50]}...")

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
            if WINDOWS_PLATFORM:
                winsound.Beep(frequency, config.BEEP_DURATION)
            else:
                # Linux/Mac: Verwende print als Feedback
                print(f"🔊 BEEP: {frequency}Hz für {config.BEEP_DURATION}ms")
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

    def _run_simulated_tray(self):
        """Führt simuliertes Tray aus (für Linux/Mac)"""
        import time
        print("\n🎤 SIMULIERTES TRAY ICON AKTIV")
        print("Drücken Sie eine Taste für Befehle...")

        while True:
            try:
                command = input("Befehl> ").strip().lower()
                if command == 'q':
                    self.quit_application()
                    break
                elif command == 's':
                    self.show_settings()
                elif command == 'h':
                    print("Befehle: s=Einstellungen, q=Beenden, h=Hilfe")
                else:
                    print("Unbekannter Befehl. 'h' für Hilfe.")
            except KeyboardInterrupt:
                self.quit_application()
                break
            except EOFError:
                break

    def quit_application(self, icon=None, item=None):
        """Beendet die Anwendung"""
        logger.info("Beende Anwendung...")
        self.cleanup()
        if self.tray_icon and self.tray_icon != "simulated":
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
        if self.tray_icon == "simulated":
            # Simuliertes Tray - warte auf Eingabe
            self._run_simulated_tray()
        else:
            self.tray_icon.run()  # type: ignore

def main():
    """Haupteinstiegspunkt"""
    try:
        print("🎤 Voice Transcriber v1.5.1 - Test-Modus")
        print("=" * 50)

        # Prüfe Verfügbarkeit
        print(f"📦 Pystray verfügbar: {PYSTRAY_AVAILABLE}")
        print(f"⌨️  Keyboard verfügbar: {KEYBOARD_AVAILABLE}")
        print(f"🔊 Windows Sound: {WINDOWS_PLATFORM}")
        print(f"📁 Assets-Pfad: {Path('../assets/icon.ico').resolve()}")

        # Erstelle App-Instanz
        app = VoiceTranscriberApp()

        # Teste Komponenten-Initialisierung
        print("\n🔧 Teste Komponenten-Initialisierung...")
        success = app.initialize_components()
        print(f"✅ Initialisierung: {'Erfolgreich' if success else 'Fehlgeschlagen'}")

        # Teste Tray Icon
        print("\n🎨 Teste Tray Icon...")
        tray_success = app.create_tray_icon()
        print(f"✅ Tray Icon: {'Erfolgreich' if tray_success else 'Fehlgeschlagen'}")

        if tray_success and app.tray_icon == "simulated":
            print("\n🚀 Starte simuliertes Tray...")
            app._run_simulated_tray()
        else:
            print("\n✅ Alle Tests erfolgreich - App bereit für Windows!")

    except KeyboardInterrupt:
        logger.info("Test durch Benutzer beendet")
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}")
        print(f"❌ Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()