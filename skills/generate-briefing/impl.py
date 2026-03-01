"""
Generate Briefing Skill Implementation

This skill generates CEO briefing reports from vault data.
"""

from pathlib import Path
from datetime import datetime, timedelta
import re


class GenerateBriefingSkill:
    """Skill for generating CEO briefing reports."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.done = self.vault_path / 'Done'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.briefings = self.vault_path / 'Briefings'
        self.business_goals = self.vault_path / 'Business_Goals.md'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.logs = self.vault_path / 'Logs'

        # Ensure briefings folder exists
        self.briefings.mkdir(parents=True, exist_ok=True)

    def _parse_frontmatter(self, content: str):
        """Parse YAML frontmatter from content."""
        lines = content.split('\n')
        in_frontmatter = False
        frontmatter = {}
        body_lines = []
        body_start = False

        for line in lines:
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    body_start = True
                continue

            if body_start:
                body_lines.append(line)
            elif in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter, '\n'.join(body_lines)

    def _get_completed_tasks(self, days: int = 7) -> list:
        """Get tasks completed in the last N days."""
        tasks = []
        cutoff = datetime.now() - timedelta(days=days)

        if not self.done.exists():
            return tasks

        for f in self.done.glob('*.md'):
            try:
                stat = f.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime)
                if mtime > cutoff:
                    content = f.read_text()
                    frontmatter, body = self._parse_frontmatter(content)
                    tasks.append({
                        'file': f.name,
                        'type': frontmatter.get('type', 'general'),
                        'date': mtime.strftime('%Y-%m-%d'),
                        'frontmatter': frontmatter
                    })
            except:
                pass

        return tasks

    def _get_pending_items(self) -> list:
        """Get items pending action."""
        items = []

        # Needs_Action items
        if self.needs_action.exists():
            for f in self.needs_action.glob('*.md'):
                content = f.read_text()
                frontmatter, body = self._parse_frontmatter(content)
                items.append({
                    'file': f.name,
                    'location': 'Needs_Action',
                    'type': frontmatter.get('type', 'general'),
                    'priority': frontmatter.get('priority', 'normal'),
                    'frontmatter': frontmatter
                })

        # Pending Approval items
        if self.pending_approval.exists():
            for f in self.pending_approval.glob('*.md'):
                content = f.read_text()
                frontmatter, body = self._parse_frontmatter(content)
                items.append({
                    'file': f.name,
                    'location': 'Pending_Approval',
                    'type': frontmatter.get('action', frontmatter.get('type', 'general')),
                    'priority': 'high',
                    'frontmatter': frontmatter
                })

        return items

    def _get_business_goals(self) -> dict:
        """Parse business goals from Business_Goals.md."""
        if not self.business_goals.exists():
            return {}

        content = self.business_goals.read_text()
        frontmatter, body = self._parse_frontmatter(content)

        goals = {
            'revenue_target': None,
            'current_mtd': None,
            'projects': [],
            'metrics': []
        }

        # Extract revenue info
        revenue_match = re.search(r'Monthly goal:\s*\$?([\d,]+)', body, re.IGNORECASE)
        if revenue_match:
            goals['revenue_target'] = float(re.sub(r'[^\d]', '', revenue_match.group(1)))

        mtd_match = re.search(r'Current MTD:\s*\$?([\d,]+)', body, re.IGNORECASE)
        if mtd_match:
            goals['current_mtd'] = float(re.sub(r'[^\d]', '', mtd_match.group(1)))

        return goals

    def _calculate_bottlenecks(self, tasks: list) -> list:
        """Identify bottlenecks from task data."""
        bottlenecks = []

        # Group tasks by type
        type_counts = {}
        for task in tasks:
            t = task.get('type', 'general')
            type_counts[t] = type_counts.get(t, 0) + 1

        # Identify types with high counts (potential bottlenecks)
        for t, count in type_counts.items():
            if count > 3:
                bottlenecks.append({
                    'type': t,
                    'count': count,
                    'suggestion': f"Consider automating {t} tasks"
                })

        return bottlenecks

    def _get_recent_revenue(self, tasks: list) -> float:
        """Calculate recent revenue from completed tasks."""
        total = 0.0

        for task in tasks:
            frontmatter = task.get('frontmatter', {})
            # Look for amount in frontmatter
            if 'amount' in frontmatter:
                try:
                    total += float(re.sub(r'[^\d.]', '', str(frontmatter['amount'])))
                except:
                    pass

        return total

    def generate_briefing(self, period: str = 'weekly') -> dict:
        """Generate a CEO briefing report."""
        timestamp = datetime.now()
        briefing_file = self.briefings / f"BRIEFING_{timestamp.strftime('%Y%m%d')}.md"

        # Gather data
        days = 7 if period == 'weekly' else 1
        completed_tasks = self._get_completed_tasks(days)
        pending_items = self._get_pending_items()
        business_goals = self._get_business_goals()
        bottlenecks = self._calculate_bottlenecks(completed_tasks)
        revenue = self._get_recent_revenue(completed_tasks)

        # Calculate metrics
        revenue_target = business_goals.get('revenue_target', 10000)
        current_mtd = business_goals.get('current_mtd', revenue)

        if revenue_target:
            progress_pct = min(100, (current_mtd / revenue_target) * 100)
        else:
            progress_pct = 0

        # Generate briefing content
        content = f"""---
