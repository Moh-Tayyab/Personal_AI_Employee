"""
Orchestrator - Main coordination script for the AI Employee

The orchestrator manages the coordination between watchers, Claude Code,
and MCP servers. It handles scheduling, folder watching, and the
Ralph Wiggum persistence loop.

Usage:
    python orchestrator.py --vault ./vault
"""

import time
import subprocess
import logging
import signal
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

# Add scripts directory to path for imports
sys.path.append(str(Path(__file__).parent / "scripts"))

try:
    from multi_cli_manager import MultiCLIManager
    from quota_manager import QuotaManager
    from multi_provider_ai import MultiProviderAI
    MULTI_CLI_AVAILABLE = True
    MULTI_PROVIDER_AVAILABLE = True
except ImportError:
    MULTI_CLI_AVAILABLE = False
    MULTI_PROVIDER_AVAILABLE = False
    logging.warning("Multi-provider system not available - falling back to original API calls")

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Orchestrator")


class Orchestrator:
    """Main orchestrator for the AI Employee."""

    def __init__(self, vault_path: str, dry_run: bool = True, primary_cli: str = "claude"):
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run
        self.running = True
        self.ralph_mode = False
        self.current_task = None
        self.primary_cli = primary_cli

        # Initialize Multi-Provider AI System (NEW - maintains Claude Code functionality)
        if MULTI_PROVIDER_AVAILABLE:
            try:
                self.multi_provider_ai = MultiProviderAI(str(vault_path))
                logger.info("✅ Multi-Provider AI system initialized (with full Claude Code functionality)")
            except Exception as e:
                logger.warning(f"Multi-Provider AI initialization failed: {e}")
                self.multi_provider_ai = None
        else:
            self.multi_provider_ai = None

        # Initialize Multi-CLI Manager (LEGACY - for basic CLI routing)
        if MULTI_CLI_AVAILABLE:
            try:
                self.multi_cli = MultiCLIManager(str(vault_path))
                self.quota_manager = QuotaManager(str(vault_path))
                logger.info("✅ Multi-CLI system initialized (legacy mode)")
            except Exception as e:
                logger.warning(f"Multi-CLI initialization failed: {e}")
                self.multi_cli = None
                self.quota_manager = None
        else:
            self.multi_cli = None
            self.quota_manager = None

        # Directories
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        for d in [self.needs_action, self.plans, self.done,
                  self.pending_approval, self.approved, self.rejected, self.logs]:
            d.mkdir(parents=True, exist_ok=True)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def check_needs_action(self) -> list:
        """Check for items in Needs_Action folder."""
        items = []
        for f in self.needs_action.glob('*.md'):
            # Skip metadata files
            if f.stat().st_size > 0:
                items.append(f)
        return items

    def check_pending_approval(self) -> list:
        """Check for items needing approval."""
        items = []
        for f in self.pending_approval.glob('*.md'):
            items.append(f)
        return items

    def check_approved(self) -> list:
        """Check for approved items ready for execution."""
        items = []
        for f in self.approved.glob('*.md'):
            items.append(f)
        return items

    def trigger_ai(self, prompt: str) -> bool:
        """Process item using AI with multi-provider system maintaining full Claude Code functionality."""
        logger.info(f"Processing with AI: {prompt[:100]}...")

        if self.dry_run:
            logger.info("[DRY RUN] Would call AI API")
            logger.info(f"Prompt: {prompt}")
            return True

        # Use Multi-Provider AI system if available (PREFERRED - maintains Claude Code functionality)
        if self.multi_provider_ai:
            return self._process_with_multi_provider_ai(prompt)
        # Fallback to Multi-CLI system (LEGACY - loses Claude Code functionality)
        elif self.multi_cli:
            return self._process_with_multi_cli(prompt)
        else:
            # Final fallback to original API system
            return self._process_with_original_apis(prompt)

    def _process_with_multi_provider_ai(self, prompt: str) -> bool:
        """Process using the multi-provider AI system with full Claude Code functionality."""
        try:
            # Load context from vault
            context = self._load_vault_context()

            # Determine task type for optimal provider routing
            task_type = self._determine_task_type(prompt)

            # Build full prompt with context and instructions
            full_prompt = f"""You are a Personal AI Employee managing business affairs for Muhammad Tayyab.

{context}

## Your Role
- Analyze incoming items (emails, messages, files)
- Determine appropriate actions based on the handbook and goals
- Create action plans with clear next steps
- Flag items requiring human approval
- Execute approved actions through MCP servers
- Use available tools (bash, read, write, edit, glob, grep, web_search, playwright, etc.)
- Leverage skills (/process-emails, /pdf, /browsing-with-playwright, etc.)

## Available Capabilities
- 🛠️ Tools: bash, read, write, edit, glob, grep, web_search, web_fetch, playwright, agent
- 🔌 MCP Servers: email, social, linkedin, twitter
- 🎯 Skills: process-emails, multi-cli-processor, pdf, browsing-with-playwright
- 🧠 Thinking Mode: Available for complex reasoning

## Output Format
Respond with a structured action plan in markdown:

### Analysis
[Your analysis of the item]

### Recommended Actions
1. [Action 1 - specify tools/skills to use]
2. [Action 2 - specify MCP servers if needed]

### Approval Required
[YES/NO - explain why if yes]

### Priority
[LOW/MEDIUM/HIGH/URGENT]

### Category
[finance/calendar/career/general/etc]

### Tools/Skills Needed
[List specific tools, skills, or MCP servers required]

---

Process this item and provide an action plan:

{prompt}
"""

            # Determine if thinking mode should be used
            use_thinking = task_type in ["reasoning", "planning", "complex_analysis"]

            # Process with multi-provider AI system
            provider_used, response = self.multi_provider_ai.process_with_tools(
                prompt=full_prompt,
                task_type=task_type,
                use_tools=True,
                thinking=use_thinking
            )

            if provider_used == "none":
                logger.error("All AI providers failed, falling back to rule-based processing")
                return self._fallback_rule_based_processing(prompt)

            logger.info(f"✅ AI response received via {provider_used} ({len(response)} chars)")
            logger.info(f"Response preview: {response[:200]}...")

            # Save AI response to Plans folder
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            plan_path = self.vault_path / 'Plans' / f'AI_PLAN_{timestamp}.md'
            plan_path.parent.mkdir(parents=True, exist_ok=True)

            plan_content = f"""---
type: ai_plan
created: {datetime.now().isoformat()}
provider: {provider_used}
task_type: {task_type}
thinking_mode: {use_thinking}
tools_available: true
mcp_servers_available: true
skills_available: true
status: pending_review
---

# AI Action Plan (Multi-Provider)

**Provider Used:** {provider_used}
**Task Type:** {task_type}
**Thinking Mode:** {"Enabled" if use_thinking else "Disabled"}

{response}

---

## Original Item
{prompt[:1000]}

## System Capabilities Used
- ✅ Full Claude Code functionality maintained
- ✅ Tools: bash, read, write, edit, glob, grep, web_search, playwright
- ✅ MCP Servers: email, social, linkedin, twitter
- ✅ Skills: process-emails, pdf, browsing-with-playwright
- ✅ Thinking Mode: {"Available" if use_thinking else "Not used for this task"}
"""

            plan_path.write_text(plan_content)
            logger.info(f"AI plan saved: {plan_path}")

            # Parse response to determine if approval needed
            if 'approval required' in response.lower() and 'yes' in response.lower():
                logger.info("AI flagged for approval - moving to Pending_Approval")
                approval_path = self.vault_path / 'Pending_Approval' / f'APPROVAL_{timestamp}.md'
                approval_path.parent.mkdir(parents=True, exist_ok=True)
                approval_path.write_text(plan_content)

            # Log provider usage for monitoring
            self.log_activity('ai_processing', {
                'provider_used': provider_used,
                'task_type': task_type,
                'thinking_mode': use_thinking,
                'tools_available': True,
                'mcp_servers_available': True,
                'skills_available': True,
                'prompt_length': len(prompt),
                'response_length': len(response),
                'timestamp': datetime.now().isoformat()
            })

            return True

        except Exception as e:
            logger.error(f"Error in multi-provider AI processing: {e}")
            logger.info("Falling back to multi-CLI system")
            if self.multi_cli:
                return self._process_with_multi_cli(prompt)
            else:
                return self._fallback_rule_based_processing(prompt)

    def _determine_task_type(self, content: str) -> str:
        """Determine task type for optimal provider routing"""
        content_lower = content.lower()

        # Complex reasoning tasks
        if any(keyword in content_lower for keyword in [
            "analyze", "plan", "strategy", "decision", "evaluate", "assess",
            "consider", "recommend", "complex", "reasoning", "think through"
        ]):
            return "reasoning"

        # Code-related tasks
        if any(keyword in content_lower for keyword in [
            "function", "class", "code", "programming", "debug", "script",
            "python", "javascript", "html", "css", "api", "database"
        ]):
            return "code"

        # Tool-heavy tasks
        if any(keyword in content_lower for keyword in [
            "file", "directory", "search", "web", "browser", "playwright",
            "automation", "scraping", "download", "upload"
        ]):
            return "tool_heavy"

        # Simple processing tasks
        if any(keyword in content_lower for keyword in [
            "extract", "summarize", "list", "count", "find", "simple",
            "quick", "basic", "format", "convert"
        ]):
            return "simple"

        return "general"

    def _process_with_multi_cli(self, prompt: str) -> bool:
        """Process using the multi-CLI system with automatic fallback."""
        try:
            # Load context from vault
            context = self._load_vault_context()

            # Build full prompt with context
            full_prompt = f"""You are a Personal AI Employee managing business affairs for Muhammad Tayyab.

{context}

## Your Role
- Analyze incoming items (emails, messages, files)
- Determine appropriate actions based on the handbook and goals
- Create action plans with clear next steps
- Flag items requiring human approval
- Execute approved actions through MCP servers

## Output Format
Respond with a structured action plan in markdown:

### Analysis
[Your analysis of the item]

### Recommended Actions
1. [Action 1]
2. [Action 2]

### Approval Required
[YES/NO - explain why if yes]

### Priority
[LOW/MEDIUM/HIGH/URGENT]

### Category
[finance/calendar/career/general/etc]

---

Process this item and provide an action plan:

{prompt}
"""

            # Use multi-CLI manager to process with best available CLI
            cli_used, response = self.multi_cli.process_with_best_cli(full_prompt, context)

            if cli_used == "none":
                logger.error("All CLIs failed, falling back to rule-based processing")
                return self._fallback_rule_based_processing(prompt)

            logger.info(f"✅ AI response received via {cli_used} ({len(response)} chars)")
            logger.info(f"Response preview: {response[:200]}...")

            # Save AI response to Plans folder
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            plan_path = self.vault_path / 'Plans' / f'AI_PLAN_{timestamp}.md'
            plan_path.parent.mkdir(parents=True, exist_ok=True)

            plan_content = f"""---
type: ai_plan
created: {datetime.now().isoformat()}
model: {cli_used}
status: pending_review
---

# AI Action Plan

{response}

---

## Original Item
{prompt[:1000]}
"""

            plan_path.write_text(plan_content)
            logger.info(f"AI plan saved: {plan_path}")

            # Parse response to determine if approval needed
            if 'approval required' in response.lower() and 'yes' in response.lower():
                logger.info("AI flagged for approval - moving to Pending_Approval")
                approval_path = self.vault_path / 'Pending_Approval' / f'APPROVAL_{timestamp}.md'
                approval_path.parent.mkdir(parents=True, exist_ok=True)
                approval_path.write_text(plan_content)

            # Log CLI usage for monitoring
            self.log_activity('ai_processing', {
                'cli_used': cli_used,
                'prompt_length': len(prompt),
                'response_length': len(response),
                'timestamp': datetime.now().isoformat()
            })

            return True

        except Exception as e:
            logger.error(f"Error in multi-CLI processing: {e}")
            logger.info("Falling back to rule-based processing")
            return self._fallback_rule_based_processing(prompt)

    def _load_vault_context(self) -> str:
        """Load context from vault files."""
        handbook_path = self.vault_path / 'Company_Handbook.md'
        goals_path = self.vault_path / 'Business_Goals.md'

        handbook = handbook_path.read_text() if handbook_path.exists() else "No handbook found."
        goals = goals_path.read_text() if goals_path.exists() else "No goals defined."

        return f"""## Company Handbook
{handbook}

## Business Goals
{goals}"""

    def _process_with_original_apis(self, prompt: str) -> bool:
        """Fallback to original API system when multi-CLI not available."""
        logger.info("Using original API system (multi-CLI not available)")

        # Check for API keys (try in order: Gemini, OpenRouter, Anthropic)
        gemini_key = os.getenv('GEMINI_API_KEY')
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')

        if not gemini_key and not openrouter_key and not anthropic_key:
            logger.error("No API key found (tried GEMINI_API_KEY, OPENROUTER_API_KEY, ANTHROPIC_API_KEY)")
            logger.info("Falling back to rule-based processing")
            return self._fallback_rule_based_processing(prompt)

        try:
            context = self._load_vault_context()
            system_prompt = f"""You are a Personal AI Employee managing business affairs for Muhammad Tayyab.

{context}

## Your Role
- Analyze incoming items (emails, messages, files)
- Determine appropriate actions based on the handbook and goals
- Create action plans with clear next steps
- Flag items requiring human approval
- Execute approved actions through MCP servers

## Output Format
Respond with a structured action plan in markdown:

### Analysis
[Your analysis of the item]

### Recommended Actions
1. [Action 1]
2. [Action 2]

### Approval Required
[YES/NO - explain why if yes]

### Priority
[LOW/MEDIUM/HIGH/URGENT]

### Category
[finance/calendar/career/general/etc]
"""

            response = None
            api_used = None

            # Try Gemini first (if key available)
            if gemini_key and not response:
                logger.info("Trying Gemini API")
                try:
                    import requests

                    # Combine system prompt and user message
                    full_prompt = f"{system_prompt}\n\n---\n\nProcess this item and provide an action plan:\n\n{prompt}"

                    data = {
                        "contents": [{
                            "parts": [{
                                "text": full_prompt
                            }]
                        }],
                        "generationConfig": {
                            "maxOutputTokens": 4096,
                            "temperature": 0.7
                        }
                    }

                    response_obj = requests.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}",
                        json=data,
                        timeout=60
                    )

                    if response_obj.status_code == 200:
                        result = response_obj.json()
                        response = result['candidates'][0]['content']['parts'][0]['text']
                        api_used = "Gemini"
                        logger.info(f"Gemini API call successful")
                    else:
                        raise Exception(f"Gemini API error: {response_obj.status_code} - {response_obj.text[:200]}")

                except Exception as e:
                    logger.warning(f"Gemini failed: {e}")

            # Try OpenRouter if Gemini failed
            if openrouter_key and not response:
                logger.info("Trying OpenRouter API")
                try:
                    import requests

                    headers = {
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/yourusername/personal-ai-employee",
                        "X-Title": "Personal AI Employee"
                    }

                    full_prompt = f"{system_prompt}\n\n---\n\nProcess this item and provide an action plan:\n\n{prompt}"

                    data = {
                        "model": "anthropic/claude-3.5-sonnet",
                        "messages": [
                            {
                                "role": "user",
                                "content": full_prompt
                            }
                        ],
                        "max_tokens": 1000  # Reduced to fit budget constraints
                    }

                    response_obj = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=60
                    )

                    if response_obj.status_code == 200:
                        result = response_obj.json()
                        response = result['choices'][0]['message']['content']
                        api_used = "OpenRouter"
                        logger.info(f"OpenRouter API call successful")
                    else:
                        raise Exception(f"OpenRouter API error: {response_obj.status_code} - {response_obj.text[:200]}")

                except Exception as e:
                    logger.warning(f"OpenRouter failed: {e}")

            # Try Anthropic direct API if others failed
            if anthropic_key and not response:
                logger.info("Trying Anthropic direct API")
                try:
                    import anthropic
                except ImportError:
                    logger.error("anthropic package not installed - run: pip install anthropic")
                    return self._fallback_rule_based_processing(prompt)

                client = anthropic.Anthropic(api_key=anthropic_key)

                message = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=4096,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Process this item and provide an action plan:\n\n{prompt}"
                        }
                    ]
                )

                response = message.content[0].text
                api_used = "Anthropic"

            # If no API worked, fall back to rule-based
            if not response:
                logger.error("All API providers failed")
                return self._fallback_rule_based_processing(prompt)

            logger.info(f"AI response received via {api_used} ({len(response)} chars)")
            logger.info(f"Response preview: {response[:200]}...")

            # Save AI response to Plans folder
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            plan_path = self.vault_path / 'Plans' / f'AI_PLAN_{timestamp}.md'
            plan_path.parent.mkdir(parents=True, exist_ok=True)

            plan_content = f"""---
type: ai_plan
created: {datetime.now().isoformat()}
model: {api_used}
status: pending_review
---

# AI Action Plan

{response}

---

## Original Item
{prompt[:1000]}
"""

            plan_path.write_text(plan_content)
            logger.info(f"AI plan saved: {plan_path}")

            # Parse response to determine if approval needed
            if 'approval required' in response.lower() and 'yes' in response.lower():
                logger.info("AI flagged for approval - moving to Pending_Approval")
                approval_path = self.vault_path / 'Pending_Approval' / f'APPROVAL_{timestamp}.md'
                approval_path.parent.mkdir(parents=True, exist_ok=True)
                approval_path.write_text(plan_content)

            return True

        except Exception as e:
            logger.error(f"Error calling AI API: {e}")
            logger.info("Falling back to rule-based processing")
            return self._fallback_rule_based_processing(prompt)

    # Keep backward compatibility
    def trigger_claude(self, prompt: str) -> bool:
        """Backward compatibility wrapper for trigger_ai."""
        return self.trigger_ai(prompt)

    def _fallback_rule_based_processing(self, prompt: str) -> bool:
        """Fallback to rule-based processing when Claude API unavailable."""
        logger.info("Using rule-based fallback processing")

        try:
            import re

            email_content = prompt
            priority = "normal"
            urgent_keywords = ['urgent', 'asap', 'emergency', 'critical', 'immediately', 'deadline']
            high_keywords = ['important', 'meeting', 'tomorrow', 'invoice', 'payment', 'due']

            email_lower = email_content.lower()
            if any(kw in email_lower for kw in urgent_keywords):
                priority = "urgent"
            elif any(kw in email_lower for kw in high_keywords):
                priority = "high"

            category = "general"
            if any(kw in email_lower for kw in ['invoice', 'bill', 'payment', 'receipt']):
                category = "finance"
            elif any(kw in email_lower for kw in ['meeting', 'schedule', 'call', 'zoom']):
                category = "calendar"
            elif any(kw in email_lower for kw in ['interview', 'job', 'position', 'resume']):
                category = "career"

            # Save to Drafts with rule-based classification
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            draft_path = self.vault_path / 'Drafts' / f'RULE_BASED_{timestamp}.md'
            draft_path.parent.mkdir(parents=True, exist_ok=True)

            draft_content = f"""---
type: rule_based_classification
priority: {priority}
category: {category}
created: {datetime.now().isoformat()}
---

# Rule-Based Classification

**Priority:** {priority}
**Category:** {category}

## Original Content
{email_content[:500]}

## Note
This was processed using rule-based classification because Claude API was unavailable.
For intelligent processing, set ANTHROPIC_API_KEY in your .env file.
"""

            draft_path.write_text(draft_content)
            logger.info(f"Rule-based draft saved: {draft_path}")

            return True

        except Exception as e:
            logger.error(f"Error in fallback processing: {e}")
            return False

    def create_plan(self, source_item: Path) -> Path:
        """Create a Plan.md file for an item in Needs_Action."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_name = f"PLAN_{timestamp}_{source_item.stem[:30]}.md"
        plan_file = self.plans / plan_name

        # Read the source item to get context
        content = source_item.read_text()

        # Extract type and key info
        item_type = 'unknown'
        from_line = 'Unknown'
        subject_line = 'No subject'

        for line in content.split('\n'):
            if line.startswith('type:'):
                item_type = line.split(':')[1].strip()
            elif line.startswith('from:'):
                from_line = line.split(':')[1].strip()
            elif line.startswith('subject:'):
                subject_line = line.split(':')[1].strip()

        # Create plan content
        plan_content = f"""---
