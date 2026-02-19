"""
Agent Coordination System - Cloud + Local Agent Communication

This module implements the coordination between Cloud and Local agents using:
- Claim-by-move pattern for work distribution
- Delegation via file-based communication
- Single-writer rule for critical files

Usage:
    from scripts.agent_coordinator import AgentCoordinator
"""

import os
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgentCoordinator")


class AgentCoordinator:
    """
    Coordinates work between Cloud and Local agents.

    Work Zones:
    - Cloud owns: Email triage, social drafts, scheduling
    - Local owns: WhatsApp, payments, approvals, final send/post
    """

    def __init__(self, vault_path: str, agent_name: str):
        self.vault_path = Path(vault_path)
        self.agent_name = agent_name

        # Define domain ownership
        self.cloud_domains = ['email', 'calendar', 'social', 'scheduling']
        self.local_domains = ['whatsapp', 'payments', 'banking', 'approvals']

        # Create required directories
        self.in_progress = self.vault_path / 'In_Progress' / agent_name
        self.updates = self.vault_path / 'Updates'
        self.needs_action = self.vault_path / 'Needs_Action'

        for d in [self.in_progress, self.updates]:
            d.mkdir(parents=True, exist_ok=True)

    def can_handle(self, item_type: str) -> bool:
        """Check if this agent can handle this item type."""
        if self.agent_name == 'cloud':
            return any(domain in item_type.lower() for domain in self.cloud_domains)
        elif self.agent_name == 'local':
            return any(domain in item_type.lower() for domain in self.local_domains)
        return True  # Shared agent can handle anything

    def claim_item(self, item: Path) -> bool:
        """
        Claim an item by moving it to In_Progress.

        Returns True if claim successful (first agent wins).
        Returns False if already claimed by another agent.
        """
        # Check if item is already claimed
        claimed_by = self._get_claimant(item)
        if claimed_by and claimed_by != self.agent_name:
            logger.info(f"Item {item.name} already claimed by {claimed_by}")
            return False

        # Move to our In_Progress folder
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = self.in_progress / f"{item.stem}_{timestamp}{item.suffix}"

        try:
            shutil.move(str(item), str(dest))
            logger.info(f"Agent '{self.agent_name}' claimed {item.name} -> {dest.name}")

            # Update claim metadata
            self._save_claim(item.name, dest.name)

            return True
        except Exception as e:
            logger.error(f"Failed to claim {item.name}: {e}")
            return False

    def release_item(self, item_name: str):
        """Release a claimed item back to Needs_Action."""
        for item in self.in_progress.glob('*'):
            if item.stem in item_name:
                dest = self.needs_action / item.name
                shutil.move(str(item), str(dest))
                logger.info(f"Agent '{self.agent_name}' released {item.name}")
                self._remove_claim(item_name)
                return

    def complete_item(self, item_name: str, result: str = None):
        """Mark an item as complete, move to Done."""
        done_folder = self.vault_path / 'Done'
        done_folder.mkdir(exist_ok=True)

        for item in self.in_progress.glob('*'):
            if item.stem in item_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                dest = done_folder / f"{item.stem}_{timestamp}{item.suffix}"

                # Add completion metadata
                content = item.read_text()
                content += f"\n\n---\nCompleted by: {self.agent_name}\nCompleted: {datetime.now().isoformat()}\n"
                if result:
                    content += f"Result: {result}\n"

                dest.write_text(content)
                item.unlink()

                logger.info(f"Agent '{self.agent_name}' completed {item.name}")
                self._remove_claim(item_name)
                return

    def write_update(self, update_type: str, content: str):
        """Write an update to the Updates folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        update_file = self.updates / f"{update_type}_{timestamp}.md"

        update_file.write_text(f"""---
type: {update_type}
agent: {self.agent_name}
timestamp: {datetime.now().isoformat()}
---

