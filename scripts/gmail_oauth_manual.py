#!/usr/bin/env python3
"""
Gmail OAuth Setup - Manual Mode

Use this if the automatic browser flow doesn't work.

Usage:
    python scripts/gmail_oauth_manual.py
"""

import os
import sys
from pathlib import Path

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]


def manual_oauth():
    """Run manual OAuth flow with authorization code."""
    
    print("=" * 60)
    print("Gmail OAuth Setup - Manual Mode")
    print("=" * 60)
    print()
    
    credentials_path = Path('./vault/secrets/gmail_credentials.json')
    
    if not credentials_path.exists():
        print("❌ Credentials file not found at: vault/secrets/gmail_credentials.json")
        print()
        print("Get your credentials from:")
        print("https://console.cloud.google.com/apis/credentials")
        return False
    
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as e:
        print(f"❌ Missing library: {e}")
        return False
    
    print("Step 1: Open authorization URL")
    print()
    
    # Create flow
    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path),
        SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Out-of-band for manual code entry
    )
    
    # Get authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    print("Copy and paste this URL into your browser:")
    print()
    print(authorization_url)
    print()
    
    print("Step 2: After granting permission, copy the authorization code")
    print()
    
    try:
        auth_code = input("Paste authorization code here: ").strip()
    except EOFError:
        print("❌ No input received")
        return False
    
    if not auth_code:
        print("❌ No authorization code provided")
        return False
    
    print()
    print("Step 3: Exchanging code for token...")
    
    try:
        # Exchange code for token
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # Save token
        token_path = Path('./vault/secrets/gmail_token.json')
        token_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print()
        print("=" * 60)
        print("✅ OAuth Complete!")
        print("=" * 60)
        print()
        print(f"Token saved to: {token_path}")
        print()
        
        # Test connection
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        
        print(f"✅ Connected to: {profile['emailAddress']}")
        print()
        print("🎉 Gmail is ready!")
        print()
        
        return True
        
    except Exception as e:
        print()
        print(f"❌ Token exchange failed: {e}")
        return False


if __name__ == '__main__':
    success = manual_oauth()
    sys.exit(0 if success else 1)
