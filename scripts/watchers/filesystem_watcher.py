#!/usr/bin/env python3
"""
Filesystem Watcher - Monitors directories for new files
Creates action files when files are added
"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from pathlib import Path
import hashlib
from datetime import datetime
from base_watcher import BaseWatcher

class FileDropHandler(FileSystemEventHandler):
    """Handle file drop events"""
    
    def __init__(self, needs_action_path: Path):
        self.needs_action = needs_action_path
        self.processed_hashes = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        
        # Skip hidden files and temp files
        if source.name.startswith('.') or source.suffix == '.tmp':
            return
        
        # Generate hash to avoid duplicates
        file_hash = hashlib.md5(source.read_bytes()).hexdigest()
        if file_hash in self.processed_hashes:
            return
        
        self.processed_hashes.add(file_hash)
        
        # Create action file
        self.create_action_file(source)
    
    def create_action_file(self, source: Path):
        """Create markdown action file for dropped file"""
        action_file = self.needs_action / f'FILE_{source.name}.md'
        
        content = f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
received: {datetime.now().isoformat()}
status: pending
---

# File Dropped for Processing

**Original File**: `{source.name}`
**Size**: {source.stat().st_size:,} bytes
**Received**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Content
```
{source.read_text()[:1000] if source.suffix in ['.txt', '.md', '.json', '.py', '.js', '.ts'] else '[Binary file - preview not available]'}
```

## Suggested Actions
- [ ] Review file content
- [ ] Process as needed
- [ ] Move to appropriate folder
- [ ] Archive after processing

## Notes
Add processing notes here...
'''
        
        action_file.write_text(content)
        print(f'Created action file: {action_file}')


class FilesystemWatcher(BaseWatcher):
    """Watch directories for new files"""
    
    def __init__(self, vault_path: str, watch_dirs: list = None):
        super().__init__(vault_path, check_interval=1)  # Watchdog is event-based
        
        self.watch_dirs = watch_dirs or [
            str(self.vault_path / 'Inbox'),
            str(self.vault_path / 'Drops'),
        ]
        
    def check_for_updates(self) -> list:
        """Not used - Watchdog is event-based"""
        return []
    
    def create_action_file(self, item) -> Path:
        """Not used - handled by FileDropHandler"""
        pass
    
    def run(self):
        """Start watchdog observer"""
        self.logger.info(f'Watching directories: {self.watch_dirs}')
        
        event_handler = FileDropHandler(self.needs_action)
        observer = Observer()
        
        for watch_dir in self.watch_dirs:
            path = Path(watch_dir)
            path.mkdir(parents=True, exist_ok=True)
            observer.schedule(event_handler, watch_dir, recursive=False)
            self.logger.info(f'Started watching: {watch_dir}')
        
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        
        observer.join()
        self.logger.info('Filesystem watcher stopped')


if __name__ == '__main__':
    import sys
    vault = sys.argv[1] if len(sys.argv) > 1 else '../vault'
    watcher = FilesystemWatcher(vault)
    watcher.run()
