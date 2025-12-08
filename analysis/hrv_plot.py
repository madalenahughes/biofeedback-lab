#!/usr/bin/env python3
"""
hrv_plot.py

Quick HRV (RMSSD) vs time plotter for session CSVs.

Usage:
    python3 hrv_plot.py path/to/session_YYYYMMDD_HHMMSS.csv
    # or compare multiple sessions:
    python3 hrv_plot.py session1.csv session2.csv
"""

import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def load_session(csv_path: Path) -> pd.DataFrame:
    """Load a session CSV and do minimal cleanup."""
    df = pd.read_csv(csv_path)

    if df.empty:
        raise ValueError(f"{csv_path} appears to be empty.")

    # Try to find a time column automatically.
    # You can hardcode this if you know the exact name.
    time_col = None
    for candidate in df.columns:
        name = candidate.lower()
        if "time" in name or name in ("t", "timestamp", "ts"):
            time_col = candidate
            break

    if time_col is None:
        # Fall back to using sample index as "time"
        df["time_s"] = (df.index - df.index[0]).astype(float)
        time_col = "time_s"

    # Make a "t_rel" column: time relative to start (seconds)
    df["t_rel_s"] = df[time_col] - df[time_col].iloc[0]

    return df


def plot_hrv_sessions(csv_paths):
    """Plot RMSSD vs time for one or more session CSVs."""
    plt.figure()
    for csv_path in csv_paths:
        path = Path(csv_path)
        df = load_session(path)

        # 🔹 Adjust these names if your columns are different:
        # Try to find an HRV-ish column
        hrv_col = None
        for candidate in df.columns:
            name = candidate.lower()
            if "rmssd" in name or "hrv" in name:
                hrv_col = candidate
                break

        if hrv_col is None:
            raise ValueError(
                f"Could not find an HRV/RMSSD column in {path}. "
                f"Columns are: {list(df.columns)}"
            )

        t = df["t_rel_s"] / 60.0  # convert seconds → minutes for nicer x-axis
        hrv = df[hrv_col]

        label = path.stem  # filename without extension
        plt.plot(t, hrv, label=label)

    plt.xlabel("Time (minutes)")
    plt.ylabel("HRV (e.g., RMSSD, ms)")
    plt.title("HRV vs Time")
    plt.grid(True)
    if len(csv_paths) > 1:
        plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 hrv_plot.py session1.csv [session2.csv ...]")
        sys.exit(1)

    csv_paths = sys.argv[1:]
    plot_hrv_sessions(csv_paths)


if __name__ == "__main__":
    main()