{content}
""")
        logger.info(f"Agent '{self.agent_name}' wrote update: {update_type}")

        return update_file

    def read_updates(self, since: datetime = None) -> List[Dict]:
        """Read updates from the other agent."""
        updates = []

        for update_file in self.updates.glob('*.md'):
            try:
                content = update_file.read_text()

                # Parse metadata
                in_frontmatter = False
                metadata = {}
                for line in content.split('\n'):
                    if line.strip() == '---':
                        if not in_frontmatter:
                            in_frontmatter = True
                        else:
                            break
                    elif ':' in line and in_frontmatter:
                        key, val = line.split(':', 1)
                        metadata[key.strip()] = val.strip()

                # Filter by time
                if since:
                    update_time = datetime.fromisoformat(metadata.get('timestamp', ''))
                    if update_time < since:
                        continue

                # Filter out own updates
                if metadata.get('agent') == self.agent_name:
                    continue

                updates.append({
                    'file': str(update_file),
                    'type': metadata.get('type', 'unknown'),
                    'content': content,
                    'timestamp': metadata.get('timestamp', '')
                })

            except Exception as e:
                logger.error(f"Error reading update {update_file}: {e}")

        return sorted(updates, key=lambda x: x['timestamp'], reverse=True)

    def merge_dashboard(self):
        """Merge updates into Dashboard.md (Local only)."""
        if self.agent_name != 'local':
            logger.warning("Only Local agent should merge Dashboard")
            return

        dashboard = self.vault_path / 'Dashboard.md'
        if not dashboard.exists():
            return

        # Read current dashboard
        current = dashboard.read_text()

        # Get recent updates
        updates = self.read_updates()

        # Add update summary
        if updates:
            update_summary = "\n## Recent Cloud Updates\n\n"
            for update in updates[:5]:
                update_summary += f"- [{update['timestamp']}] {update['type']}\n"

            # Append to dashboard
            current += update_summary
            dashboard.write_text(current)

            logger.info("Dashboard merged with updates")

    def _get_claimant(self, item: Path) -> Optional[str]:
        """Check which agent claimed an item."""
        claims_file = self.vault_path / '.claims.json'

        if claims_file.exists():
            with open(claims_file) as f:
                claims = json.load(f)

            item_name = item.stem
            for agent, items in claims.items():
                if any(item_name in i for i in items):
                    return agent

        return None

    def _save_claim(self, original_name: str, claimed_name: str):
        """Save claim metadata."""
        claims_file = self.vault_path / '.claims.json'

        claims = {}
        if claims_file.exists():
            with open(claims_file) as f:
                claims = json.load(f)

        if self.agent_name not in claims:
            claims[self.agent_name] = []

        claims[self.agent_name].append({
            'original': original_name,
            'claimed': claimed_name,
            'timestamp': datetime.now().isoformat()
        })

        with open(claims_file, 'w') as f:
            json.dump(claims, f, indent=2)

    def _remove_claim(self, item_name: str):
        """Remove claim metadata."""
        claims_file = self.vault_path / '.claims.json'

        if claims_file.exists():
            with open(claims_file) as f:
                claims = json.load(f)

            if self.agent_name in claims:
                claims[self.agent_name] = [
                    c for c in claims[self.agent_name]
                    if item_name not in c.get('original', '')
                ]

                with open(claims_file, 'w') as f:
                    json.dump(claims, f, indent=2)

    def get_status(self) -> Dict:
        """Get current agent status."""
        in_progress_items = list(self.in_progress.glob('*'))

        return {
            'agent': self.agent_name,
            'domains': self.cloud_domains if self.agent_name == 'cloud' else self.local_domains,
            'in_progress': len(in_progress_items),
            'items': [i.name for i in in_progress_items]
        }


class DistributedLock:
    """Simple file-based distributed lock."""

    def __init__(self, lock_path: Path, timeout: int = 30):
        self.lock_path = lock_path
        self.timeout = timeout

    def acquire(self, owner: str) -> bool:
        """Acquire the lock."""
        start = time.time()

        while (time.time() - start) < self.timeout:
            if not self.lock_path.exists():
                self.lock_path.write_text(json.dumps({
                    'owner': owner,
                    'timestamp': datetime.now().isoformat()
                }))
                return True
            time.sleep(1)

        return False

    def release(self, owner: str):
        """Release the lock if we own it."""
        if self.lock_path.exists():
            with open(self.lock_path) as f:
                lock_data = json.load(f)

            if lock_data.get('owner') == owner:
                self.lock_path.unlink()

    def is_locked(self) -> bool:
        """Check if lock is held."""
        return self.lock_path.exists()


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python agent_coordinator.py <vault_path> <agent_name>")
        sys.exit(1)

    vault = sys.argv[1]
    agent = sys.argv[2]

    coordinator = AgentCoordinator(vault, agent)
    print(f"Agent '{agent}' status:", coordinator.get_status())
