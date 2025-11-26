# analyze_experiment1_trimmed_polar.py
#
# Use this inside experiment1/ after generating edited_data/*.csv.
# It trims each run by MANUAL_RANGES and generates:
#   - Azimuth vs Sequence   (red)
#   - Elevation vs Sequence (red)
#   - Distance vs Sequence  (red)
#   - Polar plot: Distance vs Azimuth (trimmed)

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# TODO: fill these with the sequence ranges you want to keep
# for each trial, based on the cleaned plots.
#   "file_stem": (start_sequence, end_sequence),
MANUAL_RANGES = {
    "inhand_a":   (2457, 3050),
    "inhand_b":   (3787, 4361),
    "inhand_c":   (4900, 5450),
    "inpocket_a": (8210, 8780),
    "inpocket_b": (9233, 9787),
    "inpocket_c": (10750, 11287),
}


def main():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "edited_data"
    out_dir = base_dir / "plots_trimmed"
    out_dir.mkdir(exist_ok=True)

    csv_files = sorted(data_dir.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {data_dir}")
        return

    for csv_path in csv_files:
        df = pd.read_csv(csv_path)

        required = {"azimuth", "elevation", "distance", "sequence"}
        if not required.issubset(df.columns):
            print(
                f"Skipping {csv_path.name}: missing {required - set(df.columns)}")
            continue

        stem = csv_path.stem
        if stem not in MANUAL_RANGES:
            print(f"{stem}: no MANUAL_RANGES entry, skipping trim.")
            continue

        # Raw columns
        seq = df["sequence"]
        az = df["azimuth"]
        el = df["elevation"]
        dist = df["distance"]

        start_seq, end_seq = MANUAL_RANGES[stem]
        mask = (seq >= start_seq) & (seq <= end_seq)
        if not mask.any():
            print(f"{stem}: no samples in range {start_seq}-{end_seq}, skipping.")
            continue

        seq_t = seq[mask]
        az_t = az[mask]
        el_t = el[mask]
        dist_t = dist[mask]

        # ---------- Azimuth vs Sequence ----------
        plt.figure()
        plt.plot(seq_t, az_t, "r-")
        plt.title(f"{stem} - Azimuth vs Sequence (trimmed)")
        plt.xlabel("Sequence (50Hz)")
        plt.ylabel("Azimuth (deg)")
        plt.ylim(180, -180)  # 180 at top, -180 at bottom
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(out_dir / f"{stem}_azimuth_trimmed.png")
        plt.close()

        # ---------- Elevation vs Sequence ----------
        plt.figure()
        plt.plot(seq_t, el_t, "r-")
        plt.title(f"{stem} - Elevation vs Sequence (trimmed)")
        plt.xlabel("Sequence (50Hz)")
        plt.ylabel("Elevation (deg)")
        plt.ylim(180, -180)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(out_dir / f"{stem}_elevation_trimmed.png")
        plt.close()

        # ---------- Distance vs Sequence ----------
        plt.figure()
        plt.plot(seq_t, dist_t, "r-")
        plt.title(f"{stem} - Distance vs Sequence (trimmed)")
        plt.xlabel("Sequence (50Hz)")
        plt.ylabel("Est. Distance (m)")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(out_dir / f"{stem}_distance_trimmed.png")
        plt.close()

        # ---------- Polar: Distance vs Azimuth ----------
        # Convert azimuth (deg) → radians for polar plot.
        theta = np.deg2rad(az_t.to_numpy())
        r = dist_t.to_numpy()

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="polar")
        # Optional: set 0° at "front" and clockwise direction
        ax.set_theta_zero_location("N")   # 0° = north/up
        ax.set_theta_direction(-1)        # clockwise positive
        ax.plot(theta, r, "r.", markersize=3)
        ax.set_title(
            f"{stem} - Polar Distance vs Azimuth (trimmed)", va="bottom")
        ax.set_rlabel_position(135)  # move radial labels out of the main lobe
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(out_dir / f"{stem}_polar_distance_azimuth_trimmed.png")
        plt.close()

        print(
            f"{stem}: trimmed to {len(seq_t)} samples in "
            f"sequence [{start_seq}, {end_seq}]"
        )


if __name__ == "__main__":
    main()
