"""
Vault Sync - Synchronize vault between Cloud and Local using Git

This script handles bidirectional vault synchronization:
- Cloud pushes changes to Git
- Local pulls changes from Git
- Never sync secrets, sessions, credentials

Usage:
    python scripts/vault_sync.py --vault ./vault --mode pull  # Local
    python scripts/vault_sync.py --vault ./vault --mode push  # Cloud
"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import argparse
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VaultSync")


class VaultSync:
    """Synchronize vault using Git."""

    # Files/directories to NEVER sync (security)
    SECRETS = [
        '.env',
        'secrets/',
        '*.session',
        '*.cookie',
        'credentials.json',
        'token.json',
        '.processed_ids.json',
        '*.log',
    ]

    def __init__(self, vault_path: str, git_repo: str = None):
        self.vault_path = Path(vault_path)
        self.git_dir = self.vault_path / '.git'
        self.last_sync_file = self.vault_path / '.last_sync.json'

    def is_git_repo(self) -> bool:
        """Check if vault is a Git repository."""
        return self.git_dir.exists()

    def init_repo(self, remote_url: str = None):
        """Initialize Git repository in vault."""
        if self.is_git_repo():
            logger.info("Git repo already exists")
            return

        # Create .gitignore for secrets
        gitignore = self.vault_path / '.gitignore'
        if not gitignore.exists():
            gitignore.write_text('\n'.join(self.SECRETS))
            logger.info("Created .gitignore")

        # Initialize repo
        subprocess.run(['git', 'init'], cwd=self.vault_path, check=True)
        subprocess.run(['git', 'lfs', 'track', '*.md'], cwd=self.vault_path, check=False)

        if remote_url:
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=self.vault_path, check=True)

        # Initial commit
        subprocess.run(['git', 'add', '.'], cwd=self.vault_path, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial vault commit'], cwd=self.vault_path, check=True)

        logger.info("Git repository initialized")

    def get_last_sync(self) -> datetime:
        """Get last sync timestamp."""
        if self.last_sync_file.exists():
            with open(self.last_sync_file) as f:
                data = json.load(f)
                return datetime.fromisoformat(data['timestamp'])
        return datetime.min

    def save_last_sync(self):
        """Save last sync timestamp."""
        with open(self.last_sync_file, 'w') as f:
            json.dump({'timestamp': datetime.now().isoformat()}, f)

    def get_changed_files(self) -> list:
        """Get list of changed files since last sync."""
        last = self.get_last_sync()

        result = subprocess.run(
            ['git', 'log', '--since', last.isoformat(), '--name-only', '--pretty=format:'],
            cwd=self.vault_path,
            capture_output=True,
            text=True
        )

        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        return list(set(files))

    def pull(self) -> bool:
        """Pull changes from remote."""
        if not self.is_git_repo():
            logger.error("Not a Git repository. Run init first.")
            return False

        try:
            # Fetch and merge
            subprocess.run(['git', 'fetch', 'origin'], cwd=self.vault_path, check=True)

            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.save_last_sync()
                logger.info("Pull successful")
                return True
            else:
                logger.warning(f"Pull had conflicts: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Pull failed: {e}")
            return False

    def push(self, commit_message: str = None) -> bool:
        """Push changes to remote."""
        if not self.is_git_repo():
            logger.error("Not a Git repository. Run init first.")
            return False

        try:
            # Stage all files (respecting .gitignore)
            subprocess.run(['git', 'add', '-u'], cwd=self.vault_path, check=True)

            # Check if there are changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )

            if not result.stdout.strip():
                logger.info("No changes to push")
                return True

            # Commit
            msg = commit_message or f"Auto-sync {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(['git', 'commit', '-m', msg], cwd=self.vault_path, check=True)

            # Push
            subprocess.run(['git', 'push', 'origin', 'main'], cwd=self.vault_path, check=True)

            self.save_last_sync()
            logger.info("Push successful")
            return True

        except Exception as e:
            logger.error(f"Push failed: {e}")
            return False

    def sync(self, mode: str = 'pull') -> bool:
        """Main sync function."""
        if mode == 'pull':
            return self.pull()
        elif mode == 'push':
            return self.push()
        else:
            logger.error(f"Unknown mode: {mode}")
            return False

    def get_status(self) -> dict:
        """Get sync status."""
        if not self.is_git_repo():
            return {'status': 'not_initialized'}

        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=self.vault_path,
            capture_output=True,
            text=True
        )

        changes = [l for l in result.stdout.split('\n') if l.strip()]

        # Get ahead/behind from remote
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--left-right', '--count', 'HEAD...origin/main'],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                ahead, behind = result.stdout.strip().split()
            else:
                ahead, behind = '0', '0'
        except:
            ahead, behind = '0', '0'

        return {
            'status': 'ok',
            'changes': len(changes),
            'ahead': ahead,
            'behind': behind,
            'last_sync': str(self.get_last_sync())
        }


def main():
    parser = argparse.ArgumentParser(description='Vault Sync')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--mode', choices=['push', 'pull'], default='pull', help='Sync mode')
    parser.add_argument('--init', help='Initialize with Git remote URL')
    parser.add_argument('--status', action='store_true', help='Show sync status')

    args = parser.parse_args()

    sync = VaultSync(args.vault)

    if args.init:
        sync.init_repo(args.init)
    elif args.status:
        print(json.dumps(sync.get_status(), indent=2))
    else:
        sync.sync(args.mode)


if __name__ == "__main__":
    main()
