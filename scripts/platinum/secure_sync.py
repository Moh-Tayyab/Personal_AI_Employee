#!/usr/bin/env python3
"""
Platinum Secure Vault Sync
Watches the local vault and syncs ONLY markdown files to the shared Platinum folder.
Strictly IGNORES secrets, credentials, and .env files.
"""
import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
VAULT_PATH = Path("./vault")
SHARED_PATH = Path("/home/muhammad_tayyab/platinum_sync/vault")

# Security Blocklist (NEVER sync these)
BLOCKLIST_PATTERNS = [
    ".env", "*.key", "*.pem", "credentials/", "secrets/", "*.json", "*.pyc"
]

# Allowed Extensions
ALLOWED_EXTENSIONS = [".md"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("PlatinumSync")


class SecureSyncHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        
        src_path = Path(event.src_path)
        
        # Security Check 1: Is it a safe file type?
        if src_path.suffix not in ALLOWED_EXTENSIONS:
            logger.warning(f"🚫 BLOCKED (Extension): {src_path.name}")
            return

        # Security Check 2: Is it in the blocklist?
        for pattern in BLOCKLIST_PATTERNS:
            if pattern in str(src_path):
                logger.warning(f"🚫 BLOCKED (Security Policy): {src_path.name}")
                return

        # Sync Logic
        try:
            relative_path = src_path.relative_to(VAULT_PATH)
            dest_path = SHARED_PATH / relative_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_path, dest_path)
            logger.info(f"✅ SYNCED: {relative_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to sync {src_path.name}: {e}")

if __name__ == "__main__":
    logger.info(f"🔒 Starting Secure Vault Sync from {VAULT_PATH}")
    logger.info(f"📂 Syncing TO: {SHARED_PATH}")
    logger.info(f"🛡️ Security: Blocking {', '.join(BLOCKLIST_PATTERNS)}")

    SHARED_PATH.mkdir(parents=True, exist_ok=True)
    
    event_handler = SecureSyncHandler()
    observer = Observer()
    observer.schedule(event_handler, str(VAULT_PATH), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
