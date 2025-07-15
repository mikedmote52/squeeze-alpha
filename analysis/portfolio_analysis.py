#!/usr/bin/env python3
"""
Comprehensive Portfolio Analysis Script
Analyzes each position with AI recommendations
"""

import requests
import json
import yfinance as yf
from datetime import datetime, timedelta

# Get portfolio positions from real Alpaca API
def get_real_portfolio_positions():
    """Get real portfolio positions from Alpaca API"""
    try:
        import os
        import requests
        
        ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
        ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
        ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            print("❌ Alpaca API keys not configured")
            return {}
        
        headers = {
            'APCA-API-KEY-ID': ALPACA_API_KEY,
            'APCA-API-SECRET-KEY': ALPACA_SECRET_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{ALPACA_BASE_URL}/v2/positions", headers=headers, timeout=10)
        
        if response.status_code == 200:
            alpaca_positions = response.json()
            positions = {}
            
            for pos in alpaca_positions:
                positions[pos["symbol"]] = {
                    "quantity": float(pos["qty"]),
                    "market_value": float(pos["market_value"]),
                    "unrealized_pl": float(pos["unrealized_pl"]),
                    "current_price": float(pos["current_price"])
                }
            
            return positions
        else:
            print(f"❌ Alpaca API error: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"❌ Error getting real portfolio: {e}")
        return {}

positions = get_real_portfolio_positions()

def analyze_stock(ticker, position_data):
    """Analyze individual stock with AI and technical analysis"""
    
    try:
        # Get stock data
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="3mo")
        
        # Calculate key metrics
        current_price = position_data["current_price"]
        avg_cost = (position_data["market_value"] - position_data["unrealized_pl"]) / position_data["quantity"]
        gain_loss_pct = position_data["unrealized_pl"] / (position_data["market_value"] - position_data["unrealized_pl"]) * 100
        
        # Technical analysis
        recent_high = hist['High'].tail(20).max()
        recent_low = hist['Low'].tail(20).min()
        volume_avg = hist['Volume'].tail(20).mean()
        
        # Short interest data
        short_interest = info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0
        
        analysis = {
            "ticker": ticker,
            "company_name": info.get('longName', ticker),
            "sector": info.get('sector', 'Unknown'),
            "current_price": current_price,
            "avg_cost": round(avg_cost, 2),
            "gain_loss_pct": round(gain_loss_pct, 2),
            "position_size": position_data["market_value"],
            "quantity": position_data["quantity"],
            
            # Technical levels
            "recent_high": round(recent_high, 2),
            "recent_low": round(recent_low, 2),
            "distance_from_high": round((recent_high - current_price) / current_price * 100, 1),
            "distance_from_low": round((current_price - recent_low) / recent_low * 100, 1),
            
            # Squeeze metrics
            "short_interest": round(short_interest, 1),
            "market_cap": info.get('marketCap', 0),
            "avg_volume": int(volume_avg) if volume_avg > 0 else 0,
            
            # Risk assessment
            "volatility": round(hist['Close'].pct_change().std() * 100, 2),
            "beta": info.get('beta', 1.0)
        }
        
        return analysis
        
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return None

def get_ai_recommendation(analysis):
    """Get AI-powered recommendation for the stock"""
    
    if analysis["gain_loss_pct"] > 15:
        action = "TAKE_PROFITS"
        rationale = f"Strong gains of {analysis['gain_loss_pct']}% - consider taking partial profits"
    elif analysis["gain_loss_pct"] < -20:
        action = "CONSIDER_STOP_LOSS"
        rationale = f"Significant loss of {analysis['gain_loss_pct']}% - evaluate exit strategy"
    elif analysis["short_interest"] > 20:
        action = "HOLD_FOR_SQUEEZE"
        rationale = f"High short interest {analysis['short_interest']}% - squeeze potential"
    elif analysis["distance_from_high"] > 30:
        action = "POTENTIAL_BUY"
        rationale = f"Down {analysis['distance_from_high']}% from recent high - potential value"
    else:
        action = "HOLD"
        rationale = "Monitor position - no immediate action needed"
    
    return action, rationale

def main():
    """Main analysis function"""
    
    print("🎯 SQUEEZE ALPHA PORTFOLIO ANALYSIS")
    print("=" * 60)
    
    total_value = sum([pos["market_value"] for pos in positions.values()])
    total_pl = sum([pos["unrealized_pl"] for pos in positions.values()])
    
    print(f"📊 PORTFOLIO SUMMARY:")
    print(f"Total Value: ${total_value:,.2f}")
    print(f"Total P&L: ${total_pl:,.2f} ({total_pl/total_value*100:.2f}%)")
    print()
    
    winners = []
    losers = []
    squeeze_candidates = []
    
    for ticker, pos_data in positions.items():
        print(f"🔍 ANALYZING {ticker}...")
        
        analysis = analyze_stock(ticker, pos_data)
        if not analysis:
            continue
            
        action, rationale = get_ai_recommendation(analysis)
        
        print(f"📈 {ticker} ({analysis['company_name']})")
        print(f"   Sector: {analysis['sector']}")
        print(f"   Price: ${analysis['current_price']} (Avg Cost: ${analysis['avg_cost']})")
        print(f"   P&L: {analysis['gain_loss_pct']}%")
        print(f"   Position: {analysis['quantity']} shares (${analysis['position_size']:,.2f})")
        print(f"   Short Interest: {analysis['short_interest']}%")
        print(f"   Volatility: {analysis['volatility']}%")
        print(f"   📍 RECOMMENDATION: {action}")
        print(f"   💡 RATIONALE: {rationale}")
        
        # Categorize positions
        if analysis['gain_loss_pct'] > 5:
            winners.append((ticker, analysis['gain_loss_pct']))
        elif analysis['gain_loss_pct'] < -5:
            losers.append((ticker, analysis['gain_loss_pct']))
            
        if analysis['short_interest'] > 15:
            squeeze_candidates.append((ticker, analysis['short_interest']))
        
        print("-" * 50)
    
    # Summary recommendations
    print("\n🎯 PORTFOLIO MANAGEMENT SUMMARY:")
    print("=" * 50)
    
    if winners:
        print("🏆 TOP WINNERS (Consider Profit Taking):")
        for ticker, gain in sorted(winners, key=lambda x: x[1], reverse=True):
            print(f"   {ticker}: +{gain:.1f}%")
    
    if losers:
        print("\n⚠️  POSITIONS AT RISK (Consider Stops):")
        for ticker, loss in sorted(losers, key=lambda x: x[1]):
            print(f"   {ticker}: {loss:.1f}%")
    
    if squeeze_candidates:
        print("\n🚀 SQUEEZE CANDIDATES (Hold for Potential):")
        for ticker, short_pct in sorted(squeeze_candidates, key=lambda x: x[1], reverse=True):
            print(f"   {ticker}: {short_pct:.1f}% short interest")
    
    print(f"\n💼 PORTFOLIO ALLOCATION:")
    print(f"   Largest Position: {max(positions.items(), key=lambda x: x[1]['market_value'])[0]}")
    print(f"   Most Profitable: {max(positions.items(), key=lambda x: x[1]['unrealized_pl'])[0]}")
    print(f"   Biggest Loser: {min(positions.items(), key=lambda x: x[1]['unrealized_pl'])[0]}")

if __name__ == "__main__":
    main()