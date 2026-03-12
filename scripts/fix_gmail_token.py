#!/usr/bin/env python3
"""
Fix Gmail Token - Simple token setup for Gmail Watcher

This script helps you authenticate with Gmail API and create a working token.

Usage:
    python scripts/fix_gmail_token.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get paths from environment or use defaults
VAULT_PATH = Path(os.getenv('VAULT_PATH', './vault'))
CREDENTIALS_PATH = Path(os.getenv('GMAIL_CREDENTIALS_PATH', VAULT_PATH / 'secrets' / 'gmail_credentials.json'))
TOKEN_PATH = Path(os.getenv('GMAIL_TOKEN_PATH', VAULT_PATH / 'secrets' / 'gmail_token.json'))

print("=" * 60)
print("Gmail Token Setup for Personal AI Employee")
print("=" * 60)
print()

# Check if credentials file exists
print(f"Checking credentials file: {CREDENTIALS_PATH}")
if not CREDENTIALS_PATH.exists():
    print(f"❌ ERROR: Credentials file not found at: {CREDENTIALS_PATH}")
    print()
    print("To get Gmail credentials:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing")
    print("3. Enable Gmail API")
    print("4. Create OAuth 2.0 credentials (Desktop app)")
    print("5. Download credentials.json")
    print("6. Save as:", CREDENTIALS_PATH)
    print()
    sys.exit(1)
else:
    print("✅ Credentials file found")

print()
print(f"Token will be saved to: {TOKEN_PATH}")
print()

# Try to authenticate
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    creds = None
    
    # Try to load existing token
    if TOKEN_PATH.exists():
        print("Loading existing token...")
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
            print("✅ Existing token loaded")
        except Exception as e:
            print(f"⚠️ Existing token invalid: {e}")
            creds = None
    
    # Check if token is valid
    if creds and creds.valid:
        print("✅ Token is valid and ready to use!")
        print()
        print("Gmail Watcher is ready to use.")
        print("Run: python watchers/gmail_watcher.py --vault ./vault")
        sys.exit(0)
    
    # Token expired or not found - need to authenticate
    print()
    print("=" * 60)
    print("AUTHENTICATION REQUIRED")
    print("=" * 60)
    print()
    print("Opening browser for Gmail authentication...")
    print("Please complete the authentication in your browser.")
    print()
    
    # Ensure token directory exists
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Run OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_PATH), SCOPES
    )
    creds = flow.run_local_server(port=8080, open_browser=True)
    
    # Save the token
    with open(TOKEN_PATH, 'w') as token:
        token.write(creds.to_json())
    
    print()
    print("=" * 60)
    print("✅ AUTHENTICATION SUCCESSFUL!")
    print("=" * 60)
    print()
    print(f"Token saved to: {TOKEN_PATH}")
    print()
    print("Next steps:")
    print("1. Test Gmail watcher: python watchers/gmail_watcher.py --vault ./vault --interval 30")
    print("2. Start orchestrator: python orchestrator.py --vault ./vault")
    print()
    
except ImportError as e:
    print(f"❌ ERROR: Missing required package: {e}")
    print()
    print("Install required packages:")
    print("    pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    print("Troubleshooting:")
    print("1. Make sure credentials.json is valid")
    print("2. Make sure Gmail API is enabled in Google Cloud Console")
    print("3. Try deleting the token file and re-authenticating")
    sys.exit(1)
