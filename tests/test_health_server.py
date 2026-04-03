"""
Tests for Health Check Server.

Covers: HealthState, HTTP endpoints, health determination logic,
server lifecycle, and integration with orchestrator.
"""

import json
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from health_server import HealthServer, HealthState, HealthRequestHandler


class TestHealthState:
    """Tests for HealthState shared state object."""

    def test_default_values(self):
        state = HealthState()
        assert state.orchestrator_running is False
        assert state.ralph_mode_active is False
        assert state.ralph_iterations == 0
        assert state.needs_action_count == 0
        assert state.last_error is None
        assert state.started_at is not None

    def test_update_heartbeat(self):
        state = HealthState()
        assert state.last_heartbeat is None

        state.update_heartbeat()
        assert state.last_heartbeat is not None

        # Should update to current time
        before = datetime.now().isoformat()
        state.update_heartbeat()
        after = datetime.now().isoformat()
        assert before <= state.last_heartbeat <= after

    def test_set_running(self):
        state = HealthState()
        state.set_running(True)
        assert state.orchestrator_running is True

        state.set_running(False)
        assert state.orchestrator_running is False

    def test_set_and_clear_error(self):
        state = HealthState()
        state.set_error("Connection timeout")
        assert state.last_error == "Connection timeout"
        assert state.last_error_time is not None

        state.clear_error()
        assert state.last_error is None
        assert state.last_error_time is None

    def test_is_healthy_when_running_and_recent_heartbeat(self):
        state = HealthState()
        state.set_running(True)
        state.update_heartbeat()
        assert state._is_healthy() is True

    def test_is_unhealthy_when_not_running(self):
        state = HealthState()
        state.update_heartbeat()
        assert state._is_healthy() is False

    def test_is_unhealthy_when_stale_heartbeat(self):
        state = HealthState()
        state.set_running(True)
        # Simulate heartbeat from 10 minutes ago
        old_time = (datetime.now() - timedelta(minutes=10)).isoformat()
        state.last_heartbeat = old_time
        assert state._is_healthy() is False

    def test_is_unhealthy_when_critical_cb_open(self):
        state = HealthState()
        state.set_running(True)
        state.update_heartbeat()
        state.circuit_breakers = {"qwen_api": "open"}
        assert state._is_healthy() is False

    def test_is_unhealthy_when_gmail_cb_open(self):
        state = HealthState()
        state.set_running(True)
        state.update_heartbeat()
        state.circuit_breakers = {"gmail": "open", "qwen_api": "closed"}
        assert state._is_healthy() is False

    def test_is_healthy_when_non_critical_cb_open(self):
        state = HealthState()
        state.set_running(True)
        state.update_heartbeat()
        state.circuit_breakers = {"linkedin": "open", "twitter": "open"}
        assert state._is_healthy() is True

    def test_status_report_structure(self):
        state = HealthState()
        state.set_running(True)
        state.vault_path = "/test/vault"
        state.needs_action_count = 5
        state.pending_approval_count = 2
        state.approved_count = 1
        state.done_count = 10
        state.circuit_breakers = {"qwen_api": "closed"}
        state.watchers = {"gmail": "running"}

        report = state.to_status_dict()

        assert "status" in report
        assert "timestamp" in report
        assert "started_at" in report
        assert "orchestrator" in report
        assert "vault" in report
        assert "watchers" in report
        assert "circuit_breakers" in report

        assert report["vault"]["needs_action"] == 5
        assert report["vault"]["pending_approval"] == 2
        assert report["vault"]["approved"] == 1
        assert report["vault"]["done"] == 10
        assert report["orchestrator"]["running"] is True


class TestHealthServerLifecycle:
    """Tests for HealthServer start/stop lifecycle."""

    def test_start_and_stop(self, temp_vault):
        """Server should start and stop cleanly."""
        server = HealthServer(str(temp_vault), port=18080)
        server.start()

        assert server.is_running() is True

        server.stop()
        time.sleep(0.1)  # Allow thread to finish
        assert server.is_running() is False

    def test_server_responds_to_http(self, temp_vault):
        """Running server should respond to HTTP requests."""
        server = HealthServer(str(temp_vault), port=18081)
        server.state.set_running(True)
        server.state.update_heartbeat()
        server.start()
        time.sleep(0.2)  # Allow server to bind

        try:
            url = "http://127.0.0.1:18081/health"
            try:
                with urllib.request.urlopen(url, timeout=2) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    assert "status" in data
            except urllib.error.HTTPError as e:
                # Even 503 is a valid response
                data = json.loads(e.read().decode("utf-8"))
                assert "status" in data
        finally:
            server.stop()

    def test_server_on_used_port_fails_gracefully(self, temp_vault):
        """Should log warning when port is already in use."""
        # Start first server
        server1 = HealthServer(str(temp_vault), port=18082)
        server1.start()
        time.sleep(0.2)

        try:
            # Second server on same port should handle gracefully
            server2 = HealthServer(str(temp_vault), port=18082)
            server2.start()  # Should log warning, not crash
            assert server2.is_running() is False
        finally:
            server1.stop()


