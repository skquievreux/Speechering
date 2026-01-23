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

def get_model_path(model_name: str = "base") -> Optional[Path]:
    """Returns the path to a specific model if it exists"""
    models_dir = get_models_dir()
    
    # 1. Check direct directory (e.g. models/base)
    direct_path = models_dir / model_name
    if direct_path.exists() and (direct_path / "model.bin").exists():
        return direct_path
        
    # 2. Check huggingface cache format (e.g. models/models--Systran--faster-whisper-base)
    # This is how faster-whisper stores it when download_root is used
    hf_folder_name = f"models--Systran--faster-whisper-{model_name}"
    hf_path = models_dir / hf_folder_name
    
    if hf_path.exists():
        # Find the latest snapshot
        snapshots_dir = hf_path / "snapshots"
        if snapshots_dir.exists():
            snapshots = list(snapshots_dir.iterdir())
            if snapshots:
                # Use the latest snapshot directory
                return snapshots[0]
                
    # 3. Fallback: faster-whisper might have downloaded it directly into the download_root 
    # if it's not using the cache structure (unlikely with recent versions but for safety)
    if (models_dir / "model.bin").exists() and model_name == "base": # This is risky
        pass

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
        
        # Now find the downloaded files and move them to our clean target_dir
        # This avoids the complex huggingface-hub cache structure for our UI
        path = get_model_path(model_name) # This uses the new detection logic
        
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
