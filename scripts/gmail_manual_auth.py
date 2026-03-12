#!/usr/bin/env python3
"""
Manual Gmail OAuth Setup for WSL/Headless environments
"""

import os
import sys
import json
from pathlib import Path
from urllib.parse import urlencode
import secrets
import hashlib
import base64

def generate_auth_url():
    """Generate Gmail OAuth URL for manual authentication."""

    # Load client credentials
    credentials_path = Path('./vault/secrets/gmail_credentials.json')

    if not credentials_path.exists():
        print("❌ Gmail credentials file not found!")
        print("Please download from Google Cloud Console and save to:")
        print("   vault/secrets/gmail_credentials.json")
        return None

    with open(credentials_path) as f:
        creds = json.load(f)

    client_id = creds['installed']['client_id']

    # Generate PKCE parameters
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')

    # Store code_verifier for later use
    verifier_path = Path('./vault/secrets/gmail_code_verifier.txt')
    verifier_path.parent.mkdir(parents=True, exist_ok=True)
    verifier_path.write_text(code_verifier)

    # OAuth parameters
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8080/',
        'scope': 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.send',
        'state': secrets.token_urlsafe(32),
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'access_type': 'offline'
    }

    auth_url = 'https://accounts.google.com/o/oauth2/auth?' + urlencode(params)
    return auth_url

def exchange_code_for_token(auth_code):
    """Exchange authorization code for access token."""

    try:
        import requests
    except ImportError:
        print("❌ requests library required: pip install requests")
        return False

    # Load client credentials
    credentials_path = Path('./vault/secrets/gmail_credentials.json')
    with open(credentials_path) as f:
        creds = json.load(f)

    client_id = creds['installed']['client_id']
    client_secret = creds['installed']['client_secret']

    # Load code verifier
    verifier_path = Path('./vault/secrets/gmail_code_verifier.txt')
    if not verifier_path.exists():
        print("❌ Code verifier not found. Please run generate_auth_url() first.")
        return False

    code_verifier = verifier_path.read_text().strip()

    # Exchange code for token
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:8080/',
        'code_verifier': code_verifier
    }

    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        token_data = response.json()

        # Save token
        token_path = Path('./vault/secrets/gmail_token.json')
        token_path.parent.mkdir(parents=True, exist_ok=True)

        # Format token for google-auth library
        token_info = {
            'token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token'),
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': client_id,
            'client_secret': client_secret,
            'scopes': [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify',
                'https://www.googleapis.com/auth/gmail.send'
            ]
        }

        with open(token_path, 'w') as f:
            json.dump(token_info, f, indent=2)

        print(f"✅ Token saved to: {token_path}")

        # Clean up
        verifier_path.unlink()

        return True
    else:
        print(f"❌ Token exchange failed: {response.status_code}")
        print(response.text)
        return False

def test_gmail_connection():
    """Test Gmail API connection."""

    token_path = Path('./vault/secrets/gmail_token.json')
    if not token_path.exists():
        print("❌ No Gmail token found")
        return False

    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file(str(token_path))
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()

        print(f"✅ Gmail connected: {profile['emailAddress']}")
        return True

    except Exception as e:
        print(f"❌ Gmail connection failed: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("🔐 GMAIL OAUTH SETUP - MANUAL MODE")
        print("=" * 50)
        print()
        print("STEP 1: Get Authorization URL")
        print("-" * 30)

        auth_url = generate_auth_url()
        if auth_url:
            print("Copy this URL and open it in your browser:")
            print()
            print(auth_url)
            print()
            print("STEP 2: Complete Authorization")
            print("-" * 30)
            print("1. Sign in to your Google account")
            print("2. Grant permissions to the app")
            print("3. You'll be redirected to localhost:8080/?code=...")
            print("4. Copy the 'code' parameter from the URL")
            print("5. Run: python3 scripts/gmail_manual_auth.py [code]")
            print()

    elif len(sys.argv) == 2:
        auth_code = sys.argv[1]
        print("🔐 EXCHANGING CODE FOR TOKEN")
        print("=" * 50)

        if exchange_code_for_token(auth_code):
            print()
            print("🧪 TESTING CONNECTION")
            print("=" * 50)
            test_gmail_connection()
            print()
            print("🎉 Gmail setup complete!")
            print("Your Personal AI Employee can now send emails!")
        else:
            print("❌ Setup failed")

    else:
        print("Usage:")
        print("  python3 scripts/gmail_manual_auth.py              # Get auth URL")
        print("  python3 scripts/gmail_manual_auth.py [auth_code]  # Exchange code")