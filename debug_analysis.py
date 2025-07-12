#!/usr/bin/env python3
"""Debug portfolio analysis step by step"""

import asyncio
import sys
sys.path.append('.')
from core.live_portfolio_engine import LivePortfolioEngine
from core.comprehensive_intelligence_engine import ComprehensiveIntelligenceEngine

async def debug_analysis():
    print("🔍 DEBUGGING PORTFOLIO ANALYSIS STEP BY STEP")
    print("=" * 60)
    
    # Step 1: Get intelligence
    print("Step 1: Gathering intelligence...")
    intel_engine = ComprehensiveIntelligenceEngine()
    intelligence = await intel_engine.gather_comprehensive_intelligence('BYND')
    print("✅ Intelligence gathered successfully")
    
    # Step 2: Test the analysis method directly
    print("\nStep 2: Testing analysis method...")
    engine = LivePortfolioEngine()
    
    try:
        # Call the analysis method that's failing
        recommendation, confidence = await engine._analyze_with_intelligence(
            ticker='BYND',
            price=7.50,
            day_change=-2.0,
            unrealized_pl=-25.0,  # 25% loss
            intelligence=intelligence
        )
        print(f"✅ Analysis completed: {recommendation} ({confidence}%)")
        
    except Exception as e:
        print(f"❌ Analysis failed at: {e}")
        
        # Let's trace exactly where it fails
        print("\nDebugging specific steps...")
        
        try:
            print("Testing reddit sentiment access...")
            reddit_sentiment = intelligence.reddit_sentiment.get('sentiment', 'neutral')
            print(f"✅ Reddit sentiment: {reddit_sentiment}")
        except Exception as e2:
            print(f"❌ Reddit sentiment failed: {e2}")
            
        try:
            print("Testing options flow access...")
            options_sentiment = intelligence.options_flow.get('sentiment', 'neutral')
            print(f"✅ Options sentiment: {options_sentiment}")
        except Exception as e3:
            print(f"❌ Options flow failed: {e3}")
            
        try:
            print("Testing breaking news access...")
            news_count = len(intelligence.breaking_news)
            print(f"✅ News count: {news_count}")
        except Exception as e4:
            print(f"❌ News count failed: {e4}")

if __name__ == "__main__":
    asyncio.run(debug_analysis())