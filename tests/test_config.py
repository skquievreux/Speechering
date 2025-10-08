"""
Tests für config.py
"""

import pytest
import os
from unittest.mock import patch
from src.config import Config, load_config

class TestConfig:
    """Test-Klasse für Config"""

    def test_config_initialization(self):
        """Test Config-Initialisierung"""
        config = Config()

        assert hasattr(config, 'OPENAI_API_KEY')
        assert hasattr(config, 'MAX_RECORDING_DURATION')
        assert config.MAX_RECORDING_DURATION == 30

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_config_with_env_vars(self):
        """Test Config mit Environment-Variablen"""
        config = Config()

        assert config.OPENAI_API_KEY == 'test-key'

    def test_config_validation_valid(self):
        """Test gültige Konfiguration"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            config = Config()
            assert config.validate() == True

    def test_config_validation_invalid(self):
        """Test ungültige Konfiguration"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
            config = Config()
            assert config.validate() == False

    def test_get_temp_dir(self):
        """Test temporäres Verzeichnis"""
        config = Config()
        temp_dir = config.get_temp_dir()

        assert temp_dir.exists()
        assert temp_dir.is_dir()

    def test_get_log_level(self):
        """Test Log-Level Konvertierung"""
        config = Config()

        assert config.get_log_level() == 20  # INFO