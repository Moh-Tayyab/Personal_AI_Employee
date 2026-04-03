"""
Orchestrator - Main coordination script for the AI Employee

The orchestrator manages the coordination between watchers, Qwen Code,
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
    from agent_teams_manager import AgentTeamsManager
    MULTI_CLI_AVAILABLE = True
    MULTI_PROVIDER_AVAILABLE = True
    AGENT_TEAMS_AVAILABLE = True
except ImportError:
    MULTI_CLI_AVAILABLE = False
    MULTI_PROVIDER_AVAILABLE = False
    AGENT_TEAMS_AVAILABLE = False
    logging.warning("Multi-provider system not available - falling back to original API calls")

# Import Error Recovery Integration (Step 5)
try:
    from error_recovery_integration import (
        RecoveryContext,
        with_circuit_breaker,
        with_ralph_retry,
    )
    ERROR_RECOVERY_AVAILABLE = True
except ImportError:
    ERROR_RECOVERY_AVAILABLE = False
    RecoveryContext = None
    with_circuit_breaker = None
    with_ralph_retry = None
    logging.warning("Error recovery integration not available")

# Import Health Server (Step 6)
try:
    from health_server import HealthServer
    HEALTH_SERVER_AVAILABLE = True
except ImportError:
    HEALTH_SERVER_AVAILABLE = False
    HealthServer = None
    logging.warning("Health server not available")

# Import Config Validator (Step 7)
try:
    from config_validator import ConfigValidator
    CONFIG_VALIDATOR_AVAILABLE = True
except ImportError:
    CONFIG_VALIDATOR_AVAILABLE = False
    ConfigValidator = None
    logging.warning("Config validator not available")

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

    def __init__(self, vault_path: str, dry_run: bool = True, primary_cli: str = "qwen"):
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run
        self.running = True
        self.ralph_mode = False
        self.current_task = None
        self.primary_cli = primary_cli

        # Initialize Multi-Provider AI System (NEW - maintains Qwen Code functionality)
        if MULTI_PROVIDER_AVAILABLE:
            try:
                self.multi_provider_ai = MultiProviderAI(str(vault_path))
                logger.info("✅ Multi-Provider AI system initialized (with full Qwen Code functionality)")
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

        # Initialize Agent Teams Manager (NEW)
        if AGENT_TEAMS_AVAILABLE:
            try:
                self.agent_teams = AgentTeamsManager(self.vault_path)
                logger.info("✅ Agent Teams system initialized")
            except Exception as e:
                logger.warning(f"Agent Teams initialization failed: {e}")
                self.agent_teams = None
        else:
            self.agent_teams = None

        # Initialize Error Recovery Integration (Step 5)
        if ERROR_RECOVERY_AVAILABLE and RecoveryContext:
            try:
                self.recovery_ctx = RecoveryContext(self.vault_path)
                logger.info("✅ Error Recovery & Circuit Breakers initialized")
            except Exception as e:
                logger.warning(f"Error recovery initialization failed: {e}")
                self.recovery_ctx = None
        else:
            self.recovery_ctx = None

        # Initialize Health Server (Step 6)
        self.health_server = None
        self.health_state = None
        if HEALTH_SERVER_AVAILABLE and HealthServer:
            try:
                health_port = int(os.getenv("HEALTH_PORT", "8080"))
                health_host = os.getenv("HEALTH_HOST", "127.0.0.1")
                self.health_server = HealthServer(
                    vault_path=str(vault_path),
                    host=health_host,
                    port=health_port,
                )
                self.health_state = self.health_server.state
                logger.info(f"✅ Health server initialized on {health_host}:{health_port}")
            except Exception as e:
                logger.warning(f"Health server initialization failed: {e}")
                self.health_server = None
                self.health_state = None

        # Directories
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'
        self.in_progress = self.vault_path / 'In_Progress'

        # Ensure directories exist
        for d in [self.needs_action, self.plans, self.done,
                  self.pending_approval, self.approved, self.rejected,
                  self.logs, self.in_progress]:
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
        """Process item using AI with multi-provider system maintaining full Qwen Code functionality."""
        logger.info(f"Processing with AI: {prompt[:100]}...")

        if self.dry_run:
            logger.info("[DRY RUN] Would call AI API")
            logger.info(f"Prompt: {prompt}")
            return True

        # Check if we should create an agent team for this work
        # TEMPORARILY DISABLED - agent teams not spawning actual agents, just creating plans
        # if self.agent_teams and self._should_use_agent_team(prompt):
        #     return self._process_with_agent_team(prompt)

        # Use Multi-CLI manager (Qwen CLI) for direct processing (PREFERRED)
        if self.multi_cli:
            return self._process_with_multi_cli(prompt)
        # Fallback to Multi-Provider AI system
        elif self.multi_provider_ai:
            return self._process_with_multi_provider_ai(prompt)
        else:
            # Final fallback to original API system
            return self._process_with_original_apis(prompt)

    @with_circuit_breaker("qwen_api", max_retries=3) if with_circuit_breaker else lambda f: f
    @with_ralph_retry(max_iterations=10) if with_ralph_retry else lambda f: f
    def _process_with_multi_provider_ai(self, prompt: str) -> bool:
        """Process using the multi-provider AI system with full Qwen Code functionality."""
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
- ✅ Full Qwen Code functionality maintained
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

    def _should_use_agent_team(self, prompt: str) -> bool:
        """Determine if the current work should use an agent team."""
        if not self.agent_teams:
            return False

        # Get current work items
        needs_action_items = [f.name for f in self.check_needs_action()]

        # Use agent teams manager to determine if team is warranted
        return self.agent_teams.should_create_team(prompt, len(needs_action_items))

    def _process_with_agent_team(self, prompt: str) -> bool:
        """Process work using an agent team."""
        try:
            logger.info("🤖 Creating agent team for coordinated processing")

            # Get current work items for team composition analysis
            needs_action_items = [f.name for f in self.check_needs_action()]

            # Get team composition suggestion
            team_suggestion = self.agent_teams.suggest_team_composition(needs_action_items)

            # Create team prompt
            team_prompt = self.agent_teams.create_team_prompt(team_suggestion)

            logger.info(f"Suggested team size: {team_suggestion['recommended_size']} members")
            logger.info(f"Total tasks to distribute: {team_suggestion['total_tasks']}")

            # Log team creation
            self.agent_teams.log_team_activity("orchestrator-team", "Team Creation Initiated", {
                "Prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                "Suggested Team Size": team_suggestion['recommended_size'],
                "Total Tasks": team_suggestion['total_tasks'],
                "Task Distribution": str(team_suggestion['task_distribution'])
            })

            # Use multi-provider AI to create the team
            if self.multi_provider_ai:
                provider_used, response = self.multi_provider_ai.process_with_tools(
                    prompt=team_prompt,
                    task_type="team_coordination",
                    use_tools=True,
                    thinking=True
                )

                if provider_used != "none":
                    logger.info(f"✅ Agent team created via {provider_used}")

                    # Save team creation log
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    team_log_path = self.vault_path / 'Teams' / 'Active' / f'TEAM_CREATION_{timestamp}.md'

                    team_log_content = f"""---
