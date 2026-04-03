#!/usr/bin/env python3
"""
Comprehensive Audit Logging System (Gold Tier)

Provides centralized, structured audit logging for all AI Employee actions.
Supports multiple log types, retention policies, and audit queries.

Features:
- Structured JSON logging
- Multiple log categories
- Retention policies
- Audit queries and reports
- Log rotation
- Compliance-ready format
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

# Configure base logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Audit_Log")


class LogCategory(Enum):
    """Log categories for classification."""
    ACTION = "action"
    APPROVAL = "approval"
    ERROR = "error"
    SYSTEM = "system"
    FINANCIAL = "financial"
    COMMUNICATION = "communication"
    SOCIAL = "social"
    SECURITY = "security"


class AuditLogger:
    """
    Comprehensive audit logging for Personal AI Employee.
    """
    
    def __init__(self, vault_path: str, retention_days: int = 90):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.audit_dir = self.logs_dir / 'audit'
        self.retention_days = retention_days
        
        # Ensure directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Daily log cache
        self._log_cache = {}
        
    def log(
        self,
        category: LogCategory,
        action_type: str,
        actor: str,
        details: Dict[str, Any],
        result: str = "success",
        target: str = None
    ) -> Path:
        """
        Log an audit entry.
        
        Args:
            category: Log category
            action_type: Type of action (e.g., 'email_send', 'invoice_create')
            actor: Who/what performed the action (e.g., 'qwen_code', 'human')
            details: Additional details about the action
            result: Result status (success, failure, pending)
            target: Target of the action (e.g., email address, customer name)
        
        Returns:
            Path to the log file
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y-%m-%d')
        
        # Create log entry
        entry = {
            'timestamp': timestamp.isoformat(),
            'category': category.value,
            'action_type': action_type,
            'actor': actor,
            'target': target,
            'result': result,
            'details': details,
            'metadata': {
                'vault_path': str(self.vault_path),
                'hostname': os.getenv('HOSTNAME', 'unknown'),
                'user': os.getenv('USER', 'unknown')
            }
        }
        
        # Get or create daily log
        log_file = self.audit_dir / f"audit_{date_str}.jsonl"
        
        # Append to log file (JSONL format for efficiency)
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Also log to category-specific file for easier access
        category_file = self.logs_dir / f"{category.value}_{date_str}.json"
        self._append_to_category_log(category_file, entry)
        
        return log_file
    
    def _append_to_category_log(self, file_path: Path, entry: Dict):
        """Append entry to category-specific log."""
        if file_path.exists():
            try:
                logs = json.loads(file_path.read_text())
                if not isinstance(logs, list):
                    logs = [logs]
            except:
                logs = []
        else:
            logs = []
        
        logs.append(entry)
        file_path.write_text(json.dumps(logs, indent=2))
    
    def log_action(
        self,
        action_type: str,
        actor: str,
        details: Dict,
        result: str = "success",
        target: str = None
    ) -> Path:
        """Convenience method for logging actions."""
        return self.log(
            category=LogCategory.ACTION,
            action_type=action_type,
            actor=actor,
            details=details,
            result=result,
            target=target
        )
    
    def log_approval(
        self,
        action_type: str,
        approver: str,
        decision: str,
        item_id: str,
        details: Dict = None
    ) -> Path:
        """Log approval/rejection decision."""
        return self.log(
            category=LogCategory.APPROVAL,
            action_type=f"approval_{decision}",
            actor=approver,
            details=details or {},
            result=decision,
            target=item_id
        )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        actor: str,
        context: Dict = None,
        severity: str = "error"
    ) -> Path:
        """Log error with full context."""
        return self.log(
            category=LogCategory.ERROR,
            action_type=error_type,
            actor=actor,
            details={
                'error_message': error_message,
                'context': context or {},
                'severity': severity
            },
            result="failure"
        )
    
    def log_financial(
        self,
        transaction_type: str,
        amount: float,
        actor: str,
        details: Dict = None
    ) -> Path:
        """Log financial transaction."""
        return self.log(
            category=LogCategory.FINANCIAL,
            action_type=transaction_type,
            actor=actor,
            details={
                'amount': amount,
                'currency': 'USD',
                **(details or {})
            },
            result="success"
        )
    
    def log_communication(
        self,
        channel: str,
        direction: str,
        actor: str,
        recipient: str,
        details: Dict = None
    ) -> Path:
        """Log communication (email, message, etc.)."""
        return self.log(
            category=LogCategory.COMMUNICATION,
            action_type=f"{channel}_{direction}",
            actor=actor,
            target=recipient,
            details=details or {}
        )
    
    def log_social(
        self,
        platform: str,
        action_type: str,
        actor: str,
        content_id: str,
        details: Dict = None
    ) -> Path:
        """Log social media action."""
        return self.log(
            category=LogCategory.SOCIAL,
            action_type=f"{platform}_{action_type}",
            actor=actor,
            target=content_id,
            details=details or {}
        )
    
    def log_security(
        self,
        event_type: str,
        actor: str,
        details: Dict = None,
        severity: str = "info"
    ) -> Path:
        """Log security-related event."""
        return self.log(
            category=LogCategory.SECURITY,
            action_type=event_type,
            actor=actor,
            details={
                'severity': severity,
                **(details or {})
            }
        )
    
    def query(
        self,
        start_date: str = None,
        end_date: str = None,
        category: str = None,
        actor: str = None,
        action_type: str = None,
        result: str = None
    ) -> List[Dict]:
        """
        Query audit logs with filters.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            category: Filter by category
            actor: Filter by actor
            action_type: Filter by action type
            result: Filter by result
        
        Returns:
            List of matching log entries
        """
        results = []
        
        # Determine date range
        if not start_date:
            start_date = (datetime.now() - timedelta(days=self.retention_days)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Iterate through date range
        current = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            log_file = self.audit_dir / f"audit_{date_str}.jsonl"
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            
                            # Apply filters
                            if category and entry.get('category') != category:
                                continue
                            if actor and entry.get('actor') != actor:
                                continue
                            if action_type and entry.get('action_type') != action_type:
                                continue
                            if result and entry.get('result') != result:
                                continue
                            
                            results.append(entry)
                        except:
                            continue
            
            current += timedelta(days=1)
        
        return results
    
    def get_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get summary statistics for the specified period.
        
        Args:
            days: Number of days to summarize
        
        Returns:
            Dict with summary statistics
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        entries = self.query(start_date=start_date, end_date=end_date)
        
        # Calculate statistics
        stats = {
            'period_days': days,
            'start_date': start_date,
            'end_date': end_date,
            'total_entries': len(entries),
            'by_category': {},
            'by_actor': {},
            'by_result': {},
            'by_action_type': {}
        }
        
        for entry in entries:
            # By category
            cat = entry.get('category', 'unknown')
            stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1
            
            # By actor
            actor = entry.get('actor', 'unknown')
            stats['by_actor'][actor] = stats['by_actor'].get(actor, 0) + 1
            
            # By result
            result = entry.get('result', 'unknown')
            stats['by_result'][result] = stats['by_result'].get(result, 0) + 1
            
            # By action type
            action = entry.get('action_type', 'unknown')
            stats['by_action_type'][action] = stats['by_action_type'].get(action, 0) + 1
        
        return stats
    
    def generate_audit_report(self, period_days: int = 30) -> str:
        """
        Generate a comprehensive audit report.
        
        Args:
            period_days: Number of days to cover
        
        Returns:
            Markdown formatted audit report
        """
        summary = self.get_summary(period_days)
        
        report = f"""---
generated: {datetime.now().isoformat()}
period_days: {period_days}
---

# Audit Report

## Summary

| Metric | Value |
|--------|-------|
| Period | {summary['start_date']} to {summary['end_date']} |
| Total Entries | {summary['total_entries']} |
| Entries/Day | {summary['total_entries'] / period_days:.1f} |

## Entries by Category

| Category | Count | Percentage |
|----------|-------|------------|
"""
        
        for cat, count in sorted(summary['by_category'].items(), key=lambda x: -x[1]):
            pct = count / summary['total_entries'] * 100 if summary['total_entries'] > 0 else 0
            report += f"| {cat.title()} | {count} | {pct:.1f}% |\n"
        
        report += f"""
## Entries by Actor

| Actor | Count | Percentage |
|-------|-------|------------|
"""
        
        for actor, count in sorted(summary['by_actor'].items(), key=lambda x: -x[1]):
            pct = count / summary['total_entries'] * 100 if summary['total_entries'] > 0 else 0
            report += f"| {actor} | {count} | {pct:.1f}% |\n"
        
        report += f"""
## Results Distribution

| Result | Count | Percentage |
|--------|-------|------------|
"""
        
        for result, count in sorted(summary['by_result'].items(), key=lambda x: -x[1]):
            pct = count / summary['total_entries'] * 100 if summary['total_entries'] > 0 else 0
            report += f"| {result.title()} | {count} | {pct:.1f}% |\n"
        
        # Top action types
        top_actions = sorted(summary['by_action_type'].items(), key=lambda x: -x[1])[:10]
        
        report += f"""
## Top Action Types

| Action Type | Count |
|-------------|-------|
"""
        
        for action, count in top_actions:
            report += f"| {action} | {count} |\n"
        
        report += f"""
---
*Generated by Personal AI Employee Audit System (Gold Tier)*
"""
        
        return report
    
    def cleanup_old_logs(self) -> int:
        """
        Remove logs older than retention period.
        
        Returns:
            Number of files removed
        """
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        removed = 0
        
        for log_file in self.audit_dir.glob('audit_*.jsonl'):
            try:
                # Extract date from filename
                date_str = log_file.stem.replace('audit_', '')
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff:
                    log_file.unlink()
                    removed += 1
                    logger.info(f"Removed old log: {log_file}")
            except Exception as e:
                logger.warning(f"Error processing {log_file}: {e}")
        
        return removed


# Global audit logger instance
_audit_logger = None


def get_audit_logger(vault_path: str = None) -> AuditLogger:
    """Get or create global audit logger instance."""
    global _audit_logger
    
    if _audit_logger is None:
        vault = vault_path or os.getenv('VAULT_PATH', './vault')
        _audit_logger = AuditLogger(vault)
    
    return _audit_logger


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit Logging System')
    parser.add_argument('--vault', default='./vault', help='Path to vault')
    parser.add_argument('--query', action='store_true', help='Query logs')
    parser.add_argument('--summary', action='store_true', help='Show summary')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--cleanup', action='store_true', help='Clean up old logs')
    parser.add_argument('--days', type=int, default=7, help='Days for summary/report')
    
    args = parser.parse_args()
    
    logger = AuditLogger(args.vault)
    
    if args.cleanup:
        removed = logger.cleanup_old_logs()
        print(f"Removed {removed} old log files")
    
    if args.summary:
        summary = logger.get_summary(args.days)
        print(json.dumps(summary, indent=2))
    
    if args.report:
        report = logger.generate_audit_report(args.days)
        print(report)
    
    if args.query:
        entries = logger.query()
        print(f"Found {len(entries)} entries")
        for entry in entries[:10]:
            print(json.dumps(entry, indent=2))