type: plan
source_file: {source_item.name}
created: {datetime.now().isoformat()}
status: in_progress
---

# Plan for: {subject_line}

## Source
- **Type:** {item_type}
- **From:** {from_line}
- **Original File:** {source_item.name}

## Analysis

_AI Employee: Analyze the item and determine required actions._

## Action Items

- [ ] Review the item in Needs_Action/{source_item.name}
- [ ] Determine required actions based on Company_Handbook.md
- [ ] Execute appropriate actions
- [ ] If approval needed, create approval request in Pending_Approval/
- [ ] Move completed items to Done/

## Notes
_Created by Orchestrator at {datetime.now().isoformat()}_
"""

        plan_file.write_text(plan_content)
        logger.info(f"Created plan: {plan_file.name}")
        return plan_file

    def move_to_in_progress(self, item: Path):
        """Move item to In_Progress folder (claim ownership)."""
        in_progress = self.vault_path / 'In_Progress'
        in_progress.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = in_progress / f"{item.stem}_{timestamp}{item.suffix}"
        item.rename(dest)
        logger.info(f"Moved to In_Progress: {dest.name}")

    def process_approved_item(self, item: Path) -> bool:
        """Process an approved item using MCP servers."""
        logger.info(f"Processing approved item: {item.name}")

        if self.dry_run:
            logger.info(f"[DRY RUN] Would process: {item.name}")
            return True

        try:
            # Read the approval file to determine action
            content = item.read_text()

            # Extract action type from frontmatter
            lines = content.split('\n')
            action_type = None
            for line in lines:
                if line.startswith('action:'):
                    action_type = line.split(':')[1].strip()
                    break

            # Route to appropriate MCP handler
            if action_type == 'send_email':
                return self._handle_email_action(content)
            elif action_type == 'payment':
                return self._handle_payment_action(content)
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return False

        except Exception as e:
            logger.error(f"Error processing approved item: {e}")
            return False

    def _handle_email_action(self, content: str) -> bool:
        """Handle email sending action."""
        logger.info("Handling email action")
        # This would call the email MCP server
        return True

    def _handle_payment_action(self, content: str) -> bool:
        """Handle payment action."""
        logger.info("Handling payment action")
        # This would call the payment MCP server
        # NEVER auto-approve payments
        return True

    def notify_approval_needed(self, item: Path, details: dict = None):
        """Notify user that approval is needed via webhooks and logs."""
        logger.info(f"Sending approval notification for: {item.name}")

        details = details or {}
        notification_message = f"⚠️ **Approval Needed**\n\n"
        notification_message += f"**Item:** {item.name}\n"
        notification_message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        if details.get('priority'):
            notification_message += f"**Priority:** {details['priority']}\n"
        if details.get('category'):
            notification_message += f"**Category:** {details['category']}\n"

        notification_message += f"\n📁 Check: `vault/Pending_Approval/{item.name}`"

        # Try to send webhook notifications
        try:
            import requests

            # Load webhook config
            webhook_config_path = self.vault_path / 'secrets' / 'webhooks.json'
            if webhook_config_path.exists():
                config = json.loads(webhook_config_path.read_text())

                # Send to Slack
                slack_url = config.get('webhooks', {}).get('slack') or os.getenv('SLACK_WEBHOOK_URL')
                if slack_url:
                    try:
                        response = requests.post(
                            slack_url,
                            json={'text': notification_message},
                            timeout=5
                        )
                        if response.status_code == 200:
                            logger.info("Slack notification sent")
                        else:
                            logger.warning(f"Slack notification failed: {response.status_code}")
                    except Exception as e:
                        logger.error(f"Slack notification error: {e}")

                # Send to Discord
                discord_url = config.get('webhooks', {}).get('discord') or os.getenv('DISCORD_WEBHOOK_URL')
                if discord_url:
                    try:
                        response = requests.post(
                            discord_url,
                            json={'content': notification_message},
                            timeout=5
                        )
                        if response.status_code in [200, 204]:
                            logger.info("Discord notification sent")
                        else:
                            logger.warning(f"Discord notification failed: {response.status_code}")
                    except Exception as e:
                        logger.error(f"Discord notification error: {e}")

        except ImportError:
            logger.warning("requests library not installed - skipping webhook notifications")
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")

        # Always log to activity
        self.log_activity('approval_requested', {
            'item': item.name,
            'timestamp': datetime.now().isoformat(),
            'details': details
        })

    def move_to_done(self, item: Path):
        """Move item to Done folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = self.done / f"{item.stem}_{timestamp}{item.suffix}"
        item.rename(dest)
        logger.info(f"Moved to Done: {dest.name}")

        # Notify completion
        self._notify_completion(item)

    def move_to_rejected(self, item: Path):
        """Move item to Rejected folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = self.rejected / f"{item.stem}_{timestamp}{item.suffix}"
        item.rename(dest)
        logger.info(f"Moved to Rejected: {dest.name}")

        # Notify rejection
        self._notify_rejection(item)

    def _notify_completion(self, item: Path):
        """Notify that an item was completed."""
        try:
            import requests
            message = f"✅ **Task Completed**\n\n**Item:** {item.name}\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            slack_url = os.getenv('SLACK_WEBHOOK_URL')
            if slack_url:
                requests.post(slack_url, json={'text': message}, timeout=5)

            discord_url = os.getenv('DISCORD_WEBHOOK_URL')
            if discord_url:
                requests.post(discord_url, json={'content': message}, timeout=5)

        except Exception as e:
            logger.debug(f"Notification error: {e}")

    def _notify_rejection(self, item: Path):
        """Notify that an item was rejected."""
        try:
            import requests
            message = f"❌ **Task Rejected**\n\n**Item:** {item.name}\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            slack_url = os.getenv('SLACK_WEBHOOK_URL')
            if slack_url:
                requests.post(slack_url, json={'text': message}, timeout=5)

            discord_url = os.getenv('DISCORD_WEBHOOK_URL')
            if discord_url:
                requests.post(discord_url, json={'content': message}, timeout=5)

        except Exception as e:
            logger.debug(f"Notification error: {e}")

    def log_activity(self, activity_type: str, details: dict):
        """Log activity to daily log file."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': activity_type,
            'details': details
        }

        if log_file.exists():
            with open(log_file, 'r') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def generate_morning_briefing(self):
        """Generate Monday morning CEO briefing."""
        logger.info("Generating morning briefing...")

        # This would be handled by Claude
        prompt = """
        Generate a Monday Morning CEO Briefing by:
        1. Reading Business_Goals.md for targets
        2. Reading Logs/ for completed tasks this week
        3. Reading Accounting/ for transactions
        4. Writing a summary to Briefings/{date}_Monday_Briefing.md
        """

        self.trigger_claude(prompt)

    def run_ralph_loop(self, task_prompt: str, max_iterations: int = 10):
        """
        Run the Ralph Wiggum persistence loop.

        This keeps Claude running until a task is marked complete.
        """
        logger.info(f"Starting Ralph Wiggum loop: {task_prompt}")
        self.ralph_mode = True

        iteration = 0
        while iteration < max_iterations and self.running:
            iteration += 1
            logger.info(f"Ralph loop iteration {iteration}/{max_iterations}")

            # Check if task is done
            done_items = list(self.done.glob('*'))
            if done_items:
                logger.info("Task marked complete, exiting Ralph loop")
                break

            # Trigger Claude to continue working
            success = self.trigger_claude(task_prompt)

            if not success:
                logger.error("Claude failed, retrying...")
                time.sleep(5)

            # Small delay between iterations
            time.sleep(2)

        self.ralph_mode = False
        logger.info("Ralph Wiggum loop complete")

    def run(self):
        """Main orchestration loop."""
        logger.info(f"Starting Orchestrator (dry_run={self.dry_run})")

        while self.running:
            try:
                # Check Needs_Action
                needs_action = self.check_needs_action()
                if needs_action:
                    logger.info(f"Found {len(needs_action)} items in Needs_Action")
                    for item in needs_action:
                        # Create a Plan.md first
                        self.create_plan(item)

                        # Then trigger Claude to process
                        prompt = f"""Process the item in {item.name}.

The plan has been created in Plans/ folder.
1. Read the item in Needs_Action/{item.name}
2. Read Company_Handbook.md for rules
3. Determine required actions
4. If approval needed, create request in Pending_Approval/
5. When complete, move original to Done/ and update plan status to completed
"""
                        self.trigger_claude(prompt)
                        self.move_to_in_progress(item)

                # Check Approved folder
                approved = self.check_approved()
                if approved:
                    logger.info(f"Found {len(approved)} approved items to execute")
                    for item in approved:
                        if self.process_approved_item(item):
                            self.move_to_done(item)

                # Check Pending Approval
                pending = self.check_pending_approval()
                if pending:
                    logger.info(f"Found {len(pending)} items pending approval")

                # Log heartbeat
                self.log_activity('heartbeat', {'status': 'running'})

                # Sleep before next check
                time.sleep(30)

            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}")
                self.log_activity('error', {'error': str(e)})
                time.sleep(10)

        logger.info("Orchestrator stopped")

    def schedule_task(self, task: str, cron_expr: str):
        """Schedule a task using cron-like syntax."""
        # Simple scheduling - in production use proper cron
        logger.info(f"Scheduling task: {task} with schedule: {cron_expr}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Orchestrator with Multi-CLI Support')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Run in dry-run mode (no external actions)')
    parser.add_argument('--live', action='store_false', dest='dry_run',
                        help='Run in live mode (execute real actions)')

    # Multi-CLI options
    parser.add_argument('--primary-cli', choices=['claude', 'qwen', 'codex'],
                        default='claude', help='Primary CLI to use (default: claude)')
    parser.add_argument('--enable-fallback', action='store_true', default=True,
                        help='Enable automatic fallback between CLIs (default: enabled)')
    parser.add_argument('--force-cli', choices=['claude', 'qwen', 'codex'],
                        help='Force use of specific CLI (disables fallback)')

    # Testing and monitoring
    parser.add_argument('--test-clis', action='store_true',
                        help='Test all available CLIs and exit')
    parser.add_argument('--quota-status', action='store_true',
                        help='Show quota status and exit')
    parser.add_argument('--reset-quotas', action='store_true',
                        help='Reset quota tracking and exit')

    args = parser.parse_args()

    # Handle special commands
    if args.test_clis:
        if MULTI_CLI_AVAILABLE:
            manager = MultiCLIManager(args.vault)
            print("Testing all CLIs...")
            test_prompt = "Hello, please respond with 'CLI working'"

            print("\n🔍 Testing Claude...")
            success, result = manager.call_claude(test_prompt)
            print(f"Claude: {'✅' if success else '❌'} {result[:100]}")

            print("\n🔍 Testing Qwen...")
            success, result = manager.call_qwen(test_prompt)
            print(f"Qwen: {'✅' if success else '❌'} {result[:100]}")

            print("\n🔍 Testing Codex...")
            success, result = manager.call_codex(test_prompt)
            print(f"Codex: {'✅' if success else '❌'} {result[:100]}")

            print(f"\n📊 Status: {manager.get_status()}")
        else:
            print("❌ Multi-CLI system not available")
        return

    if args.quota_status:
        if MULTI_CLI_AVAILABLE:
            quota_manager = QuotaManager(args.vault)
            status = quota_manager.get_status_report()
            print("📊 Quota Status:")
            print(json.dumps(status, indent=2))
        else:
            print("❌ Multi-CLI system not available")
        return

    if args.reset_quotas:
        if MULTI_CLI_AVAILABLE:
            quota_manager = QuotaManager(args.vault)
            quota_manager.quota_data["claude"]["exhausted"] = False
            quota_manager.quota_data["codex"]["exhausted"] = False
            quota_manager.save_quota_status()
            print("✅ Quota status reset")
        else:
            print("❌ Multi-CLI system not available")
        return

    # Determine primary CLI
    primary_cli = args.force_cli if args.force_cli else args.primary_cli

    orchestrator = Orchestrator(
        vault_path=args.vault,
        dry_run=args.dry_run,
        primary_cli=primary_cli
    )

    # Disable fallback if force-cli is specified
    if args.force_cli and hasattr(orchestrator, 'multi_cli') and orchestrator.multi_cli:
        print(f"🔒 Forcing CLI: {args.force_cli} (fallback disabled)")
        # Override the process method to use only the forced CLI
        original_process = orchestrator.multi_cli.process_with_best_cli
        def forced_process(prompt, context=""):
            cli_used = args.force_cli
            success, result = orchestrator.multi_cli.call_cli(cli_used, prompt, context, "general")
            if success:
                return cli_used, result
            else:
                return "none", f"Forced CLI {cli_used} failed: {result}"
        orchestrator.multi_cli.process_with_best_cli = forced_process

    print(f"🚀 Starting Orchestrator with primary CLI: {primary_cli}")
    if MULTI_CLI_AVAILABLE and not args.force_cli:
        print("🔄 Multi-CLI fallback enabled")
    elif args.force_cli:
        print(f"🔒 Forced to use: {args.force_cli}")
    else:
        print("⚠️  Multi-CLI system not available, using original API system")

    orchestrator.run()


if __name__ == "__main__":
    main()
