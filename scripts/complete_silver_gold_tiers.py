#!/usr/bin/env python3
"""
Silver and Gold Tier Completion using Agent Teams

This script launches specialized Claude agents to complete all Silver and Gold tier requirements.
Each agent focuses on their domain of expertise while coordinating through the vault structure.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vault/Logs/agent_teams_completion.log')
    ]
)
logger = logging.getLogger("TierCompletionAgent")

class TierCompletionAgent:
    """Orchestrates agent teams to complete Silver and Gold tiers."""

    def __init__(self, vault_path: str, dry_run: bool = True):
        self.vault_path = Path(vault_path).resolve()
        self.dry_run = dry_run
        self.config_path = Path("config/agent_teams_config.json")
        
        # Vault directories
        self.needs_action = self.vault_path / "Needs_Action"
        self.plans = self.vault_path / "Plans"
        self.done = self.vault_path / "Done"
        self.pending_approval = self.vault_path / "Pending_Approval"
        self.approved = self.vault_path / "Approved"
        self.logs = self.vault_path / "Logs"
        self.briefings = self.vault_path / "Briefings"
        
        # Ensure directories exist
        for dir_path in [self.needs_action, self.plans, self.done, 
                         self.pending_approval, self.approved, self.logs, self.briefings]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self.load_config()
        
        logger.info(f"Initialized TierCompletionAgent with vault: {self.vault_path}")
        logger.info(f"Dry run mode: {self.dry_run}")

    def load_config(self) -> Dict:
        """Load agent teams configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Config file not found: {self.config_path}")
            return {}

    def get_silver_tier_tasks(self) -> List[Dict]:
        """Get all tasks related to Silver tier completion."""
        tasks = []
        
        # Check for email tasks
        email_dir = self.needs_action / "email"
        if email_dir.exists():
            for email_file in email_dir.glob("*.md"):
                tasks.append({
                    "type": "email",
                    "file": str(email_file),
                    "agent": "email-specialist",
                    "tier": "silver"
                })
        
        # Check for social media tasks
        for social_file in self.needs_action.glob("SOCIAL_*.md"):
            tasks.append({
                "type": "social",
                "file": str(social_file),
                "agent": "social-media-manager",
                "tier": "silver"
            })
        
        # Check for general tasks that need approval workflow
        for item_file in self.needs_action.glob("*.md"):
            if "EMAIL_" in item_file.name or "SOCIAL_" in item_file.name:
                continue  # Already counted
            
            content = item_file.read_text()
            if "email" in content.lower() or "send" in content.lower():
                tasks.append({
                    "type": "email",
                    "file": str(item_file),
                    "agent": "email-specialist",
                    "tier": "silver"
                })
            elif "social" in content.lower() or "post" in content.lower():
                tasks.append({
                    "type": "social",
                    "file": str(item_file),
                    "agent": "social-media-manager",
                    "tier": "silver"
                })
        
        return tasks

    def get_gold_tier_tasks(self) -> List[Dict]:
        """Get all tasks related to Gold tier completion."""
        tasks = []
        
        # Check for accounting/invoice tasks
        for invoice_file in self.needs_action.glob("INVOICE_*.md"):
            tasks.append({
                "type": "accounting",
                "file": str(invoice_file),
                "agent": "accounting-specialist",
                "tier": "gold"
            })
        
        # Check for LinkedIn-specific tasks
        for linkedin_file in self.needs_action.glob("*linkedin*.md"):
            tasks.append({
                "type": "linkedin",
                "file": str(linkedin_file),
                "agent": "linkedin-manager",
                "tier": "gold"
            })
        
        # Check for research tasks (for CEO briefing)
        for research_file in self.needs_action.glob("RESEARCH_*.md"):
            tasks.append({
                "type": "research",
                "file": str(research_file),
                "agent": "executive-reporter",
                "tier": "gold"
            })
        
        return tasks

    def create_agent_prompt(self, task: Dict) -> str:
        """Create a specialized prompt for the agent based on task type."""
        task_type = task["type"]
        agent = task["agent"]
        file_path = task["file"]
        
        prompts = {
            "email": f"""
# Email Specialist Agent - Silver Tier Task

## Your Role
You are an Email Specialist agent responsible for processing emails efficiently.

## Task
Process the email file: {file_path}

## Instructions
1. Read and analyze the email content
2. Determine the appropriate response or action
3. Check if approval is needed (multiple recipients, sensitive content)
4. If approval needed:
   - Create approval request in vault/Pending_Approval/Emails/
   - Include draft response and reasoning
5. If no approval needed:
   - Draft the response in vault/Drafts/
   - Or send directly if within autonomy level
6. Move processed item to vault/Done/
7. Log your actions to vault/Logs/

## Autonomy Level
- L2: Draft only, send requires approval
- Auto-approve: Simple responses, single recipient
- Require approval: Multiple recipients, partnerships, sensitive topics

## Success Criteria
- Email analyzed and understood
- Appropriate response drafted or sent
- Approval workflow followed correctly
- Action logged and item moved to Done/

## File to Process
Read the file at: {file_path}
""",
            
            "social": f"""
# Social Media Manager Agent - Silver Tier Task

## Your Role
You are a Social Media Manager responsible for creating and publishing content.

## Task
Process the social media task: {file_path}

## Instructions
1. Read and analyze the social media requirements
2. Determine which platform(s) to post to (LinkedIn, Twitter, Facebook)
3. Create platform-optimized content
4. Check if approval is needed:
   - Routine posts: Auto-approve
   - Announcements, partnerships: Require approval
5. If approval needed:
   - Create approval request in vault/Pending_Approval/Social/
   - Include draft content and target platform
6. If approved or auto-approved:
   - Post using appropriate MCP server
   - LinkedIn: python -m mcp.linkedin.server
   - Twitter: python -m mcp.twitter.server
   - Facebook: python -m mcp.facebook.server
7. Move processed item to vault/Done/
8. Log your actions to vault/Logs/

## Autonomy Level
- L3: Auto-post routine content
- Require approval: Major announcements, partnerships

## Success Criteria
- Content created for appropriate platform
- Approval workflow followed
- Post published successfully
- Action logged and item moved to Done/

## File to Process
Read the file at: {file_path}
""",
            
            "accounting": f"""
# Accounting Specialist Agent - Gold Tier Task

## Your Role
You are an Accounting Specialist responsible for managing financial operations via Odoo.

## Task
Process the invoice/expense: {file_path}

## Instructions
1. Read and extract invoice details:
   - Vendor/Customer name
   - Invoice amount
   - Invoice date
   - Line items and descriptions
   - Payment terms
2. Create invoice in Odoo via MCP server:
   - python -m mcp.odoo.server
   - Use create_invoice method
3. Check amount against approval threshold ($500):
   - If <= $500: Auto-validate
   - If > $500: Create approval request
4. If approval needed:
   - Create approval request in vault/Pending_Approval/Accounting/
   - Include invoice details and amount
5. If approved or auto-approved:
   - Validate invoice in Odoo
   - Categorize expense appropriately
6. Move processed item to vault/Done/
7. Log your actions to vault/Logs/

## Autonomy Level
- L2: Create drafts, validate requires approval for >$500
- Auto-validate: Expenses <= $500

## Success Criteria
- Invoice details extracted accurately
- Invoice created in Odoo
- Approval workflow followed
- Expense categorized correctly
- Action logged and item moved to Done/

## File to Process
Read the file at: {file_path}
""",
            
            "linkedin": f"""
# LinkedIn Manager Agent - Gold Tier Task

## Your Role
You are a LinkedIn Manager responsible for professional networking and content.

## Task
Process the LinkedIn task: {file_path}

## Instructions
1. Read and analyze the LinkedIn requirements
2. Create professional, engaging content:
   - Length: 150-300 words for optimal engagement
   - Tone: Professional but personable
   - Include relevant hashtags (3-5)
   - Add call-to-action if appropriate
3. Check session authentication:
   - Verify LinkedIn session exists in vault/secrets/linkedin_session/
4. Post to LinkedIn:
   - python -m mcp.linkedin.server
   - Use create_post method
   - Or schedule for optimal time (business hours, Tue-Thu)
5. Monitor for errors and retry if needed
6. Move processed item to vault/Done/
7. Log your actions to vault/Logs/

## Best Practices
- Post during business hours (9 AM - 5 PM weekdays)
- Use professional images if applicable
- Engage with comments within 24 hours
- Track post performance

## Success Criteria
- High-quality LinkedIn content created
- Post published successfully
- Engagement monitored
- Action logged and item moved to Done/

## File to Process
Read the file at: {file_path}
""",
            
            "research": f"""
# Executive Reporter Agent - Gold Tier Task

## Your Role
You are an Executive Reporter responsible for generating CEO briefings and research reports.

## Task
Process the research task: {file_path}

## Instructions
1. Read and analyze the research requirements
2. Gather data from multiple sources:
   - Activity logs in vault/Logs/
   - Completed tasks in vault/Done/
   - MCP server outputs
   - External research if needed
3. Analyze and synthesize information:
   - Identify key trends and insights
   - Calculate relevant KPIs
   - Highlight bottlenecks or issues
4. Generate comprehensive report:
   - Executive Summary
   - Key Findings
   - Data Analysis
   - Recommendations
   - Action Items
5. Save report to appropriate location:
   - Research reports: vault/Active_Projects/
   - CEO briefings: vault/Briefings/
6. Move processed item to vault/Done/
7. Log your actions to vault/Logs/

## Report Structure
- Title and date
- Executive Summary (1 paragraph)
- Key Metrics and KPIs
- Detailed Analysis
- Bottlenecks and Issues
- Recommendations
- Next Steps

## Success Criteria
- Comprehensive research completed
- Actionable insights provided
- Report saved in appropriate location
- Action logged and item moved to Done/

## File to Process
Read the file at: {file_path}
"""
        }
        
        return prompts.get(task_type, f"""
# General Agent Task

## Task
Process the file: {file_path}

## Instructions
1. Read and analyze the file content
2. Determine the appropriate action based on content type
3. Follow the appropriate workflow (email, social, accounting, etc.)
4. Use the correct MCP server for the task
5. Follow approval workflow if needed
6. Log all actions and move to Done/

## File to Process
Read the file at: {file_path}
""")

    def launch_agent(self, task: Dict) -> subprocess.Popen:
        """Launch a Claude agent for the specific task."""
        prompt = self.create_agent_prompt(task)
        
        # Create a task file for the agent
        task_file = self.plans / f"AGENT_TASK_{task['agent']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        task_file.write_text(f"""---
