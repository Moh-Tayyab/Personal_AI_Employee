#!/usr/bin/env python3
"""
Error Recovery & Graceful Degradation System (Gold Tier)

Provides comprehensive error handling, recovery strategies, and graceful
degradation for the Personal AI Employee system.

Features:
- Automatic retry with exponential backoff
- Circuit breaker pattern
- Error categorization and handling
- Graceful degradation when services unavailable
- Error logging and alerting
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from functools import wraps
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Error_Recovery")


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for handling."""
    TRANSIENT = "transient"  # Network timeout, rate limit
    AUTHENTICATION = "authentication"  # Expired token, invalid credentials
    LOGIC = "logic"  # AI misinterpretation, validation error
    DATA = "data"  # Corrupted file, missing field
    SYSTEM = "system"  # Crash, disk full, out of memory


class CircuitBreaker:
    """
    Circuit Breaker pattern implementation.
    
    Prevents cascading failures by stopping requests to failing services.
    """
    
    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        
    def record_success(self):
        """Record a successful call."""
        self.failure_count = 0
        self.state = "closed"
        logger.info(f"Circuit breaker '{self.name}' closed (reset)")
        
    def record_failure(self):
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker '{self.name}' opened after {self.failure_count} failures")
            
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == "closed":
            return True
            
        if self.state == "open":
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.state = "half-open"
                    logger.info(f"Circuit breaker '{self.name}' half-open (testing)")
                    return True
            return False
            
        # half-open: allow one test call
        return True


class RetryHandler:
    """
    Retry handler with exponential backoff.
    """
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except TransientError as e:
                last_exception = e
                if attempt == self.max_attempts:
                    raise
                    
                delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
                logger.warning(f"Attempt {attempt} failed, retrying in {delay:.1f}s: {e}")
                time.sleep(delay)
            except Exception as e:
                # Non-transient errors are not retried
                raise
                
        raise last_exception


class TransientError(Exception):
    """Exception for transient/recoverable errors."""
    pass


