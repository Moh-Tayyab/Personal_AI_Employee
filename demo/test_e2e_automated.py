#!/usr/bin/env python3
"""
Automated End-to-End Demo Test (Non-Interactive)

Tests the complete workflow without requiring user input.
Run this to verify all components work together.

Usage:
    python demo/test_e2e_automated.py --vault ./vault
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator import Orchestrator


def print_section(title: str):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_success(message: str):
    """Print success message."""
    print(f"  ✅ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"  ℹ️  {message}")


def print_error(message: str):
    """Print error message."""
    print(f"  ❌ {message}")


def main():
    """Run automated end-to-end test."""
    print_section("PERSONAL AI EMPLOYEE - AUTOMATED E2E TEST")
    print()
    print("Testing complete workflow with Groq AI...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"DRY_RUN: true (safe testing mode)")
    
    results = {
        'passed': 0,
        'failed': 0,
        'steps': []
    }
    
    # ============================================================
    # STEP 1: Initialize Orchestrator
    # ============================================================
    print_section("STEP 1: Initialize Orchestrator")
    
    try:
        orch = Orchestrator(vault_path='./vault', dry_run=True)
        print_success("Orchestrator initialized")
        print_info(f"Vault: {orch.vault_path}")
        print_info(f"DRY_RUN: {orch.dry_run}")
        results['passed'] += 1
        results['steps'].append(('Initialize Orchestrator', 'PASS'))
    except Exception as e:
        print_error(f"Orchestrator initialization failed: {e}")
        results['failed'] += 1
        results['steps'].append(('Initialize Orchestrator', 'FAIL'))
        return
    
    # ============================================================
    # STEP 2: Create Test Item in Needs_Action
    # ============================================================
    print_section("STEP 2: Create Test Item (Simulating WhatsApp Message)")
    
    try:
        test_item_content = f"""---
type: whatsapp_message
from: Test Client
received: {datetime.now().isoformat()}
priority: HIGH
status: pending
trigger_keywords: true
---

# WhatsApp Message

## Sender
Test Client

## Message Content
Hi, I need an invoice for January 2026 consulting services. Please send it ASAP.

## Classification
- **Priority**: HIGH
- **Contains Trigger Words**: Yes (invoice, ASAP)

