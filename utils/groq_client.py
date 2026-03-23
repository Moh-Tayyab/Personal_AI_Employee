"""
Groq API Integration for Personal AI Employee

Provides ultra-fast inference (500+ tokens/sec) for:
- Email classification
- Text categorization
- Sentiment analysis
- Quick pre-processing before Claude Code

Usage:
    from utils.groq_client import GroqClient
    
    client = GroqClient()
    response = client.chat("Classify this email as urgent or not: ...")
"""

import os
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GroqClient:
    """Client for Groq API integration."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Model to use (defaults to llama-3.3-70b-versatile)
            base_url: API base URL (defaults to Groq's OpenAI-compatible endpoint)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.base_url = base_url or os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Set it in your .env file or environment."
            )
        
        # Try to import requests, provide helpful error if missing
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError(
                "requests library required. Install with: pip install requests"
            )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1024,
        **kwargs
    ) -> str:
        """
        Send chat completion request to Groq.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional API parameters
            
        Returns:
            Generated text response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        response = self.requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        return data["choices"][0]["message"]["content"]
    
    def classify_text(
        self,
        text: str,
        categories: List[str],
        instructions: Optional[str] = None
    ) -> str:
        """
        Classify text into categories using Groq.
        
        Args:
            text: Text to classify
            categories: List of possible categories
            instructions: Optional classification instructions
            
        Returns:
            Category label
        """
        default_instructions = (
            f"Classify the following text into one of these categories: {', '.join(categories)}. "
            f"Respond with ONLY the category name, nothing else."
        )
        
        messages = [
            {"role": "system", "content": instructions or default_instructions},
            {"role": "user", "content": f"Text to classify:\n{text}"}
        ]
        
        return self.chat(messages, max_tokens=50)
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        Extract keywords from text using Groq.
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords
            
        Returns:
            List of keywords
        """
        messages = [
            {
                "role": "system",
                "content": f"Extract up to {max_keywords} important keywords from the text. Return them as a comma-separated list."
            },
            {"role": "user", "content": text}
        ]
        
        response = self.chat(messages, max_tokens=100)
        return [kw.strip() for kw in response.split(",")]
    
    def summarize(self, text: str, max_length: int = 100) -> str:
        """
        Summarize text using Groq.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length in words
            
        Returns:
            Summary text
        """
        messages = [
            {
                "role": "system",
                "content": f"Summarize the following text in {max_length} words or less."
            },
            {"role": "user", "content": text}
        ]
        
        return self.chat(messages, max_tokens=150)
    
    def is_available(self) -> bool:
        """
        Check if Groq API is available.
        
        Returns:
            True if API responds successfully
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = self.requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False


# Convenience functions for quick use

def get_client() -> GroqClient:
    """Get a configured GroqClient instance."""
    return GroqClient()


def classify_email(text: str) -> str:
    """
    Classify an email using Groq.
    
    Categories: urgent, invoice, important, normal, promotional
    
    Args:
        text: Email text to classify
        
    Returns:
        Category label
    """
    client = get_client()
    return client.classify_text(
        text,
        categories=["urgent", "invoice", "important", "normal", "promotional"]
    )


def detect_urgency(text: str) -> str:
    """
    Detect urgency level in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Urgency level: high, medium, low
    """
    client = get_client()
    return client.classify_text(
        text,
        categories=["high", "medium", "low"],
        instructions="Detect the urgency level of this text. Respond with ONLY: high, medium, or low."
    )


if __name__ == "__main__":
    # Test Groq connection
    print("Testing Groq API connection...")
    
    try:
        client = GroqClient()
        
        if client.is_available():
            print("✅ Groq API is available!")
            
            # Test classification
            test_email = "URGENT: Server is down! Need immediate assistance."
            category = classify_email(test_email)
            print(f"Test classification: '{test_email}' → {category}")
            
            # Test summarization
            test_text = """
            The quarterly financial report shows significant growth in revenue,
            with a 25% increase compared to last quarter. Operating expenses
            remained stable, resulting in improved profit margins. The company
            plans to expand into new markets next quarter.
            """
            summary = client.summarize(test_text)
            print(f"Summary: {summary}")
            
        else:
            print("❌ Groq API is not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
