"""
Resource management for Voice Transcriber.
Handles path resolution for bundled assets and files.
"""

import sys
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_resource_path(relative_path: str) -> Path:
    """
    Resolves resource paths for both development and frozen mode (PyInstaller).
    
    Args:
        relative_path: Path relative to the project root (e.g., 'assets/icon.ico')
    """
    try:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # PyInstaller extracts data to a temp folder and stores the path in _MEIPASS
            base_path = Path(sys._MEIPASS)
        else:
            # Development mode: resolve relative to project root
            # This works if script is run from project root or via module
            base_path = Path(__file__).parent.parent

        resolved_path = base_path / relative_path
        
        # Verbose logging for debugging path issues in production
        if getattr(sys, 'frozen', False):
            if resolved_path.exists():
                logger.debug(f"Resource found: {relative_path} -> {resolved_path}")
            else:
                logger.warning(f"Resource NOT found: {relative_path} -> {resolved_path}")
        
        return resolved_path
    except Exception as e:
        logger.error(f"Error resolving resource path for {relative_path}: {e}")
        return Path(relative_path)
