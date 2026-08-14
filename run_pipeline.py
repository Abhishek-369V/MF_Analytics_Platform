"""
Master Pipeline Script — Bluestock MF Analytics Platform
Runs the full ETL sequence: ingestion -> live NAV fetch -> cleaning -> DB setup.
Usage: python run_pipeline.py
"""

import subprocess
import sys

STEPS = [
    ("Data Ingestion", "data_ingestion.py"),
    ("Live NAV Fetch", "fetch_live_nav.py"),
    ("Data Cleaning", "data_cleaning.py"),
    ("Database Setup", "database_setup.py"),
]


def run_pipeline() -> None:
    for step_name, script in STEPS:
        print("\n" + "=" * 60)
        print(f"RUNNING: {step_name} ({script})")
        print("=" * 60)
        result = subprocess.run([sys.executable, script])
        if result.returncode != 0:
            print(f"\nPipeline stopped: {step_name} failed.")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE — all steps ran successfully.")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()