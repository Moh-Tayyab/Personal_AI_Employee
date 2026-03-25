#!/usr/bin/env python3
"""
Social Media Manager Agent - Silver/Gold Tier

This agent handles all social media operations:
- LinkedIn posts and engagement
- Twitter/X tweets and threads
- Facebook posts and messaging
- Content scheduling and publishing
"""

import argparse
import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vault/Logs/social_media_manager.log')
    ]
)
logger = logging.getLogger("SocialMediaManager")


class SocialMediaManagerAgent:
    """Specialized agent for social media management."""

    def __init__(self, vault_path: str, dry_run: bool = True):
        self.vault_path = Path(vault_path).resolve()
        self.dry_run = dry_run
        
        # Vault directories
        self.needs_action = self.vault_path / "Needs_Action"
        self.drafts = self.vault_path / "Drafts" / "Social"
        self.pending_approval = self.vault_path / "Pending_Approval" / "Social"
        self.approved = self.vault_path / "Approved" / "Social"
        self.done = self.vault_path / "Done" / "Social"
        self.logs = self.vault_path / "Logs"
        self.secrets = self.vault_path / "secrets"
        
        # Ensure directories exist
        for dir_path in [self.drafts, self.pending_approval, self.approved, self.done, self.logs]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Platform configurations
        self.platforms = {
            "linkedin": {
                "max_length": 3000,
                "optimal_length": "150-300",
                "hashtag_limit": 5,
                "best_posting_times": ["9:00", "12:00", "17:00"],
                "best_days": ["Tuesday", "Wednesday", "Thursday"],
                "session_path": self.secrets / "linkedin_session"
            },
            "twitter": {
                "max_length": 280,
                "thread_support": True,
                "hashtag_limit": 3,
                "best_posting_times": ["9:00", "12:00", "18:00"],
                "best_days": ["Wednesday", "Thursday", "Friday"],
                "session_path": self.secrets / "twitter_session"
            },
            "facebook": {
                "max_length": 63206,
                "optimal_length": "40-80",
                "hashtag_limit": 3,
                "best_posting_times": ["9:00", "13:00", "15:00"],
                "best_days": ["Thursday", "Friday", "Saturday", "Sunday"],
                "session_path": self.secrets / "facebook_session"
            }
        }
        
        # Approval rules
        self.approval_required = [
            "partnership", "announcement", "product launch", "major",
            "financial", "investment", "acquisition"
        ]
        
        logger.info(f"Social Media Manager initialized - Vault: {self.vault_path}")
        logger.info(f"Dry run mode: {self.dry_run}")

    def parse_social_task(self, file_path: Path) -> Dict:
        """Parse a social media task file."""
        content = file_path.read_text(encoding='utf-8')
        
        # Extract frontmatter
        frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        metadata = {}
        body = content
        
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            body = content[frontmatter_match.end():].strip()
        
        # Determine platform from metadata or filename
        platform = metadata.get('platform', 'linkedin')
        if 'twitter' in file_path.name.lower() or 'tweet' in file_path.name.lower():
            platform = 'twitter'
        elif 'facebook' in file_path.name.lower():
            platform = 'facebook'
        elif 'linkedin' in file_path.name.lower():
            platform = 'linkedin'
        
        return {
            "file_path": file_path,
            "metadata": metadata,
            "body": body,
            "content": content,
            "platform": platform
        }

    def create_platform_content(self, task: Dict, platform: str) -> str:
        """Create platform-optimized content."""
        body = task["body"]
        metadata = task["metadata"]
        
        # Extract key points from the task
        platform_config = self.platforms.get(platform, self.platforms["linkedin"])
        
        if platform == "linkedin":
            # Professional, longer-form content
            content = self._create_linkedin_content(body, metadata, platform_config)
        elif platform == "twitter":
            # Short, engaging content (may create thread)
            content = self._create_twitter_content(body, metadata, platform_config)
        elif platform == "facebook":
            # Conversational, engaging content
            content = self._create_facebook_content(body, metadata, platform_config)
        else:
            content = f"Content for {platform}:\n\n{body[:platform_config['max_length']]}"
        
        return content

    def _create_linkedin_content(self, body: str, metadata: Dict, config: Dict) -> str:
        """Create LinkedIn-optimized content."""
        # Professional tone, 150-300 words optimal
        content = []
        
        # Hook (first line is critical on LinkedIn)
        content.append("🚀 Exciting news!")
        content.append("")
        
        # Main content
        content.append(body[:1000] if len(body) > 1000 else body)
        content.append("")
        
        # Call to action
        content.append("What are your thoughts on this? Let's discuss in the comments! 👇")
        content.append("")
        
        # Hashtags (3-5 relevant ones)
        hashtags = ["#AI", "#Automation", "#Productivity", "#Innovation", "#Technology"]
        content.append(" ".join(hashtags[:config["hashtag_limit"]]))
        
        return "\n".join(content)

    def _create_twitter_content(self, body: str, metadata: Dict, config: Dict) -> str:
        """Create Twitter-optimized content (may create thread)."""
        # Short, engaging, may need thread
        if len(body) <= config["max_length"]:
            # Single tweet
            return f"{body}\n\n#AI #Automation"
        else:
            # Create thread
            words = body.split()
            tweets = []
            current_tweet = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= config["max_length"] - 20:  # Leave room for thread indicator
                    current_tweet.append(word)
                    current_length += len(word) + 1
                else:
                    tweets.append(" ".join(current_tweet))
                    current_tweet = [word]
                    current_length = len(word)
            
            if current_tweet:
                tweets.append(" ".join(current_tweet))
            
            # Format as thread
            thread = []
            for i, tweet in enumerate(tweets):
                thread.append(f"{i+1}/{len(tweets)} {tweet}")
            
            return "\n\n".join(thread)

    def _create_facebook_content(self, body: str, metadata: Dict, config: Dict) -> str:
        """Create Facebook-optimized content."""
        # Conversational tone
        content = []
        
        content.append(body[:500] if len(body) > 500 else body)
        content.append("")
        content.append("Share your thoughts in the comments! 💬")
        
        # Add emoji for engagement
        emojis = ["👍", "❤️", "🎉", "🚀", "💡"]
        content.append(f"{' '.join(emojis[:3])}")
        
        return "\n".join(content)

    def check_approval_required(self, task: Dict) -> tuple:
        """Check if post requires approval."""
        content = task["content"].lower()
        metadata = task["metadata"]
        
        # Check for approval keywords
        for keyword in self.approval_required:
            if keyword in content:
                return True, f"Contains approval keyword: {keyword}"
        
        # Check priority
        if metadata.get("priority") == "high":
            return True, "High priority content requires approval"
        
        # Check if it's an announcement
        if "announcement" in metadata.get("type", "").lower():
            return True, "Announcement type requires approval"
        
        return False, None

    def create_approval_request(self, task: Dict, content: str, platform: str) -> Path:
        """Create an approval request for social media post."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_file = self.pending_approval / f"APPROVAL_{timestamp}_{Path(task['file_path']).stem}.md"
        
        approval_content = f"""---
