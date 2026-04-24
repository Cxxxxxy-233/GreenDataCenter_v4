# -*- coding: utf-8 -*-
"""
Test DeepSeek API with correct endpoint
"""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LLM_API_KEY", "")
print(f"API Key: {api_key[:10]}...{api_key[-5:]}")

# Try with DeepSeek's actual API endpoint
from langchain_openai import ChatOpenAI

print("\n=== Testing DeepSeek API ===")
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com",
    timeout=60,
)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, please respond with: OK"}
]

try:
    response = llm.invoke(messages)
    print(f"Response: {response.content}")
    print("[SUCCESS] DeepSeek API is working!")
except Exception as e:
    print(f"Error: {e}")
