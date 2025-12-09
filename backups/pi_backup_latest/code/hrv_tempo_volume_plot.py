import pandas as pd
import matplotlib.pyplot as plt

# ---- SETTINGS ----
# Use your new session file here:
FNAME = "session_20251123_035114_samples.csv"  # change if needed

# ---- LOAD DATA ----
df = pd.read_csv(FNAME)

t_min = df["t_rel_sec"] / 60.0
rmssd_ms = df["rmssd_ms"]
tempo = df["tempo"]
volume = df["volume"]

t_end = t_min.max()
# If you want a final 60s baseline shaded, this will mark it
last_baseline_start = max(t_end - 1.0, 0.0)

# ---- PLOT ----
fig, axes = plt.subplots(2, 1, sharex=True, figsize=(10, 6))

ax1, ax2 = axes

# Helper to shade phases on any axis
def shade_phases(ax):
    # Baseline 1: 0–1 min
    ax.axvspan(0, 1, color="lightgray", alpha=0.3, label="Baseline 1")

    # Standard params: 1–2 min
    ax.axvspan(1, 2, color="honeydew", alpha=0.4, label="Standard Params")

    # Manipulated audio: 2 min → last baseline start
    ax.axvspan(2, last_baseline_start, color="lightblue", alpha=0.25,
               label="Manipulated Audio")

    # Baseline 2: last 60 s
    ax.axvspan(last_baseline_start, t_end, color="lavender", alpha=0.4,
               label="Baseline 2")

# --- Top: HRV ---
shade_phases(ax1)
ax1.plot(t_min, rmssd_ms, linewidth=1.5, color="blue")
ax1.set_ylabel("RMSSD (ms)")
ax1.set_title("HRV (RMSSD) vs Time")
ax1.grid(True)

# Deduplicate legend for top axis
handles, labels = ax1.get_legend_handles_labels()
unique = dict(zip(labels, handles))
ax1.legend(unique.values(), unique.keys(), loc="upper left")

# --- Bottom: Tempo + Volume ---
shade_phases(ax2)

ax2_left = ax2
ax2_right = ax2.twinx()

ax2_left.plot(t_min, tempo, linewidth=1.5)
ax2_left.set_ylabel("Tempo (playback rate)")
ax2_left.grid(True)

ax2_right.plot(t_min, volume, "--", linewidth=1.2)
ax2_right.set_ylabel("Volume")

ax2_left.set_xlabel("Time (minutes)")
ax2_left.set_title("Tempo and Volume vs Time")

fig.tight_layout()
plt.show()

