#!/usr/bin/env python3
"""
Test script to check if GitHub Models API is working
"""
import os
from openai import OpenAI

def test_github_models():
    """Test GitHub Models API connection"""
    
    # Get token
    github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
    
    if not github_token:
        print("❌ No GITHUB_TOKEN found")
        return False
    
    print(f"✅ GitHub Token found: {github_token[:7]}...{github_token[-4:]}")
    
    try:
        # Initialize OpenAI client with GitHub Models endpoint
        client = OpenAI(
            base_url="https://models.github.ai/inference",
            api_key=github_token
        )
        
        print("🔄 Testing GitHub Models API connection...")
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",  # Use the smaller model first
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from GitHub Models!' if this is working."}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        print(f"✅ GitHub Models Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ GitHub Models Error: {e}")
        return False

if __name__ == "__main__":
    test_github_models() 