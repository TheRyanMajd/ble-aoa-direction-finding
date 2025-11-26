#!/usr/bin/env python3
"""
Analyze AoA experiment data: CSV output from raw data (no trimming).
"""

import json
from pathlib import Path

import pandas as pd
import numpy as np


# ---------------------- parsing helpers ----------------------------

def parse_mqtt_txt_file(path: Path) -> pd.DataFrame:
    """
    Parse mosquitto_sub log .txt files and extract JSON angle packets.

    Expected columns:
        azimuth, azimuth_stdev,
        elevation, elevation_stdev,
        distance, distance_stdev,
        sequence
    """

    records = []
    collecting = False
    buf = []

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:

            # Detect start of JSON block
            if "{" in line and not collecting:
                collecting = True
                json_part = line[line.index("{"):]
                buf = [json_part]

                # One-line JSON block
                if "}" in json_part:
                    json_str = "".join(buf)
                    _add_record(json_str, records)
                    collecting = False
                    buf = []

            # Continue collecting multi-line JSON
            elif collecting:
                buf.append(line)
                if "}" in line:
                    json_str = "".join(buf)
                    _add_record(json_str, records)
                    collecting = False
                    buf = []

    if not records:
        raise ValueError(f"No JSON records parsed from {path}")

    df = pd.DataFrame(records)

    expected_cols = [
        "azimuth",
        "azimuth_stdev",
        "elevation",
        "elevation_stdev",
        "distance",
        "distance_stdev",
        "sequence",
    ]

    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Missing expected column '{col}' in {path}")

    df["sample_index"] = np.arange(len(df))

    # Ensure deterministic column ordering
    return df[expected_cols + ["sample_index"]]


def _add_record(json_str: str, records: list):
    """Safely parse JSON and append if valid."""
    try:
        records.append(json.loads(json_str))
    except json.JSONDecodeError:
        pass


# --------------------------- main -----------------------------------

def main():
    base_dir = Path(__file__).resolve().parent
    raw_dir = base_dir / "raw_data"
    out_dir = base_dir / "edited_data"
    out_dir.mkdir(exist_ok=True)

    summary_rows = []

    txt_files = sorted(raw_dir.glob("*.txt"))
    if not txt_files:
        print(f"No .txt files found in {raw_dir}")
        return

    print(f"Found {len(txt_files)} raw data files:")
    for f in txt_files:
        print(f"  - {f.name}")

    for path in txt_files:
        print(f"\nProcessing {path.name} ...")

        try:
            df = parse_mqtt_txt_file(path)
        except Exception as e:
            print(f"  !! Skipping {path.name}, parse error: {e}")
            continue

        # Save CSV (no trimming)
        cleaned_csv = out_dir / f"{path.stem}.csv"
        df.to_csv(cleaned_csv, index=False)
        print(f"  -> Saved CSV to {cleaned_csv}")

        # Add summary
        summary_rows.append({
            "file": path.name,
            "n_samples": len(df),
            "azimuth_mean": df["azimuth"].mean(),
            "azimuth_std": df["azimuth"].std(),
            "elevation_mean": df["elevation"].mean(),
            "elevation_std": df["elevation"].std(),
            "distance_mean": df["distance"].mean(),
            "distance_std": df["distance"].std(),
            "sequence_min": df["sequence"].min(),
            "sequence_max": df["sequence"].max(),
        })

    # Write summary CSV
    if summary_rows:
        summary_df = pd.DataFrame(summary_rows)
        summary_path = out_dir / "summary.csv"
        summary_df.to_csv(summary_path, index=False)
        print(f"\nSummary saved to {summary_path}")
    else:
        print("\nNo valid files processed")


if __name__ == "__main__":
    main()
