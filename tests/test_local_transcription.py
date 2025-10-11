"""
Unit-Tests für das lokale Transkriptionsmodul (faster-whisper)
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.config import config
from src.local_transcription import LocalTranscriptionService


class TestLocalTranscriptionService:
    """Unit-Tests für LocalTranscriptionService"""

    @pytest.fixture
    def test_wav_file(self):
        """Stellt eine Test-WAV-Datei bereit"""
        test_file = Path(__file__).parent / "test_data" / "audio" / "speech_like_2s.wav"
        if test_file.exists():
            return str(test_file)
        return None

    @pytest.fixture
    def mock_whisper_model(self):
        """Mock für WhisperModel"""
        with patch('src.local_transcription.WhisperModel') as mock_whisper, \
             patch('src.local_transcription.torch') as mock_torch:
            mock_model = MagicMock()
            mock_whisper.return_value = mock_model

            # Mock torch.cuda
            mock_torch.cuda.is_available.return_value = False

            # Mock transcribe Methode
            mock_segments = [
                MagicMock(text="Das ist ein Test."),
                MagicMock(text=" Wie geht es dir?")
            ]
            mock_model.transcribe.return_value = (mock_segments, {"language": "de"})

            yield mock_model

    def test_initialization_success(self, mock_whisper_model):
        """Test erfolgreiche Initialisierung"""
        with patch('src.local_transcription.torch.cuda.is_available', return_value=True):
            service = LocalTranscriptionService()

            assert service.model is not None
            assert service.model_size == config.WHISPER_MODEL_SIZE
            assert service.is_available()

    def test_initialization_failure(self):
        """Test Initialisierung bei Fehler"""
        with patch('src.local_transcription.WhisperModel', side_effect=Exception("Model load failed")):
            with pytest.raises(RuntimeError, match="Whisper-Modell konnte nicht geladen werden"):
                LocalTranscriptionService()

    def test_transcribe_file_success(self, test_wav_file, mock_whisper_model):
        """Test erfolgreiche Transkription einer Datei"""
        if not test_wav_file:
            pytest.skip("Test-WAV-Datei nicht verfügbar")

        service = LocalTranscriptionService()

        result = service.transcribe(test_wav_file)

        assert isinstance(result, str)
        assert "Das ist ein Test." in result
        assert "Wie geht es dir?" in result
        mock_whisper_model.transcribe.assert_called_once()

    def test_transcribe_file_validation_error(self, mock_whisper_model):
        """Test Validierungsfehler bei ungültiger Datei"""
        service = LocalTranscriptionService()

        # Test mit nicht existierender Datei
        result = service.transcribe("nonexistent.wav")
        assert result is None

        # Test mit zu großer Datei
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('pathlib.Path.is_file', return_value=True):
            mock_stat.return_value.st_size = 30 * 1024 * 1024  # 30MB
            result = service.transcribe("large_file.wav")
            assert result is None

    def test_transcribe_audio_data_success(self, mock_whisper_model, tmp_path):
        """Test erfolgreiche Transkription von Audio-Daten"""
        service = LocalTranscriptionService()

        test_data = b'dummy_audio_data'

        # Erstelle eine echte temporäre Datei für den Test
        temp_file = tmp_path / "temp_audio.mp3"
        temp_file.write_bytes(test_data)

        with patch('tempfile.NamedTemporaryFile') as mock_temp_file:
            mock_file = MagicMock()
            mock_file.name = str(temp_file)
            mock_temp_file.return_value.__enter__.return_value = mock_file

            result = service.transcribe_audio_data(test_data, "audio.mp3")

            assert isinstance(result, str)
            assert "Das ist ein Test." in result
            assert "Wie geht es dir?" in result

    def test_transcribe_audio_data_error(self, mock_whisper_model):
        """Test Fehlerbehandlung bei Audio-Daten-Transkription"""
        service = LocalTranscriptionService()

        # Mock tempfile Fehler
        with patch('tempfile.NamedTemporaryFile', side_effect=Exception("Temp file error")):
            result = service.transcribe_audio_data(b'dummy', "audio.mp3")
            assert result is None

    def test_get_model_info(self, mock_whisper_model):
        """Test Modell-Info Abruf"""
        with patch('src.local_transcription.torch.cuda.is_available', return_value=True):
            service = LocalTranscriptionService()

            info = service.get_model_info()

            assert info["available"] is True
            assert info["model_size"] == config.WHISPER_MODEL_SIZE
            assert info["device"] == "cuda"
            assert info["compute_type"] == "float16"

    def test_get_model_info_no_cuda(self, mock_whisper_model):
        """Test Modell-Info ohne CUDA"""
        with patch('src.local_transcription.torch.cuda.is_available', return_value=False):
            service = LocalTranscriptionService()

            info = service.get_model_info()

            assert info["device"] == "cpu"
            assert info["compute_type"] == "int8"

    def test_get_model_info_unavailable(self):
        """Test Modell-Info wenn Modell nicht verfügbar"""
        service = LocalTranscriptionService()
        service.model = None  # Simuliere nicht verfügbares Modell

        info = service.get_model_info()

        assert info["available"] is False

    def test_validate_transcript(self, mock_whisper_model):
        """Test Transkript-Validierung"""
        service = LocalTranscriptionService()

        # Gültiges Transkript
        assert service._validate_transcript("Das ist ein Test.") is True

        # Leeres Transkript
        assert service._validate_transcript("") is False
        assert service._validate_transcript("   ") is False

    def test_validate_audio_file(self, test_wav_file, mock_whisper_model):
        """Test Audio-Datei-Validierung"""
        service = LocalTranscriptionService()

        if test_wav_file:
            # Gültige Datei
            assert service._validate_audio_file(test_wav_file) is True

        # Nicht existierende Datei
        assert service._validate_audio_file("nonexistent.wav") is False

        # Zu große Datei
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 30 * 1024 * 1024  # 30MB
                with patch('pathlib.Path.is_file', return_value=True):
                    assert service._validate_audio_file("large.wav") is False

    def test_supported_formats(self, mock_whisper_model):
        """Test unterstützte Audio-Formate"""
        service = LocalTranscriptionService()

        formats = service.get_supported_formats()

        expected_formats = ['wav', 'mp3', 'm4a', 'flac', 'ogg']
        assert formats == expected_formats

    def test_transcribe_with_whisper_error(self, test_wav_file, mock_whisper_model):
        """Test Transkription bei Whisper-Fehler"""
        if not test_wav_file:
            pytest.skip("Test-WAV-Datei nicht verfügbar")

        service = LocalTranscriptionService()

        # Mock Whisper-Fehler
        mock_whisper_model.transcribe.side_effect = Exception("Whisper error")

        result = service.transcribe(test_wav_file)

        assert result is None

    def test_device_detection(self, mock_whisper_model):
        """Test automatische Geräte-Erkennung"""
        service = LocalTranscriptionService()

        # Test CUDA verfügbar
        with patch('src.local_transcription.torch.cuda.is_available', return_value=True):
            service._load_model()
            # WhisperModel sollte mit cuda und float16 aufgerufen werden
            from src.local_transcription import WhisperModel
            WhisperModel.assert_called_with(
                config.WHISPER_MODEL_SIZE,
                device="cuda",
                compute_type="float16",
                download_root=str(config.get_temp_dir() / "whisper_models")
            )

        # Test CPU fallback
        with patch('src.local_transcription.torch.cuda.is_available', return_value=False):
            service._load_model()
            # WhisperModel sollte mit cpu und int8 aufgerufen werden
            WhisperModel.assert_called_with(
                config.WHISPER_MODEL_SIZE,
                device="cpu",
                compute_type="int8",
                download_root=str(config.get_temp_dir() / "whisper_models")
            )