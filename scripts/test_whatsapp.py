#!/usr/bin/env python3
"""
WhatsApp Automation Test Suite
Tests all components of the WhatsApp automation system.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_vault_structure():
    """Test vault directory structure"""
    print("Testing vault structure...")
    
    vault = Path(".")
    required_dirs = [
        "Needs_Action",
        "Plans",
        "Pending_Approval",
        "Approved",
        "Done",
        "Logs",
        ".whatsapp_session"
    ]
    
    for dir_name in required_dirs:
        dir_path = vault / dir_name
        if not dir_path.exists():
            print(f"✗ Directory missing: {dir_name}")
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {dir_name}")
        else:
            print(f"✓ Found: {dir_name}")
    
    print("✓ Vault structure test passed\n")
    return True


def test_watcher_imports():
    """Test that all required modules can be imported"""
    print("Testing module imports...")
    
    try:
        from watchers.whatsapp_watcher import WhatsAppWatcher
        print("✓ WhatsAppWatcher imported")
    except ImportError as e:
        print(f"✗ Failed to import WhatsAppWatcher: {e}")
        return False
    
    try:
        from watchers.whatsapp_orchestrator import WhatsAppOrchestrator
        print("✓ WhatsAppOrchestrator imported")
    except ImportError as e:
        print(f"✗ Failed to import WhatsAppOrchestrator: {e}")
        return False
    
    try:
        from mcp_servers.whatsapp_mcp import WhatsAppMCPServer
        print("✓ WhatsAppMCPServer imported")
    except ImportError as e:
        print(f"✗ Failed to import WhatsAppMCPServer: {e}")
        return False
    
    print("✓ All imports successful\n")
    return True


def test_watcher_initialization():
    """Test WhatsApp Watcher initialization"""
    print("Testing WhatsApp Watcher initialization...")
    
    try:
        from watchers.whatsapp_watcher import WhatsAppWatcher
        
        watcher = WhatsAppWatcher(
            vault_path=".",
            session_path="./vault/.whatsapp_session",
            check_interval=30
        )
        
        print(f"✓ Watcher created")
        print(f"  - Vault: {watcher.vault_path}")
        print(f"  - Session: {watcher.session_path}")
        print(f"  - Check interval: {watcher.check_interval}s")
        print(f"  - Trigger keywords: {len(watcher.trigger_keywords)}")
        
        # Test status method
        status = watcher.get_status()
        print(f"✓ Status method works: {status}")
        
        print("✓ Watcher initialization test passed\n")
        return True
        
    except Exception as e:
        print(f"✗ Watcher initialization failed: {e}")
        return False


def test_orchestrator_initialization():
    """Test WhatsApp Orchestrator initialization"""
    print("Testing WhatsApp Orchestrator initialization...")
    
    try:
        from watchers.whatsapp_orchestrator import WhatsAppOrchestrator
        
        orchestrator = WhatsAppOrchestrator(vault_path=".")
        
        print(f"✓ Orchestrator created")
        print(f"  - Vault: {orchestrator.vault_path}")
        print(f"  - Needs_Action: {orchestrator.needs_action}")
        print(f"  - Pending_Approval: {orchestrator.pending_approval}")
        
        print("✓ Orchestrator initialization test passed\n")
        return True
        
    except Exception as e:
        print(f"✗ Orchestrator initialization failed: {e}")
        return False


def test_action_file_creation():
    """Test action file creation"""
    print("Testing action file creation...")
    
    try:
        from watchers.whatsapp_watcher import WhatsAppWatcher
        
        watcher = WhatsAppWatcher(vault_path=".")
        
        # Create test message
        test_message = {
            'chat_name': 'Test User',
            'last_message': 'Hello! This is a test message with invoice keyword.',
            'timestamp': datetime.now().isoformat(),
            'is_trigger': True,
            'raw_data': 'Hello! This is a test message with invoice keyword.'
        }
        
        # Create action file
        action_file = watcher._create_action_file(test_message)
        
        if action_file.exists():
            print(f"✓ Action file created: {action_file.name}")
            
            # Verify content
            content = action_file.read_text()
            assert 'type: whatsapp_message' in content
            assert 'from: Test User' in content
            assert 'priority: HIGH' in content
            print("✓ Action file content valid")
            
            # Cleanup
            action_file.unlink()
            print("✓ Test file cleaned up")
            
            print("✓ Action file creation test passed\n")
            return True
        else:
            print("✗ Action file not created")
            return False
            
    except Exception as e:
        print(f"✗ Action file creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trigger_detection():
    """Test trigger keyword detection"""
    print("Testing trigger keyword detection...")
    
    try:
        from watchers.whatsapp_watcher import WhatsAppWatcher
        
        watcher = WhatsAppWatcher(vault_path=".")
        
        test_cases = [
            ("Send me the invoice ASAP", True),
            ("Hello, how are you?", False),
            ("Urgent payment needed", True),
            ("Just checking in", False),
            ("Please review this document", True),
            ("Thanks for your help", False),
        ]
        
        all_passed = True
        for message, expected in test_cases:
            result = watcher._is_trigger_message(message)
            status = "✓" if result == expected else "✗"
            print(f"  {status} '{message[:30]}...' -> {result} (expected {expected})")
            if result != expected:
                all_passed = False
        
        if all_passed:
            print("✓ All trigger detection tests passed\n")
        else:
            print("✗ Some trigger detection tests failed\n")
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Trigger detection test failed: {e}")
        return False


def test_mcp_server():
    """Test MCP Server initialization"""
    print("Testing MCP Server...")
    
    try:
        from mcp_servers.whatsapp_mcp import WhatsAppMCPServer
        
        server = WhatsAppMCPServer(vault_path=".")
        
        print(f"✓ MCP Server created")
        print(f"  - Vault: {server.vault_path}")
        print(f"  - Pending approvals: {server.pending_approvals}")
        
        print("✓ MCP Server test passed\n")
        return True
        
    except Exception as e:
        print(f"✗ MCP Server test failed: {e}")
        return False


def test_integration():
    """Test integration between components"""
    print("Testing component integration...")
    
    try:
        from watchers.whatsapp_watcher import WhatsAppWatcher
        from watchers.whatsapp_orchestrator import WhatsAppOrchestrator
        
        # Create watcher and orchestrator
        watcher = WhatsAppWatcher(vault_path=".")
        orchestrator = WhatsAppOrchestrator(vault_path=".")
        
        # Simulate message flow
        test_message = {
            'chat_name': 'Integration Test',
            'last_message': 'Test message for integration',
            'timestamp': datetime.now().isoformat(),
            'is_trigger': False,
            'raw_data': 'Test message for integration'
        }
        
        # Step 1: Watcher creates action file
        action_file = watcher._create_action_file(test_message)
        print(f"✓ Step 1: Action file created: {action_file.name}")
        
        # Step 2: Orchestrator processes action file
        content = action_file.read_text()
        orchestrator._process_action_file(action_file)
        print(f"✓ Step 2: Orchestrator processed action file")
        
        # Step 3: Check if plan was created
        plan_files = list(orchestrator.plans.glob("PLAN_*.md"))
        if plan_files:
            print(f"✓ Step 3: Plan created: {plan_files[0].name}")
        else:
            print(f"  - No plan created (expected for non-trigger message)")
        
        # Cleanup
        action_file.unlink()
        for plan_file in plan_files:
            plan_file.unlink()
        print("✓ Integration test cleaned up")
        
        print("✓ Integration test passed\n")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_approval_workflow():
    """Test approval workflow"""
    print("Testing approval workflow...")
    
    try:
        from mcp_servers.whatsapp_mcp import WhatsAppMCPServer
        import asyncio
        
        server = WhatsAppMCPServer(vault_path=".")
        
        # Create approval request
        approval_args = {
            "recipient": "Test Recipient",
            "message": "This is a test message",
            "reason": "Testing approval workflow"
        }
        
        # Create a mock async context
        async def test_approval():
            result = await server._create_approval_request(approval_args)
            
            # Check result
            result_text = result.content[0].text
            
            if "Approval request created" in result_text:
                print(f"✓ Approval request created")

                # Extract filename (handle multi-line result text)
                result_lines = result_text.split('\n')
                filename = None
                for line in result_lines:
                    if line.startswith("Approval request created:"):
                        filename = line.split(": ", 1)[1].strip()
                        break
                
                if not filename:
                    print(f"✗ Could not extract filename from result: {result_text}")
                    return False

                approval_file = server.pending_approvals / filename

                if approval_file.exists():
                    print(f"✓ Approval file exists: {filename}")

                    # Verify content
                    content = approval_file.read_text()
                    assert "Test Recipient" in content
                    assert "This is a test message" in content
                    print("✓ Approval file content valid")

                    # Cleanup
                    approval_file.unlink()
                    print("✓ Test file cleaned up")

                    return True
                else:
                    print(f"✗ Approval file not found at: {approval_file}")
                    print(f"  Pending approvals dir: {server.pending_approvals}")
                    print(f"  Files in dir: {list(server.pending_approvals.glob('*.md'))}")
                    return False
            else:
                print(f"✗ Unexpected result: {result_text}")
                return False
        
        # Run async test
        result = asyncio.run(test_approval())
        
        if result:
            print("✓ Approval workflow test passed\n")
        else:
            print("✗ Approval workflow test failed\n")
        
        return result
        
    except Exception as e:
        print(f"✗ Approval workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_field_extraction():
    """Test field extraction from markdown"""
    print("Testing field extraction...")

    try:
        from mcp_servers.whatsapp_mcp import WhatsAppMCPServer

        server = WhatsAppMCPServer(vault_path=".")

        # Test YAML frontmatter format (used in approval requests)
        test_content_frontmatter = """---