type: agent_team_creation
created: {datetime.now().isoformat()}
provider: {provider_used}
status: active
---

# Agent Team Creation Log

## Original Request
{prompt}

## Team Composition Analysis
- **Recommended Size**: {team_suggestion['recommended_size']} members
- **Total Tasks**: {team_suggestion['total_tasks']}
- **Task Distribution**: {team_suggestion['task_distribution']}

## Team Creation Prompt
{team_prompt}

## AI Response
{response}

---

## Team Members
{chr(10).join([f"- **{member['role']}**: {member['description']} ({member['estimated_tasks']} tasks)" for member in team_suggestion['suggested_team']])}
"""

                    team_log_path.write_text(team_log_content)
                    logger.info(f"Team creation log saved: {team_log_path}")

                    return True
                else:
                    logger.warning("Team creation failed, falling back to single-agent processing")
                    return self._process_with_multi_provider_ai(prompt)
            else:
                logger.warning("Multi-provider AI not available for team creation")
                return False

        except Exception as e:
            logger.error(f"Error in agent team processing: {e}")
            logger.info("Falling back to single-agent processing")
            if self.multi_provider_ai:
                return self._process_with_multi_provider_ai(prompt)
            else:
                return False

    def monitor_agent_teams(self):
        """Monitor active agent teams and perform maintenance."""
        if not self.agent_teams:
            return

        try:
            # Get status of all active teams
            active_teams = self.agent_teams.get_active_teams()

            if active_teams:
                logger.info(f"Monitoring {len(active_teams)} active agent teams")

                for team in active_teams:
                    team_name = team['team_name']

                    # Log team status
                    if team['issues']:
                        logger.warning(f"Team {team_name} has issues: {', '.join(team['issues'])}")

                    # Check for completed teams
                    if (team['tasks']['completed'] > 0 and
                        team['tasks']['pending'] == 0 and
                        team['tasks']['in_progress'] == 0):
                        logger.info(f"Team {team_name} appears to have completed all tasks")

                # Create status report
                status_report = self.agent_teams.create_team_status_report()

                # Save status report to vault
                status_path = self.vault_path / 'Teams' / 'team_status_report.md'
                status_path.write_text(status_report)

                # Clean up completed teams
                self.agent_teams.cleanup_completed_teams()

            else:
                logger.debug("No active agent teams to monitor")

        except Exception as e:
            logger.error(f"Error monitoring agent teams: {e}")

    def get_system_status(self) -> dict:
        """Get comprehensive system status including agent teams."""
        status = {
            'timestamp': datetime.now().isoformat(),
            'vault_path': str(self.vault_path),
            'dry_run': self.dry_run,
            'ralph_mode': self.ralph_mode,
            'current_task': self.current_task,
            'needs_action_count': len(self.check_needs_action()),
            'pending_approval_count': len(self.check_pending_approval()),
            'approved_count': len(self.check_approved()),
            'multi_provider_available': self.multi_provider_ai is not None,
            'multi_cli_available': self.multi_cli is not None,
            'agent_teams_available': self.agent_teams is not None,
            'agent_teams': None
        }

        # Add agent teams status if available
        if self.agent_teams:
            try:
                active_teams = self.agent_teams.get_active_teams()
                status['agent_teams'] = {
                    'active_count': len(active_teams),
                    'teams': active_teams
                }
            except Exception as e:
                status['agent_teams'] = {'error': str(e)}

        return status

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
    def trigger_qwen(self, prompt: str) -> bool:
        """Backward compatibility wrapper for trigger_ai."""
        return self.trigger_ai(prompt)

    def _fallback_rule_based_processing(self, prompt: str) -> bool:
        """Fallback to rule-based processing when Qwen API unavailable."""
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
This was processed using rule-based classification because Qwen API was unavailable.
For intelligent processing, set QWEN_API_KEY or ANTHROPIC_API_KEY in your .env file.
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

    @with_circuit_breaker("filesystem", max_retries=2) if with_circuit_breaker else lambda f: f
    def process_approved_item(self, item: Path) -> bool:
        """Process an approved item using MCP servers.

        Routes to the appropriate MCP handler based on the action type
        extracted from the item's YAML frontmatter.
        """
        logger.info(f"Processing approved item: {item.name}")

        if self.dry_run:
            logger.info(f"[DRY RUN] Would process approved item: {item.name}")
            return True

        try:
            # Read the approval file to determine action
            content = item.read_text()

            # Extract action type from frontmatter
            action_type = self._extract_frontmatter_field(content, 'action')
            if not action_type:
                # Try to infer from content
                content_lower = content.lower()
                if 'email' in content_lower and ('send' in content_lower or 'reply' in content_lower):
                    action_type = 'send_email'
                elif 'linkedin' in content_lower:
                    action_type = 'linkedin_post'
                elif 'twitter' in content_lower or 'tweet' in content_lower:
                    action_type = 'twitter_post'
                elif 'facebook' in content_lower or 'instagram' in content_lower:
                    action_type = 'social_post'
                elif 'invoice' in content_lower or 'payment' in content_lower:
                    action_type = 'odoo_payment'
                else:
                    logger.warning(f"Could not determine action type for: {item.name}")
                    return False

            logger.info(f"Action type: {action_type}")

            # Route to appropriate MCP handler
            handlers = {
                'send_email': self._handle_email_action,
                'linkedin_post': self._handle_linkedin_action,
                'twitter_post': self._handle_twitter_action,
                'social_post': self._handle_social_action,
                'odoo_invoice': self._handle_odoo_invoice_action,
                'odoo_payment': self._handle_odoo_payment_action,
            }

            handler = handlers.get(action_type)
            if handler:
                return handler(content)
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return False

        except Exception as e:
            logger.error(f"Error processing approved item: {e}")
            return False

    def _extract_frontmatter_field(self, content: str, field: str) -> str:
        """Extract a field from YAML frontmatter."""
        import re
        match = re.search(rf'^{field}:\s*(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip().strip('"').strip("'")
        return ""

    def _call_mcp_server(self, server_name: str, tool_name: str, arguments: dict) -> dict:
        """Call an MCP server tool via subprocess using the MCP stdio protocol.

        This is a simplified invocation that runs the MCP server script directly
        and calls the specified tool function.
        """
        import importlib.util

        server_paths = {
            'email': 'mcp/email/server.py',
            'filesystem': 'mcp/filesystem/server.py',
            'approval': 'mcp/approval/server.py',
            'linkedin': 'mcp/linkedin/server.py',
            'twitter': 'mcp/twitter/server.py',
            'social': 'mcp/social/server.py',
            'odoo': 'mcp/odoo/server.py',
        }

        if server_name not in server_paths:
            return {"error": f"Unknown MCP server: {server_name}"}

        server_path = Path(__file__).parent / server_paths[server_name]
        if not server_path.exists():
            return {"error": f"MCP server file not found: {server_path}"}

        try:
            # Import the server module and call the tool function directly
            spec = importlib.util.spec_from_file_location(server_name, server_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get the tool function
            tool_func = getattr(module, tool_name, None)
            if not tool_func:
                return {"error": f"Tool {tool_name} not found in {server_name} server"}

            # Call the tool
            result = tool_func(**arguments)
            return result

        except Exception as e:
            return {"error": f"Failed to call MCP server {server_name}/{tool_name}: {e}"}

    def _handle_email_action(self, content: str) -> bool:
        """Handle email sending action via Email MCP server."""
        logger.info("Handling email action via Email MCP server")

        # Extract email fields from frontmatter
        to_addr = self._extract_frontmatter_field(content, 'to') or self._extract_frontmatter_field(content, 'recipient')
        subject = self._extract_frontmatter_field(content, 'subject')
        cc_addr = self._extract_frontmatter_field(content, 'cc')
        bcc_addr = self._extract_frontmatter_field(content, 'bcc')

        # Use body as remaining content after frontmatter
        import re
        fm_match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)', content, re.DOTALL)
        body = fm_match.group(1).strip() if fm_match else content

        if not to_addr:
            logger.error("No recipient found for email action")
            return False

        result = self._call_mcp_server('email', 'send_email', {
            'to': to_addr,
            'subject': subject or 'No Subject',
            'body': body,
            'cc': cc_addr or '',
            'bcc': bcc_addr or '',
        })

        if result.get('success'):
            logger.info(f"Email sent successfully to {to_addr}")
            self.log_activity('email_sent', {'to': to_addr, 'subject': subject, 'result': result})
            return True
        else:
            logger.error(f"Failed to send email: {result.get('error')}")
            self.log_activity('email_failed', {'to': to_addr, 'error': result.get('error')})
            return False

    def _handle_linkedin_action(self, content: str) -> bool:
        """Handle LinkedIn posting action via LinkedIn MCP server."""
        logger.info("Handling LinkedIn action via LinkedIn MCP server")

        # Extract fields from frontmatter
        post_content = self._extract_frontmatter_field(content, 'content')
        visibility = self._extract_frontmatter_field(content, 'visibility') or 'PUBLIC'
        image_url = self._extract_frontmatter_field(content, 'image_url')

        # Use body as post content if no explicit content field
        import re
        fm_match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)', content, re.DOTALL)
        if not post_content and fm_match:
            post_content = fm_match.group(1).strip()[:3000]  # LinkedIn limit

        if not post_content:
            logger.error("No content found for LinkedIn action")
            return False

        if image_url:
            result = self._call_mcp_server('linkedin', 'post_with_image', {
                'content': post_content,
                'image_url': image_url,
                'visibility': visibility,
            })
        else:
            result = self._call_mcp_server('linkedin', 'post_to_linkedin', {
                'content': post_content,
                'visibility': visibility,
            })

        if result.get('success'):
            logger.info(f"LinkedIn post successful (dry_run={result.get('dry_run', False)})")
            self.log_activity('linkedin_posted', {'result': result})
            return True
        else:
            logger.error(f"Failed to post on LinkedIn: {result.get('error')}")
            self.log_activity('linkedin_failed', {'error': result.get('error')})
            return False

    def _handle_twitter_action(self, content: str) -> bool:
        """Handle Twitter posting action via Twitter MCP server."""
        logger.info("Handling Twitter action via Twitter MCP server")

        post_content = self._extract_frontmatter_field(content, 'content')
        reply_to = self._extract_frontmatter_field(content, 'reply_to')

        import re
        fm_match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)', content, re.DOTALL)
        if not post_content and fm_match:
            post_content = fm_match.group(1).strip()[:280]  # Twitter limit

        if not post_content:
            logger.error("No content found for Twitter action")
            return False

        result = self._call_mcp_server('twitter', 'post_tweet', {
            'content': post_content,
            'reply_to': reply_to or None,
        })

        if result.get('success'):
            logger.info(f"Twitter post successful (dry_run={result.get('dry_run', False)})")
            self.log_activity('twitter_posted', {'result': result})
            return True
        else:
            logger.error(f"Failed to post on Twitter: {result.get('error')}")
            self.log_activity('twitter_failed', {'error': result.get('error')})
            return False

    def _handle_social_action(self, content: str) -> bool:
        """Handle Facebook/Instagram posting action via Social MCP server."""
        logger.info("Handling social action via Facebook/Instagram MCP server")

        post_content = self._extract_frontmatter_field(content, 'content')
        platform = self._extract_frontmatter_field(content, 'platform').lower()
        image_url = self._extract_frontmatter_field(content, 'image_url')

        import re
        fm_match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)', content, re.DOTALL)
        if not post_content and fm_match:
            post_content = fm_match.group(1).strip()

        if not post_content:
            logger.error("No content found for social action")
            return False

        if platform == 'instagram':
            if not image_url:
                logger.error("Image URL required for Instagram post")
                return False
            result = self._call_mcp_server('social', 'post_to_instagram', {
                'caption': post_content,
                'image_url': image_url,
            })
        else:
            result = self._call_mcp_server('social', 'post_to_facebook', {
                'content': post_content,
            })

        if result.get('success'):
            logger.info(f"Social post successful on {platform} (dry_run={result.get('dry_run', False)})")
            self.log_activity(f'{platform}_posted', {'result': result})
            return True
        else:
            logger.error(f"Failed to post on {platform}: {result.get('error')}")
            self.log_activity(f'{platform}_failed', {'error': result.get('error')})
            return False

    def _handle_odoo_invoice_action(self, content: str) -> bool:
        """Handle Odoo invoice creation/posting action via Odoo MCP server."""
        logger.info("Handling Odoo invoice action via Odoo MCP server")

        action = self._extract_frontmatter_field(content, 'action').replace('odoo_', '')
        partner_name = self._extract_frontmatter_field(content, 'partner_name')
        partner_email = self._extract_frontmatter_field(content, 'partner_email')
        amount = self._extract_frontmatter_field(content, 'amount')
        invoice_id = self._extract_frontmatter_field(content, 'invoice_id')

        if action == 'invoice' or action == 'create_invoice':
            if not partner_name or not partner_email:
                logger.error("Missing partner info for invoice")
                return False

            # Parse invoice lines from content
            import re
            lines = []
            for line_match in re.finditer(r'line:\s*(.+)', content):
                line_data = {}
                line_text = line_match.group(1)
                for field_match in re.finditer(r'(\w+)=([^,]+)', line_text):
                    key, val = field_match.groups()
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                    line_data[key] = val
                lines.append(line_data)

            if not lines:
                lines = [{'name': 'Service', 'quantity': 1, 'price_unit': float(amount) if amount else 0}]

            result = self._call_mcp_server('odoo', 'create_invoice', {
                'partner_name': partner_name,
                'partner_email': partner_email,
                'invoice_lines': lines,
            })

        elif action == 'post_invoice' and invoice_id:
            result = self._call_mcp_server('odoo', 'post_invoice', {
                'invoice_id': int(invoice_id),
            })
        else:
            logger.error(f"Unknown Odoo action: {action}")
            return False

        if result.get('success'):
            logger.info(f"Odoo invoice action successful (dry_run={result.get('dry_run', False)})")
            self.log_activity('odoo_invoice', {'result': result})
            return True
        else:
            logger.error(f"Failed Odoo invoice action: {result.get('error')}")
            self.log_activity('odoo_invoice_failed', {'error': result.get('error')})
            return False

    def _handle_odoo_payment_action(self, content: str) -> bool:
        """Handle Odoo payment action via Odoo MCP server."""
        logger.info("Handling Odoo payment action via Odoo MCP server")

        invoice_id = self._extract_frontmatter_field(content, 'invoice_id')
        amount = self._extract_frontmatter_field(content, 'amount')
        payment_ref = self._extract_frontmatter_field(content, 'payment_reference')

        if not invoice_id or not amount:
            logger.error("Missing invoice ID or amount for payment")
            return False

        result = self._call_mcp_server('odoo', 'create_payment', {
            'invoice_id': int(invoice_id),
            'amount': float(amount),
            'payment_reference': payment_ref or f'Payment for invoice {invoice_id}',
        })

        if result.get('success'):
            logger.info(f"Odoo payment successful (dry_run={result.get('dry_run', False)})")
            self.log_activity('odoo_payment', {'result': result})
            return True
        else:
            logger.error(f"Failed Odoo payment: {result.get('error')}")
            self.log_activity('odoo_payment_failed', {'error': result.get('error')})
            return False

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

    def _update_dashboard(self, needs_action: list, pending: list, approved: list):
        """Update the Dashboard.md with current system state."""
        dashboard_path = self.vault_path / 'Dashboard.md'

        done_count = len(list(self.done.glob('*.md')))
        in_progress_count = len(list(self.in_progress.glob('*.md')))
        total_processed = done_count + in_progress_count

        dashboard = f"""# AI Employee Dashboard

