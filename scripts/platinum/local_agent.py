#!/usr/bin/env python3
"""
Platinum Local Agent - The "Executor"
Monitors the Platinum Sync folder for approved drafts from the Cloud Agent.
Executes actions (WhatsApp, Odoo, Send Email) and moves to Done.
"""
import os
import time
import shutil
from pathlib import Path
from datetime import datetime

SYNC_DIR = Path(os.path.expanduser("~/platinum_sync"))
APPROVED_DIR = SYNC_DIR / "Approved"
DONE_DIR = SYNC_DIR / "Done"
LOG_FILE = SYNC_DIR / "execution.log"

def check_approved():
    """Look for approved files from Cloud Agent."""
    files = list(APPROVED_DIR.glob("*.md"))
    return files

def execute_action(filepath: Path):
    """Simulate executing the action (e.g., sending email, posting to Odoo)."""
    print(f"🏠 [LOCAL AGENT] Executing: {filepath.name}")
    
    # In a real scenario, we would parse the file and call MCP servers here.
    # For Platinum Demo, we simulate the "Final Execution".
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] EXECUTED: {filepath.name} -> Moved to Done\n"
    
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    
    # Move to Done
    dest = DONE_DIR / filepath.name
    shutil.move(str(filepath), str(dest))
    print(f"🏠 [LOCAL AGENT] ✅ Action Complete. Moved to Done.")

def main():
    print("🏠 [LOCAL AGENT] Starting Local Execution Loop...")
    print("🏠 [LOCAL AGENT] Monitoring: ~/platinum_sync/Approved/")
    
    os.makedirs(APPROVED_DIR, exist_ok=True)
    os.makedirs(DONE_DIR, exist_ok=True)

    while True:
        approved_files = check_approved()
        if approved_files:
            for f in approved_files:
                execute_action(f)
        time.sleep(5)

if __name__ == "__main__":
    main()
