#!/usr/bin/env python3

import requests
import os

# Test the environment variable key
env_key = os.getenv('OPENROUTER_API_KEY')
print('Testing env key:', env_key[:20], '...')

headers = {
    'Authorization': 'Bearer ' + env_key,
    'Content-Type': 'application/json',
    'HTTP-Referer': 'http://localhost:8000',
    'X-Title': 'AI Trading System'
}

payload = {
    'model': 'anthropic/claude-3-sonnet',
    'messages': [{'role': 'user', 'content': 'Test message'}],
    'max_tokens': 100
}

response = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=payload)
print('Status:', response.status_code)
if response.status_code != 200:
    print('Error:', response.text)
else:
    print('Success!')