#!/usr/bin/env python3
"""
CLI script to train the AgriSathi crop model.
"""

import sys
from agrisathi.ml.train import train_and_evaluate


def main():
    print("=== AgriSathi Model Training ===")
    _, metrics = train_and_evaluate()
    print(f"Training succeeded with Test Accuracy: {metrics['accuracy'] * 100:.2f}%")
    sys.exit(0)


if __name__ == "__main__":
    main()
