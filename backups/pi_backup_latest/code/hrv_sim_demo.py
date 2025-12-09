import numpy as np
from math import sqrt

# Example: fake RR intervals in seconds (around 1s = 60 bpm)
rr_intervals = np.array([0.96, 1.02, 1.00, 1.05, 0.98, 1.01, 0.99, 1.03])

# Convert to ms for classic HRV formulas
rr_ms = rr_intervals * 1000.0

# Time-domain HRV metrics
mean_nn = np.mean(rr_ms)                # mean of NN intervals
sdnn = np.std(rr_ms, ddof=1)            # standard deviation of NN
diffs = np.diff(rr_ms)
rmssd = sqrt(np.mean(diffs**2))         # root mean square of successive diffs
nn50 = np.sum(np.abs(diffs) > 50.0)     # count of diffs > 50 ms
pnn50 = 100.0 * nn50 / len(diffs)       # % of NN50

print(f"Mean NN (ms): {mean_nn:.2f}")
print(f"SDNN (ms):    {sdnn:.2f}")
print(f"RMSSD (ms):   {rmssd:.2f}")
print(f"NN50:         {nn50}")
print(f"pNN50 (%):    {pnn50:.2f}")
