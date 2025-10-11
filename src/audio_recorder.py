"""
Audio Recorder - Mikrofon-Aufnahme
Zeichnet Audio vom Standard-Mikrofon auf und speichert als WAV.
"""

import io
import logging
import threading
import time
import wave
from pathlib import Path
from typing import Optional

import pyaudio

from src.config import config

# Optional: pydub für Audio-Komprimierung
PYDUB_AVAILABLE = False
try:
    from pydub import AudioSegment

    # Teste pydub Funktionalität
    test_segment = AudioSegment.empty()
    PYDUB_AVAILABLE = True
    logging.info("pydub erfolgreich initialisiert - Audio-Komprimierung verfügbar")
except Exception as e:
    logging.warning(f"pydub nicht verfügbar oder defekt ({e}) - Audio-Komprimierung deaktiviert")
    PYDUB_AVAILABLE = False

logger = logging.getLogger(__name__)

class AudioRecorder:
    """Verwaltet Audio-Aufnahme vom Mikrofon"""

    def __init__(self):
        self.audio: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        self.frames = []
        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.temp_file: Optional[Path] = None
        self.last_recording_duration = 0.0  # Dauer der letzten Aufnahme in Sekunden

        self._init_audio()

    def _init_audio(self):
        """Initialisiert PyAudio"""
        try:
            self.audio = pyaudio.PyAudio()

            # Logge verfügbare Audio-Geräte für Debugging
            device_count = self.audio.get_device_count()
            logger.info(f"PyAudio erfolgreich initialisiert - {device_count} Audio-Geräte verfügbar")

            # Zeige Standard-Input-Gerät
            try:
                default_input = self.audio.get_default_input_device_info()
                logger.info(f"Standard-Input-Gerät: {default_input['name']} (Index: {default_input['index']})")
            except Exception as e:
                logger.warning(f"Konnte Standard-Input-Gerät nicht ermitteln: {e}")

        except Exception as e:
            logger.error(f"Fehler bei PyAudio-Initialisierung: {e}")
            raise

    def start_recording(self) -> Optional[str]:
        """Startet die Audio-Aufnahme und gibt den Dateipfad zurück"""
        if self.is_recording:
            logger.warning("Aufnahme läuft bereits")
            return None

        try:
            # Stelle sicher, dass vorheriger Stream geschlossen ist
            self._cleanup_stream()

            # Stream öffnen
            input_device_index = config.AUDIO_DEVICE_INDEX if config.AUDIO_DEVICE_INDEX >= 0 else None
            self.stream = self.audio.open(  # type: ignore
                format=pyaudio.paInt16,
                channels=config.CHANNELS,
                rate=config.SAMPLE_RATE,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=1024
            )

            self.frames = []
            self.is_recording = True

            # Temporäre Datei vorbereiten
            self.temp_file = config.get_temp_dir() / f"recording_{int(time.time())}.wav"

            # Aufnahme in separatem Thread starten
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.daemon = True
            self.recording_thread.start()

            logger.info("Audio-Aufnahme gestartet")
            return str(self.temp_file)

        except Exception as e:
            logger.error(f"Fehler beim Starten der Aufnahme: {e}")
            self._cleanup_stream()
            return None

    def stop_recording(self) -> Optional[str]:
        """Stoppt die Aufnahme und speichert die Datei"""
        if not self.is_recording:
            logger.warning("Keine Aufnahme läuft")
            return None

        try:
            self.is_recording = False

            # Warte auf Thread-Ende
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=1.0)

            # Stream schließen
            self._cleanup_stream()

            # WAV-Datei speichern
            if self.frames and self.temp_file:
                self._save_wav_file()

                # Berechne Aufnahmedauer
                self.last_recording_duration = len(self.frames) * 1024 / config.SAMPLE_RATE

                logger.info(f"Audio gespeichert: {self.temp_file}")
                return str(self.temp_file)
            else:
                logger.error("Keine Audio-Frames zum Speichern")
                return None

        except Exception as e:
            logger.error(f"Fehler beim Stoppen der Aufnahme: {e}")
            return None

    def record_audio(self) -> Optional[str]:
        """Führt komplette Audio-Aufnahme durch (start + stop)"""
        wav_path = self.start_recording()
        if not wav_path:
            return None

        # Kurze Pause für Aufnahme
        time.sleep(1.0)  # 1 Sekunde Test-Aufnahme

        return self.stop_recording()

    def _record_audio(self):
        """Aufnahme-Loop in separatem Thread"""
        logger.info("Aufnahme-Thread gestartet")

        start_time = time.time()
        max_duration = config.MAX_RECORDING_DURATION

        try:
            while self.is_recording:
                # Prüfe Zeitlimit
                if time.time() - start_time >= max_duration:
                    logger.info(f"Maximale Aufnahmedauer ({max_duration}s) erreicht")
                    self.is_recording = False
                    break

                # Audio-Frame lesen
                try:
                    data = self.stream.read(1024, exception_on_overflow=False)  # type: ignore
                    self.frames.append(data)
                except Exception as e:
                    logger.error(f"Fehler beim Lesen von Audio-Frame: {e}")
                    break

        except Exception as e:
            logger.error(f"Fehler im Aufnahme-Thread: {e}")
        finally:
            logger.info("Aufnahme-Thread beendet")

    def _save_wav_file(self):
        """Speichert die aufgezeichneten Frames als WAV-Datei"""
        try:
            with wave.open(str(self.temp_file), 'wb') as wf:
                wf.setnchannels(config.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))  # type: ignore
                wf.setframerate(config.SAMPLE_RATE)
                wf.writeframes(b''.join(self.frames))

            logger.info(f"WAV-Datei gespeichert: {self.temp_file} ({len(self.frames)} Frames)")

        except Exception as e:
            logger.error(f"Fehler beim Speichern der WAV-Datei: {e}")
            raise

    def compress_audio(self, wav_path: str, output_format: Optional[str] = None,
                      bitrate: Optional[str] = None) -> bytes:
        """Komprimiert WAV-Datei in effizienteres Format"""
        if not PYDUB_AVAILABLE:
            logger.warning("pydub nicht verfügbar - verwende Original-WAV")
            with open(wav_path, 'rb') as f:
                return f.read()

        if output_format is None:
            output_format = config.AUDIO_COMPRESSION_FORMAT
        if bitrate is None:
            bitrate = config.AUDIO_COMPRESSION_BITRATE

        try:
            # Audio laden
            audio = AudioSegment.from_wav(wav_path)

            # In Buffer komprimieren
            buffer = io.BytesIO()
            audio.export(buffer, format=output_format, bitrate=bitrate)
            compressed_data = buffer.getvalue()

            # Logging
            original_size = Path(wav_path).stat().st_size
            compression_ratio = len(compressed_data) / original_size
            logger.info(f"Audio komprimiert: {original_size} → {len(compressed_data)} bytes "
                       f"({compression_ratio:.1%})")

            return compressed_data

        except Exception as e:
            logger.error(f"Fehler bei Audio-Komprimierung: {e}")
            # Fallback: Original WAV zurückgeben
            with open(wav_path, 'rb') as f:
                return f.read()

    def record_and_compress(self) -> Optional[bytes]:
        """Vollständiger Workflow: Aufnahme + Komprimierung (wartet auf Hotkey-Release)"""
        if not config.AUDIO_COMPRESSION_ENABLED:
            logger.info("Audio-Komprimierung deaktiviert, verwende Standard-Aufnahme")
            wav_path = self.record_audio()
            if not wav_path:
                return None
            with open(wav_path, 'rb') as f:
                return f.read()

        try:
            # Aufnahme starten
            wav_path = self.start_recording()
            if not wav_path:
                return None

            logger.info("Aufnahme mit Komprimierung gestartet - warte auf Hotkey-Release...")

            # Warten bis Hotkey losgelassen wird (is_recording = False)
            while self.is_recording:
                time.sleep(0.01)  # Kurze Pause

            # Aufnahme stoppen
            final_wav_path = self.stop_recording()
            if not final_wav_path:
                return None

            # Prüfe Mindestdauer (0.1 Sekunden für OpenAI)
            audio_duration = len(self.frames) * 1024 / config.SAMPLE_RATE
            if audio_duration < 0.1:
                logger.warning(".2f")
                # Cleanup
                Path(final_wav_path).unlink(missing_ok=True)
                return None

            logger.info(".2f")

            # Komprimierung
            compressed_data = self.compress_audio(final_wav_path)

            # Cleanup
            Path(final_wav_path).unlink(missing_ok=True)

            return compressed_data

        except Exception as e:
            logger.error(f"Fehler bei Aufnahme + Komprimierung: {e}")
            # Fallback: Original WAV verwenden
            try:
                if 'final_wav_path' in locals() and final_wav_path and Path(final_wav_path).exists():
                    with open(final_wav_path, 'rb') as f:
                        return f.read()
            except Exception as fallback_e:
                logger.error(f"Fallback fehlgeschlagen: {fallback_e}")
            return None

    def _cleanup_stream(self):
        """Schließt Audio-Stream und räumt auf"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
                logger.debug("Audio-Stream geschlossen")
        except Exception as e:
            logger.warning(f"Fehler beim Schließen des Streams: {e}")

    def cleanup(self):
        """Vollständiges Cleanup"""
        logger.info("Audio-Recorder Cleanup")

        # Stoppe Aufnahme falls läuft
        if self.is_recording:
            self.stop_recording()

        # Stream schließen
        self._cleanup_stream()

        # PyAudio schließen
        try:
            if self.audio:
                self.audio.terminate()
                self.audio = None
                logger.debug("PyAudio terminiert")
        except Exception as e:
            logger.warning(f"Fehler beim Terminieren von PyAudio: {e}")

        # Temporäre Dateien löschen
        self._cleanup_temp_files()

    def _cleanup_temp_files(self):
        """Löscht temporäre Audio-Dateien"""
        try:
            temp_dir = config.get_temp_dir()
            for wav_file in temp_dir.glob("recording_*.wav"):
                try:
                    wav_file.unlink()
                    logger.debug(f"Temporäre Datei gelöscht: {wav_file}")
                except Exception as e:
                    logger.warning(f"Fehler beim Löschen von {wav_file}: {e}")
        except Exception as e:
            logger.warning(f"Fehler beim Cleanup temporärer Dateien: {e}")

    def __del__(self):
        """Destructor"""
        self.cleanup()