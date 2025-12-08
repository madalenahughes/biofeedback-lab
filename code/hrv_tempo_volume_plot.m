% hrv_tempo_volume_plot.m
% Plot RMSSD (ms), tempo, and volume vs time from session CSV.

% ---- SETTINGS ----
fname = 'session_20251123_043557_samples.csv';  % change if needed

% ---- LOAD DATA ----
T = readtable(fname);

% Time in minutes
t_min = T.t_rel_sec / 60;

% Signals
rmssd_ms = T.rmssd_ms;
tempo    = T.tempo;
volume   = T.volume;

% ---- FIGURE ----
figure;

% --- Subplot 1: HRV (RMSSD ms) ---
subplot(2,1,1);
plot(t_min, rmssd_ms, 'LineWidth', 1.5);
grid on;
xlabel('Time (minutes)');
ylabel('RMSSD (ms)');
title('HRV (RMSSD) vs Time');
xlim([min(t_min) max(t_min)]);

% --- Subplot 2: Tempo + Volume (dual y-axis) ---
subplot(2,1,2);

yyaxis left;
plot(t_min, tempo, 'LineWidth', 1.5);
ylabel('Tempo (playback rate)');
xlim([min(t_min) max(t_min)]);
grid on;

yyaxis right;
plot(t_min, volume, '--', 'LineWidth', 1.2);
ylabel('Volume');

xlabel('Time (minutes)');
title('Tempo and Volume vs Time');

legend({'Tempo','Volume'}, 'Location', 'best');

set(gcf, 'Position', [100 100 850 600]);

