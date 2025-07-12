#!/usr/bin/env python3
"""Debug intelligence data structure"""

import asyncio
import sys
sys.path.append('.')
from core.comprehensive_intelligence_engine import ComprehensiveIntelligenceEngine

async def debug_intelligence():
    print("🔍 DEBUGGING INTELLIGENCE DATA STRUCTURE")
    print("=" * 60)
    
    engine = ComprehensiveIntelligenceEngine()
    intelligence = await engine.gather_comprehensive_intelligence('BYND')
    
    print(f"📊 Intelligence object type: {type(intelligence)}")
    print(f"📊 Ticker: {intelligence.ticker}")
    print(f"📊 Timestamp: {intelligence.timestamp}")
    
    print(f"\n🔍 Reddit sentiment type: {type(intelligence.reddit_sentiment)}")
    print(f"🔍 Reddit sentiment value: {intelligence.reddit_sentiment}")
    
    print(f"\n🔍 Twitter sentiment type: {type(intelligence.twitter_sentiment)}")
    print(f"🔍 Twitter sentiment value: {intelligence.twitter_sentiment}")
    
    print(f"\n🔍 Options flow type: {type(intelligence.options_flow)}")
    print(f"🔍 Options flow value: {intelligence.options_flow}")
    
    print(f"\n🔍 Breaking news type: {type(intelligence.breaking_news)}")
    print(f"🔍 Breaking news length: {len(intelligence.breaking_news)}")
    
    # Test the .get() calls that are failing
    try:
        reddit_sentiment = intelligence.reddit_sentiment.get('sentiment', 'neutral')
        print(f"✅ Reddit sentiment extraction worked: {reddit_sentiment}")
    except Exception as e:
        print(f"❌ Reddit sentiment extraction failed: {e}")
        
    try:
        options_sentiment = intelligence.options_flow.get('sentiment', 'neutral')
        print(f"✅ Options sentiment extraction worked: {options_sentiment}")
    except Exception as e:
        print(f"❌ Options sentiment extraction failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_intelligence())