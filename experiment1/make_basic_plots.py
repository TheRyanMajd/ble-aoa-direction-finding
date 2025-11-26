from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

"""
Creates the plots for visualizing the experiment data. Does not trim. 
"""


def main():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "edited_data"
    out_dir = base_dir / "plots_basic"
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
        seq = df["sequence"]
        az = df["azimuth"]
        el = df["elevation"]
        dist = df["distance"]

        # Azimuth
        plt.figure()
        plt.plot(seq, az, "b-")
        plt.title(f"{stem} - Azimuth vs Sequence")
        plt.xlabel("Sequence (50Hz)")
        plt.ylabel("Azimuth (deg)")
        plt.ylim(180, -180)   # 180 at top, -180 at bottom
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(out_dir / f"{stem}_azimuth.png")
        plt.close()

        # Elevation
        plt.figure()
        plt.plot(seq, el, "b-")
        plt.title(f"{stem} - Elevation vs Sequence")
        plt.xlabel("Sequence (50Hz)")
        plt.ylabel("Elevation (deg)")
        plt.ylim(180, -180)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(out_dir / f"{stem}_elevation.png")
        plt.close()

        # Distance
        plt.figure()
        plt.plot(seq, dist, "b-")
        plt.title(f"{stem} - Distance vs Sequence")
        plt.xlabel("Sequence (50Hz)")
        plt.ylabel("Est. Distance (m)")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(out_dir / f"{stem}_distance.png")
        plt.close()

        print(f"Basic plots written for {csv_path.name}")


if __name__ == "__main__":
    main()