class ErrorRecoverySystem:
    """
    Main error recovery system for Personal AI Employee.
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.errors_dir = self.vault_path / 'Logs' / 'errors'
        self.errors_dir.mkdir(parents=True, exist_ok=True)
        
        # Circuit breakers for different services
        self.circuit_breakers = {
            'odoo': CircuitBreaker('odoo', failure_threshold=5, recovery_timeout=60),
            'gmail': CircuitBreaker('gmail', failure_threshold=3, recovery_timeout=30),
            'linkedin': CircuitBreaker('linkedin', failure_threshold=3, recovery_timeout=30),
            'twitter': CircuitBreaker('twitter', failure_threshold=3, recovery_timeout=30),
            'qwen_api': CircuitBreaker('qwen_api', failure_threshold=5, recovery_timeout=60)
        }
        
        # Retry handler
        self.retry_handler = RetryHandler(max_attempts=3, base_delay=1.0)
        
        # Error statistics
        self.error_stats = {
            'total': 0,
            'by_category': {},
            'by_severity': {},
            'recovered': 0,
            'escalated': 0
        }
        
    def categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize an error for appropriate handling."""
        error_str = str(error).lower()
        
        # Authentication errors
        if any(kw in error_str for kw in ['auth', 'token', 'credential', 'permission', '401', '403']):
            return ErrorCategory.AUTHENTICATION
            
        # Transient errors
        if any(kw in error_str for kw in ['timeout', 'rate limit', 'temporary', 'retry', '503', '504']):
            return ErrorCategory.TRANSIENT
            
        # Data errors
        if any(kw in error_str for kw in ['corrupt', 'invalid', 'missing', 'parse', 'format']):
            return ErrorCategory.DATA
            
        # System errors
        if any(kw in error_str for kw in ['disk', 'memory', 'crash', 'fatal', 'segfault']):
            return ErrorCategory.SYSTEM
            
        # Default to logic error
        return ErrorCategory.LOGIC
    
    def get_severity(self, category: ErrorCategory, context: Dict = None) -> ErrorSeverity:
        """Determine error severity."""
        if category == ErrorCategory.SYSTEM:
            return ErrorSeverity.CRITICAL
        if category == ErrorCategory.AUTHENTICATION:
            return ErrorSeverity.HIGH
        if category == ErrorCategory.DATA:
            return ErrorSeverity.MEDIUM
        if category == ErrorCategory.TRANSIENT:
            return ErrorSeverity.LOW
        return ErrorSeverity.MEDIUM
    
    def handle_error(self, error: Exception, context: Dict = None) -> Dict[str, Any]:
        """
        Handle an error with appropriate recovery strategy.
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
        
        Returns:
            Dict with handling result and recommendations
        """
        category = self.categorize_error(error)
        severity = self.get_severity(category, context)
        
        # Update statistics
        self.error_stats['total'] += 1
        cat_key = category.value
        self.error_stats['by_category'][cat_key] = self.error_stats['by_category'].get(cat_key, 0) + 1
        
        sev_key = severity.value
        self.error_stats['by_severity'][sev_key] = self.error_stats['by_severity'].get(sev_key, 0) + 1
        
        # Log error
        error_log = self._log_error(error, category, severity, context)
        
        # Determine handling strategy
        result = {
            'error': str(error),
            'category': category.value,
            'severity': severity.value,
            'log_file': str(error_log),
            'action': self._get_recovery_action(category, severity),
            'should_retry': category == ErrorCategory.TRANSIENT,
            'should_alert': severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL],
            'should_quarantine': category == ErrorCategory.DATA
        }
        
        # Execute recovery action
        if result['should_retry']:
            result['recovery_attempted'] = True
        elif result['should_alert']:
            self._alert_human(error, category, context)
            self.error_stats['escalated'] += 1
        elif result['should_quarantine']:
            self._quarantine_item(context)
            
        return result
    
    def _get_recovery_action(self, category: ErrorCategory, severity: ErrorSeverity) -> str:
        """Get recommended recovery action."""
        actions = {
            ErrorCategory.TRANSIENT: "Retry with exponential backoff",
            ErrorCategory.AUTHENTICATION: "Refresh credentials and retry",
            ErrorCategory.LOGIC: "Review and correct input data",
            ErrorCategory.DATA: "Quarantine item and alert human",
            ErrorCategory.SYSTEM: "Restart service and alert human"
        }
        return actions.get(category, "Manual review required")
    
    def _log_error(self, error: Exception, category: ErrorCategory, severity: ErrorSeverity, context: Dict = None) -> Path:
        """Log error to file."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.errors_dir / f"errors_{today}.json"
        
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'category': category.value,
            'severity': severity.value,
            'context': context or {}
        }
        
        # Read existing errors or create new list
        if log_file.exists():
            try:
                errors = json.loads(log_file.read_text())
                if not isinstance(errors, list):
                    errors = [errors]
            except:
                errors = []
        else:
            errors = []
        
        errors.append(error_entry)
        log_file.write_text(json.dumps(errors, indent=2))
        
        return log_file
    
    def _alert_human(self, error: Exception, category: ErrorCategory, context: Dict = None):
        """Alert human about critical error."""
        # Create alert file in Needs_Action
        alerts_dir = self.vault_path / 'Needs_Action' / 'alerts'
        alerts_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        alert_file = alerts_dir / f'ALERT_{category.value}_{timestamp}.md'
        
        alert_content = f"""---
type: error_alert
category: {category.value}
created: {datetime.now().isoformat()}
severity: high
---

# Error Alert: {category.value.title()} Error

## Error Details
- **Type:** {type(error).__name__}
- **Message:** {str(error)}
- **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Context
{json.dumps(context or {}, indent=2)}

## Required Action
Please review and resolve this error. Check the error logs for more details.

