"""
Tests für audio_recorder.py - Audio-Komprimierung
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.audio_recorder import PYDUB_AVAILABLE, AudioRecorder
from src.config import config


class TestAudioCompression:
    """Test-Klasse für Audio-Komprimierung"""

    @pytest.fixture
    def recorder(self):
        """Erstellt einen AudioRecorder für Tests"""
        recorder = AudioRecorder()
        yield recorder
        recorder.cleanup()

    @pytest.fixture
    def test_wav_file(self):
        """Erstellt eine temporäre Test-WAV-Datei"""
        # Verwende eine der generierten Test-Dateien
        test_file = Path(__file__).parent / "test_data" / "audio" / "tone_440hz_1s.wav"
        if test_file.exists():
            return str(test_file)

        # Fallback: Erstelle eine einfache WAV-Datei
        import wave

        import numpy as np

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            # Erstelle 1 Sekunde 440Hz Ton
            sample_rate = 16000
            duration = 1.0
            frequency = 440
            num_samples = int(sample_rate * duration)
            t = np.linspace(0, duration, num_samples, False)
            wave_data = 0.5 * np.sin(2 * np.pi * frequency * t)
            samples = (wave_data * 32767).astype(np.int16)

            with wave.open(tmp.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(samples.tobytes())

            return tmp.name

    def test_compress_audio_basic(self, recorder, test_wav_file):
        """Test grundlegende Audio-Komprimierung"""
        # Komprimiere die Test-Datei
        compressed_data = recorder.compress_audio(test_wav_file)

        # Prüfe dass Daten zurückgegeben werden
        assert isinstance(compressed_data, bytes)
        assert len(compressed_data) > 0

        # Prüfe dass komprimierte Datei kleiner ist als Original (nur wenn pydub verfügbar)
        original_size = Path(test_wav_file).stat().st_size
        if PYDUB_AVAILABLE:
            assert len(compressed_data) < original_size
        else:
            # Wenn pydub nicht verfügbar, sollte Original zurückgegeben werden
            assert len(compressed_data) == original_size

    def test_compress_audio_with_custom_params(self, recorder, test_wav_file):
        """Test Komprimierung mit benutzerdefinierten Parametern"""
        compressed_data = recorder.compress_audio(
            test_wav_file,
            output_format='mp3',
            bitrate='128k'
        )

        assert isinstance(compressed_data, bytes)
        assert len(compressed_data) > 0

    def test_compress_audio_invalid_file(self, recorder):
        """Test Komprimierung mit ungültiger Datei"""
        with pytest.raises(Exception):
            recorder.compress_audio("nonexistent.wav")

    @patch('src.config.config.AUDIO_COMPRESSION_ENABLED', True)
    def test_record_and_compress_enabled(self, recorder):
        """Test record_and_compress wenn Komprimierung aktiviert"""
        # Mock die Aufnahme-Methode
        with patch.object(recorder, 'record_audio', return_value='test.wav'):
            with patch.object(recorder, 'compress_audio', return_value=b'compressed_data') as mock_compress:
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', MagicMock()) as mock_open:
                        result = recorder.record_and_compress()

                        assert result == b'compressed_data'
                        mock_compress.assert_called_once_with('test.wav')

    @patch('src.config.config.AUDIO_COMPRESSION_ENABLED', False)
    def test_record_and_compress_disabled(self, recorder):
        """Test record_and_compress wenn Komprimierung deaktiviert"""
        # Mock die Aufnahme-Methode
        with patch.object(recorder, 'record_audio', return_value='test.wav'):
            with patch('builtins.open', MagicMock()) as mock_open:
                mock_file = MagicMock()
                mock_file.read.return_value = b'raw_wav_data'
                mock_open.return_value.__enter__.return_value = mock_file

                result = recorder.record_and_compress()

                assert result == b'raw_wav_data'

    def test_record_and_compress_error_handling(self, recorder):
        """Test Fehlerbehandlung in record_and_compress"""
        # Mock die Aufnahme-Methode um None zurückzugeben
        with patch.object(recorder, 'record_audio', return_value=None):
            result = recorder.record_and_compress()
            assert result is None

    def test_compression_ratio_calculation(self, recorder, test_wav_file):
        """Test dass Komprimierungsrate korrekt berechnet wird"""
        original_size = Path(test_wav_file).stat().st_size

        with patch('src.audio_recorder.logger') as mock_logger:
            recorder.compress_audio(test_wav_file)

            if PYDUB_AVAILABLE:
                # Prüfe dass Logging-Aufruf mit Komprimierungsrate erfolgt
                mock_logger.info.assert_called()
                log_call = mock_logger.info.call_args[0][0]
                assert "Audio komprimiert:" in log_call
                assert ".1%" in log_call
            else:
                # Bei fehlendem pydub sollte keine Info-Log-Nachricht erfolgen
                mock_logger.info.assert_not_called()

    @pytest.mark.parametrize("output_format,bitrate", [
        ('mp3', '64k'),
        ('mp3', '128k'),
        ('mp3', '256k'),
    ])
    def test_different_compression_settings(self, recorder, test_wav_file, output_format, bitrate):
        """Test verschiedene Komprimierungseinstellungen"""
        compressed_data = recorder.compress_audio(
            test_wav_file,
            output_format=output_format,
            bitrate=bitrate
        )

        assert isinstance(compressed_data, bytes)
        assert len(compressed_data) > 0

        # Höhere Bitrate sollte größere Datei ergeben (nur wenn pydub verfügbar)
        if PYDUB_AVAILABLE and bitrate == '256k':
            # Vergleiche mit 64k Version
            compressed_64k = recorder.compress_audio(test_wav_file, output_format=output_format, bitrate='64k')
            assert len(compressed_data) > len(compressed_64k)