#!/usr/bin/env python3
"""
Step 6: Error Recovery & Resilience — Integration Tests

Tests:
- ErrorRecoverySystem base module (error_recovery.py)
- Graceful degradation strategies
- End-to-end orchestrator → health server HTTP flow
- Circuit breaker + retry + recovery chain
- Health check script JSON output validation
- Error escalation and quarantine flow

Run:
    python -m pytest tests/test_error_recovery_resilience.py -v
    python -m pytest tests/test_error_recovery_resilience.py -v -k "graceful"
    python -m pytest tests/test_error_recovery_resilience.py -v -k "health"
"""

import sys
import os
import json
import shutil
import tempfile
import threading
import time
import subprocess
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def temp_vault(tmp_path):
    """Create a clean temporary vault."""
    vault = tmp_path / "test_vault"
    vault.mkdir()
    for d in ['Needs_Action', 'Plans', 'Done', 'Pending_Approval',
              'Approved', 'Rejected', 'Logs', 'In_Progress', 'Briefings',
              'Logs/errors', 'Needs_Action/alerts', 'Needs_Action/quarantine']:
        (vault / d).mkdir(parents=True, exist_ok=True)
    (vault / 'Company_Handbook.md').write_text("# Company Handbook\n")
    (vault / 'Business_Goals.md').write_text("# Business Goals\n")
    (vault / 'Dashboard.md').write_text("# Dashboard\n")
    return vault


@pytest.fixture
def recovery_system(temp_vault):
    """Create an ErrorRecoverySystem instance."""
    from error_recovery import ErrorRecoverySystem
    return ErrorRecoverySystem(vault_path=str(temp_vault))


# ============================================================
# Test Group 1: ErrorRecoverySystem Base Module
# ============================================================

