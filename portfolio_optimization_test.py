#!/usr/bin/env python3
"""Test REAL portfolio optimization recommendations"""

import asyncio
import sys
sys.path.append('.')
from core.live_portfolio_engine import LivePortfolioEngine

async def get_optimization_recommendations():
    print("🎯 SQUEEZE ALPHA - PORTFOLIO OPTIMIZATION ANALYSIS")
    print("=" * 70)
    print("💰 Portfolio Value: $99,809.68")
    print("📊 Analyzing 14 positions for optimization opportunities...")
    print("=" * 70)
    
    engine = LivePortfolioEngine()
    portfolio = await engine.get_live_portfolio()
    
    # Categorize recommendations
    buy_recs = []
    sell_recs = []
    weak_holds = []
    strong_holds = []
    
    for position in portfolio:
        if hasattr(position, 'ai_recommendation'):
            if position.ai_recommendation == 'BUY':
                buy_recs.append(position)
            elif position.ai_recommendation == 'SELL':
                sell_recs.append(position)
            elif position.ai_recommendation == 'HOLD':
                if position.ai_confidence < 70:
                    weak_holds.append(position)
                else:
                    strong_holds.append(position)
    
    print(f"\n🔥 SELL RECOMMENDATIONS ({len(sell_recs)} positions)")
    print("-" * 50)
    for pos in sell_recs:
        print(f"📉 {pos.ticker}: {pos.ai_confidence}% confidence")
        print(f"   Current: ${pos.market_value:.2f} ({pos.unrealized_pl_percent:.1f}%)")
        print(f"   Action: {pos.position_size_rec} to {pos.target_allocation}%")
        print(f"   Thesis: {pos.thesis[:80]}...")
        print()
    
    print(f"\n⚠️  WEAK HOLDS ({len(weak_holds)} positions)")
    print("-" * 50)
    for pos in weak_holds:
        print(f"🤔 {pos.ticker}: {pos.ai_confidence}% confidence")
        print(f"   Current: ${pos.market_value:.2f} ({pos.unrealized_pl_percent:.1f}%)")
        print(f"   Risk: {pos.risk_level}")
        print()
    
    print(f"\n📈 BUY RECOMMENDATIONS ({len(buy_recs)} positions)")
    print("-" * 50)
    for pos in buy_recs:
        print(f"🚀 {pos.ticker}: {pos.ai_confidence}% confidence")
        print(f"   Current: ${pos.market_value:.2f} ({pos.unrealized_pl_percent:.1f}%)")
        print(f"   Action: {pos.position_size_rec} to {pos.target_allocation}%")
        print()
    
    print(f"\n✅ STRONG HOLDS ({len(strong_holds)} positions)")
    print("-" * 50)
    for pos in strong_holds:
        print(f"💪 {pos.ticker}: {pos.ai_confidence}% confidence - ${pos.market_value:.2f}")
    
    # Portfolio-level recommendations
    total_sell_value = sum(pos.market_value for pos in sell_recs)
    total_weak_value = sum(pos.market_value for pos in weak_holds)
    
    print(f"\n🎯 PORTFOLIO OPTIMIZATION SUMMARY")
    print("=" * 50)
    print(f"💰 Total portfolio value: $99,809.68")
    print(f"📉 Value to consider selling: ${total_sell_value:.2f}")
    print(f"⚠️  Value in weak positions: ${total_weak_value:.2f}")
    print(f"🔄 Potential rebalancing: ${total_sell_value + total_weak_value:.2f}")
    
    if sell_recs or weak_holds:
        print(f"\n📋 NEXT STEPS:")
        print(f"1. Review sell recommendations - consider exiting underperformers")
        print(f"2. Monitor weak holds - reduce if confidence drops further") 
        print(f"3. Reallocate freed capital to stronger opportunities")
        print(f"4. Consider adding Twitter/Benzinga APIs for enhanced analysis")

if __name__ == "__main__":
    asyncio.run(get_optimization_recommendations())