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

        # Audio-Geräte laden
        self.audio_devices = self._get_audio_devices()

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

        # Tab 4: Über
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
            ("Ctrl + Shift + S", "ctrl+shift+s"),
            ("Alt + Shift + S", "alt+shift+s"),
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

    def _create_audio_tab(self, parent):
        """Erstellt den Audio-Tab"""
        audio_frame = ttk.LabelFrame(parent, text="Audio-Geräte", padding=10)
        audio_frame.pack(fill='x', pady=5)

        ttk.Label(audio_frame, text="Verfügbare Mikrofone:").pack(anchor='w', pady=5)

        # Audio Devices Liste
        device_frame = ttk.Frame(audio_frame)
        device_frame.pack(fill='x')

        if self.audio_devices:
            for i, device in enumerate(self.audio_devices[:5]):  # Max 5 anzeigen
                ttk.Label(device_frame, text=f"{i+1}. {device}").pack(anchor='w')
        else:
            ttk.Label(device_frame, text="❌ Keine Mikrofone gefunden", foreground="red").pack(anchor='w')

        # Test Button
        ttk.Button(audio_frame, text="Mikrofon testen", command=self._test_microphone).pack(pady=10)

    def _create_about_tab(self, parent):
        """Erstellt den Über-Tab"""
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
                    devices.append(device_info.get('name', f'Device {i}'))

            audio.terminate()
            return devices

        except Exception as e:
            logger.error(f"Fehler beim Laden der Audio-Geräte: {e}")
            return []

    def _test_microphone(self):
        """Testet das Mikrofon"""
        messagebox.showinfo("Mikrofon-Test", "Mikrofon-Test wird implementiert...")

    def _load_current_settings(self):
        """Lädt aktuelle Einstellungen"""
        # Hier könnte man gespeicherte Hotkey-Einstellungen laden
        pass

    def _save_settings(self):
        """Speichert die Einstellungen"""
        selected_hotkey = self.hotkey_var.get()
        messagebox.showinfo(
            "Einstellungen gespeichert",
            f"Hotkey '{selected_hotkey}' wurde ausgewählt.\n\n"
            "Änderungen werden nach Neustart der Anwendung wirksam."
        )
        self._close_window()

    def _reset_defaults(self):
        """Setzt Standardeinstellungen zurück"""
        self.hotkey_var.set("f12")
        messagebox.showinfo("Zurückgesetzt", "Standardeinstellungen wiederhergestellt.")

    def _close_window(self):
        """Schließt das Fenster"""
        if self.window:
            self.window.destroy()

    def get_selected_hotkey(self):
        """Gibt den ausgewählten Hotkey zurück"""
        return self.hotkey_var.get()