type: social_media_approval
created: {datetime.now().isoformat()}
status: pending
platform: {platform}
content_type: {task['metadata'].get('type', 'post')}
---

# Social Media Approval Request

## Platform
{platform.title()}

## Proposed Content

```
{content}
```

## Original Task

---

{task['content']}

---

## Action Required

Please review and:
- Move to `../Approved/Social/` to publish
- Move to `../Rejected/` to decline
- Add comments for modifications

**File:** {approval_file.name}
"""
        
        approval_file.write_text(approval_content, encoding='utf-8')
        logger.info(f"Created approval request: {approval_file}")
        
        return approval_file

    def publish_to_platform(self, content: str, platform: str) -> bool:
        """Publish content to the specified platform."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would publish to {platform}")
            logger.info(f"[DRY RUN] Content preview: {content[:100]}...")
            return True
        
        try:
            if platform == "linkedin":
                from mcp.linkedin.server import LinkedInMCPServer
                server = LinkedInMCPServer()
                server.create_post({"content": content})
                logger.info(f"Published to LinkedIn")
                
            elif platform == "twitter":
                from mcp.twitter.server import TwitterMCPServer
                server = TwitterMCPServer()
                server.post_tweet({"content": content})
                logger.info(f"Published to Twitter")
                
            elif platform == "facebook":
                from mcp.facebook.server import FacebookMCPServer
                server = FacebookMCPServer()
                server.create_post({"content": content})
                logger.info(f"Published to Facebook")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish to {platform}: {e}")
            return False

    def process_social_task(self, file_path: Path) -> Dict:
        """Process a single social media task."""
        logger.info(f"Processing social media task: {file_path.name}")
        
        try:
            # Parse task
            task = self.parse_social_task(file_path)
            platform = task["platform"]
            
            logger.info(f"Platform: {platform}")
            
            # Create platform-optimized content
            content = self.create_platform_content(task, platform)
            logger.info(f"Content created ({len(content)} chars)")
            
            # Check if approval required
            needs_approval, reason = self.check_approval_required(task)
            
            if needs_approval:
                # Create approval request
                approval_file = self.create_approval_request(task, content, platform)
                
                result = {
                    "status": "pending_approval",
                    "file": str(file_path),
                    "approval_file": str(approval_file),
                    "reason": reason,
                    "platform": platform
                }
            else:
                # Publish directly
                if self.dry_run:
                    # Save draft
                    draft_file = self.drafts / f"DRAFT_{platform}_{file_path.stem}.md"
                    draft_file.write_text(f"""---
platform: {platform}
created: {datetime.now().isoformat()}
---

{content}
""", encoding='utf-8')
                    
                    result = {
                        "status": "draft_created",
                        "file": str(file_path),
                        "draft_file": str(draft_file),
                        "platform": platform
                    }
                else:
                    # Publish
                    success = self.publish_to_platform(content, platform)
                    
                    if success:
                        # Move to Done
                        done_file = self.done / file_path.name
                        file_path.rename(done_file)
                        
                        result = {
                            "status": "published",
                            "file": str(file_path),
                            "platform": platform
                        }
                    else:
                        result = {
                            "status": "failed",
                            "file": str(file_path),
                            "error": "Publish failed"
                        }
            
            # Log action
            self.log_action(task, content, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing task {file_path.name}: {e}")
            return {
                "status": "error",
                "file": str(file_path),
                "error": str(e)
            }

    def log_action(self, task: Dict, content: str, result: Dict):
        """Log the social media action."""
        log_file = self.logs / f"social_log_{datetime.now().strftime('%Y%m%d')}.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": {
                "platform": task["platform"],
                "type": task["metadata"].get("type", "post"),
                "content_preview": content[:200]
            },
            "result": result
        }
        
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except:
                logs = []
        
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

    def process_all_tasks(self) -> List[Dict]:
        """Process all social media tasks."""
        results = []
        
        # Find social media tasks
        social_files = []
        social_files.extend(self.needs_action.glob("SOCIAL_*.md"))
        social_files.extend(self.needs_action.glob("*linkedin*.md"))
        social_files.extend(self.needs_action.glob("*twitter*.md"))
        social_files.extend(self.needs_action.glob("*facebook*.md"))
        
        logger.info(f"Found {len(social_files)} social media tasks")
        
        for social_file in social_files:
            result = self.process_social_task(social_file)
            results.append(result)
        
        return results

    def generate_report(self, results: List[Dict]) -> str:
        """Generate a processing report."""
        report = f"""# Social Media Manager Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Dry Run:** {self.dry_run}

## Summary

| Status | Count |
|--------|-------|
| Published | {sum(1 for r in results if r['status'] == 'published')} |
| Draft Created | {sum(1 for r in results if r['status'] == 'draft_created')} |
| Pending Approval | {sum(1 for r in results if r['status'] == 'pending_approval')} |
| Failed | {sum(1 for r in results if r['status'] == 'failed')} |

## Platform Breakdown

"""
        
        platform_counts = {}
        for result in results:
            platform = result.get("platform", "unknown")
            if platform not in platform_counts:
                platform_counts[platform] = {"published": 0, "pending": 0, "draft": 0}
            
            if result["status"] == "published":
                platform_counts[platform]["published"] += 1
            elif result["status"] == "pending_approval":
                platform_counts[platform]["pending"] += 1
            elif result["status"] == "draft_created":
                platform_counts[platform]["draft"] += 1
        
        for platform, counts in platform_counts.items():
            report += f"### {platform.title()}\n"
            report += f"- Published: {counts['published']}\n"
            report += f"- Pending: {counts['pending']}\n"
            report += f"- Drafts: {counts['draft']}\n\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Social Media Manager Agent')
    parser.add_argument('--vault', default='./vault', help='Vault path')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--no-dry-run', action='store_false', dest='dry_run', help='Live mode')
    parser.add_argument('--platform', choices=['linkedin', 'twitter', 'facebook'], help='Specific platform')
    parser.add_argument('--file', type=str, help='Process specific file')
    parser.add_argument('--report', action='store_true', help='Generate report')

    args = parser.parse_args()

    agent = SocialMediaManagerAgent(vault_path=args.vault, dry_run=args.dry_run)

    if args.file:
        result = agent.process_social_task(Path(args.file))
        print(f"\nResult: {result}")
    else:
        results = agent.process_all_tasks()
        
        if args.report:
            report = agent.generate_report(results)
            print(report)
            
            report_file = Path(args.vault) / "Logs" / f"social_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            report_file.write_text(report)
            print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    main()
