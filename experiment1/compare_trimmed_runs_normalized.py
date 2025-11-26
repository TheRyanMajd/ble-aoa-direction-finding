# compare_trimmed_runs_normalized.py
#
# Run this from experiment1/ AFTER you've generated edited_data/*.csv.
# It:
#   - trims each run by MANUAL_RANGES (sequence-based)
#   - creates a normalized progress axis:
#         progress = (sequence - start_seq) / (end_seq - start_seq)
#     so every run spans x in [0, 1]
#   - produces combined plots for:
#       * inhand:   a, b, c overlaid
#       * inpocket: a, b, c overlaid
#   - outputs:
#       plots_trimmed/inhand_all_*.png
#       plots_trimmed/inpocket_all_*.png
#
# This DOES NOT modify any CSVs; it only reads from edited_data and writes plots.

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Use the same sequence ranges you used for trimming
MANUAL_RANGES = {
    "inhand_a":   (2457, 3050),
    "inhand_b":   (3787, 4361),
    "inhand_c":   (4900, 5450),
    "inpocket_a": (8210, 8780),
    "inpocket_b": (9233, 9787),
    "inpocket_c": (10750, 11287),
}

# Color mapping per trial letter
COLORS = {
    "a": "green",
    "b": "purple",
    "c": "orange",
}


def load_and_normalize():
    """
    Load edited_data/*.csv, trim by MANUAL_RANGES, and create a normalized
    'progress' axis in [0, 1] for each run.

    Returns:
        dict:
            {
              "inhand": {
                  "a": DataFrame(...),
                  "b": DataFrame(...),
                  "c": DataFrame(...),
              },
              "inpocket": { ... }
            }
        where each DataFrame has columns:
            ["progress", "sequence", "azimuth", "elevation", "distance"]
    """
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "edited_data"
    csv_files = sorted(data_dir.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {data_dir}")
        return {}

    grouped = {"inhand": {}, "inpocket": {}}

    for csv_path in csv_files:
        df = pd.read_csv(csv_path)

        required = {"azimuth", "elevation", "distance", "sequence"}
        if not required.issubset(df.columns):
            print(
                f"Skipping {csv_path.name}: "
                f"missing {required - set(df.columns)}"
            )
            continue

        stem = csv_path.stem           # e.g. "inhand_a_cleaned"
        base = stem.replace("_cleaned", "")  # e.g. "inhand_a"

        if base not in MANUAL_RANGES:
            print(f"{stem}: base '{base}' not in MANUAL_RANGES, skipping.")
            continue

        start_seq, end_seq = MANUAL_RANGES[base]
        seq = df["sequence"]
        mask = (seq >= start_seq) & (seq <= end_seq)
        if not mask.any():
            print(f"{stem}: no samples in range {start_seq}-{end_seq}, skipping.")
            continue

        trimmed = df.loc[mask].copy()

        # Normalized progress in [0, 1]
        denom = float(end_seq - start_seq)
        if denom <= 0:
            print(
                f"{stem}: invalid MANUAL_RANGES ({start_seq}, {end_seq}), skipping.")
            continue

        progress = (trimmed["sequence"] - start_seq) / denom
        trimmed["progress"] = progress

        # Decide group: "inhand" or "inpocket"
        if base.startswith("inhand_"):
            group = "inhand"
        elif base.startswith("inpocket_"):
            group = "inpocket"
        else:
            print(f"{stem}: base '{base}' not in inhand/inpocket, skipping.")
            continue

        # trial letter: a/b/c
        letter = base.split("_")[-1]
        if letter not in {"a", "b", "c"}:
            print(f"{stem}: unexpected trial suffix '{letter}', skipping.")
            continue

        grouped[group][letter] = trimmed[[
            "progress",
            "sequence",
            "azimuth",
            "elevation",
            "distance",
        ]]

        print(
            f"Loaded {stem} as {group}/{letter}, "
            f"{len(trimmed)} samples in [{start_seq}, {end_seq}]"
        )

    return grouped


def plot_group(group_name, runs, out_dir):
    """
    group_name: "inhand" or "inpocket"
    runs: dict { "a": df, "b": df, "c": df }
    """
    if not runs:
        print(f"No runs for group {group_name}, skipping plots.")
        return

    # ---------- Azimuth vs normalized progress ----------
    plt.figure()
    for letter, df in sorted(runs.items()):
        c = COLORS.get(letter, "black")
        plt.plot(df["progress"], df["azimuth"], color=c,
                 label=f"{group_name}_{letter}")
    plt.title(f"{group_name} - Azimuth vs Normalized Walk Progress")
    plt.xlabel("Normalized progress (0 = start, 1 = end)")
    plt.ylabel("Azimuth (deg)")
    plt.ylim(180, -180)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"{group_name}_all_azimuth_norm.png")
    plt.close()

    # ---------- Elevation vs normalized progress ----------
    plt.figure()
    for letter, df in sorted(runs.items()):
        c = COLORS.get(letter, "black")
        plt.plot(df["progress"], df["elevation"],
                 color=c, label=f"{group_name}_{letter}")
    plt.title(f"{group_name} - Elevation vs Normalized Walk Progress")
    plt.xlabel("Normalized progress (0 = start, 1 = end)")
    plt.ylabel("Elevation (deg)")
    plt.ylim(180, -180)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"{group_name}_all_elevation_norm.png")
    plt.close()

    # ---------- Distance vs normalized progress ----------
    plt.figure()
    for letter, df in sorted(runs.items()):
        c = COLORS.get(letter, "black")
        plt.plot(df["progress"], df["distance"],
                 color=c, label=f"{group_name}_{letter}")
    plt.title(f"{group_name} - Estimated Distance vs Normalized Walk Progress")
    plt.xlabel("Normalized progress (0 = start, 1 = end)")
    plt.ylabel("Est. Distance (m)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"{group_name}_all_distance_norm.png")
    plt.close()

    # ---------- Polar: Distance vs Azimuth (no progress axis, just overlay) ----------
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="polar")
    ax.set_theta_zero_location("N")   # 0° at top
    ax.set_theta_direction(-1)        # clockwise positive

    for letter, df in sorted(runs.items()):
        c = COLORS.get(letter, "black")
        theta = np.deg2rad(df["azimuth"].to_numpy())
        r = df["distance"].to_numpy()
        ax.plot(theta, r, ".", color=c, markersize=3,
                label=f"{group_name}_{letter}")

    ax.set_title(
        f"{group_name} - Polar Distance vs Azimuth (all trials, trimmed)",
        va="bottom",
    )
    ax.set_rlabel_position(135)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1))
    plt.tight_layout()
    plt.savefig(out_dir / f"{group_name}_all_polar.png")
    plt.close()


def main():
    base_dir = Path(__file__).resolve().parent
    out_dir = base_dir / "plots_trimmed"
    out_dir.mkdir(exist_ok=True)

    grouped = load_and_normalize()
    if not grouped:
        return

    for group_name in ["inhand", "inpocket"]:
        runs = grouped.get(group_name, {})
        plot_group(group_name, runs, out_dir)


if __name__ == "__main__":
    main()