## System Status
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: {'🟢 Active' if self.running else '🔴 Stopped'}
- **Reasoning Engine**: Qwen Code
- **Mode**: {'DRY RUN' if self.dry_run else 'LIVE'}
- **Ralph Loop**: {'Active' if self.ralph_mode else 'Inactive'}

## Queue Status
| Folder | Count |
|--------|-------|
| Needs_Action | {len(needs_action)} |
| In_Progress | {in_progress_count} |
| Pending_Approval | {len(pending)} |
| Approved | {len(approved)} |
| Done | {done_count} |

## Recent Activity
- Last cycle: {datetime.now().strftime('%H:%M:%S')}
- Items processed this cycle: {len(needs_action)}

## Quick Actions
- [ ] Check Needs_Action folder
- [ ] Review Pending_Approval
- [ ] Execute Approved items

## Statistics
- **Total Processed**: {total_processed}
- **Errors**: 0

---
*Generated by AI Employee v0.1 — Auto-updated every 30s*
"""

        dashboard_path.write_text(dashboard)
        logger.debug("Dashboard updated")

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

        # This would be handled by Qwen
        prompt = """
        Generate a Monday Morning CEO Briefing by:
        1. Reading Business_Goals.md for targets
        2. Reading Logs/ for completed tasks this week
        3. Reading Accounting/ for transactions
        4. Writing a summary to Briefings/{date}_Monday_Briefing.md
        """

        self.trigger_qwen(prompt)

    def run_ralph_loop(self, task_prompt: str, max_iterations: int = 10):
        """
        Run the Ralph Wiggum persistence loop — EMBEDDED into orchestrator.

        This keeps Qwen working autonomously until a task is marked complete,
        with circuit breaker protection and exponential backoff retry.
        """
        logger.info("=" * 60)
        logger.info("🔄 Starting Ralph Wiggum Loop (Embedded)")
        logger.info(f"Prompt: {task_prompt[:100]}...")
        logger.info(f"Max iterations: {max_iterations}")
        logger.info("=" * 60)

        # Activate Ralph mode in recovery context
        if self.recovery_ctx:
            self.recovery_ctx.ralph_active = True
            self.recovery_ctx.ralph_iterations = 0
            self.recovery_ctx.ralph_max_iterations = max_iterations

        self.ralph_mode = True
        start_time = datetime.now()
        last_done_count = len(list(self.done.glob("*.md")))
        iteration = 0

        while iteration < max_iterations and self.running:
            iteration += 1
            if self.recovery_ctx:
                self.recovery_ctx.ralph_iterations = iteration

            logger.info(f"🔄 Ralph iteration {iteration}/{max_iterations}")

            # Check completion via file movement
            current_done_count = len(list(self.done.glob("*.md")))
            if current_done_count > last_done_count:
                logger.info(f"✅ Task complete — {current_done_count - last_done_count} new files in Done/")
                break

            # Check if Needs_Action is empty
            remaining = len(list(self.needs_action.glob("*.md")))
            if remaining == 0:
                logger.info("✅ Needs_Action folder empty — task complete")
                break

            # Trigger AI processing (with circuit breaker + retry from decorator)
            success = self.trigger_ai(task_prompt)

            if not success:
                logger.warning(f"⚠️ Ralph iteration {iteration} failed — will retry")
                # Exponential backoff: 2s, 4s, 8s, ... up to 30s
                delay = min(2 * (2 ** (iteration - 1)), 30)
                logger.info(f"⏳ Backing off for {delay}s before retry")
                time.sleep(delay)
            else:
                # Brief pause between successful iterations
                time.sleep(2)

            last_done_count = current_done_count

        # Deactivate Ralph mode
        self.ralph_mode = False
        if self.recovery_ctx:
            self.recovery_ctx.ralph_active = False

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("=" * 60)
        logger.info(f"✅ Ralph Wiggum Loop complete: {iteration} iterations, {elapsed:.1f}s")
        logger.info("=" * 60)

        # Log summary
        if self.recovery_ctx:
            self.recovery_ctx.log_error("ralph_loop_summary", {
                "iterations": iteration,
                "max_iterations": max_iterations,
                "elapsed_seconds": round(elapsed, 1),
                "completed": iteration < max_iterations,
                "done_count": current_done_count,
            })

    def run(self):
        """Main orchestration loop."""
        logger.info(f"Starting Orchestrator (dry_run={self.dry_run})")

        # Start health server
        if self.health_server:
            self.health_server.start()
            if self.health_state:
                self.health_state.set_running(True)

        # Track last team monitoring time
        last_team_monitor = datetime.now()
        team_monitor_interval = timedelta(minutes=5)  # Monitor teams every 5 minutes

        while self.running:
            try:
                # Monitor agent teams periodically
                if (self.agent_teams and
                    datetime.now() - last_team_monitor > team_monitor_interval):
                    self.monitor_agent_teams()
                    last_team_monitor = datetime.now()

                # Check Needs_Action
                needs_action = self.check_needs_action()
                if needs_action:
                    logger.info(f"Found {len(needs_action)} items in Needs_Action")

                    # Determine if we should use agent teams for this batch
                    if len(needs_action) > 1:
                        # Create a summary prompt for team decision
                        items_summary = "\n".join([f"- {item.name}" for item in needs_action])
                        batch_prompt = f"""Process {len(needs_action)} items requiring attention:

