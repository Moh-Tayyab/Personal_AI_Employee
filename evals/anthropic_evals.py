#!/usr/bin/env python3
"""
Skill Evaluator - Integration with Official Anthropic skill-creator

This script provides a bridge between the simple CSV-based eval framework
and the official Anthropic skill-creator eval system.

Usage:
    # Run simple CSV-based evals (our framework)
    python evals/runner.py --skill mcp-email --prompt-set evals/prompt-sets/mcp-email.csv
    
    # Run official Anthropic trigger evals
    python evals/anthropic_evals.py trigger --skill-path .claude/skills/skill-creator --eval-set evals/trigger-evals.json
    
    # Run official Anthropic task evals
    python evals/anthropic_evals.py task --skill-path .claude/skills/skill-creator --workspace mcp-email-workspace
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def create_trigger_eval_set(skill_name: str, output_path: Path):
    """
    Create a trigger evaluation set for testing skill description triggering.
    
    This tests whether the skill's description causes Claude to trigger
    (read the skill) for various queries.
    """
    eval_set = {
        "skill_name": skill_name,
        "queries": [
            {
                "query": f"Use the {skill_name} skill to send an email",
                "should_trigger": True
            },
            {
                "query": f"Run {skill_name} for processing emails",
                "should_trigger": True
            },
            {
                "query": "Send an email to test@example.com",
                "should_trigger": True  # If skill is about email
            },
            {
                "query": "Write a Python script",
                "should_trigger": False
            },
            {
                "query": "Create a PowerPoint presentation",
                "should_trigger": False
            }
        ]
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(eval_set, f, indent=2)
    
    print(f"✅ Created trigger eval set: {output_path}")
    return output_path


def create_task_eval_set(skill_name: str, output_path: Path):
    """
    Create a task evaluation set for testing skill execution.
    
    This tests whether the skill produces correct outputs when executed.
    """
    eval_set = {
        "skill_name": skill_name,
        "evals": [
            {
                "id": 1,
                "prompt": "Send an email to test@example.com with subject 'Test' and body 'Hello World'",
                "expected_output": "Email sent successfully to test@example.com",
                "files": [],
                "expectations": [
                    "The email was sent to test@example.com",
                    "The subject line is 'Test'",
                    "The body contains 'Hello World'"
                ]
            },
            {
                "id": 2,
                "prompt": "Draft a reply to the latest email",
                "expected_output": "Draft email created in Drafts folder",
                "files": [],
                "expectations": [
                    "A draft file was created",
                    "The draft is in the Drafts folder"
                ]
            },
            {
                "id": 3,
                "prompt": "Search for emails about 'project update'",
                "expected_output": "Search results returned",
                "files": [],
                "expectations": [
                    "Email search was performed",
                    "Results were returned"
                ]
            }
        ]
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(eval_set, f, indent=2)
    
    print(f"✅ Created task eval set: {output_path}")
    return output_path


def run_trigger_eval(skill_path: str, eval_set_path: str, workspace: str = None):
    """
    Run trigger evaluation using official skill-creator run_eval.py
    """
    skill_creator_path = Path(__file__).parent.parent / '.claude' / 'skills' / 'skill-creator'
    run_eval_script = skill_creator_path / 'scripts' / 'run_eval.py'
    
    if not run_eval_script.exists():
        print(f"❌ Error: run_eval.py not found at {run_eval_script}")
        return False
    
    cmd = [
        sys.executable,
        str(run_eval_script),
        '--eval-set', eval_set_path,
        '--skill-path', skill_path,
        '--runs-per-query', '3',
        '--verbose'
    ]
    
    if workspace:
        cmd.extend(['--workspace', workspace])
    
    print(f"Running trigger eval: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ Trigger eval completed successfully")
        return True
    else:
        print(f"❌ Trigger eval failed with code {result.returncode}")
        return False


def run_task_eval(skill_path: str, workspace: str):
    """
    Run task evaluation using official skill-creator workflow.
    
    This spawns subagents to execute tasks with and without the skill.
    """
    print(f"Task eval requires Claude Code session.")
    print(f"Use the skill-creator skill within Claude Code to run task evals.")
    print(f"\nInstructions:")
    print(f"1. Start a Claude Code session")
    print(f"2. Use the skill-creator skill")
    print(f"3. Provide the eval prompts from evals/evals.json")
    print(f"4. Review results with eval-viewer/generate_review.py")
    return True


def convert_csv_to_json(csv_path: str, output_path: str):
    """
    Convert our CSV prompt set to official Anthropic JSON format.
    """
    import csv
    
    evals = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            eval_entry = {
                "id": i,
                "prompt": row['prompt'],
                "expected_output": row.get('expected_outcome', 'Task completed'),
                "files": [],
                "expectations": [
                    f"Task completed: {row.get('expected_outcome', 'success')}"
                ]
            }
            evals.append(eval_entry)
    
    output = {
        "skill_name": Path(csv_path).stem,
        "evals": evals
    }
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Converted {csv_path} to {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Trigger eval command
    trigger_parser = subparsers.add_parser('trigger', help='Run trigger evaluation')
    trigger_parser.add_argument('--skill-path', required=True, help='Path to skill directory')
    trigger_parser.add_argument('--eval-set', required=True, help='Path to eval set JSON')
    trigger_parser.add_argument('--workspace', help='Workspace directory for results')
    
    # Task eval command
    task_parser = subparsers.add_parser('task', help='Run task evaluation')
    task_parser.add_argument('--skill-path', required=True, help='Path to skill directory')
    task_parser.add_argument('--workspace', required=True, help='Workspace directory')
    
    # Create eval set command
    create_parser = subparsers.add_parser('create', help='Create eval set')
    create_parser.add_argument('--skill-name', required=True, help='Skill name')
    create_parser.add_argument('--type', choices=['trigger', 'task'], default='task', help='Eval type')
    create_parser.add_argument('--output', help='Output path (default: evals/<type>-evals.json)')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert CSV to JSON')
    convert_parser.add_argument('--csv', required=True, help='Input CSV path')
    convert_parser.add_argument('--output', required=True, help='Output JSON path')
    
    args = parser.parse_args()
    
    if args.command == 'trigger':
        success = run_trigger_eval(args.skill_path, args.eval_set, args.workspace)
        sys.exit(0 if success else 1)
    
    elif args.command == 'task':
        success = run_task_eval(args.skill_path, args.workspace)
        sys.exit(0 if success else 1)
    
    elif args.command == 'create':
        output_path = Path(args.output) if args.output else Path(f'evals/{args.type}-evals.json')
        if args.type == 'trigger':
            create_trigger_eval_set(args.skill_name, output_path)
        else:
            create_task_eval_set(args.skill_name, output_path)
    
    elif args.command == 'convert':
        convert_csv_to_json(args.csv, args.output)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
