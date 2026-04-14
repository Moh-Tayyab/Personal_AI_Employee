#!/usr/bin/env python3
"""
Platinum Cloud Agent - The "Watcher"
Simulates a cloud-based AI that monitors emails and creates drafts.
It runs 24/7 and ONLY writes to the shared vault.
"""
import os
import time
import random
from datetime import datetime
from pathlib import Path

SYNC_DIR = Path("/mnt/sync")
NEEDS_ACTION = SYNC_DIR / "Needs_Action"

def simulate_cloud_monitoring():
    print("☁️  [CLOUD AGENT] Starting monitoring loop...")
    print("☁️  [CLOUD AGENT] Monitoring: Gmail, Twitter Mentions")
    print("☁️  [CLOUD AGENT] Mode: Draft-Only (No Sending)")

    while True:
        # Simulate random incoming communication
        if random.random() < 0.3:  # 30% chance every cycle
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"EMAIL_Cloud_Draft_{timestamp}.md"
            filepath = NEEDS_ACTION / filename

            content = f"""---
type: email_draft
source: cloud_agent
from: ceo@bigclient.com
subject: Urgent Project Update
created: {datetime.now().isoformat()}
status: pending_approval
---

# Draft Reply Created by Cloud AI

I have analyzed the incoming email from **ceo@bigclient.com**.
They are asking for the Q3 report. I have prepared a draft response.

**Draft Content:**
"Dear Client, The Q3 report is ready. Please find attached..."

**Action Required:** Local Agent must approve and send.
"""
            filepath.write_text(content)
            print(f"☁️  [CLOUD AGENT] 📄 Created Draft: {filename}")
        
        time.sleep(10) # Check every 10 seconds for demo

if __name__ == "__main__":
    simulate_cloud_monitoring()
