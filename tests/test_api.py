# -*- coding: utf-8 -*-
"""
Simple test for DeepSeek API
"""

import os
from dotenv import load_dotenv

load_dotenv()

llm_api_key = os.getenv("LLM_API_KEY", "")

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=llm_api_key,
    base_url="https://api.deepseek.com",
    timeout=60,
)

messages = [
    {"role": "system", "content": "You are a helpful assistant. Respond in Chinese."},
    {"role": "user", "content": "Hello, please respond with: OK"}
]

try:
    response = llm.invoke(messages)
    print(f"Response: {response.content}")
except Exception as e:
    print(f"Error: {e}")
