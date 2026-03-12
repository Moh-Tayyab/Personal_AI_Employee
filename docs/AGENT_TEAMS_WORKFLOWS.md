# Agent Teams Workflow Examples

## Example 1: Daily Business Operations Team

### Scenario
Process morning business activities across multiple domains simultaneously.

### Team Setup
```bash
# Start Claude Code and create the team
Create a business operations team with 4 specialists:
- Email processor: Handle urgent emails, partnership inquiries, and customer communications using email MCP server
- Social media manager: Create and schedule posts, respond to mentions, track engagement using social MCP servers
- Accounting specialist: Process invoices, update expenses, track revenue using Odoo MCP server
- Research analyst: Gather market intelligence, competitor analysis, and business insights

Each teammate should work independently while coordinating through shared tasks.
```

### Expected Workflow
1. **Team Lead** creates shared task list with morning priorities
2. **Email Processor** claims email-related tasks, processes inbox
3. **Social Media Manager** claims content tasks, creates posts
4. **Accounting Specialist** claims financial tasks, updates records
5. **Research Analyst** claims research tasks, gathers intelligence
6. All teammates update task status and communicate findings
7. **Team Lead** synthesizes results and creates morning briefing

### Sample Tasks
- Process 25 new emails from overnight
- Create LinkedIn post about new AI integration
- Update Q1 expense tracking spreadsheet
- Research competitor pricing for new service
- Respond to customer support tickets
- Schedule social media content for the week

---

## Example 2: Development Team for Bug Fix

### Scenario
Critical bug reported in email MCP server - coordinate fix across multiple areas.

### Team Setup
```bash
Create a development team to fix the email authentication bug:
- Backend developer: Investigate and fix the email MCP server authentication issue
- DevOps engineer: Check deployment, logs, and infrastructure for related issues
- QA tester: Create test cases and verify the fix works properly

Require plan approval for any production changes.
```

### Expected Workflow
1. **Backend Developer** investigates the authentication bug
2. **DevOps Engineer** checks logs and infrastructure
3. **QA Tester** reproduces the bug and creates test cases
4. Team discusses findings and develops fix strategy
5. **Backend Developer** implements fix with plan approval
6. **QA Tester** validates fix against test cases
7. **DevOps Engineer** deploys fix to production
8. All teammates verify resolution

### Sample Tasks
- Analyze email MCP server logs for authentication errors
- Review OAuth token refresh mechanism
- Check Gmail API quota and rate limits
- Create automated test for authentication flow
- Implement token refresh retry logic
- Deploy fix to staging environment
- Validate fix in production

---

## Example 3: Content Creation Team

### Scenario
Create comprehensive content package for new AI service launch.

### Team Setup
```bash
Form a content creation team for the AI service launch:
- Content writer: Create blog posts, documentation, and marketing copy
- Social media strategist: Develop social media campaign and content calendar
- Brand manager: Ensure all content aligns with brand voice and messaging
- SEO specialist: Optimize content for search engines and discoverability

All content must be approved by brand manager before publication.
```

### Expected Workflow
1. **Brand Manager** defines brand guidelines and messaging strategy
2. **Content Writer** creates blog posts and documentation
3. **Social Media Strategist** develops campaign strategy and posts
4. **SEO Specialist** optimizes content for search engines
5. **Brand Manager** reviews all content for brand compliance
6. Team iterates based on feedback
7. **Social Media Strategist** schedules approved content
8. All teammates track performance metrics

### Sample Tasks
- Write 2000-word blog post about AI automation benefits
- Create 10 LinkedIn posts for launch campaign
- Develop FAQ document for new service
- Optimize blog post for "AI automation" keywords
- Design social media content calendar
- Review all content for brand voice compliance
- Schedule social media posts across platforms

---

## Example 4: Research and Analysis Team

### Scenario
Evaluate potential partnership with new AI company - need diverse perspectives.

### Team Setup
```bash
Create a research team to evaluate the InnovateAI partnership:
- Market analyst: Research InnovateAI's market position, competitors, and growth
- Technical analyst: Evaluate their technology stack, APIs, and integration potential
- Financial analyst: Assess financial terms, revenue impact, and cost-benefit
- Risk analyst: Identify potential risks, dependencies, and mitigation strategies

Have them debate findings and challenge each other's assumptions.
```

### Expected Workflow
1. Each analyst researches their domain independently
2. **Market Analyst** provides market and competitive analysis
3. **Technical Analyst** evaluates technical feasibility
4. **Financial Analyst** models financial impact
5. **Risk Analyst** identifies potential issues
6. Team debates findings in structured discussion
7. Each analyst challenges others' assumptions
8. Team reaches consensus recommendation
9. **Team Lead** synthesizes final recommendation

### Sample Tasks
- Research InnovateAI's market share and growth trajectory
- Analyze their API documentation and integration complexity
- Model revenue impact of partnership over 12 months
- Identify technical dependencies and integration risks
- Research customer reviews and satisfaction scores
- Evaluate competitive response to partnership
- Assess legal and compliance implications
- Create partnership recommendation report

---

## Team Communication Patterns

### Direct Messaging Examples
```
@email-processor: Please prioritize the partnership inquiry from TechCorp - it's time-sensitive
@social-media: The blog post is ready for promotion - can you create supporting social content?
@accounting: Need Q1 revenue numbers for the board presentation by 2 PM
@researcher: Can you validate the market size claims in the partnership proposal?
```

### Broadcast Examples
```
Team update: Client meeting moved to 3 PM - all deliverables need to be ready by 2:30 PM
Priority shift: Focus on the security incident response - all other tasks are secondary
Lunch break: Team standup at 1 PM to sync on morning progress
```

### Handoff Examples
```
@social-media: Content is approved and ready for scheduling. Files are in vault/Approved/Content/
@devops: Backend fix is tested and ready for deployment. Deployment notes in vault/Plans/
@accounting: Invoice data is processed and validated. Ready for Odoo import.
```

---

## Quality Gates and Approval Workflows

### Email Team Quality Gates
- All customer emails reviewed before sending
- Partnership emails require business development approval
- Technical support emails include solution verification
- Urgent emails escalated within 30 minutes

### Social Media Quality Gates
- All posts reviewed for brand voice compliance
- Include relevant hashtags and mentions
- Check for typos and grammar
- Verify links and attachments work
- Schedule posts for optimal engagement times

### Development Team Quality Gates
- All code changes include tests
- Production deployments require approval
- Security vulnerabilities addressed immediately
- Performance impact measured and documented
- Rollback plan prepared for all deployments

### Content Team Quality Gates
- Brand manager approval required for all content
- SEO optimization checklist completed
- Fact-checking for all claims and statistics
- Legal review for sensitive topics
- Accessibility compliance verified

---

## Troubleshooting Common Issues

### Teammate Not Responding
```
@teammate-name: Please provide status update on your current task
If no response: Spawn replacement teammate and reassign tasks
```

### Task Conflicts
```
Team lead: Reassign conflicting tasks to different teammates
Update task dependencies to prevent future conflicts
Use file locking for shared resources
```

### Quality Issues
```
Use quality check hooks to catch issues early
Implement peer review for critical deliverables
Set up automated validation where possible
```

### Communication Gaps
```
Establish regular check-in schedule
Use explicit handoff messages
Document decisions in shared vault
Create status update templates
```

These examples demonstrate how agent teams can dramatically increase your Personal AI Employee's capability to handle complex, multi-domain tasks efficiently while maintaining quality and coordination.