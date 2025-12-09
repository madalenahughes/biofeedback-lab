#!/usr/bin/env python3
"""
session_stress_csv.py

Connects to Polar H10 via rmssd_z_stream(), logs RMSSD z-scores,
and computes a pre- and post-session "stress score" for a single run.

- "Pre" window = first BASELINE_SECONDS of the session
- "Post" window = last POST_WINDOW_SECONDS before you stop the script

Writes:
1) A per-sample log CSV:   logs/session_<timestamp>.csv
2) A summary CSV (append): stress_summary.csv
"""

import asyncio
import csv
import os
from datetime import datetime
from typing import List, Tuple

from polar_hrv import rmssd_z_stream  # you already have this


# ===== CONFIG =====
BASELINE_SECONDS = 120      # how long you consider "pre" at start
POST_WINDOW_SECONDS = 60    # how much of the end counts as "post"
SUMMARY_CSV = "stress_summary.csv"
LOG_DIR = "logs"

# Optional: put a subject/session label here or pass via CLI later if you want
SUBJECT_ID = "test_subject"
SESSION_LABEL = "music_biofeedback_1"


async def collect_session_data() -> Tuple[List[Tuple[float, float]], float, float]:
    """
    Collects RMSSD z-scores from rmssd_z_stream() until you Ctrl+C.

    Returns:
      - samples: list of (t_rel, z) tuples (time since start, z-score)
      - t_start: absolute UNIX timestamp when we started collecting
      - t_end:   absolute UNIX timestamp when we stopped
    """
    samples: List[Tuple[float, float]] = []

    print("\n[session] Connecting to Polar and starting HRV stream...")
    print("[session] First {:.0f}s will be treated as BASELINE (pre-stress window).".format(BASELINE_SECONDS))
    print("[session] Last  {:.0f}s before you stop will be treated as POST (post-stress window).".format(POST_WINDOW_SECONDS))
    print("[session] Press Ctrl+C when the audio is done / winding down.\n")

    t_start = None
    t_end = None

    try:
        async for sample in rmssd_z_stream():
            # Adapt this unpack if your rmssd_z_stream() yields a different shape
            # Example assumption: (timestamp, rr_ms, rmssd_ms, z_score)
            ts, rr_ms, rmssd_ms, z = sample

            if t_start is None:
                t_start = ts

            t_rel = ts - t_start  # seconds since start
            samples.append((t_rel, z))

            # Lightweight console print so you see it's alive
            print(f"[HRV] t={t_rel:6.1f}s  z={z:5.2f}")

    except KeyboardInterrupt:
        t_end = datetime.now().timestamp()
        print("\n[session] Stopped by user (Ctrl+C).")
    finally:
        if t_start is None:
            raise RuntimeError("No data collected from rmssd_z_stream().")

    if t_end is None:
        # Fallback if we didn't capture on KeyboardInterrupt
        t_end = t_start + (samples[-1][0] if samples else 0.0)

    return samples, t_start, t_end


def compute_pre_post(samples: List[Tuple[float, float]]):
    """
    Given all samples (t_rel, z), compute:
      - mean z over [0, BASELINE_SECONDS]  -> pre
      - mean z over last POST_WINDOW_SECONDS of session -> post

    Returns (pre_mean, post_mean, delta)
    """
    if not samples:
        raise ValueError("No samples to compute statistics on.")

    t_last = samples[-1][0]
    pre_window_end = BASELINE_SECONDS
    post_window_start = max(0.0, t_last - POST_WINDOW_SECONDS)

    pre_vals = [z for t, z in samples if t <= pre_window_end]
    post_vals = [z for t, z in samples if t >= post_window_start]

    if not pre_vals:
        raise ValueError("No pre-window samples collected. Increase BASELINE_SECONDS or run longer.")
    if not post_vals:
        raise ValueError("No post-window samples collected. Increase POST_WINDOW_SECONDS or run longer.")

    pre_mean = sum(pre_vals) / len(pre_vals)
    post_mean = sum(post_vals) / len(post_vals)
    delta = post_mean - pre_mean

    return pre_mean, post_mean, delta, t_last, len(pre_vals), len(post_vals)


