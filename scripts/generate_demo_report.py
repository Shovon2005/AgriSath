#!/usr/bin/env python3
"""
CLI script to generate a sample PDF Agronomic Advisory Report to disk.
"""

from pathlib import Path
from agrisathi.core.validator import validate_farm_input
from agrisathi.ml.predictor import get_predictor
from agrisathi.advisory.engine import generate_full_advisory
from agrisathi.reports.pdf_generator import generate_pdf_advisory_report
from agrisathi.data.scenarios import get_scenario_parameters_map


def main():
    print("=== Generating Sample PDF Advisory Report ===")
    scenarios = get_scenario_parameters_map()
    sample_payload = scenarios.get("rice", {})

    sanitized = validate_farm_input(sample_payload)
    predictor = get_predictor()
    prediction = predictor.predict(sanitized)
    advisory = generate_full_advisory(sanitized, prediction["recommended_crop"])

    pdf_bytes = generate_pdf_advisory_report(prediction, advisory)

    out_file = Path("demo_advisory_report.pdf")
    with open(out_file, "wb") as f:
        f.write(pdf_bytes)

    print(f"Report generated successfully: {out_file.resolve()} ({len(pdf_bytes)} bytes)")


if __name__ == "__main__":
    main()
