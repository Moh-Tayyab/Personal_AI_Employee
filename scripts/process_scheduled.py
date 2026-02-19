"""
Scheduled Post Processor - Execute scheduled social media posts

This script runs periodically to process scheduled posts:
- Check vault/Scheduled/ folder
- Execute posts that are due
- Move to Done when complete

Usage:
    python -m scripts.process_scheduled --vault ./vault
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))


class ScheduledPostProcessor:
    """Process scheduled social media posts."""

    def __init__(self, vault_path: str, dry_run: bool = True):
        self.vault_path = Path(vault_path)
        self.scheduled_folder = self.vault_path / 'Scheduled'
        self.done_folder = self.vault_path / 'Done'
        self.dry_run = dry_run

        # Ensure folders exist
        self.scheduled_folder.mkdir(parents=True, exist_ok=True)
        self.done_folder.mkdir(parents=True, exist_ok=True)

    def process_scheduled_posts(self):
        """Process all due scheduled posts."""
        now = datetime.now()
        processed = []

        for post_file in self.scheduled_folder.glob('*.md'):
            try:
                content = post_file.read_text()

                # Parse frontmatter
                scheduled_time = None
                platform = None
                status = None

                in_frontmatter = False
                for line in content.split('\n'):
                    if line.strip() == '---':
                        if not in_frontmatter:
                            in_frontmatter = True
                        else:
                            break
                    elif in_frontmatter:
                        if line.startswith('scheduled_time:'):
                            scheduled_time_str = line.split(':')[1].strip()
                            try:
                                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
                            except:
                                pass
                        elif line.startswith('platform:'):
                            platform = line.split(':')[1].strip()
                        elif line.startswith('status:'):
                            status = line.split(':')[1].strip()

                # Check if it's time to post
                if scheduled_time and status == 'pending':
                    # Convert to local time for comparison
                    if scheduled_time.tzinfo:
                        scheduled_time = scheduled_time.replace(tzinfo=None)

                    if now >= scheduled_time:
                        # Post is due
                        if self.dry_run:
                            print(f"[DRY RUN] Would post to {platform}: {post_file.name}")
                        else:
                            # Execute the post (would call MCP here)
                            print(f"Posting to {platform}: {post_file.name}")

                        # Move to Done
                        dest = self.done_folder / post_file.name
                        post_file.rename(dest)
                        processed.append(post_file.name)

            except Exception as e:
                print(f"Error processing {post_file.name}: {e}")

        return processed


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Process scheduled posts')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--dry-run', action='store_true', default=True)
    parser.add_argument('--live', action='store_false', dest='dry_run')

    args = parser.parse_args()

    processor = ScheduledPostProcessor(args.vault, args.dry_run)
    processed = processor.process_scheduled_posts()

    print(f"Processed {len(processed)} scheduled posts")


if __name__ == "__main__":
    main()