{items_summary}

Items include various types of work that may benefit from parallel processing by specialized teammates."""

                        # Check if this warrants a team approach (DISABLED - teams not spawning agents)
                        if False and self._should_use_agent_team(batch_prompt):
                            logger.info("🤖 Creating agent team for batch processing")
                            success = self._process_with_agent_team(batch_prompt)
                            if success:
                                # Team created successfully, let them handle the work
                                logger.info("Agent team created, monitoring progress...")
                                # Move items to a processing state or let team claim them
                                time.sleep(30)  # Give team time to start working
                                continue
                            else:
                                logger.warning("Team creation failed, falling back to single-agent processing")

                    # Process items individually if no team was created
                    for item in needs_action:
                        # Step 1: Create a Plan.md
                        plan_path = self.create_plan(item)

                        # Step 2: Read item content for AI prompt
                        item_content = item.read_text()

                        # Step 3: Trigger AI to analyze and create action plan
                        prompt = f"""You are a Personal AI Employee. Process this item:

## Item: {item.name}
{item_content}

## Instructions
1. Analyze the item content
2. Read Company_Handbook.md for rules and boundaries
3. Read Business_Goals.md for context
4. Determine what actions are needed
5. If the item requires external action (sending email, posting, payment):
   - Create a detailed action plan and save it in Pending_Approval/ with action type in frontmatter
   - DO NOT execute external actions without approval
