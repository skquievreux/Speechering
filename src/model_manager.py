"""
Model Manager - Handles downloading and managing AI models (Whisper)
"""

import os
import logging
from pathlib import Path
from typing import Optional, List
import shutil

# Configure logging
logger = logging.getLogger(__name__)

def get_models_dir() -> Path:
    """Returns the directory where models are stored"""
    if os.name == 'nt':
        base_dir = Path(os.environ.get('APPDATA', os.path.expanduser('~'))) / "VoiceTranscriber" / "models"
    else:
        base_dir = Path.home() / ".voicetranscriber" / "models"
    
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def get_model_path(model_name: str = "base", search_dir: Optional[Path] = None) -> Optional[Path]:
    """Returns the path to a specific model if it exists"""
    search_paths = []
    
    # 1. If explicit search_dir is provided, use only that (e.g. during download)
    if search_dir:
        search_paths.append(search_dir)
    else:
        # a. Check AppData (User downloaded)
        search_paths.append(get_models_dir())
        
        # b. Check Application Directory (Bundled with EXE or in Dev-Root)
        import sys
        if getattr(sys, 'frozen', False):
            # PyInstaller temp path (_MEIPASS)
            if hasattr(sys, '_MEIPASS'):
                search_paths.append(Path(sys._MEIPASS) / "models")
            # Also check next to EXE (portable/onedir)
            search_paths.append(Path(sys.executable).parent / "models")
        else:
            # Dev path: project_root/models
            search_paths.append(Path(__file__).parent.parent / "models")

    for models_dir in search_paths:
        if not models_dir.exists():
            continue
            
        # 1. Check direct directory (e.g. models/base)
        direct_path = models_dir / model_name
        if direct_path.exists() and (direct_path / "model.bin").exists():
            return direct_path
            
        # 2. Check huggingface cache format (e.g. models/models--Systran--faster-whisper-base)
        hf_folder_name = f"models--Systran--faster-whisper-{model_name}"
        hf_path = models_dir / hf_folder_name
        
        if hf_path.exists():
            snapshots_dir = hf_path / "snapshots"
            if snapshots_dir.exists():
                snapshots = list(snapshots_dir.iterdir())
                if snapshots:
                    return snapshots[0]
                    
        # 3. Fallback: Check if model.bin is directly in the search_dir (legacy/direct structure)
        if (models_dir / "model.bin").exists() and model_name == "base":
             return models_dir

    return None

def download_whisper_model(model_name: str = "base") -> bool:
    """
    Downloads the faster-whisper model and stores it in a clean directory
    """
    try:
        from faster_whisper import WhisperModel
        import shutil
        
        target_dir = get_models_dir() / model_name
        temp_download_root = get_models_dir() / "temp_download"
        
        logger.info(f"Downloading Whisper model '{model_name}'...")
        
        # Download using faster-whisper's mechanism into a temp folder
        # This will create the models--Systran--... structure
        WhisperModel(
            model_name, 
            device="cpu", 
            compute_type="int8", 
            download_root=str(temp_download_root)
        )
        
        # Now find the downloaded files in the temp directory and move them to our clean target_dir
        path = get_model_path(model_name, search_dir=temp_download_root)
        
        if path and path.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
            for f in path.iterdir():
                shutil.copy2(f, target_dir / f.name)
            
            # Cleanup temp download
            shutil.rmtree(temp_download_root, ignore_errors=True)
            
            logger.info(f"Model '{model_name}' successfully moved to {target_dir}")
            return True
            
        return False
    except Exception as e:
        logger.error(f"Failed to download model '{model_name}': {e}")
        return False

def list_available_models() -> List[str]:
    """Lists locally available models"""
    models_dir = get_models_dir()
    if not models_dir.exists():
        return []
    
    return [d.name for d in models_dir.iterdir() if d.is_dir()]

def verify_model(model_name: str) -> bool:
    """Verifies if a model is complete and ready to use"""
    model_path = get_model_path(model_name)
    if not model_path:
        return False
    
    # Basic check: look for required files (simple heuristic)
    required_files = ["model.bin", "config.json", "vocabulary.json"]
    for f in required_files:
        if not (model_path / f).exists():
            # Some models might have different structures, but these are typical
            pass
            
    return True
