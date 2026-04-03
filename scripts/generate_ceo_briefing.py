#!/usr/bin/env python3
"""
CEO Briefing Generator - Gold Tier

Generates comprehensive weekly CEO briefings with:
- Revenue tracking from Odoo
- Completed tasks analysis
- Bottleneck detection
- Social media performance
- Cost optimization suggestions
- Upcoming deadlines

Usage:
    python scripts/generate_ceo_briefing.py --vault ./vault
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CEO_Briefing")


class CEOBriefingGenerator:
    """Generate comprehensive CEO briefings."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.briefings_dir = self.vault_path / 'Briefings'
        self.done_dir = self.vault_path / 'Done'
        
        # Ensure directories exist
        self.briefings_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Load business goals
        self.business_goals = self._load_business_goals()
        
        # Odoo credentials
        self.odoo_enabled = bool(os.getenv('ODOO_API_KEY'))
        
    def _load_business_goals(self) -> Dict:
        """Load business goals from vault."""
        goals_file = self.vault_path / 'Business_Goals.md'
        
        if not goals_file.exists():
            return self._default_goals()
        
        content = goals_file.read_text()
        
        # Simple YAML-like parsing
        goals = self._default_goals()
        
        try:
            for line in content.split('\n'):
                if 'Monthly goal:' in line:
                    try:
                        goals['monthly_revenue_target'] = float(line.split('$')[1].replace(',', ''))
                    except:
                        pass
                elif 'Current MTD:' in line:
                    try:
                        goals['current_mtd_revenue'] = float(line.split('$')[1].replace(',', ''))
                    except:
                        pass
        except Exception as e:
            logger.warning(f"Error parsing business goals: {e}")
        
        return goals
    
    def _default_goals(self) -> Dict:
        """Return default business goals."""
        return {
            'monthly_revenue_target': 10000.0,
            'current_mtd_revenue': 0.0,
            'response_time_target_hours': 24,
            'payment_rate_target': 90.0
        }
    
    def _get_week_date_range(self) -> tuple:
        """Get the date range for the current week."""
        today = datetime.now()
        # Start of week (Monday)
        start_of_week = today - timedelta(days=today.weekday())
        # End of week (Sunday)
        end_of_week = start_of_week + timedelta(days=6)
        
        return start_of_week, end_of_week
    
    def _analyze_completed_tasks(self) -> Dict[str, Any]:
        """Analyze completed tasks from Done folder."""
        tasks = []
        
        # Read Done folder
        if self.done_dir.exists():
            for f in self.done_dir.glob('*.md'):
                try:
                    content = f.read_text()
                    
                    # Extract task info
                    task = {
                        'file': f.name,
                        'completed_date': self._extract_date(content),
                        'type': self._extract_type(content),
                        'content': content[:500]  # First 500 chars
                    }
                    tasks.append(task)
                except Exception as e:
                    logger.warning(f"Error reading {f}: {e}")
        
        # Group by type
        by_type = {}
        for task in tasks:
            task_type = task.get('type', 'unknown')
            if task_type not in by_type:
                by_type[task_type] = []
            by_type[task_type].append(task)
        
        return {
            'total_completed': len(tasks),
            'by_type': by_type,
            'tasks': tasks[:10]  # Last 10 tasks
        }
    
    def _extract_date(self, content: str) -> str:
        """Extract date from markdown content."""
        # Look for date patterns
        import re
        patterns = [
            r'completed: (\d{4}-\d{2}-\d{2})',
            r'created: (\d{4}-\d{2}-\d{2})',
            r'date: (\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return datetime.now().strftime('%Y-%m-%d')
    
    def _extract_type(self, content: str) -> str:
        """Extract type from markdown frontmatter."""
        import re
        match = re.search(r'type:\s*(\w+)', content)
        if match:
            return match.group(1)
        return 'general'
    
    def _get_financial_data(self) -> Dict[str, Any]:
        """Get financial data from Odoo or logs."""
        financial = {
            'revenue': 0,
            'expenses': 0,
            'profit': 0,
            'invoices_sent': 0,
            'payments_received': 0,
            'source': 'logs'  # or 'odoo'
        }
        
        if self.odoo_enabled:
            try:
                # Try to get data from Odoo
                from mcp.odoo.server import get_financial_summary
                
                result = get_financial_summary(period_days=7)
                if result.get('success'):
                    financial.update({
                        'revenue': result.get('revenue', {}).get('total', 0),
                        'expenses': result.get('expenses', {}).get('total', 0),
                        'profit': result.get('profit', 0),
                        'invoices_sent': result.get('revenue', {}).get('invoice_count', 0),
                        'source': 'odoo'
                    })
            except Exception as e:
                logger.warning(f"Could not get Odoo data: {e}")
        
        # Fallback: Parse logs for financial data
        if financial['source'] == 'logs':
            financial.update(self._parse_financial_logs())
        
        return financial
    
    def _parse_financial_logs(self) -> Dict[str, Any]:
        """Parse financial data from logs."""
        revenue = 0
        invoices = 0
        
        # Look for invoice logs
        for log_file in self.logs_dir.glob('odoo_invoices_*.json'):
            try:
                data = json.loads(log_file.read_text())
                if isinstance(data, list):
                    for entry in data:
                        if entry.get('type') == 'invoice_created':
                            invoices += 1
                            invoice_data = entry.get('data', {})
                            revenue += invoice_data.get('total', 0)
            except Exception as e:
                logger.warning(f"Error parsing {log_file}: {e}")
        
        return {
            'revenue': revenue,
            'invoices_sent': invoices
        }
    
    def _analyze_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify bottlenecks from task completion times."""
        bottlenecks = []
        
        # Analyze Plans folder for delayed tasks
        plans_dir = self.vault_path / 'Plans'
        if plans_dir.exists():
            for f in plans_dir.glob('*.md'):
                try:
                    content = f.read_text()
                    
                    # Check if task took longer than expected
                    if 'delay' in content.lower() or 'blocked' in content.lower():
                        bottlenecks.append({
                            'task': f.name,
                            'issue': 'Delay detected',
                            'severity': 'medium'
                        })
                except Exception as e:
                    pass
        
        # Check Pending_Approval for old items
        pending_dir = self.vault_path / 'Pending_Approval'
        if pending_dir.exists():
            old_approvals = []
            for f in pending_dir.glob('*.md'):
                age = datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)
                if age.days > 2:
                    old_approvals.append({
                        'task': f.name,
                        'age_days': age.days,
                        'issue': 'Pending approval for >2 days',
                        'severity': 'high' if age.days > 5 else 'medium'
                    })
            bottlenecks.extend(old_approvals)
        
        return bottlenecks
    
    def _get_social_media_summary(self) -> Dict[str, Any]:
        """Get social media activity summary from logs."""
        social = {
            'linkedin_posts': 0,
            'twitter_posts': 0,
            'facebook_posts': 0,
            'instagram_posts': 0
        }
        
        # Parse social media logs
        for log_file in self.logs_dir.glob('linkedin_*.json'):
            try:
                data = json.loads(log_file.read_text())
                if isinstance(data, list):
                    social['linkedin_posts'] += len([d for d in data if d.get('status') in ['posted', 'simulated']])
            except:
                pass
        
        for log_file in self.logs_dir.glob('twitter_*.json'):
            try:
                data = json.loads(log_file.read_text())
                if isinstance(data, list):
                    social['twitter_posts'] += len([d for d in data if d.get('status') == 'posted'])
            except:
                pass
        
        for log_file in self.logs_dir.glob('social_*.json'):
            try:
                data = json.loads(log_file.read_text())
                if isinstance(data, list):
                    for entry in data:
                        platform = entry.get('platform', '')
                        if platform == 'facebook':
                            social['facebook_posts'] += 1
                        elif platform == 'instagram':
                            social['instagram_posts'] += 1
            except:
                pass
        
        return social
    
    def _generate_cost_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Generate cost optimization suggestions."""
        suggestions = []
        
        # Check for subscription patterns in logs
        subscription_keywords = {
            'netflix': 'Netflix',
            'spotify': 'Spotify',
            'adobe': 'Adobe Creative Cloud',
            'notion': 'Notion',
            'slack': 'Slack',
            'github': 'GitHub',
            'vercel': 'Vercel',
            'aws': 'AWS'
        }
        
        # Analyze transaction logs
        for log_file in self.logs_dir.glob('*.json'):
            try:
                content = log_file.read_text().lower()
                
                for keyword, name in subscription_keywords.items():
                    if keyword in content:
                        suggestions.append({
                            'type': 'subscription_review',
                            'item': name,
                            'action': 'Review usage and consider cancellation if unused',
                            'priority': 'medium'
                        })
                        break
            except:
                pass
        
        # Remove duplicates
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            key = s['item']
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(s)
        
        return unique_suggestions[:5]  # Top 5 suggestions
    
    def _get_upcoming_deadlines(self) -> List[Dict[str, Any]]:
        """Get upcoming deadlines from Business_Goals.md and Plans."""
        deadlines = []
        
        # Parse Business_Goals.md for projects
        goals_file = self.vault_path / 'Business_Goals.md'
        if goals_file.exists():
            content = goals_file.read_text()
            
            # Look for project deadlines
            import re
            projects = re.findall(r'(\w+\s*\w*)\s*-\s*Due\s+(\w+\s+\d+)', content, re.IGNORECASE)
            
            for project, due_date in projects:
                deadlines.append({
                    'project': project.strip(),
                    'due_date': due_date.strip(),
                    'type': 'project'
                })
        
        # Check Plans folder for upcoming items
        plans_dir = self.vault_path / 'Plans'
        if plans_dir.exists():
            for f in list(plans_dir.glob('*.md'))[:5]:
                deadlines.append({
                    'task': f.name,
                    'type': 'pending_task'
                })
        
        return deadlines
    
    def generate_briefing(self, period_days: int = 7) -> str:
        """
        Generate a comprehensive CEO briefing.
        
        Args:
            period_days: Number of days to cover (default: 7 for weekly)
        
        Returns:
            Markdown content of the briefing
        """
        # Gather all data
        start_date, end_date = self._get_week_date_range()
        tasks_analysis = self._analyze_completed_tasks()
        financial = self._get_financial_data()
        bottlenecks = self._analyze_bottlenecks()
        social = self._get_social_media_summary()
        cost_suggestions = self._generate_cost_optimization_suggestions()
        deadlines = self._get_upcoming_deadlines()
        
        # Calculate metrics
        revenue_target = self.business_goals['monthly_revenue_target']
        weekly_target = revenue_target / 4  # Approximate weekly target
        revenue_percentage = (financial['revenue'] / weekly_target * 100) if weekly_target > 0 else 0
        
        # Determine trend
        if revenue_percentage >= 100:
            trend = "📈 Above target"
        elif revenue_percentage >= 75:
            trend = "➡️ On track"
        else:
            trend = "📉 Below target"
        
        # Generate briefing content
        briefing = f"""---
generated: {datetime.now().isoformat()}
period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
period_days: {period_days}
---

# Monday Morning CEO Briefing

## Executive Summary

{self._generate_executive_summary(financial, tasks_analysis, bottlenecks)}

---

## 📊 Revenue & Metrics

### This Week's Revenue
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Revenue | ${financial['revenue']:,.2f} | ${weekly_target:,.2f} | {revenue_percentage:.0f}% |
| Invoices Sent | {financial['invoices_sent']} | - | - |
| Payments Received | {financial['payments_received']} | - | - |

**Trend:** {trend}

### Key Performance Indicators
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Tasks Completed | 10/week | {tasks_analysis['total_completed']} | {'✅' if tasks_analysis['total_completed'] >= 10 else '⚠️'} |
| Response Time | <24 hours | - | - |
| Social Posts | 3/week | {sum(social.values())} | {'✅' if sum(social.values()) >= 3 else '⚠️'} |

---

## ✅ Completed Tasks

**Total:** {tasks_analysis['total_completed']} tasks completed

### By Category
"""
        
        # Add tasks by type
        for task_type, tasks in tasks_analysis['by_type'].items():
            briefing += f"\n**{task_type.title()}:** {len(tasks)}\n"
        
        briefing += f"""
### Recent Tasks
"""
        for task in tasks_analysis['tasks'][:5]:
            briefing += f"- [x] {task['file']} ({task['completed_date']})\n"
        
        briefing += f"""
---

## ⚠️ Bottlenecks

"""
        if bottlenecks:
            briefing += "| Issue | Severity | Action |\n|-------|----------|--------|\n"
            for b in bottlenecks[:5]:
                severity_icon = "🔴" if b.get('severity') == 'high' else "🟡"
                briefing += f"| {b.get('task', b.get('issue'))} | {severity_icon} {b.get('severity')} | Review needed |\n"
        else:
            briefing += "*No significant bottlenecks detected.*\n"
        
        briefing += f"""
---

## 📱 Social Media Activity

| Platform | Posts This Week |
|----------|-----------------|
| LinkedIn | {social['linkedin_posts']} |
| Twitter/X | {social['twitter_posts']} |
| Facebook | {social['facebook_posts']} |
| Instagram | {social['instagram_posts']} |
| **Total** | **{sum(social.values())}** |

---

## 💰 Cost Optimization Suggestions

"""
        if cost_suggestions:
            for i, suggestion in enumerate(cost_suggestions, 1):
                briefing += f"{i}. **{suggestion['item']}**: {suggestion['action']}\n"
        else:
            briefing += "*No cost optimization suggestions at this time.*\n"
        
        briefing += f"""
---

## 📅 Upcoming Deadlines

"""
        if deadlines:
            for d in deadlines[:5]:
                if 'due_date' in d:
                    briefing += f"- **{d['project']}**: Due {d['due_date']}\n"
                else:
                    briefing += f"- {d.get('task', 'Pending task')}\n"
        else:
            briefing += "*No upcoming deadlines identified.*\n"
        
        briefing += f"""
---

## 🎯 Action Items for This Week

Based on the analysis above, here are the recommended priorities:

1. **Revenue Focus**: {self._get_revenue_action(revenue_percentage)}
2. **Bottleneck Resolution**: {self._get_bottleneck_action(bottlenecks)}
3. **Social Media**: {self._get_social_action(social)}

---

## 📈 Week-over-Week Comparison

*Note: Historical comparison will be available after multiple briefings.*

---

*Generated by Personal AI Employee v1.0 (Gold Tier)*
*Next briefing: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}*
"""
        
        return briefing
    
    def _generate_executive_summary(self, financial: Dict, tasks: Dict, bottlenecks: List) -> str:
        """Generate executive summary paragraph."""
        parts = []
        
        # Revenue status
        if financial['revenue'] > 0:
            parts.append(f"Revenue of ${financial['revenue']:,.2f} this week")
        else:
            parts.append("No revenue recorded this week")
        
        # Task status
        if tasks['total_completed'] > 0:
            parts.append(f"{tasks['total_completed']} tasks completed")
        
        # Bottleneck status
        if bottlenecks:
            high_priority = [b for b in bottlenecks if b.get('severity') == 'high']
            if high_priority:
                parts.append(f"{len(high_priority)} high-priority bottleneck(s) need attention")
        
        return ". ".join(parts) + "."
    
    def _get_revenue_action(self, percentage: float) -> str:
        """Get revenue-focused action item."""
        if percentage >= 100:
            return "Maintain momentum, consider upselling existing clients"
        elif percentage >= 75:
            return "On track - focus on closing pending deals"
        else:
            return "Urgent: Increase lead generation and follow-ups"
    
    def _get_bottleneck_action(self, bottlenecks: List) -> str:
        """Get bottleneck resolution action."""
        if not bottlenecks:
            return "No bottlenecks - maintain current workflow"
        
        high_priority = [b for b in bottlenecks if b.get('severity') == 'high']
        if high_priority:
            return f"Address {len(high_priority)} high-priority issue(s) immediately"
        return "Monitor and resolve medium-priority items"
    
    def _get_social_action(self, social: Dict) -> str:
        """Get social media action item."""
        total = sum(social.values())
        if total >= 5:
            return "Excellent activity - maintain posting schedule"
        elif total >= 3:
            return "Good activity - consider increasing engagement"
        else:
            return "Increase posting frequency to 3-5 times per week"
    
    def save_briefing(self, content: str) -> Path:
        """Save briefing to file."""
        filename = f"{datetime.now().strftime('%Y-%m-%d')}_CEO_Briefing.md"
        filepath = self.briefings_dir / filename
        filepath.write_text(content)
        logger.info(f"Briefing saved to {filepath}")
        return filepath


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate CEO Briefing')
    parser.add_argument('--vault', default='./vault', help='Path to vault')
    parser.add_argument('--period', type=int, default=7, help='Period in days')
    parser.add_argument('--output', help='Output file (optional)')
    
    args = parser.parse_args()
    
    # Generate briefing
    generator = CEOBriefingGenerator(args.vault)
    briefing = generator.generate_briefing(args.period)
    
    # Save briefing
    filepath = generator.save_briefing(briefing)
    
    print(f"\n{'='*50}")
    print("CEO Briefing Generated Successfully!")
    print(f"{'='*50}")
    print(f"\nSaved to: {filepath}")
    print(f"\nTo view:")
    print(f"  cat {filepath}")
    print()


if __name__ == "__main__":
    main()
