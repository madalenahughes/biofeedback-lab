% hrv_plot_ms.m
fname = 'session_20251123_035114_samples.csv';
T = readtable(fname);

t_min = T.t_rel_sec / 60;
rmssd_ms = T.rmssd_ms;

figure;
plot(t_min, rmssd_ms, 'LineWidth', 1.5);
grid on;
xlabel('Time (minutes)');
ylabel('RMSSD (ms)');
title('HRV (RMSSD) vs Time');
