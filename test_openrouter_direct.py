#!/usr/bin/env python3
"""
Direct test of OpenRouter integration to debug the issue
"""

import requests
import json
import asyncio
import re
from datetime import datetime

# Use the same API key from the backend
OPENROUTER_API_KEY = "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"

async def test_openrouter_direct():
    """Test OpenRouter API directly with the same code from backend"""
    
    print("🔍 Testing OpenRouter Integration Directly...")
    print("=" * 50)
    
    symbol = "AAPL"
    context = "Testing real AI conversations"
    
    # Real AI models for analysis
    models = [
        {"name": "Claude", "model": "anthropic/claude-3-sonnet"},
        {"name": "ChatGPT", "model": "openai/gpt-4"},
        {"name": "Grok", "model": "x-ai/grok-beta"}
    ]
    
    agents = []
    
    # Prompt for financial analysis
    prompt = f"""
    Analyze {symbol} stock for investment decision. Context: {context}
    
    Provide:
    1. Current outlook (bullish/bearish/neutral)
    2. Key factors driving your view
    3. Confidence level (1-10)
    4. Brief reasoning (2-3 sentences max)
    
    Be concise and actionable. Focus on what matters most for trading decisions.
    """
    
    print(f"📝 Prompt: {prompt[:100]}...")
    print(f"🔑 API Key: {OPENROUTER_API_KEY[:20]}...")
    print()
    
    for model_info in models:
        print(f"🤖 Testing {model_info['name']} ({model_info['model']})...")
        
        try:
            # Call OpenRouter API
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "AI Trading System"
            }
            
            payload = {
                "model": model_info["model"],
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            print(f"   📡 Calling OpenRouter API...")
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            print(f"   📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                print(f"   ✅ Success! Response length: {len(ai_response)} chars")
                print(f"   💬 Response preview: {ai_response[:100]}...")
                
                # Extract confidence and reasoning
                confidence = 7.5  # Default confidence
                try:
                    if "confidence" in ai_response.lower():
                        conf_match = re.search(r'confidence.*?(\d+)', ai_response.lower())
                        if conf_match:
                            confidence = float(conf_match.group(1))
                except:
                    pass
                
                agents.append({
                    "name": model_info["name"],
                    "model": model_info["model"],
                    "confidence": confidence / 10.0,  # Normalize to 0-1
                    "reasoning": ai_response[:500],  # Limit length
                    "timestamp": datetime.now().isoformat(),
                    "source": "OpenRouter API"
                })
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   🔍 Error details: {error_data}")
                except:
                    print(f"   🔍 Error text: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            continue
        
        print()
    
    if agents:
        print(f"🎯 SUCCESS! {len(agents)} AI models responded:")
        print("-" * 30)
        
        for agent in agents:
            print(f"✅ {agent['name']}: {agent['confidence']*100:.0f}% confidence")
            print(f"   {agent['reasoning'][:150]}...")
            print()
        
        # Save successful conversation
        conversation_data = {
            "symbol": symbol,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "source": "Direct OpenRouter Test",
            "agents": agents
        }
        
        with open("openrouter_test_success.json", "w") as f:
            json.dump(conversation_data, f, indent=2)
        
        print("💾 Conversation saved to: openrouter_test_success.json")
        
        return True
    else:
        print("❌ FAILED: No AI models responded")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openrouter_direct())
    
    if success:
        print("\n🚀 OpenRouter integration is working!")
        print("💡 The issue is in the backend implementation, not the API.")
    else:
        print("\n💥 OpenRouter API has issues that need to be resolved.")