class TestErrorRecoverySystem:
    """Test the base ErrorRecoverySystem module (error_recovery.py)."""

    def test_initialization(self, recovery_system, temp_vault):
        """Should initialize all circuit breakers and handlers."""
        assert 'odoo' in recovery_system.circuit_breakers
        assert 'gmail' in recovery_system.circuit_breakers
        assert 'linkedin' in recovery_system.circuit_breakers
        assert 'twitter' in recovery_system.circuit_breakers
        assert 'qwen_api' in recovery_system.circuit_breakers

        assert recovery_system.retry_handler.max_attempts == 3
        assert recovery_system.retry_handler.base_delay == 1.0

        assert recovery_system.error_stats['total'] == 0

    def test_categorize_auth_error(self, recovery_system):
        """Should categorize authentication errors."""
        for msg in ['401 Unauthorized', 'token expired', 'invalid credentials', 'permission denied']:
            error = Exception(msg)
            cat = recovery_system.categorize_error(error)
            assert cat.value == 'authentication', f"Expected authentication for: {msg}"

    def test_categorize_transient_error(self, recovery_system):
        """Should categorize transient/recoverable errors."""
        for msg in ['timeout', 'rate limit exceeded', '503 Service Unavailable', 'temporary failure']:
            error = Exception(msg)
            cat = recovery_system.categorize_error(error)
            assert cat.value == 'transient', f"Expected transient for: {msg}"

    def test_categorize_data_error(self, recovery_system):
        """Should categorize data parsing errors."""
        for msg in ['corrupt file', 'invalid JSON', 'missing field', 'parse error']:
            error = Exception(msg)
            cat = recovery_system.categorize_error(error)
            assert cat.value == 'data', f"Expected data for: {msg}"

    def test_categorize_system_error(self, recovery_system):
        """Should categorize system-level errors."""
        for msg in ['disk full', 'out of memory', 'fatal crash', 'segfault']:
            error = Exception(msg)
            cat = recovery_system.categorize_error(error)
            assert cat.value == 'system', f"Expected system for: {msg}"

    def test_categorize_logic_error_default(self, recovery_system):
        """Should default to logic for unrecognized errors."""
        error = Exception('some unknown error')
        cat = recovery_system.categorize_error(error)
        assert cat.value == 'logic'

    def test_handle_error_creates_log(self, recovery_system, temp_vault):
        """Should create error log file when handling an error."""
        error = Exception('test timeout error')
        result = recovery_system.handle_error(error, {'context': 'test'})

        assert result['category'] == 'transient'
        assert result['severity'] == 'low'
        assert result['should_retry'] is True
        assert result['should_alert'] is False

        # Error log should be created
        error_files = list((temp_vault / 'Logs' / 'errors').glob('errors_*.json'))
        assert len(error_files) >= 1

        # Log should contain the error
        log_data = json.loads(error_files[-1].read_text())
        assert any('test timeout error' in entry.get('error_message', '') for entry in log_data)

    def test_handle_auth_error_escalates(self, recovery_system, temp_vault):
        """Should escalate high-severity auth errors (alert human)."""
        error = Exception('401 Unauthorized — token expired')
        result = recovery_system.handle_error(error, {'context': 'test'})

        assert result['category'] == 'authentication'
        assert result['severity'] == 'high'
        assert result['should_alert'] is True
        assert result['should_retry'] is False

        # Alert file should be created in Needs_Action/alerts
        alert_files = list((temp_vault / 'Needs_Action' / 'alerts').glob('ALERT_*.md'))
        assert len(alert_files) >= 1

    def test_handle_data_error_quarantines(self, recovery_system, temp_vault):
        """Should quarantine data errors."""
        # Create a test file to quarantine
        test_file = temp_vault / 'Needs_Action' / 'corrupted_item.md'
        test_file.write_text("# Corrupted item")

        error = Exception('corrupt JSON data — parse error')
        result = recovery_system.handle_error(error, {
            'file_path': str(test_file),
            'context': 'test'
        })

        assert result['category'] == 'data'
        assert result['severity'] == 'medium'
        assert result['should_quarantine'] is True

    def test_error_stats_accumulate(self, recovery_system):
        """Should accumulate error statistics."""
        errors = [
            Exception('timeout'),
            Exception('timeout'),
            Exception('401 Unauthorized'),
        ]
        for error in errors:
            recovery_system.handle_error(error)

        stats = recovery_system.error_stats
        assert stats['total'] == 3
        assert stats['by_category']['transient'] == 2
        assert stats['by_category']['authentication'] == 1
        assert stats['by_severity']['low'] == 2
        assert stats['by_severity']['high'] == 1

    def test_get_status_report(self, recovery_system):
        """Should return status report with all data."""
        report = recovery_system.get_status_report()

        assert 'timestamp' in report
        assert 'error_statistics' in report
        assert 'recovery_rate' in report
        assert 'circuit_breakers' in report
        assert 'recent_errors' in report

        assert 'odoo' in report['circuit_breakers']
        assert 'gmail' in report['circuit_breakers']

    def test_execute_with_circuit_breaker_success(self, recovery_system):
        """Should execute function and record success on circuit breaker."""
        call_count = [0]

        def success_func():
            call_count[0] += 1
            return "result"

        result = recovery_system.execute_with_circuit_breaker('gmail', success_func)
        assert result == "result"
        assert call_count[0] == 1

        # Circuit breaker should be closed
        breaker = recovery_system.circuit_breakers['gmail']
        assert breaker.state == 'closed'

    def test_execute_with_circuit_breaker_opens_after_failures(self, recovery_system):
        """Should open circuit breaker after threshold failures."""
        def fail_func():
            raise Exception("connection timeout")

        breaker = recovery_system.circuit_breakers['gmail']
        assert breaker.failure_threshold == 3

        # Record 3 failures — should open
        for _ in range(3):
            with pytest.raises(Exception):
                recovery_system.execute_with_circuit_breaker('gmail', fail_func)

        assert breaker.state == 'open'

        # Subsequent calls should be blocked
        from error_recovery import TransientError
        with pytest.raises(TransientError, match="Circuit breaker open"):
            recovery_system.execute_with_circuit_breaker('gmail', fail_func)

    def test_execute_with_circuit_breaker_unknown_service(self, recovery_system):
        """Should execute directly for services without circuit breakers."""
        def test_func():
            return "ok"

        result = recovery_system.execute_with_circuit_breaker('unknown_service', test_func)
        assert result == "ok"


# ============================================================
# Test Group 2: Graceful Degradation
# ============================================================

class TestGracefulDegradation:
    """Test graceful degradation strategies when services fail."""

    def test_degradation_strategy_odoo(self, recovery_system):
        """Should queue accounting actions when Odoo is down."""
        result = recovery_system.graceful_degradation('odoo')
        assert result['degraded'] is True
        assert 'Queue accounting' in result['strategy']

    def test_degradation_strategy_gmail(self, recovery_system):
        """Should queue emails locally when Gmail is down."""
        result = recovery_system.graceful_degradation('gmail')
        assert result['degraded'] is True
        assert 'Queue outgoing emails' in result['strategy']

    def test_degradation_strategy_linkedin(self, recovery_system):
        """Should save drafts when LinkedIn is down."""
        result = recovery_system.graceful_degradation('linkedin')
        assert result['degraded'] is True
        assert 'Save post drafts' in result['strategy']

    def test_degradation_strategy_qwen(self, recovery_system):
        """Should fallback to rule-based processing when Qwen is down."""
        result = recovery_system.graceful_degradation('qwen_api')
        assert result['degraded'] is True
        assert 'rule-based' in result['strategy'].lower()

    def test_degradation_with_fallback_function(self, recovery_system):
        """Should execute fallback function if provided."""
        fallback_result = {'type': 'fallback', 'status': 'ok'}

        def fallback_func():
            return fallback_result

        result = recovery_system.graceful_degradation('odoo', fallback_func)
        assert result == fallback_result

    def test_degradation_unknown_service(self, recovery_system):
        """Should handle unknown service degradation."""
        result = recovery_system.graceful_degradation('nonexistent_service')
        assert result['degraded'] is True
        assert 'Manual intervention' in result['strategy']


