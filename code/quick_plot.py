import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("session_20251123_035114_samples.csv")

t_min = df["t_rel_sec"] / 60
rmssd_ms = df["rmssd_ms"]

plt.figure(figsize=(10, 6))

# --- Background shaded regions ---
# Baseline: 0 to 1 min
plt.axvspan(0, 1, color='lightgray', alpha=0.3, label='Baseline')

# Music no parameter change: 1 to 2 min
plt.axvspan(1, 2, color='lightgreen', alpha=0.25, label='Standard Params')

# Music / Intervention: 2 min to end of file 
plt.axvspan(2, t_min.max()-1, color='lightblue', alpha=0.25, label='Music Phase')

# Final 60 seconds
plt.axvspan(t_min.max()-1, t_min.max(), color='honeydew', alpha = 0.25, label='Final Comparator')

# --- Plot the HRV curve ---
plt.plot(t_min, rmssd_ms, linewidth=1.5, color='blue')

# Labels and title
plt.xlabel("Time (minutes)")
plt.ylabel("RMSSD (ms)")
plt.title("HRV (RMSSD) vs Time with Phase Shading")
plt.grid(True)

# Show legend for the shaded areas only ONCE
handles, labels = plt.gca().get_legend_handles_labels()
unique = dict(zip(labels, handles))
plt.legend(unique.values(), unique.keys())

plt.tight_layout()
plt.show()

