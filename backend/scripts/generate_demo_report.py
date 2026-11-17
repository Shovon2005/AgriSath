#!/usr/bin/env python3
"""
CLI script to generate a sample PDF Agronomic Advisory Report to disk.
"""

from pathlib import Path
from agrisathi.advisory.engine import run_full_pipeline
from agrisathi.reports.pdf_generator import generate_pdf_advisory_report
from agrisathi.data.scenarios import get_scenario_parameters_map


def main():
    print("=== Generating Sample PDF Advisory Report ===")
    scenarios = get_scenario_parameters_map()
    sample_payload = scenarios.get("rice", {})

    _, prediction, advisory = run_full_pipeline(sample_payload)
    pdf_bytes = generate_pdf_advisory_report(prediction, advisory)

    out_file = Path("demo_advisory_report.pdf")
    with open(out_file, "wb") as f:
        f.write(pdf_bytes)

    print(f"Report generated successfully: {out_file.resolve()} ({len(pdf_bytes)} bytes)")


if __name__ == "__main__":
    main()
