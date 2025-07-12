#!/usr/bin/env python3
"""
API Key Testing Script
Tests all API keys and shows exactly what's working vs using mock data
"""

import os
import sys
sys.path.append('core')
import json
import asyncio
import aiohttp
import requests
from datetime import datetime
from secrets_manager import SecretsManager

def load_config():
    """Load configuration from config.json"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        return {}

def get_api_key(key_name):
    """Get API key from environment or config"""
    # Try environment variable first
    env_key = os.getenv(key_name)
    if env_key and env_key != f"YOUR_{key_name}":
        return env_key
    
    # Try config file
    config = load_config()
    config_key = config.get('api_credentials', {}).get(key_name.lower())
    if config_key and not config_key.startswith("YOUR_"):
        return config_key
    
    return None

async def test_anthropic_api():
    """Test Anthropic Claude API"""
    api_key = get_api_key('ANTHROPIC_API_KEY')
    
    if not api_key:
        return {
            "service": "Anthropic Claude",
            "status": "❌ API KEY MISSING",
            "message": "USING MOCK DATA - Set ANTHROPIC_API_KEY environment variable",
            "using_mock": True
        }
    
    try:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=10) as response:
                if response.status == 200:
                    return {
                        "service": "Anthropic Claude",
                        "status": "✅ WORKING",
                        "message": "Real Claude API responses available",
                        "using_mock": False
                    }
                else:
                    error_text = await response.text()
                    return {
                        "service": "Anthropic Claude",
                        "status": "❌ API ERROR",
                        "message": f"USING MOCK DATA - API Error: {response.status}",
                        "using_mock": True,
                        "error": error_text[:100]
                    }
    except Exception as e:
        return {
            "service": "Anthropic Claude",
            "status": "❌ CONNECTION ERROR",
            "message": f"USING MOCK DATA - Error: {str(e)}",
            "using_mock": True
        }

async def test_openai_api():
    """Test OpenAI API"""
    api_key = get_api_key('OPENAI_API_KEY')
    
    if not api_key:
        return {
            "service": "OpenAI ChatGPT",
            "status": "❌ API KEY MISSING",
            "message": "USING MOCK DATA - Set OPENAI_API_KEY environment variable",
            "using_mock": True
        }
    
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=10) as response:
                if response.status == 200:
                    return {
                        "service": "OpenAI ChatGPT",
                        "status": "✅ WORKING",
                        "message": "Real ChatGPT API responses available",
                        "using_mock": False
                    }
                else:
                    error_text = await response.text()
                    return {
                        "service": "OpenAI ChatGPT",
                        "status": "❌ API ERROR",
                        "message": f"USING MOCK DATA - API Error: {response.status}",
                        "using_mock": True,
                        "error": error_text[:100]
                    }
    except Exception as e:
        return {
            "service": "OpenAI ChatGPT",
            "status": "❌ CONNECTION ERROR",
            "message": f"USING MOCK DATA - Error: {str(e)}",
            "using_mock": True
        }

def test_perplexity_api():
    """Test Perplexity API"""
    api_key = get_api_key('PERPLEXITY_API_KEY')
    
    if not api_key:
        return {
            "service": "Perplexity AI",
            "status": "❌ API KEY MISSING",
            "message": "USING MOCK DATA - Set PERPLEXITY_API_KEY environment variable",
            "using_mock": True
        }
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return {
                "service": "Perplexity AI",
                "status": "✅ WORKING",
                "message": "Real Perplexity stock discovery available",
                "using_mock": False
            }
        else:
            return {
                "service": "Perplexity AI",
                "status": "❌ API ERROR",
                "message": f"USING MOCK DATA - API Error: {response.status_code}",
                "using_mock": True,
                "error": response.text[:100]
            }
    except Exception as e:
        return {
            "service": "Perplexity AI",
            "status": "❌ CONNECTION ERROR",
            "message": f"USING MOCK DATA - Error: {str(e)}",
            "using_mock": True
        }

def test_yfinance():
    """Test Yahoo Finance (free, no API key needed)"""
    try:
        import yfinance as yf
        
        # Test getting stock data
        stock = yf.Ticker("AAPL")
        hist = stock.history(period="1d")
        
        if not hist.empty:
            return {
                "service": "Yahoo Finance",
                "status": "✅ WORKING",
                "message": "Real-time stock data available",
                "using_mock": False
            }
        else:
            return {
                "service": "Yahoo Finance",
                "status": "❌ NO DATA",
                "message": "USING MOCK DATA - No stock data returned",
                "using_mock": True
            }
    except Exception as e:
        return {
            "service": "Yahoo Finance",
            "status": "❌ ERROR",
            "message": f"USING MOCK DATA - Error: {str(e)}",
            "using_mock": True
        }

async def main():
    """Test all APIs and show status"""
    
    print("🔍 API KEY TESTING SYSTEM")
    print("=" * 80)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test all APIs
    tests = [
        await test_anthropic_api(),
        await test_openai_api(),
        test_perplexity_api(),
        test_yfinance()
    ]
    
    print("📊 API STATUS REPORT:")
    print("-" * 50)
    
    using_mock_count = 0
    
    for test in tests:
        status_color = "🟢" if test["status"].startswith("✅") else "🔴"
        print(f"{status_color} {test['service']}: {test['status']}")
        print(f"   {test['message']}")
        
        if test.get("using_mock", False):
            using_mock_count += 1
            print(f"   ⚠️  WARNING: This service is using MOCK/FAKE data!")
        
        if "error" in test:
            print(f"   📝 Error Details: {test['error']}")
        
        print()
    
    print("=" * 80)
    print("🎯 SUMMARY:")
    
    if using_mock_count == 0:
        print("✅ ALL SYSTEMS USING REAL-TIME DATA")
        print("🚀 Your system is fully operational with live APIs!")
    else:
        print(f"⚠️  {using_mock_count} services using MOCK DATA")
        print("🔧 Fix API keys to get real-time data")
    
    print()
    print("💡 TO FIX API ISSUES:")
    print("1. Set environment variables:")
    print("   export ANTHROPIC_API_KEY='your-claude-key'")
    print("   export OPENAI_API_KEY='your-openai-key'") 
    print("   export PERPLEXITY_API_KEY='your-perplexity-key'")
    print()
    print("2. Or update config/config.json with real API keys")
    print()
    print("3. Restart the system after setting keys")

if __name__ == "__main__":
    asyncio.run(main())