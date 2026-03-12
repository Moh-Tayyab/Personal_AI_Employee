#!/usr/bin/env python3
"""
Gmail OAuth Setup Script

This script helps you authenticate with Gmail API and generate the required token.

Requirements:
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

Usage:
    python scripts/gmail_oauth_setup.py
"""

import os
import sys
from pathlib import Path

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]


def setup_gmail_oauth():
    """Run Gmail OAuth setup flow."""
    
    print("=" * 60)
    print("Gmail OAuth Setup")
    print("=" * 60)
    print()
    
    # Check if credentials file exists
    credentials_path = Path('./vault/secrets/gmail_credentials.json')
    
    if not credentials_path.exists():
        print("❌ Gmail credentials file not found!")
        print()
        print("To get your credentials:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download the credentials JSON file")
        print("6. Save it to: vault/secrets/gmail_credentials.json")
        print()
        return False
    
    print(f"✅ Found credentials: {credentials_path}")
    
    # Try to import required libraries
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        print("✅ Gmail API libraries found")
    except ImportError as e:
        print(f"❌ Missing required library: {e}")
        print()
        print("Install with:")
        print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return False
    
    # Token path
    token_path = Path('./vault/secrets/gmail_token.json')
    token_path.parent.mkdir(parents=True, exist_ok=True)
    
    print()
    print("Starting OAuth flow...")
    print()
    print("📋 INSTRUCTIONS:")
    print("1. A browser window will open (or you'll get a URL)")
    print("2. Sign in with your Google account")
    print("3. Grant permissions to access your Gmail")
    print("4. You'll be redirected to a page with an authorization code")
    print("5. Copy the code and paste it in the terminal")
    print()
    
    # Check if running in interactive terminal
    import sys
    if sys.stdin.isatty():
        print("Press Enter to continue...")
        input()
    else:
        print("Non-interactive mode - proceeding directly...")
    
    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            SCOPES
        )
        
        # Try to open browser automatically
        creds = flow.run_local_server(
            port=8080,
            open_browser=True,
            success_message="Authentication successful! You can close this window.",
            authorization_prompt_message="Please visit this URL: {url}"
        )
        
        # Save token
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print()
        print("=" * 60)
        print("✅ OAuth Setup Complete!")
        print("=" * 60)
        print()
        print(f"Token saved to: {token_path}")
        print()
        
        # Test the connection
        print("Testing Gmail API connection...")
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        
        print(f"✅ Connected to: {profile['emailAddress']}")
        print()
        print("🎉 Gmail integration is ready!")
        print()
        print("Next steps:")
        print("1. Configure MCP server in ~/.config/claude-code/mcp.json")
        print("2. Test email with: claude 'Send a test email'")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ OAuth failed: {e}")
        print("=" * 60)
        print()
        print("Troubleshooting:")
        print("1. Make sure Gmail API is enabled in Google Cloud Console")
        print("2. Check that credentials file is valid")
        print("3. Try running again")
        print()
        return False


def check_existing_token():
    """Check if a valid token already exists."""
    token_path = Path('./vault/secrets/gmail_token.json')
    
    if not token_path.exists():
        return None
    
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        creds = Credentials.from_authorized_user_file(
            str(token_path),
            SCOPES
        )
        
        # Check if token is still valid
        if creds and creds.valid:
            service = build('gmail', 'v1', credentials=creds)
            profile = service.users().getProfile(userId='me').execute()
            return profile['emailAddress']
        
    except Exception as e:
        print(f"Token check failed: {e}")
    
    return None


def main():
    """Main entry point."""
    print()
    
    # Check for existing valid token
    existing_email = check_existing_token()
    if existing_email:
        print(f"✅ Found existing valid token for: {existing_email}")
        print()
        response = input("Do you want to re-run OAuth setup? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup complete. Token is valid.")
            return 0
    
    # Run setup
    success = setup_gmail_oauth()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