6. If the item is informational (read, summarize, categorize):
   - Create a summary in Plans/
   - Move the original item to Done/
7. Update the plan status as you work

Respond with your analysis and planned actions.
"""
                        success = self.trigger_ai(prompt)

                        if success:
                            # Move to In_Progress to indicate AI is working on it
                            self.move_to_in_progress(item)
                            logger.info(f"Item {item.name} moved to In_Progress")
                        else:
                            logger.warning(f"Failed to process item {item.name}")

                # Check Approved folder — execute approved actions
                approved = self.check_approved()
                if approved:
                    logger.info(f"Found {len(approved)} approved items to execute")
                    for item in approved:
                        logger.info(f"Executing approved item: {item.name}")
                        success = self.process_approved_item(item)
                        if success:
                            self.move_to_done(item)
                            logger.info(f"✅ Approved item {item.name} executed and moved to Done")
                        else:
                            logger.error(f"❌ Failed to execute approved item: {item.name}")
                            # Move to In_Progress for manual review
                            self.move_to_in_progress(item)

                # Check Pending Approval
                pending = self.check_pending_approval()
                if pending:
                    logger.info(f"Found {len(pending)} items pending approval")

                # Update Dashboard
                self._update_dashboard(needs_action, pending, approved)

                # Check quarantined items and report
                if self.recovery_ctx and self.recovery_ctx.quarantine_dir.exists():
                    quarantined = list(self.recovery_ctx.quarantine_dir.glob("*.md"))
                    if quarantined:
                        logger.warning(f"🔒 {len(quarantined)} items in quarantine (review required)")

                # Log heartbeat with recovery context
                heartbeat_data = {
                    "status": "running",
                    "ralph_mode": self.ralph_mode,
                }
                if self.recovery_ctx:
                    heartbeat_data["circuit_breakers"] = {
                        name: cb.state
                        for name, cb in self.recovery_ctx.breakers.items()
                    }
                    heartbeat_data["ralph_iterations"] = self.recovery_ctx.ralph_iterations
                self.log_activity("heartbeat", heartbeat_data)

                # Update health server state
                if self.health_state:
                    self.health_state.update_heartbeat()
                    self.health_state.ralph_mode_active = self.ralph_mode
                    self.health_state.needs_action_count = len(needs_action)
                    self.health_state.pending_approval_count = len(pending) if pending else 0
                    self.health_state.approved_count = len(approved) if approved else 0
                    self.health_state.done_count = len(list(self.done.glob("*.md")))

                    if self.recovery_ctx:
                        self.health_state.circuit_breakers = {
                            name: cb.state
                            for name, cb in self.recovery_ctx.breakers.items()
                        }
                        self.health_state.ralph_iterations = self.recovery_ctx.ralph_iterations

                # Sleep before next check
                time.sleep(30)

            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}")

                # Update health state with error
                if self.health_state:
                    self.health_state.set_error(str(e))

                # Use error recovery to categorize and handle
                if self.recovery_ctx:
                    from error_recovery_integration import _categorize_error, ErrorCategory
                    category = _categorize_error(e)

                    self.recovery_ctx.log_error("orchestration_error", {
                        "category": category.value,
                        "error": str(e),
                    })

                    # System errors: log and continue
                    if category == ErrorCategory.SYSTEM:
                        logger.critical("💥 System error — logging and continuing")
                    # Auth errors: log and alert
                    elif category == ErrorCategory.AUTHENTICATION:
                        logger.error("🔐 Authentication error — check credentials")
                    # Transient: retry after delay
                    elif category == ErrorCategory.TRANSIENT:
                        logger.info("⏳ Transient error — will retry on next loop")
                        # Clear error after transient — will recover
                        if self.health_state:
                            self.health_state.clear_error()

                self.log_activity("error", {"error": str(e)})
                time.sleep(10)

        logger.info("Orchestrator stopped")

        # Stop health server
        if self.health_server:
            self.health_server.stop()
            if self.health_state:
                self.health_state.set_running(False)

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
                        default='qwen', help='Primary CLI to use (default: qwen)')
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

    # Ralph Wiggum Loop (Step 5)
    parser.add_argument('--ralph-mode', action='store_true',
                        help='Enable Ralph Wiggum persistence loop')
    parser.add_argument('--ralph-max-iterations', type=int, default=10,
                        help='Maximum Ralph loop iterations (default: 10)')
    parser.add_argument('--ralph-prompt', type=str, default=None,
                        help='Prompt for Ralph loop (default: process all items)')

    # Error Recovery Status
    parser.add_argument('--recovery-status', action='store_true',
                        help='Show error recovery and circuit breaker status and exit')

    # Health Check (Step 6)
    parser.add_argument('--health-port', type=int, default=8080,
                        help='Health server port (default: 8080)')
    parser.add_argument('--health-check', action='store_true',
                        help='Query health endpoint and exit (for monitoring scripts)')
    parser.add_argument('--health-url', type=str, default=None,
                        help='Full health URL to check (default: http://127.0.0.1:8080/health)')

    # Configuration Validation (Step 7)
    parser.add_argument('--validate-config', action='store_true',
                        help='Run startup configuration validation and exit')
    parser.add_argument('--validate-json', action='store_true',
                        help='Output validation report as JSON')
    parser.add_argument('--no-network-checks', action='store_true',
                        help='Skip network connectivity tests during validation')

    args = parser.parse_args()

    # Handle special commands
    if args.test_clis:
        if MULTI_CLI_AVAILABLE:
            manager = MultiCLIManager(args.vault)
            print("Testing all CLIs...")
            test_prompt = "Hello, please respond with 'CLI working'"

            print("\n🔍 Testing Qwen (Primary)...")
            success, result = manager.call_qwen(test_prompt)
            print(f"Qwen: {'✅' if success else '❌'} {result[:100]}")

            print("\n🔍 Testing Claude (Fallback)...")
            success, result = manager.call_claude(test_prompt)
            print(f"Claude: {'✅' if success else '❌'} {result[:100]}")

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
            quota_manager.quota_data["qwen"]["exhausted"] = False
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

    # Handle --recovery-status
    if args.recovery_status:
        if orchestrator.recovery_ctx:
            import json
            status = orchestrator.recovery_ctx.get_status_report()
            print(json.dumps(status, indent=2))
        else:
            print("Error recovery not available")
        return

    # Handle --ralph-mode
    if args.ralph_mode:
        prompt = args.ralph_prompt or "Process all items in Needs_Action folder. Move completed items to Done/."
        print(f"🔄 Starting Ralph Wiggum Loop (max {args.ralph_max_iterations} iterations)")
        orchestrator.run_ralph_loop(prompt, max_iterations=args.ralph_max_iterations)
        return  # Exit after Ralph loop completes

    # Handle --health-check (query endpoint and exit)
    if args.health_check:
        import urllib.request
        url = args.health_url or f"http://127.0.0.1:{args.health_port}/health/status"
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(json.dumps(data, indent=2))
                status_code = resp.status
                if status_code == 200:
                    return 0
                else:
                    return 1
        except Exception as e:
            print(json.dumps({"error": str(e), "status": "unreachable"}))
            return 2

    # Handle --validate-config (run pre-flight checks and exit)
    if args.validate_config:
        if CONFIG_VALIDATOR_AVAILABLE and ConfigValidator:
            validator = ConfigValidator(args.vault)
            run_network = not args.no_network_checks
            report = validator.validate_all(run_network_checks=run_network)

            if args.validate_json:
                print(validator.print_json_report())
            else:
                validator.print_summary()

            # Exit with appropriate code
            if report.fatal_errors:
                return 1
            return 0
        else:
            print("Config validator not available")
            return 2

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