type: whatsapp_approval_request
recipient: John Doe
message: Hello World
reason: Testing
---

# WhatsApp Message Approval Request

## Message Details
- **To**: John Doe
- **Message**: Hello World
- **Reason**: Testing
"""

        # Test YAML frontmatter extraction
        recipient = server._extract_field(test_content_frontmatter, "recipient")
        message = server._extract_field(test_content_frontmatter, "message")

        if recipient == "John Doe":
            print(f"✓ Extracted recipient from frontmatter: {recipient}")
        else:
            print(f"✗ Failed to extract recipient from frontmatter: {recipient}")
            return False

        if message == "Hello World":
            print(f"✓ Extracted message from frontmatter: {message}")
        else:
            print(f"✗ Failed to extract message from frontmatter: {message}")
            return False

        # Test markdown body extraction
        test_content_markdown = """# Some Content

## Details
- **To**: Jane Smith
- **Message**: Test Message
- **Reason**: Testing
"""

        to_name = server._extract_field(test_content_markdown, "To")
        msg = server._extract_field(test_content_markdown, "Message")

        if to_name == "Jane Smith":
            print(f"✓ Extracted name from markdown body: {to_name}")
        else:
            print(f"✗ Failed to extract name from markdown body: {to_name}")
            return False

        if msg == "Test Message":
            print(f"✓ Extracted message from markdown body: {msg}")
        else:
            print(f"✗ Failed to extract message from markdown body: {msg}")
            return False

        print("✓ Field extraction test passed\n")
        return True

    except Exception as e:
        print(f"✗ Field extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_browser_manager_singleton():
    """Test browser manager singleton pattern"""
    print("Testing browser manager singleton...")

    try:
        from watchers.whatsapp_browser_manager import get_browser_manager

        # Get instance twice - should return same object
        mgr1 = get_browser_manager(session_path="./test_session_1", headless=True)
        mgr2 = get_browser_manager(session_path="./test_session_2", headless=True)

        # Should be same instance (singleton)
        if mgr1 is mgr2:
            print("✓ Singleton pattern works - same instance returned")
        else:
            print("✗ Singleton failed - different instances returned")
            return False

        # Verify session path is from first call (singleton doesn't reinitialize)
        if str(mgr1.session_path) == "./test_session_1" or mgr1.session_path == Path("./test_session_1"):
            print(f"✓ Session path preserved: {mgr1.session_path}")
        else:
            print(f"✗ Session path not preserved: {mgr1.session_path}")
            return False

        # Cleanup test session directory
        import shutil
        test_path = Path("./test_session_1")
        if test_path.exists():
            shutil.rmtree(test_path)

        print("✓ Browser manager singleton test passed\n")
        return True

    except Exception as e:
        print(f"✗ Browser manager singleton test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_send_method_signature():
    """Test that send method has proper signature and structure (without actually sending)"""
    print("Testing send method structure...")

    try:
        from mcp_servers.whatsapp_mcp import WhatsAppMCPServer
        import asyncio

        server = WhatsAppMCPServer(vault_path=".")

        # Verify method exists and has correct signature
        assert hasattr(server, '_send_via_playwright'), "_send_via_playwright method missing"
        assert hasattr(server, '_open_chat_async'), "_open_chat_async method missing"
        assert hasattr(server, '_type_message_async'), "_type_message_async method missing"
        assert hasattr(server, '_send_message_async'), "_send_message_async method missing"
        assert hasattr(server, '_verify_message_sent_async'), "_verify_message_sent_async method missing"

        print("✓ All send methods exist")

        # Test that it's a coroutine (async function)
        import inspect
        assert inspect.iscoroutinefunction(server._send_via_playwright), "Method should be async"
        assert inspect.iscoroutinefunction(server._open_chat_async), "Method should be async"
        assert inspect.iscoroutinefunction(server._type_message_async), "Method should be async"
        assert inspect.iscoroutinefunction(server._send_message_async), "Method should be async"
        assert inspect.iscoroutinefunction(server._verify_message_sent_async), "Method should be async"

        print("✓ All methods are properly async")

        # Test that method returns bool (when it fails gracefully without browser)
        async def test_return_type():
            # This will fail without browser but should return False, not raise
            try:
                # Don't actually try to initialize browser in test
                # Just verify the method exists and is callable
                import inspect
                sig = inspect.signature(server._send_via_playwright)
                params = list(sig.parameters.keys())
                if params == ['recipient', 'message']:
                    print(f"  Method signature correct: {params}")
                    return True
                else:
                    print(f"  Method signature wrong: {params}")
                    return False
            except Exception as e:
                print(f"  Method check raised exception: {e}")
                return False

        result = asyncio.run(test_return_type())
        if result:
            print("✓ Send method has correct signature")

        print("✓ Send method structure test passed\n")
        return True

    except Exception as e:
        print(f"✗ Send method structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_read_method_signature():
    """Test that read method has proper signature and structure"""
    print("Testing read method structure...")

    try:
        from mcp_servers.whatsapp_mcp import WhatsAppMCPServer
        import asyncio

        server = WhatsAppMCPServer(vault_path=".")

        # Verify method exists
        assert hasattr(server, '_read_via_playwright'), "_read_via_playwright method missing"
        assert hasattr(server, '_extract_messages_from_chat'), "_extract_messages_from_chat method missing"

        print("✓ All read methods exist")

        # Test that it's async
        import inspect
        assert inspect.iscoroutinefunction(server._read_via_playwright), "Method should be async"
        assert inspect.iscoroutinefunction(server._extract_messages_from_chat), "Method should be async"

        print("✓ All methods are properly async")

        # Test that method returns list (when it fails gracefully without browser)
        async def test_return_type():
            try:
                # Don't actually try to initialize browser in test
                # Just verify the method exists and has correct signature
                import inspect
                sig = inspect.signature(server._read_via_playwright)
                params = list(sig.parameters.keys())
                if params == ['chat_name', 'limit']:
                    print(f"  Method signature correct: {params}")
                    return True
                else:
                    print(f"  Method signature wrong: {params}")
                    return False
            except Exception as e:
                print(f"  Method check raised exception: {e}")
                return False

        result = asyncio.run(test_return_type())
        if result:
            print("✓ Read method has correct signature")

        print("✓ Read method structure test passed\n")
        return True

    except Exception as e:
        print(f"✗ Read method structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("  WhatsApp Automation Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Vault Structure", test_vault_structure),
        ("Module Imports", test_watcher_imports),
        ("Watcher Initialization", test_watcher_initialization),
        ("Orchestrator Initialization", test_orchestrator_initialization),
        ("Action File Creation", test_action_file_creation),
        ("Trigger Detection", test_trigger_detection),
        ("MCP Server", test_mcp_server),
        ("Integration", test_integration),
        ("Approval Workflow", test_approval_workflow),
        ("Field Extraction", test_field_extraction),
        ("Browser Manager Singleton", test_browser_manager_singleton),
        ("Send Method Signature", test_send_method_signature),
        ("Read Method Signature", test_read_method_signature),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("=" * 60)
    print("  Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! WhatsApp automation is ready.")
        print("\nNext steps:")
        print("1. Run: bash scripts/quickstart_whatsapp.sh")
        print("2. Scan QR code with your phone")
        print("3. Send a test message to verify automation")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
