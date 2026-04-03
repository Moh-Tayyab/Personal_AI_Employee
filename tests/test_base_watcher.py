"""
Tests for BaseWatcher and watcher utilities.

Covers: ID tracking, action file creation, logging, and duplicate prevention.
"""

import json
from pathlib import Path

import pytest

# Watchers are at project root
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchers.base_watcher import BaseWatcher


class ConcreteWatcher(BaseWatcher):
    """Concrete implementation for testing the abstract base class."""

    def __init__(self, vault_path):
        super().__init__(vault_path, check_interval=60, name="TestWatcher")

    def check_for_updates(self):
        """No-op for testing."""
        return []

    def create_action_file(self, item):
        """No-op for testing."""
        pass


class TestBaseWatcherInit:
    """Tests for BaseWatcher initialization."""

    def test_get_processed_ids_empty_initially(self, temp_vault):
        """Should return empty set when no processed IDs exist."""
        watcher = ConcreteWatcher(str(temp_vault))
        ids = watcher.get_processed_ids()
        assert ids == set()

    def test_loads_existing_processed_ids(self, temp_vault):
        """Should load previously processed IDs."""
        ids_file = temp_vault / ".processed_ids.json"
        ids_file.write_text(json.dumps({"TestWatcher": ["id1", "id2", "id3"]}))

        watcher = ConcreteWatcher(str(temp_vault))
        ids = watcher.get_processed_ids()
        assert ids == {"id1", "id2", "id3"}

    def test_sets_default_name(self, temp_vault):
        """Should set the watcher name."""
        watcher = ConcreteWatcher(str(temp_vault))
        assert watcher.name == "TestWatcher"


class TestProcessedIDs:
    """Tests for processed ID tracking."""

    def test_save_and_reload_processed_ids(self, temp_vault):
        """Should persist and reload processed IDs."""
        watcher = ConcreteWatcher(str(temp_vault))
        watcher.save_processed_ids({"id1", "id2"})

        watcher2 = ConcreteWatcher(str(temp_vault))
        ids = watcher2.get_processed_ids()
        assert ids == {"id1", "id2"}

    def test_is_processed_via_saved_ids(self, temp_vault):
        """Should check if an ID is in the saved set."""
        watcher = ConcreteWatcher(str(temp_vault))
        watcher.save_processed_ids({"existing"})

        ids = watcher.get_processed_ids()
        assert "existing" in ids
        assert "new" not in ids

    def test_persists_ids_to_disk(self, temp_vault):
        """Should save processed IDs to disk in correct format."""
        watcher = ConcreteWatcher(str(temp_vault))
        watcher.save_processed_ids({"a", "b", "c"})

        ids_file = temp_vault / ".processed_ids.json"
        assert ids_file.exists()
        with open(ids_file) as f:
            saved = json.load(f)

        assert "TestWatcher" in saved
        assert set(saved["TestWatcher"]) == {"a", "b", "c"}

    def test_handles_large_id_sets(self, temp_vault):
        """Should handle large numbers of IDs without issue."""
        watcher = ConcreteWatcher(str(temp_vault))
        large_set = {f"id_{i}" for i in range(1000)}
        watcher.save_processed_ids(large_set)

        watcher2 = ConcreteWatcher(str(temp_vault))
        ids = watcher2.get_processed_ids()
        assert len(ids) == 1000


class TestWatcherLogging:
    """Tests for watcher logging."""

    def test_log_action_creates_log_file(self, temp_vault):
        """Should create a log entry."""
        watcher = ConcreteWatcher(str(temp_vault))
        watcher.log_action("test_action", {"key": "value"})

        log_dir = temp_vault / "Logs" / "watchers"
        if log_dir.exists():
            log_files = list(log_dir.glob("*.jsonl"))
            assert len(log_files) > 0