# ============================================================
# Test Group 3: Retry Handler
# ============================================================

class TestRetryHandler:
    """Test retry with exponential backoff."""

    def test_retry_succeeds_on_first_attempt(self):
        """Should return immediately on success."""
        from error_recovery import RetryHandler

        handler = RetryHandler(max_attempts=3, base_delay=0.01)
        call_count = [0]

        def success_func():
            call_count[0] += 1
            return "success"

        result = handler.execute_with_retry(success_func)
        assert result == "success"
        assert call_count[0] == 1

    def test_retry_succeeds_after_failures(self):
        """Should retry and eventually succeed."""
        from error_recovery import RetryHandler, TransientError

        handler = RetryHandler(max_attempts=3, base_delay=0.01)
        call_count = [0]

        def flaky_func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise TransientError("temporary failure")
            return "success"

        result = handler.execute_with_retry(flaky_func)
        assert result == "success"
        assert call_count[0] == 3

    def test_retry_raises_after_max_attempts(self):
        """Should raise after exhausting all attempts."""
        from error_recovery import RetryHandler, TransientError

        handler = RetryHandler(max_attempts=3, base_delay=0.01)
        call_count = [0]

        def always_fail():
            call_count[0] += 1
            raise TransientError("persistent failure")

        with pytest.raises(TransientError):
            handler.execute_with_retry(always_fail)

        assert call_count[0] == 3

    def test_non_transient_errors_not_retried(self):
        """Should not retry non-transient exceptions."""
        from error_recovery import RetryHandler

        handler = RetryHandler(max_attempts=3, base_delay=0.01)
        call_count = [0]

        def auth_error():
            call_count[0] += 1
            raise Exception("401 Unauthorized")

        with pytest.raises(Exception, match="401"):
            handler.execute_with_retry(auth_error)

        assert call_count[0] == 1  # Only called once


# ============================================================
# Test Group 4: End-to-End Orchestrator → Health Server Flow
# ============================================================

class TestOrchestratorHealthFlow:
    """Test orchestrator properly updates health server state."""

    def test_orchestrator_updates_health_state_on_start(self, temp_vault):
        """Orchestrator should set health state running on start."""
        os.environ['DRY_RUN'] = 'true'
        os.environ['VAULT_PATH'] = str(temp_vault)

        from orchestrator import Orchestrator
        from health_server import HealthServer

        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        # Health server should be initialized
        assert orch.health_server is not None
        assert orch.health_state is not None

        # Simulate orchestrator start
        if orch.health_state:
            orch.health_state.set_running(True)
            orch.health_state.update_heartbeat()

        assert orch.health_state.orchestrator_running is True
        assert orch.health_state.last_heartbeat is not None

    def test_health_server_reflects_orchestrator_state(self, temp_vault):
        """Health server endpoint should reflect orchestrator state changes."""
        from health_server import HealthServer, HealthState

        state = HealthState()
        state.vault_path = str(temp_vault)
        state.set_running(True)
        state.update_heartbeat()
        state.needs_action_count = 5
        state.pending_approval_count = 2
        state.done_count = 10

        report = state.to_status_dict()

        assert report['status'] == 'healthy'
        assert report['orchestrator']['running'] is True
        assert report['vault']['needs_action'] == 5
        assert report['vault']['pending_approval'] == 2
        assert report['vault']['done'] == 10

    def test_health_server_becomes_unhealthy_when_orchestrator_stops(self, temp_vault):
        """Health server should report unhealthy when orchestrator stops."""
        from health_server import HealthServer, HealthState

        state = HealthState()
        state.vault_path = str(temp_vault)
        state.set_running(True)
        state.update_heartbeat()

        assert state._is_healthy() is True

        # Stop orchestrator
        state.set_running(False)

        assert state._is_healthy() is False
        report = state.to_status_dict()
        assert report['status'] == 'unhealthy'

    def test_health_server_http_basic_endpoint(self, temp_vault):
        """Health server basic endpoint should respond with 200 when healthy."""
        from health_server import HealthServer

        server = HealthServer(vault_path=str(temp_vault), port=9090)
        server.state.set_running(True)
        server.state.update_heartbeat()
        server.start()
        time.sleep(0.5)

        try:
            import urllib.request
            url = "http://127.0.0.1:9090/health"
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode())

            assert 'status' in data
            assert 'timestamp' in data
            assert response.status == 200
        finally:
            server.stop()

    def test_health_server_http_status_endpoint(self, temp_vault):
        """Health server status endpoint should return full report."""
        from health_server import HealthServer

        server = HealthServer(vault_path=str(temp_vault), port=9091)
        server.state.set_running(True)
        server.state.update_heartbeat()
        server.state.needs_action_count = 3
        server.start()
        time.sleep(0.5)

        try:
            import urllib.request
            url = "http://127.0.0.1:9091/health/status"
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode())

            assert data['status'] == 'healthy'
            assert data['orchestrator']['running'] is True
            assert data['vault']['needs_action'] == 3
        finally:
            server.stop()

    def test_health_server_circuit_breakers_endpoint(self, temp_vault):
        """Circuit breakers endpoint should return breaker states."""
        from health_server import HealthServer

        server = HealthServer(vault_path=str(temp_vault), port=9092)
        server.state.circuit_breakers = {
            'qwen_api': 'closed',
            'gmail': 'closed',
            'odoo': 'open',
        }
        server.start()
        time.sleep(0.5)

        try:
            import urllib.request
            url = "http://127.0.0.1:9092/health/circuit-breakers"
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode())

            assert 'circuit_breakers' in data
            assert data['circuit_breakers']['qwen_api'] == 'closed'
            assert data['circuit_breakers']['odoo'] == 'open'
        finally:
            server.stop()