generated: {timestamp.isoformat()}
period: {period}
type: ceo_briefing
---

# Monday Morning CEO Briefing

*Generated: {timestamp.strftime('%Y-%m-%d %H:%M')}*

## Executive Summary

"""
        # Add summary based on metrics
        if progress_pct >= 50:
            content += "✅ Strong progress this period. "
        elif progress_pct >= 25:
            content += "📊 Moderate progress this period. "
        else:
            content += "⚠️ Behind target this period. "

        if bottlenecks:
            content += f"{len(bottlenecks)} bottleneck(s) identified.\n"
        else:
            content += "No significant bottlenecks detected.\n"

        content += f"""
## Revenue

| Metric | Value |
|--------|-------|
| **This Period** | ${revenue:,.2f} |
| **MTD** | ${current_mtd:,.2f} |
| **Target** | ${revenue_target:,.2f} |
| **Progress** | {progress_pct:.1f}% |

"""
        # Add progress bar
        bar_length = 20
        filled = int(bar_length * progress_pct / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        content += f"Progress: [{bar}] {progress_pct:.1f}%\n\n"

        # Completed tasks section
        content += f"""## Completed Tasks ({len(completed_tasks)})

"""
        if completed_tasks:
            for task in completed_tasks[:10]:  # Show top 10
                content += f"- [x] {task['file'].replace('.md', '')} ({task['type']})\n"
        else:
            content += "*No tasks completed this period.*\n"

        # Bottlenecks section
        if bottlenecks:
            content += f"""
## Bottlenecks

| Task Type | Count | Suggestion |
|-----------|-------|------------|
"""
            for b in bottlenecks:
                content += f"| {b['type']} | {b['count']} | {b['suggestion']} |\n"

        # Pending items section
        high_priority = [i for i in pending_items if i.get('priority') == 'high']
        content += f"""
## Pending Items ({len(pending_items)})

"""
        content += f"- **High Priority**: {len(high_priority)}\n"
        content += f"- **Awaiting Approval**: {len([i for i in pending_items if i['location'] == 'Pending_Approval'])}\n"

        if high_priority:
            content += "\n### Urgent Items\n"
            for item in high_priority[:5]:
                content += f"- 🔴 {item['file'].replace('.md', '')}\n"

        # Proactive suggestions
        content += """
## Proactive Suggestions

"""
        suggestions = []

        if progress_pct < 25:
            suggestions.append("**Revenue Gap**: Consider outreach to pending leads to accelerate revenue.")

        if bottlenecks:
            suggestions.append("**Process Optimization**: Review bottlenecks for automation opportunities.")

        if len(pending_items) > 10:
            suggestions.append("**Workload**: High number of pending items. Consider prioritization review.")

        if suggestions:
            for s in suggestions:
                content += f"- {s}\n"
        else:
            content += "*No proactive suggestions at this time.*\n"

        # Upcoming deadlines
        content += """
## Upcoming Deadlines

*Check Plans/ folder for scheduled items.*

---
*Generated by AI Employee*
"""

        briefing_file.write_text(content)

        return {
            "status": "generated",
            "file": str(briefing_file.name),
            "period": period,
            "metrics": {
                "completed_tasks": len(completed_tasks),
                "pending_items": len(pending_items),
                "high_priority": len(high_priority),
                "bottlenecks": len(bottlenecks),
                "revenue": revenue,
                "progress_pct": progress_pct
            }
        }

    def run(self, period: str = 'weekly'):
        """Execute the skill."""
        return self.generate_briefing(period)


def execute(vault_path: str, period: str = 'weekly'):
    """Main entry point for the skill."""
    skill = GenerateBriefingSkill(vault_path)
    return skill.run(period)