#!/bin/bash

# Simple menu to run backup/deploy actions for the biofeedback project

BACKUP_DIR="$HOME/Desktop/biofeedback/backups"
REPO_DIR="$HOME/Desktop/biofeedback"

echo "==============================="
echo "  Biofeedback Flipper Menu"
echo "==============================="
echo "1) Backup only (latest_backup.sh)"
echo "2) Deploy only (deploy.sh)"
echo "3) Backup + Deploy"
echo "4) Quit"
echo

read -p "Select an option [1-4]: " choice

case "$choice" in
  1)
    echo ">>> Running backup only..."
    cd "$BACKUP_DIR" || { echo "!!! Could not cd to $BACKUP_DIR"; exit 1; }
    ./latest_backup.sh
    echo ">>> Backup complete."
    ;;

  2)
    echo ">>> Running deploy only..."
    cd "$REPO_DIR" || { echo "!!! Could not cd to $REPO_DIR"; exit 1; }
    ./deploy.sh "Flipper deploy $(date '+%Y-%m-%d %H:%M:%S')"
    echo ">>> Deploy complete."
    ;;

  3)
    echo ">>> Running backup + deploy..."
    cd "$BACKUP_DIR" || { echo "!!! Could not cd to $BACKUP_DIR"; exit 1; }
    ./latest_backup.sh
    cd "$REPO_DIR" || { echo "!!! Could not cd to $REPO_DIR"; exit 1; }
    ./deploy.sh "Flipper backup+deploy $(date '+%Y-%m-%d %H:%M:%S')"
    echo ">>> Backup + Deploy complete."
    ;;

  4)
    echo ">>> Quit selected. Exiting."
    ;;

  *)
    echo ">>> Invalid option."
    ;;
esac

echo "Press Enter to close..."
read

