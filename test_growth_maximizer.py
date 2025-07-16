#!/usr/bin/env python3
"""
Quick test of the Growth Maximizer system
"""

import sys
import asyncio

# Add paths
sys.path.append('./growth_system')
sys.path.append('./core')

from integrated_growth_system import IntegratedGrowthSystem

async def test_growth_maximizer():
    print("🚀 Testing Growth Maximizer System")
    print("=" * 50)
    
    # Initialize system
    system = IntegratedGrowthSystem()
    init_result = system.initialize_system()
    
    print(f"✅ System Status: {init_result['status']}")
    print(f"🎯 Goal: {init_result['goal']}")
    
    # Run growth cycle
    print("\n🔄 Running growth cycle...")
    result = await system.execute_growth_cycle()
    
    if result['status'] == 'success':
        cycle_data = result['cycle_result']
        print(f"\n📊 Results:")
        print(f"  • Portfolio Value: ${result.get('portfolio_value', 0):,.2f}")
        print(f"  • Opportunities Found: {cycle_data['opportunities_found']}")
        print(f"  • Trading Signals: {len(cycle_data['trading_signals'])}")
        print(f"  • Expected Growth: {cycle_data['expected_growth']:.2%}")
        print(f"  • Risk Level: {cycle_data['risk_assessment']}")
        
        if cycle_data['top_opportunities']:
            print(f"\n🏆 Top Opportunities:")
            for i, opp in enumerate(cycle_data['top_opportunities'][:3], 1):
                print(f"  {i}. {opp['symbol']} - Score: {opp['growth_score']:.1f}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print("\n✅ Growth Maximizer test complete!")

if __name__ == "__main__":
    asyncio.run(test_growth_maximizer())