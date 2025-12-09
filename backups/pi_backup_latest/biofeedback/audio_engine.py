#!/usr/bin/env python3
"""
audio_engine.py
Simple audio engine using python-vlc to play a background track and
apply tempo/volume changes via an AudioParams-style interface.

Also exposes:
    AudioEngine.finished  -> bool
which becomes True when the audio file finishes playing.
"""

import os
import time
from typing import Optional

import vlc


class AudioEngine:
    def __init__(self, media_path: Optional[str] = None) -> None:
        """
        Initialize VLC player and load an audio file.

        If media_path is not provided, the engine will look for an MP3 file
        in an ./audio directory (relative to the working directory).
        """
        if media_path is None:
            media_path = self.find_default_media()

        if not os.path.isfile(media_path):
            raise FileNotFoundError(f"Audio file not found: {media_path}")

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        media = self.instance.media_new(media_path)
        self.player.set_media(media)

        # Flag set to True when playback reaches the end
        self.finished: bool = False

        # Register end-of-track callback
        try:
            em = self.player.event_manager()
            em.event_attach(
                vlc.EventType.MediaPlayerEndReached,
                self._on_end_reached,
            )
        except Exception as e:
            print(f"[audio_engine] Warning: could not attach end-of-track handler: {e!r}")

        # Neutral starting volume
        self.player.audio_set_volume(60)

    # ------------------------------------------------------------------
    # VLC event callbacks
    # ------------------------------------------------------------------
    def _on_end_reached(self, event) -> None:
        """Called by VLC when the media finishes."""
        self.finished = True
        print("[audio_engine] Media finished (MediaPlayerEndReached).")

    # ------------------------------------------------------------------
    # Media helpers
    # ------------------------------------------------------------------
    def find_default_media(self) -> str:
        """
        Look for an MP3 file in ./audio and return its path.

        Raises FileNotFoundError if nothing is found.
        """
        audio_dir = os.path.join(os.getcwd(), "audio")
        if not os.path.isdir(audio_dir):
            raise FileNotFoundError(
                "audio/ directory not found. Please create ./audio and "
                "place a background MP3 there."
            )

        candidates = [
            os.path.join(audio_dir, f)
            for f in os.listdir(audio_dir)
            if f.lower().endswith(".mp3")
        ]
        if candidates:
            # Just take the first match for now.
            return candidates[0]

        raise FileNotFoundError(
            "No MP3 file found in ./audio. "
            "Please place an audio file (e.g., Weightless.mp3) in the audio/ directory."
        )

    # ------------------------------------------------------------------
    # Control interface
    # ------------------------------------------------------------------
    def set_params(self, params) -> None:
        """
        Apply AudioParams-like values to the underlying player.

        Expects:
            params.tempo  ~ around 1.0 (e.g., [0.9, 1.1])
            params.pitch  ~ semitones (currently logged only; rate is tempo-based)
            params.volume ~ [0, 100]
        """
        t = float(getattr(params, "tempo", 1.0))
        p = float(getattr(params, "pitch", 0.0))
        v = float(getattr(params, "volume", 60.0))

        # Playback rate control.
        # Keep playback rate near 1.0 so it never sounds too extreme.
        base_rate = 1.05  # small built-in bias toward slightly energetic
        rate = base_rate * t
        rate = max(0.90, min(1.20, rate))

        try:
            self.player.set_rate(rate)
        except Exception as e:
            print(f"[audio_engine] Warning: failed to set rate: {e!r}")

        # Volume: clamp to valid VLC range [0, 100]
        volume_int = int(max(0, min(100, v)))
        try:
            self.player.audio_set_volume(volume_int)
        except Exception as e:
            print(f"[audio_engine] Warning: failed to set volume: {e!r}")

        # Pitch is currently not changing playback; it is intended for
        # future DSP or to be logged for analysis.
        print(
            f"[audio_engine] tempo={t:.3f}  pitch={p:.2f}  "
            f"volume={volume_int:d}  rate={rate:.3f}"
        )

    def stop(self) -> None:
        """Stop playback if possible."""
        try:
            self.player.stop()
        except Exception:
            pass


if __name__ == "__main__":
    # Simple self-test: play 10 seconds
    engine = AudioEngine()
    print("Testing audio: playing 10 seconds…")
    engine.player.play()
    t0 = time.time()
    while time.time() - t0 < 10 and not engine.finished:
        time.sleep(0.2)
    print("Stopping.")
    engine.stop()
