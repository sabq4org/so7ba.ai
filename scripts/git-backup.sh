#!/bin/bash
# صُحبة Daily Git Backup
cd /home/openclaw/.openclaw/workspace
git add -A
git diff --cached --quiet && exit 0  # nothing to commit
git commit -m "🔄 Auto-backup $(date +%Y-%m-%d_%H:%M)"
git push origin main
