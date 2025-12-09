#!/usr/bin/env python3
"""
music_harness.py

Sensor-free harness that:
  - generates fake rmssd_z + FAA (demo or manual)
  - runs them through update_audio_parameters(...)
  - sends the result to the VLC audio engine playing Weightless.
"""

import argparse
import math
import time

from controller import AudioParams, update_audio_parameters
from audio_engine import AudioEngine

STEP_SEC = 0.5  # seconds between demo updates

# ====== AUDIO ENGINE SETUP ======

_engine = None
_params = AudioParams(tempo=80.0, pitch=0.0, volume=0.6)


def init_audio():
    global _engine
    if _engine is None:
        # Use the same path that worked in your isolated test
        _engine = AudioEngine("~/biofeedback/audio/Weightless.mp3")
        _engine.start()
        print("[AUDIO] Started Weightless playback.")


def send_to_audio(params: AudioParams):
    """
    Send parameters to the actual audio engine AND print them.
    """
    init_audio()

    print(
        f"[AUDIO] tempo={params.tempo:6.2f} BPM   "
        f"pitch={params.pitch:5.2f} st   "
        f"volume={params.volume:4.2f}"
    )

    _engine.set_params(params)


# ====== MODES ======

def mode_manual():
    """
    Manual mode:
      - You repeatedly enter rmssd_z and FAA.
      - Each step updates audio parameters and sends to engine.
    """
    global _params
    print("\nManual mode (Ctrl+C or 'q' to quit).")
    print("  Enter:")
    print("    rmssd_z FAA")
    print("  e.g., '-1.0 0.2' (stressed + right-dominant)")
    print("        '0.5 -0.1' (relaxed + left-dominant)\n")

    send_to_audio(_params)

    while True:
        try:
            line = input("rmssd_z FAA > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[manual] Exiting.")
            break

        if not line:
            continue
        if line.lower() in ("q", "quit", "exit"):
            print("[manual] Exiting.")
            break

        parts = line.split()
        if len(parts) != 2:
            print("  Please enter two numbers: rmssd_z FAA")
            continue

        try:
            rmssd_z = float(parts[0])
            FAA = float(parts[1])
        except ValueError:
            print("  Could not parse numbers, try again.")
            continue

        _params = update_audio_parameters(rmssd_z, FAA, _params)
        send_to_audio(_params)


def mode_demo():
    """
    Demo mode:
      - Simulates a 'stress then recovery' scenario in a loop.
        * rmssd_z: starts near 0, dips negative (stress), returns to 0.
        * FAA: slowly oscillates from left to right dominance.
    """
    global _params
    print("\nDemo mode: synthetic stress + FAA pattern (Ctrl+C to stop).")

    t0 = time.time()
    init_audio()

    while True:
        t = time.time() - t0

        # rmssd_z: 0 → -1 over 30 s, then back to 0 over next 30 s
        period_hrv = 60.0
        phase = (t % period_hrv) / period_hrv  # 0..1
        if phase < 0.5:
            rmssd_z = -2.0 * phase      # 0 → -1
        else:
            rmssd_z = -2.0 * (1 - phase)  # -1 → 0

        # FAA: slow sine oscillation between -0.3 and +0.3
        FAA = 0.3 * math.sin(2 * math.pi * t / 40.0)

        print(f"\n[demo] t={t:5.1f}s  rmssd_z={rmssd_z:5.2f}  FAA={FAA:5.2f}")
        _params = update_audio_parameters(rmssd_z, FAA, _params)
        send_to_audio(_params)

        time.sleep(STEP_SEC)


# ====== MAIN ======

def main():
    parser = argparse.ArgumentParser(description="HRV+FAA music control harness")
    parser.add_argument(
        "--mode",
        choices=["manual", "demo"],
        default="demo",
        help="How to generate rmssd_z and FAA (manual or synthetic demo).",
    )
    args = parser.parse_args()

    try:
        if args.mode == "manual":
            mode_manual()
        else:
            mode_demo()
    except KeyboardInterrupt:
        print("\n[main] Stopped by user.")


if __name__ == "__main__":
    main()

