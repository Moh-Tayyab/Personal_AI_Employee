"""
Audit Subscriptions Skill Implementation

This skill analyzes subscriptions and recurring expenses.
"""

from pathlib import Path
from datetime import datetime, timedelta
import re
import json


class AuditSubscriptionsSkill:
    """Skill for auditing subscriptions and recurring expenses."""

    # Common subscription patterns
    SUBSCRIPTION_PATTERNS = {
        'netflix': {'name': 'Netflix', 'category': 'entertainment', 'typical_cost': 15.99},
        'spotify': {'name': 'Spotify', 'category': 'entertainment', 'typical_cost': 9.99},
        'adobe': {'name': 'Adobe Creative Cloud', 'category': 'software', 'typical_cost': 54.99},
        'notion': {'name': 'Notion', 'category': 'productivity', 'typical_cost': 8.00},
        'slack': {'name': 'Slack', 'category': 'communication', 'typical_cost': 7.25},
        'zoom': {'name': 'Zoom', 'category': 'communication', 'typical_cost': 14.99},
        'microsoft 365': {'name': 'Microsoft 365', 'category': 'software', 'typical_cost': 12.99},
        'google workspace': {'name': 'Google Workspace', 'category': 'productivity', 'typical_cost': 12.00},
        'dropbox': {'name': 'Dropbox', 'category': 'storage', 'typical_cost': 11.99},
        'icloud': {'name': 'iCloud', 'category': 'storage', 'typical_cost': 2.99},
        'amazon prime': {'name': 'Amazon Prime', 'category': 'shopping', 'typical_cost': 14.99},
        'github': {'name': 'GitHub Pro', 'category': 'development', 'typical_cost': 4.00},
        'cursor': {'name': 'Cursor', 'category': 'development', 'typical_cost': 20.00},
        'claude': {'name': 'Claude Pro', 'category': 'ai', 'typical_cost': 20.00},
        'chatgpt': {'name': 'ChatGPT Plus', 'category': 'ai', 'typical_cost': 20.00},
        'openai': {'name': 'OpenAI API', 'category': 'ai', 'typical_cost': 0},
        'anthropic': {'name': 'Anthropic API', 'category': 'ai', 'typical_cost': 0},
    }

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.accounting = self.vault_path / 'Accounting'
        self.logs = self.vault_path / 'Logs'
        self.briefings = self.vault_path / 'Briefings'
        self.pending_approval = self.vault_path / 'Pending_Approval'

        # Ensure directories exist
        self.accounting.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

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

    def _extract_transactions_from_logs(self, days: int = 30) -> list:
        """Extract transactions from log files."""
        transactions = []
        cutoff = datetime.now() - timedelta(days=days)

        if not self.logs.exists():
            return transactions

        for log_file in self.logs.glob('*.json'):
            try:
                log_date = datetime.strptime(log_file.stem, '%Y-%m-%d')
                if log_date < cutoff:
                    continue

                data = json.loads(log_file.read_text())
                if isinstance(data, list):
                    transactions.extend(data)
            except:
                pass

        return transactions

    def _identify_subscription(self, description: str) -> dict:
        """Identify if a transaction is a subscription."""
        desc_lower = description.lower()

        for pattern, info in self.SUBSCRIPTION_PATTERNS.items():
            if pattern in desc_lower:
                return {
                    'identified': True,
                    'name': info['name'],
                    'category': info['category'],
                    'typical_cost': info['typical_cost'],
                    'pattern': pattern
                }

        # Check for subscription keywords
        sub_keywords = ['subscription', 'monthly', 'recurring', 'auto-renew', 'membership']
        if any(kw in desc_lower for kw in sub_keywords):
            return {
                'identified': True,
                'name': description[:50],
                'category': 'other',
                'typical_cost': 0,
                'pattern': 'keyword'
            }

        return {'identified': False}

    def _extract_amount(self, text: str) -> float:
        """Extract monetary amount from text."""
        patterns = [
            r'\$([\d,]+\.?\d*)',
            r'(\d+\.\d{2})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(re.sub(r'[^\d.]', '', match.group(1)))
                except:
                    pass
        return 0.0

    def audit_subscriptions(self) -> dict:
        """Perform subscription audit."""
        timestamp = datetime.now()
        audit_file = self.accounting / f"SUBSCRIPTION_AUDIT_{timestamp.strftime('%Y%m%d')}.md"

        # Get recent transactions
        transactions = self._extract_transactions_from_logs(30)

        # Identify subscriptions
        subscriptions = {}
        for tx in transactions:
            desc = tx.get('target', tx.get('description', ''))
            amount = tx.get('amount', self._extract_amount(str(tx)))

            sub_info = self._identify_subscription(desc)
            if sub_info['identified']:
                name = sub_info['name']
                if name not in subscriptions:
                    subscriptions[name] = {
                        'name': name,
                        'category': sub_info['category'],
                        'typical_cost': sub_info['typical_cost'],
                        'actual_cost': amount,
                        'occurrences': 1,
                        'last_seen': tx.get('timestamp', timestamp.isoformat())
                    }
                else:
                    subscriptions[name]['occurrences'] += 1
                    subscriptions[name]['actual_cost'] += amount

        # Calculate totals
        total_monthly = sum(s['actual_cost'] for s in subscriptions.values())
        total_yearly = total_monthly * 12

        # Categorize
        by_category = {}
        for sub in subscriptions.values():
            cat = sub['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(sub)

        # Generate audit report
        content = f"""---
generated: {timestamp.isoformat()}
type: subscription_audit
period: 30 days
total_monthly: {total_monthly}
total_yearly: {total_yearly}
---

# Subscription Audit Report

*Generated: {timestamp.strftime('%Y-%m-%d %H:%M')}*

## Summary

| Metric | Value |
|--------|-------|
| **Total Subscriptions** | {len(subscriptions)} |
| **Monthly Cost** | ${total_monthly:,.2f} |
| **Yearly Cost** | ${total_yearly:,.2f} |

## Subscriptions by Category

"""
        for category, subs in sorted(by_category.items()):
            cat_total = sum(s['actual_cost'] for s in subs)
            content += f"""### {category.title()}
*Monthly: ${cat_total:,.2f}*

| Service | Cost/Mo | Occurrences | Typical |
|---------|---------|-------------|---------|
"""
            for sub in sorted(subs, key=lambda x: x['actual_cost'], reverse=True):
                content += f"| {sub['name']} | ${sub['actual_cost']:,.2f} | {sub['occurrences']} | ${sub['typical_cost']:,.2f} |\n"
            content += "\n"

        # Add recommendations
        content += """## Recommendations

"""
        recommendations = []

        # Check for duplicate services
        categories_with_duplicates = [c for c, s in by_category.items() if len(s) > 2]
        if categories_with_duplicates:
            recommendations.append(f"- **Consolidation Opportunity**: Multiple subscriptions in {', '.join(categories_with_duplicates)}")

        # Check for high-cost subscriptions
        high_cost = [s for s in subscriptions.values() if s['actual_cost'] > 50]
        if high_cost:
            recommendations.append(f"- **High-Cost Subscriptions**: {len(high_cost)} subscriptions over $50/month")

        # Check for unused subscriptions (only 1 occurrence in 30 days)
        unused = [s for s in subscriptions.values() if s['occurrences'] == 1]
        if unused:
            recommendations.append(f"- **Potentially Unused**: {', '.join(s['name'] for s in unused[:5])}")

        if recommendations:
            content += "\n".join(recommendations)
        else:
            content += "*No immediate recommendations.*\n"

        content += f"""
## Action Items

- [ ] Review each subscription for necessity
- [ ] Cancel unused subscriptions
- [ ] Consider annual plans for frequently used services
- [ ] Set up subscription tracking in accounting software

---
*Generated by AI Employee Subscription Audit*
"""

        audit_file.write_text(content)

        # Create approval requests for high-cost subscriptions that might need cancellation
        approval_requests = []
        for sub in unused:
            if sub['actual_cost'] > 10:
                approval = self._create_cancellation_approval(sub)
                approval_requests.append(approval)

        return {
            "status": "completed",
            "file": str(audit_file.name),
            "summary": {
                "total_subscriptions": len(subscriptions),
                "monthly_cost": total_monthly,
                "yearly_cost": total_yearly,
                "categories": list(by_category.keys())
            },
            "subscriptions": list(subscriptions.values()),
            "recommendations": recommendations,
            "approval_requests": approval_requests
        }

    def _create_cancellation_approval(self, subscription: dict) -> dict:
        """Create approval request for subscription cancellation."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_file = self.pending_approval / f"SUB_CANCEL_{timestamp}_{subscription['name'][:20]}.md"

        content = f"""---
type: approval_request
action: subscription_cancellation
created: {datetime.now().isoformat()}
status: pending
subscription: {subscription['name']}
monthly_cost: {subscription['actual_cost']}
---

# Subscription Cancellation Review

## Service
{subscription['name']}

## Category
{subscription['category']}

## Cost
- Monthly: ${subscription['actual_cost']:,.2f}
- Yearly: ${subscription['actual_cost'] * 12:,.2f}

## Reason for Review
This subscription had only 1 occurrence in the last 30 days and may be unused.

## Recommendation
Consider cancelling if not actively using this service.

## To Approve Cancellation
Move this file to /Approved folder.

## To Keep Subscription
Move this file to /Rejected folder.

---
*Auto-generated by Subscription Audit*
"""
        approval_file.write_text(content)
        return {"file": str(approval_file.name), "subscription": subscription['name']}

    def run(self):
        """Execute the skill."""
        return self.audit_subscriptions()


def execute(vault_path: str):
    """Main entry point for the skill."""
    skill = AuditSubscriptionsSkill(vault_path)
    return skill.run()