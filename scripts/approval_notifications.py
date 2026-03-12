#!/usr/bin/env python3
"""
Approval Notifications - Send notifications when items need human approval

Supports:
- Slack webhooks
- Discord webhooks
- Email notifications
- Console logging

Usage:
    python scripts/approval_notifications.py --vault ./vault --message "New approval needed"
"""

import os
import sys
import json
import requests
import smtplib
import argparse
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


class ApprovalNotifier:
    """Send approval notifications via multiple channels."""
    
    def __init__(self, vault_path: str = None):
        self.vault = Path(vault_path) if vault_path else Path('./vault')
        
        # Load webhook URLs from environment
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        
        # Email configuration
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.notification_email = os.getenv('NOTIFICATION_EMAIL')
        
        # Notification log
        self.log_path = self.vault / "Logs" / "notifications.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_notification(self, channel: str, status: str, message: str):
        """Log notification attempt."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{channel}] [{status}] {message}\n"
        
        with open(self.log_path, 'a') as f:
            f.write(log_entry)
        
        # Also print to console
        colors = {
            "success": GREEN,
            "error": RED,
            "warning": YELLOW,
            "info": BLUE
        }
        color = colors.get(status, RESET)
        print(f"{color}[{channel}] {message}{RESET}")
    
    def send_slack(self, message: str, title: str = None, color: str = "warning"):
        """Send notification to Slack."""
        if not self.slack_webhook:
            self.log_notification("Slack", "warning", "Webhook URL not configured")
            return False
        
        payload = {
            "text": title or "🔔 Approval Required",
            "attachments": [
                {
                    "color": color,
                    "text": message,
                    "footer": "Personal AI Employee - Silver Tier",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        try:
            response = requests.post(
                self.slack_webhook,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_notification("Slack", "success", "Notification sent")
                return True
            else:
                self.log_notification("Slack", "error", f"HTTP {response.status_code}: {response.text[:100]}")
                return False
                
        except Exception as e:
            self.log_notification("Slack", "error", str(e))
            return False
    
    def send_discord(self, message: str, title: str = None, color: int = 16753920):
        """Send notification to Discord."""
        if not self.discord_webhook:
            self.log_notification("Discord", "warning", "Webhook URL not configured")
            return False
        
        payload = {
            "embeds": [
                {
                    "title": title or "🔔 Approval Required",
                    "description": message,
                    "color": color,
                    "footer": {
                        "text": "Personal AI Employee - Silver Tier"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        try:
            response = requests.post(
                self.discord_webhook,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                self.log_notification("Discord", "success", "Notification sent")
                return True
            else:
                self.log_notification("Discord", "error", f"HTTP {response.status_code}: {response.text[:100]}")
                return False
                
        except Exception as e:
            self.log_notification("Discord", "error", str(e))
            return False
    
    def send_email(self, message: str, subject: str = None, to_email: str = None):
        """Send email notification."""
        if not all([self.smtp_user, self.smtp_password, self.notification_email]):
            self.log_notification("Email", "warning", "SMTP credentials not configured")
            return False
        
        to_email = to_email or self.notification_email
        subject = subject or "🔔 Approval Required - Personal AI Employee"
        
        msg = MIMEMultipart()
        msg['From'] = self.smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        body = f"""
{message}

---
Personal AI Employee - Silver Tier
Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            self.log_notification("Email", "success", f"Sent to {to_email}")
            return True
            
        except Exception as e:
            self.log_notification("Email", "error", str(e))
            return False
    
    def notify_all(self, message: str, title: str = None, channels: list = None):
        """Send notification to all configured channels."""
        if channels is None:
            channels = ['slack', 'discord', 'email', 'console']
        
        results = {}
        
        if 'slack' in channels:
            results['slack'] = self.send_slack(message, title)
        
        if 'discord' in channels:
            results['discord'] = self.send_discord(message, title)
        
        if 'email' in channels:
            results['email'] = self.send_email(message, title)
        
        if 'console' in channels:
            print(f"\n{BOLD}{YELLOW}🔔 APPROVAL REQUIRED{RESET}")
            print(f"{BOLD}Title:{RESET} {title or 'New approval needed'}")
            print(f"{BOLD}Message:{RESET} {message}")
            print()
            results['console'] = True
        
        return results


def check_pending_approvals(vault_path: str, notifier: ApprovalNotifier):
    """Check for pending approvals and send notifications."""
    vault = Path(vault_path)
    pending_folder = vault / "Pending_Approval"
    
    if not pending_folder.exists():
        return
    
    # Get list of pending approvals
    pending_files = list(pending_folder.glob("*.md"))
    
    if not pending_files:
        return
    
    # Check if we already notified about these (using a tracking file)
    notified_file = vault / "Logs" / "notified_approvals.json"
    notified_files = set()
    
    if notified_file.exists():
        try:
            with open(notified_file) as f:
                data = json.load(f)
                notified_files = set(data.get('notified', []))
        except:
            pass
    
    # Send notifications for new pending approvals
    for pending_file in pending_files:
        if pending_file.name not in notified_files:
            # Read the approval file
            content = pending_file.read_text()
            
            # Extract key information
            title = pending_file.stem.replace('_', ' ')
            
            # Find summary in the file
            summary = ""
            if "## Summary" in content:
                summary = content.split("## Summary")[1].split("\n\n")[0].strip()
            elif "# " in content:
                summary = content.split("# ")[1].split("\n")[0].strip()
            
            message = f"""
**File:** {pending_file.name}

**Summary:**
{summary[:500] if summary else 'See file for details'}

**Location:** {pending_folder.absolute()}

**Action Required:**
Move file to Approved/ to approve, or Rejected/ to decline.
"""
            
            # Send notification
            notifier.notify_all(
                message=message,
                title=f"Approval: {title}"
            )
            
            # Mark as notified
            notified_files.add(pending_file.name)
            
            # Save notified list
            with open(notified_file, 'w') as f:
                json.dump({'notified': list(notified_files)}, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Approval Notifications')
    parser.add_argument('--vault', default='./vault', help='Path to vault')
    parser.add_argument('--message', help='Notification message')
    parser.add_argument('--title', help='Notification title')
    parser.add_argument('--channels', nargs='+', default=['console'],
                       choices=['slack', 'discord', 'email', 'console'],
                       help='Notification channels')
    parser.add_argument('--check', action='store_true', help='Check for pending approvals')
    
    args = parser.parse_args()
    
    notifier = ApprovalNotifier(args.vault)
    
    print()
    print(f"{BOLD}{BLUE}{'=' * 50}{RESET}")
    print(f"{BOLD}Approval Notification System{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 50}{RESET}")
    print()
    
    if args.check:
        print("Checking for pending approvals...")
        check_pending_approvals(args.vault, notifier)
    elif args.message:
        print(f"Sending notification...")
        notifier.notify_all(
            message=args.message,
            title=args.title,
            channels=args.channels
        )
    else:
        # Demo mode
        print("Demo mode - sending test notification...")
        notifier.notify_all(
            message="This is a test notification from the Personal AI Employee approval system.",
            title="🧪 Test Notification",
            channels=args.channels
        )
    
    print()
    print(f"{GREEN}✅ Notification system ready{RESET}")
    print()
    print("Configuration tips:")
    print("  - Slack: Set SLACK_WEBHOOK_URL in .env")
    print("  - Discord: Set DISCORD_WEBHOOK_URL in .env")
    print("  - Email: Set SMTP_USER, SMTP_PASSWORD, NOTIFICATION_EMAIL in .env")
    print()


if __name__ == "__main__":
    main()
