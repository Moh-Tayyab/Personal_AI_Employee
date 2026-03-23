#!/usr/bin/env python3
"""
Social Media Authentication Script

Authenticate Twitter/X, Facebook, and LinkedIn for browser automation.
This script provides an interactive CLI for logging into each platform
and saving the session for later automated use.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python scripts/authenticate_social_media.py
    python scripts/authenticate_social_media.py --platform twitter
    python scripts/authenticate_social_media.py --platform linkedin --headless
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SocialMediaAuthenticator:
    """Handle authentication for all social media platforms."""

    def __init__(self, vault_path: str = "./vault"):
        self.vault_path = Path(vault_path)
        self.secrets_dir = self.vault_path / "secrets"
        self.secrets_dir.mkdir(parents=True, exist_ok=True)

        # Platform configurations
        self.platforms = {
            "twitter": {
                "name": "Twitter/X",
                "session_path": self.secrets_dir / "twitter_session",
                "env_var": "TWITTER_SESSION_PATH",
            },
            "linkedin": {
                "name": "LinkedIn",
                "session_path": self.secrets_dir / "linkedin_session",
                "env_var": "LINKEDIN_SESSION_PATH",
            },
            "facebook": {
                "name": "Facebook",
                "session_path": self.secrets_dir / "facebook_session",
                "env_var": "FACEBOOK_SESSION_PATH",
            },
        }

    def get_credentials(self, platform: str) -> tuple:
        """Get credentials from environment or prompt."""
        platform_config = self.platforms[platform]

        # Try environment variables first
        email_var = f"{platform.upper()}_EMAIL"
        password_var = f"{platform.upper()}_PASSWORD"

        email = os.getenv(email_var)
        password = os.getenv(password_var)

        if email and password:
            print(f"✓ Using credentials from environment variables")
            return email, password

        # Prompt for credentials
        print(f"\n{'='*60}")
        print(f"  {platform_config['name']} Authentication")
        print(f"{'='*60}\n")

        if platform == "twitter":
            print("Enter your Twitter/X username (not email)")
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            return username, password
        else:
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            return email, password

    def authenticate_twitter(self, username: str, password: str, headless: bool = False) -> dict:
        """Authenticate with Twitter/X."""
        from mcp.twitter.browser import TwitterBrowserSync

        print(f"\n🔐 Authenticating with Twitter/X...")
        print(f"   Username: {username}")
        print(f"   Headless: {headless}")

        browser = TwitterBrowserSync(str(self.platforms["twitter"]["session_path"]))

        try:
            result = browser.login(username, password)
            return result
        finally:
            browser.close()

    def authenticate_linkedin(self, email: str, password: str, headless: bool = False) -> dict:
        """Authenticate with LinkedIn."""
        from mcp.linkedin.browser import LinkedInBrowserSync

        print(f"\n🔐 Authenticating with LinkedIn...")
        print(f"   Email: {email}")
        print(f"   Headless: {headless}")

        browser = LinkedInBrowserSync(str(self.platforms["linkedin"]["session_path"]))

        try:
            result = browser.login(email, password)
            return result
        finally:
            browser.close()

    def authenticate_facebook(self, email: str, password: str, headless: bool = False) -> dict:
        """Authenticate with Facebook."""
        from mcp.facebook.browser import FacebookBrowserSync

        print(f"\n🔐 Authenticating with Facebook...")
        print(f"   Email: {email}")
        print(f"   Headless: {headless}")

        browser = FacebookBrowserSync(str(self.platforms["facebook"]["session_path"]))

        try:
            result = browser.login(email, password)
            return result
        finally:
            browser.close()

    def check_session(self, platform: str) -> dict:
        """Check if session is valid."""
        platform_config = self.platforms[platform]
        session_path = platform_config["session_path"]

        # Check if session file exists
        storage_file = session_path / "storage.json"
        if not storage_file.exists():
            return {"status": "not_authenticated", "message": "No session file found"}

        # Load and check session
        try:
            with open(storage_file, "r") as f:
                session_data = json.load(f)

            # Check cookies
            cookies = session_data.get("cookies", [])
            if not cookies:
                return {"status": "expired", "message": "Session has no cookies"}

            # Check expiry
            now = datetime.now().timestamp()
            expired_cookies = [c for c in cookies if c.get("expirationDate", now + 86400) < now]

            if len(expired_cookies) > len(cookies) * 0.5:  # More than 50% expired
                return {"status": "expired", "message": "Most session cookies expired"}

            return {"status": "valid", "message": "Session appears valid", "cookies_count": len(cookies)}

        except Exception as e:
            return {"status": "error", "message": f"Error reading session: {e}"}

    def save_auth_status(self, platform: str, result: dict):
        """Save authentication status to file."""
        status_file = self.secrets_dir / f"{platform}_auth_status.json"

        status_data = {
            "platform": platform,
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "session_path": str(self.platforms[platform]["session_path"]),
        }

        with open(status_file, "w") as f:
            json.dump(status_data, f, indent=2)

        print(f"\n✓ Authentication status saved to: {status_file}")

    def authenticate(self, platform: str, headless: bool = False, username: str = None, password: str = None) -> dict:
        """Authenticate with a platform."""
        if platform not in self.platforms:
            return {"status": "error", "message": f"Unknown platform: {platform}"}

        # Get credentials
        if username and password:
            cred1, cred2 = username, password
        else:
            cred1, cred2 = self.get_credentials(platform)

        # Authenticate based on platform
        if platform == "twitter":
            result = self.authenticate_twitter(cred1, cred2, headless)
        elif platform == "linkedin":
            result = self.authenticate_linkedin(cred1, cred2, headless)
        elif platform == "facebook":
            result = self.authenticate_facebook(cred1, cred2, headless)
        else:
            result = {"status": "error", "message": "Invalid platform"}

        # Save status
        self.save_auth_status(platform, result)

        return result


def print_auth_result(platform: str, result: dict):
    """Print authentication result."""
    status = result.get("status", "unknown")

    print(f"\n{'='*60}")
    print(f"  {platform.upper()} Authentication Result")
    print(f"{'='*60}\n")

    if status == "logged_in" or status == "already_logged_in":
        print(f"✅ SUCCESS: Authenticated to {platform}")
        if "profile_url" in result:
            print(f"   Profile: {result['profile_url']}")
    elif status == "needs_verification":
        print(f"⚠️  VERIFICATION REQUIRED")
        print(f"   {result.get('message', 'Additional verification needed')}")
        print(f"   URL: {result.get('url', 'N/A')}")
        print(f"\n   Please complete verification manually, then re-run this script.")
    elif status == "login_failed":
        print(f"❌ FAILED: Could not login")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        print(f"\n   Possible reasons:")
        print(f"   - Incorrect username/password")
        print(f"   - Two-factor authentication required")
        print(f"   - Account locked or suspended")
    elif status == "valid":
        print(f"✅ Session is valid")
        print(f"   {result.get('message', '')}")
    elif status == "expired" or status == "not_authenticated":
        print(f"⚠️  Session {status}")
        print(f"   {result.get('message', '')}")
    else:
        print(f"❓ Unknown status: {status}")
        print(f"   {result}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Authenticate social media accounts for automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode - choose platform
  python scripts/authenticate_social_media.py

  # Authenticate specific platform
  python scripts/authenticate_social_media.py --platform twitter
  python scripts/authenticate_social_media.py --platform linkedin
  python scripts/authenticate_social_media.py --platform facebook

  # With credentials from environment
  export TWITTER_EMAIL=myusername
  export TWITTER_PASSWORD=mypassword
  python scripts/authenticate_social_media.py --platform twitter

  # Check session status
  python scripts/authenticate_social_media.py --platform twitter --check-session

  # Headless mode (no browser window)
  python scripts/authenticate_social_media.py --platform linkedin --headless
        """
    )

    parser.add_argument(
        "--platform",
        choices=["twitter", "linkedin", "facebook", "all"],
        help="Platform to authenticate"
    )
    parser.add_argument(
        "--username",
        help="Username (for Twitter) or Email (for LinkedIn/Facebook)"
    )
    parser.add_argument(
        "--password",
        help="Password"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (no GUI)"
    )
    parser.add_argument(
        "--check-session",
        action="store_true",
        help="Check existing session status instead of authenticating"
    )
    parser.add_argument(
        "--vault",
        default="./vault",
        help="Path to vault directory"
    )

    args = parser.parse_args()

    # Initialize authenticator
    auth = SocialMediaAuthenticator(vault_path=args.vault)

    # Check session mode
    if args.check_session:
        if not args.platform or args.platform == "all":
            print("Please specify a platform with --platform")
            sys.exit(1)

        print(f"\n📋 Checking {args.platform.upper()} session status...\n")
        result = auth.check_session(args.platform)
        print_auth_result(args.platform, result)
        sys.exit(0 if result.get("status") == "valid" else 1)

    # Authenticate mode
    if args.platform and args.platform != "all":
        # Single platform
        result = auth.authenticate(
            platform=args.platform,
            headless=args.headless,
            username=args.username,
            password=args.password
        )
        print_auth_result(args.platform, result)
        sys.exit(0 if result.get("status") in ["logged_in", "already_logged_in", "valid"] else 1)

    elif args.platform == "all":
        # Authenticate all platforms
        platforms = ["twitter", "linkedin", "facebook"]
        results = {}

        for platform in platforms:
            print(f"\n\n{'#'*60}")
            print(f"#  Authenticating {platform.upper()}")
            print(f"{'#'*60}")

            result = auth.authenticate(
                platform=platform,
                headless=args.headless,
                username=args.username,
                password=args.password
            )
            results[platform] = result
            print_auth_result(platform, result)

        # Summary
        print(f"\n{'='*60}")
        print(f"  Authentication Summary")
        print(f"{'='*60}\n")

        success_count = sum(1 for r in results.values() if r.get("status") in ["logged_in", "already_logged_in"])
        print(f"  Successful: {success_count}/{len(platforms)}")

        for platform, result in results.items():
            status_icon = "✅" if result.get("status") in ["logged_in", "already_logged_in"] else "❌"
            print(f"  {status_icon} {platform}: {result.get('status', 'unknown')}")

        sys.exit(0 if success_count == len(platforms) else 1)

    else:
        # Interactive mode - show menu
        print("\n" + "="*60)
        print("  Social Media Authentication")
        print("="*60)
        print("\nSelect platform to authenticate:\n")
        print("  1. Twitter/X")
        print("  2. LinkedIn")
        print("  3. Facebook")
        print("  4. Check session status")
        print("  5. Exit")
        print()

        while True:
            choice = input("Enter choice (1-5): ").strip()

            if choice == "1":
                result = auth.authenticate("twitter", headless=args.headless)
                print_auth_result("twitter", result)
            elif choice == "2":
                result = auth.authenticate("linkedin", headless=args.headless)
                print_auth_result("linkedin", result)
            elif choice == "3":
                result = auth.authenticate("facebook", headless=args.headless)
                print_auth_result("facebook", result)
            elif choice == "4":
                platform = input("Enter platform (twitter/linkedin/facebook): ").strip().lower()
                if platform in auth.platforms:
                    result = auth.check_session(platform)
                    print_auth_result(platform, result)
                else:
                    print(f"Invalid platform: {platform}")
            elif choice == "5":
                print("\nGoodbye!\n")
                break
            else:
                print("Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
