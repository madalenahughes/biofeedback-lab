#!/usr/bin/env python3
"""
polar_run.py
Real-time HRV (RMSSD z) from Polar H10 → AudioParams → AudioEngine.
"""

import asyncio

from controller import AudioParams, update_audio_parameters
from audio_engine import AudioEngine
from polar_hrv import rmssd_z_stream


async def main() -> None:
    # Initialize audio engine and parameter state
    engine = AudioEngine()
    params = AudioParams()

    print("Starting audio engine…")
    engine.player.play()
    await asyncio.sleep(1.0)

    print("Connecting to Polar H10 and starting HRV-driven control (Ctrl+C to stop)")

    try:
        async for rmssd_z in rmssd_z_stream():
            # Use raw z from HRV stream; controller handles clamping/scaling.
            raw_z = float(rmssd_z)
            FAA = 0.0  # EEG FAA placeholder for future integration

            # Update params using our controller
            params = update_audio_parameters(raw_z, FAA, params)

            # Apply params to audio engine
            if hasattr(engine, "set_params"):
                engine.set_params(params)
            else:
                # Fallback mapping for VLC-style player
                try:
                    base_rate = 1.05
                    rate = base_rate * float(params.tempo)
                    rate = max(1.00, min(1.20, rate))
                    engine.player.set_rate(rate)
                except Exception as e:
                    print(f"[audio_engine] set_rate failed: {e}")

                try:
                    vol = int(max(0, min(100, float(params.volume))))
                    engine.player.audio_set_volume(vol)
                except Exception as e:
                    print(f"[audio_engine] set_volume failed: {e}")

            # Debug output
            print(
                f"RMSSD_z_raw={raw_z:+.2f}  "
                f"tempo={params.tempo:.2f}, "
                f"pitch={params.pitch:.2f}, "
                f"volume={params.volume:.1f}"
            )

    except KeyboardInterrupt:
        print("\nStopping (KeyboardInterrupt).")
    finally:
        print("Stopping audio engine…")
        engine.stop()


if __name__ == "__main__":
    asyncio.run(main())
