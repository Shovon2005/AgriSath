"""
Backward-compatibility root bridge for model training script.
Delegates to backend.train_model.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from backend.train_model import train_and_evaluate

if __name__ == "__main__":
    train_and_evaluate()
