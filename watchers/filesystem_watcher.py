"""
Filesystem Watcher - Monitors a drop folder for new files

Watches a specified directory for new files and creates action files
in the vault's Needs_Action folder.

Usage:
    python -m watchers.filesystem_watcher --vault ./vault --watch-path ./drop
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchers.base_watcher import BaseWatcher


class FileDropHandler(FileSystemEventHandler):
    """Handler for filesystem events."""

    def __init__(self, watcher):
        self.watcher = watcher

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return

        source = Path(event.src_path)

        # Skip temporary/hidden files
        if source.name.startswith('.') or source.name.startswith('~'):
            return

        # Skip certain extensions
        skip_extensions = {'.tmp', '.temp', '.crdownload', '.part'}
        if source.suffix.lower() in skip_extensions:
            return

        try:
            self.watcher.process_file(source)
        except Exception as e:
            self.watcher.logger.error(f"Error processing file {source}: {e}")


class FilesystemWatcher(BaseWatcher):
    """Watches a directory for new files."""

    def __init__(self, vault_path: str, watch_path: str):
        super().__init__(vault_path, check_interval=30, name="FilesystemWatcher")
        self.watch_path = Path(watch_path)
        self.watch_path.mkdir(parents=True, exist_ok=True)

        self.observer = Observer()
        handler = FileDropHandler(self)
        self.observer.schedule(handler, str(self.watch_path), recursive=False)

    def process_file(self, source: Path):
        """Process a new file."""
        # Wait a moment for file to be fully written
        import time
        time.sleep(0.5)

        # Determine file category
        category = self._categorize_file(source)

        # Create metadata file
        content = f"""---
type: file_drop
source: filesystem
original_name: {source.name}
size: {source.stat().st_size}
received: {datetime.now().isoformat()}
category: {category}
status: pending
---

# File Information

- **Original Name:** {source.name}
- **Size:** {source.stat().st_size:,} bytes
- **Type:** {source.suffix}
- **Category:** {category}

# Actions

- [ ] Review file content
- [ ] Categorize and file appropriately
- [ ] Extract actionable information (if applicable)
- [ ] Delete or archive original

## Notes
_AI Employee: Process this file according to its type and content._
"""

        # Copy to Needs_Action
        dest_name = f"FILE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{source.name}"
        dest = self.needs_action / dest_name
        shutil.copy2(source, dest)

        # Write metadata
        meta_path = self.needs_action / f"{dest_name}.md"
        meta_path.write_text(content)

        self.logger.info(f"Processed file: {source.name} -> {dest}")
        self.log_action('file_processed', {
            'source': str(source),
            'destination': str(dest)
        })

    def _categorize_file(self, file_path: Path) -> str:
        """Determine file category based on extension."""
        ext = file_path.suffix.lower()

        categories = {
            'document': {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'},
            'spreadsheet': {'.xls', '.xlsx', '.csv', '.ods'},
            'image': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'},
            'video': {'.mp4', '.mov', '.avi', '.mkv'},
            'audio': {'.mp3', '.wav', '.flac', '.aac'},
            'archive': {'.zip', '.tar', '.gz', '.rar', '.7z'},
            'code': {'.py', '.js', '.html', '.css', '.json', '.xml'},
        }

        for category, extensions in categories.items():
            if ext in extensions:
                return category

        return 'other'

    def check_for_updates(self) -> list:
        """Check for new files in the watch folder."""
        files = []
        for f in self.watch_path.iterdir():
            if f.is_file() and not f.name.startswith('.'):
                # Skip already processed files
                if str(f) not in self.get_processed_ids():
                    files.append({'id': str(f), 'path': f})
        return files

    def create_action_file(self, item) -> Path:
        """Create action file for existing files."""
        return self.process_file(item['path'])

    def run(self):
        """Run the filesystem watcher."""
        self.logger.info(f"Starting filesystem watcher on: {self.watch_path}")
        self.observer.start()

        try:
            super().run()
        finally:
            self.observer.stop()
            self.observer.join()


def main():
    """Main entry point for Filesystem Watcher."""
    import argparse

    parser = argparse.ArgumentParser(description='Filesystem Watcher')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--watch-path', required=True, help='Path to watch')

    args = parser.parse_args()

    watcher = FilesystemWatcher(
        vault_path=args.vault,
        watch_path=args.watch_path
    )
    watcher.run()


if __name__ == "__main__":
    main()
