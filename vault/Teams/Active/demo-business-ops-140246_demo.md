# Agent Team Demo: Business-Ops

**Created:** 2026-03-12 14:02:46
**Status:** Demo Mode
**Items:** 4 work items created

## Team Composition
Create a business operations team with 4 specialists:
- Email specialist: Handle partnership inquiry and customer communications
- Social media manager: Create LinkedIn post and manage engagement
- Accounting specialist: Process monthly expenses and update financial records
- Research analyst: Conduct competitor analysis and market intelligence

Each teammate should work independently while coordinating through shared tasks.

## Sample Work Items Created
- EMAIL_20260312_140241_001_partnership_inquiry.md
- SOCIAL_20260312_140241_002_linkedin_post.md
- INVOICE_20260312_140241_003_monthly_expenses.md
- RESEARCH_20260312_140241_004_competitor_analysis.md

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
./scripts/manage_teams.sh tasks demo-business-ops-140246

# View team logs
cat vault/Teams/Logs/demo-business-ops-140246_*.md
```
