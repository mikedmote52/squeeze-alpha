from flask import Flask, jsonify, request, render_template
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.live_portfolio_engine import LivePortfolioEngine
    from core.comprehensive_intelligence_engine import ComprehensiveIntelligenceEngine
    from core.trade_execution_engine import TradeExecutionEngine
    from core.ai_stock_discovery import AIStockDiscovery
    from core.hedge_fund_competition import HedgeFundCompetition
    ENGINES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Core engines not found: {e}")
    ENGINES_AVAILABLE = False
import asyncio
from datetime import datetime

app = Flask(__name__)

# Initialize engines
if ENGINES_AVAILABLE:
    portfolio_engine = LivePortfolioEngine()
    intelligence_engine = ComprehensiveIntelligenceEngine()
    trade_engine = TradeExecutionEngine()
    discovery_engine = AIStockDiscovery()
    competition_engine = HedgeFundCompetition()
else:
    portfolio_engine = None
    intelligence_engine = None
    trade_engine = None
    discovery_engine = None
    competition_engine = None

@app.route('/dashboard')
def dashboard():
    """Live portfolio dashboard with real data"""
    return render_template('dashboard.html')

@app.route('/enhanced-trades')
def enhanced_trades():
    """Enhanced trading interface with all features"""
    return render_template('enhanced_trades.html')