def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def write_per_sample_log(samples: List[Tuple[float, float]], t_start: float, session_id: str) -> str:
    """
    Write detailed per-sample time series to logs/session_<session_id>.csv

    Returns path to the log CSV.
    """
    ensure_log_dir()
    filename = os.path.join(LOG_DIR, f"session_{session_id}.csv")
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["t_rel_sec", "z_score"])  # you can add more columns later
        for t_rel, z in samples:
            writer.writerow([f"{t_rel:.3f}", f"{z:.5f}"])
    return filename


def append_summary_row(session_id: str,
                       pre_mean: float,
                       post_mean: float,
                       delta: float,
                       t_last: float,
                       n_pre: int,
                       n_post: int,
                       t_start_iso: str):
    """
    Append a single summary row to stress_summary.csv
    """
    file_exists = os.path.exists(SUMMARY_CSV)
    with open(SUMMARY_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp_iso",
                "subject_id",
                "session_label",
                "session_id",
                "baseline_window_s",
                "post_window_s",
                "session_duration_s",
                "pre_mean_z",
                "post_mean_z",
                "delta_z",
                "n_pre_samples",
                "n_post_samples"
            ])
        writer.writerow([
            t_start_iso,
            SUBJECT_ID,
            SESSION_LABEL,
            session_id,
            BASELINE_SECONDS,
            POST_WINDOW_SECONDS,
            f"{t_last:.3f}",
            f"{pre_mean:.5f}",
            f"{post_mean:.5f}",
            f"{delta:.5f}",
            n_pre,
            n_post
        ])


async def main():
    # One session ID per run
    start_dt = datetime.now()
    session_id = start_dt.strftime("%Y%m%d_%H%M%S")
    t_start_iso = start_dt.isoformat(timespec="seconds")

    # 1) Collect HRV samples for this session
    samples, t_start, t_end = await collect_session_data()

    # 2) Compute pre/post statistics
    pre_mean, post_mean, delta, t_last, n_pre, n_post = compute_pre_post(samples)

    # "Stress score": if you want something that goes UP when stress goes UP,
    # you can define stress_score = -z (since higher z = higher RMSSD = more relaxed)
    pre_stress = -pre_mean
    post_stress = -post_mean
    delta_stress = post_stress - pre_stress

    print("\n===== SESSION SUMMARY =====")
    print(f"Subject:        {SUBJECT_ID}")
    print(f"Label:          {SESSION_LABEL}")
    print(f"Session ID:     {session_id}")
    print(f"Start (ISO):    {t_start_iso}")
    print(f"Duration:       {t_last:.1f} s")
    print(f"Pre window:     0 – {BASELINE_SECONDS:.0f} s   (n={n_pre})")
    print(f"Post window:    last {POST_WINDOW_SECONDS:.0f} s  (n={n_post})")
    print("")
    print(f"Pre  mean z:    {pre_mean:6.3f}")
    print(f"Post mean z:    {post_mean:6.3f}")
    print(f"Δz (post-pre):  {delta:6.3f}")
    print("")
    print(f"Pre  stress:    {pre_stress:6.3f}  (defined as -z)")
    print(f"Post stress:    {post_stress:6.3f}")
    print(f"Δstress:        {delta_stress:6.3f}  (positive = more stressed)\n")

    # 3) Write raw per-sample log
    per_sample_path = write_per_sample_log(samples, t_start, session_id)
    print(f"[session] Per-sample log written to: {per_sample_path}")

    # 4) Append summary row
    append_summary_row(
        session_id,
        pre_mean,
        post_mean,
        delta,
        t_last,
        n_pre,
        n_post,
        t_start_iso,
    )
    print(f"[session] Summary appended to: {SUMMARY_CSV}")
    print("\nYou can now open 'stress_summary.csv' in Sheets/Excel and get one row per run.")


if __name__ == "__main__":
    asyncio.run(main())

