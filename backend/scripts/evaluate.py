#!/usr/bin/env python3
"""
CLI script to evaluate current model performance and print classification metrics.
"""

import json
from agrisathi.config import Config


def main():
    print("=== AgriSathi Model Evaluation Report ===")
    if not Config.MODEL_METRICS_PATH.exists():
        print(f"Metrics file not found at {Config.MODEL_METRICS_PATH}. Please train the model first.")
        return

    with open(Config.MODEL_METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    print(f"Overall Test Accuracy: {metrics.get('accuracy', 0) * 100:.2f}%")
    print(f"Total Samples: {metrics.get('sample_count')}")
    print(f"Classes Count: {metrics.get('n_classes')}")
    print("\nSupported Crops:")
    print(", ".join(metrics.get("classes", [])))


if __name__ == "__main__":
    main()
