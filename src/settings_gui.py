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

class Tooltip:
    """Custom Tooltip class for tkinter widgets"""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Shows the tooltip"""
        if self.tooltip_window or not self.text:
            return

        # Get widget position
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Create label with tooltip text
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            justify='left',
            background="#ffffe0",
            relief='solid',
            borderwidth=1,
            font=("TkDefaultFont", 8)
        )
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        """Hides the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class SettingsGUI:
    """Einstellungs-GUI für Voice Transcriber"""

    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.hotkey_var = tk.StringVar(value="f12")
        self.audio_device_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.show_key_var = tk.BooleanVar(value=False)  # Für API-Key Sichtbarkeit

        # Rate-Limiting für Speichern (verhindert Mehrfach-Speicherung)
        self.last_save_time = 0
        self.save_cooldown = 1.0  # 1 Sekunde Cooldown

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
        self.window = tk.Toplevel(self.parent)        # Styles konfigurieren
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=2)
        
        # Tab-Style optimieren
        style.configure("TNotebook", padding=5)
        style.configure("TNotebook.Tab", 
                       padding=[12, 4], 
                       font=("TkDefaultFont", 10))
        
        # Aktiven Tab hervorheben (Fett + Dunklerer Hintergrund simulieren durch Map)
        style.map("TNotebook.Tab",
                 background=[("selected", "#0078D7")], # Windows Blau für aktiv
                 foreground=[("selected", "white")],
                 font=[("selected", ("TkDefaultFont", 10, "bold"))])

        self.window.geometry("600x800")
        self.window.resizable(True, True)

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

        open_debug_btn = ttk.Button(
            debug_frame,
            text="📄 Debug-Datei öffnen",
            command=self._open_debug_file
        )
        open_debug_btn.pack(side='left', padx=5)
        Tooltip(open_debug_btn, "Öffnet die Debug-Datei im Standard-Editor.\nEnthält Aufnahme-Details, Transkriptions-Ergebnisse und Fehler-Logs.")

        clear_debug_btn = ttk.Button(
            debug_frame,
            text="🗑️ Debug-Datei löschen",
            command=self._clear_debug_file
        )
        clear_debug_btn.pack(side='left', padx=5)
        Tooltip(clear_debug_btn, "Löscht die Debug-Datei vollständig.\nDie Datei wird bei der nächsten Aufnahme neu erstellt.")

        self.notebook = ttk.Notebook(self.window)
        # Mehr Abstand nach oben für bessere Sichtbarkeit der Reiter
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(15, 10))

        # Tabs erstellen
        self.tabs = {}
        for name, creator in [
            ("Allgemein", self._create_general_tab),
            ("Hotkeys", self._create_hotkey_tab),
            ("Audio", self._create_audio_tab),
            ("Transkription", self._create_transcription_tab),
            ("API-Schlüssel", self._create_api_tab),
            ("Über", self._create_about_tab)
        ]:
            # Erstelle Tab-Frame mit Canvas für Scrolling
            tab_outer_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_outer_frame, text=name)
            
            # Canvas + Scrollbar (mit sichtbarem Hintergrund)
            canvas = tk.Canvas(tab_outer_frame, highlightthickness=0, bg='SystemButtonFace')
            scrollbar = ttk.Scrollbar(tab_outer_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas, padding=10)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Mausrad-Unterstützung
            def _on_mousewheel(event, c=canvas):
                c.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            self.tabs[name] = scrollable_frame
            
            try:
                creator(scrollable_frame)
            except Exception as e:
                logger.error(f"Fehler beim Erstellen des Tabs '{name}': {e}")
                ttk.Label(scrollable_frame, text=f"Fehler beim Laden: {e}", foreground="red").pack()

        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=5)

        save_btn = ttk.Button(button_frame, text="Speichern", command=self._save_settings)
        save_btn.pack(side='right', padx=5)
        Tooltip(save_btn, "Speichert alle Einstellungen und schließt das Fenster.\nÄnderungen werden beim nächsten Neustart wirksam.")

        cancel_btn = ttk.Button(button_frame, text="Abbrechen", command=self._close_window)
        cancel_btn.pack(side='right', padx=5)
        Tooltip(cancel_btn, "Schließt das Einstellungsfenster ohne zu speichern.")

        export_btn = ttk.Button(button_frame, text="Export", command=self._export_settings)
        export_btn.pack(side='left', padx=5)
        Tooltip(export_btn, "Exportiert alle Einstellungen in eine Datei.")

        import_btn = ttk.Button(button_frame, text="Import", command=self._import_settings)
        import_btn.pack(side='left', padx=5)
        Tooltip(import_btn, "Importiert Einstellungen aus einer Datei.")

        reset_btn = ttk.Button(button_frame, text="Standard", command=self._reset_defaults)
        reset_btn.pack(side='left', padx=5)
        Tooltip(reset_btn, "Setzt alle Einstellungen auf Standardwerte zurück.")

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

        # Datei-Verwaltung
        files_frame = ttk.LabelFrame(parent, text="Datei-Verwaltung", padding=10)
        files_frame.pack(fill='x', pady=5, anchor='n')  # explizit anchor n

        btn_frame = ttk.Frame(files_frame)
        btn_frame.pack(fill='x', expand=True, pady=5)

        open_temp_btn = ttk.Button(btn_frame, text="📂 Temp-Ordner öffnen", command=self._open_temp_dir)
        open_temp_btn.pack(side='left', padx=5, fill='x', expand=True)
        Tooltip(open_temp_btn, "Öffnet den Ordner mit temporären Audiodateien.")

        cleanup_btn = ttk.Button(btn_frame, text="🧹 Temp bereinigen", command=self._cleanup_temp_files)
        cleanup_btn.pack(side='left', padx=5, fill='x', expand=True)
        Tooltip(cleanup_btn, "Löscht alle temporären Audiodateien (.wav).")

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
            rb = ttk.Radiobutton(
                hotkey_frame,
                text=text,
                variable=self.hotkey_var,
                value=value
            )
            rb.pack(anchor='w', pady=2)
            Tooltip(rb, f"Aktiviert Push-to-Talk mit {text}.\nDrücken Sie diese Taste, um mit der Aufnahme zu beginnen.")

        # Info
        info_frame = ttk.Frame(hotkey_frame)
        info_frame.pack(fill='x', pady=10)

        rec_label = ttk.Label(
            info_frame,
            text="💡 Empfehlung: F12 - funktioniert immer und ist einfach zu erreichen",
            foreground="blue"
        )
        rec_label.pack(anchor='w')
        Tooltip(rec_label, "F12 ist die beste Wahl für die meisten Benutzer.\nSie ist immer verfügbar und einfach zu erreichen.")

        restart_label = ttk.Label(
            info_frame,
            text="🔄 Änderungen werden nach Neustart wirksam",
            foreground="orange"
        )
        restart_label.pack(anchor='w')
        Tooltip(restart_label, "Der Hotkey-Listener muss neu gestartet werden,\num die Änderungen zu übernehmen.")

        windows_label = ttk.Label(
            info_frame,
            text="⚠️ Windows-Taste-Kombinationen werden vom OS blockiert",
            foreground="red"
        )
        windows_label.pack(anchor='w')
        Tooltip(windows_label, "Kombinationen mit der Windows-Taste werden vom\nBetriebssystem reserviert und funktionieren nicht.")

        # Test Button für Live-Vorschau
        test_hotkey_btn = ttk.Button(hotkey_frame, text="Hotkey testen", command=self._test_hotkey)
        test_hotkey_btn.pack(pady=10)
        Tooltip(test_hotkey_btn, "Testet den ausgewählten Hotkey live.\nDrücken Sie den Hotkey innerhalb von 5 Sekunden.")

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
        Tooltip(device_combo, "Wählen Sie Ihr bevorzugtes Mikrofon aus.\n'Standard' verwendet das System-Standardgerät.")

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
        test_btn = ttk.Button(audio_frame, text="Mikrofon testen", command=self._test_microphone)
        test_btn.pack(pady=10)
        Tooltip(test_btn, "Testet das ausgewählte Mikrofon auf Funktionalität.\nÜberprüft Audio-Eingang und Qualität.")

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

        api_rb = ttk.Radiobutton(
            mode_frame,
            text="OpenAI API (kostenpflichtig, immer verfügbar)",
            variable=self.transcription_mode_var,
            value="api"
        )
        api_rb.pack(anchor='w', pady=2)
        Tooltip(api_rb, "Verwendet OpenAI's Whisper API für Transkription.\nErfordert API-Key und Internet-Verbindung.")

        local_rb = ttk.Radiobutton(
            mode_frame,
            text="Lokales Modell (kostenlos, offline-fähig)",
            variable=self.transcription_mode_var,
            value="local"
        )
        local_rb.pack(anchor='w', pady=2)
        Tooltip(local_rb, "Lädt Whisper-Modell auf Ihren Computer.\nFunktioniert offline, erster Start dauert länger.")

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
            rb = ttk.Radiobutton(
                model_frame,
                text=text,
                variable=self.model_size_var,
                value=value
            )
            rb.pack(anchor='w', pady=1)
            Tooltip(rb, f"Wählt das {value.upper()} Modell.\n{text.split('(')[1].rstrip(')')}\nGrößere Modelle sind genauer aber langsamer.")

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

        # Password-Entry für Sicherheit mit Validierung
        self.api_key_entry = ttk.Entry(input_frame, textvariable=self.api_key_var, show="*")
        self.api_key_entry.pack(fill='x', pady=5)
        Tooltip(self.api_key_entry, "Geben Sie Ihren OpenAI API-Key ein.\nBeginnt mit 'sk-' und ist ca. 51 Zeichen lang.\nWird verschlüsselt gespeichert.")

        # Validierungs-Label (wird dynamisch aktualisiert)
        self.api_key_validation_label = ttk.Label(input_frame, text="", foreground="red")
        self.api_key_validation_label.pack(anchor='w', pady=2)

        # API-Key Validierung beim Tippen
        self.api_key_var.trace_add("write", self._validate_api_key)

        # Checkbox zum Anzeigen/Verstecken
        self.show_key_var = tk.BooleanVar(value=False)
        show_key_cb = ttk.Checkbutton(
            input_frame,
            text="API-Key anzeigen",
            variable=self.show_key_var,
            command=self._toggle_api_key_visibility
        )
        show_key_cb.pack(anchor='w', pady=5)
        Tooltip(show_key_cb, "Zeigt den API-Key im Klartext an.\nDeaktivieren Sie dies für Sicherheit.")

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

    def _validate_api_key(self, *args):
        """Validiert den API-Key beim Tippen"""
        api_key = self.api_key_var.get().strip()

        if not api_key:
            self.api_key_validation_label.config(text="", foreground="red")
            return

        # Länge prüfen (OpenAI Keys sind ~51 Zeichen)
        if len(api_key) < 20:
            self.api_key_validation_label.config(
                text="❌ Zu kurz (OpenAI Keys sind ~51 Zeichen)",
                foreground="red"
            )
            return

        # Format prüfen (muss mit sk- beginnen)
        if not api_key.startswith('sk-'):
            self.api_key_validation_label.config(
                text="❌ Muss mit 'sk-' beginnen",
                foreground="red"
            )
            return

        # Länge für vollständigen Key prüfen
        if len(api_key) > 10 and len(api_key) < 50:
            self.api_key_validation_label.config(
                text="⚠️ Unvollständig (OpenAI Keys sind ~51 Zeichen)",
                foreground="orange"
            )
            return

        # Erfolgreich
        if len(api_key) >= 50:
            self.api_key_validation_label.config(
                text="✅ Format korrekt",
                foreground="green"
            )
        else:
            self.api_key_validation_label.config(text="", foreground="red")

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
        # Rate-Limiting prüfen
        import time
        current_time = time.time()
        if current_time - self.last_save_time < self.save_cooldown:
            messagebox.showwarning("Bitte warten", "Bitte warten Sie einen Moment, bevor Sie erneut speichern.")
            return
        self.last_save_time = current_time

        try:
            from src.user_config import user_config

            # API-Key Validierung
            api_key = self.api_key_var.get().strip()
            if api_key:
                if not api_key.startswith('sk-'):
                    messagebox.showerror("Fehler", "Ungültiger API-Key Format. Muss mit 'sk-' beginnen.")
                    return
                if len(api_key) < 50:
                    messagebox.showerror("Fehler", "API-Key scheint unvollständig zu sein. OpenAI Keys sind ~51 Zeichen lang.")
                    return
                user_config.set_encrypted('api.openai_key', api_key)
                logger.info("API-Key erfolgreich verschlüsselt gespeichert")

                # API-Key aus RAM löschen für Sicherheit
                self.api_key_var.set("")
                self.api_key_validation_label.config(text="", foreground="red")

            # Audio-Gerät speichern
            selected_device = self.audio_device_var.get()
            user_config.set('audio.device_name', selected_device)

            # Transkriptions-Einstellungen mit Validierung
            transcription_mode = self.transcription_mode_var.get()
            use_local = transcription_mode == "local"
            model_size = self.model_size_var.get()

            # Modell-Validierung
            valid_models = ['tiny', 'base', 'small', 'medium', 'large']
            if use_local and model_size not in valid_models:
                messagebox.showerror("Fehler", f"Ungültiges Whisper-Modell: {model_size}. Muss eines der folgenden sein: {', '.join(valid_models)}")
                return

            user_config.set('transcription.use_local', use_local)
            user_config.set('transcription.whisper_model_size', model_size)
            logger.info(f"Transkriptions-Einstellungen gespeichert: use_local={use_local}, model_size={model_size}")

            # Hotkey speichern mit Sanitization
            selected_hotkey = self.hotkey_var.get().strip().lower()
            if selected_hotkey:
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
            from .user_config import user_config
            possible_paths = [
                user_config.get_appdata_dir() / "voice_transcriber_debug.txt",  # AppData (priorisiert)
                Path.home() / "voice_transcriber_debug.txt",  # Home-Verzeichnis (Legacy)
                Path.cwd() / "voice_transcriber_debug.txt",   # Arbeitsverzeichnis
                Path.home() / "AppData" / "Roaming" / "VoiceTranscriber" / "voice_transcriber_debug.txt",  # Windows AppData explizit
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

    def _export_settings(self):
        """Exportiert Einstellungen in eine Datei"""
        try:
            from tkinter import filedialog
            from pathlib import Path
            import json
            from datetime import datetime

            # Datei-Dialog für Export
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")],
                title="Einstellungen exportieren"
            )

            if not file_path:
                return

            # Sammle alle Einstellungen
            from src.user_config import user_config
            settings = {
                "version": config.APP_VERSION,
                "export_date": datetime.now().isoformat(),
                "settings": user_config._config.copy()  # Export raw config
            }

            # Schreibe in Datei
            Path(file_path).write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding='utf-8')

            messagebox.showinfo("Export erfolgreich", f"Einstellungen wurden nach {file_path} exportiert.")

        except Exception as e:
            logger.error(f"Fehler beim Exportieren: {e}")
            messagebox.showerror("Fehler", f"Export fehlgeschlagen: {e}")

    def _open_temp_dir(self):
        """Öffnet das Temp-Verzeichnis"""
        try:
            import os
            import subprocess
            temp_dir = config.get_temp_dir()
            
            if not temp_dir.exists():
                temp_dir.mkdir(parents=True)
                
            if os.name == 'nt':
                os.startfile(temp_dir)
            else:
                subprocess.run(['xdg-open', str(temp_dir)])
                
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Temp-Verzeichnisses: {e}")
            messagebox.showerror("Fehler", f"Konnte Temp-Verzeichnis nicht öffnen: {e}")

    def _cleanup_temp_files(self):
        """Bereinigt temporäre Dateien"""
        if not messagebox.askyesno("Bereinigen", "Möchten Sie wirklich alle temporären WAV-Dateien löschen?"):
            return
            
        try:
            temp_dir = config.get_temp_dir()
            count = 0
            size_bytes = 0
            
            for wav_file in temp_dir.glob("recording_*.wav"):
                try:
                    size_bytes += wav_file.stat().st_size
                    wav_file.unlink()
                    count += 1
                except Exception:
                    pass
            
            size_mb = size_bytes / (1024 * 1024)
            messagebox.showinfo("Bereinigung", f"Es wurden {count} Dateien gelöscht ({size_mb:.1f} MB freigegeben).")
            
        except Exception as e:
            logger.error(f"Fehler beim Bereinigen: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Bereinigen: {e}")

    def _import_settings(self):
        """Importiert Einstellungen aus einer Datei"""
        try:
            from tkinter import filedialog
            from pathlib import Path
            import json

            # Datei-Dialog für Import
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")],
                title="Einstellungen importieren"
            )

            if not file_path:
                return

            # Lese Datei
            content = Path(file_path).read_text(encoding='utf-8')
            data = json.loads(content)

            # Validiere Format
            if "settings" not in data:
                raise ValueError("Ungültiges Dateiformat")

            # Bestätigung
            if not messagebox.askyesno("Import bestätigen",
                f"Möchten Sie wirklich alle Einstellungen aus {Path(file_path).name} importieren?\n\nDies überschreibt alle aktuellen Einstellungen."):
                return

            # Importiere Einstellungen
            from src.user_config import user_config
            user_config._config = data["settings"]
            user_config.save()

            messagebox.showinfo("Import erfolgreich",
                "Einstellungen wurden erfolgreich importiert.\n\nDie Änderungen werden beim nächsten Neustart wirksam.")

        except Exception as e:
            logger.error(f"Fehler beim Importieren: {e}")
            messagebox.showerror("Fehler", f"Import fehlgeschlagen: {e}")

    def _test_hotkey(self):
        """Testet den ausgewählten Hotkey live"""
        import threading
        import time

        selected_hotkey = self.hotkey_var.get()
        if not selected_hotkey:
            messagebox.showwarning("Kein Hotkey", "Bitte wählen Sie zuerst einen Hotkey aus.")
            return

        # Temporäres Flag für Test-Erkennung
        self.hotkey_test_detected = False

        def on_test_press():
            self.hotkey_test_detected = True

        def test_thread():
            try:
                import keyboard
                # Registriere temporären Hotkey
                keyboard.on_press_key(selected_hotkey, lambda e: on_test_press())

                # Zeige Countdown
                for i in range(5, 0, -1):
                    if hasattr(self, 'test_progress_label'):
                        self.test_progress_label.config(text=f"Drücken Sie {selected_hotkey.upper()} ... {i}s")
                    time.sleep(1)

                # Aufräumen
                keyboard.unhook_all()

                # Ergebnis anzeigen
                if self.hotkey_test_detected:
                    messagebox.showinfo("Hotkey-Test", f"✅ Hotkey '{selected_hotkey.upper()}' funktioniert!\n\nDer Hotkey wurde erfolgreich erkannt.")
                else:
                    messagebox.showwarning("Hotkey-Test", f"❌ Hotkey '{selected_hotkey.upper()}' nicht erkannt.\n\nMögliche Ursachen:\n• Hotkey wird vom System blockiert\n• Tippfehler in der Kombination\n• Andere Anwendung verwendet den Hotkey")

            except Exception as e:
                messagebox.showerror("Fehler", f"Hotkey-Test fehlgeschlagen: {e}")

        # Erstelle temporäres Label für Countdown
        if self.window:
            self.test_progress_label = ttk.Label(self.window, text=f"Drücken Sie {selected_hotkey.upper()} ... 5s")
            self.test_progress_label.pack(pady=5)

            # Starte Test in separatem Thread
            threading.Thread(target=test_thread, daemon=True).start()

            # Entferne Label nach 6 Sekunden
            self.window.after(6000, lambda: self.test_progress_label.destroy() if hasattr(self, 'test_progress_label') else None)
        else:
            messagebox.showerror("Fehler", "Fenster nicht verfügbar für Hotkey-Test.")

    def get_selected_hotkey(self):
        """Gibt den ausgewählten Hotkey zurück"""
        return self.hotkey_var.get()

    def _create_about_tab(self, parent):
        """Erstellt den Über-Tab (parent ist bereits scrollbar)"""
        # Icon (Mikrofon-Emoji als Text)
        icon_label = ttk.Label(parent, text="🎤", font=("Segoe UI Emoji", 48))
        icon_label.pack(pady=(20, 10))

        # App Name
        ttk.Label(parent, text="Voice Transcriber", 
                 font=("TkDefaultFont", 16, "bold")).pack()

        # Version
        ttk.Label(parent, text=f"Version {config.APP_VERSION}", 
                 font=("TkDefaultFont", 10)).pack(pady=5)

        # Beschreibung
        ttk.Label(parent, text="Push-to-Talk Sprach-zu-Text Transkription", 
                 font=("TkDefaultFont", 9)).pack(pady=10)

        # Technologien
        tech_frame = ttk.LabelFrame(parent, text="Technologien", padding=15)
        tech_frame.pack(fill='x', padx=20, pady=10)

        technologies = [
            "• Whisper AI (OpenAI) - Lokale Transkription",
            "• PyAudio - Audio-Aufnahme",
            "• PyTorch (CPU) - ML-Framework",
            "• Tkinter - Benutzeroberfläche",
            "• Python 3.13 - Programmiersprache"
        ]

        for tech in technologies:
            ttk.Label(tech_frame, text=tech, font=("TkDefaultFont", 9)).pack(anchor='w', pady=2)

        # Features
        features_frame = ttk.LabelFrame(parent, text="Features", padding=15)
        features_frame.pack(fill='x', padx=20, pady=10)

        features = [
            "✓ Lokale Whisper-Transkription (offline)",
            "✓ Mehrere Hotkeys (F12, F11, F10)",
            "✓ Persistente Geräteauswahl",
            "✓ Temp-Datei-Verwaltung",
            "✓ Debug-Logging"
        ]

        for feature in features:
            ttk.Label(features_frame, text=feature, font=("TkDefaultFont", 9)).pack(anchor='w', pady=2)

        # Copyright
        ttk.Label(parent, text="© 2026 Quievreux", 
                 font=("TkDefaultFont", 8)).pack(pady=(20, 10))