#!/usr/bin/env python3
"""
WhatsApp Health Check and Monitoring System
Provides real-time health monitoring, alerting, and auto-recovery for WhatsApp automation.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List

logger = logging.getLogger('WhatsAppHealthMonitor')


class WhatsAppHealthMonitor:
    """
    Monitors WhatsApp automation health and provides:
    - Connection status checks
    - Message processing metrics
    - Error rate tracking
    - Auto-recovery suggestions
    - Performance metrics
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs_path = self.vault_path / 'Logs'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        
        # Health state
        self.health_history: List[Dict] = []
        self.last_check_time = None
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        
        # Metrics
        self.messages_processed_today = 0
        self.messages_sent_today = 0
        self.errors_today = 0
        self.last_message_time = None
        self.last_send_time = None
        
        logger.info(f"WhatsApp Health Monitor initialized")
    
    def check_health(self) -> Dict:
        """
        Perform comprehensive health check.
        Returns health status dictionary.
        """
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'components': {},
                'metrics': self._get_metrics(),
                'alerts': [],
                'recommendations': []
            }
            
            # Check components
            health_status['components']['vault'] = self._check_vault_health()
            health_status['components']['message_queue'] = self._check_message_queue()
            health_status['components']['approval_queue'] = self._check_approval_queue()
            health_status['components']['error_rate'] = self._check_error_rate()
            health_status['components']['disk_space'] = self._check_disk_space()
            
            # Determine overall status
            statuses = [comp['status'] for comp in health_status['components'].values()]
            if 'critical' in statuses:
                health_status['overall_status'] = 'critical'
            elif 'warning' in statuses:
                health_status['overall_status'] = 'warning'
            else:
                health_status['overall_status'] = 'healthy'
            
            # Generate alerts and recommendations
            health_status['alerts'] = self._generate_alerts(health_status['components'])
            health_status['recommendations'] = self._generate_recommendations(health_status['components'])
            
            # Store health history
            self.health_history.append(health_status)
            self.last_check_time = datetime.now()
            
            # Keep only last 100 checks
            if len(self.health_history) > 100:
                self.health_history = self.health_history[-100:]
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'error',
                'error': str(e)
            }
    
    def _check_vault_health(self) -> Dict:
        """Check vault accessibility and structure"""
        try:
            required_dirs = [
                self.needs_action,
                self.pending_approval,
                self.approved,
                self.done,
                self.logs_path
            ]
            
            missing_dirs = [d for d in required_dirs if not d.exists()]
            
            if missing_dirs:
                return {
                    'status': 'critical',
                    'message': f'Missing directories: {[str(d.name) for d in missing_dirs]}',
                    'action_required': True
                }
            
            return {
                'status': 'healthy',
                'message': 'All vault directories present',
                'path': str(self.vault_path)
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Vault check failed: {str(e)}',
                'action_required': True
            }
    
    def _check_message_queue(self) -> Dict:
        """Check message processing queue"""
        try:
            pending_messages = list(self.needs_action.glob('WHATSAPP_*.md'))
            pending_count = len(pending_messages)
            
            # Check for stale messages (older than 1 hour)
            stale_messages = []
            for msg_file in pending_messages:
                file_age = datetime.now() - datetime.fromtimestamp(msg_file.stat().st_mtime)
                if file_age > timedelta(hours=1):
                    stale_messages.append(msg_file.name)
            
            if pending_count > 50:
                return {
                    'status': 'warning',
                    'message': f'High message queue: {pending_count} pending',
                    'pending_count': pending_count,
                    'action_required': False
                }
            
            if stale_messages:
                return {
                    'status': 'warning',
                    'message': f'{len(stale_messages)} stale messages (>1 hour old)',
                    'stale_messages': stale_messages[:5],  # Show first 5
                    'action_required': True
                }
            
            return {
                'status': 'healthy',
                'message': f'{pending_count} messages pending',
                'pending_count': pending_count
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Message queue check failed: {str(e)}',
                'action_required': True
            }
    
    def _check_approval_queue(self) -> Dict:
        """Check approval queue"""
        try:
            pending_approvals = list(self.pending_approval.glob('WHATSAPP_*.md'))
            approved = list(self.approved.glob('WHATSAPP_*.md'))
            
            # Check for stale approvals (older than 24 hours)
            stale_approvals = []
            for approval_file in pending_approvals:
                file_age = datetime.now() - datetime.fromtimestamp(approval_file.stat().st_mtime)
                if file_age > timedelta(hours=24):
                    stale_approvals.append(approval_file.name)
            
            if stale_approvals:
                return {
                    'status': 'warning',
                    'message': f'{len(stale_approvals)} approvals pending >24 hours',
                    'stale_approvals': stale_approvals[:5],
                    'action_required': True
                }
            
            return {
                'status': 'healthy',
                'message': f'{len(pending_approvals)} pending approvals, {len(approved)} ready to execute',
                'pending_count': len(pending_approvals),
                'approved_count': len(approved)
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Approval queue check failed: {str(e)}',
                'action_required': True
            }
    
    def _check_error_rate(self) -> Dict:
        """Check error rates in logs"""
        try:
            # Read today's log file
            log_file = self.logs_path / f"whatsapp_orchestrator_{datetime.now().strftime('%Y%m%d')}.md"
            
            if not log_file.exists():
                return {
                    'status': 'healthy',
                    'message': 'No errors logged today',
                    'error_count': 0
                }
            
            content = log_file.read_text()
            error_count = content.count('Status**: Error')
            failed_count = content.count('send FAILED')
            
            total_errors = error_count + failed_count
            
            if total_errors > 10:
                return {
                    'status': 'warning',
                    'message': f'High error rate: {total_errors} errors today',
                    'error_count': total_errors,
                    'action_required': False
                }
            
            return {
                'status': 'healthy',
                'message': f'{total_errors} errors today',
                'error_count': total_errors
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'Error rate check failed: {str(e)}',
                'action_required': False
            }
    
    def _check_disk_space(self) -> Dict:
        """Check disk space usage"""
        try:
            import shutil
            
            total, used, free = shutil.disk_usage(self.vault_path)
            usage_percent = (used / total) * 100
            
            if usage_percent > 90:
                return {
                    'status': 'critical',
                    'message': f'Disk space critical: {usage_percent:.1f}% used',
                    'usage_percent': usage_percent,
                    'free_gb': free / (1024**3),
                    'action_required': True
                }
            elif usage_percent > 75:
                return {
                    'status': 'warning',
                    'message': f'Disk space warning: {usage_percent:.1f}% used',
                    'usage_percent': usage_percent,
                    'free_gb': free / (1024**3),
                    'action_required': False
                }
            
            return {
                'status': 'healthy',
                'message': f'Disk space OK: {usage_percent:.1f}% used',
                'usage_percent': usage_percent,
                'free_gb': free / (1024**3)
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'Disk space check failed: {str(e)}',
                'action_required': False
            }
    
    def _get_metrics(self) -> Dict:
        """Get processing metrics"""
        return {
            'messages_processed_today': self.messages_processed_today,
            'messages_sent_today': self.messages_sent_today,
            'errors_today': self.errors_today,
            'last_message_time': self.last_message_time.isoformat() if self.last_message_time else None,
            'last_send_time': self.last_send_time.isoformat() if self.last_send_time else None,
            'consecutive_failures': self.consecutive_failures
        }
    
    def _generate_alerts(self, components: Dict) -> List[Dict]:
        """Generate alerts based on component status"""
        alerts = []
        
        for component_name, component_status in components.items():
            if component_status.get('status') == 'critical':
                alerts.append({
                    'severity': 'critical',
                    'component': component_name,
                    'message': component_status.get('message', 'Unknown error'),
                    'timestamp': datetime.now().isoformat(),
                    'action_required': True
                })
            elif component_status.get('status') == 'warning':
                alerts.append({
                    'severity': 'warning',
                    'component': component_name,
                    'message': component_status.get('message', 'Warning'),
                    'timestamp': datetime.now().isoformat(),
                    'action_required': component_status.get('action_required', False)
                })
        
        return alerts
    
    def _generate_recommendations(self, components: Dict) -> List[str]:
        """Generate recommendations based on health status"""
        recommendations = []
        
        # Check message queue
        msg_queue = components.get('message_queue', {})
        if msg_queue.get('pending_count', 0) > 20:
            recommendations.append("Consider increasing orchestrator check frequency")
        
        # Check approval queue
        approval_queue = components.get('approval_queue', {})
        if approval_queue.get('pending_count', 0) > 10:
            recommendations.append("Review and process pending approvals")
        
        # Check error rate
        error_rate = components.get('error_rate', {})
        if error_rate.get('error_count', 0) > 5:
            recommendations.append("Review error logs and fix recurring issues")
        
        # Check disk space
        disk_space = components.get('disk_space', {})
        if disk_space.get('usage_percent', 0) > 70:
            recommendations.append("Clean up old logs and processed files")
        
        return recommendations
    
    def record_message_processed(self) -> None:
        """Record that a message was processed"""
        self.messages_processed_today += 1
        self.last_message_time = datetime.now()
    
    def record_message_sent(self) -> None:
        """Record that a message was sent"""
        self.messages_sent_today += 1
        self.last_send_time = datetime.now()
    
    def record_error(self) -> None:
        """Record an error"""
        self.errors_today += 1
        self.consecutive_failures += 1
    
    def record_success(self) -> None:
        """Record a success (reset consecutive failures)"""
        self.consecutive_failures = 0
    
    def get_health_report(self) -> str:
        """Get formatted health report"""
        health = self.check_health()
        
        report = f"\n{'='*60}\n"
        report += f"WhatsApp Health Report\n"
        report += f"{'='*60}\n"
        report += f"Timestamp: {health['timestamp']}\n"
        report += f"Overall Status: {health['overall_status'].upper()}\n\n"
        
        # Components
        report += "Components:\n"
        for name, status in health['components'].items():
            icon = "✅" if status['status'] == 'healthy' else "⚠️" if status['status'] == 'warning' else "❌"
            report += f"  {icon} {name}: {status['message']}\n"
        
        # Metrics
        report += f"\nMetrics:\n"
        metrics = health['metrics']
        report += f"  - Messages processed today: {metrics['messages_processed_today']}\n"
        report += f"  - Messages sent today: {metrics['messages_sent_today']}\n"
        report += f"  - Errors today: {metrics['errors_today']}\n"
        report += f"  - Consecutive failures: {metrics['consecutive_failures']}\n"
        
        # Alerts
        if health['alerts']:
            report += f"\nAlerts ({len(health['alerts'])}):\n"
            for alert in health['alerts']:
                icon = "🔴" if alert['severity'] == 'critical' else "🟡"
                report += f"  {icon} [{alert['severity'].upper()}] {alert['message']}\n"
        
        # Recommendations
        if health['recommendations']:
            report += f"\nRecommendations:\n"
            for rec in health['recommendations']:
                report += f"  💡 {rec}\n"
        
        report += f"\n{'='*60}\n"
        
        return report
    
    def is_healthy(self) -> bool:
        """Quick health check"""
        health = self.check_health()
        return health['overall_status'] == 'healthy'
    
    def needs_attention(self) -> bool:
        """Check if system needs human attention"""
        health = self.check_health()
        return any(alert.get('action_required') for alert in health.get('alerts', []))
    
    def save_health_report(self) -> Path:
        """Save health report to file"""
        report = self.get_health_report()
        report_file = self.logs_path / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_file.write_text(report)
        return report_file


def main():
    """Run health check"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Health Monitor')
    parser.add_argument('--vault', type=str, default='.')
    parser.add_argument('--report', action='store_true', help='Save report to file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    monitor = WhatsAppHealthMonitor(vault_path=args.vault)
    
    if args.json:
        health = monitor.check_health()
        print(json.dumps(health, indent=2))
    else:
        report = monitor.get_health_report()
        print(report)
        
        if args.report:
            report_file = monitor.save_health_report()
            print(f"\nReport saved to: {report_file}")
    
    # Exit with appropriate code
    if monitor.is_healthy():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
