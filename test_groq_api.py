"""Test script to diagnose Groq API issues with the specific model and prompt."""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', "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")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

def test_completion():
    """Test a basic chat completion to diagnose API issues."""
    
    print(f"Testing Groq API with model: {MODEL}")
    
    # Use a simpler prompt for testing
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Extract the title, company, and location from this text: 'Software Engineer at Google in Mountain View'"}
    ]
    
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 150
    }
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
        
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! Response content:")
            print(json.dumps(result, indent=2))
            content = result["choices"][0]["message"]["content"]
            print(f"\nExtracted content: {content}")
        else:
            print(f"Error response: {response.text}")
            
            if response.status_code == 401 or response.status_code == 403:
                print("Authentication error - please check your API key")
            elif response.status_code == 404:
                print(f"Model '{MODEL}' may not be available")
            elif response.status_code == 429:
                print("Rate limit exceeded")
                
    except Exception as e:
        print(f"Exception during API call: {str(e)}")

if __name__ == "__main__":
    test_completion()
