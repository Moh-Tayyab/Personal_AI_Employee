"""
CEO Briefing Generator - Weekly business audit and reporting

This script generates the Monday Morning CEO Briefing by analyzing:
- Business goals and targets
- Completed tasks from the Done folder
- Accounting transactions
- Pending items and bottlenecks

Usage:
    python -m scripts.generate_briefing --vault ./vault
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


class CEOBriefingGenerator:
    """Generate weekly CEO briefing reports."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.goals_file = self.vault_path / 'Business_Goals.md'
        self.done_folder = self.vault_path / 'Done'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.logs_folder = self.vault_path / 'Logs'
        self.briefings_folder = self.vault_path / 'Briefings'
        self.accounting_folder = self.vault_path / 'Accounting'

        # Ensure folders exist
        self.briefings_folder.mkdir(parents=True, exist_ok=True)

    def get_date_range(self):
        """Get the date range for this week."""
        today = datetime.now()
        # Get start of week (Monday)
        start = today - timedelta(days=today.weekday())
        # Go back 7 days to cover previous week
        week_start = start - timedelta(days=7)
        week_end = start
        return week_start, week_end

    def analyze_business_goals(self):
        """Read and analyze business goals."""
        if not self.goals_file.exists():
            return {}

        content = self.goals_file.read_text()
        goals = {
            'revenue_target': 0,
            'revenue_actual': 0,
            'kpis': []
        }

        # Simple parsing - in production use proper YAML/markdown parser
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'monthly goal' in line.lower() or 'target' in line.lower():
                # Try to extract amount
                import re
                amounts = re.findall(r'\$?([\d,]+)', line)
                if amounts:
                    goals['revenue_target'] = int(amounts[0].replace(',', ''))

            if 'current mtd' in line.lower() or 'actual' in line.lower():
                amounts = re.findall(r'\$?([\d,]+)', line)
                if amounts:
                    goals['revenue_actual'] = int(amounts[0].replace(',', ''))

        return goals

    def analyze_completed_tasks(self):
        """Analyze completed tasks from Done folder."""
        tasks = []

        if not self.done_folder.exists():
            return tasks

        for f in self.done_folder.glob('*.md'):
            content = f.read_text()

            # Extract type
            item_type = 'unknown'
            for line in content.split('\n'):
                if line.startswith('type:'):
                    item_type = line.split(':')[1].strip()
                    break

            tasks.append({
                'file': f.name,
                'type': item_type,
                'completed': f.stat().st_mtime
            })

        return tasks

    def analyze_pending_items(self):
        """Analyze items waiting in queues."""
        pending = {
            'needs_action': [],
            'pending_approval': []
        }

        # Needs Action
        if self.needs_action.exists():
            for f in self.needs_action.glob('*.md'):
                pending['needs_action'].append(f.name)

        # Pending Approval
        if self.pending_approval.exists():
            for f in self.pending_approval.glob('*.md'):
                pending['pending_approval'].append(f.name)

        return pending

    def analyze_activity_logs(self):
        """Analyze activity from log files."""
        week_start, week_end = self.get_date_range()
        activities = defaultdict(int)

        if not self.logs_folder.exists():
            return activities

        for log_file in self.logs_folder.glob('*.json'):
            # Check if file is from this week
            try:
                date_str = log_file.stem
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                if not (week_start <= file_date <= week_end):
                    continue
            except ValueError:
                continue

            try:
                with open(log_file) as f:
                    logs = json.load(f)
                    for entry in logs:
                        activity_type = entry.get('type', 'unknown')
                        activities[activity_type] += 1
            except:
                continue

        return dict(activities)

    def identify_bottlenecks(self):
        """Identify potential bottlenecks."""
        bottlenecks = []

        # Check for old items in Needs_Action
        if self.needs_action.exists():
            now = datetime.now().timestamp()
            for f in self.needs_action.glob('*.md'):
                age_days = (now - f.stat().st_mtime) / 86400
                if age_days > 3:
                    bottlenecks.append(f"Item '{f.name}' waiting {int(age_days)} days")

        # Check for old pending approvals
        if self.pending_approval.exists():
            for f in self.pending_approval.glob('*.md'):
                age_days = (now - f.stat().st_mtime) / 86400
                if age_days > 1:
                    bottlenecks.append(f"Approval '{f.name}' waiting {int(age_days)} days")

        return bottlenecks

    def generate_briefing(self):
        """Generate the full briefing report."""
        goals = self.analyze_business_goals()
        completed_tasks = self.analyze_completed_tasks()
        pending = self.analyze_pending_items()
        activities = self.analyze_activity_logs()
        bottlenecks = self.identify_bottlenecks()

        week_start, week_end = self.get_date_range()

        # Calculate revenue
        revenue_actual = goals.get('revenue_actual', 0)
        revenue_target = goals.get('revenue_target', 1)
        revenue_pct = (revenue_actual / revenue_target * 100) if revenue_target > 0 else 0

        # Count task types
        task_counts = defaultdict(int)
        for task in completed_tasks:
            task_counts[task['type']] += 1

        # Generate report
        report = f"""---
generated: {datetime.now().isoformat()}
period: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}
type: ceo_briefing
---

# Monday Morning CEO Briefing

**Period:** {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---

## Executive Summary

"""

        # Add summary based on data
        if revenue_pct >= 80:
            report += "Strong week with revenue ahead of target. "
        elif revenue_pct >= 50:
            report += "Revenue on track but needs attention. "
        else:
            report += "Revenue behind target - review needed. "

        if bottlenecks:
            report += f"{len(bottlenecks)} bottleneck(s) identified.\n"
        else:
            report += "No critical bottlenecks identified.\n"

        report += f"""
## Revenue Summary

| Period | Amount | Target | % of Target |
|--------|--------|--------|-------------|
| This Week | ${revenue_actual:,} | ${revenue_target:,} | {revenue_pct:.1f}% |

"""

        report += f"""
## Completed Tasks ({len(completed_tasks)} total)

"""
        if task_counts:
            report += "### By Type\n\n"
            for task_type, count in sorted(task_counts.items()):
                report += f"- **{task_type}**: {count}\n"
            report += "\n"

        # List recent completions
        recent = sorted(completed_tasks, key=lambda x: x['completed'], reverse=True)[:5]
        if recent:
            report += "### Recent Completions\n\n"
            for task in recent:
                report += f"- {task['file']}\n"
            report += "\n"

        report += f"""
## Pending Items

### Needs Action ({len(pending['needs_action'])} items)
"""
        if pending['needs_action']:
            for item in pending['needs_action'][:5]:
                report += f"- {item}\n"
            if len(pending['needs_action']) > 5:
                report += f"- ... and {len(pending['needs_action']) - 5} more\n"
        else:
            report += "- No items\n"

        report += f"""
### Pending Approval ({len(pending['pending_approval'])} items)
"""
        if pending['pending_approval']:
            for item in pending['pending_approval']:
                report += f"- {item}\n"
        else:
            report += "- No items\n"

        report += f"""
## Bottlenecks

"""
        if bottlenecks:
            for bottleneck in bottlenecks:
                report += f"- {bottleneck}\n"
        else:
            report += "- No bottlenecks identified\n"

        report += f"""
## Activity This Week

"""
        if activities:
            for activity, count in sorted(activities.items(), key=lambda x: x[1], reverse=True):
                report += f"- **{activity}**: {count}\n"
        else:
            report += "- No activity logged\n"

        report += f"""
## Suggestions

"""
        # Generate proactive suggestions
        if revenue_pct < 50:
            report += "- Revenue is significantly behind target - consider reviewing sales pipeline\n"

        if len(pending['pending_approval']) > 5:
            report += "- Multiple items pending approval - review to keep workflow moving\n"

        if len(bottlenecks) > 3:
            report += "- Multiple bottlenecks identified - prioritize clearing these\n"

        if not bottlenecks and revenue_pct >= 80:
            report += "- Consider taking on additional projects or scaling operations\n"

        report += """
---

*Generated by AI Employee v0.3 (Gold)*
"""

        # Save briefing
        date_str = datetime.now().strftime('%Y-%m-%d')
        briefing_file = self.briefings_folder / f'{date_str}_Monday_Briefing.md'
        briefing_file.write_text(report)

        print(f"Briefing generated: {briefing_file}")
        return briefing_file


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate CEO Briefing')
    parser.add_argument('--vault', required=True, help='Path to vault')

    args = parser.parse_args()

    generator = CEOBriefingGenerator(args.vault)
    generator.generate_briefing()


if __name__ == "__main__":
    main()
