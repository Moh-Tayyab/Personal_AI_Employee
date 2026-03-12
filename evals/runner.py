#!/usr/bin/env python3
"""
Skill Evaluation Runner

Executes evaluation prompt sets against skills and generates reports.

Usage:
    python evals/runner.py --skill <skill-name> --prompt-set <csv-file>
    python evals/runner.py --skill mcp-email --prompt-set evals/prompt-sets/mcp-email.csv
"""

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class SkillEvaluator:
    """Runs evaluations against skills."""
    
    def __init__(self, skill_name: str, vault_path: Path = None):
        """
        Initialize evaluator.
        
        Args:
            skill_name: Name of skill to evaluate
            vault_path: Path to Obsidian vault (optional)
        """
        self.skill_name = skill_name
        self.vault_path = vault_path or Path.home() / 'vault'
        self.results = []
        self.artifacts_dir = Path(__file__).parent / 'artifacts'
        self.reports_dir = Path(__file__).parent / 'reports'
        self.checks_dir = Path(__file__).parent / 'checks'
        
        # Ensure directories exist
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def load_prompt_set(self, csv_path: str) -> list[dict]:
        """
        Load prompts from CSV file.
        
        Args:
            csv_path: Path to CSV file
        
        Returns:
            List of prompt dictionaries
        """
        prompts = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prompts.append({
                    'id': row['id'],
                    'should_trigger': row['should_trigger'].lower() == 'true',
                    'prompt': row['prompt'],
                    'expected_outcome': row.get('expected_outcome', 'unknown'),
                    'category': row.get('category', 'general')
                })
        return prompts
    
    def execute_prompt(self, prompt: dict) -> dict:
        """
        Execute a single prompt and capture trace.
        
        In a real implementation, this would:
        1. Invoke Claude Code with the skill
        2. Capture JSONL trace output
        3. Save artifacts
        
        For now, this is a placeholder that simulates execution.
        
        Args:
            prompt: Prompt dictionary
        
        Returns:
            Execution result with trace
        """
        print(f"  Executing: {prompt['id']} - {prompt['prompt'][:50]}...")
        
        # TODO: Real implementation would use:
        # codex exec --json --full-auto "<prompt>"
        # or
        # claude-code --skill <skill> --json "<prompt>"
        
        # Simulated trace for demonstration
        trace = {
            'prompt': prompt['prompt'],
            'skill': self.skill_name,
            'timestamp': datetime.now().isoformat(),
            'events': self._simulate_execution(prompt),
            'usage': {
                'input_tokens': 1500,
                'output_tokens': 800,
                'total_tokens': 2300
            }
        }
        
        # Save trace to artifacts
        artifact_path = self.artifacts_dir / f"{prompt['id']}.trace.json"
        with open(artifact_path, 'w') as f:
            json.dump(trace, f, indent=2)
        
        return {
            'prompt': prompt,
            'trace': trace,
            'artifact_path': str(artifact_path)
        }
    
    def _simulate_execution(self, prompt: dict) -> list[dict]:
        """
        Simulate execution events for demonstration.
        
        In real implementation, this comes from actual skill execution.
        """
        outcome = prompt['expected_outcome']
        
        if not prompt['should_trigger']:
            return [
                {'type': 'skill.analyzed', 'details': {'triggered': False}}
            ]
        
        if outcome == 'email_sent':
            return [
                {'type': 'skill.invoked', 'skill': self.skill_name},
                {'type': 'context.gathered', 'details': {'source': 'vault'}},
                {'type': 'command_execution', 'command': 'mcp-email send --to test@example.com'},
                {'type': 'email.sent', 'details': {'to': 'test@example.com', 'subject': 'Test'}}
            ]
        elif outcome == 'draft_created':
            return [
                {'type': 'skill.invoked', 'skill': self.skill_name},
                {'type': 'command_execution', 'command': 'mcp-email draft --reply latest'},
                {'type': 'file.created', 'path': 'vault/Drafts/draft-reply.md'}
            ]
        elif outcome == 'search_completed':
            return [
                {'type': 'skill.invoked', 'skill': self.skill_name},
                {'type': 'command_execution', 'command': 'mcp-email search --query "project update"'},
                {'type': 'email.search', 'results': [{'id': '123', 'subject': 'Project Update'}]}
            ]
        else:
            return [
                {'type': 'skill.invoked', 'skill': self.skill_name},
                {'type': 'skill.completed', 'details': {'status': 'success'}}
            ]
    
    def run_checks(self, execution_result: dict) -> dict:
        """
        Run evaluation checks on execution result.
        
        Args:
            execution_result: Result from execute_prompt
        
        Returns:
            Check results
        """
        prompt = execution_result['prompt']
        trace = execution_result['trace']
        
        checks = []
        
        # Check 1: Skill invocation
        invoked_check = self._check_invocation(trace, prompt['should_trigger'])
        checks.append(invoked_check)
        
        # Check 2: Expected outcome
        if prompt['should_trigger']:
            outcome_check = self._check_outcome(trace, prompt['expected_outcome'])
            checks.append(outcome_check)
        
        # Check 3: Token efficiency
        token_check = self._check_token_efficiency(trace)
        checks.append(token_check)
        
        # Check 4: Command count
        command_check = self._check_command_count(trace)
        checks.append(command_check)
        
        # Calculate overall pass/fail
        all_passed = all(c['pass'] for c in checks)
        
        return {
            'prompt_id': prompt['id'],
            'checks': checks,
            'overall_pass': all_passed,
            'score': sum(c['pass'] for c in checks) / len(checks) * 100
        }
    
    def _check_invocation(self, trace: dict, should_trigger: bool) -> dict:
        """Check if skill was invoked correctly."""
        events = trace.get('events', [])
        invoked = any(e.get('type') == 'skill.invoked' for e in events)
        
        passed = (invoked == should_trigger)
        
        return {
            'id': 'skill_invocation',
            'pass': passed,
            'evidence': f"Skill {'invoked' if invoked else 'not invoked'}",
            'notes': f"Expected: {'invoke' if should_trigger else 'skip'}, Got: {'invoke' if invoked else 'skip'}"
        }
    
    def _check_outcome(self, trace: dict, expected_outcome: str) -> dict:
        """Check if expected outcome was achieved."""
        events = trace.get('events', [])
        event_types = [e.get('type') for e in events]
        
        outcome_map = {
            'email_sent': 'email.sent',
            'draft_created': 'file.created',
            'search_completed': 'email.search'
        }
        
        expected_event = outcome_map.get(expected_outcome)
        passed = expected_event in event_types if expected_event else False
        
        return {
            'id': 'outcome_achieved',
            'pass': passed,
            'evidence': f"Events: {', '.join(event_types)}",
            'notes': f"Expected outcome: {expected_outcome}"
        }
    
    def _check_token_efficiency(self, trace: dict, max_tokens: int = 5000) -> dict:
        """Check token usage."""
        usage = trace.get('usage', {})
        total_tokens = usage.get('total_tokens', 0)
        passed = total_tokens <= max_tokens
        
        return {
            'id': 'token_efficiency',
            'pass': passed,
            'evidence': f"Total tokens: {total_tokens}",
            'notes': f"Limit: {max_tokens}"
        }
    
    def _check_command_count(self, trace: dict, max_commands: int = 10) -> dict:
        """Check command count (thrashing detection)."""
        events = trace.get('events', [])
        command_count = sum(1 for e in events if e.get('type') == 'command_execution')
        passed = command_count <= max_commands
        
        return {
            'id': 'command_efficiency',
            'pass': passed,
            'evidence': f"Commands executed: {command_count}",
            'notes': f"Limit: {max_commands}"
        }
    
    def run_evaluation(self, prompt_set_path: str) -> dict:
        """
        Run complete evaluation.
        
        Args:
            prompt_set_path: Path to CSV prompt set
        
        Returns:
            Complete evaluation results
        """
        print(f"\n{'='*60}")
        print(f"Evaluating skill: {self.skill_name}")
        print(f"Prompt set: {prompt_set_path}")
        print(f"{'='*60}\n")
        
        prompts = self.load_prompt_set(prompt_set_path)
        print(f"Loaded {len(prompts)} prompts\n")
        
        results = []
        for prompt in prompts:
            execution = self.execute_prompt(prompt)
            check_result = self.run_checks(execution)
            check_result['execution'] = execution
            results.append(check_result)
        
        self.results = results
        
        # Generate report
        report_path = self.generate_report()
        
        return {
            'skill': self.skill_name,
            'prompt_set': prompt_set_path,
            'results': results,
            'report_path': str(report_path),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_report(self) -> Path:
        """
        Generate markdown report from results.
        
        Returns:
            Path to report file
        """
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        report_path = self.reports_dir / f"{self.skill_name}-report-{timestamp}.md"
        
        # Calculate summary statistics
        total = len(self.results)
        passed = sum(1 for r in self.results if r['overall_pass'])
        avg_score = sum(r['score'] for r in self.results) / total if total > 0 else 0
        
        # Generate report
        report = f"""# Evaluation Report: {self.skill_name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Prompt Set:** {self.skill_name}.csv

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {total} |
| Passed | {passed} |
| Failed | {total - passed} |
| Pass Rate | {passed/total*100:.1f}% |
| Average Score | {avg_score:.1f}/100 |

## Results by Category

"""
        
        # Group by category
        categories = {}
        for result in self.results:
            category = result['execution']['prompt'].get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        for category, results in categories.items():
            cat_passed = sum(1 for r in results if r['overall_pass'])
            cat_total = len(results)
            report += f"### {category.title()}\n\n"
            report += f"| ID | Status | Score |\n"
            report += f"|----|--------|-------|\n"
            for r in results:
                status = "✅ Pass" if r['overall_pass'] else "❌ Fail"
                report += f"| {r['prompt_id']} | {status} | {r['score']:.0f} |\n"
            report += f"\n"
        
        # Detailed results
        report += """## Detailed Results

"""
        for result in self.results:
            prompt_text = result['execution']['prompt']['prompt']
            status = "✅ PASS" if result['overall_pass'] else "❌ FAIL"
            
            report += f"### {result['prompt_id']}: {status}\n\n"
            report += f"**Prompt:** {prompt_text}\n\n"
            report += f"**Category:** {result['execution']['prompt'].get('category', 'general')}\n\n"
            report += f"**Checks:**\n\n"
            
            for check in result['checks']:
                check_status = "✅" if check['pass'] else "❌"
                report += f"- {check_status} **{check['id']}**: {check['notes']}\n"
                report += f"  - Evidence: {check['evidence']}\n"
            
            report += f"\n---\n\n"
        
        # Write report
        report_path.write_text(report)
        print(f"\nReport generated: {report_path}\n")
        
        return report_path


def main():
    parser = argparse.ArgumentParser(description='Run skill evaluations')
    parser.add_argument('--skill', required=True, help='Skill name to evaluate')
    parser.add_argument('--prompt-set', required=True, help='Path to CSV prompt set')
    parser.add_argument('--vault', help='Path to Obsidian vault')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault) if args.vault else None
    
    evaluator = SkillEvaluator(args.skill, vault_path)
    results = evaluator.run_evaluation(args.prompt_set)
    
    # Print summary
    print(f"\n{'='*60}")
    print("EVALUATION COMPLETE")
    print(f"{'='*60}")
    print(f"Skill: {results['skill']}")
    print(f"Tests: {len(results['results'])}")
    print(f"Passed: {sum(1 for r in results['results'] if r['overall_pass'])}")
    print(f"Report: {results['report_path']}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
