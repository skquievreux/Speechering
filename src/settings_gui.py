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
        self.transcription_mode_var = tk.StringVar(value="api" if not config.USE_LOCAL_TRANSCRIPTION else "local")
        self.model_size_var = tk.StringVar(value=config.WHISPER_MODEL_SIZE)
        self.api_key_var = tk.StringVar()

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
        self._create_general_tab(general_tab)

        # Tab 2: Hotkeys
        hotkey_tab = ttk.Frame(notebook)
        notebook.add(hotkey_tab, text="Hotkeys")
        self._create_hotkey_tab(hotkey_tab)

        # Tab 3: Audio
        audio_tab = ttk.Frame(notebook)
        notebook.add(audio_tab, text="Audio")
        self._create_audio_tab(audio_tab)

        # Tab 4: Transkription
        transcription_tab = ttk.Frame(notebook)
        notebook.add(transcription_tab, text="Transkription")
        self._create_transcription_tab(transcription_tab)

        # Tab 5: API-Schlüssel
        api_tab = ttk.Frame(notebook)
        notebook.add(api_tab, text="API-Schlüssel")
        self._create_api_tab(api_tab)

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
        audio_frame = ttk.LabelFrame(parent, text="Audio-Geräte", padding=10)
        audio_frame.pack(fill='x', pady=5)

        # Aktuelles Gerät anzeigen
        current_device = "Standard (automatisch)"
        if config.AUDIO_DEVICE_INDEX >= 0 and config.AUDIO_DEVICE_INDEX < len(self.audio_devices):
            current_device = self.audio_devices[config.AUDIO_DEVICE_INDEX]

        ttk.Label(audio_frame, text=f"Aktives Mikrofon: {current_device}").pack(anchor='w', pady=5)

        # Geräte-Auswahl
        ttk.Label(audio_frame, text="Mikrofon auswählen:").pack(anchor='w', pady=5)

        device_frame = ttk.Frame(audio_frame)
        device_frame.pack(fill='x', pady=5)

        # Dropdown für Geräteauswahl
        device_options = ["Standard (automatisch)"] + self.audio_devices
        # Sicherstellen, dass der Index gültig ist
        if config.AUDIO_DEVICE_INDEX >= 0 and config.AUDIO_DEVICE_INDEX < len(self.audio_devices):
            self.audio_device_var.set(device_options[config.AUDIO_DEVICE_INDEX + 1])
        else:
            self.audio_device_var.set(device_options[0])

        device_combo = ttk.Combobox(device_frame, textvariable=self.audio_device_var, values=device_options, state="readonly")
        device_combo.pack(fill='x')

        # Info
        ttk.Label(audio_frame, text="Verfügbare Mikrofone:").pack(anchor='w', pady=5)

        device_list_frame = ttk.Frame(audio_frame)
        device_list_frame.pack(fill='x')

        if self.audio_devices:
            for i, device in enumerate(self.audio_devices[:8]):  # Max 8 anzeigen
                status = "✅" if i == config.AUDIO_DEVICE_INDEX else "○"
                ttk.Label(device_list_frame, text=f"{status} {device}").pack(anchor='w')
        else:
            ttk.Label(device_list_frame, text="❌ Keine Mikrofone gefunden", foreground="red").pack(anchor='w')

        # Test Button
        ttk.Button(audio_frame, text="Mikrofon testen", command=self._test_microphone).pack(pady=10)

    def _create_transcription_tab(self, parent):
        """Erstellt den Transkription-Tab"""
        transcription_frame = ttk.LabelFrame(parent, text="Transkriptions-Einstellungen", padding=10)
        transcription_frame.pack(fill='x', pady=5)

        # Transkriptionsmodus
        mode_frame = ttk.Frame(transcription_frame)
        mode_frame.pack(fill='x', pady=5)

        ttk.Label(mode_frame, text="Transkriptionsmodus:").pack(anchor='w')

        # Radio-Buttons für Modus-Auswahl
        self.transcription_mode_var = tk.StringVar(value="local" if config.USE_LOCAL_TRANSCRIPTION else "api")

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

        self.model_size_var = tk.StringVar(value=config.WHISPER_MODEL_SIZE)

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
        about_frame = ttk.LabelFrame(parent, text="Voice Transcriber", padding=10)
        about_frame.pack(fill='x', pady=5)

        # Logo/Icon Platzhalter
        ttk.Label(about_frame, text="🎤", font=("Arial", 48)).pack(pady=10)

        ttk.Label(about_frame, text="Voice Transcriber", font=("Arial", 16, "bold")).pack(pady=5)
        ttk.Label(about_frame, text=f"Version {config.APP_VERSION} (Build 2025-11-10)").pack()
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
            return devices

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
            device_index = user_config.get('audio.device_index', -1)
            if device_index >= 0 and device_index < len(self.audio_devices):
                self.audio_device_var.set(self.audio_devices[device_index])
            else:
                self.audio_device_var.set("Standard (automatisch)")

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
            device_index = -1
            if selected_device != "Standard (automatisch)" and selected_device in self.audio_devices:
                device_index = self.audio_devices.index(selected_device)
            
            # Immer den Index speichern, auch wenn es -1 ist (Standard)
            user_config.set('audio.device_index', device_index)
            logger.info(f"Audio-Gerät gespeichert: {selected_device} (Index: {device_index})")

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

            debug_file = Path.home() / "voice_transcriber_debug.txt"
            if debug_file.exists():
                # Öffne mit Standard-Editor
                if os.name == 'nt':  # Windows
                    subprocess.run(['notepad.exe', str(debug_file)])
                else:
                    subprocess.run(['xdg-open', str(debug_file)])
            else:
                messagebox.showinfo("Debug-Datei", "Debug-Datei existiert noch nicht.\nMachen Sie eine Aufnahme, um sie zu erstellen.")

        except Exception as e:
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