#!/usr/bin/env python3
"""
Agent Teams Demo Script - Personal AI Employee

This script demonstrates agent teams capabilities by creating sample scenarios
and showing how multiple Claude instances coordinate to handle complex workflows.
"""

import argparse
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AgentTeamsDemo")

class AgentTeamsDemo:
    """Demonstrates agent teams functionality."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.teams_dir = Path.home() / ".claude" / "teams"

        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)

    def create_sample_work_items(self, scenario: str):
        """Create sample work items for demonstration."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if scenario == "business-ops":
            items = [
                {
                    "filename": f"EMAIL_{timestamp}_001_partnership_inquiry.md",
                    "content": """---
type: email
from: sarah@innovateai.com
subject: Partnership Opportunity - AI Integration
priority: high
received: 2026-03-12T10:30:00Z
---

# Partnership Inquiry from InnovateAI

Hi there,

I'm Sarah from InnovateAI, and we're interested in exploring a partnership opportunity with your Personal AI Employee system. We've developed some cutting-edge AI models that could complement your existing infrastructure.

Would you be available for a call this week to discuss potential collaboration? We're particularly interested in:

1. API integration possibilities
2. Revenue sharing models
3. Joint go-to-market strategies

Looking forward to hearing from you!

Best regards,
Sarah Chen
Business Development Director
InnovateAI
sarah@innovateai.com
"""
                },
                {
                    "filename": f"SOCIAL_{timestamp}_002_linkedin_post.md",
                    "content": """---
type: social_media
platform: linkedin
priority: medium
due_date: 2026-03-12T16:00:00Z
---

# LinkedIn Post Request

Create a LinkedIn post about our new agent teams feature. Key points to highlight:

- Multiple Claude instances working together
- Coordinated workflows for complex tasks
- Improved efficiency for business operations
- Real-world use cases and benefits

Target audience: Business professionals, AI enthusiasts, productivity-focused individuals

Tone: Professional but engaging, include relevant hashtags

Suggested length: 150-200 words
"""
                },
                {
                    "filename": f"INVOICE_{timestamp}_003_monthly_expenses.md",
                    "content": """---
type: accounting
category: expense_processing
priority: medium
due_date: 2026-03-15T17:00:00Z
---

# Monthly Expense Processing

Process the following expenses for March 2026:

## Cloud Services
- AWS: $245.67 (Infrastructure)
- Google Cloud: $89.23 (AI APIs)
- Anthropic API: $156.78 (Claude usage)

## Software Subscriptions
- GitHub Pro: $21.00
- Slack Business: $45.00
- Notion Team: $32.00

## Marketing
- LinkedIn Ads: $300.00
- Content creation tools: $67.89

Total: $957.57

Please categorize, validate, and update the accounting system.
"""
                },
                {
                    "filename": f"RESEARCH_{timestamp}_004_competitor_analysis.md",
                    "content": """---
type: research
category: market_intelligence
priority: medium
deadline: 2026-03-14T12:00:00Z
---

# Competitor Analysis Request

Research and analyze the following AI automation competitors:

## Primary Competitors
1. **Zapier AI** - workflow automation platform
2. **Microsoft Power Automate** - business process automation
3. **UiPath** - robotic process automation
4. **Automation Anywhere** - intelligent automation

## Research Areas
- Feature comparison with our Personal AI Employee
- Pricing models and market positioning
- Customer reviews and satisfaction scores
- Recent product updates and roadmap
- Market share and growth trends

## Deliverables
- Competitive analysis report
- SWOT analysis for each competitor
- Recommendations for differentiation
- Pricing strategy insights

Format: Markdown report with executive summary
"""
                }
            ]

        elif scenario == "development":
            items = [
                {
                    "filename": f"BUG_{timestamp}_001_email_auth_issue.md",
                    "content": """---
type: bug_report
severity: high
component: email_mcp_server
reported_by: user_testing
priority: urgent
---

# Email Authentication Bug

## Problem Description
Users are experiencing authentication failures when trying to send emails through the Gmail MCP server. The error occurs intermittently, affecting approximately 30% of email send attempts.

## Error Details
```
Error: Authentication failed - invalid_grant
Token refresh failed with status 400
Gmail API returned: Token has been expired or revoked
```

## Steps to Reproduce
1. Attempt to send email via MCP server
2. Authentication token refresh is triggered
3. Refresh fails with invalid_grant error
4. Email send operation fails

## Impact
- Email functionality unreliable
- User workflow disrupted
- Potential data loss for unsent emails

## Environment
- Python 3.11
- Gmail API v1
- OAuth 2.0 authentication
- MCP server version 1.2.3
"""
                },
                {
                    "filename": f"FEATURE_{timestamp}_002_team_dashboard.md",
                    "content": """---
type: feature_request
priority: medium
component: web_dashboard
requested_by: product_team
---

# Agent Teams Dashboard Feature

## Feature Description
Create a web dashboard to monitor and manage agent teams in real-time.

## Requirements

### Core Features
- List all active teams with status
- Show team member assignments and progress
- Display task distribution and completion rates
- Real-time updates via WebSocket connection

### Team Management
- Create new teams from templates
- Assign tasks to specific team members
- Monitor team health and performance
- Shutdown teams when work is complete

### Visualization
- Team activity timeline
- Task completion charts
- Performance metrics dashboard
- Resource utilization graphs

## Technical Specifications
- React frontend with TypeScript
- WebSocket for real-time updates
- REST API for team management
- Integration with existing vault structure

## Acceptance Criteria
- Dashboard loads in under 2 seconds
- Real-time updates with <1 second latency
- Mobile-responsive design
- Accessible UI following WCAG guidelines
"""
                },
                {
                    "filename": f"DEPLOY_{timestamp}_003_staging_update.md",
                    "content": """---
type: deployment
environment: staging
priority: medium
component: mcp_servers
---

# Staging Environment Update

## Deployment Requirements
Update staging environment with latest MCP server changes and agent teams functionality.

## Components to Deploy
1. **Email MCP Server v1.3.0**
   - Fixed authentication token refresh
   - Added retry logic for failed sends
   - Improved error handling

2. **Social Media MCP Server v1.1.0**
   - LinkedIn API integration
   - Twitter/X posting capabilities
   - Content scheduling features

3. **Agent Teams Manager v1.0.0**
   - Team lifecycle management
   - Task coordination system
   - Quality monitoring hooks

## Deployment Steps
1. Backup current staging environment
2. Deploy new MCP server versions
3. Update configuration files
4. Run integration tests
5. Verify agent teams functionality
6. Update monitoring dashboards

## Rollback Plan
- Keep previous version containers available
- Database migration rollback scripts ready
- Configuration backup restoration procedure

## Testing Checklist
- [ ] Email sending functionality
- [ ] Social media posting
- [ ] Agent team creation
- [ ] Task coordination
- [ ] Monitoring and logging
"""
                }
            ]

        elif scenario == "content":
            items = [
                {
                    "filename": f"BLOG_{timestamp}_001_ai_automation_guide.md",
                    "content": """---
type: content_creation
category: blog_post
priority: high
target_audience: business_professionals
seo_keywords: ["AI automation", "business efficiency", "digital transformation"]
due_date: 2026-03-15T12:00:00Z
---

# Blog Post: The Complete Guide to AI Automation for Business

## Content Brief
Write a comprehensive guide about AI automation for business professionals who are new to the concept.

## Target Audience
- Small to medium business owners
- Operations managers
- Technology decision makers
- Entrepreneurs exploring AI solutions

## Key Topics to Cover
1. **Introduction to AI Automation**
   - What is AI automation?
   - Benefits for businesses
   - Common misconceptions

2. **Use Cases and Applications**
   - Email management and responses
   - Social media scheduling
   - Data processing and analysis
   - Customer service automation

3. **Implementation Strategy**
   - Assessing business needs
   - Choosing the right tools
   - Change management
   - Measuring ROI

4. **Best Practices**
   - Starting small and scaling
   - Human oversight and quality control
   - Data security considerations
   - Continuous improvement

## Content Requirements
- Length: 2500-3000 words
- Include practical examples
- Add relevant statistics and data
- SEO optimized for target keywords
- Include call-to-action for our services
- Professional but accessible tone
"""
                },
                {
                    "filename": f"SOCIAL_{timestamp}_002_campaign_strategy.md",
                    "content": """---
type: social_media_campaign
duration: 30_days
platforms: ["linkedin", "twitter", "instagram"]
priority: medium
---

# Q2 Social Media Campaign Strategy

## Campaign Overview
Develop a 30-day social media campaign to promote our Personal AI Employee system and agent teams feature.

## Campaign Objectives
- Increase brand awareness by 25%
- Generate 500 new leads
- Drive 1000+ website visits
- Establish thought leadership in AI automation

## Content Themes
1. **Week 1: Problem Awareness**
   - Highlight common business inefficiencies
   - Share statistics about time wasted on repetitive tasks
   - Customer pain point stories

2. **Week 2: Solution Introduction**
   - Introduce Personal AI Employee concept
   - Demonstrate key features and benefits
   - Success stories and case studies

3. **Week 3: Deep Dive Features**
   - Agent teams coordination
   - MCP server integrations
   - Automation workflows

4. **Week 4: Call to Action**
   - Free trial offers
   - Demo scheduling
   - Community building

## Content Calendar
- LinkedIn: 5 posts per week (professional content)
- Twitter: 10 posts per week (quick tips, updates)
- Instagram: 3 posts per week (visual content, behind-scenes)

## Success Metrics
- Engagement rate > 5%
- Click-through rate > 2%
- Lead conversion rate > 3%
- Brand mention increase > 20%
"""
                }
            ]

        else:
            logger.error(f"Unknown scenario: {scenario}")
            return

        # Create the sample files
        created_files = []
        for item in items:
            file_path = self.needs_action / item["filename"]
            file_path.write_text(item["content"])
            created_files.append(file_path)
            logger.info(f"Created sample item: {item['filename']}")

        return created_files

    def run_demo(self, scenario: str, interactive: bool = False):
        """Run a complete agent teams demonstration."""
        logger.info(f"🚀 Starting Agent Teams Demo: {scenario}")

        # Step 1: Create sample work items
        logger.info("📝 Creating sample work items...")
        created_files = self.create_sample_work_items(scenario)

        if interactive:
            input("Press Enter to continue to team creation...")
        else:
            time.sleep(2)

        # Step 2: Show team suggestion
        logger.info("🤖 Analyzing work items for team composition...")

        # This would normally be done by the orchestrator
        if scenario == "business-ops":
            suggested_prompt = """Create a business operations team with 4 specialists:
- Email specialist: Handle partnership inquiry and customer communications
- Social media manager: Create LinkedIn post and manage engagement
- Accounting specialist: Process monthly expenses and update financial records
- Research analyst: Conduct competitor analysis and market intelligence

Each teammate should work independently while coordinating through shared tasks."""

        elif scenario == "development":
            suggested_prompt = """Create a development team to handle the bug fix and feature development:
- Backend developer: Fix email authentication bug and investigate root cause
- Frontend developer: Build agent teams dashboard with real-time monitoring
- DevOps engineer: Deploy updates to staging and manage infrastructure

Require plan approval for production deployments."""

        elif scenario == "content":
            suggested_prompt = """Form a content creation team for the marketing campaign:
- Content writer: Create comprehensive AI automation blog post
- Social media strategist: Develop Q2 campaign strategy and content calendar
- Brand manager: Ensure all content aligns with brand voice and messaging
- SEO specialist: Optimize content for search engines and target keywords

All content must be approved before publication."""

        logger.info(f"💡 Suggested team prompt:\n{suggested_prompt}")

        if interactive:
            create_team = input("Create this team? (y/n): ").lower().startswith('y')
            if not create_team:
                logger.info("Demo cancelled by user")
                return
        else:
            time.sleep(3)

        # Step 3: Simulate team creation (in real scenario, this would call Claude)
        logger.info("🏗️  Creating agent team...")

        # Create a mock team status file
        team_name = f"demo-{scenario}-{datetime.now().strftime('%H%M%S')}"
        demo_status_path = self.vault_path / "Teams" / "Active" / f"{team_name}_demo.md"
        demo_status_path.parent.mkdir(parents=True, exist_ok=True)

        demo_status = f"""# Agent Team Demo: {scenario.title()}

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** Demo Mode
**Items:** {len(created_files)} work items created

## Team Composition
{suggested_prompt}

## Sample Work Items Created
{chr(10).join([f"- {f.name}" for f in created_files])}

## Next Steps
1. Start Claude Code with agent teams enabled
2. Use the suggested team prompt above
3. Monitor team coordination in real-time
4. Observe parallel processing of work items

## Demo Commands
```bash
# Check team status
./scripts/manage_teams.sh list

# Monitor team tasks
./scripts/manage_teams.sh tasks {team_name}

# View team logs
cat vault/Teams/Logs/{team_name}_*.md
```
"""

        demo_status_path.write_text(demo_status)
        logger.info(f"📊 Demo status saved: {demo_status_path}")

        # Step 4: Show monitoring commands
        logger.info("📈 Team monitoring commands:")
        print(f"""
🔍 Monitor your agent team:
   ./scripts/manage_teams.sh list
   ./scripts/manage_teams.sh tasks {team_name}

📝 Check work items:
   ls -la vault/Needs_Action/

📊 View team dashboard:
   cat vault/Teams/Active/{team_name}_demo.md

🚀 Start the actual team:
   claude --vault ./vault
   # Then use the suggested prompt above
""")

        logger.info("✅ Agent Teams Demo completed!")
        logger.info(f"🎯 Next: Start Claude Code and create the {scenario} team")

    def cleanup_demo(self):
        """Clean up demo files."""
        logger.info("🧹 Cleaning up demo files...")

        # Remove demo work items
        demo_files = list(self.needs_action.glob("*_demo_*")) + \
                    list(self.needs_action.glob("EMAIL_*")) + \
                    list(self.needs_action.glob("SOCIAL_*")) + \
                    list(self.needs_action.glob("INVOICE_*")) + \
                    list(self.needs_action.glob("RESEARCH_*")) + \
                    list(self.needs_action.glob("BUG_*")) + \
                    list(self.needs_action.glob("FEATURE_*")) + \
                    list(self.needs_action.glob("DEPLOY_*")) + \
                    list(self.needs_action.glob("BLOG_*"))

        for file in demo_files:
            file.unlink()
            logger.info(f"Removed: {file.name}")

        # Remove demo team status files
        teams_active = self.vault_path / "Teams" / "Active"
        if teams_active.exists():
            demo_team_files = list(teams_active.glob("demo-*"))
            for file in demo_team_files:
                file.unlink()
                logger.info(f"Removed: {file.name}")

        logger.info("✅ Demo cleanup completed")

def main():
    parser = argparse.ArgumentParser(description='Agent Teams Demo for Personal AI Employee')
    parser.add_argument('--vault', default='./vault', help='Path to vault directory')
    parser.add_argument('--scenario', choices=['business-ops', 'development', 'content'],
                       default='business-ops', help='Demo scenario to run')
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode with prompts')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up demo files')

    args = parser.parse_args()

    demo = AgentTeamsDemo(args.vault)

    if args.cleanup:
        demo.cleanup_demo()
    else:
        demo.run_demo(args.scenario, args.interactive)

if __name__ == "__main__":
    main()