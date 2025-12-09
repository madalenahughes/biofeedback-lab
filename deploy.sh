#!/bin/bash

# ==== CONFIG ====
REPO_DIR="$HOME/Desktop/biofeedback"

# Hostnames / IPs for your Pis
PIS=(
  "madalenahughes@pitop.local"    # Pi 3 in the Ceed
)

# ==== SCRIPT ====

set -e

# Commit message: use all arguments if provided, otherwise auto message
if [ $# -eq 0 ]; then
  COMMIT_MSG="auto-deploy $(date '+%Y-%m-%d %H:%M:%S')"
else
  COMMIT_MSG="$*"
fi

echo ">>> Moving to repo: $REPO_DIR"
cd "$REPO_DIR"

echo ">>> Git status:"
git status

echo ">>> Adding all changes..."
git add .

echo ">>> Committing with message: $COMMIT_MSG"
if git commit -m "$COMMIT_MSG"; then
  echo ">>> Pushing to GitHub..."
  git push
else
  echo ">>> No changes to commit. Skipping push."
fi

# If push happened, pull on each Pi
for HOST in "${PIS[@]}"; do
  echo ">>> Deploying to $HOST..."
  ssh "$HOST" 'cd ~/biofeedback-lab && git pull' || echo "!!! Failed to update $HOST"
done

echo ">>> Deploy complete."

