#!/usr/bin/env python3
"""Test the complete web integration"""

import sys
import asyncio
sys.path.append('.')
from core.trade_execution_engine import TradeExecutionEngine
from core.live_portfolio_engine import LivePortfolioEngine

async def test_complete_system():
    print("🧪 TESTING COMPLETE TRADE EXECUTION SYSTEM")
    print("=" * 60)
    
    try:
        # Test portfolio analysis
        print("1. Testing portfolio analysis...")
        portfolio_engine = LivePortfolioEngine()
        portfolio = await portfolio_engine.get_live_portfolio()
        print(f"✅ Portfolio loaded: {len(portfolio)} positions")
        
        # Test trade recommendations
        print("\n2. Testing trade recommendations...")
        trade_engine = TradeExecutionEngine()
        recommendations = trade_engine.create_trade_recommendations(portfolio)
        print(f"✅ Generated {len(recommendations)} recommendations")
        
        for rec in recommendations[:3]:  # Show first 3
            print(f"   📊 {rec.ticker}: {rec.action} {rec.recommended_shares} shares ({rec.confidence}%)")
        
        # Test adjustments
        print("\n3. Testing recommendation adjustments...")
        if recommendations:
            first_rec = recommendations[0]
            success = trade_engine.adjust_recommendation(
                ticker=first_rec.ticker,
                user_shares=int(first_rec.recommended_shares * 0.5),
                approved=True
            )
            print(f"✅ Adjustment {'successful' if success else 'failed'}")
        
        # Test portfolio impact
        print("\n4. Testing portfolio impact preview...")
        impact = trade_engine.get_portfolio_impact_preview()
        print(f"✅ Impact calculated: {impact['total_trades']} trades, ${impact['net_cash_change']:.2f} net change")
        
        # Test dry run execution
        print("\n5. Testing dry run execution...")
        executions = await trade_engine.execute_approved_trades(dry_run=True)
        print(f"✅ Dry run completed: {len(executions)} executions")
        
        for execution in executions:
            print(f"   🎯 {execution.ticker}: {execution.status} - {execution.execution_notes}")
        
        print(f"\n🎉 COMPLETE SYSTEM TEST SUCCESSFUL!")
        print(f"   📊 Portfolio: {len(portfolio)} positions")
        print(f"   🎯 Recommendations: {len(recommendations)} generated")
        print(f"   ✅ Ready for web deployment!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_system())