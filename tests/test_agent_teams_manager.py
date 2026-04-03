"""
Tests for AgentTeamsManager.

Covers: team creation decision, composition suggestion, task distribution,
team prompt generation, and team cleanup.
"""

import json
from pathlib import Path

import pytest

from agent_teams_manager import AgentTeamsManager


class TestAgentTeamsManagerShouldCreateTeam:
    """Tests for the should_create_team decision logic."""

    def test_disabled_by_default(self, temp_vault, monkeypatch):
        """Teams should be disabled unless AGENT_TEAMS_ENABLED=true."""
        monkeypatch.delenv("AGENT_TEAMS_ENABLED", raising=False)
        manager = AgentTeamsManager(temp_vault)

        assert manager.should_create_team("test", 10) is False

    def test_enabled_when_env_set(self, temp_vault, monkeypatch):
        """Teams should be enabled when AGENT_TEAMS_ENABLED=true."""
        monkeypatch.setenv("AGENT_TEAMS_ENABLED", "true")
        manager = AgentTeamsManager(temp_vault)

        # With enough items, should return True
        assert manager.should_create_team("test", 10) is True

    def test_requires_minimum_items(self, temp_vault, monkeypatch):
        """Should not create team with too few items."""
        monkeypatch.setenv("AGENT_TEAMS_ENABLED", "true")
        manager = AgentTeamsManager(temp_vault)

        assert manager.should_create_team("test", 1) is False
        assert manager.should_create_team("test", 2) is False

    def test_detects_multi_domain_prompt(self, temp_vault, monkeypatch):
        """Should detect multiple domains and recommend team."""
        monkeypatch.setenv("AGENT_TEAMS_ENABLED", "true")
        manager = AgentTeamsManager(temp_vault)

        # Prompt spans email and finance domains
        prompt = "Process the invoice email and update the payment in odoo accounting"
        assert manager.should_create_team(prompt, 5) is True

    def test_high_item_count_triggers_team(self, temp_vault, monkeypatch):
        """Should trigger team creation when many items exist (2x threshold)."""
        monkeypatch.setenv("AGENT_TEAMS_ENABLED", "true")
        manager = AgentTeamsManager(temp_vault)

        threshold = manager.MIN_ITEMS_FOR_TEAM * 2
        assert manager.should_create_team("misc items", threshold) is True


class TestTeamComposition:
    """Tests for team composition suggestions."""

    def test_recommends_matching_roles(self, temp_vault):
        """Should recommend roles that match the items."""
        manager = AgentTeamsManager(temp_vault)
        items = [
            "invoice_payment.md",
            "odoo_accounting.md",
            "billing_statement.md",
        ]

        suggestion = manager.suggest_team_composition(items)

        assert suggestion["recommended_size"] >= 1
        assert "finance_specialist" in suggestion["roles"]
        assert suggestion["total_tasks"] == 3

    def test_includes_generalist(self, temp_vault):
        """Should always include generalist role."""
        manager = AgentTeamsManager(temp_vault)
        items = ["unknown_item_type.md"]

        suggestion = manager.suggest_team_composition(items)
        assert "generalist" in suggestion["roles"]

    def test_caps_team_size(self, temp_vault):
        """Should not exceed MAX_TEAM_SIZE."""
        manager = AgentTeamsManager(temp_vault)
        # Create items spanning many domains
        items = [
            "email_reply_to_client.md",
            "invoice_123_payment.md",
            "tweet_about_product.md",
            "debug_api_endpoint.py.md",
            "research_competitor.md",
            "email_follow_up.md",
            "payment_processing.md",
            "linkedin_post.md",
        ]

        suggestion = manager.suggest_team_composition(items)
        assert suggestion["recommended_size"] <= manager.MAX_TEAM_SIZE

    def test_distributes_tasks(self, temp_vault):
        """Should distribute items among roles."""
        manager = AgentTeamsManager(temp_vault)
        items = [
            "email_urgent_invoice.md",
            "twitter_announcement.md",
            "code_bug_fix.md",
        ]

        suggestion = manager.suggest_team_composition(items)
        distribution = suggestion["task_distribution"]

        # Each item should be assigned to exactly one role
        total_assigned = sum(len(v) for v in distribution.values())
        assert total_assigned == len(items)

    def test_role_scores_reflect_relevance(self, temp_vault):
        """Higher scores should reflect more matching items."""
        manager = AgentTeamsManager(temp_vault)
        items = [
            "invoice_1.md",
            "invoice_2.md",
            "invoice_3.md",
            "email_1.md",
        ]

        suggestion = manager.suggest_team_composition(items)
        assert suggestion["role_scores"]["finance_specialist"] >= 3
        assert suggestion["role_scores"]["email_specialist"] >= 1


