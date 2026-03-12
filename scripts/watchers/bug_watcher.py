#!/usr/bin/env python3
"""
Bug Report Watcher - Monitors for new bug reports
Triggers fix-ticket skill when bugs are detected
"""

import hashlib
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher


class BugWatcher(BaseWatcher):
    """Watch for new bug reports in Needs_Action/bugs folder"""
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        
        self.bugs_folder = self.needs_action / 'bugs'
        self.bugs_folder.mkdir(parents=True, exist_ok=True)
        
        self.processed_files = set()
        
        # Load already processed files
        done_folder = self.vault_path / 'Done' / 'bugs'
        if done_folder.exists():
            for f in done_folder.glob('*.md'):
                self.processed_files.add(f.stem)
    
    def check_for_updates(self) -> list:
        """Check for new bug report files"""
        new_bugs = []
        
        for bug_file in self.bugs_folder.glob('*.md'):
            if bug_file.stem not in self.processed_files:
                try:
                    content = bug_file.read_text()
                    bug_data = self.parse_bug_report(content, bug_file)
                    if bug_data:
                        new_bugs.append(bug_data)
                        self.processed_files.add(bug_file.stem)
                        self.logger.info(f'New bug detected: {bug_file.name}')
                except Exception as e:
                    self.logger.error(f'Error reading bug file {bug_file}: {e}')
        
        return new_bugs
    
    def parse_bug_report(self, content: str, filepath: Path) -> dict:
        """Parse bug report markdown"""
        lines = content.split('\n')
        
        bug = {
            'id': filepath.stem,
            'filepath': str(filepath),
            'priority': 'P2',  # Default
            'url': '',
            'description': '',
            'steps': [],
            'expected': '',
            'actual': '',
        }
        
        in_frontmatter = False
        in_steps = False
        current_section = None
        
        for line in lines:
            # Parse frontmatter
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            
            if in_frontmatter:
                if 'priority:' in line:
                    bug['priority'] = line.split(':')[1].strip()
                elif 'url:' in line:
                    bug['url'] = line.split(':')[1].strip()
            
            # Parse sections
            if line.startswith('## '):
                current_section = line[3:].strip().lower()
                in_steps = current_section == 'steps to reproduce'
                continue
            
            if current_section == 'bug Description':
                bug['description'] += line + '\n'
            elif current_section == 'steps to reproduce':
                if line.strip().startswith('- ') or line.strip().startswith('1.'):
                    bug['steps'].append(line.strip()[2:].strip())
            elif current_section == 'expected behavior':
                bug['expected'] += line + '\n'
            elif current_section == 'actual behavior':
                bug['actual'] += line + '\n'
        
        bug['description'] = bug['description'].strip()
        bug['expected'] = bug['expected'].strip()
        bug['actual'] = bug['actual'].strip()
        
        return bug
    
    def create_action_file(self, bug: dict) -> Path:
        """Create action file for bug (already exists, just log)"""
        self.write_log('bug_detected', {
            'bug_id': bug['id'],
            'priority': bug['priority'],
            'url': bug['url'],
        })
        
        # Return path to original bug file
        return Path(bug['filepath'])


if __name__ == '__main__':
    import sys
    vault = sys.argv[1] if len(sys.argv) > 1 else '../vault'
    watcher = BugWatcher(vault)
    watcher.run()
