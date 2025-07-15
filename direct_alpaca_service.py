#!/usr/bin/env python3
"""
Direct Alpaca Service - Get real portfolio data directly from Alpaca API
"""

import os
import requests
import json
from datetime import datetime
import yfinance as yf

# API Configuration
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"  # Paper trading for safety
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

def get_alpaca_headers():
    """Get headers for Alpaca API requests"""
    return {
        'APCA-API-KEY-ID': ALPACA_API_KEY,
        'APCA-API-SECRET-KEY': ALPACA_SECRET_KEY,
        'Content-Type': 'application/json'
    }

def get_real_portfolio_positions():
    """Get real portfolio positions directly from Alpaca"""
    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        return None
    
    try:
        # Get positions from Alpaca
        response = requests.get(
            f"{ALPACA_BASE_URL}/v2/positions",
            headers=get_alpaca_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            positions_data = response.json()
            processed_positions = []
            
            for pos in positions_data:
                # Get current price from yfinance for accuracy
                try:
                    ticker = yf.Ticker(pos['symbol'])
                    current_price = ticker.history(period='1d')['Close'].iloc[-1]
                except:
                    current_price = float(pos['market_value']) / float(pos['qty']) if float(pos['qty']) > 0 else 0
                
                processed_positions.append({
                    'symbol': pos['symbol'],
                    'qty': float(pos['qty']),
                    'avg_cost': float(pos['avg_entry_price']),
                    'current_price': current_price,
                    'market_value': float(pos['market_value']),
                    'unrealized_pl': float(pos['unrealized_pl']),
                    'unrealized_plpc': float(pos['unrealized_plpc']) * 100
                })
            
            return {
                'positions': processed_positions,
                'source': 'Alpaca Paper Trading API',
                'last_updated': datetime.now()
            }
        else:
            return None
            
    except Exception as e:
        print(f"Error getting Alpaca positions: {e}")
        return None

def get_ai_analysis_for_stock(symbol):
    """Get AI analysis for a stock using OpenRouter"""
    if not OPENROUTER_API_KEY:
        return {
            'claude_score': 'API key needed',
            'actionable_recommendation': 'Configure OpenRouter API key for analysis',
            'risk_analysis': 'Unable to analyze without API key'
        }
    
    try:
        # Get basic stock info
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period='30d')
        
        if hist.empty:
            return {
                'claude_score': 'Insufficient data',
                'actionable_recommendation': 'Unable to analyze - no price data available',
                'risk_analysis': 'No historical data available'
            }
        
        current_price = hist['Close'].iloc[-1]
        price_change_30d = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
        
        # Generate AI analysis using OpenRouter
        prompt = f"""
        Analyze {symbol} stock:
        Current Price: ${current_price:.2f}
        30-day Change: {price_change_30d:.1f}%
        Company: {info.get('longName', symbol)}
        
        Provide:
        1. Buy/Sell/Hold recommendation with confidence %
        2. Brief actionable recommendation (1 sentence)
        3. Key risk factors (1 sentence)
        """
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "anthropic/claude-3-haiku",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200
            },
            timeout=10
        )
        
        if response.status_code == 200:
            ai_response = response.json()
            content = ai_response['choices'][0]['message']['content']
            
            # Parse the response
            lines = content.split('\n')
            recommendation = lines[0] if lines else "HOLD (50%)"
            actionable = lines[1] if len(lines) > 1 else "Monitor position"
            risk = lines[2] if len(lines) > 2 else "Standard market risk"
            
            return {
                'claude_score': recommendation,
                'actionable_recommendation': actionable,
                'risk_analysis': risk
            }
        else:
            return {
                'claude_score': 'Analysis unavailable',
                'actionable_recommendation': 'Unable to get AI analysis at this time',
                'risk_analysis': 'Analysis service unavailable'
            }
            
    except Exception as e:
        return {
            'claude_score': 'Error',
            'actionable_recommendation': f'Analysis error: {str(e)[:50]}...',
            'risk_analysis': 'Unable to analyze due to technical issues'
        }

def execute_trade_order(symbol, quantity, side):
    """Execute a trade order through Alpaca"""
    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        return {"error": "Alpaca API keys not configured"}
    
    try:
        order_data = {
            "symbol": symbol,
            "qty": str(quantity),
            "side": side,
            "type": "market",
            "time_in_force": "day"
        }
        
        response = requests.post(
            f"{ALPACA_BASE_URL}/v2/orders",
            headers=get_alpaca_headers(),
            json=order_data,
            timeout=10
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            return {"error": f"Order failed: {response.text}"}
            
    except Exception as e:
        return {"error": f"Trade execution error: {str(e)}"}

def is_api_configured():
    """Check if APIs are properly configured"""
    return bool(ALPACA_API_KEY and ALPACA_SECRET_KEY)