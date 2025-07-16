#!/usr/bin/env python3
"""
Simple web interface for the Growth Maximizer
"""

import asyncio
import json
from flask import Flask, render_template_string, jsonify
import sys

# Add paths
sys.path.append('./growth_system')
sys.path.append('./core')

from integrated_growth_system import IntegratedGrowthSystem

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🚀 Growth Maximizer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: white; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .metric { background: #333; padding: 20px; margin: 10px; border-radius: 8px; display: inline-block; }
        .button { background: #00D4AA; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .button:hover { background: #00B894; }
        .results { margin-top: 30px; }
        .opportunity { background: #2d3436; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .buy { border-left: 4px solid #00b894; }
        .sell { border-left: 4px solid #e17055; }
        .hold { border-left: 4px solid #fdcb6e; }
        .loading { text-align: center; font-size: 18px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Growth Maximizer System</h1>
            <p>Maximize investment growth over short time periods</p>
            <button class="button" onclick="runGrowthScan()">🔄 Run Growth Scan</button>
        </div>
        
        <div id="results" class="results"></div>
    </div>

    <script>
        async function runGrowthScan() {
            document.getElementById('results').innerHTML = '<div class="loading">🔄 Scanning for growth opportunities...</div>';
            
            try {
                const response = await fetch('/api/growth-scan');
                const data = await response.json();
                
                if (data.status === 'success') {
                    displayResults(data);
                } else {
                    document.getElementById('results').innerHTML = `<div style="color: red;">Error: ${data.error}</div>`;
                }
            } catch (error) {
                document.getElementById('results').innerHTML = `<div style="color: red;">Error: ${error.message}</div>`;
            }
        }
        
        function displayResults(data) {
            const result = data.cycle_result;
            const portfolioValue = data.portfolio_value;
            
            let html = `
                <div class="metric">
                    <h3>Portfolio Value</h3>
                    <div style="font-size: 24px; color: #00D4AA;">$${portfolioValue.toLocaleString()}</div>
                </div>
                
                <div class="metric">
                    <h3>Opportunities Found</h3>
                    <div style="font-size: 24px;">${result.opportunities_found}</div>
                </div>
                
                <div class="metric">
                    <h3>Trading Signals</h3>
                    <div style="font-size: 24px;">${result.trading_signals.length}</div>
                </div>
                
                <div class="metric">
                    <h3>Expected Growth</h3>
                    <div style="font-size: 24px; color: #00D4AA;">${(result.expected_growth * 100).toFixed(2)}%</div>
                </div>
                
                <div class="metric">
                    <h3>Risk Level</h3>
                    <div style="font-size: 24px;">${result.risk_assessment.toUpperCase()}</div>
                </div>
            `;
            
            if (result.trading_signals.length > 0) {
                html += '<h2>🎯 Trading Signals</h2>';
                result.trading_signals.forEach(signal => {
                    const actionClass = signal.action === 'BUY' ? 'buy' : signal.action === 'SELL' ? 'sell' : 'hold';
                    html += `
                        <div class="opportunity ${actionClass}">
                            <h3>${signal.symbol} - ${signal.action}</h3>
                            <p>Quantity: ${signal.quantity} shares</p>
                            <p>Signal Strength: ${signal.signal_strength}</p>
                            <p>Expected Return: ${(signal.expected_return * 100).toFixed(2)}%</p>
                        </div>
                    `;
                });
            }
            
            if (result.top_opportunities.length > 0) {
                html += '<h2>🏆 Top Opportunities</h2>';
                result.top_opportunities.forEach(opp => {
                    html += `
                        <div class="opportunity">
                            <h3>${opp.symbol}</h3>
                            <p>Growth Score: ${opp.growth_score.toFixed(1)}/100</p>
                            <p>Confidence: ${(opp.confidence * 100).toFixed(1)}%</p>
                            <p>Entry Price: $${opp.entry_price.toFixed(2)}</p>
                            <p>Target Price: $${opp.target_price.toFixed(2)}</p>
                            <p>Risk Level: ${opp.risk_level.toUpperCase()}</p>
                        </div>
                    `;
                });
            }
            
            document.getElementById('results').innerHTML = html;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/growth-scan')
def growth_scan():
    async def run_scan():
        system = IntegratedGrowthSystem()
        system.initialize_system()
        result = await system.execute_growth_cycle()
        return result
    
    try:
        result = asyncio.run(run_scan())
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

if __name__ == '__main__':
    print("🚀 Starting Growth Maximizer Web Interface...")
    print("📊 Connect to: http://localhost:5000")
    print("🛡️  ZERO MOCK DATA - Real portfolio analysis only")
    app.run(debug=True, host='0.0.0.0', port=5000)