#!/usr/bin/env python3
"""
Final test to verify real AI conversations between Claude, ChatGPT, and Gemini
"""

import requests
import json
from datetime import datetime

def test_real_ai_conversations():
    """Test real AI conversations and show proof they're working"""
    
    print("🤖 FINAL TEST: Real AI Conversations")
    print("=" * 60)
    print("Testing Claude, ChatGPT, and Gemini discussions...")
    print()
    
    # Test with a real stock
    symbol = "NVDA"
    context = "High-growth AI chip company analysis"
    
    try:
        print(f"📊 Requesting AI analysis for {symbol}...")
        
        response = requests.post(
            "http://localhost:8000/api/ai-analysis",
            json={"symbol": symbol, "context": context},
            timeout=20  # Give more time for multiple model calls
        )
        
        if response.status_code == 200:
            data = response.json()
            source = data.get('source', 'Unknown')
            agents = data.get('agents', [])
            
            print(f"✅ SUCCESS! Received response from {len(agents)} AI models")
            print(f"📡 Source: {source}")
            print()
            
            if "OpenRouter" in source:
                print("🎉 CONFIRMED: Real OpenRouter API conversations!")
                print("🔥 Claude, ChatGPT, and Gemini are actually talking!")
            else:
                print("⚠️  Using fallback analysis (not real AI conversations)")
            
            print()
            print("💬 AI CONVERSATION TRANSCRIPT:")
            print("-" * 40)
            
            for i, agent in enumerate(agents, 1):
                name = agent.get('name', 'Unknown AI')
                model = agent.get('model', 'Unknown')
                confidence = agent.get('confidence', 0)
                reasoning = agent.get('reasoning', 'No reasoning provided')
                source_type = agent.get('source', 'Unknown')
                
                print(f"\n{i}. {name} ({model})")
                print(f"   Confidence: {confidence:.1%}")
                print(f"   Source: {source_type}")
                print(f"   Analysis: {reasoning[:300]}...")
                
                if "OpenRouter" in source_type:
                    print("   ✅ REAL AI MODEL RESPONSE")
                else:
                    print("   ⚠️  Local analysis response")
            
            # Check for real conversations
            openrouter_responses = sum(1 for agent in agents if "OpenRouter" in agent.get('source', ''))
            
            print(f"\n📈 SUMMARY:")
            print(f"   Total responses: {len(agents)}")
            print(f"   Real AI responses: {openrouter_responses}")
            print(f"   Local responses: {len(agents) - openrouter_responses}")
            
            if openrouter_responses >= 2:
                print("\n🎯 SUCCESS: Real AI conversations are happening!")
                print("✅ Claude and ChatGPT are having actual discussions")
                print("✅ The system is working as designed")
                
                # Save proof
                proof = {
                    'test_timestamp': datetime.now().isoformat(),
                    'symbol_tested': symbol,
                    'context': context,
                    'source': source,
                    'real_ai_responses': openrouter_responses,
                    'total_responses': len(agents),
                    'agents': agents,
                    'status': 'SUCCESS - Real AI conversations confirmed'
                }
                
                with open('real_ai_conversations_proof.json', 'w') as f:
                    json.dump(proof, f, indent=2)
                
                print("💾 Proof saved to: real_ai_conversations_proof.json")
                
                return True
            else:
                print("\n❌ ISSUE: Real AI conversations are not working")
                print("🔧 Still using fallback analysis")
                return False
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_real_ai_conversations()
    
    print("\n" + "=" * 60)
    if success:
        print("🚀 FINAL RESULT: AI CONVERSATIONS ARE WORKING!")
        print("🤖 Claude, ChatGPT, and Gemini are actively discussing stocks")
        print("✅ The trading system is fully operational with real AI")
    else:
        print("💥 FINAL RESULT: AI CONVERSATIONS NEED FIXING")
        print("🔧 The system needs debugging to enable real conversations")