#!/usr/bin/env python3
"""
Test Filesystem Watcher - Quick test for Bronze Tier

This script tests the filesystem watcher by creating a test file
and verifying it gets processed correctly.

Usage:
    python scripts/test_filesystem_watcher.py --vault ./vault
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchers.filesystem_watcher import FilesystemWatcher


def test_filesystem_watcher(vault_path: str, test_duration: int = 10):
    """Test the filesystem watcher."""
    
    vault = Path(vault_path)
    watch_path = vault / "drop_folder"
    needs_action = vault / "Needs_Action"
    
    print("=" * 60)
    print("Filesystem Watcher Test")
    print("=" * 60)
    print()
    
    # Ensure directories exist
    watch_path.mkdir(parents=True, exist_ok=True)
    needs_action.mkdir(parents=True, exist_ok=True)
    
    print(f"Watch folder: {watch_path}")
    print(f"Needs_Action folder: {needs_action}")
    print()
    
    # Create watcher
    print("Starting filesystem watcher...")
    watcher = FilesystemWatcher(
        vault_path=vault_path,
        watch_path=str(watch_path)
    )
    
    # Start observer in background
    watcher.observer.start()
    print("✅ Filesystem watcher started")
    print()
    
    # Create a test file
    test_file = watch_path / f"test_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    test_file.write_text("This is a test file for the filesystem watcher.")
    print(f"Created test file: {test_file}")
    print()
    
    # Wait for processing
    print(f"Waiting {test_duration} seconds for processing...")
    time.sleep(test_duration)
    
    # Check if action file was created
    action_files = list(needs_action.glob("FILE_*.md"))
    
    print()
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    if action_files:
        print("✅ SUCCESS: Action file created!")
        print()
        print(f"Action files found: {len(action_files)}")
        for f in action_files[-3:]:  # Show last 3
            print(f"  - {f.name}")
        print()
        
        # Show content of latest file
        latest = max(action_files, key=lambda x: x.stat().st_mtime)
        print(f"Content of {latest.name}:")
        print("-" * 40)
        print(latest.read_text()[:500])
        print("...")
        print()
        
        # Cleanup
        print("Cleaning up test files...")
        test_file.unlink(missing_ok=True)
        for f in action_files:
            if "test" in f.name.lower():
                f.unlink(missing_ok=True)
                meta = needs_action / f"{f.name}"
                meta.unlink(missing_ok=True)
        print("✅ Cleanup complete")
        
        return True
    else:
        print("❌ FAILED: No action file created")
        print()
        print("Troubleshooting:")
        print("1. Check if watchdog is installed: pip install watchdog")
        print("2. Check watch folder permissions")
        print("3. Try creating a file manually in:", watch_path)
        
        # Cleanup
        test_file.unlink(missing_ok=True)
        return False
    
    finally:
        # Stop watcher
        watcher.observer.stop()
        watcher.observer.join()
        print("Filesystem watcher stopped")


def main():
    parser = argparse.ArgumentParser(description='Test Filesystem Watcher')
    parser.add_argument('--vault', default='./vault', help='Path to vault')
    parser.add_argument('--duration', type=int, default=10, help='Test duration in seconds')
    
    args = parser.parse_args()
    
    success = test_filesystem_watcher(args.vault, args.duration)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
