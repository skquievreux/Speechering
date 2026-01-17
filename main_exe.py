import sys
import os
from pathlib import Path

# Füge src zum Python-Pfad hinzu (für Development/non-frozen Mode)
# In der EXE (frozen) fügt PyInstaller den Pfad automatisch hinzu
if not getattr(sys, 'frozen', False):
    sys.path.append(os.path.abspath("src"))

try:
    from src.main import main
except ImportError:
    # Fallback falls src nicht importiert werden kann (z.B. falsches CWD)
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
    from main import main

if __name__ == "__main__":
    main()
