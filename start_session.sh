#!/bin/bash

echo "🎧 Local Biofeedback Helper"
echo "This version doesn’t talk to the Pi yet."

PROJECT_DIR="/Users/madalenahughes/Desktop/biofeedback"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ Project directory not found: $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR" || exit 1

echo "📂 Opening project folder in Finder..."
open "$PROJECT_DIR"

# Try to open in VS Code if installed; ignore errors
if command -v code >/dev/null 2>&1; then
  echo "🧠 Opening project in VS Code..."
  code "$PROJECT_DIR" >/dev/null 2>&1 &
fi

echo "✅ Local helper finished. Later we’ll swap this to start the Pi session."
