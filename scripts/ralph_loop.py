#!/usr/bin/env python3
"""
Ralph Wiggum Loop - Multi-Step Task Persistence (Gold Tier)

The Ralph Wiggum pattern keeps Qwen Code working autonomously until a task
is marked complete. It intercepts the agent's exit and re-injects the prompt
if the task is not yet done.

Usage:
    python scripts/ralph_loop.py --vault ./vault --prompt "Process all items"

Features:
- File movement detection (task completion)
- Promise-based completion detection
- Maximum iteration limiting
- Progress tracking
- Graceful exit on completion
"""

import os
import sys
import time
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Ralph_Loop")


class RalphWiggumLoop:
    """
    Ralph Wiggum persistence loop for multi-step task completion.
    """
    
    def __init__(
        self,
        vault_path: str,
        prompt: str,
        max_iterations: int = 10,
        completion_signal: str = None,
        check_interval: float = 2.0
    ):
        self.vault_path = Path(vault_path)
        self.prompt = prompt
        self.max_iterations = max_iterations
        self.completion_signal = completion_signal  # Optional: text to look for in output
        self.check_interval = check_interval
        
        # Directories
        self.done_dir = self.vault_path / 'Done'
        self.plans_dir = self.vault_path / 'Plans'
        self.needs_action_dir = self.vault_path / 'Needs_Action'
        
        # State
        self.iteration = 0
        self.start_time = None
        self.task_start_state = None
        
        # Ensure directories exist
        self.done_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_completion_strategies(self) -> List[Dict[str, Any]]:
        """Get available completion detection strategies."""
        return [
            {
                'name': 'file_movement',
                'description': 'Detect when files move to Done/',
                'check': self._check_file_movement
            },
            {
                'name': 'promise_detection',
                'description': 'Detect <promise>TASK_COMPLETE</promise> in output',
                'check': self._check_promise
            },
            {
                'name': 'needs_action_empty',
                'description': 'Check if Needs_Action/ is empty',
                'check': self._check_needs_action_empty
            }
        ]
    
    def _capture_start_state(self):
        """Capture the initial state for comparison."""
        self.task_start_state = {
            'done_count': len(list(self.done_dir.glob('*.md'))),
            'needs_action_count': len(list(self.needs_action_dir.glob('*.md'))),
            'plans_count': len(list(self.plans_dir.glob('*.md'))) if self.plans_dir.exists() else 0,
            'timestamp': datetime.now()
        }
        logger.info(f"Initial state: {self.task_start_state['needs_action_count']} items in Needs_Action, "
                   f"{self.task_start_state['done_count']} in Done")
    
    def _check_file_movement(self, last_output: str = None) -> bool:
        """Check if files have moved to Done/."""
        current_done_count = len(list(self.done_dir.glob('*.md')))
        
        if current_done_count > self.task_start_state['done_count']:
            logger.info(f"File movement detected: {current_done_count - self.task_start_state['done_count']} "
                       f"new files in Done/")
            return True
        
        return False
    
    def _check_promise(self, last_output: str = None) -> bool:
        """Check for completion promise in output."""
        if not last_output:
            return False
            
        completion_markers = [
            '<promise>TASK_COMPLETE</promise>',
            '<TASK_COMPLETE>',
            'TASK_COMPLETE',
            '[TASK COMPLETE]',
            '✅ Task complete'
        ]
        
        for marker in completion_markers:
            if marker in last_output:
                logger.info(f"Completion promise detected: {marker}")
                return True
        
        return False
    
    def _check_needs_action_empty(self, last_output: str = None) -> bool:
        """Check if Needs_Action/ folder is empty."""
        current_count = len(list(self.needs_action_dir.glob('*.md')))
        
        if current_count == 0 and self.task_start_state['needs_action_count'] > 0:
            logger.info("Needs_Action folder is now empty - task complete")
            return True
        
        return False
    
    def _run_qwen(self, prompt: str) -> tuple:
        """
        Run Qwen Code with the given prompt.
        
        Returns:
            Tuple of (success, output)
        """
        try:
            # Build command
            cmd = [
                'qwen',
                '--prompt', prompt,
                '--cwd', str(self.vault_path)
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            # Run with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per iteration
            )
            
            output = result.stdout + result.stderr
            
            if result.returncode == 0:
                return True, output
            else:
                logger.error(f"Qwen exited with code {result.returncode}")
                return False, output
                
        except subprocess.TimeoutExpired:
            logger.error("Qwen timed out after 5 minutes")
            return False, "Timeout expired"
        except FileNotFoundError:
            logger.error("qwen command not found. Install Qwen Code.")
            return False, "Command not found"
        except Exception as e:
            logger.error(f"Error running Qwen: {e}")
            return False, str(e)
    
    def _log_iteration(self, iteration: int, output: str, completed: bool):
        """Log iteration details."""
        logs_dir = self.vault_path / 'Logs' / 'ralph_loop'
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = logs_dir / f"iteration_{iteration:03d}.json"
        
        log_entry = {
            'iteration': iteration,
            'timestamp': datetime.now().isoformat(),
            'completed': completed,
            'output_length': len(output),
            'output_preview': output[:500] if output else None,
            'done_count': len(list(self.done_dir.glob('*.md'))),
            'needs_action_count': len(list(self.needs_action_dir.glob('*.md')))
        }
        
        log_file.write_text(json.dumps(log_entry, indent=2))
    
    def run(self) -> Dict[str, Any]:
        """
        Run the Ralph Wiggum loop until task completion or max iterations.
        
        Returns:
            Dict with run results
        """
        logger.info("="*60)
        logger.info("Starting Ralph Wiggum Loop")
        logger.info(f"Prompt: {self.prompt[:100]}...")
        logger.info(f"Max iterations: {self.max_iterations}")
        logger.info("="*60)
        
        self.start_time = datetime.now()
        self._capture_start_state()
        
        last_output = ""
        completion_detected = False
        completion_strategy = None
        
        while self.iteration < self.max_iterations:
            self.iteration += 1
            
            logger.info(f"\n{'='*40}")
            logger.info(f"Iteration {self.iteration}/{self.max_iterations}")
            logger.info(f"{'='*40}")
            
            # Run Qwen
            success, output = self._run_qwen(self.prompt)
            last_output = output
            
            if not success:
                logger.warning(f"Iteration {self.iteration} failed, retrying...")
                time.sleep(self.check_interval)
                continue
            
            # Check for completion using all strategies
            strategies = self._get_completion_strategies()
            
            for strategy in strategies:
                if strategy['check'](last_output):
                    completion_detected = True
                    completion_strategy = strategy['name']
                    logger.info(f"✅ Completion detected via: {strategy['name']}")
                    break
            
            # Log iteration
            self._log_iteration(self.iteration, last_output, completion_detected)
            
            if completion_detected:
                break
            
            # Check if we should continue
            if self.iteration < self.max_iterations:
                logger.info(f"Task not complete, continuing... (waiting {self.check_interval}s)")
                time.sleep(self.check_interval)
        
        # Calculate results
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        final_state = {
            'done_count': len(list(self.done_dir.glob('*.md'))),
            'needs_action_count': len(list(self.needs_action_dir.glob('*.md')))
        }
        
        result = {
            'completed': completion_detected,
            'completion_strategy': completion_strategy,
            'iterations': self.iteration,
            'max_iterations': self.max_iterations,
            'duration_seconds': duration,
            'start_state': self.task_start_state,
            'final_state': final_state,
            'progress': {
                'files_completed': final_state['done_count'] - self.task_start_state['done_count'],
                'files_remaining': final_state['needs_action_count']
            }
        }
        
        # Log final result
        logger.info("\n" + "="*60)
        if completion_detected:
            logger.info("✅ Ralph Wiggum Loop completed successfully!")
        else:
            logger.warning("⚠️ Ralph Wiggum Loop ended: max iterations reached")
        logger.info(f"Iterations: {self.iteration}/{self.max_iterations}")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Files completed: {result['progress']['files_completed']}")
        logger.info(f"Files remaining: {result['progress']['files_remaining']}")
        logger.info("="*60)
        
        return result


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Ralph Wiggum Loop - Multi-Step Task Persistence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all items in Needs_Action
  python ralph_loop.py --vault ./vault --prompt "Process all files"

  # With custom max iterations
  python ralph_loop.py --vault ./vault --prompt "Fix all bugs" --max-iterations 15

  # With completion signal
  python ralph_loop.py --vault ./vault --prompt "Generate briefing" --completion-signal "TASK_COMPLETE"
        """
    )
    
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--prompt', required=True, help='Prompt to give Qwen')
    parser.add_argument('--max-iterations', type=int, default=10, help='Maximum iterations')
    parser.add_argument('--completion-signal', help='Custom completion signal to look for')
    parser.add_argument('--check-interval', type=float, default=2.0, help='Seconds between iterations')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen without running')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("Dry run mode - would execute:")
        print(f"  Vault: {args.vault}")
        print(f"  Prompt: {args.prompt}")
        print(f"  Max iterations: {args.max_iterations}")
        print()
        print("Completion strategies:")
        print("  1. File movement detection (files moving to Done/)")
        print("  2. Promise detection (<promise>TASK_COMPLETE</promise>)")
        print("  3. Needs_Action folder empty check")
        return
    
    # Run the loop
    loop = RalphWiggumLoop(
        vault_path=args.vault,
        prompt=args.prompt,
        max_iterations=args.max_iterations,
        completion_signal=args.completion_signal,
        check_interval=args.check_interval
    )
    
    result = loop.run()
    
    # Exit with appropriate code
    sys.exit(0 if result['completed'] else 1)


if __name__ == "__main__":
    main()
