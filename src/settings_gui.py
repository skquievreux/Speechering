"""
Settings GUI - Einstellungsfenster mit tkinter
Zeigt App-Info und ermöglicht Hotkey-Auswahl
"""

import logging
import tkinter as tk
from tkinter import messagebox, ttk

import pyaudio

from src.config import config

logger = logging.getLogger(__name__)

class SettingsGUI:
    """Einstellungs-GUI für Voice Transcriber"""

    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.hotkey_var = tk.StringVar(value="f12")
        self.audio_device_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.show_key_var = tk.BooleanVar(value=False)  # Für API-Key Sichtbarkeit

        # Lade Transkriptions-Einstellungen aus user_config für Konsistenz
        try:
            from src.user_config import user_config
            use_local = user_config.get('transcription.use_local', False)
            model_size = user_config.get('transcription.whisper_model_size', 'small')
        except:
            use_local = getattr(config, 'USE_LOCAL_TRANSCRIPTION', False)
            model_size = getattr(config, 'WHISPER_MODEL_SIZE', 'small')

        self.transcription_mode_var = tk.StringVar(value="local" if use_local else "api")
        self.model_size_var = tk.StringVar(value=model_size)

        # Audio-Geräte laden
        self.audio_devices = self._get_audio_devices()
        self.audio_device_indices = self._get_audio_device_indices()

    def show(self):
        """Zeigt das Einstellungsfenster"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title(f"Voice Transcriber v{config.APP_VERSION} - Einstellungen")
        self.window.geometry("500x600")
        self.window.resizable(False, False)

        self._create_widgets()
        self._load_current_settings()

        # Modal machen wenn parent existiert
        if self.parent:
            self.window.transient(self.parent)
            self.window.grab_set()

        self.window.focus_set()

    def _create_widgets(self):
        """Erstellt alle GUI-Elemente"""
        # Debug-Datei Button oben hinzufügen
        debug_frame = ttk.Frame(self.window)
        debug_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(
            debug_frame,
            text="📄 Debug-Datei öffnen",
            command=self._open_debug_file
        ).pack(side='left', padx=5)

        ttk.Button(
            debug_frame,
            text="🗑️ Debug-Datei löschen",
            command=self._clear_debug_file
        ).pack(side='left', padx=5)

        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Allgemein
        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="Allgemein")

        # Tab 2: Hotkeys
        hotkey_tab = ttk.Frame(notebook)
        notebook.add(hotkey_tab, text="Hotkeys")

        # Tab 3: Audio
        audio_tab = ttk.Frame(notebook)
        notebook.add(audio_tab, text="Audio")

        # Tab 4: Transkription
        transcription_tab = ttk.Frame(notebook)
        notebook.add(transcription_tab, text="Transkription")

        # Tab 5: API-Schlüssel
        api_tab = ttk.Frame(notebook)
        notebook.add(api_tab, text="API-Schlüssel")

        # Tab 6: Über
        about_tab = ttk.Frame(notebook)
        notebook.add(about_tab, text="Über")
        self._create_about_tab(about_tab)

        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(button_frame, text="Speichern", command=self._save_settings).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Abbrechen", command=self._close_window).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Standard", command=self._reset_defaults).pack(side='left', padx=5)

    def _create_general_tab(self, parent):
        """Erstellt den Allgemein-Tab"""
        # Fett gedruckte Überschrift
        ttk.Label(parent, text="ALLGEMEIN", font=("TkDefaultFont", 10, "bold")).pack(anchor='w', pady=(0, 10))

        # App Status
        status_frame = ttk.LabelFrame(parent, text="App Status", padding=10)
        status_frame.pack(fill='x', pady=5)

        ttk.Label(status_frame, text=f"Version: {config.APP_VERSION}").pack(anchor='w')
        ttk.Label(status_frame, text=f"Konfiguration: {'OK' if config.validate() else 'FEHLER'}").pack(anchor='w')

        api_status = "✅ API-Key gesetzt" if config.OPENAI_API_KEY else "❌ API-Key fehlt"
        ttk.Label(status_frame, text=f"OpenAI API: {api_status}").pack(anchor='w')

        # Aufnahme-Einstellungen
        recording_frame = ttk.LabelFrame(parent, text="Aufnahme-Einstellungen", padding=10)
        recording_frame.pack(fill='x', pady=5)

        ttk.Label(recording_frame, text=f"Max. Dauer: {config.MAX_RECORDING_DURATION}s").pack(anchor='w')
        ttk.Label(recording_frame, text=f"Sample Rate: {config.SAMPLE_RATE}Hz").pack(anchor='w')
        ttk.Label(recording_frame, text=f"Kanäle: {config.CHANNELS}").pack(anchor='w')

    def _create_hotkey_tab(self, parent):
        """Erstellt den Hotkey-Tab"""
        # Fett gedruckte Überschrift
        ttk.Label(parent, text="HOTKEYS", font=("TkDefaultFont", 10, "bold")).pack(anchor='w', pady=(0, 10))

        hotkey_frame = ttk.LabelFrame(parent, text="Push-to-Talk Hotkey", padding=10)
        hotkey_frame.pack(fill='x', pady=5)

        ttk.Label(hotkey_frame, text="Wähle deine bevorzugte Tastenkombination:").pack(anchor='w', pady=5)

        # Hotkey Optionen (nur funktionierende)
        hotkey_options = [
            ("F12 (empfohlen)", "f12"),
            ("F11", "f11"),
            ("F10", "f10"),
            ("Strg + Umschalt + S", "ctrl+shift+s"),
            ("Alt + Umschalt + S", "alt+shift+s"),
            ("Strg + Alt + S", "ctrl+alt+s"),
            ("Strg + Shift + Space", "ctrl+shift+space"),
            ("Alt + Shift + Space", "alt+shift+space"),
        ]

        for text, value in hotkey_options:
            ttk.Radiobutton(
                hotkey_frame,
                text=text,
                variable=self.hotkey_var,
                value=value
            ).pack(anchor='w', pady=2)

        # Info
        info_frame = ttk.Frame(hotkey_frame)
        info_frame.pack(fill='x', pady=10)

        ttk.Label(
            info_frame,
            text="💡 Empfehlung: F12 - funktioniert immer und ist einfach zu erreichen",
            foreground="blue"
        ).pack(anchor='w')

        ttk.Label(
            info_frame,
            text="🔄 Änderungen werden nach Neustart wirksam",
            foreground="orange"
        ).pack(anchor='w')

        ttk.Label(
            info_frame,
            text="⚠️ Windows-Taste-Kombinationen werden vom OS blockiert",
            foreground="red"
        ).pack(anchor='w')

    def _create_audio_tab(self, parent):
        """Erstellt den Audio-Tab"""
        # Fett gedruckte Überschrift
        ttk.Label(parent, text="AUDIO", font=("TkDefaultFont", 10, "bold")).pack(anchor='w', pady=(0, 10))

        audio_frame = ttk.LabelFrame(parent, text="Audio-Geräte", padding=10)
        audio_frame.pack(fill='x', pady=5)

        # Aktuelles Gerät anzeigen (wird später in _load_current_settings gesetzt)
        self.current_device_label = ttk.Label(audio_frame, text="Aktives Mikrofon: Wird geladen...")
        self.current_device_label.pack(anchor='w', pady=5)

        # Geräte-Auswahl
        ttk.Label(audio_frame, text="Mikrofon auswählen:").pack(anchor='w', pady=5)

        device_frame = ttk.Frame(audio_frame)
        device_frame.pack(fill='x', pady=5)

        # Dropdown für Geräteauswahl
        device_options = ["Standard (automatisch)"] + self.audio_devices
        self.audio_device_var.set("Standard (automatisch)")  # Default, wird in _load_current_settings überschrieben

        device_combo = ttk.Combobox(device_frame, textvariable=self.audio_device_var, values=device_options, state="readonly")
        device_combo.pack(fill='x')

        # Info
        ttk.Label(audio_frame, text="Verfügbare Mikrofone:").pack(anchor='w', pady=5)

        device_list_frame = ttk.Frame(audio_frame)
        device_list_frame.pack(fill='x')

        if self.audio_devices:
            current_device = self.audio_device_var.get()
            for device in self.audio_devices[:8]:  # Max 8 anzeigen
                status = "✅" if device == current_device else "○"
                ttk.Label(device_list_frame, text=f"{status} {device}").pack(anchor='w')
        else:
            ttk.Label(device_list_frame, text="❌ Keine Mikrofone gefunden", foreground="red").pack(anchor='w')

        # Test Button
        ttk.Button(audio_frame, text="Mikrofon testen", command=self._test_microphone).pack(pady=10)

    def _create_transcription_tab(self, parent):
        """Erstellt den Transkription-Tab"""
        # Fett gedruckte Überschrift
        ttk.Label(parent, text="TRANSKRIPTION", font=("TkDefaultFont", 10, "bold")).pack(anchor='w', pady=(0, 10))

        transcription_frame = ttk.LabelFrame(parent, text="Transkriptions-Einstellungen", padding=10)
        transcription_frame.pack(fill='x', pady=5)

        # Transkriptionsmodus
        mode_frame = ttk.Frame(transcription_frame)
        mode_frame.pack(fill='x', pady=5)

        ttk.Label(mode_frame, text="Transkriptionsmodus:").pack(anchor='w')

        # Radio-Buttons für Modus-Auswahl (verwendet bereits oben definierte Variable)

        ttk.Radiobutton(
            mode_frame,
            text="OpenAI API (kostenpflichtig, immer verfügbar)",
            variable=self.transcription_mode_var,
            value="api"
        ).pack(anchor='w', pady=2)

        ttk.Radiobutton(
            mode_frame,
            text="Lokales Modell (kostenlos, offline-fähig)",
            variable=self.transcription_mode_var,
            value="local"
        ).pack(anchor='w', pady=2)

        # Modellgröße (nur bei lokalem Modus)
        model_frame = ttk.LabelFrame(transcription_frame, text="Lokales Modell", padding=10)
        model_frame.pack(fill='x', pady=10)

        ttk.Label(model_frame, text="Whisper-Modellgröße:").pack(anchor='w', pady=5)

        # model_size_var ist bereits oben definiert

        model_options = [
            ("Tiny (ca. 39 MB, schnell aber weniger genau)", "tiny"),
            ("Base (ca. 74 MB, ausgewogen)", "base"),
            ("Small (ca. 244 MB, empfohlen)", "small"),
            ("Medium (ca. 769 MB, genauer)", "medium"),
            ("Large (ca. 1550 MB, sehr genau)", "large")
        ]

        for text, value in model_options:
            ttk.Radiobutton(
                model_frame,
                text=text,
                variable=self.model_size_var,
                value=value
            ).pack(anchor='w', pady=1)

        # Info-Text
        info_frame = ttk.Frame(transcription_frame)
        info_frame.pack(fill='x', pady=10)

        info_text = """💡 Hinweise:
• Lokale Modelle benötigen beim ersten Start Zeit zum Download
• GPU-Beschleunigung wird automatisch verwendet (falls verfügbar)
• Bei Problemen mit lokalem Modell wechselt die App automatisch zur API"""

        ttk.Label(info_frame, text=info_text, foreground="blue", justify="left").pack(anchor='w')

    def _create_api_tab(self, parent):
        """Erstellt den API-Schlüssel-Tab"""
        # Fett gedruckte Überschrift
        ttk.Label(parent, text="API-SCHLÜSSEL", font=("TkDefaultFont", 10, "bold")).pack(anchor='w', pady=(0, 10))

        api_frame = ttk.LabelFrame(parent, text="OpenAI API-Schlüssel", padding=10)
        api_frame.pack(fill='x', pady=5)

        # Aktueller Status
        status_frame = ttk.Frame(api_frame)
        status_frame.pack(fill='x', pady=5)

        has_key = bool(config.OPENAI_API_KEY and config.OPENAI_API_KEY != 'sk-your-openai-api-key-here')
        status_text = "✅ API-Key gesetzt und verschlüsselt" if has_key else "❌ API-Key nicht gesetzt"
        status_color = "green" if has_key else "red"

        ttk.Label(status_frame, text=status_text, foreground=status_color).pack(anchor='w')

        # Eingabefeld für API-Key
        input_frame = ttk.Frame(api_frame)
        input_frame.pack(fill='x', pady=10)

        ttk.Label(input_frame, text="OpenAI API-Key:").pack(anchor='w', pady=5)

        # Password-Entry für Sicherheit
        self.api_key_entry = ttk.Entry(input_frame, textvariable=self.api_key_var, show="*")
        self.api_key_entry.pack(fill='x', pady=5)

        # Checkbox zum Anzeigen/Verstecken
        self.show_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            input_frame,
            text="API-Key anzeigen",
            variable=self.show_key_var,
            command=self._toggle_api_key_visibility
        ).pack(anchor='w', pady=5)

        # Info-Text
        info_frame = ttk.Frame(api_frame)
        info_frame.pack(fill='x', pady=10)

        info_text = """🔐 Sicherheitshinweise:
• Der API-Key wird verschlüsselt in Ihrem AppData-Verzeichnis gespeichert
• Er ist nur auf diesem Computer lesbar
• Bei Problemen mit der Verschlüsselung wird ein sicherer Fallback verwendet

💡 Den API-Key finden Sie unter: https://platform.openai.com/account/api-keys"""

        ttk.Label(info_frame, text=info_text, foreground="blue", justify="left").pack(anchor='w')

    def _toggle_api_key_visibility(self):
        """Schaltet die Sichtbarkeit des API-Keys um"""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")

    def _create_about_tab(self, parent):
        """Erstellt den Über-Tab"""
        # Fett gedruckte Überschrift
        ttk.Label(parent, text="ÜBER", font=("TkDefaultFont", 10, "bold")).pack(anchor='w', pady=(0, 10))

        about_frame = ttk.LabelFrame(parent, text="Voice Transcriber", padding=10)
        about_frame.pack(fill='x', pady=5)

        # Logo/Icon Platzhalter
        ttk.Label(about_frame, text="🎤", font=("Arial", 48)).pack(pady=10)

        ttk.Label(about_frame, text="Voice Transcriber", font=("Arial", 16, "bold")).pack(pady=5)
        ttk.Label(about_frame, text=f"Version {config.APP_VERSION}").pack()
        ttk.Label(about_frame, text="Push-to-Talk Sprach-zu-Text Transkription").pack(pady=5)

        ttk.Label(about_frame, text="Technologien:").pack(anchor='w', pady=5)
        ttk.Label(about_frame, text="• OpenAI Whisper + GPT-4").pack(anchor='w')
        ttk.Label(about_frame, text="• Python mit tkinter GUI").pack(anchor='w')
        ttk.Label(about_frame, text="• PyAudio für Audio-Aufnahme").pack(anchor='w')

        ttk.Label(about_frame, text="© 2025 Voice Transcriber Team").pack(pady=10)

    def _get_audio_devices(self):
        """Holt verfügbare Audio-Geräte"""
        try:
            audio = pyaudio.PyAudio()
            devices = []

            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                max_channels = device_info.get('maxInputChannels')
                if max_channels is not None and isinstance(max_channels, (int, float)) and max_channels > 0:  # Input device
                    device_name = device_info.get('name', f'Device {i}')
                    # Bereinige den Gerätenamen von Sonderzeichen und Codierungsproblemen
                    try:
                        # Stelle sicher, dass device_name ein String ist
                        if not isinstance(device_name, str):
                            device_name = str(device_name)

                        # Versuche UTF-8 Decodierung falls nötig
                        if isinstance(device_name, bytes):
                            device_name = device_name.decode('utf-8', errors='replace')

                        # Normalisiere Unicode-Zeichen und entferne problematische Zeichen
                        import unicodedata
                        device_name = unicodedata.normalize('NFKD', device_name).encode('ascii', 'ignore').decode('ascii')

                        # Entferne Null-Bytes und andere Steuerzeichen
                        device_name = ''.join(c for c in device_name if ord(c) >= 32 or c in '\t\n\r')

                        # Entferne überflüssige Leerzeichen
                        device_name = device_name.strip()

                        # Fallback falls der Name leer ist
                        if not device_name:
                            device_name = f"Audio Device {i}"

                    except Exception as encoding_error:
                        logger.warning(f"Fehler bei der Bereinigung des Gerätenamens '{device_name}': {encoding_error}")
                        device_name = f"Audio Device {i}"
                    devices.append(device_name)

            audio.terminate()

            # Entferne Duplikate und sortiere
            unique_devices = list(set(devices))
            unique_devices.sort()
            return unique_devices

        except Exception as e:
            logger.error(f"Fehler beim Laden der Audio-Geräte: {e}")
            return []

    def _get_audio_device_indices(self):
        """Holt verfügbare Audio-Geräte-Indizes"""
        try:
            audio = pyaudio.PyAudio()
            indices = []

            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                max_channels = device_info.get('maxInputChannels')
                if max_channels is not None and isinstance(max_channels, (int, float)) and max_channels > 0:  # Input device
                    indices.append(i)

            audio.terminate()
            return indices

        except Exception as e:
            logger.error(f"Fehler beim Laden der Audio-Geräte-Indizes: {e}")
            return []

    def _test_microphone(self):
        """Testet das Mikrofon"""
        messagebox.showinfo("Mikrofon-Test", "Mikrofon-Test wird implementiert...")

    def _load_current_settings(self):
        """Lädt aktuelle Einstellungen"""
        try:
            from src.user_config import user_config

            # Hotkey laden
            primary_hotkey = user_config.get_hotkey('primary')
            if primary_hotkey:
                self.hotkey_var.set(primary_hotkey)

            # Audio-Gerät laden
            saved_device = user_config.get('audio.device_name', "Standard (automatisch)")
            if saved_device in self.audio_devices or saved_device == "Standard (automatisch)":
                self.audio_device_var.set(saved_device)
                self.current_device_label.config(text=f"Aktives Mikrofon: {saved_device}")
            else:
                self.audio_device_var.set("Standard (automatisch)")
                self.current_device_label.config(text="Aktives Mikrofon: Standard (automatisch)")

            # Transkriptions-Einstellungen laden
            use_local = user_config.get('transcription.use_local', False)
            self.transcription_mode_var.set("local" if use_local else "api")

            model_size = user_config.get('transcription.whisper_model_size', 'small')
            self.model_size_var.set(model_size)

            # API-Key Status (nicht laden, nur Status anzeigen)
            has_key = bool(config.OPENAI_API_KEY and config.OPENAI_API_KEY != 'sk-your-openai-api-key-here')
            if has_key:
                self.api_key_var.set("*** API-Key ist gesetzt ***")

        except Exception as e:
            logger.error(f"Fehler beim Laden der Einstellungen: {e}")

    def _save_settings(self):
        """Speichert die Einstellungen"""
        try:
            from src.user_config import user_config

            # API-Key speichern (verschlüsselt)
            api_key = self.api_key_var.get().strip()
            if api_key:
                if not api_key.startswith('sk-'):
                    messagebox.showerror("Fehler", "Ungültiger API-Key Format. Muss mit 'sk-' beginnen.")
                    return
                user_config.set_encrypted('api.openai_key', api_key)
                logger.info("API-Key erfolgreich verschlüsselt gespeichert")

            # Audio-Gerät speichern
            selected_device = self.audio_device_var.get()
            user_config.set('audio.device_name', selected_device)

            # Transkriptions-Einstellungen
            transcription_mode = self.transcription_mode_var.get()
            use_local = transcription_mode == "local"
            model_size = self.model_size_var.get()

            user_config.set('transcription.use_local', use_local)
            user_config.set('transcription.whisper_model_size', model_size)
            logger.info(f"Transkriptions-Einstellungen gespeichert: use_local={use_local}, model_size={model_size}")

            # Hotkey speichern
            selected_hotkey = self.hotkey_var.get()
            user_config.set_hotkey('primary', selected_hotkey)

            # Speichern
            user_config.save()
            logger.info("Alle Einstellungen erfolgreich gespeichert")

            messagebox.showinfo(
                "Einstellungen gespeichert",
                "✅ Alle Einstellungen wurden erfolgreich gespeichert!\n\n"
                "🔄 Die Änderungen werden beim nächsten Neustart wirksam."
            )
            self._close_window()

        except Exception as e:
            logger.error(f"Fehler beim Speichern der Einstellungen: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    def _reset_defaults(self):
        """Setzt Standardeinstellungen zurück"""
        self.hotkey_var.set("f12")
        messagebox.showinfo("Zurückgesetzt", "Standardeinstellungen wiederhergestellt.")

    def _close_window(self):
        """Schließt das Fenster"""
        if self.window:
            self.window.destroy()

    def _open_debug_file(self):
        """Öffnet die Debug-Datei"""
        try:
            import os
            import subprocess
            from pathlib import Path

            # Versuche verschiedene mögliche Pfade
            possible_paths = [
                Path.home() / "voice_transcriber_debug.txt",  # Home-Verzeichnis
                Path.cwd() / "voice_transcriber_debug.txt",   # Arbeitsverzeichnis
                Path.home() / "AppData" / "Roaming" / "VoiceTranscriber" / "voice_transcriber_debug.txt",  # Windows AppData
                Path.home() / ".config" / "VoiceTranscriber" / "voice_transcriber_debug.txt",  # Linux config
            ]

            debug_file = None
            for path in possible_paths:
                if path.exists():
                    debug_file = path
                    break

            if debug_file and debug_file.exists():
                logger.info(f"Öffne Debug-Datei: {debug_file}")
                # Öffne mit Standard-Editor
                if os.name == 'nt':  # Windows
                    subprocess.run(['notepad.exe', str(debug_file)], check=True)
                else:  # Linux/macOS
                    subprocess.run(['xdg-open', str(debug_file)], check=True)

                messagebox.showinfo("Debug-Datei", f"Debug-Datei geöffnet:\n{debug_file}")
            else:
                # Erstelle eine Beispiel-Datei zur Demonstration
                example_file = Path.home() / "voice_transcriber_debug.txt"
                try:
                    example_content = """Voice Transcriber - Debug-Datei

Diese Datei wird während der Aufnahme erstellt und enthält:
- Aufnahme-Details (Dauer, Format, Größe)
- Transkriptions-Ergebnisse
- Fehler-Logs und Warnungen
- Performance-Messungen

Die Datei wird automatisch erstellt, wenn Sie eine Aufnahme machen.
"""
                    example_file.parent.mkdir(parents=True, exist_ok=True)
                    example_file.write_text(example_content, encoding='utf-8')
                    messagebox.showinfo("Debug-Datei", f"Beispiel-Debug-Datei erstellt:\n{example_file}\n\nMachen Sie eine Aufnahme, um echte Debug-Daten zu sehen.")
                except Exception as create_error:
                    logger.error(f"Fehler beim Erstellen der Beispiel-Datei: {create_error}")
                    messagebox.showinfo("Debug-Datei", "Debug-Datei existiert noch nicht.\nMachen Sie eine Aufnahme, um sie zu erstellen.")

        except Exception as e:
            if "subprocess" in str(type(e)).lower():
                logger.error(f"Fehler beim Öffnen der Debug-Datei mit Editor: {e}")
                messagebox.showerror("Fehler", f"Editor konnte Datei nicht öffnen: {e}")
            else:
                logger.error(f"Fehler beim Öffnen der Debug-Datei: {e}")
                messagebox.showerror("Fehler", f"Debug-Datei konnte nicht geöffnet werden: {e}")

    def _clear_debug_file(self):
        """Löscht die Debug-Datei"""
        try:
            from pathlib import Path
            debug_file = Path.home() / "voice_transcriber_debug.txt"
            if debug_file.exists():
                debug_file.unlink()
                messagebox.showinfo("Debug-Datei", "Debug-Datei wurde gelöscht.")
            else:
                messagebox.showinfo("Debug-Datei", "Debug-Datei existiert nicht.")

        except Exception as e:
            logger.error(f"Fehler beim Löschen der Debug-Datei: {e}")
            messagebox.showerror("Fehler", f"Debug-Datei konnte nicht gelöscht werden: {e}")

    def get_selected_hotkey(self):
        """Gibt den ausgewählten Hotkey zurück"""
        return self.hotkey_var.get()