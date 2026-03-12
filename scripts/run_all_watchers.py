#!/usr/bin/env python3
"""
Run Multiple Watchers - Start all watchers simultaneously for Silver Tier

This script starts Gmail, Filesystem, and WhatsApp watchers concurrently
using threading, enabling true multi-source monitoring.

Usage:
    python scripts/run_all_watchers.py --vault ./vault
"""

import os
import sys
import time
import signal
import threading
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_status(watcher_name: str, message: str, status: str = "info"):
    """Print colored status message."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    colors = {
        "info": BLUE,
        "success": GREEN,
        "error": RED,
        "warning": YELLOW
    }
    color = colors.get(status, RESET)
    print(f"{color}[{timestamp}] [{watcher_name}] {message}{RESET}")


class WatcherThread(threading.Thread):
    """Run a watcher in a separate thread."""
    
    def __init__(self, name: str, watcher_class, **kwargs):
        super().__init__(daemon=True)
        self.name = name
        self.watcher_class = watcher_class
        self.kwargs = kwargs
        self.running = True
        self.error = None
    
    def run(self):
        """Run the watcher."""
        try:
            print_status(self.name, f"Starting...", "info")
            
            # Import watcher dynamically
            module_name = f"watchers.{self.name.lower()}_watcher"
            module = __import__(module_name, fromlist=[''])
            watcher_class = getattr(module, f"{self.name.capitalize()}Watcher")
            
            # Initialize watcher
            watcher = watcher_class(**self.kwargs)
            
            # Run the watcher
            watcher.run()
            
            print_status(self.name, f"Stopped", "success")
            
        except ImportError as e:
            self.error = f"Import error: {e}"
            print_status(self.name, f"Failed to import: {e}", "error")
        except Exception as e:
            self.error = str(e)
            print_status(self.name, f"Error: {e}", "error")
    
    def stop(self):
        """Stop the watcher."""
        self.running = False


def run_filesystem_watcher(vault_path: str, interval: int = 30):
    """Run filesystem watcher in current thread."""
    from watchers.filesystem_watcher import FilesystemWatcher
    
    watch_path = Path(vault_path) / "drop_folder"
    watch_path.mkdir(parents=True, exist_ok=True)
    
    watcher = FilesystemWatcher(
        vault_path=vault_path,
        watch_path=str(watch_path)
    )
    watcher.check_interval = interval
    
    print_status("Filesystem", f"Watching: {watch_path}", "success")
    watcher.run()


def run_gmail_watcher(vault_path: str, interval: int = 60):
    """Run Gmail watcher in current thread."""
    from watchers.gmail_watcher import GmailWatcher
    
    credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH')
    token_path = os.getenv('GMAIL_TOKEN_PATH')
    
    # Check if credentials exist
    if credentials_path and not Path(credentials_path).exists():
        print_status("Gmail", "Credentials not found, skipping", "warning")
        return
    
    watcher = GmailWatcher(
        vault_path=vault_path,
        credentials_path=credentials_path,
        token_path=token_path
    )
    watcher.check_interval = interval
    
    print_status("Gmail", f"Monitoring inbox (interval: {interval}s)", "success")
    watcher.run()


def run_whatsapp_watcher(vault_path: str, interval: int = 30):
    """Run WhatsApp watcher in current thread."""
    from watchers.whatsapp_watcher import WhatsAppWatcher
    
    session_path = Path(vault_path) / "secrets" / "whatsapp_session"
    
    watcher = WhatsAppWatcher(
        vault_path=vault_path,
        session_path=str(session_path),
        headless=True,
        check_interval=interval
    )
    
    print_status("WhatsApp", f"Monitoring messages (interval: {interval}s)", "success")
    watcher.run()


def main():
    parser = argparse.ArgumentParser(description='Run Multiple Watchers')
    parser.add_argument('--vault', default='./vault', help='Path to vault')
    parser.add_argument('--watchers', nargs='+', default=['filesystem', 'gmail'],
                       choices=['filesystem', 'gmail', 'whatsapp'],
                       help='Watchers to run')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    vault = Path(args.vault)
    
    print()
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}Silver Tier - Multiple Watchers{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}")
    print()
    print(f"Vault: {vault.absolute()}")
    print(f"Watchers: {', '.join(args.watchers)}")
    print(f"Interval: {args.interval} seconds")
    print()
    print(f"{GREEN}Press Ctrl+C to stop all watchers{RESET}")
    print()
    
    # Ensure vault directories exist
    (vault / "Needs_Action").mkdir(parents=True, exist_ok=True)
    (vault / "Logs").mkdir(parents=True, exist_ok=True)
    
    threads = []
    
    # Start watchers
    try:
        for watcher_name in args.watchers:
            if watcher_name == 'filesystem':
                t = threading.Thread(
                    target=run_filesystem_watcher,
                    args=(args.vault, args.interval),
                    daemon=True
                )
                t.start()
                threads.append(t)
                time.sleep(1)  # Stagger startup
                
            elif watcher_name == 'gmail':
                t = threading.Thread(
                    target=run_gmail_watcher,
                    args=(args.vault, args.interval * 2),
                    daemon=True
                )
                t.start()
                threads.append(t)
                time.sleep(1)
                
            elif watcher_name == 'whatsapp':
                t = threading.Thread(
                    target=run_whatsapp_watcher,
                    args=(args.vault, args.interval),
                    daemon=True
                )
                t.start()
                threads.append(t)
                time.sleep(1)
        
        print_status("System", f"All {len(threads)} watchers started", "success")
        print()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print()
        print_status("System", "Shutting down watchers...", "warning")
        
        # Wait for threads to finish
        for t in threads:
            t.join(timeout=2)
        
        print_status("System", "All watchers stopped", "success")
    
    except Exception as e:
        print_status("System", f"Fatal error: {e}", "error")
        sys.exit(1)


if __name__ == "__main__":
    main()
