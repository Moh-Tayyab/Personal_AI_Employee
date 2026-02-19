"""
Orchestrator - Main coordination script for the AI Employee

The orchestrator manages the coordination between watchers, Claude Code,
and MCP servers. It handles scheduling, folder watching, and the
Ralph Wiggum persistence loop.

Usage:
    python orchestrator.py --vault ./vault
"""

import time
import subprocess
import logging
import signal
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Orchestrator")


class Orchestrator:
    """Main orchestrator for the AI Employee."""

    def __init__(self, vault_path: str, dry_run: bool = True):
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run
        self.running = True
        self.ralph_mode = False
        self.current_task = None

        # Directories
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        for d in [self.needs_action, self.plans, self.done,
                  self.pending_approval, self.approved, self.rejected, self.logs]:
            d.mkdir(parents=True, exist_ok=True)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def check_needs_action(self) -> list:
        """Check for items in Needs_Action folder."""
        items = []
        for f in self.needs_action.glob('*.md'):
            # Skip metadata files
            if f.stat().st_size > 0:
                items.append(f)
        return items

    def check_pending_approval(self) -> list:
        """Check for items needing approval."""
        items = []
        for f in self.pending_approval.glob('*.md'):
            items.append(f)
        return items

    def check_approved(self) -> list:
        """Check for approved items ready for execution."""
        items = []
        for f in self.approved.glob('*.md'):
            items.append(f)
        return items

    def trigger_claude(self, prompt: str) -> bool:
        """Trigger Claude Code to process a task."""
        logger.info(f"Triggering Claude with prompt: {prompt[:100]}...")

        if self.dry_run:
            logger.info("[DRY RUN] Would execute Claude with prompt")
            logger.info(f"Prompt: {prompt}")
            return True

        try:
            # Run Claude Code with the prompt
            # Use --cwd to point to vault
            result = subprocess.run(
                ['claude', '--print', '--cwd', str(self.vault_path), prompt],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                logger.info("Claude executed successfully")
                logger.info(f"Claude response: {result.stdout[:200]}...")
                return True
            else:
                logger.error(f"Claude error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Claude execution timed out")
            return False
        except FileNotFoundError:
            logger.error("Claude Code not found in PATH")
            return False
        except Exception as e:
            logger.error(f"Error running Claude: {e}")
            return False

    def create_plan(self, source_item: Path) -> Path:
        """Create a Plan.md file for an item in Needs_Action."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_name = f"PLAN_{timestamp}_{source_item.stem[:30]}.md"
        plan_file = self.plans / plan_name

        # Read the source item to get context
        content = source_item.read_text()

        # Extract type and key info
        item_type = 'unknown'
        from_line = 'Unknown'
        subject_line = 'No subject'

        for line in content.split('\n'):
            if line.startswith('type:'):
                item_type = line.split(':')[1].strip()
            elif line.startswith('from:'):
                from_line = line.split(':')[1].strip()
            elif line.startswith('subject:'):
                subject_line = line.split(':')[1].strip()

        # Create plan content
        plan_content = f"""---
type: plan
source_file: {source_item.name}
created: {datetime.now().isoformat()}
status: in_progress
---

# Plan for: {subject_line}

## Source
- **Type:** {item_type}
- **From:** {from_line}
- **Original File:** {source_item.name}

## Analysis

_AI Employee: Analyze the item and determine required actions._

## Action Items

- [ ] Review the item in Needs_Action/{source_item.name}
- [ ] Determine required actions based on Company_Handbook.md
- [ ] Execute appropriate actions
- [ ] If approval needed, create approval request in Pending_Approval/
- [ ] Move completed items to Done/

## Notes
_Created by Orchestrator at {datetime.now().isoformat()}_
"""

        plan_file.write_text(plan_content)
        logger.info(f"Created plan: {plan_file.name}")
        return plan_file

    def move_to_in_progress(self, item: Path):
        """Move item to In_Progress folder (claim ownership)."""
        in_progress = self.vault_path / 'In_Progress'
        in_progress.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = in_progress / f"{item.stem}_{timestamp}{item.suffix}"
        item.rename(dest)
        logger.info(f"Moved to In_Progress: {dest.name}")

    def process_approved_item(self, item: Path) -> bool:
        """Process an approved item using MCP servers."""
        logger.info(f"Processing approved item: {item.name}")

        if self.dry_run:
            logger.info(f"[DRY RUN] Would process: {item.name}")
            return True

        try:
            # Read the approval file to determine action
            content = item.read_text()

            # Extract action type from frontmatter
            lines = content.split('\n')
            action_type = None
            for line in lines:
                if line.startswith('action:'):
                    action_type = line.split(':')[1].strip()
                    break

            # Route to appropriate MCP handler
            if action_type == 'send_email':
                return self._handle_email_action(content)
            elif action_type == 'payment':
                return self._handle_payment_action(content)
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return False

        except Exception as e:
            logger.error(f"Error processing approved item: {e}")
            return False

    def _handle_email_action(self, content: str) -> bool:
        """Handle email sending action."""
        logger.info("Handling email action")
        # This would call the email MCP server
        return True

    def _handle_payment_action(self, content: str) -> bool:
        """Handle payment action."""
        logger.info("Handling payment action")
        # This would call the payment MCP server
        # NEVER auto-approve payments
        return True

    def move_to_done(self, item: Path):
        """Move item to Done folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = self.done / f"{item.stem}_{timestamp}{item.suffix}"
        item.rename(dest)
        logger.info(f"Moved to Done: {dest.name}")

    def move_to_rejected(self, item: Path):
        """Move item to Rejected folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = self.rejected / f"{item.stem}_{timestamp}{item.suffix}"
        item.rename(dest)
        logger.info(f"Moved to Rejected: {dest.name}")

    def log_activity(self, activity_type: str, details: dict):
        """Log activity to daily log file."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': activity_type,
            'details': details
        }

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

    def generate_morning_briefing(self):
        """Generate Monday morning CEO briefing."""
        logger.info("Generating morning briefing...")

        # This would be handled by Claude
        prompt = """
        Generate a Monday Morning CEO Briefing by:
        1. Reading Business_Goals.md for targets
        2. Reading Logs/ for completed tasks this week
        3. Reading Accounting/ for transactions
        4. Writing a summary to Briefings/{date}_Monday_Briefing.md
        """

        self.trigger_claude(prompt)

    def run_ralph_loop(self, task_prompt: str, max_iterations: int = 10):
        """
        Run the Ralph Wiggum persistence loop.

        This keeps Claude running until a task is marked complete.
        """
        logger.info(f"Starting Ralph Wiggum loop: {task_prompt}")
        self.ralph_mode = True

        iteration = 0
        while iteration < max_iterations and self.running:
            iteration += 1
            logger.info(f"Ralph loop iteration {iteration}/{max_iterations}")

            # Check if task is done
            done_items = list(self.done.glob('*'))
            if done_items:
                logger.info("Task marked complete, exiting Ralph loop")
                break

            # Trigger Claude to continue working
            success = self.trigger_claude(task_prompt)

            if not success:
                logger.error("Claude failed, retrying...")
                time.sleep(5)

            # Small delay between iterations
            time.sleep(2)

        self.ralph_mode = False
        logger.info("Ralph Wiggum loop complete")

    def run(self):
        """Main orchestration loop."""
        logger.info(f"Starting Orchestrator (dry_run={self.dry_run})")

        while self.running:
            try:
                # Check Needs_Action
                needs_action = self.check_needs_action()
                if needs_action:
                    logger.info(f"Found {len(needs_action)} items in Needs_Action")
                    for item in needs_action:
                        # Create a Plan.md first
                        self.create_plan(item)

                        # Then trigger Claude to process
                        prompt = f"""Process the item in {item.name}.

The plan has been created in Plans/ folder.
1. Read the item in Needs_Action/{item.name}
2. Read Company_Handbook.md for rules
3. Determine required actions
4. If approval needed, create request in Pending_Approval/
5. When complete, move original to Done/ and update plan status to completed
"""
                        self.trigger_claude(prompt)
                        self.move_to_in_progress(item)

                # Check Approved folder
                approved = self.check_approved()
                if approved:
                    logger.info(f"Found {len(approved)} approved items to execute")
                    for item in approved:
                        if self.process_approved_item(item):
                            self.move_to_done(item)

                # Check Pending Approval
                pending = self.check_pending_approval()
                if pending:
                    logger.info(f"Found {len(pending)} items pending approval")

                # Log heartbeat
                self.log_activity('heartbeat', {'status': 'running'})

                # Sleep before next check
                time.sleep(30)

            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}")
                self.log_activity('error', {'error': str(e)})
                time.sleep(10)

        logger.info("Orchestrator stopped")

    def schedule_task(self, task: str, cron_expr: str):
        """Schedule a task using cron-like syntax."""
        # Simple scheduling - in production use proper cron
        logger.info(f"Scheduling task: {task} with schedule: {cron_expr}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Run in dry-run mode (no external actions)')
    parser.add_argument('--live', action='store_false', dest='dry_run',
                        help='Run in live mode (execute real actions)')

    args = parser.parse_args()

    orchestrator = Orchestrator(
        vault_path=args.vault,
        dry_run=args.dry_run
    )

    orchestrator.run()


if __name__ == "__main__":
    main()
