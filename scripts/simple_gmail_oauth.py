#!/usr/bin/env python3
"""
Simple Gmail OAuth Setup - Works around redirect_uri issues

Usage:
    python3 scripts/simple_gmail_oauth.py
"""

import json
from pathlib import Path
import webbrowser
import http.server
import socketserver
import threading
from urllib.parse import urlparse, parse_qs
import base64
import hashlib
import secrets

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

def generate_pkce():
    """Generate PKCE code challenge."""
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()
    return code_verifier, code_challenge

def main():
    print("=" * 60)
    print("Gmail OAuth Setup - Simple Mode")
    print("=" * 60)
    print()
    
    # Load credentials
    credentials_path = Path('./vault/secrets/gmail_credentials.json')
    if not credentials_path.exists():
        print("❌ Credentials file not found at: vault/secrets/gmail_credentials.json")
        return False
    
    with open(credentials_path) as f:
        creds_data = json.load(f)
    
    # Handle both formats
    if 'installed' in creds_data:
        client_id = creds_data['installed']['client_id']
        client_secret = creds_data['installed']['client_secret']
    elif 'web' in creds_data:
        client_id = creds_data['web']['client_id']
        client_secret = creds_data['web']['client_secret']
    else:
        print("❌ Invalid credentials format")
        return False
    
    print(f"✅ Loaded credentials for client: {client_id[:20]}...")
    print()
    
    # Generate PKCE
    code_verifier, code_challenge = generate_pkce()
    state = secrets.token_urlsafe(16)
    
    # Build authorization URL
    auth_url = "https://accounts.google.com/o/oauth2/auth"
    params = {
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8080',
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    auth_url = f"{auth_url}?{query}"
    
    print("Step 1: Open authorization URL")
    print()
    print("Copy and paste this URL into your browser:")
    print()
    print(auth_url)
    print()
    
    # Try to open browser
    try:
        webbrowser.open(auth_url)
        print("🌐 Browser opened (if not, copy URL manually)")
    except:
        print("🌐 Could not open browser automatically - please copy URL")
    
    print()
    print("Step 2: Sign in and grant permission")
    print()
    
    # Set up local server to catch redirect
    authorization_code = None
    
    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal authorization_code
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            
            if 'code' in params:
                authorization_code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                response = """
                <html><body>
                <h1>✅ Success!</h1>
                <p>Authorization successful. You can close this window.</p>
                <script>setTimeout(() => window.close(), 3000);</script>
                </body></html>
                """
                self.wfile.write(response.encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Error: No code received")
        
        def log_message(self, format, *args):
            pass  # Suppress logging
    
    # Start server
    print("Step 3: Waiting for callback on localhost:8080...")
    print()
    
    with socketserver.TCPServer(("", 8080), CallbackHandler) as httpd:
        httpd.timeout = 120  # 2 minute timeout
        
        # Run server in background
        server_thread = threading.Thread(target=httpd.handle_request)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for callback
        server_thread.join(timeout=120)
    
    if not authorization_code:
        print("❌ No authorization code received")
        print()
        print("Alternative: Manually copy the code from browser URL")
        print("The URL will look like: http://localhost:8080/?code=4/0A...")
        print()
        
        try:
            authorization_code = input("Paste code here: ").strip()
        except EOFError:
            print("❌ No code provided")
            return False
    
    print("✅ Received authorization code")
    print()
    print("Step 4: Exchanging code for token...")
    
    # Exchange code for token
    import urllib.request
    import urllib.error
    
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': authorization_code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:8080',
        'code_verifier': code_verifier
    }
    
    try:
        request = urllib.request.Request(
            token_url,
            data=urllib.parse.urlencode(token_data).encode(),
            method='POST'
        )
        
        with urllib.request.urlopen(request) as response:
            token_response = json.loads(response.read().decode())
            
            if 'access_token' in token_response:
                # Save token
                token_path = Path('./vault/secrets/gmail_token.json')
                token_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Format as Google credentials JSON
                token_json = {
                    'token': token_response.get('access_token'),
                    'refresh_token': token_response.get('refresh_token'),
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'scopes': SCOPES,
                    'expiry': token_response.get('expiry_date')
                }
                
                with open(token_path, 'w') as f:
                    json.dump(token_json, f, indent=2)
                
                print()
                print("=" * 60)
                print("✅ OAuth Complete!")
                print("=" * 60)
                print()
                print(f"Token saved to: {token_path}")
                print()
                
                # Test connection
                try:
                    from google.oauth2.credentials import Credentials
                    from googleapiclient.discovery import build
                    
                    creds = Credentials(
                        token=token_response['access_token'],
                        refresh_token=token_response.get('refresh_token'),
                        token_uri=token_response['token_uri'],
                        client_id=client_id,
                        client_secret=client_secret,
                        scopes=SCOPES
                    )
                    
                    service = build('gmail', 'v1', credentials=creds)
                    profile = service.users().getProfile(userId='me').execute()
                    
                    print(f"✅ Connected to: {profile['emailAddress']}")
                    print()
                    print("🎉 Gmail integration is ready!")
                    print()
                    
                    return True
                    
                except Exception as e:
                    print(f"⚠️ Token saved but test failed: {e}")
                    print("You may need to re-run OAuth")
                    return True
            else:
                print(f"❌ Token exchange failed: {token_response}")
                return False
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ HTTP Error {e.code}: {error_body}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
