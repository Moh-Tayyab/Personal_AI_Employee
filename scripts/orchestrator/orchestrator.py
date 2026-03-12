#!/usr/bin/env python3
"""
Orchestrator - Master process for Personal AI Employee
Manages watchers, triggers Claude, handles task routing
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import logging
import signal
import os

class Orchestrator:
    """Main orchestrator for AI Employee"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.running = True
        self.processes = {}
        
        # Setup logging
        log_dir = self.vault_path / 'Logs' / 'orchestrator'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Orchestrator')
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info('Shutdown signal received')
        self.running = False
    
    def start_watcher(self, name: str, script: str):
        """Start a watcher process"""
        try:
            cmd = ['python3', str(script), str(self.vault_path)]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes[name] = proc
            self.logger.info(f'Started watcher: {name} (PID: {proc.pid})')
            
            # Save PID file
            pid_file = Path(f'/tmp/ai_employee_{name}.pid')
            pid_file.write_text(str(proc.pid))
            
        except Exception as e:
            self.logger.error(f'Failed to start watcher {name}: {e}')
    
    def check_needs_action(self):
        """Check for items needing action and trigger Claude"""
        needs_action = self.vault_path / 'Needs_Action'
        
        if not needs_action.exists():
            return
        
        # Count items by type
        items = {
            'bugs': list((needs_action / 'bugs').glob('*.md')) if (needs_action / 'bugs').exists() else [],
            'emails': list(needs_action.glob('EMAIL_*.md')),
            'whatsapp': list(needs_action.glob('WHATSAPP_*.md')),
            'files': list(needs_action.glob('FILE_*.md')),
        }
        
        total = sum(len(v) for v in items.values())
        
        if total > 0:
            self.logger.info(f'Found {total} items needing action')
            
            # Trigger Claude for processing
            self.trigger_claude(items)
    
    def trigger_claude(self, items: dict):
        """Trigger Claude Code to process items"""
        self.logger.info('Triggering Claude Code...')
        
        # Build prompt based on item types
        prompts = []
        
        if items['bugs']:
            prompts.append(f"Process {len(items['bugs'])} bug report(s) using /fix-ticket skill")
        
        if items['emails']:
            prompts.append(f"Process {len(items['emails'])} email(s) - read, categorize, draft responses")
        
        if items['whatsapp']:
            prompts.append(f"Process {len(items['whatsapp'])} WhatsApp message(s) - identify urgent, draft replies")
        
        if items['files']:
            prompts.append(f"Process {len(items['files'])} file(s) dropped for processing")
        
        if not prompts:
            return
        
        prompt = '. '.join(prompts) + '. Update Dashboard.md after processing.'
        
        try:
            # Run Claude Code
            cmd = [
                'claude',
                '--prompt', prompt,
                '--cwd', str(self.vault_path)
            ]
            
            self.logger.info(f'Running: {" ".join(cmd)}')
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.logger.info('Claude processing completed successfully')
            else:
                self.logger.error(f'Claude error: {result.stderr}')
                
        except subprocess.TimeoutExpired:
            self.logger.error('Claude processing timed out')
        except Exception as e:
            self.logger.error(f'Error triggering Claude: {e}')
    
    def check_approved(self):
        """Check approved folder and execute actions"""
        approved = self.vault_path / 'Approved'
        
        if not approved.exists():
            return
        
        approved_files = list(approved.glob('*.md'))
        
        for filepath in approved_files:
            self.logger.info(f'Processing approved file: {filepath.name}')
            
            # Read approval file to determine action type
            content = filepath.read_text()
            
            # Trigger Claude to execute approved action
            cmd = [
                'claude',
                '--prompt', f'Execute approved action in {filepath.name}. Read the file and perform the action using appropriate MCP servers.',
                '--cwd', str(self.vault_path)
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # Move to Done
                    done_folder = self.vault_path / 'Done' / 'approved'
                    done_folder.mkdir(parents=True, exist_ok=True)
                    filepath.rename(done_folder / filepath.name)
                    self.logger.info(f'Approved action completed: {filepath.name}')
                else:
                    self.logger.error(f'Error executing approved action: {result.stderr}')
                    
            except Exception as e:
                self.logger.error(f'Error processing approved file: {e}')
    
    def update_dashboard(self):
        """Update dashboard with current status"""
        dashboard = self.vault_path / 'Dashboard.md'
        
        if not dashboard.exists():
            return
        
        # Count items
        needs_action = self.vault_path / 'Needs_Action'
        done = self.vault_path / 'Done'
        pending_approval = self.vault_path / 'Pending_Approval'
        
        counts = {
            'needs_action': len(list(needs_action.glob('*.md'))) if needs_action.exists() else 0,
            'done_today': 0,
            'pending_approval': len(list(pending_approval.glob('*.md'))) if pending_approval.exists() else 0,
        }
        
        # Count today's completed
        if done.exists():
            today = datetime.now().strftime('%Y-%m-%d')
            for f in done.rglob('*.md'):
                if today in f.stem:
                    counts['done_today'] += 1
        
        # Update dashboard
        content = dashboard.read_text()
        
        # Update counts (simple string replacement)
        if '| **Pending Tasks** |' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '| **Pending Tasks** |' in line:
                    lines[i] = f'| **Pending Tasks** | {counts["needs_action"]} | {"✅" if counts["needs_action"] == 0 else "🟡"} |'
                elif '| **Completed Today** |' in line:
                    lines[i] = f'| **Completed Today** | {counts["done_today"]} | 📊 |'
                elif '| **Pending Approval** |' in line:
                    lines[i] = f'| **Pending Approval** | {counts["pending_approval"]} | ⏳ |'
            
            content = '\n'.join(lines)
            dashboard.write_text(content)
    
    def run(self):
        """Main orchestrator loop"""
        self.logger.info('=' * 50)
        self.logger.info('Personal AI Employee Orchestrator Starting')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info('=' * 50)
        
        # Start watchers
        watcher_scripts = [
            ('filesystem', self.vault_path.parent / 'scripts' / 'watchers' / 'filesystem_watcher.py'),
            ('bug', self.vault_path.parent / 'scripts' / 'watchers' / 'bug_watcher.py'),
        ]
        
        for name, script in watcher_scripts:
            if script.exists():
                self.start_watcher(name, script)
            else:
                self.logger.warning(f'Watcher script not found: {script}')
        
        # Main loop
        last_check = 0
        last_dashboard_update = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check for items needing action every 30 seconds
                if current_time - last_check >= 30:
                    self.check_needs_action()
                    self.check_approved()
                    last_check = current_time
                
                # Update dashboard every 5 minutes
                if current_time - last_dashboard_update >= 300:
                    self.update_dashboard()
                    last_dashboard_update = current_time
                
                # Check watcher health
                for name, proc in list(self.processes.items()):
                    if proc.poll() is not None:
                        self.logger.warning(f'Watcher {name} died, restarting...')
                        # Restart watcher
                        script = next(s for n, s in watcher_scripts if n == name)
                        self.start_watcher(name, script)
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f'Error in orchestrator loop: {e}')
                time.sleep(5)
        
        # Shutdown
        self.logger.info('Shutting down orchestrator...')
        for name, proc in self.processes.items():
            proc.terminate()
            self.logger.info(f'Stopped watcher: {name}')
        
        self.logger.info('Orchestrator stopped')


if __name__ == '__main__':
    vault = sys.argv[1] if len(sys.argv) > 1 else '../vault'
    orchestrator = Orchestrator(vault)
    orchestrator.run()