agent: {task['agent']}
type: {task['type']}
tier: {task['tier']}
created: {datetime.now().isoformat()}
status: in_progress
---

# Agent Task Assignment

{prompt}
""")
        
        logger.info(f"Created task file for {task['agent']}: {task_file}")
        
        # In a real implementation, this would spawn a Claude Code agent
        # For now, we'll simulate the agent work
        if not self.dry_run:
            # Launch Claude Code with the agent prompt
            cmd = [
                "claude",
                "--vault", str(self.vault_path),
                "--prompt", prompt
            ]
            return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            logger.info(f"[DRY RUN] Would launch agent: {task['agent']}")
            return None

    def process_all_tasks(self, tasks: List[Dict]):
        """Process all tasks using appropriate agents."""
        logger.info(f"Processing {len(tasks)} tasks with agent teams")
        
        # Group tasks by agent
        agent_tasks = {}
        for task in tasks:
            agent = task["agent"]
            if agent not in agent_tasks:
                agent_tasks[agent] = []
            agent_tasks[agent].append(task)
        
        # Process tasks for each agent
        for agent, agent_task_list in agent_tasks.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing tasks for agent: {agent}")
            logger.info(f"Number of tasks: {len(agent_task_list)}")
            logger.info(f"{'='*60}\n")
            
            for task in agent_task_list:
                logger.info(f"Processing task: {task['file']}")
                
                if self.dry_run:
                    # Simulate processing
                    logger.info(f"  [DRY RUN] Agent {agent} would process: {Path(task['file']).name}")
                else:
                    # Launch agent
                    process = self.launch_agent(task)
                    if process:
                        stdout, stderr = process.communicate()
                        logger.info(f"Agent completed: {task['agent']}")
                        if stderr:
                            logger.error(f"Agent errors: {stderr.decode()}")
                
                # Update task status
                self.update_task_status(task, "completed")
        
        logger.info("\n" + "="*60)
        logger.info("All tasks processed!")
        logger.info("="*60)

    def update_task_status(self, task: Dict, status: str):
        """Update the status of a task."""
        # In a real implementation, this would update the task file
        logger.info(f"Task {Path(task['file']).name} status: {status}")

    def generate_completion_report(self) -> str:
        """Generate a completion report for Silver and Gold tiers."""
        silver_tasks = self.get_silver_tier_tasks()
        gold_tasks = self.get_gold_tier_tasks()
        
        report = f"""# Tier Completion Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Vault:** {self.vault_path}
