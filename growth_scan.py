#!/usr/bin/env python3
"""
Growth Maximizer - Quick Command Line Scanner
Run this anytime to get AI-powered growth analysis of your portfolio
"""

import sys
import asyncio
import json
from datetime import datetime

# Add paths
sys.path.append('./growth_system')
sys.path.append('./core')

from integrated_growth_system import IntegratedGrowthSystem

def print_separator():
    print("=" * 70)

def print_header():
    print("🚀 GROWTH MAXIMIZER - PORTFOLIO ANALYSIS")
    print_separator()
    print("🎯 Goal: Maximize investment growth over short time periods")
    print("🛡️  ZERO MOCK DATA - Real portfolio analysis only")
    print_separator()

def print_portfolio_metrics(portfolio_value, opportunities, signals, expected_growth, risk):
    print("📊 PORTFOLIO METRICS")
    print_separator()
    print(f"💰 Portfolio Value: ${portfolio_value:,.2f}")
    print(f"🎯 Opportunities Found: {opportunities}")
    print(f"📈 Trading Signals: {signals}")
    print(f"📊 Expected Growth: {expected_growth:.2%}")
    print(f"⚠️  Risk Level: {risk.upper()}")
    print_separator()

def print_opportunities(opportunities):
    if not opportunities:
        print("⚠️  No opportunities found - system needs real data connection")
        return
    
    print("🏆 TOP GROWTH OPPORTUNITIES")
    print_separator()
    
    for i, opp in enumerate(opportunities[:5], 1):
        print(f"{i}. {opp['symbol']}")
        print(f"   📊 Growth Score: {opp['growth_score']:.1f}/100")
        print(f"   🎯 Confidence: {opp['confidence']:.1%}")
        print(f"   💵 Entry Price: ${opp['entry_price']:.2f}")
        print(f"   🎪 Target Price: ${opp['target_price']:.2f}")
        print(f"   🔥 Potential Return: {((opp['target_price'] - opp['entry_price']) / opp['entry_price']):.2%}")
        print(f"   ⚠️  Risk Level: {opp['risk_level'].upper()}")
        print()

def print_trading_signals(signals):
    if not signals:
        print("📍 No trading signals generated")
        return
    
    print("📈 TRADING SIGNALS")
    print_separator()
    
    for signal in signals:
        action_emoji = "🟢" if signal['action'] == 'BUY' else "🔴" if signal['action'] == 'SELL' else "🟡"
        print(f"{action_emoji} {signal['action']} {signal['symbol']}")
        print(f"   📊 Quantity: {signal['quantity']:.2f} shares")
        print(f"   💪 Signal Strength: {signal['signal_strength']}")
        print(f"   📈 Expected Return: {signal['expected_return']:.2%}")
        print()

async def main():
    print_header()
    
    try:
        # Initialize system
        system = IntegratedGrowthSystem()
        init_result = system.initialize_system()
        
        if init_result['status'] != 'initialized':
            print("❌ System initialization failed")
            return
        
        print("🔄 Running growth analysis...")
        print()
        
        # Execute growth cycle
        result = await system.execute_growth_cycle()
        
        if result['status'] == 'success':
            cycle_data = result['cycle_result']
            portfolio_value = result.get('portfolio_value', 0)
            
            # Print metrics
            print_portfolio_metrics(
                portfolio_value,
                cycle_data['opportunities_found'],
                len(cycle_data['trading_signals']),
                cycle_data['expected_growth'],
                cycle_data['risk_assessment']
            )
            
            # Print opportunities
            print_opportunities(cycle_data['top_opportunities'])
            
            # Print trading signals
            print_trading_signals(cycle_data['trading_signals'])
            
            print_separator()
            print("✅ Growth analysis complete!")
            print(f"📅 Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ System error: {e}")
        print("💡 Try running the analysis again")

if __name__ == "__main__":
    asyncio.run(main())