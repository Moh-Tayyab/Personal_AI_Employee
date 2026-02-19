#!/bin/bash
# Cron Scheduler Setup for Personal AI Employee
# Add these lines to your crontab (crontab -e)

# Run orchestrator every 5 minutes
# */5 * * * * cd /path/to/Personal_AI_Employee && source .venv/bin/activate && python orchestrator.py --vault ./vault --dry-run >> /tmp/ai_employee.log 2>&1

# Run filesystem watcher continuously (use PM2 instead for persistent processes)
# */5 * * * * cd /path/to/Personal_AI_Employee && source .venv/bin/activate && python watchers/filesystem_watcher.py --vault ./vault --watch-path ./drop >> /tmp/filesystem_watcher.log 2>&1

# Generate morning briefing at 7 AM every Monday
# 0 7 * * 1 cd /path/to/Personal_AI_Employee && source .venv/bin/activate && python -c "from orchestrator import Orchestrator; o = Orchestrator('./vault', True); o.generate_morning_briefing()" >> /tmp/morning_briefing.log 2>&1
