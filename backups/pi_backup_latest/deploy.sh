#!/bin/bash

# ==== CONFIG ====
REPO_DIR="$HOME/Desktop/biofeedback"

# Hostnames / IPs for your Pis
PIS=(
  "madalenahughes@pitop.local"    # Pi-top Ceed Pi 3
  # Add more like: "pi@raspberrypi.local" if/when you want
)

# ==== SCRIPT ====

# Commit message: use all arguments if provided, otherwise auto message
if [ $# -eq 0 ]; then
  COMMIT_MSG="auto-deploy $(date '+%Y-%m-%d %H:%M:%S')"
else
  COMMIT_MSG="$*"
fi

echo ">>> Moving to repo: $REPO_DIR"
cd "$REPO_DIR" || { echo "!!! Failed to cd into $REPO_DIR"; exit 1; }

echo ">>> Current git status (short):"
git status -sb || git status

echo ">>> Checking for changes (excluding pi_backup_latest)..."
CHANGES=$(git status --porcelain | grep -v 'backups/pi_backup_latest' || true)

if [ -z "$CHANGES" ]; then
  echo ">>> No changes to commit; working tree clean."

  # Still try to pull on each Pi so they stay synced with GitHub
  for HOST in "${PIS[@]}"; do
    echo ">>> Pulling latest on $HOST (no local changes to deploy)..."
    ssh "$HOST" 'cd ~/biofeedback-lab && git pull' || echo "!!! Failed to update $HOST"
  done

  # macOS notification + beep for "nothing to do"
  osascript -e 'display notification "No changes to deploy (repo already up to date)." with title "Biofeedback Deploy"' 2>/dev/null || true
  osascript -e 'beep 1' 2>/dev/null || true
  echo ">>> Deploy finished: nothing to commit."
  osascript -e 'display notification "No changes to deploy." with title "Biofeedback Deploy"' 2>/dev/null || true
  osascript -e 'beep 1' 2>/dev/null || true
  exit 0
fi

echo ">>> Changes detected. Updating code snapshot in backups/pi_backup_latest/..."

# Refresh latest code snapshot (code + helper scripts only)
mkdir -p backups/pi_backup_latest/code

# Snapshot all code/* into backups/pi_backup_latest/code
rsync -a --delete code/ backups/pi_backup_latest/code/ 2>/dev/null || true

# Optionally snapshot key scripts at top level
[ -f start_session.sh ] && cp start_session.sh backups/pi_backup_latest/ || true
[ -f deploy.sh ] && cp deploy.sh backups/pi_backup_latest/ || true

echo ">>> Adding all changes (including updated snapshot)..."
git add .

echo ">>> Committing with message: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

echo ">>> Pushing to GitHub..."
git push

# After a successful push, pull on each Pi
for HOST in "${PIS[@]}"; do
  echo ">>> Deploying to $HOST..."
  ssh "$HOST" 'cd ~/biofeedback-lab && git pull' || echo "!!! Failed to update $HOST"
done

# macOS notification + beep for successful deploy
osascript -e 'display notification "Deploy complete and synced to Pis." with title "Biofeedback Deploy"' 2>/dev/null || true
osascript -e 'beep 2' 2>/dev/null || true

echo ">>> Deploy complete."

