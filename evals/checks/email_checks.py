#!/usr/bin/env python3
"""
Evaluation Checks for MCP Email Skill

Deterministic checks for verifying email skill behavior.
"""

import json
from pathlib import Path
from typing import Any


def check_email_sent(trace: dict) -> tuple[bool, str]:
    """
    Check if email was sent by examining trace events.
    
    Returns:
        tuple: (passed, evidence)
    """
    events = trace.get('events', [])
    
    for event in events:
        # Check for email sent event
        if event.get('type') == 'email.sent':
            return True, f"Email sent event found: {json.dumps(event.get('details', {}))}"
        
        # Check for MCP email send command
        if event.get('type') == 'command_execution':
            command = event.get('command', '')
            if 'email' in command.lower() and 'send' in command.lower():
                return True, f"Email send command executed: {command}"
    
    return False, "No email sent event found in trace"


def check_draft_created(trace: dict, vault_path: Path) -> tuple[bool, str]:
    """
    Check if draft email was created in vault.
    
    Returns:
        tuple: (passed, evidence)
    """
    drafts_folder = vault_path / 'Drafts'
    
    if not drafts_folder.exists():
        return False, "Drafts folder does not exist"
    
    # Check for new markdown files in Drafts
    draft_files = list(drafts_folder.glob('*.md'))
    if draft_files:
        latest_draft = max(draft_files, key=lambda p: p.stat().st_mtime)
        return True, f"Draft created: {latest_draft.name}"
    
    # Check trace for draft creation
    events = trace.get('events', [])
    for event in events:
        if event.get('type') == 'file.created':
            path = event.get('path', '')
            if 'draft' in path.lower():
                return True, f"Draft file created: {path}"
    
    return False, "No draft creation detected"


def check_search_completed(trace: dict) -> tuple[bool, str]:
    """
    Check if email search was completed.
    
    Returns:
        tuple: (passed, evidence)
    """
    events = trace.get('events', [])
    
    for event in events:
        # Check for search event
        if event.get('type') == 'email.search':
            results = event.get('results', [])
            if isinstance(results, list):
                return True, f"Search completed, found {len(results)} results"
        
        # Check for MCP search command
        if event.get('type') == 'command_execution':
            command = event.get('command', '')
            if 'email' in command.lower() and 'search' in command.lower():
                return True, f"Email search command executed: {command}"
    
    return False, "No email search event found in trace"


def check_no_trigger(trace: dict) -> tuple[bool, str]:
    """
    Check that skill correctly did NOT trigger.
    
    Returns:
        tuple: (passed, evidence)
    """
    events = trace.get('events', [])
    
    # Check if any email-related actions were taken
    email_actions = ['email.sent', 'email.search', 'email.draft', 'email.read']
    
    for event in events:
        event_type = event.get('type', '')
        if event_type in email_actions:
            return False, f"Skill incorrectly triggered: {event_type}"
        
        # Check for email commands
        if event.get('type') == 'command_execution':
            command = event.get('command', '')
            if any(term in command.lower() for term in ['email', 'send', 'draft']):
                return False, f"Email command incorrectly executed: {command}"
    
    return True, "Skill correctly did not trigger for non-email prompt"


def check_skill_invoked(trace: dict, expected: bool) -> tuple[bool, str]:
    """
    Check if skill was invoked when it should/shouldn't be.
    
    Args:
        trace: Execution trace
        expected: Whether invocation was expected
    
    Returns:
        tuple: (passed, evidence)
    """
    events = trace.get('events', [])
    
    invoked = False
    for event in events:
        if event.get('type') == 'skill.invoked':
            skill = event.get('skill', '')
            if 'email' in skill.lower() or 'mcp' in skill.lower():
                invoked = True
                break
    
    if invoked == expected:
        status = "invoked" if invoked else "not invoked"
        return True, f"Skill correctly {status}"
    else:
        if expected:
            return False, "Skill should have been invoked but wasn't"
        else:
            return False, "Skill should NOT have been invoked but was"


def check_token_efficiency(trace: dict, max_tokens: int = 5000) -> tuple[bool, str]:
    """
    Check if execution was token-efficient.
    
    Args:
        trace: Execution trace
        max_tokens: Maximum acceptable token usage
    
    Returns:
        tuple: (passed, evidence)
    """
    usage = trace.get('usage', {})
    total_tokens = usage.get('total_tokens', 0)
    
    if total_tokens <= max_tokens:
        return True, f"Token usage: {total_tokens} (under {max_tokens} limit)"
    else:
        return False, f"Token usage: {total_tokens} (exceeds {max_tokens} limit)"


def check_command_count(trace: dict, max_commands: int = 10) -> tuple[bool, str]:
    """
    Check if execution didn't thrash (too many commands).
    
    Args:
        trace: Execution trace
        max_commands: Maximum acceptable command count
    
    Returns:
        tuple: (passed, evidence)
    """
    events = trace.get('events', [])
    command_count = sum(1 for e in events if e.get('type') == 'command_execution')
    
    if command_count <= max_commands:
        return True, f"Command count: {command_count} (under {max_commands} limit)"
    else:
        return False, f"Command count: {command_count} (exceeds {max_commands} limit)"


def check_file_exists(file_path: Path) -> tuple[bool, str]:
    """
    Check if expected file exists.
    
    Args:
        file_path: Path to check
    
    Returns:
        tuple: (passed, evidence)
    """
    if file_path.exists():
        return True, f"File exists: {file_path}"
    else:
        return False, f"File not found: {file_path}"


def check_file_content(file_path: Path, expected_content: str) -> tuple[bool, str]:
    """
    Check if file contains expected content.
    
    Args:
        file_path: Path to file
        expected_content: String that should be in file
    
    Returns:
        tuple: (passed, evidence)
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    content = file_path.read_text()
    if expected_content in content:
        return True, f"File contains '{expected_content}'"
    else:
        return False, f"File does not contain '{expected_content}'"


# Map of check names to functions
CHECKS = {
    'email_sent': check_email_sent,
    'draft_created': check_draft_created,
    'search_completed': check_search_completed,
    'no_trigger': check_no_trigger,
}


def run_check(check_name: str, trace: dict, vault_path: Path = None, **kwargs) -> dict:
    """
    Run a named check with provided arguments.
    
    Args:
        check_name: Name of check to run
        trace: Execution trace
        vault_path: Path to vault (optional)
        **kwargs: Additional arguments for check
    
    Returns:
        dict: Check result with pass/fail and evidence
    """
    if check_name not in CHECKS:
        return {
            'pass': False,
            'evidence': f"Unknown check: {check_name}",
            'notes': f"Check '{check_name}' not found in CHECKS registry"
        }
    
    check_func = CHECKS[check_name]
    
    try:
        # Call check function with appropriate arguments
        import inspect
        sig = inspect.signature(check_func)
        params = {}
        if 'trace' in sig.parameters:
            params['trace'] = trace
        if 'vault_path' in sig.parameters and vault_path:
            params['vault_path'] = vault_path
        
        result = check_func(**params)
        
        if isinstance(result, tuple) and len(result) == 2:
            passed, evidence = result
            return {
                'pass': passed,
                'evidence': evidence,
                'notes': f"Check '{check_name}' executed successfully"
            }
        else:
            return {
                'pass': False,
                'evidence': str(result),
                'notes': f"Check '{check_name}' returned unexpected result"
            }
    
    except Exception as e:
        return {
            'pass': False,
            'evidence': f"Error: {str(e)}",
            'notes': f"Check '{check_name}' raised exception"
        }
