#!/usr/bin/env python3
"""
Test script to verify AI conversations between Claude, ChatGPT, and Grok
Saves conversation examples to files for review
"""

import requests
import json
from datetime import datetime
import os

def test_ai_conversations():
    """Test AI conversations and save examples"""
    
    print("🤖 Testing AI Conversations...")
    print("=" * 50)
    
    # Test symbols
    test_symbols = ["AAPL", "TSLA", "NVDA", "AMD"]
    
    conversations = []
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}...")
        
        try:
            # Test main AI analysis endpoint
            response = requests.post(
                "http://localhost:8000/api/ai-analysis",
                json={"symbol": symbol, "context": f"Analyzing {symbol} for investment decision"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                source = data.get('source', 'Unknown')
                agents = data.get('agents', [])
                
                print(f"✅ {symbol}: {len(agents)} AI agents responded")
                print(f"   Source: {source}")
                
                conversation = {
                    'symbol': symbol,
                    'timestamp': datetime.now().isoformat(),
                    'source': source,
                    'agents': []
                }
                
                for agent in agents:
                    agent_name = agent.get('name', 'Unknown')
                    reasoning = agent.get('reasoning', 'No reasoning provided')
                    confidence = agent.get('confidence', 0)
                    
                    print(f"   • {agent_name}: {confidence:.1%} confidence")
                    print(f"     {reasoning[:100]}...")
                    
                    conversation['agents'].append({
                        'name': agent_name,
                        'confidence': confidence,
                        'reasoning': reasoning,
                        'model': agent.get('model', 'Unknown'),
                        'source': agent.get('source', 'Unknown')
                    })
                
                conversations.append(conversation)
                
            else:
                print(f"❌ {symbol}: API error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")
    
    # Save conversations to file
    if conversations:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_conversations_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(conversations, f, indent=2)
        
        print(f"\n📄 Conversations saved to: {filename}")
        
        # Also create a readable summary
        summary_filename = f"ai_conversation_summary_{timestamp}.txt"
        
        with open(summary_filename, 'w') as f:
            f.write("AI Trading System - Conversation Analysis\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for conv in conversations:
                f.write(f"Symbol: {conv['symbol']}\n")
                f.write(f"Source: {conv['source']}\n")
                f.write(f"Agents: {len(conv['agents'])}\n")
                f.write("-" * 30 + "\n")
                
                for agent in conv['agents']:
                    f.write(f"\n{agent['name']} ({agent['confidence']:.1%} confidence):\n")
                    f.write(f"Model: {agent['model']}\n")
                    f.write(f"Source: {agent['source']}\n")
                    f.write(f"Analysis: {agent['reasoning'][:500]}...\n")
                
                f.write("\n" + "=" * 50 + "\n\n")
        
        print(f"📄 Summary saved to: {summary_filename}")
        
        # Check if OpenRouter is actually being used
        openrouter_count = sum(1 for conv in conversations 
                              for agent in conv['agents'] 
                              if 'openrouter' in agent.get('source', '').lower())
        
        local_count = sum(len(conv['agents']) for conv in conversations) - openrouter_count
        
        print(f"\n📈 Analysis Summary:")
        print(f"   OpenRouter AI responses: {openrouter_count}")
        print(f"   Local AI responses: {local_count}")
        
        if openrouter_count > 0:
            print("✅ OpenRouter integration is working!")
            print("🤖 Real conversations between Claude, ChatGPT, and Grok detected")
        else:
            print("⚠️  OpenRouter integration not active")
            print("🔧 Using fallback local AI analysis")
            
        return filename, summary_filename
    else:
        print("❌ No conversations captured")
        return None, None

if __name__ == "__main__":
    test_ai_conversations()