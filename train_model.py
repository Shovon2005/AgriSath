"""
Backward-compatible training script.
Delegates to agrisathi.ml.train.
"""

from agrisathi.ml.train import train_and_evaluate


if __name__ == "__main__":
    train_and_evaluate()
