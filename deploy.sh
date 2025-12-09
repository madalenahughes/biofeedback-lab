#!/bin/bash

# ==== CONFIG ====
REPO_DIR="$HOME/Desktop/biofeedback"
BACKUP_LATEST="$REPO_DIR/backups/pi_backup_latest/biofeedback"
CODE_DIR="$REPO_DIR/code"

PIS=(
  "madalenahughes@pitop.local"    # Pi-top Ceed Pi 3
  # Add more like: "pi@raspberrypi.local" if/when you want
)

# ==== SCRIPT ====

# Commit message: use all arguments if provided, otherwise auto message
if [ $# == 0 ]; then
  COMMIT_MSG="auto-deploy $(date '+%Y-%m-%d %H:%M:%S')"
else
  COMMIT_MSG="$*"
fi

echo ">>> Moving to repo: $REPO_DIR"
cd "$REPO_DIR" || { echo "!!! Failed to cd into $REPO_DIR"; exit 1; }

echo ">>> Checking that latest backup exists at: $BACKUP_LATEST"
if [ ! -d "$BACKUP_LATEST" ]; then
  echo "!!! Latest backup directory not found: $BACKUP_LATEST"
  echo "!!! Run backups/latest_backup.sh first."
  osascript -e 'display notification "Latest backup not found. Run latest_backup.sh first." with title "Biofeedback Deploy"' 2>/dev/null || true
  osascript -e 'beep 3' 2>/dev/null || true
  exit 1
fi

echo ">>> Rebuilding code/ snapshot from latest backup..."
mkdir -p "$CODE_DIR"

# Copy ONLY .py and .sh from pi_backup_latest/biofeedback into code/
# Preserve folder structure, delete stale files in code/
rsync -a --delete \
  --include='*/' \
  --include='*.py' \
  --include='*.sh' \
  --exclude='*' \
  "$BACKUP_LATEST"/ "$CODE_DIR"/

echo ">>> Current git status (short):"
git status -sb || git status

echo ">>> Checking for changes after snapshot..."
if ! git status --porcelain | grep -q .; then
  echo ">>> No changes to commit; working tree clean."

  # Still try to pull on each Pi so they stay synced with GitHub
  for HOST in "${PIS[@]}"; do
    echo ">>> Pulling latest on $HOST (no new snapshot changes)..."
    ssh "$HOST" 'cd ~/biofeedback-lab && git pull' || echo "!!! Failed to update $HOST"
  done

  # macOS notification + single beep
  osascript -e 'display notification "No changes to deploy (snapshot identical to last one)." with title "Biofeedback Deploy"' 2>/dev/null || true
  osascript -e 'beep 1' 2>/dev/null || true
  echo ">>> Deploy finished: nothing to commit."
  exit 0
fi

echo ">>> Changes detected in code snapshot. Adding files..."
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

# macOS notification + double beep
osascript -e 'display notification "Deploy complete. GitHub now has code from latest Pi backup." with title "Biofeedback Deploy"' 2>/dev/null || true
osascript -e 'beep 2' 2>/dev/null || true

echo ">>> Deploy complete."