class TestTeamPrompt:
    """Tests for team prompt generation."""

    def test_generates_valid_prompt(self, temp_vault):
        """Generated prompt should be non-empty and contain key sections."""
        manager = AgentTeamsManager(temp_vault)
        suggestion = {
            "recommended_size": 2,
            "roles": ["email_specialist", "generalist"],
            "total_tasks": 5,
            "task_distribution": {
                "email_specialist": ["item1", "item2"],
                "generalist": ["item3", "item4", "item5"],
            },
        }

        prompt = manager.create_team_prompt(suggestion)
        assert len(prompt) > 50
        assert "email_specialist" in prompt
        assert "generalist" in prompt
        assert "task distribution" in prompt.lower()


class TestDomainDetection:
    """Tests for domain detection."""

    def test_detects_email_domain(self, temp_vault):
        """Should detect email-related prompts."""
        manager = AgentTeamsManager(temp_vault)
        domains = manager._detect_domains("reply to this email and draft a response")
        assert "email_specialist" in domains

    def test_detects_finance_domain(self, temp_vault):
        """Should detect finance-related prompts."""
        manager = AgentTeamsManager(temp_vault)
        domains = manager._detect_domains("process invoice and record payment")
        assert "finance_specialist" in domains

    def test_detects_social_domain(self, temp_vault):
        """Should detect social media prompts."""
        manager = AgentTeamsManager(temp_vault)
        domains = manager._detect_domains("post to linkedin and twitter")
        assert "social_specialist" in domains

    def test_defaults_to_generalist(self, temp_vault):
        """Should return generalist for unrecognizable prompts."""
        manager = AgentTeamsManager(temp_vault)
        domains = manager._detect_domains("do something random and unspecified")
        assert "generalist" in domains

    def test_detects_multiple_domains(self, temp_vault):
        """Should detect multiple domains in a prompt."""
        manager = AgentTeamsManager(temp_vault)
        prompt = "reply to the email about the invoice and post about it on twitter"
        domains = manager._detect_domains(prompt)
        assert len(domains) >= 2


class TestTeamStatus:
    """Tests for team status and cleanup."""

    def test_get_active_teams_empty(self, temp_vault):
        """Should return empty list when no teams exist."""
        manager = AgentTeamsManager(temp_vault)
        teams = manager.get_active_teams()
        assert teams == []

    def test_get_active_teams_reads_files(self, temp_vault):
        """Should read team data from Active directory."""
        manager = AgentTeamsManager(temp_vault)
        team_data = {
            "team_name": "test-team",
            "roles": ["email_specialist"],
            "tasks": {"completed": 1, "pending": 0, "in_progress": 0},
            "created": "2026-04-01",
            "status": "active",
        }
        team_file = manager.active_teams_dir / "team_001.json"
        team_file.write_text(json.dumps(team_data))

        teams = manager.get_active_teams()
        assert len(teams) == 1
        assert teams[0]["team_name"] == "test-team"

    def test_cleanup_completed_teams(self, temp_vault):
        """Should move completed teams to Completed directory."""
        manager = AgentTeamsManager(temp_vault)
        completed_team = {
            "team_name": "finished-team",
            "tasks": {"completed": 5, "pending": 0, "in_progress": 0},
        }
        active_team = {
            "team_name": "still-working",
            "tasks": {"completed": 2, "pending": 3, "in_progress": 1},
        }

        (manager.active_teams_dir / "finished.json").write_text(json.dumps(completed_team))
        (manager.active_teams_dir / "active.json").write_text(json.dumps(active_team))

        manager.cleanup_completed_teams()

        assert (manager.completed_teams_dir / "finished.json").exists()
        assert (manager.active_teams_dir / "finished.json").exists() is False
        assert (manager.active_teams_dir / "active.json").exists()

    def test_status_report_format(self, temp_vault):
        """Should generate markdown status report."""
        manager = AgentTeamsManager(temp_vault)
        team_data = {
            "team_name": "report-team",
            "roles": ["email_specialist", "finance_specialist"],
            "tasks": {"completed": 3, "pending": 2, "in_progress": 1},
            "created": "2026-04-01",
            "status": "in_progress",
            "issues": ["One task failing"],
        }
        (manager.active_teams_dir / "team_report.json").write_text(json.dumps(team_data))

        report = manager.create_team_status_report()
        assert "# Agent Team Status" in report
        assert "report-team" in report
        assert "email_specialist" in report
        assert "issues" in report.lower() or "⚠️" in report