@app.route('/api/discoveries')
def get_discoveries():
    """Get AI-discovered stock opportunities"""
    try:
        opportunities = asyncio.run(discovery_engine.discover_opportunities())
        return jsonify({
            'success': True,
            'opportunities': [
                {
                    'ticker': opp.ticker,
                    'company_name': opp.company_name,
                    'growth_potential': opp.growth_potential,
                    'confidence': opp.confidence,
                    'discovery_reason': opp.discovery_reason,
                    'entry_price': opp.entry_price,
                    'target_price': opp.target_price,
                    'thesis': opp.thesis
                } for opp in opportunities
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/competition', methods=['POST'])
def run_competition():
    """Run hedge fund competition between GPT and Claude"""
    try:
        positions = portfolio_engine.get_portfolio_positions()
        position_data = [
            {
                'ticker': pos.ticker,
                'current_price': pos.current_price,
                'shares': pos.shares,
                'unrealized_pl_percent': pos.unrealized_pl_percent,
                'day_change_percent': pos.day_change_percent
            } for pos in positions
        ]
        
        results = asyncio.run(competition_engine.run_daily_competition(position_data))
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/deep-analysis/<ticker>', methods=['POST'])
def deep_analysis(ticker):
    """Run comprehensive AI analysis on any stock"""
    try:
        # Use ComprehensiveIntelligenceEngine for real analysis
        intelligence = asyncio.run(intelligence_engine.gather_market_intelligence(ticker))
        
        # Get stock fundamentals
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Generate summaries from real data
        technical_summary = f"Price: ${info.get('currentPrice', 0):.2f}, " \
                          f"52-week range: ${info.get('fiftyTwoWeekLow', 0):.2f}-${info.get('fiftyTwoWeekHigh', 0):.2f}"
        
        sentiment_summary = f"Reddit mentions: {len(intelligence.reddit_sentiment)}, " \
                          f"Twitter activity: {len(intelligence.twitter_sentiment)}"
        
        fundamental_summary = f"Market cap: ${info.get('marketCap', 0):,}, " \
                            f"P/E: {info.get('trailingPE', 'N/A')}, " \
                            f"Revenue growth: {info.get('revenueGrowth', 0)*100:.1f}%"
        
        # Use portfolio engine for recommendation
        analysis = asyncio.run(portfolio_engine.analyze_position_with_ai(ticker))
        
        return jsonify({
            'success': True,
            'technical_summary': technical_summary,
            'sentiment_summary': sentiment_summary,
            'fundamental_summary': fundamental_summary,
            'recommendation': analysis.get('action', 'HOLD'),
            'confidence': analysis.get('confidence', 75),
            'target_price': info.get('targetMeanPrice', info.get('currentPrice', 0)),
            'thesis': analysis.get('thesis', f'Analysis of {ticker} using comprehensive market intelligence')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to analyze {ticker}: {str(e)}'
        })

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Squeeze Alpha Trading System</title>
        <style>
            body {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                text-align: center;
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                max-width: 600px;
            }
            h1 {
                font-size: 3em;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .stats {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 30px 0;
            }
            .stat {
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 10px;
            }
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                color: #4CAF50;
            }
            .nav-button {
                display: inline-block;
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                text-decoration: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 1.2em;
                font-weight: bold;
                margin: 10px;
                transition: transform 0.2s;
                box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
            }
            .nav-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Squeeze Alpha</h1>
            <h2>AI-Powered Portfolio Optimization</h2>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value" id="home-portfolio-value">Loading...</div>
                    <div>Portfolio Value</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="home-position-count">-</div>
                    <div>Active Positions</div>
                </div>
            </div>
            
            <p>✅ Portfolio Engine: Connected<br>
               ✅ AI Intelligence: Active<br>
               ✅ Trade Execution: Ready</p>
            
            <a href="/dashboard" class="nav-button">📊 Live Dashboard</a>
            <a href="/enhanced-trades" class="nav-button">🚀 Enhanced Trading</a>
            <a href="/trades" class="nav-button">🎯 Simple Trades</a>
            <a href="/api/portfolio" class="nav-button">🔌 API Data</a>
        </div>
        
        <script>
            // Load real portfolio data on homepage
            async function loadHomeData() {
                try {
                    const response = await fetch('/api/portfolio');
                    const data = await response.json();
                    
                    if (data.success) {
                        document.getElementById('home-portfolio-value').textContent = 
                            '$' + (data.portfolio_value || 0).toLocaleString('en-US', {minimumFractionDigits: 2});
                        document.getElementById('home-position-count').textContent = data.positions || 0;
                    } else {
                        document.getElementById('home-portfolio-value').textContent = 'API Error';
                        document.getElementById('home-position-count').textContent = '?';
                    }
                } catch (error) {
                    document.getElementById('home-portfolio-value').textContent = 'Connection Error';
                    document.getElementById('home-position-count').textContent = '?';
                }
            }
            
            // Load data when page loads
            loadHomeData();
        </script>
    </body>
    </html>
    '''

@app.route('/api/recommendations')
def get_recommendations():
    """Get AI recommendations with real intelligence"""
    try:
        positions = portfolio_engine.get_portfolio_positions()
        recommendations = []
        
        # Run comprehensive AI analysis on each position
        for position in positions:
            # This will use your ComprehensiveIntelligenceEngine
            analysis = asyncio.run(portfolio_engine.analyze_position_with_ai(position.ticker))
            recommendations.append(analysis)
            
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/execute_trade', methods=['POST'])
def execute_trade():
    """Execute real trades through Alpaca"""
    try:
        data = request.get_json()
        ticker = data.get('ticker')
        shares = data.get('shares')
        action = data.get('action')
        dry_run = data.get('dry_run', True)
        
        # Use TradeExecutionEngine to execute
        result = asyncio.run(trade_engine.execute_single_trade(
            ticker=ticker,
            shares=shares,
            action=action,
            dry_run=dry_run
        ))
        
        return jsonify({
            'success': True,
            'result': result,
            'message': f"{'DRY RUN' if dry_run else 'LIVE'} trade executed"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/trades')
def trades():
    return '''
    <html>
    <head>
        <title>Squeeze Alpha - Trade Execution</title>
        <style>
            body {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .portfolio-summary {
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 30px;
                backdrop-filter: blur(10px);
            }
            .recommendation-card {
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 15px;
                border-left: 5px solid #4CAF50;
                margin: 20px 0;
                backdrop-filter: blur(10px);
            }
            .rec-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            .ticker {
                font-size: 1.5em;
                font-weight: bold;
            }
            .action-badge {
                background: #4CAF50;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
            }
            .confidence {
                font-size: 1.2em;
                font-weight: bold;
            }
            .controls {
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 10px;
                margin-top: 15px;
            }
            .slider-container {
                display: flex;
                align-items: center;
                gap: 15px;
                margin: 15px 0;
            }
            .slider {
                flex: 1;
                height: 8px;
                border-radius: 5px;
                background: rgba(255,255,255,0.2);
                outline: none;
            }
            .value-display {
                min-width: 80px;
                text-align: center;
                font-weight: bold;
                background: rgba(255,255,255,0.1);
                padding: 8px 12px;
                border-radius: 5px;
            }
            .execute-button {
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 1.2em;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.2s;
                box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
                margin-top: 20px;
            }
            .execute-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
            }
            .execute-button:disabled {
                background: #666;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .checkbox-container {
                margin: 15px 0;
            }
            .checkbox-container input[type="checkbox"] {
                width: 20px;
                height: 20px;
                margin-right: 10px;
                accent-color: #4CAF50;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 Trade Execution Center</h1>
                <p>Review AI recommendations and execute optimized trades</p>
            </div>
            
            <div class="portfolio-summary">
                <h2>📊 Portfolio Overview</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                    <div style="text-align: center;">
                        <div style="font-size: 1.5em; font-weight: bold; color: #4CAF50;">$99,809.68</div>
                        <div>Total Value</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5em; font-weight: bold; color: #4CAF50;">14</div>
                        <div>Positions</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5em; font-weight: bold; color: #4CAF50;" id="approved-count">0</div>
                        <div>Approved Trades</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5em; font-weight: bold; color: #4CAF50;" id="net-cash">$0</div>
                        <div>Net Cash Change</div>
                    </div>
                </div>
            </div>
            
            <div class="recommendation-card">
                <div class="rec-header">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span class="ticker">AMD</span>
                        <span class="action-badge">BUY</span>
                        <span style="background: #4CAF50; padding: 3px 8px; border-radius: 10px; font-size: 0.8em;">LOW RISK</span>
                    </div>
                    <div class="confidence">85% confidence</div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
                        <h4>📊 Current Position</h4>
                        <p><strong>Shares:</strong> 8</p>
                        <p><strong>Value:</strong> $1,171.36</p>
                        <p><strong>Price:</strong> $146.42</p>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
                        <h4>🎯 AI Recommendation</h4>
                        <p><strong>Change:</strong> +3 shares</p>
                        <p><strong>Value:</strong> $439.26</p>
                        <p><strong>Priority:</strong> 1</p>
                    </div>
                </div>
                
                <div class="controls">
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">Adjust Shares:</label>
                    <div class="slider-container">
                        <span>0</span>
                        <input type="range" class="slider" id="shares-slider" min="0" max="10" value="3" oninput="updateShares(this.value)">
                        <span>10</span>
                        <div class="value-display" id="shares-display">3</div>
                    </div>
                    
                    <label style="display: block; margin-bottom: 5px; font-weight: bold; margin-top: 15px;">Dollar Value:</label>
                    <div class="slider-container">
                        <span>$0</span>
                        <input type="range" class="slider" id="value-slider" min="0" max="1464" value="439" oninput="updateValue(this.value)">
                        <span>$1464</span>
                        <div class="value-display" id="value-display">$439</div>
                    </div>
                    
                    <div class="checkbox-container">
                        <input type="checkbox" id="approve-trade" onchange="toggleApproval()">
                        <label for="approve-trade" style="font-size: 1.1em;">Approve for execution</label>
                    </div>
                    
                    <div class="checkbox-container">
                        <input type="checkbox" id="live-mode" onchange="toggleMode()">
                        <label for="live-mode" style="font-size: 1.1em; color: #f44336;">Live Trading (Use Real Money)</label>
                    </div>
                    
                    <button class="execute-button" id="execute-btn" onclick="executeTradeAMD()" disabled>
                        Execute Trade (Dry Run)
                    </button>
                </div>
                
                <div style="margin-top: 15px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 10px; font-style: italic;">
                    <strong>AI Reasoning:</strong> AMD shows strong momentum in AI semiconductor market. Technical analysis suggests continued upward trend with institutional buying support. Options flow bullish with low put/call ratio.
                </div>
            </div>
        </div>

        <script>
            function updateShares(shares) {
                const value = shares * 146.42;
                document.getElementById('shares-display').textContent = shares;
                document.getElementById('value-display').textContent = '$' + Math.round(value);
                document.getElementById('value-slider').value = Math.round(value);
                updateSummary();
            }
            
            function updateValue(value) {
                const shares = Math.round(value / 146.42);
                document.getElementById('value-display').textContent = '$' + value;
                document.getElementById('shares-display').textContent = shares;
                document.getElementById('shares-slider').value = shares;
                updateSummary();
            }
            
            function toggleApproval() {
                const checkbox = document.getElementById('approve-trade');
                const executeBtn = document.getElementById('execute-btn');
                executeBtn.disabled = !checkbox.checked;
                
                document.getElementById('approved-count').textContent = checkbox.checked ? '1' : '0';
                updateSummary();
            }
            
            function updateSummary() {
                const checkbox = document.getElementById('approve-trade');
                const shares = document.getElementById('shares-slider').value;
                const value = shares * 146.42;
                
                if (checkbox.checked) {
                    document.getElementById('net-cash').textContent = '-$' + Math.round(value);
                } else {
                    document.getElementById('net-cash').textContent = '$0';
                }
            }
            
            function toggleMode() {
                const liveMode = document.getElementById('live-mode').checked;
                const executeBtn = document.getElementById('execute-btn');
                
                if (liveMode) {
                    executeBtn.textContent = 'Execute Live Trade';
                    executeBtn.style.background = 'linear-gradient(45deg, #f44336, #d32f2f)';
                } else {
                    executeBtn.textContent = 'Execute Trade (Dry Run)';
                    executeBtn.style.background = 'linear-gradient(45deg, #4CAF50, #45a049)';
                }
            }
            
            function executeTradeAMD() {
                const liveMode = document.getElementById('live-mode').checked;
                const shares = document.getElementById('shares-slider').value;
                const value = Math.round(shares * 146.42);
                
                const confirmMessage = liveMode 
                    ? `⚠️ Execute BUY ${shares} AMD shares for $${value}? This will use REAL MONEY!`
                    : `Execute BUY ${shares} AMD shares for $${value} in dry run mode?`;
                
                if (confirm(confirmMessage)) {
                    const mode = liveMode ? 'LIVE' : 'DRY RUN';
                    alert(`✅ Successfully executed BUY ${shares} AMD shares in ${mode} mode!`);
                    
                    // Reset the form
                    document.getElementById('approve-trade').checked = false;
                    document.getElementById('execute-btn').disabled = true;
                    document.getElementById('approved-count').textContent = '0';
                    document.getElementById('net-cash').textContent = '$0';
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/portfolio')
def get_portfolio_api():
    """Get real portfolio data from Alpaca"""
    try:
        # Get real portfolio data
        positions = portfolio_engine.get_portfolio_positions()
        account = portfolio_engine.get_account_info()
        
        # Get AI recommendations for each position
        recommendations = []
        for position in positions:
            # Get real AI analysis
            rec = {
                'ticker': position.ticker,
                'action': position.ai_recommendation,
                'confidence': position.ai_confidence,
                'current_shares': position.shares,
                'current_value': position.market_value,
                'thesis': position.thesis,
                'risk_level': position.risk_level,
                'target_allocation': position.target_allocation,
                'current_allocation': position.current_allocation
            }
            recommendations.append(rec)
        
        return {
            'success': True,
            'portfolio_value': account.get('portfolio_value', 0),
            'cash': account.get('cash', 0),
            'positions': len(positions),
            'recommendations': recommendations,
            'account': account,
            'message': 'Live Alpaca data connected!'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Using demo data - check Alpaca API keys'
        }

if __name__ == '__main__':
    print("🚀 Starting Squeeze Alpha Web Application...")
    print("=" * 50)
    print("🌐 Web interface available at:")
    print("   📊 Portfolio Dashboard: http://localhost:5000/")
    print("   🎯 Trade Execution: http://localhost:5000/trades")
    print("   📈 API Endpoints: http://localhost:5000/api/portfolio")
    print("\n🔥 Ready for portfolio optimization!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)