## Log Location
`{self.errors_dir}/errors_{datetime.now().strftime('%Y-%m-%d')}.json`
"""
        alert_file.write_text(alert_content)
        logger.warning(f"Alert created: {alert_file}")
    
    def _quarantine_item(self, context: Dict = None):
        """Quarantine problematic item."""
        if not context:
            return
            
        quarantine_dir = self.vault_path / 'Quarantine'
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        
        # Move or copy problematic file
        source_path = context.get('file_path')
        if source_path and Path(source_path).exists():
            dest_path = quarantine_dir / Path(source_path).name
            try:
                import shutil
                shutil.copy2(source_path, dest_path)
                logger.info(f"Quarantined: {source_path} -> {dest_path}")
            except Exception as e:
                logger.error(f"Failed to quarantine: {e}")
    
    def execute_with_circuit_breaker(self, service: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        breaker = self.circuit_breakers.get(service)
        
        if not breaker:
            # No circuit breaker for this service, execute directly
            return func(*args, **kwargs)
        
        if not breaker.can_execute():
            logger.warning(f"Circuit breaker '{service}' is open, skipping execution")
            raise TransientError(f"Circuit breaker open for {service}")
        
        try:
            result = func(*args, **kwargs)
            breaker.record_success()
            return result
        except Exception as e:
            breaker.record_failure()
            raise
    
    def graceful_degradation(self, failed_service: str, fallback_func: Callable = None, *args, **kwargs) -> Any:
        """
        Implement graceful degradation when a service fails.
        
        Args:
            failed_service: Name of the failed service
            fallback_func: Optional fallback function to execute
            *args, **kwargs: Arguments for fallback function
        
        Returns:
            Result from fallback or degraded response
        """
        logger.warning(f"Service '{failed_service}' failed, applying graceful degradation")
        
        degradation_strategies = {
            'odoo': "Queue accounting actions locally, process when restored",
            'gmail': "Queue outgoing emails locally, process when restored",
            'linkedin': "Save post drafts locally, publish when restored",
            'twitter': "Save tweet drafts locally, publish when restored",
            'qwen_api': "Use rule-based fallback processing"
        }
        
        strategy = degradation_strategies.get(failed_service, "Manual intervention required")
        logger.info(f"Degradation strategy: {strategy}")
        
        # Execute fallback if provided
        if fallback_func:
            try:
                return fallback_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Fallback also failed: {e}")
        
        # Return degraded response
        return {
            'degraded': True,
            'service': failed_service,
            'strategy': strategy,
            'message': f"Service {failed_service} unavailable. {strategy}"
        }
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get error recovery system status report."""
        # Calculate recovery rate
        total = self.error_stats['total']
        recovered = self.error_stats['recovered']
        recovery_rate = (recovered / total * 100) if total > 0 else 0
        
        # Get circuit breaker states
        breaker_states = {
            name: breaker.state 
            for name, breaker in self.circuit_breakers.items()
        }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'error_statistics': self.error_stats,
            'recovery_rate': f"{recovery_rate:.1f}%",
            'circuit_breakers': breaker_states,
            'recent_errors': self._get_recent_errors()
        }
    
    def _get_recent_errors(self, count: int = 10) -> List[Dict]:
        """Get recent errors from logs."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.errors_dir / f"errors_{today}.json"
        
        if not log_file.exists():
            return []
        
        try:
            errors = json.loads(log_file.read_text())
            if isinstance(errors, list):
                return errors[-count:]
        except:
            pass
        
        return []


# Decorator for automatic error handling
def with_error_recovery(vault_path: str = './vault', service: str = None):
    """
    Decorator for automatic error recovery.
    
    Usage:
        @with_error_recovery(vault_path='./vault', service='odoo')
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            recovery = ErrorRecoverySystem(vault_path)
            
            try:
                if service:
                    return recovery.execute_with_circuit_breaker(service, func, *args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                result = recovery.handle_error(e, {
                    'function': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                })
                
                if result['should_retry']:
                    # Retry once
                    try:
                        return func(*args, **kwargs)
                    except Exception as retry_error:
                        recovery.handle_error(retry_error, result['context'])
                        raise
                
                raise
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test error recovery system
    recovery = ErrorRecoverySystem('./vault')
    
    print("Error Recovery System Status:")
    print(json.dumps(recovery.get_status_report(), indent=2))
