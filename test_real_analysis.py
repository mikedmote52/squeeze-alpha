#!/usr/bin/env python3
"""Test real portfolio analysis for specific positions"""

import asyncio
import sys
sys.path.append('.')
from core.live_portfolio_engine import LivePortfolioEngine

async def test_specific_positions():
    print("🔍 TESTING REAL PORTFOLIO OPTIMIZATION ANALYSIS")
    print("=" * 60)
    
    engine = LivePortfolioEngine()
    
    # Test questionable positions from your portfolio
    test_positions = [
        ('BYND', 'Beyond Meat - plant-based food company'),
        ('BLNK', 'Blink Charging - EV charging network'), 
        ('BTBT', 'Bit Digital - Bitcoin mining'),
        ('NVAX', 'Novavax - COVID vaccine'),
        ('CHPT', 'ChargePoint - EV charging')
    ]
    
    for ticker, description in test_positions:
        print(f"\n📊 ANALYZING {ticker} - {description}")
        print("-" * 50)
        
        try:
            # Get current price data
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            current_price = info.get('currentPrice', 0)
            day_change = info.get('regularMarketChangePercent', 0)
            
            # Simulate portfolio position analysis
            analysis = await engine.generate_ai_recommendation(
                ticker=ticker,
                price=current_price, 
                day_change=day_change,
                unrealized_pl=-20  # Assume 20% loss for testing
            )
            
            print(f"✅ RECOMMENDATION: {analysis['action']}")
            print(f"✅ CONFIDENCE: {analysis['confidence']}%")
            print(f"✅ POSITION SIZING: {analysis['position_sizing']}")
            print(f"✅ TARGET ALLOCATION: {analysis['target_allocation']}%")
            print(f"✅ DATA SOURCES: {analysis.get('data_sources', 'Basic only')}")
            
            # This should give SELL recommendations for poor performers
            if analysis['action'] == 'SELL':
                print(f"🎯 OPTIMIZATION: Consider reducing/exiting {ticker}")
            elif analysis['action'] == 'HOLD' and analysis['confidence'] < 70:
                print(f"⚠️  CAUTION: Weak hold on {ticker}")
                
        except Exception as e:
            print(f"❌ Error analyzing {ticker}: {e}")
    
    print(f"\n🎯 PORTFOLIO OPTIMIZATION SUMMARY:")
    print("The system should identify underperformers and suggest rebalancing")
    print("Currently falling back to basic analysis due to API limitations")

if __name__ == "__main__":
    asyncio.run(test_specific_positions())