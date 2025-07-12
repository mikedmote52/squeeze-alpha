#!/usr/bin/env python3
"""Quick test to verify system is working"""

import sys
import asyncio
sys.path.append('.')
from core.live_portfolio_engine import LivePortfolioEngine

async def main():
    print("🔍 Testing Squeeze Alpha system...")
    
    try:
        engine = LivePortfolioEngine()
        print("✅ Portfolio engine created")
        
        # Test one position analysis
        portfolio = await engine.get_live_portfolio()
        print(f"✅ Portfolio loaded with {len(portfolio)} positions")
        
        if portfolio:
            sample_holding = portfolio[0]
            print(f"✅ Sample analysis: {sample_holding.get('ticker', 'Unknown')} - {sample_holding.get('ai_recommendation', 'No recommendation')}")
        
        print("🎉 System is working correctly!")
        print("📋 Next steps:")
        print("   1. Get Twitter Bearer Token for enhanced sentiment analysis")
        print("   2. Get Benzinga API key for financial news")
        print("   3. Run: python main.py (for full analysis)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())