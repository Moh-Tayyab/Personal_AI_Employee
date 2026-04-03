"""
Shared pytest fixtures for Personal AI Employee tests.

Provides temporary vault structures, mock objects, and common test utilities.
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path so all modules are importable
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


@pytest.fixture
def temp_vault(tmp_path):
    """
    Create a temporary vault structure for testing.

    Returns a Path to the vault root with all required subdirectories.
    """
    vault = tmp_path / "test_vault"
    vault.mkdir()

    # Create standard vault directories
    for subdir in [
        "Needs_Action",
        "Plans",
        "Done",
        "Pending_Approval",
        "Approved",
        "Rejected",
        "Logs",
        "Briefings",
        "Logs/audit",
        "Logs/cli_usage",
        "secrets",
        "Teams/Active",
        "Teams/Completed",
    ]:
        (vault / subdir).mkdir(parents=True, exist_ok=True)

    # Create minimal vault files
    (vault / "Dashboard.md").write_text("# Dashboard\n\nStatus: Active\n")
    (vault / "Company_Handbook.md").write_text("# Company Handbook\n")
    (vault / "Business_Goals.md").write_text("# Business Goals\n")

    return vault


@pytest.fixture
def temp_vault_with_items(tmp_vault):
    """Create a vault populated with sample action items."""
    # Add items to Needs_Action
    for i, item in enumerate([
        "EMAIL_20260401_100000_UrgentInvoice.md",
        "WHATSAPP_20260401_110000_ImportantClient.md",
        "FILE_20260401_120000_Report.pdf.md",
    ]):
        content = f"""---
type: action_item
created: 2026-04-01T{i+10:02d}:00:00
source: {item.split('_')[0].lower()}
---

# {item.replace('.md', '')}

Sample action item content for testing.
"""
        (tmp_vault / "Needs_Action" / item).write_text(content)

    return tmp_vault


@pytest.fixture
def sample_email_action():
    """Return sample email action item content."""
    return """---
type: action_item
created: 2026-04-01T10:00:00
source: email
priority: high
---

# EMAIL_20260401_100000_UrgentInvoice

**From:** billing@vendor.com
**Subject:** Urgent: Invoice #12345 - Payment Overdue
**Date:** 2026-04-01

Dear Muhammad,

This is a reminder that invoice #12345 for $500 is now 30 days overdue.
Please process the payment at your earliest convenience.

Keywords: invoice, payment, urgent
"""


@pytest.fixture
def sample_whatsapp_action():
    """Return sample WhatsApp action item content."""
    return """---
type: action_item
created: 2026-04-01T11:00:00
source: whatsapp
priority: medium
---

# WHATSAPP_20260401_110000_ImportantClient

**Contact:** John Doe
**Message:** Hi, can you send me the pricing for the new project?
**Matched Keywords:** pricing

Keywords: pricing, project
"""


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("QWEN_API_KEY", "test-qwen-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")


@pytest.fixture
def sample_plan_content():
    """Return sample plan content."""
    return """---
type: ai_plan
created: 2026-04-01T10:05:00
provider: gemini
task_type: finance
---

# AI Action Plan

## Analysis
Invoice requires payment approval. Amount $500 is under $500 threshold.

## Recommended Actions
1. Create payment record in Odoo
2. Notify sender that payment is processing

## Approval Required
NO - under threshold

## Priority
HIGH
"""


@pytest.fixture
def sample_approval_item():
    """Return sample approval request content."""
    return """---
type: approval_request
created: 2026-04-01T10:05:00
action: send_email
recipient_count: 5
---

# Approval Request: Send Email Response

## Action
Send email response to billing @vendor.com regarding invoice #12345.

## Reason
Acknowledging receipt and confirming payment date.

## Risk Assessment
LOW - Standard business communication
"""


@pytest.fixture
def temp_vault_with_approval_flow(tmp_vault, sample_plan_content, sample_approval_item):
    """Create a vault with items in the approval workflow."""
    (tmp_vault / "Pending_Approval" / "APPROVAL_001.md").write_text(sample_plan_content)
    (tmp_vault / "Approved" / "EMAIL_001.md").write_text(sample_approval_item)
    return tmp_vault
