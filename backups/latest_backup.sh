#!/usr/bin/env bash
set -euo pipefail

# --------- CONFIG ---------
PI_HOST="raspberrypi.local"
PI_USER="madalenahughes"
REMOTE_DIR="/home/${PI_USER}/biofeedback"
LOCAL_BASE="${HOME}/Desktop/biofeedback/backups"
# --------------------------

TIMESTAMP="$(date +"%Y-%m-%d_%H-%M-%S")"

LATEST_DIR="${LOCAL_BASE}/latest_backup"
ARCHIVE_DIR="${LOCAL_BASE}/pi_backup_${TIMESTAMP}"

echo "🔄 Backing up ${PI_USER}@${PI_HOST}:${REMOTE_DIR} ..."
mkdir -p "${LATEST_DIR}"

# Sync from Pi → latest_backup
rsync -av --delete "${PI_USER}@${PI_HOST}:${REMOTE_DIR}/" "${LATEST_DIR}/"

echo "📦 Creating timestamped archive at: ${ARCHIVE_DIR}"
cp -a "${LATEST_DIR}" "${ARCHIVE_DIR}"

echo "✅ Backup complete."