**Dry Run:** {self.dry_run}

## Summary

| Tier | Tasks Found | Status |
|------|-------------|--------|
| Silver | {len(silver_tasks)} | {'✅ Complete' if not self.dry_run else '🟡 Pending'} |
| Gold | {len(gold_tasks)} | {'✅ Complete' if not self.dry_run else '🟡 Pending'} |

## Silver Tier Tasks

"""
        
        if silver_tasks:
            for task in silver_tasks:
                report += f"- [{task['type']}] {Path(task['file']).name} → Agent: {task['agent']}\n"
        else:
            report += "*No Silver tier tasks found*\n"
        
        report += "\n## Gold Tier Tasks\n\n"
        
        if gold_tasks:
            for task in gold_tasks:
                report += f"- [{task['type']}] {Path(task['file']).name} → Agent: {task['agent']}\n"
        else:
            report += "*No Gold tier tasks found*\n"
        
        report += f"""
## Agent Teams Used

"""
        
        if self.config:
            for team_name, team_config in self.config.get("teams", {}).items():
                report += f"### {team_config.get('name', team_name)}\n"
                report += f"**Objective:** {team_config.get('objective', 'N/A')}\n\n"
                
                for member in team_config.get("members", []):
                    report += f"- **{member['role']}**: {member['description']}\n"
                report += "\n"
        
        # Save report
        report_file = self.logs / f"tier_completion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_file.write_text(report)
        
        logger.info(f"Completion report saved to: {report_file}")
        
        return report

    def run(self):
        """Run the tier completion process."""
        logger.info("\n" + "="*60)
        logger.info("🚀 Starting Silver and Gold Tier Completion")
        logger.info("="*60 + "\n")
        
        # Get tasks
        silver_tasks = self.get_silver_tier_tasks()
        gold_tasks = self.get_gold_tier_tasks()
        
        all_tasks = silver_tasks + gold_tasks
        
        logger.info(f"Found {len(silver_tasks)} Silver tier tasks")
        logger.info(f"Found {len(gold_tasks)} Gold tier tasks")
        logger.info(f"Total tasks: {len(all_tasks)}\n")
        
        if not all_tasks:
            logger.warning("No tasks found! Add items to vault/Needs_Action/ first.")
            return
        
        # Process tasks
        self.process_all_tasks(all_tasks)
        
        # Generate report
        report = self.generate_completion_report()
        
        print("\n" + "="*60)
        print("✅ Tier Completion Process Finished!")
        print("="*60)
        print(f"\nReport saved to: vault/Logs/tier_completion_report_*.md")
        print("\nTo process in LIVE mode (not dry run):")
        print("  python scripts/complete_silver_gold_tiers.py --vault ./vault --no-dry-run\n")


def main():
    parser = argparse.ArgumentParser(
        description='Complete Silver and Gold Tiers using Agent Teams'
    )
    parser.add_argument(
        '--vault',
        default='./vault',
        help='Path to vault directory'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no actual actions)'
    )
    parser.add_argument(
        '--no-dry-run',
        action='store_false',
        dest='dry_run',
        help='Run in live mode (actual actions)'
    )
    parser.add_argument(
        '--list-tasks',
        action='store_true',
        help='List all tasks without processing'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate completion report'
    )

    args = parser.parse_args()

    agent = TierCompletionAgent(vault_path=args.vault, dry_run=args.dry_run)

    if args.list_tasks:
        silver = agent.get_silver_tier_tasks()
        gold = agent.get_gold_tier_tasks()
        
        print("\n📋 Silver Tier Tasks:")
        for task in silver:
            print(f"  - [{task['type']}] {Path(task['file']).name}")
        
        print("\n📋 Gold Tier Tasks:")
        for task in gold:
            print(f"  - [{task['type']}] {Path(task['file']).name}")
        
        print(f"\nTotal: {len(silver) + len(gold)} tasks")
    else:
        agent.run()


if __name__ == "__main__":
    main()
