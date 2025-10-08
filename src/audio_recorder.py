"""
Audio Recorder - Mikrofon-Aufnahme
Zeichnet Audio vom Standard-Mikrofon auf und speichert als WAV.
"""

import logging
import threading
import time
import wave
import pyaudio
from pathlib import Path
from typing import Optional

from .config import config

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

        self._init_audio()

    def _init_audio(self):
        """Initialisiert PyAudio"""
        try:
            self.audio = pyaudio.PyAudio()
            logger.info("PyAudio erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"Fehler bei PyAudio-Initialisierung: {e}")
            raise

    def start_recording(self) -> Optional[str]:
        """Startet die Audio-Aufnahme und gibt den Dateipfad zurück"""
        if self.is_recording:
            logger.warning("Aufnahme läuft bereits")
            return None

        try:
            # Stream öffnen
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=config.CHANNELS,
                rate=config.SAMPLE_RATE,
                input=True,
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
                logger.info(f"Audio gespeichert: {self.temp_file}")
                return str(self.temp_file)
            else:
                logger.error("Keine Audio-Frames zum Speichern")
                return None

        except Exception as e:
            logger.error(f"Fehler beim Stoppen der Aufnahme: {e}")
            return None

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
                    data = self.stream.read(1024, exception_on_overflow=False)
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
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(config.SAMPLE_RATE)
                wf.writeframes(b''.join(self.frames))

            logger.info(f"WAV-Datei gespeichert: {self.temp_file} ({len(self.frames)} Frames)")

        except Exception as e:
            logger.error(f"Fehler beim Speichern der WAV-Datei: {e}")
            raise

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