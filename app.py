#!/usr/bin/env python3
"""
Simple Flask app for Render deployment - No complex backend needed
"""

import os
import sys
import json
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
import subprocess
import threading
import time

# Add core modules
sys.path.append('./core')

# CRITICAL: Import no-mock-data enforcer
from no_mock_data_enforcer import get_validated_portfolio, validate_no_mock_data, enforcer

app = Flask(__name__)

# SYSTEM PROTECTION: NO HARDCODED PORTFOLIO DATA
# All portfolio data MUST come from real Alpaca API through the enforcer

def get_safe_portfolio_data():
    """
    Gets portfolio data safely through the no-mock-data enforcer
    """
    return get_validated_portfolio()

@app.route('/')
def home():
    """Main dashboard"""
    # Get validated portfolio data through enforcer
    portfolio_response = get_safe_portfolio_data()
    
    if portfolio_response['status'] == 'connecting':
        # Show connection status instead of mock data
        return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>🚀 AI Trading System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #1a1a1a; 
            color: white; 
            text-align: center;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .header { margin-bottom: 30px; }
        .header h1 { color: #00D4AA; font-size: 2.5em; margin: 0; }
        .status { 
            background: #333; 
            padding: 30px; 
            border-radius: 10px; 
            margin: 20px 0;
        }
        .connecting { border-left: 4px solid #FF9800; }
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #333;
            border-left: 4px solid #00D4AA;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .protection-notice {
            background: #2d5a2d;
            border: 2px solid #4CAF50;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AI Trading System</h1>
            <p>{{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}</p>
        </div>
        
        <div class="status connecting">
            <div class="spinner"></div>
            <h2>🔌 Connecting to Real Alpaca API</h2>
            <p>System is establishing secure connection to your live trading account...</p>
            <p><strong>NO MOCK DATA WILL BE SHOWN</strong></p>
        </div>
        
        <div class="protection-notice">
            <h3>✅ System Protection Active</h3>
            <p>• Zero tolerance for mock/fake data</p>
            <p>• Real Alpaca API connection only</p>
            <p>• No hardcoded portfolio positions</p>
            <p>• Authentic trading data enforced</p>
        </div>
        
        <div style="margin-top: 30px; color: #666;">
            <p>🔄 Refreshing connection every 10 seconds</p>
            <p>📱 Mobile optimized • 🌐 Access from anywhere</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 10 seconds to check for real data
        setInterval(() => {
            location.reload();
        }, 10000);
    </script>
</body>
</html>
        """, datetime=datetime)
    
    # If we have real data, show it
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>🚀 AI Trading System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #1a1a1a; 
            color: white; 
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #00D4AA; font-size: 2.5em; margin: 0; }
        .header p { color: #888; font-size: 1.2em; }
        .portfolio-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-top: 30px; 
        }
        .portfolio-card { 
            background: #2a2a2a; 
            border: 2px solid #00D4AA; 
            border-radius: 10px; 
            padding: 20px; 
            transition: transform 0.3s; 
        }
        .portfolio-card:hover { transform: translateY(-5px); }
        .symbol { font-size: 1.5em; font-weight: bold; color: #00D4AA; }
        .price { font-size: 1.3em; margin: 10px 0; }
        .gain { color: #4CAF50; }
        .loss { color: #f44336; }
        .metrics { margin-top: 15px; }
        .metric { 
            display: flex; 
            justify-content: space-between; 
            margin: 5px 0; 
            padding: 5px 0; 
            border-bottom: 1px solid #444; 
        }
        .status { 
            background: #333; 
            padding: 15px; 
            border-radius: 10px; 
            margin-bottom: 20px; 
            text-align: center; 
        }
        .status.success { border-left: 4px solid #4CAF50; }
        .nav-buttons {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .nav-button {
            background: #00D4AA;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.3s;
        }
        .nav-button:hover {
            background: #00B894;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px;
        }
        .refresh-btn:hover {
            background: #5a67d8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AI Trading System</h1>
            <p>{{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}</p>
            <p>💰 Real-Time Portfolio & AI Analysis</p>
        </div>
        
        <div class="status success">
            <strong>✅ System Online</strong> - Portfolio data loading successfully
        </div>
        
        <div class="nav-buttons">
            <button class="nav-button" onclick="refreshPortfolio()">🔄 Refresh Portfolio</button>
            <button class="nav-button" onclick="showDiscovery()">📊 Stock Discovery</button>
            <button class="nav-button" onclick="showAnalysis()">🤖 AI Analysis</button>
            <button class="nav-button" onclick="showMemory()">🧠 Portfolio Memory</button>
        </div>
        
        <div class="portfolio-grid" id="portfolio-grid">
            {% for stock in portfolio %}
            <div class="portfolio-card">
                <div class="symbol">{{ stock.symbol }}</div>
                <div class="price">${{ "%.2f"|format(stock.current_price) }}</div>
                <div class="metrics">
                    <div class="metric">
                        <span>Quantity:</span>
                        <span>{{ stock.qty }}</span>
                    </div>
                    <div class="metric">
                        <span>Market Value:</span>
                        <span>${{ "{:,.2f}"|format(stock.market_value) }}</span>
                    </div>
                    <div class="metric">
                        <span>Day Change:</span>
                        <span class="{{ 'gain' if stock.day_change > 0 else 'loss' }}">
                            {{ "{:+.2f}"|format(stock.day_change) }} ({{ "{:+.2f}%"|format(stock.day_change_percent) }})
                        </span>
                    </div>
                    <div class="metric">
                        <span>Total P&L:</span>
                        <span class="{{ 'gain' if stock.unrealized_pl > 0 else 'loss' }}">
                            ${{ "{:+,.2f}"|format(stock.unrealized_pl) }} ({{ "{:+.2f}%"|format(stock.unrealized_plpc) }})
                        </span>
                    </div>
                    <div class="metric">
                        <span>Cost Basis:</span>
                        <span>${{ "%.2f"|format(stock.cost_basis) }}</span>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>🔄 Auto-refresh every 30 seconds</p>
            <p>📱 Mobile optimized • 🌐 Access from anywhere</p>
        </div>
    </div>
    
    <script>
        function refreshPortfolio() {
            location.reload();
        }
        
        function showDiscovery() {
            alert('🔍 Stock Discovery feature coming soon!');
        }
        
        function showAnalysis() {
            alert('🤖 AI Analysis feature coming soon!');
        }
        
        function showMemory() {
            alert('🧠 Portfolio Memory feature coming soon!');
        }
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            refreshPortfolio();
        }, 30000);
    </script>
</body>
</html>
    """, portfolio=portfolio_response['data'], datetime=datetime)

@app.route('/api/portfolio')
def api_portfolio():
    """API endpoint for portfolio data - NO MOCK DATA ALLOWED"""
    portfolio_response = get_safe_portfolio_data()
    
    if portfolio_response['status'] == 'connecting':
        return jsonify({
            "status": "connecting",
            "data": [],
            "message": "Connecting to real Alpaca API - no mock data available",
            "timestamp": datetime.now().isoformat()
        })
    
    portfolio_data = portfolio_response['data']
    return jsonify({
        "status": "success",
        "data": portfolio_data,
        "source": portfolio_response['source'],
        "timestamp": datetime.now().isoformat(),
        "total_value": sum(stock["market_value"] for stock in portfolio_data) if portfolio_data else 0,
        "total_pl": sum(stock["unrealized_pl"] for stock in portfolio_data) if portfolio_data else 0
    })

@app.route('/api/status')
def api_status():
    """System status endpoint"""
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "message": "AI Trading System is running"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting AI Trading System on port {port}")
    print("✅ System ready!")
    print(f"🌐 Available at: http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)