#!/usr/bin/env python3
"""
sim_run.py
End-to-end test: simulated AudioParams → AudioEngine (Weightless via VLC).
"""

import math
import time

from controller import AudioParams
from audio_engine import AudioEngine


def simulated_param_stream():
    """
    Generator that yields slowly varying AudioParams.

    This does NOT use real HRV/FAA yet — it just creates smooth changes
    so we can test the end-to-end audio control.
    """
    t = 0.0
    dt = 1.0  # seconds between updates

    while True:
        # s varies between -1 and +1 over time
        s = math.sin(t / 20.0)

        # Interpret tempo as a playback-rate factor around 1.0
        tempo = 1.0 - 0.2 * s      # ~0.8–1.2

        # Keep pitch constant for now (you can wire this later)
        pitch = 0.0

        # Volume: 40–80-ish
        volume = 60 + 20 * s

        yield AudioParams(
            tempo=float(tempo),
            pitch=float(pitch),
            volume=float(volume),
        )

        t += dt
        time.sleep(dt)


def main():
    engine = AudioEngine()   # uses default Weightless.mp3 path
    print("Starting audio engine…")
    engine.player.play()

    # Give VLC a moment to start playback
    time.sleep(1.0)

    print("Running simulated AudioParams → audio loop. Ctrl+C to stop.")

    try:
        for params in simulated_param_stream():
            # Preferred path: let your engine handle AudioParams
            if hasattr(engine, "set_params"):
                engine.set_params(params)
            else:
                # Fallback path if set_params doesn't exist:
                #  - treat tempo as playback rate factor
                #  - use volume directly
                try:
                    rate = max(0.5, min(2.0, params.tempo))
                    engine.player.set_rate(rate)
                except Exception:
                    pass

                vol = int(max(0, min(100, params.volume)))
                engine.player.audio_set_volume(vol)

            print(f"→ tempo={params.tempo:.2f}, pitch={params.pitch:.2f}, volume={params.volume:.1f}")
    except KeyboardInterrupt:
        print("\nStopping…")
    finally:
        engine.player.stop()


if __name__ == "__main__":
    main()
