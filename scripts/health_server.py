"""
Health Check Server for Personal AI Employee

Provides HTTP endpoints for monitoring the health of the orchestrator,
watchers, and overall system status. Designed for use with PM2, cron,
or external monitoring tools (Uptime Kuma, Healthchecks, etc.).

Usage:
    # In orchestrator.py:
    from health_server import HealthServer

    server = HealthServer(vault_path, port=8080)
    server.start()  # Runs as daemon thread

Endpoints:
    GET /health           - Basic liveness check (200 OK)
    GET /health/ready     - Readiness: all critical services healthy
    GET /health/live      - Liveness: orchestrator is running
    GET /health/status    - Full system status report (JSON)

    GET /health/watchers  - Watcher status summary
    GET /health/circuit-breakers  - Circuit breaker states

Example:
    $ curl http://localhost:8080/health
    {"status": "healthy", "timestamp": "2026-04-03T10:00:00"}

    $ curl http://localhost:8080/health/ready
    {"status": "ready", "checks": {"vault": true, "circuit_breakers": true}}

    $ curl http://localhost:8080/health/status
    {"orchestrator": {...}, "watchers": {...}, "circuit_breakers": {...}}
"""

import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger("HealthServer")


class HealthState:
    """
    Shared state between the orchestrator and health server.

    The orchestrator updates this state, and the health server
    reads it to serve HTTP responses.
    """

    def __init__(self):
        self.started_at = datetime.now().isoformat()
        self.last_heartbeat = None
        self.orchestrator_running = False
        self.ralph_mode_active = False
        self.ralph_iterations = 0
        self.needs_action_count = 0
        self.pending_approval_count = 0
        self.approved_count = 0
        self.done_count = 0
        self.vault_path: Optional[str] = None
        self.watchers: Dict[str, Any] = {}
        self.circuit_breakers: Dict[str, Any] = {}
        self.last_error = None
        self.last_error_time = None
        self.uptime_seconds = 0

    def update_heartbeat(self):
        """Called by orchestrator on each loop iteration."""
        self.last_heartbeat = datetime.now().isoformat()

    def set_running(self, running: bool):
        self.orchestrator_running = running

    def set_error(self, error: str):
        self.last_error = error
        self.last_error_time = datetime.now().isoformat()

    def clear_error(self):
        self.last_error = None
        self.last_error_time = None

    def to_status_dict(self) -> Dict[str, Any]:
        """Generate full status report."""
        return {
            "status": "healthy" if self._is_healthy() else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "started_at": self.started_at,
            "last_heartbeat": self.last_heartbeat,
            "orchestrator": {
                "running": self.orchestrator_running,
                "ralph_mode": self.ralph_mode_active,
                "ralph_iterations": self.ralph_iterations,
                "last_error": self.last_error,
                "last_error_time": self.last_error_time,
            },
            "vault": {
                "path": self.vault_path,
                "needs_action": self.needs_action_count,
                "pending_approval": self.pending_approval_count,
                "approved": self.approved_count,
                "done": self.done_count,
            },
            "watchers": self.watchers,
            "circuit_breakers": self.circuit_breakers,
        }

    def _is_healthy(self) -> bool:
        """Overall health determination."""
        if not self.orchestrator_running:
            return False

        # Check for stale heartbeat (no heartbeat in last 5 minutes)
        if self.last_heartbeat:
            last_hb = datetime.fromisoformat(self.last_heartbeat)
            age = (datetime.now() - last_hb).total_seconds()
            if age > 300:  # 5 minutes
                return False

        # Check if any critical circuit breaker is open
        for name, state in self.circuit_breakers.items():
            if name in ("qwen_api", "gmail") and state == "open":
                return False

        return True


class HealthRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health check endpoints."""

    def log_message(self, format, *args):
        """Suppress default stderr logging."""
        logger.debug(f"Health HTTP: {format % args}")

    @property
    def health_state(self) -> Optional[HealthState]:
        """Access health state from the server instance."""
        return getattr(self.server, "health_state", None)

    def do_GET(self):
        """Handle GET requests to health endpoints."""
        path = self.path.rstrip("/")

        if path == "/health" or path == "":
            self._serve_basic_health()
        elif path == "/health/ready":
            self._serve_readiness()
        elif path == "/health/live":
            self._serve_liveness()
        elif path == "/health/status":
            self._serve_full_status()
        elif path == "/health/watchers":
            self._serve_watchers()
        elif path == "/health/circuit-breakers":
            self._serve_circuit_breakers()
        else:
            self._send_json(404, {"error": "Not found", "available_endpoints": [
                "/health", "/health/ready", "/health/live",
                "/health/status", "/health/watchers", "/health/circuit-breakers",
            ]})

    def _serve_basic_health(self):
        """Basic health check — returns 200 if system is up."""
        state = self.health_state
        if state and state._is_healthy():
            self._send_json(200, {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
            })
        else:
            self._send_json(503, {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
            })

    def _serve_readiness(self):
        """Readiness check — can this instance handle traffic?"""
        state = self.health_state
        vault_ok = state.vault_path and Path(state.vault_path).exists()
        cb_ok = all(
            s != "open"
            for name, s in state.circuit_breakers.items()
            if name in ("qwen_api", "gmail")
        )

        ready = bool(state.orchestrator_running and vault_ok and cb_ok)

        status_code = 200 if ready else 503
        self._send_json(status_code, {
            "status": "ready" if ready else "not_ready",
            "checks": {
                "orchestrator_running": state.orchestrator_running,
                "vault_accessible": bool(vault_ok),
                "circuit_breakers": bool(cb_ok),
            },
        })

    def _serve_liveness(self):
        """Liveness check — is the process alive?"""
        # If we get here, the process is alive (HTTP responded)
        self._send_json(200, {
            "status": "alive",
            "timestamp": datetime.now().isoformat(),
        })

    def _serve_full_status(self):
        """Full system status — detailed JSON report."""
        state = self.health_state
        if state:
            self._send_json(200, state.to_status_dict())
        else:
            self._send_json(500, {"error": "Health state not available"})

    def _serve_watchers(self):
        """Watcher status summary."""
        state = self.health_state
        self._send_json(200, {
            "watchers": state.watchers if state else {},
            "timestamp": datetime.now().isoformat(),
        })

    def _serve_circuit_breakers(self):
        """Circuit breaker states."""
        state = self.health_state
        self._send_json(200, {
            "circuit_breakers": state.circuit_breakers if state else {},
            "timestamp": datetime.now().isoformat(),
        })

    def _send_json(self, status_code: int, data: dict):
        """Send a JSON response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))


class HealthServer:
    """
    HTTP health check server that runs as a background daemon thread.

    Usage:
        server = HealthServer(vault_path="./vault", port=8080)
        server.start()
        # Later: server.stop()
    """

    def __init__(self, vault_path: str, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self.state = HealthState()
        self.state.vault_path = vault_path
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start the health server as a daemon thread."""
        try:
            self._server = HTTPServer((self.host, self.port), HealthRequestHandler)
            # Store state on the server instance so the handler can access it
            # via `self.server.health_state`
            self._server.health_state = self.state  # type: ignore[attr-defined]

            self._thread = threading.Thread(
                target=self._server.serve_forever,
                daemon=True,
                name="HealthServer",
            )
            self._thread.start()
            logger.info(f"✅ Health server started on http://{self.host}:{self.port}")
        except OSError as e:
            if "Address already in use" in str(e):
                logger.warning(
                    f"⚠️ Health server port {self.port} in use — "
                    f"check if another process is using it, or change port"
                )
            else:
                logger.error(f"Failed to start health server: {e}")

    def stop(self):
        """Stop the health server."""
        if self._server:
            self._server.shutdown()
            logger.info("Health server stopped")

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()
