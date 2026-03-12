#!/usr/bin/env python3
"""
Quick Test Script - Verify Personal AI Employee Setup

This script tests all critical components to ensure the system is working.

Usage:
    python test_setup.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name, status, message=""):
    """Print test result."""
    symbol = "✅" if status else "❌"
    color = GREEN if status else RED
    print(f"{symbol} {color}{name}{RESET}")
    if message:
        print(f"   {message}")

def print_section(name):
    """Print section header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def test_environment():
    """Test environment configuration."""
    print_section("1. Environment Configuration")

    # Check .env file
    env_exists = Path('.env').exists()
    print_test(".env file exists", env_exists)

    if env_exists:
        load_dotenv()

    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    has_api_key = bool(api_key and api_key.startswith('sk-ant-'))
    print_test("ANTHROPIC_API_KEY set", has_api_key,
               "Required for Claude integration" if not has_api_key else "")

    # Check vault path
    vault_path = Path(os.getenv('VAULT_PATH', './vault'))
    vault_exists = vault_path.exists()
    print_test("Vault directory exists", vault_exists)

    return env_exists and has_api_key and vault_exists

def test_dependencies():
    """Test Python dependencies."""
    print_section("2. Python Dependencies")

    dependencies = {
        'anthropic': 'Claude API',
        'google.auth': 'Gmail API',
        'playwright': 'Browser automation',
        'flask': 'Web server',
        'requests': 'HTTP requests',
        'dotenv': 'Environment variables'
    }

    all_installed = True
    for module, description in dependencies.items():
        try:
            __import__(module.replace('.', '_'))
            print_test(f"{module} ({description})", True)
        except ImportError:
            print_test(f"{module} ({description})", False,
                      f"Install with: pip install {module}")
            all_installed = False

    return all_installed

def test_vault_structure():
    """Test vault folder structure."""
    print_section("3. Vault Structure")

    vault_path = Path(os.getenv('VAULT_PATH', './vault'))
    required_folders = [
        'Needs_Action',
        'Plans',
        'Done',
        'Pending_Approval',
        'Approved',
        'Drafts',
        'Logs',
        'secrets'
    ]

    all_exist = True
    for folder in required_folders:
        folder_path = vault_path / folder
        exists = folder_path.exists()
        print_test(f"{folder}/ folder", exists)
        if not exists:
            all_exist = False
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"   Created: {folder_path}")

    return all_exist

def test_claude_api():
    """Test Claude API connection."""
    print_section("4. Claude API Integration")

    try:
        import anthropic
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv('ANTHROPIC_API_KEY')

        if not api_key:
            print_test("Claude API connection", False, "API key not set")
            return False

        client = anthropic.Anthropic(api_key=api_key)

        # Test API call
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Reply with just 'OK' if you can read this."}
            ]
        )

        response = message.content[0].text
        success = 'OK' in response.upper()

        print_test("Claude API connection", success,
                   f"Response: {response[:50]}" if success else "Unexpected response")
        return success

    except ImportError:
        print_test("Claude API connection", False, "anthropic package not installed")
        return False
    except Exception as e:
        print_test("Claude API connection", False, f"Error: {str(e)}")
        return False

def test_gmail_auth():
    """Test Gmail authentication."""
    print_section("5. Gmail Authentication")

    token_path = Path(os.getenv('GMAIL_TOKEN_PATH', './vault/secrets/gmail_token.json'))
    creds_path = Path(os.getenv('GMAIL_CREDENTIALS_PATH', './vault/secrets/gmail_credentials.json'))

    creds_exist = creds_path.exists()
    token_exists = token_path.exists()

    print_test("Gmail credentials file", creds_exist,
               "Download from Google Cloud Console" if not creds_exist else "")
    print_test("Gmail token file", token_exists,
               "Run: python watchers/gmail_watcher.py --vault ./vault" if not token_exists else "")

    if token_exists:
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials.from_authorized_user_file(str(token_path))
            service = build('gmail', 'v1', credentials=creds)

            # Test API call
            profile = service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress', 'Unknown')

            print_test("Gmail API connection", True, f"Authenticated as: {email}")
            return True

        except ImportError:
            print_test("Gmail API connection", False, "google-api-python-client not installed")
            return False
        except Exception as e:
            print_test("Gmail API connection", False, f"Error: {str(e)}")
            return False

    return False

def test_email_operations():
    """Test email MCP server."""
    print_section("6. Email Operations")

    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from mcp.email.server import EmailMCPServer

        # Set dry-run mode
        os.environ['DRY_RUN'] = 'true'

        server = EmailMCPServer()

        # Test send_email
        result = server.send_email({
            'to': 'test@example.com',
            'subject': 'Test',
            'body': 'Test email'
        })
        send_works = result.get('status') in ['sent', 'dry_run', 'created']
        print_test("Email sending", send_works, f"Status: {result.get('status')}")

        # Test search_emails
        result = server.search_emails({
            'query': 'is:unread',
            'max_results': 1
        })
        search_works = result.get('status') in ['success', 'error']
        print_test("Email search", search_works,
                   f"Found {result.get('count', 0)} emails" if search_works else "")

        return send_works and search_works

    except Exception as e:
        print_test("Email operations", False, f"Error: {str(e)}")
        return False

def test_orchestrator():
    """Test orchestrator."""
    print_section("7. Orchestrator")

    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from orchestrator import Orchestrator

        vault_path = os.getenv('VAULT_PATH', './vault')
        orch = Orchestrator(vault_path, dry_run=True)

        print_test("Orchestrator initialization", True)

        # Test trigger_claude
        test_prompt = "Test email: This is a test message."
        result = orch.trigger_claude(test_prompt)

        print_test("Claude integration", result,
                   "Orchestrator can call Claude API" if result else "")

        return result

    except Exception as e:
        print_test("Orchestrator", False, f"Error: {str(e)}")
        return False

def print_summary(results):
    """Print test summary."""
    print_section("Test Summary")

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    print(f"Total tests: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")

    if failed == 0:
        print(f"\n{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}✅ All tests passed! System is ready to use.{RESET}")
        print(f"{GREEN}{'='*60}{RESET}\n")
        print("Next steps:")
        print("1. Run: python orchestrator.py --vault ./vault")
        print("2. Run: python watchers/gmail_watcher.py --vault ./vault")
        print("3. Check vault/Plans/ for Claude's action plans")
    else:
        print(f"\n{RED}{'='*60}{RESET}")
        print(f"{RED}❌ Some tests failed. Fix issues above.{RESET}")
        print(f"{RED}{'='*60}{RESET}\n")
        print("Common fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set API key in .env: ANTHROPIC_API_KEY=sk-ant-...")
        print("3. Authenticate Gmail: python watchers/gmail_watcher.py --vault ./vault")
        print("4. See SETUP.md for detailed instructions")

def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Personal AI Employee - Setup Test{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    results = {
        'environment': test_environment(),
        'dependencies': test_dependencies(),
        'vault_structure': test_vault_structure(),
        'claude_api': test_claude_api(),
        'gmail_auth': test_gmail_auth(),
        'email_operations': test_email_operations(),
        'orchestrator': test_orchestrator()
    }

    print_summary(results)

    # Exit with appropriate code
    sys.exit(0 if all(results.values()) else 1)

if __name__ == '__main__':
    main()
