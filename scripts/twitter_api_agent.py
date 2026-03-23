#!/usr/bin/env python3
"""
Twitter API Agent - Post tweets using Twitter API v2

This agent uses the official Twitter API (not browser automation)
for reliable tweet posting.

Usage:
    python scripts/twitter_api_agent.py --tweet "Hello from AI Employee!"
    python scripts/twitter_api_agent.py --test
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import tweepy


class TwitterAPIAgent:
    """Twitter API agent for posting tweets."""
    
    def __init__(self):
        # Get credentials from environment
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        
        # Validate credentials
        if not all([self.bearer_token, self.api_key, self.api_secret, 
                    self.access_token, self.access_token_secret]):
            raise ValueError("Missing Twitter API credentials in .env")
        
        # Initialize client
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
        
        print("✅ Twitter API Agent initialized")
    
    def test_connection(self):
        """Test Twitter API connection."""
        try:
            # Get authenticated user's info
            me = self.client.get_me()
            
            if me.data:
                print(f"✅ Connected to Twitter API")
                print(f"   Username: @{me.data.username}")
                print(f"   Name: {me.data.name}")
                print(f"   ID: {me.data.id}")
                return True
            else:
                print("❌ Could not get user info")
                return False
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def post_tweet(self, text: str) -> dict:
        """Post a tweet to Twitter."""
        try:
            # Validate tweet length
            if len(text) > 280:
                return {
                    "status": "error",
                    "message": "Tweet exceeds 280 characters"
                }
            
            # Post tweet
            response = self.client.create_tweet(text=text)
            
            if response.data:
                tweet_id = response.data["id"]
                tweet_url = f"https://twitter.com/developerh64043/status/{tweet_id}"
                
                return {
                    "status": "success",
                    "tweet_id": tweet_id,
                    "tweet_url": tweet_url,
                    "text": text
                }
            else:
                return {
                    "status": "error",
                    "message": "No response data from Twitter"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_recent_tweets(self, count: int = 5):
        """Get recent tweets from authenticated user."""
        try:
            # Get user ID first
            me = self.client.get_me()
            user_id = me.data.id
            
            # Get tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=count,
                tweet_fields=["created_at", "public_metrics"]
            )
            
            if tweets.data:
                return {
                    "status": "success",
                    "tweets": [
                        {
                            "id": t.id,
                            "text": t.text,
                            "created_at": t.created_at,
                            "metrics": t.public_metrics
                        }
                        for t in tweets.data
                    ]
                }
            else:
                return {
                    "status": "success",
                    "tweets": []
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


def main():
    parser = argparse.ArgumentParser(description="Twitter API Agent")
    parser.add_argument("--tweet", type=str, help="Tweet text to post")
    parser.add_argument("--test", action="store_true", help="Test Twitter API connection")
    parser.add_argument("--recent", action="store_true", help="Show recent tweets")
    
    args = parser.parse_args()
    
    print("="*70)
    print("  Twitter API Agent")
    print("="*70)
    print()
    
    try:
        agent = TwitterAPIAgent()
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nMake sure all Twitter API credentials are in .env file")
        return 1
    
    if args.test:
        # Test connection
        success = agent.test_connection()
        return 0 if success else 1
    
    elif args.recent:
        # Get recent tweets
        result = agent.get_recent_tweets()
        if result["status"] == "success":
            print(f"📋 Recent Tweets:\n")
            for i, tweet in enumerate(result["tweets"], 1):
                print(f"{i}. {tweet['text'][:100]}...")
                print(f"   Posted: {tweet['created_at']}")
                print(f"   Likes: {tweet['metrics']['like_count']}, Retweets: {tweet['metrics']['retweet_count']}")
                print()
        else:
            print(f"❌ Error: {result['message']}")
        return 0
    
    elif args.tweet:
        # Post tweet
        print(f"📝 Posting tweet:\n   \"{args.tweet}\"\n")
        result = agent.post_tweet(args.tweet)
        
        if result["status"] == "success":
            print(f"✅ Tweet posted successfully!")
            print(f"   Tweet ID: {result['tweet_id']}")
            print(f"   URL: {result['tweet_url']}")
        else:
            print(f"❌ Failed to post tweet")
            print(f"   Error: {result['message']}")
        return 0 if result["status"] == "success" else 1
    
    else:
        # Show help
        parser.print_help()
        print("\n\nExamples:")
        print("  python scripts/twitter_api_agent.py --test")
        print("  python scripts/twitter_api_agent.py --tweet \"Hello World!\"")
        print("  python scripts/twitter_api_agent.py --recent")
        return 0


if __name__ == "__main__":
    sys.exit(main())