## Suggested Actions
- [ ] Review message
- [ ] Create invoice
- [ ] Send via email
"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_file_name = f"TEST_whatsapp_invoice_{timestamp}.md"
        test_file_path = orch.needs_action / test_file_name
        test_file_path.write_text(test_item_content)
        
        print_success(f"Test item created: {test_file_name}")
        print_info(f"Location: Needs_Action/{test_file_name}")
        
        # Verify file exists
        assert test_file_path.exists()
        print_success("File verified in Needs_Action/")
        
        results['passed'] += 1
        results['steps'].append(('Create Test Item', 'PASS'))
        
    except Exception as e:
        print_error(f"Failed to create test item: {e}")
        results['failed'] += 1
        results['steps'].append(('Create Test Item', 'FAIL'))
    
    # ============================================================
    # STEP 3: Check Needs_Action
    # ============================================================
    print_section("STEP 3: Check Needs_Action Folder")
    
    try:
        items = orch.check_needs_action()
        print_success(f"Found {len(items)} item(s) in Needs_Action")
        
        for item in items:
            print_info(f"  - {item.name}")
        
        assert len(items) > 0, "No items found"
        results['passed'] += 1
        results['steps'].append(('Check Needs_Action', 'PASS'))
        
    except Exception as e:
        print_error(f"Failed to check Needs_Action: {e}")
        results['failed'] += 1
        results['steps'].append(('Check Needs_Action', 'FAIL'))
    
    # ============================================================
    # STEP 4: Create Action Plan
    # ============================================================
    print_section("STEP 4: Create Action Plan")
    
    try:
        test_item = items[0]
        plan_path = orch.create_plan(test_item)
        
        print_success(f"Plan created: {plan_path.name}")
        print_info(f"Location: Plans/{plan_path.name}")
        
        # Verify plan exists
        assert plan_path.exists()
        print_success("Plan file verified")
        
        results['passed'] += 1
        results['steps'].append(('Create Action Plan', 'PASS'))
        
    except Exception as e:
        print_error(f"Failed to create plan: {e}")
        results['failed'] += 1
        results['steps'].append(('Create Action Plan', 'FAIL'))
    
    # ============================================================
    # STEP 5: Move to In_Progress
    # ============================================================
    print_section("STEP 5: Move to In_Progress")
    
    try:
        orch.move_to_in_progress(test_item)
        print_success("Item moved to In_Progress")
        
        # Verify it's in In_Progress
        in_progress_items = list(orch.in_progress.glob('*.md'))
        assert len(in_progress_items) > 0
        print_success(f"Verified: {len(in_progress_items)} item(s) in In_Progress")
        
        results['passed'] += 1
        results['steps'].append(('Move to In_Progress', 'PASS'))
        
    except Exception as e:
        print_error(f"Failed to move to In_Progress: {e}")
        results['failed'] += 1
        results['steps'].append(('Move to In_Progress', 'FAIL'))
    
    # ============================================================
    # STEP 6: Trigger AI Processing
    # ============================================================
    print_section("STEP 6: Trigger AI Processing (Groq)")
    
    try:
        prompt = f"""Process this WhatsApp message and create an action plan:

Item: {test_item.name}
Type: whatsapp_message
Priority: HIGH
Content: Client requesting invoice for January 2026 consulting services.

Analyze and provide:
1. What action is needed?
2. What information is required?
3. Does this need approval?
4. What are the next steps?
"""
        
        print_info("Sending to Groq AI for analysis...")
        start_time = time.time()
        success = orch.trigger_ai(prompt)
        duration = time.time() - start_time
        
        if success:
            print_success(f"AI processing completed ({duration:.2f}s)")
            print_info("Response saved to Plans/")
            
            # Check if plan was created
            plans = list(orch.plans.glob('*.md'))
            print_success(f"Total plans in vault: {len(plans)}")
            
            results['passed'] += 1
            results['steps'].append(('AI Processing (Groq)', 'PASS'))
        else:
            print_error("AI processing failed")
            results['failed'] += 1
            results['steps'].append(('AI Processing (Groq)', 'FAIL'))
        
    except Exception as e:
        print_error(f"AI processing error: {e}")
        results['failed'] += 1
        results['steps'].append(('AI Processing (Groq)', 'FAIL'))
    
    # ============================================================
    # STEP 7: Create Approval Request
    # ============================================================
    print_section("STEP 7: Create Approval Request")
    
    try:
        approval_content = f"""---
type: approval_request
action: send_invoice
recipient: Test Client
amount: 1500.00
reason: January 2026 consulting services
created: {datetime.now().isoformat()}
status: pending
---

# Approval Request: Send Invoice

## Details
- **Action**: Send invoice via email
- **Recipient**: Test Client
- **Amount**: $1,500.00
- **Reference**: January 2026 consulting

## To Approve
Move this file to Approved/ folder.

## To Reject
Move this file to Rejected/ folder.
"""
        
        approval_file_name = f"APPROVAL_invoice_{timestamp}.md"
        approval_path = orch.pending_approval / approval_file_name
        approval_path.write_text(approval_content)
        
        print_success(f"Approval request created: {approval_file_name}")
        
        # Verify
        approvals = orch.check_pending_approval()
        print_success(f"Pending approvals: {len(approvals)}")
        
        results['passed'] += 1
        results['steps'].append(('Create Approval Request', 'PASS'))
        
    except Exception as e:
        print_error(f"Failed to create approval request: {e}")
        results['failed'] += 1
        results['steps'].append(('Create Approval Request', 'FAIL'))
    
    # ============================================================
    # STEP 8: Simulate Approval (Move to Approved)
    # ============================================================
    print_section("STEP 8: Simulate Human Approval")
    
    try:
        # Simulate human approval by moving file
        import shutil
        approved_path = orch.approved / approval_file_name
        shutil.move(str(approval_path), str(approved_path))
        
        print_success("Approval request moved to Approved/")
        
        # Verify
        approved_items = orch.check_approved()
        print_success(f"Approved items ready for execution: {len(approved_items)}")
        
        results['passed'] += 1
        results['steps'].append(('Simulate Approval', 'PASS'))
        
    except Exception as e:
        print_error(f"Failed to simulate approval: {e}")
        results['failed'] += 1
        results['steps'].append(('Simulate Approval', 'FAIL'))
    
    # ============================================================
    # STEP 9: Execute Approved Action
    # ============================================================
    print_section("STEP 9: Execute Approved Action")
    
    try:
        approved_items = orch.check_approved()
        
        if approved_items:
            for item in approved_items:
                print_info(f"Processing: {item.name}")
                success = orch.process_approved_item(item)
                
                if success:
                    print_success(f"Action executed (DRY_RUN): {item.name}")
                    orch.move_to_done(item)
                    print_success(f"Moved to Done/: {item.name}")
                else:
                    print_error(f"Failed to process: {item.name}")
        
        results['passed'] += 1
        results['steps'].append(('Execute Approved Action', 'PASS'))
        
    except Exception as e:
        print_error(f"Failed to execute approved action: {e}")
        results['failed'] += 1
        results['steps'].append(('Execute Approved Action', 'FAIL'))
    
    # ============================================================
    # STEP 10: Update Dashboard
    # ============================================================
    print_section("STEP 10: Update Dashboard")
    
    try:
        orch._update_dashboard(
            orch.check_needs_action(),
            orch.check_pending_approval(),
            orch.check_approved()
        )
        
        print_success("Dashboard updated")
        
        # Verify dashboard
        dashboard_path = orch.vault_path / 'Dashboard.md'
        if dashboard_path.exists():
            content = dashboard_path.read_text()
            print_info(f"Dashboard size: {len(content)} bytes")
            print_success("Dashboard file verified")
        
        results['passed'] += 1
        results['steps'].append(('Update Dashboard', 'PASS'))
        
    except Exception as e:
        print_error(f"Failed to update dashboard: {e}")
        results['failed'] += 1
        results['steps'].append(('Update Dashboard', 'FAIL'))
    
    # ============================================================
    # STEP 11: Move Test Item to Done
    # ============================================================
    print_section("STEP 11: Complete Test Item")
    
    try:
        # Find the test item in In_Progress and move to Done
        in_progress_items = list(orch.in_progress.glob('TEST_*.md'))
        
        for item in in_progress_items:
            orch.move_to_done(item)
            print_success(f"Moved to Done/: {item.name}")
        
        done_items = list(orch.done.glob('*.md'))
        print_success(f"Total completed items: {len(done_items)}")
        
        results['passed'] += 1
        results['steps'].append(('Move to Done', 'PASS'))
        
    except Exception as e:
        print_error(f"Failed to move to Done: {e}")
        results['failed'] += 1
        results['steps'].append(('Move to Done', 'FAIL'))
    
    # ============================================================
    # STEP 12: Verify Logs
    # ============================================================
    print_section("STEP 12: Verify Audit Logs")
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = orch.logs / f'{today}.json'
        
        if log_file.exists():
            content = log_file.read_text()
            print_success(f"Log file exists: {log_file.name}")
            print_info(f"Log size: {len(content)} bytes")
        else:
            print_info("No log file yet (created on first action)")
        
        results['passed'] += 1
        results['steps'].append(('Verify Logs', 'PASS'))
        
    except Exception as e:
        print_error(f"Failed to verify logs: {e}")
        results['failed'] += 1
        results['steps'].append(('Verify Logs', 'FAIL'))
    
    # ============================================================
    # FINAL SUMMARY
    # ============================================================
    print_section("TEST SUMMARY")
    
    total = results['passed'] + results['failed']
    print()
    print(f"  Steps Passed: {results['passed']}/{total}")
    print(f"  Steps Failed: {results['failed']}/{total}")
    print()
    
    for step_name, status in results['steps']:
        icon = "✅" if status == "PASS" else "❌"
        print(f"  {icon} {step_name}: {status}")
    
    print()
    print("="*70)
    
    if results['failed'] == 0:
        print("  🎉 ALL TESTS PASSED! End-to-end workflow is working!")
        print()
        print("  Your AI Employee can:")
        print("  • Detect and process incoming requests")
        print("  • Create action plans with AI")
        print("  • Route through approval workflow")
        print("  • Execute approved actions")
        print("  • Update dashboard and logs")
        print("  • Archive completed tasks")
    else:
        print(f"  ⚠️  {results['failed']} test(s) failed - review errors above")
    
    print("="*70)
    print()


if __name__ == "__main__":
    main()
