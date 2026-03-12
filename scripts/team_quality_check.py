#!/usr/bin/env python3
"""
Team Quality Check Script for Agent Teams
Validates teammate work quality and enforces standards before going idle.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

def load_team_config(team_name):
    """Load team configuration from Claude teams directory."""
    teams_dir = Path.home() / ".claude" / "teams" / team_name
    config_file = teams_dir / "config.json"

    if not config_file.exists():
        return None

    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading team config: {e}", file=sys.stderr)
        return None

def check_task_completion(team_name, teammate_id):
    """Check if teammate has properly completed their assigned tasks."""
    tasks_dir = Path.home() / ".claude" / "tasks" / team_name

    if not tasks_dir.exists():
        return True, "No tasks directory found"

    issues = []
    completed_tasks = 0

    # Check all task files
    for task_file in tasks_dir.glob("*.json"):
        try:
            with open(task_file, 'r') as f:
                task = json.load(f)

            # Check if this task is assigned to the teammate
            if task.get('owner') == teammate_id:
                if task.get('status') == 'in_progress':
                    issues.append(f"Task {task.get('id', 'unknown')} still in progress")
                elif task.get('status') == 'completed':
                    completed_tasks += 1

                    # Validate completed task has proper documentation
                    if not task.get('description'):
                        issues.append(f"Task {task.get('id', 'unknown')} missing description")

                    # Check for completion timestamp
                    if not task.get('completedAt'):
                        issues.append(f"Task {task.get('id', 'unknown')} missing completion timestamp")

        except Exception as e:
            issues.append(f"Error reading task file {task_file}: {e}")

    return len(issues) == 0, f"Completed {completed_tasks} tasks. Issues: {'; '.join(issues) if issues else 'None'}"

def check_work_quality(team_name, teammate_id, last_action):
    """Check the quality of work performed by the teammate."""
    issues = []

    # Check based on teammate role/type
    team_config = load_team_config(team_name)
    if team_config:
        teammate_info = None
        for member in team_config.get('members', []):
            if member.get('name') == teammate_id:
                teammate_info = member
                break

        if teammate_info:
            agent_type = teammate_info.get('agentType', '')

            # Role-specific quality checks
            if 'email' in agent_type.lower():
                # Email specialist quality checks
                if 'send' in last_action.lower() and 'draft' not in last_action.lower():
                    issues.append("Email sent without draft review - consider using draft workflow")

            elif 'social' in agent_type.lower():
                # Social media quality checks
                if 'post' in last_action.lower():
                    # Check if post includes required elements (this is a simplified check)
                    if len(last_action) < 50:
                        issues.append("Social media post may be too short for engagement")

            elif 'accounting' in agent_type.lower():
                # Accounting quality checks
                if 'update' in last_action.lower() or 'process' in last_action.lower():
                    # Ensure financial data is properly validated
                    pass  # Would implement actual validation logic here

    return len(issues) == 0, f"Quality check issues: {'; '.join(issues) if issues else 'None'}"

def check_handoff_requirements(team_name, teammate_id):
    """Check if teammate has properly handed off work to other team members."""
    # This would check for proper handoff documentation
    # For now, we'll do a basic check

    vault_dir = Path("./vault")
    handoff_dir = vault_dir / "Handoffs"

    if not handoff_dir.exists():
        return True, "No handoff directory - assuming no handoffs required"

    # Look for recent handoff files from this teammate
    recent_handoffs = []
    for handoff_file in handoff_dir.glob(f"*{teammate_id}*.md"):
        stat = handoff_file.stat()
        # Check if file was modified in the last hour
        if (datetime.now().timestamp() - stat.st_mtime) < 3600:
            recent_handoffs.append(handoff_file.name)

    return True, f"Recent handoffs: {', '.join(recent_handoffs) if recent_handoffs else 'None'}"

def main():
    parser = argparse.ArgumentParser(description='Team Quality Check for Agent Teams')
    parser.add_argument('--teammate-id', required=True, help='ID of the teammate')
    parser.add_argument('--team-name', required=True, help='Name of the team')
    parser.add_argument('--last-action', required=True, help='Description of last action performed')
    parser.add_argument('--strict', action='store_true', help='Use strict quality checks')

    args = parser.parse_args()

    print(f"Running quality check for teammate: {args.teammate_id}")
    print(f"Team: {args.team_name}")
    print(f"Last action: {args.last_action}")

    all_passed = True
    results = []

    # Run quality checks
    checks = [
        ("Task Completion", check_task_completion(args.team_name, args.teammate_id)),
        ("Work Quality", check_work_quality(args.team_name, args.teammate_id, args.last_action)),
        ("Handoff Requirements", check_handoff_requirements(args.team_name, args.teammate_id))
    ]

    for check_name, (passed, message) in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check_name}: {status} - {message}")
        results.append({"check": check_name, "passed": passed, "message": message})

        if not passed:
            all_passed = False

    # Log results to vault
    vault_dir = Path("./vault")
    logs_dir = vault_dir / "Logs" / "TeamQuality"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / f"{args.team_name}_{args.teammate_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    log_data = {
        "timestamp": datetime.now().isoformat(),
        "teammate_id": args.teammate_id,
        "team_name": args.team_name,
        "last_action": args.last_action,
        "overall_passed": all_passed,
        "checks": results
    }

    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)

    print(f"\nOverall Result: {'✓ PASS' if all_passed else '✗ FAIL'}")
    print(f"Quality check log saved to: {log_file}")

    # Exit with appropriate code
    # Exit code 2 means "blocking error" - teammate should not go idle
    # Exit code 0 means success - teammate can go idle
    # Exit code 1 means non-blocking error - teammate can go idle but with warnings

    if args.strict and not all_passed:
        print("Strict mode: Blocking teammate from going idle due to quality issues")
        sys.exit(2)
    elif not all_passed:
        print("Quality issues found but allowing teammate to go idle")
        sys.exit(1)
    else:
        print("All quality checks passed")
        sys.exit(0)

if __name__ == "__main__":
    main()