# ============================================================
# Test Group 5: Full Error → Recovery → Done Chain
# ============================================================

class TestErrorRecoveryChain:
    """Test complete error → circuit breaker → retry → recovery chain."""

    def test_full_chain_transient_error_recovers(self, temp_vault):
        """Transient error should be retried and recover through retry handler."""
        from error_recovery import RetryHandler, TransientError

        handler = RetryHandler(max_attempts=5, base_delay=0.01)
        call_count = [0]

        def flaky_api():
            call_count[0] += 1
            if call_count[0] < 3:
                raise TransientError("503 Service Unavailable")
            return {"status": "ok"}

        # Should retry until success on 3rd attempt
        result = handler.execute_with_retry(flaky_api)

        assert result == {"status": "ok"}
        assert call_count[0] == 3

    def test_full_chain_auth_error_no_retry(self, temp_vault):
        """Auth error should not be retried — should escalate."""
        from error_recovery_integration import _categorize_error, ErrorCategory

        error = Exception("401 Unauthorized: token expired")
        category = _categorize_error(error)

        assert category == ErrorCategory.AUTHENTICATION
        # Auth errors should trigger escalation, not retry

    def test_full_chain_system_error_no_retry(self, temp_vault):
        """System error should not be retried — should alert."""
        from error_recovery_integration import _categorize_error, ErrorCategory

        error = Exception("disk full — cannot write")
        category = _categorize_error(error)

        assert category == ErrorCategory.SYSTEM

    def test_full_chain_quarantine_flow(self, temp_vault):
        """Data error should quarantine the item."""
        from error_recovery_integration import RecoveryContext

        ctx = RecoveryContext(temp_vault)

        # Create item to quarantine
        item = temp_vault / 'Needs_Action' / 'corrupt_data.md'
        item.write_text("# Corrupt data")

        ctx.quarantine_item(item, "Repeated JSON parse failure")

        # Item should be moved to quarantine
        assert not item.exists()

        quarantine_files = list((temp_vault / 'Needs_Action' / 'quarantine').glob('*quarantined*.md'))
        assert len(quarantine_files) >= 1

        # Quarantine file should have metadata
        content = quarantine_files[0].read_text()
        assert 'type: quarantined' in content
        assert 'corrupt_data.md' in content
        assert 'Repeated JSON parse failure' in content


# ============================================================
# Test Group 6: Health Check Script Output Validation
# ============================================================

class TestHealthCheckScript:
    """Validate the health_check.sh script output."""

    def test_health_check_script_exists(self):
        """Health check script should exist and be executable."""
        project_root = Path(__file__).parent.parent
        script_path = project_root / 'scripts' / 'health_check.sh'

        assert script_path.exists()
        assert os.access(script_path, os.X_OK)

    def test_health_check_runs_successfully(self):
        """Health check script should run and produce output."""
        project_root = Path(__file__).parent.parent
        env = os.environ.copy()
        env['VAULT_PATH'] = str(project_root / 'vault')

        result = subprocess.run(
            [str(project_root / 'scripts' / 'health_check.sh')],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_root),
            env=env,
        )

        # Should exit with 0 (healthy) or 1 (degraded but expected)
        assert result.returncode in (0, 1), f"Unexpected exit code: {result.returncode}\n{result.stderr}"

        # Output should contain key sections
        output = result.stdout
        assert 'Health Check Validation' in output
        assert 'Vault Directories' in output
        assert 'Disk Space' in output
        assert 'Python Environment' in output
        assert 'MCP Servers' in output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
