"""
Integration-Tests für den vollständigen Audio-zu-Text Workflow
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.audio_recorder import AudioRecorder
from src.config import config
from src.transcription import TranscriptionService


class TestAudioToTextWorkflow:
    """Integration-Tests für den kompletten Workflow"""

    @pytest.fixture
    def test_wav_file(self):
        """Stellt eine Test-WAV-Datei bereit"""
        test_file = Path(__file__).parent / "test_data" / "audio" / "speech_like_2s.wav"
        if test_file.exists():
            return str(test_file)
        return None

    @pytest.fixture
    def mock_openai_client(self):
        """Mock für OpenAI Client"""
        with patch('src.transcription.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            # Mock die transcribe Methode
            mock_response = MagicMock()
            mock_response.transcriptions.create.return_value = "Das ist ein Test-Transkript."
            mock_client.audio.transcriptions.create = mock_response.transcriptions.create

            yield mock_client

    def test_full_compression_workflow(self, test_wav_file, mock_openai_client):
        """Test vollständiger Workflow: Komprimierung + Transkription"""
        if not test_wav_file:
            pytest.skip("Test-WAV-Datei nicht verfügbar")

        # Erstelle AudioRecorder
        recorder = AudioRecorder()

        try:
            # Schritt 1: Audio komprimieren
            compressed_data = recorder.compress_audio(test_wav_file)

            assert isinstance(compressed_data, bytes)
            assert len(compressed_data) > 0

            # Schritt 2: Komprimierte Daten transkribieren
            transcription_service = TranscriptionService()
            result = transcription_service.transcribe_audio_data(compressed_data, "audio.mp3")

            assert isinstance(result, str)
            assert len(result) > 0

            # Prüfe dass OpenAI API mit korrekten Parametern aufgerufen wurde
            mock_openai_client.audio.transcriptions.create.assert_called_once()
            call_args = mock_openai_client.audio.transcriptions.create.call_args

            # Prüfe Parameter
            assert call_args[1]['model'] == 'whisper-1'
            assert call_args[1]['language'] == 'de'
            assert call_args[1]['response_format'] == 'text'

            # Prüfe dass file-Objekt übergeben wurde
            file_obj = call_args[1]['file']
            assert hasattr(file_obj, 'name')
            assert file_obj.name == "audio.mp3"

        finally:
            recorder.cleanup()

    def test_compression_disabled_workflow(self, test_wav_file, mock_openai_client):
        """Test Workflow wenn Komprimierung deaktiviert ist"""
        if not test_wav_file:
            pytest.skip("Test-WAV-Datei nicht verfügbar")

        recorder = AudioRecorder()

        try:
            # Komprimierung deaktivieren
            with patch('src.config.config.AUDIO_COMPRESSION_ENABLED', False):
                # Mock record_audio um Test-Datei zurückzugeben
                with patch.object(recorder, 'record_audio', return_value=test_wav_file):
                    result = recorder.record_and_compress()

                    # Sollte Rohdaten zurückgeben
                    assert result is not None
                    assert isinstance(result, bytes)

        finally:
            recorder.cleanup()

    def test_compression_error_fallback(self, test_wav_file, mock_openai_client):
        """Test Fallback bei Komprimierungsfehlern"""
        if not test_wav_file:
            pytest.skip("Test-WAV-Datei nicht verfügbar")

        recorder = AudioRecorder()

        try:
            # Mock compress_audio um Exception zu werfen
            with patch.object(recorder, 'compress_audio', side_effect=Exception("Komprimierung fehlgeschlagen")):
                with patch.object(recorder, 'record_audio', return_value=test_wav_file):
                    with patch('builtins.open', MagicMock()) as mock_open:
                        mock_file = MagicMock()
                        mock_file.read.return_value = b'fallback_data'
                        mock_open.return_value.__enter__.return_value = mock_file

                        result = recorder.record_and_compress()

                        # Sollte Fallback-Daten zurückgeben
                        assert result == b'fallback_data'

        finally:
            recorder.cleanup()

    def test_different_audio_formats(self, mock_openai_client):
        """Test verschiedene Audio-Formate in Transkription"""
        transcription_service = TranscriptionService()

        test_data = b'dummy_audio_data'

        # Test verschiedene Dateinamen/Formate
        formats = ['audio.mp3', 'audio.wav', 'audio.m4a', 'audio.ogg']

        for filename in formats:
            result = transcription_service.transcribe_audio_data(test_data, filename)

            assert isinstance(result, str)
            assert len(result) > 0

            # Prüfe dass der Dateiname korrekt gesetzt wurde
            call_args = mock_openai_client.audio.transcriptions.create.call_args
            file_obj = call_args[1]['file']
            assert file_obj.name == filename

    def test_transcription_error_handling(self, mock_openai_client):
        """Test Fehlerbehandlung bei Transkription"""
        transcription_service = TranscriptionService()

        # Mock API-Fehler
        mock_openai_client.audio.transcriptions.create.side_effect = Exception("API Error")

        test_data = b'dummy_audio_data'

        result = transcription_service.transcribe_audio_data(test_data, "audio.mp3")

        # Sollte None zurückgeben bei Fehler
        assert result is None

    def test_workflow_performance(self, test_wav_file, mock_openai_client):
        """Test Performance-Aspekte des Workflows"""
        if not test_wav_file:
            pytest.skip("Test-WAV-Datei nicht verfügbar")

        recorder = AudioRecorder()

        try:
            import time

            # Messe Komprimierungszeit
            start_time = time.time()
            compressed_data = recorder.compress_audio(test_wav_file)
            compression_time = time.time() - start_time

            # Komprimierung sollte schnell sein (< 1 Sekunde für kleine Dateien)
            assert compression_time < 1.0

            # Komprimierte Datei sollte signifikant kleiner sein (nur wenn pydub verfügbar)
            original_size = Path(test_wav_file).stat().st_size
            compression_ratio = len(compressed_data) / original_size

            # Import pydub availability check
            try:
                from src.audio_recorder import PYDUB_AVAILABLE
                if PYDUB_AVAILABLE:
                    # Erwarte mindestens 50% Größenreduktion
                    assert compression_ratio < 0.5
                else:
                    # Bei fehlendem pydub sollte Ratio 1.0 sein
                    assert compression_ratio == 1.0
            except ImportError:
                # Fallback: Bei fehlendem pydub sollte Ratio 1.0 sein
                assert compression_ratio == 1.0

        finally:
            recorder.cleanup()

    def test_memory_efficiency(self, test_wav_file):
        """Test Speichereffizienz bei großen Dateien"""
        if not test_wav_file:
            pytest.skip("Test-WAV-Datei nicht verfügbar")

        recorder = AudioRecorder()

        try:
            # Test mit größerer Datei
            large_test_file = Path(__file__).parent / "test_data" / "audio" / "long_tone_5s.wav"
            if large_test_file.exists():
                compressed_data = recorder.compress_audio(str(large_test_file))

                # Komprimierte Daten sollten in Speicher passen
                assert len(compressed_data) < 1024 * 1024  # < 1MB

                # Berechne Komprimierungsrate
                original_size = large_test_file.stat().st_size
                ratio = len(compressed_data) / original_size
                print(".1%")

        finally:
            recorder.cleanup()