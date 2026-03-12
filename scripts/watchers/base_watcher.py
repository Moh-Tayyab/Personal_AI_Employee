#!/usr/bin/env python3
"""
Base Watcher - Abstract base class for all watchers
Monitors external sources and creates action files in Needs_Action folder
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
import json

class BaseWatcher(ABC):
    """Base class for all watcher scripts"""
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize watcher
        
        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        
        # Setup logging
        log_dir = self.vault_path / 'Logs' / 'watchers'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'{self.__class__.__name__.lower()}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure directories exist
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Create required directories"""
        dirs = [
            self.needs_action,
            self.vault_path / 'Plans',
            self.vault_path / 'Done',
            self.vault_path / 'Logs',
            self.vault_path / 'Attachments',
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process
        
        Returns:
            List of new items (dicts with item data)
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create action file in Needs_Action folder
        
        Args:
            item: Item data from check_for_updates
            
        Returns:
            Path to created file
        """
        pass
    
    def run(self):
        """Main watcher loop"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    try:
                        filepath = self.create_action_file(item)
                        self.logger.info(f'Created action file: {filepath}')
                    except Exception as e:
                        self.logger.error(f'Error creating action file: {e}')
                        
            except Exception as e:
                self.logger.error(f'Error in check cycle: {e}')
                time.sleep(5)  # Wait before retrying
            
            time.sleep(self.check_interval)
    
    def write_log(self, action: str, details: dict):
        """Write action to log file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'watcher': self.__class__.__name__,
            'action': action,
            'details': details
        }
        
        log_file = self.vault_path / 'Logs' / f'watchers/{datetime.now().strftime("%Y-%m-%d")}.json'
        
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except:
                logs = []
        
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))