def _http_get(port, path):
    """Make HTTP GET request and return (status_code, parsed_json)."""
    url = f"http://127.0.0.1:{port}{path}"
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


class TestHealthEndpoints:
    """Tests for all HTTP endpoints."""

    @pytest.fixture
    def running_server(self, temp_vault):
        """Start a health server with a populated state."""
        server = HealthServer(str(temp_vault), port=18083)
        server.state.set_running(True)
        server.state.update_heartbeat()
        server.state.needs_action_count = 3
        server.state.done_count = 7
        server.state.circuit_breakers = {
            "qwen_api": "closed",
            "gmail": "closed",
            "odoo": "closed",
        }
        server.state.watchers = {
            "gmail-watcher": "running",
            "whatsapp-watcher": "running",
        }
        server.start()
        time.sleep(0.2)

        yield server

        server.stop()

    def test_health_basic(self, running_server):
        """GET /health should return 200 with status."""
        status, data = _http_get(18083, "/health")
        assert status == 200
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_health_ready(self, running_server):
        """GET /health/ready should return 200 when ready."""
        status, data = _http_get(18083, "/health/ready")
        assert status == 200
        assert data["status"] == "ready"
        assert data["checks"]["orchestrator_running"] is True
        assert data["checks"]["vault_accessible"] is True
        assert data["checks"]["circuit_breakers"] is True

    def test_health_live(self, running_server):
        """GET /health/live should always return 200."""
        status, data = _http_get(18083, "/health/live")
        assert status == 200
        assert data["status"] == "alive"

    def test_health_status_full(self, running_server):
        """GET /health/status should return complete report."""
        status, data = _http_get(18083, "/health/status")
        assert status == 200
        assert data["orchestrator"]["running"] is True
        assert data["vault"]["needs_action"] == 3
        assert data["vault"]["done"] == 7
        assert "qwen_api" in data["circuit_breakers"]
        assert "gmail-watcher" in data["watchers"]

    def test_health_watchers(self, running_server):
        """GET /health/watchers should return watcher summary."""
        status, data = _http_get(18083, "/health/watchers")
        assert status == 200
        assert "gmail-watcher" in data["watchers"]
        assert "whatsapp-watcher" in data["watchers"]

    def test_health_circuit_breakers(self, running_server):
        """GET /health/circuit-breakers should return CB states."""
        status, data = _http_get(18083, "/health/circuit-breakers")
        assert status == 200
        assert data["circuit_breakers"]["qwen_api"] == "closed"
        assert data["circuit_breakers"]["gmail"] == "closed"

    def test_health_404_for_unknown_endpoint(self, running_server):
        """Unknown endpoints should return 404."""
        status, data = _http_get(18083, "/unknown")
        assert status == 404
        assert "error" in data
        assert "available_endpoints" in data

    def test_health_returns_503_when_unhealthy(self, temp_vault):
        """Should return 503 when system is unhealthy."""
        server = HealthServer(str(temp_vault), port=18084)
        # Don't set running — should be unhealthy
        server.start()
        time.sleep(0.2)

        try:
            status, data = _http_get(18084, "/health")
            assert status == 503
            assert data["status"] == "unhealthy"
        finally:
            server.stop()

    def test_health_ready_returns_503_when_not_ready(self, temp_vault):
        """Readiness should fail when orchestrator not running."""
        server = HealthServer(str(temp_vault), port=18085)
        server.start()
        time.sleep(0.2)

        try:
            status, data = _http_get(18085, "/health/ready")
            assert status == 503
            assert data["status"] == "not_ready"
        finally:
            server.stop()

    def test_no_cache_header(self, running_server):
        """Responses should include Cache-Control: no-store."""
        url = "http://127.0.0.1:18083/health"
        with urllib.request.urlopen(url, timeout=2) as resp:
            assert resp.headers.get("Cache-Control") == "no-store"


class TestHealthServerNoLogging:
    """Tests to verify health server doesn't pollute stderr."""

    def test_handler_suppresses_default_logging(self):
        """Request handler should override log_message to suppress stderr output."""
        handler = HealthRequestHandler.__dict__["log_message"]
        # Should be our override, not the base class method
        assert handler is not BaseHTTPRequestHandler.log_message

    def test_health_state_is_property(self):
        """health_state should be a property accessing server.health_state."""
        assert isinstance(
            HealthRequestHandler.__dict__["health_state"], property
        )
