"""
Base Watcher Template - Foundation for all watcher scripts

This abstract base class provides the foundation for all watcher scripts
that monitor external sources and create action files in the vault.

Usage:
    python -m watchers.base_watcher
"""

from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
import logging
import time
import json
import signal
import sys


class BaseWatcher(ABC):
    """Abstract base class for all watcher implementations."""

    def __init__(
        self,
        vault_path: str,
        check_interval: int = 60,
        name: str = "BaseWatcher"
    ):
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.name = name
        self.running = True

        # Setup logging
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Ensure required directories exist
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs = self.vault_path / 'Logs'
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new updates from the data source.

        Returns:
            list: List of new items to process
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create an action file in the Needs_Action folder.

        Args:
            item: The item to create an action file for

        Returns:
            Path: Path to the created file
        """
        pass

    def log_action(self, action_type: str, details: dict):
        """Log an action to the daily log file."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'watcher': self.name,
            'action_type': action_type,
            'details': details
        }

        # Read existing logs or create new list
        if log_file.exists():
            with open(log_file, 'r') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def get_processed_ids(self) -> set:
        """Get set of already processed item IDs."""
        processed_file = self.vault_path / '.processed_ids.json'
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                data = json.load(f)
                # Convert list to set if stored as list
                ids = data.get(self.name, [])
                return set(ids) if isinstance(ids, list) else ids
        return set()

    def save_processed_ids(self, processed_ids: set):
        """Save processed item IDs to prevent duplicates."""
        processed_file = self.vault_path / '.processed_ids.json'

        all_processed = {}
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                try:
                    all_processed = json.load(f)
                except json.JSONDecodeError:
                    all_processed = {}

        all_processed[self.name] = list(processed_ids)

        with open(processed_file, 'w') as f:
            json.dump(all_processed, f)

    def run(self):
        """Main run loop for the watcher."""
        self.logger.info(f"Starting {self.name}")
        processed_ids = self.get_processed_ids()

        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        while self.running:
            try:
                items = self.check_for_updates()
                new_items = [i for i in items if i.get('id') not in processed_ids]

                for item in new_items:
                    try:
                        filepath = self.create_action_file(item)
                        # Get item ID, fallback to path if not available
                        item_id = item.get('id') or str(item.get('path', ''))
                        processed_ids.add(item_id)
                        self.save_processed_ids(processed_ids)
                        self.logger.info(f"Created action file: {filepath}")
                        self.log_action('item_processed', {
                            'item_id': item.get('id'),
                            'file': str(filepath)
                        })
                    except Exception as e:
                        self.logger.error(f"Error processing item: {e}")
                        item_id = item.get('id') or str(item.get('path', ''))
                        self.log_action('item_error', {
                            'item_id': item_id,
                            'error': str(e)
                        })

            except Exception as e:
                self.logger.error(f"Error in check loop: {e}")
                self.log_action('check_error', {'error': str(e)})

            # Sleep until next check
            time.sleep(self.check_interval)

        self.logger.info(f"{self.name} stopped")


# Example usage when run directly
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Base Watcher')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')

    args = parser.parse_args()

    # This would be subclassed for actual watchers
    print(f"Base watcher initialized with vault: {args.vault}")
    print("This is a template - implement a specific watcher class")
