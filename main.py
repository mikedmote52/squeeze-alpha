#!/usr/bin/env python3
"""
AI TRADING SYSTEM - Main Entry Point
Clean, organized launcher for Replit with web interface
"""

import os
import sys
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import threading
import asyncio

# Add directories to Python path
sys.path.append('core')
sys.path.append('utils')

# Create Flask app
app = Flask(__name__)

def main():
    print("🚀 AI TRADING SYSTEM v2.0")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💰 Real-Time Stock Discovery & Portfolio Analysis")
    print()
    
    print("🔍 SYSTEM MENU:")
    print("1. 🔑 Check API Keys & Setup")
    print("2. 🛡️ Validate System Safety") 
    print("3. 📊 Discover New Stocks")
    print("4. 💰 Analyze Your Portfolio")
    print("5. 🚀 Start Full Trading System")
    print("6. 🧪 Quick Market Check")
    print("7. 📖 Help & Documentation")
    print()
    
    while True:
        try:
            choice = input("➤ Enter choice (1-7) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("👋 System stopped. Happy trading!")
                break
                
            elif choice == '1':
                check_api_setup()
                
            elif choice == '2':
                validate_system_safety()
                
            elif choice == '3':
                discover_stocks()
                
            elif choice == '4':
                analyze_portfolio()
                
            elif choice == '5':
                start_full_system()
                
            elif choice == '6':
                quick_market_check()
                
            elif choice == '7':
                show_help()
                
            else:
                print("❌ Invalid choice. Please enter 1-7 or 'q'")
                
            print("\n" + "─" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 System stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def check_api_setup():
    """Check API keys and setup"""
    print("\n🔑 CHECKING API SETUP...")
    
    try:
        from secrets_manager import SecretsManager
        
        secrets = SecretsManager()
        secrets.print_status_report()
        
        print("\n💡 To add API keys:")
        print("1. Click 'Secrets' tab in Replit sidebar")
        print("2. Add: ANTHROPIC_API_KEY, OPENAI_API_KEY, ALPACA_API_KEY")
        print("3. Restart Repl after adding keys")
        
    except ImportError:
        print("❌ Secrets manager not found. Upload core/secrets_manager.py")
    except Exception as e:
        print(f"❌ Setup check failed: {e}")

def validate_system_safety():
    """Validate system safety"""
    print("\n🛡️ VALIDATING SYSTEM SAFETY...")
    
    try:
        from trading_safety_validator import TradingSafetyValidator
        
        validator = TradingSafetyValidator()
        is_safe, violations = validator.validate_all_systems()
        
        if is_safe:
            print("✅ SYSTEM READY FOR REAL MONEY TRADING")
        else:
            print(f"🚨 {len(violations)} safety issues found")
            print("💡 Configure API keys to fix issues")
            
    except ImportError:
        print("❌ Safety validator not found. Upload core/trading_safety_validator.py")
    except Exception as e:
        print(f"❌ Safety check failed: {e}")

def discover_stocks():
    """Discover new stock opportunities"""
    print("\n📊 DISCOVERING NEW STOCK OPPORTUNITIES...")
    
    try:
        import asyncio
        from real_time_stock_discovery import RealTimeStockDiscovery
        
        async def run_discovery():
            discovery = RealTimeStockDiscovery()
            candidates = await discovery.discover_live_explosive_opportunities('today')
            
            if candidates:
                print(f"\n✅ FOUND {len(candidates)} REAL OPPORTUNITIES:")
                for i, candidate in enumerate(candidates[:3], 1):
                    print(f"\n{i}. {candidate.ticker} - {candidate.company_name}")
                    print(f"   💰 Price: ${candidate.current_price:.2f}")
                    print(f"   📈 Change: {candidate.price_change_1d:+.1f}% today")
                    print(f"   📊 Volume: {candidate.volume_spike:.1f}x normal")
                    print(f"   🎯 Reason: {candidate.discovery_reason}")
                    print(f"   ⭐ Confidence: {candidate.confidence_score:.0%}")
            else:
                print("📊 No qualifying opportunities in current market")
                print("💡 Market may be in low-volatility period")
        
        asyncio.run(run_discovery())
        
    except ImportError:
        print("❌ Discovery engine not found. Upload core/real_time_stock_discovery.py")
    except Exception as e:
        print(f"❌ Discovery failed: {e}")

def analyze_portfolio():
    """Analyze current portfolio with hedge fund-level intelligence"""
    print("\n🧠 HEDGE FUND-LEVEL PORTFOLIO ANALYSIS")
    print("=" * 60)
    print("🔍 Gathering comprehensive market intelligence...")
    
    try:
        from live_portfolio_engine import LivePortfolioEngine
        import asyncio
        
        # Use enhanced portfolio engine
        engine = LivePortfolioEngine()
        positions = asyncio.run(engine.get_live_portfolio())
        summary = engine.generate_portfolio_summary(positions)
        
        print(f"\n💰 PORTFOLIO SUMMARY:")
        print(f"Total Value: ${summary['total_value']:,.2f}")
        print(f"Total P&L: ${summary['total_pl']:,.2f} ({summary['total_pl_percent']:+.1f}%)")
        print(f"Winners: {summary['winners_count']} | Losers: {summary['losers_count']}")
        print(f"AI Recommendations: {summary['buy_recommendations']} BUY | {summary['sell_recommendations']} SELL | {summary['hold_recommendations']} HOLD")
        
        print(f"\n🎯 HEDGE FUND RECOMMENDATIONS:")
        print("=" * 50)
        
        # Sort by recommendation priority (SELL first, then BUY, then HOLD)
        sorted_positions = sorted(positions, key=lambda x: (
            0 if x.ai_recommendation == 'SELL' else 
            1 if x.ai_recommendation == 'BUY' else 2,
            -x.ai_confidence
        ))
        
        for pos in sorted_positions:
            # Color coding for terminal
            if pos.ai_recommendation == 'BUY':
                action_color = "🟢"
            elif pos.ai_recommendation == 'SELL':
                action_color = "🔴"
            else:
                action_color = "🟡"
            
            # Performance indicator
            perf_indicator = "📈" if pos.unrealized_pl >= 0 else "📉"
            
            print(f"\n{action_color} {pos.ticker} - {pos.company_name}")
            print(f"   💰 Value: ${pos.market_value:,.0f} ({pos.current_allocation:.1f}% of portfolio)")
            print(f"   {perf_indicator} P&L: ${pos.unrealized_pl:+,.0f} ({pos.unrealized_pl_percent:+.1f}%) | Today: {pos.day_change_percent:+.1f}%")
            print(f"   🤖 AI Rec: {pos.ai_recommendation} ({pos.ai_confidence}% confidence)")
            print(f"   ⚖️ Position: {pos.position_size_rec} to {pos.target_allocation:.1f}% allocation")
            print(f"   🏷️ Risk: {pos.risk_level} | Sector: {pos.sector}")
            print(f"   📝 Thesis: {pos.thesis[:100]}...")
            
            # Show intelligence factors if available
            if hasattr(pos, 'intelligence_used') and pos.intelligence_used:
                print(f"   🧠 Intelligence: {pos.data_sources} active data sources")
        
        # Optimization recommendations
        print(f"\n🎯 PORTFOLIO OPTIMIZATION PRIORITIES:")
        print("=" * 40)
        
        sell_positions = [p for p in positions if p.ai_recommendation == 'SELL']
        buy_positions = [p for p in positions if p.ai_recommendation == 'BUY']
        
        if sell_positions:
            print("🔴 IMMEDIATE SELLS:")
            for pos in sell_positions[:3]:
                print(f"   • {pos.ticker}: {pos.ai_confidence}% confidence - Cut to {pos.target_allocation:.1f}%")
        
        if buy_positions:
            print("🟢 ACCUMULATION TARGETS:")
            for pos in buy_positions[:3]:
                print(f"   • {pos.ticker}: {pos.ai_confidence}% confidence - Increase to {pos.target_allocation:.1f}%")
        
        # Risk analysis
        high_risk_positions = [p for p in positions if p.risk_level == 'HIGH']
        if high_risk_positions:
            print("⚠️ HIGH RISK POSITIONS:")
            for pos in high_risk_positions[:3]:
                print(f"   • {pos.ticker}: {pos.current_allocation:.1f}% allocation - Monitor closely")
        
        print(f"\n💡 ACCESS FULL ANALYSIS:")
        print("   🌐 Start web interface (Option 5) for clickable stock tiles")
        print("   📊 Each tile shows complete thesis, news, and recommendations")
        
    except ImportError:
        print("❌ Portfolio engine not found. Upload core/live_portfolio_engine.py")
    except Exception as e:
        print(f"❌ Portfolio analysis failed: {e}")
        print("💡 Falling back to basic analysis - check API keys and restart")

def start_full_system():
    """Start the full autonomous trading system"""
    print("\n🚀 STARTING FULL TRADING SYSTEM...")
    
    try:
        # First run safety check
        from trading_safety_validator import emergency_trading_safety_check
        
        is_safe, violations = emergency_trading_safety_check()
        
        if not is_safe:
            print("🛑 SYSTEM BLOCKED FOR SAFETY")
            print("❌ Cannot start with mock data detected")
            print("💡 Configure API keys first")
            return
        
        print("✅ Safety check passed")
        print("🚀 Starting autonomous system...")
        
        # Run the full system
        os.system("python3 utils/start_autonomous_system.py")
        
    except ImportError:
        print("❌ Full system not available. Upload start_autonomous_system.py")
    except Exception as e:
        print(f"❌ System start failed: {e}")

def quick_market_check():
    """Quick market overview"""
    print("\n🧪 QUICK MARKET CHECK...")
    
    try:
        import yfinance as yf
        
        print("📊 MARKET OVERVIEW:")
        print("=" * 30)
        
        # Market indices and key stocks
        symbols = [
            ('SPY', 'S&P 500'),
            ('QQQ', 'NASDAQ'),
            ('AMC', 'AMC Entertainment'),
            ('GME', 'GameStop'),
            ('TSLA', 'Tesla')
        ]
        
        for symbol, name in symbols:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period='2d')
                
                if len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change = ((current - prev) / prev) * 100
                    volume = hist['Volume'].iloc[-1] / 1e6
                    
                    status = "🟢" if change > 0 else "🔴"
                    print(f"{status} {symbol}: ${current:.2f} ({change:+.1f}%) Vol: {volume:.1f}M")
                    
            except:
                print(f"⚠️ {symbol}: Data unavailable")
        
        print(f"\n⏰ Market data as of {datetime.now().strftime('%H:%M %Z')}")
        
    except ImportError:
        print("❌ yfinance not installed. Run: pip install yfinance")
    except Exception as e:
        print(f"❌ Market check failed: {e}")

def show_help():
    """Show help and documentation"""
    print("\n📖 HELP & DOCUMENTATION")
    print("=" * 40)
    print()
    print("🔑 API SETUP:")
    print("   • Get Claude API: https://console.anthropic.com/")
    print("   • Get OpenAI API: https://platform.openai.com/api-keys") 
    print("   • Get Alpaca API: https://app.alpaca.markets/")
    print("   • Add keys to Replit Secrets tab")
    print()
    print("🚀 SYSTEM FEATURES:")
    print("   • Real-time stock discovery using live market data")
    print("   • AI-powered analysis with Claude vs ChatGPT debates")
    print("   • Portfolio optimization and risk management")
    print("   • Safety systems prevent trading with mock data")
    print()
    print("🧪 TESTING:")
    print("   • Option 1: Check if API keys are configured")
    print("   • Option 2: Validate system safety (shows issues)")
    print("   • Option 3: Test discovery with real market data")
    print("   • Option 4: Analyze your current holdings")
    print()
    print("💡 TROUBLESHOOTING:")
    print("   • If Run button doesn't work: Use Shell tab")
    print("   • If imports fail: Run 'pip install yfinance aiohttp'")
    print("   • If API errors: Check Secrets tab configuration")
    print("   • If no opportunities: Normal during low volatility")

# Web Interface HTML Template
WEB_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 AI Trading System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .header { 
            text-align: center; 
            margin-bottom: 40px;
        }
        .header h1 { 
            font-size: 2.5em; 
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .header p { 
            font-size: 1.2em; 
            opacity: 0.9;
        }
        .menu-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px;
        }
        .menu-item { 
            background: rgba(255,255,255,0.15);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }
        .menu-item:hover { 
            background: rgba(255,255,255,0.25);
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }
        .menu-item h3 { 
            font-size: 1.3em; 
            margin-bottom: 15px;
        }
        .menu-item p { 
            opacity: 0.8;
            line-height: 1.5;
        }
        .results { 
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
            min-height: 150px;
            font-family: 'Courier New', monospace;
        }
        .results h3 { 
            margin-bottom: 15px;
            color: #4CAF50;
        }
        .loading { 
            text-align: center;
            padding: 40px;
        }
        .spinner { 
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255,255,255,0.3);
            border-left: 4px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin { 
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .status-bar {
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-good { background: #4CAF50; }
        .status-warning { background: #FF9800; }
        .status-error { background: #F44336; }
        
        /* Portfolio Tiles */
        .portfolio-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .portfolio-tile {
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
            position: relative;
        }
        .portfolio-tile:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        }
        .portfolio-tile.positive {
            border-color: #4CAF50;
        }
        .portfolio-tile.negative {
            border-color: #F44336;
        }
        .tile-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .ticker-symbol {
            font-size: 1.2em;
            font-weight: bold;
        }
        .recommendation {
            font-size: 0.8em;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: bold;
        }
        .rec-buy { background: #4CAF50; color: white; }
        .rec-sell { background: #F44336; color: white; }
        .rec-hold { background: #FF9800; color: white; }
        .tile-metrics {
            font-size: 0.9em;
            line-height: 1.4;
        }
        .loading-tile {
            text-align: center;
            padding: 40px;
            grid-column: 1 / -1;
        }
        
        /* Stock Tiles */
        .stock-tile {
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
            position: relative;
            min-height: 180px;
        }
        .stock-tile:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        }
        .stock-tile.gain {
            border-color: #4CAF50;
        }
        .stock-tile.loss {
            border-color: #F44336;
        }
        .stock-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .stock-header h3 {
            margin: 0;
            font-size: 1.2em;
            font-weight: bold;
        }
        .stock-price {
            font-size: 1.1em;
            font-weight: bold;
        }
        .stock-info {
            margin: 10px 0;
            font-size: 0.9em;
            line-height: 1.4;
        }
        .stock-change.gain {
            color: #4CAF50;
        }
        .stock-change.loss {
            color: #F44336;
        }
        .stock-pl.gain {
            color: #4CAF50;
        }
        .stock-pl.loss {
            color: #F44336;
        }
        .ai-recommendation {
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 0.8em;
            padding: 4px 8px;
            border-radius: 12px;
            font-weight: bold;
            color: white;
        }
        .stock-risk {
            position: absolute;
            bottom: 10px;
            right: 10px;
            font-size: 0.7em;
            padding: 2px 6px;
            border-radius: 8px;
            font-weight: bold;
        }
        .risk-low {
            background: #4CAF50;
            color: white;
        }
        .risk-medium {
            background: #FF9800;
            color: white;
        }
        .risk-high {
            background: #F44336;
            color: white;
        }
        
        /* Stock Detail Modal */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
        }
        .modal-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 5% auto;
            padding: 30px;
            border-radius: 20px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            color: white;
        }
        .close {
            color: white;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover {
            color: #ccc;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AI Trading System</h1>
            <p>📅 {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}</p>
            <p>💰 Real-Time Stock Discovery & Portfolio Analysis</p>
        </div>
        
        <div class="status-bar">
            <span class="status-indicator status-warning"></span>
            <strong>System Status:</strong> Ready for commands
        </div>
        
        <!-- Portfolio Tiles Section -->
        <div id="portfolio-section">
            <h2 style="text-align: center; margin-bottom: 20px;">💰 YOUR LIVE PORTFOLIO</h2>
            <div id="portfolio-tiles" class="portfolio-grid">
                <div class="loading-tile">
                    <div class="spinner"></div>
                    <p>Loading portfolio...</p>
                </div>
            </div>
        </div>
        
        <!-- Control Menu -->
        <div class="menu-grid">
            <div class="menu-item" onclick="runCommand('refresh_portfolio')">
                <h3>🔄 Refresh Portfolio</h3>
                <p>Update live portfolio data and AI recommendations</p>
            </div>
            
            <div class="menu-item" onclick="runCommand('discover_stocks')">
                <h3>📊 Alpha Discovery</h3>
                <p>Momentum, volume spikes, institutional-grade filtering</p>
            </div>
            
            <div class="menu-item" onclick="runCommand('discover_catalysts')">
                <h3>🎯 Catalyst Discovery</h3>
                <p>FDA approvals, earnings, M&A, regulatory events</p>
            </div>
            
            <div class="menu-item" onclick="runCommand('system_performance')">
                <h3>🏆 System Performance</h3>
                <p>Track which discovery system is winning</p>
            </div>
            
            <div class="menu-item" onclick="runCommand('ai_debate')">
                <h3>🤖 AI Stock Debate</h3>
                <p>Claude vs ChatGPT vs Grok multi-AI analysis</p>
            </div>
            
            <div class="menu-item" onclick="runCommand('api_check')">
                <h3>🔑 System Status</h3>
                <p>Check API keys and system safety</p>
            </div>
            
            <div class="menu-item" onclick="runCommand('market_analysis')">
                <h3>📈 Market Analysis</h3>
                <p>Real-time Polygon.io data with news and options flow</p>
            </div>
            
            <div class="menu-item" onclick="runCommand('slack_test')">
                <h3>💬 Test Slack</h3>
                <p>Send test portfolio update to Slack</p>
            </div>
        </div>
        
        <div class="results" id="results">
            <h3>📋 Results</h3>
            <p>Click any option above to start analyzing...</p>
        </div>
    </div>
    
    <!-- Stock Detail Modal -->
    <div id="stockModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div id="stock-details">
                <!-- Stock details will be loaded here -->
            </div>
        </div>
    </div>

    <script>
        async function runCommand(command) {
            const resultsDiv = document.getElementById('results');
            
            // Show loading
            resultsDiv.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Running ${command}...</p>
                </div>
            `;
            
            try {
                const response = await fetch('/api/' + command, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                
                // Display results
                resultsDiv.innerHTML = `
                    <h3>${data.title}</h3>
                    <pre style="white-space: pre-wrap; line-height: 1.6;">${data.content}</pre>
                `;
                
                // If refreshing portfolio, update the tiles too
                if (command === 'refresh_portfolio') {
                    loadPortfolioTiles();
                }
                
            } catch (error) {
                resultsDiv.innerHTML = `
                    <h3>❌ Error</h3>
                    <p>Failed to execute command: ${error.message}</p>
                `;
            }
        }
        
        async function loadPortfolioTiles() {
            const portfolioDiv = document.getElementById('portfolio-tiles');
            
            try {
                const response = await fetch('/api/portfolio_tiles', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                portfolioDiv.innerHTML = data.html;
                
            } catch (error) {
                portfolioDiv.innerHTML = `
                    <div class="loading-tile">
                        <p>❌ Failed to load portfolio</p>
                    </div>
                `;
            }
        }
        
        async function showStockDetails(ticker) {
            const modal = document.getElementById('stockModal');
            const detailsDiv = document.getElementById('stock-details');
            
            detailsDiv.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Loading ${ticker} analysis...</p>
                </div>
            `;
            
            modal.style.display = 'block';
            
            try {
                const response = await fetch('/api/stock_details/' + ticker, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                detailsDiv.innerHTML = data.html;
                
            } catch (error) {
                detailsDiv.innerHTML = `
                    <h3>❌ Error</h3>
                    <p>Failed to load ${ticker} details: ${error.message}</p>
                `;
            }
        }
        
        // Modal controls
        document.addEventListener('DOMContentLoaded', function() {
            const modal = document.getElementById('stockModal');
            const closeBtn = document.querySelector('.close');
            
            closeBtn.onclick = function() {
                modal.style.display = 'none';
            }
            
            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = 'none';
                }
            }
            
            // Load portfolio on page load
            loadPortfolioTiles();
        });
        
        // Auto-refresh portfolio every 60 seconds
        setInterval(async () => {
            try {
                loadPortfolioTiles();
            } catch (error) {
                console.log('Portfolio refresh failed:', error);
            }
        }, 60000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(WEB_TEMPLATE, datetime=datetime)

@app.route('/api/<command>', methods=['POST'])
def api_command(command):
    try:
        if command == 'api_check':
            result = run_api_check()
            return jsonify({
                'title': '🔑 API Keys Status',
                'content': result
            })
        
        elif command == 'safety_check':
            result = run_safety_check()
            return jsonify({
                'title': '🛡️ System Safety Check',
                'content': result
            })
        
        elif command == 'discover_stocks':
            result = run_stock_discovery()
            return jsonify({
                'title': '📊 Alpha Discovery Results',
                'content': result
            })
        
        elif command == 'discover_catalysts':
            result = run_catalyst_discovery()
            return jsonify({
                'title': '🎯 Catalyst Discovery Results',
                'content': result
            })
        
        elif command == 'system_performance':
            result = run_system_performance()
            return jsonify({
                'title': '🏆 System Performance Comparison',
                'content': result
            })
        
        elif command == 'analyze_portfolio':
            result = run_portfolio_analysis()
            return jsonify({
                'title': '💰 Portfolio Analysis',
                'content': result
            })
        
        elif command == 'market_check':
            result = run_market_check()
            return jsonify({
                'title': '🧪 Market Overview',
                'content': result
            })
        
        elif command == 'ai_debate':
            result = run_ai_stock_debate()
            return jsonify({
                'title': '🤖 AI Stock Debate Results',
                'content': result
            })
        
        elif command == 'refresh_portfolio':
            result = run_portfolio_refresh()
            return jsonify({
                'title': '🔄 Portfolio Refreshed',
                'content': result
            })
        
        elif command == 'market_analysis':
            result = run_market_analysis()
            return jsonify({
                'title': '📈 Polygon Market Analysis',
                'content': result
            })
        
        elif command == 'slack_test':
            result = run_slack_test()
            return jsonify({
                'title': '💬 Slack Integration Test',
                'content': result
            })
        
        elif command == 'portfolio_tiles':
            result = generate_portfolio_tiles()
            return jsonify({
                'html': result
            })
        
        elif command == 'help':
            result = get_help_info()
            return jsonify({
                'title': '📖 Help & Documentation',
                'content': result
            })
        
        else:
            return jsonify({
                'title': '❌ Error',
                'content': f'Unknown command: {command}'
            })
    
    except Exception as e:
        return jsonify({
            'title': '❌ Error',
            'content': f'Command failed: {str(e)}'
        })

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'ready',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/portfolio_tiles', methods=['POST'])
def api_portfolio_tiles():
    try:
        html = generate_portfolio_tiles_html()
        return jsonify({'html': html})
    except Exception as e:
        return jsonify({'html': f'<div class="loading-tile"><p>❌ Error: {str(e)}</p></div>'})

@app.route('/api/stock_details/<ticker>', methods=['POST'])
def api_stock_details(ticker):
    try:
        html = generate_stock_details_html(ticker)
        return jsonify({'html': html})
    except Exception as e:
        return jsonify({'html': f'<h3>❌ Error</h3><p>Failed to load {ticker}: {str(e)}</p>'})

def run_api_check():
    try:
        from secrets_manager import SecretsManager
        secrets = SecretsManager()
        
        # Get all API keys using the updated method
        keys = secrets.get_all_api_keys()
        
        result = "🔑 API KEYS STATUS:\n"
        result += "=" * 30 + "\n\n"
        
        # Use the new labels
        key_labels = {
            'OPENROUTER_API_KEY': 'OpenRouter (Multi-AI)',
            'ANTHROPIC_API_KEY': 'Anthropic (Claude)',
            'OPENAI_API_KEY': 'OpenAI (ChatGPT)',
            'ALPACA_API_KEY': 'Alpaca (Trading)',
            'ALPACA_SECRET_KEY': 'Alpaca (Secret)',
            'PERPLEXITY_API_KEY': 'Perplexity (Research)',
            'POLYGON_API_KEY': 'Polygon (Real-time Data)',
            'SLACK_WEBHOOK_URL': 'Slack (Notifications)'
        }
        
        for key_name, key_value in keys.items():
            label = key_labels.get(key_name, key_name)
            if key_value:
                preview = key_value[:12] + "..." if len(key_value) > 12 else key_value
                result += f"✅ {label}: {preview}\n"
            else:
                result += f"❌ {label}: MISSING\n"
        
        configured_count = sum(1 for v in keys.values() if v)
        if configured_count >= 6:
            result += "\n✅ API keys are configured! System ready for professional trading.\n"
        elif configured_count >= 4:
            result += "\n✅ Core APIs configured! Add Polygon & Slack for full features.\n"
        else:
            result += "\n💡 TO ADD API KEYS:\n"
            result += "1. Click 'Secrets' tab in Replit sidebar\n"
            result += "2. Add missing API keys\n"
            result += "3. Restart Repl after adding keys\n"
        
        return result
    
    except Exception as e:
        return f"❌ API check failed: {str(e)}"

def run_safety_check():
    try:
        from trading_safety_validator import TradingSafetyValidator
        
        validator = TradingSafetyValidator()
        is_safe, violations = validator.validate_all_systems()
        
        result = "🛡️ SYSTEM SAFETY VALIDATION:\n"
        result += "=" * 35 + "\n\n"
        
        if is_safe:
            result += "✅ SYSTEM READY FOR REAL MONEY TRADING\n"
            result += "✅ No mock data detected\n"
            result += "✅ All safety checks passed\n"
        else:
            result += f"🚨 {len(violations)} SAFETY ISSUES FOUND:\n\n"
            for i, violation in enumerate(violations, 1):
                result += f"{i}. {violation}\n"
            result += "\n💡 Configure API keys to fix most issues\n"
        
        return result
    
    except Exception as e:
        return f"❌ Safety check failed: {str(e)}"

def run_stock_discovery():
    try:
        import asyncio
        from alpha_engine_enhanced import EnhancedAlphaEngine
        
        async def discover():
            engine = EnhancedAlphaEngine()
            candidates = await engine.discover_alpha_opportunities('swing')
            
            result = "🔍 ENHANCED ALPHA DISCOVERY ENGINE\n"
            result += "=" * 45 + "\n"
            result += "📊 Professional-grade institutional quality filtering\n"
            result += "🎯 Focus: Quality opportunities, not meme stocks\n\n"
            
            if candidates:
                result += f"✅ FOUND {len(candidates)} HIGH-QUALITY ALPHA OPPORTUNITIES:\n\n"
                for i, candidate in enumerate(candidates[:5], 1):
                    result += f"{i}. {candidate.ticker} - {candidate.company_name}\n"
                    result += f"   💰 Price: ${candidate.current_price:.2f}\n"
                    result += f"   📈 Change: {candidate.price_change_1d:+.1f}% today\n"
                    result += f"   📊 Volume: {candidate.volume_spike:.1f}x normal\n"
                    result += f"   🏢 Market Cap: ${candidate.market_cap/1e9:.1f}B\n"
                    result += f"   🎯 Quality: {candidate.quality_score:.1f}/1.0\n"
                    result += f"   ⚠️ Risk: {candidate.risk_score:.1f}/1.0\n"
                    result += f"   ⭐ Confidence: {candidate.confidence_score:.0%}\n"
                    result += f"   📝 Discovery: {candidate.discovery_reason}\n\n"
            else:
                result += "📊 No qualifying institutional-grade opportunities found\n"
                result += "💡 Current market conditions may not meet quality filters\n"
                result += "🔄 Enhanced engine filters out dilution stocks like AMC/GME\n"
                result += "⏰ Try again during high-volume market periods\n"
            
            return result
        
        # Run async function
        return asyncio.run(discover())
    
    except Exception as e:
        return f"❌ Enhanced alpha discovery failed: {str(e)}"

def run_catalyst_discovery():
    """Run catalyst discovery engine for binary events"""
    try:
        import asyncio
        from catalyst_discovery_engine import CatalystDiscoveryEngine
        
        async def discover():
            engine = CatalystDiscoveryEngine()
            return await engine.discover_catalyst_opportunities_for_main()
        
        return asyncio.run(discover())
    except Exception as e:
        return f"❌ Catalyst discovery failed: {str(e)}"

def run_system_performance():
    """Run system performance comparison and tracking"""
    try:
        import asyncio
        from discovery_system_tracker import DiscoverySystemTracker
        
        async def analyze():
            tracker = DiscoverySystemTracker()
            return await tracker.generate_system_comparison_report()
        
        return asyncio.run(analyze())
    except Exception as e:
        return f"❌ System performance analysis failed: {str(e)}"

def run_portfolio_analysis():
    try:
        import asyncio
        from live_portfolio_engine import LivePortfolioEngine
        
        async def analyze_portfolio():
            engine = LivePortfolioEngine()
            positions = await engine.get_live_portfolio()
            summary = engine.generate_portfolio_summary(positions)
            
            result = "💰 LIVE PORTFOLIO ANALYSIS:\n"
            result += "=" * 35 + "\n\n"
            
            if not positions:
                result += "📊 No portfolio positions found.\n\n"
                result += "🔧 TROUBLESHOOTING:\n"
                result += "• Check if Alpaca API keys are configured\n"
                result += "• Verify you have positions in your Alpaca account\n"
                result += "• System falls back to demo holdings if Alpaca unavailable\n\n"
                result += "📋 Expected Holdings: AMD, NVAX, WOLF, BTBT, CRWV, VIGL, SMCI, SOUN\n"
                return result
            
            # Portfolio Summary
            result += f"💰 Total Value: ${summary['total_value']:,.2f}\n"
            result += f"📊 Total P&L: ${summary['total_pl']:,.2f} ({summary['total_pl_percent']:+.1f}%)\n"
            result += f"🏆 Winners: {summary['winners_count']} | 📉 Losers: {summary['losers_count']}\n\n"
            
            # Individual positions
            result += "📈 CURRENT POSITIONS:\n"
            for pos in positions:
                status = "🟢" if pos.unrealized_pl >= 0 else "🔴"
                result += f"{status} {pos.ticker}: ${pos.current_price:.2f} "
                result += f"({pos.day_change_percent:+.1f}% today, "
                result += f"{pos.unrealized_pl_percent:+.1f}% total)\n"
                result += f"   💰 Value: ${pos.market_value:,.0f} ({pos.current_allocation:.1f}%)\n"
                result += f"   🤖 AI Rec: {pos.ai_recommendation} ({pos.ai_confidence}%)\n\n"
            
            # Top performers
            if summary['highest_performer']:
                hp = summary['highest_performer']
                result += f"🥇 BEST PERFORMER: {hp.ticker} ({hp.unrealized_pl_percent:+.1f}%)\n"
            
            if summary['lowest_performer']:
                lp = summary['lowest_performer']
                result += f"🔻 WORST PERFORMER: {lp.ticker} ({lp.unrealized_pl_percent:+.1f}%)\n"
            
            # AI Recommendations Summary
            result += f"\n🤖 AI RECOMMENDATIONS:\n"
            result += f"• {summary['buy_recommendations']} BUY signals\n"
            result += f"• {summary['sell_recommendations']} SELL signals\n"
            result += f"• {summary['hold_recommendations']} HOLD signals\n"
            
            return result
        
        return asyncio.run(analyze_portfolio())
    
    except Exception as e:
        return f"❌ Live portfolio analysis failed: {str(e)}\n\n💡 Check Alpaca API configuration or try Enhanced Alpha Discovery instead."

def run_market_check():
    try:
        import yfinance as yf
        
        result = "🧪 MARKET OVERVIEW:\n"
        result += "=" * 25 + "\n\n"
        
        # Market indices and key stocks
        symbols = [
            ('SPY', 'S&P 500'),
            ('QQQ', 'NASDAQ'),
            ('AMC', 'AMC Entertainment'),
            ('GME', 'GameStop'),
            ('TSLA', 'Tesla')
        ]
        
        for symbol, name in symbols:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period='2d')
                
                if len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change = ((current - prev) / prev) * 100
                    volume = hist['Volume'].iloc[-1] / 1e6
                    
                    status = "🟢" if change > 0 else "🔴"
                    result += f"{status} {symbol}: ${current:.2f} ({change:+.1f}%) Vol: {volume:.1f}M\n"
                    
            except:
                result += f"⚠️ {symbol}: Data unavailable\n"
        
        result += f"\n⏰ Market data as of {datetime.now().strftime('%H:%M %Z')}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Market check failed: {str(e)}"

def run_ai_stock_debate():
    try:
        import asyncio
        from openrouter_stock_debate import OpenRouterStockDebate
        
        async def debate():
            debate_engine = OpenRouterStockDebate()
            
            # Use AMC as example (the user was concerned about AMC)
            result = await debate_engine.debate_stock('AMC', 3.33, 11.0, 3.0)
            
            if 'error' in result:
                return f"❌ AI Debate Error: {result['error']}\n\n💡 {result['recommendation']}"
            
            output = "🤖 AI STOCK DEBATE RESULTS\n"
            output += "=" * 40 + "\n"
            output += f"📈 Ticker: {result['ticker']}\n"
            output += f"⏰ Time: {result['timestamp'][:19]}\n\n"
            
            output += "🔵 CLAUDE'S ANALYSIS:\n"
            output += f"{result['analyses']['claude']}\n\n"
            
            output += "🟢 CHATGPT'S ANALYSIS:\n"
            output += f"{result['analyses']['chatgpt']}\n\n"
            
            output += "🟠 GROK'S ANALYSIS:\n"
            output += f"{result['analyses']['grok']}\n\n"
            
            output += "🎯 FINAL CONSENSUS:\n"
            output += f"{result['final_consensus']}\n\n"
            
            # Add conversation thesis
            if 'conversation_thesis' in result:
                output += f"{result['conversation_thesis']}\n\n"
            
            output += "📊 RECOMMENDATION:\n"
            output += f"Action: {result['recommendation']['action']}\n"
            output += f"Confidence: {result['recommendation']['confidence']}%\n"
            output += f"Summary: {result['recommendation']['summary']}\n"
            
            return output
        
        # Run async function
        return asyncio.run(debate())
    
    except Exception as e:
        return f"❌ AI Debate failed: {str(e)}\n\n💡 Make sure OpenRouter API key is configured in Secrets"

def run_portfolio_refresh():
    try:
        import asyncio
        from live_portfolio_engine import LivePortfolioEngine
        
        async def refresh():
            engine = LivePortfolioEngine()
            positions = await engine.get_live_portfolio()
            summary = engine.generate_portfolio_summary(positions)
            
            result = "🔄 PORTFOLIO REFRESHED\n"
            result += "=" * 30 + "\n\n"
            result += f"💰 Total Value: ${summary['total_value']:,.2f}\n"
            result += f"📊 Total P&L: ${summary['total_pl']:,.2f} ({summary['total_pl_percent']:+.1f}%)\n"
            result += f"🏆 Winners: {summary['winners_count']} | 📉 Losers: {summary['losers_count']}\n"
            result += f"🤖 AI Recs: {summary['buy_recommendations']} BUY | {summary['sell_recommendations']} SELL | {summary['hold_recommendations']} HOLD\n\n"
            
            if summary['highest_performer']:
                hp = summary['highest_performer']
                result += f"🥇 Best: {hp.ticker} ({hp.unrealized_pl_percent:+.1f}%)\n"
            
            if summary['lowest_performer']:
                lp = summary['lowest_performer']
                result += f"🔻 Worst: {lp.ticker} ({lp.unrealized_pl_percent:+.1f}%)\n"
            
            result += "\n✅ Portfolio tiles updated with live data!"
            return result
        
        return asyncio.run(refresh())
    
    except Exception as e:
        return f"❌ Portfolio refresh failed: {str(e)}"

def generate_portfolio_tiles_html():
    try:
        import asyncio
        from live_portfolio_engine import LivePortfolioEngine
        
        async def get_tiles():
            engine = LivePortfolioEngine()
            positions = await engine.get_live_portfolio()
            
            if not positions:
                return '<div class="loading-tile"><p>No positions found</p></div>'
            
            html = ""
            for pos in positions:
                positive_class = "positive" if pos.unrealized_pl >= 0 else "negative"
                rec_class = f"rec-{pos.ai_recommendation.lower()}"
                
                html += f'''
                <div class="portfolio-tile {positive_class}" onclick="showStockDetails('{pos.ticker}')">
                    <div class="tile-header">
                        <span class="ticker-symbol">{pos.ticker}</span>
                        <span class="recommendation {rec_class}">{pos.ai_recommendation}</span>
                    </div>
                    <div class="tile-metrics">
                        <div>${pos.current_price:.2f} ({pos.day_change_percent:+.1f}%)</div>
                        <div>${pos.market_value:,.0f} ({pos.current_allocation:.1f}%)</div>
                        <div>P&L: {pos.unrealized_pl_percent:+.1f}%</div>
                        <div>AI: {pos.ai_confidence}% confidence</div>
                    </div>
                </div>
                '''
            
            return html
        
        return asyncio.run(get_tiles())
    
    except Exception as e:
        return f'<div class="loading-tile"><p>❌ Error: {str(e)}</p></div>'

def generate_stock_details_html(ticker):
    try:
        import asyncio
        from live_portfolio_engine import LivePortfolioEngine
        
        async def get_details():
            engine = LivePortfolioEngine()
            positions = await engine.get_live_portfolio()
            
            # Find the specific position
            position = None
            for pos in positions:
                if pos.ticker == ticker:
                    position = pos
                    break
            
            if not position:
                return f"<h3>❌ Position Not Found</h3><p>{ticker} not found in portfolio</p>"
            
            rec_color = {
                'BUY': '#4CAF50',
                'SELL': '#F44336', 
                'HOLD': '#FF9800'
            }.get(position.ai_recommendation, '#666')
            
            html = f'''
            <h2>{position.ticker} - {position.company_name}</h2>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                <div>
                    <h3>📊 Position Details</h3>
                    <p><strong>Shares:</strong> {position.shares:,.0f}</p>
                    <p><strong>Current Price:</strong> ${position.current_price:.2f}</p>
                    <p><strong>Market Value:</strong> ${position.market_value:,.2f}</p>
                    <p><strong>Cost Basis:</strong> ${position.cost_basis:.2f}</p>
                    <p><strong>Day Change:</strong> {position.day_change_percent:+.1f}%</p>
                </div>
                
                <div>
                    <h3>💰 Performance</h3>
                    <p><strong>Unrealized P&L:</strong> ${position.unrealized_pl:,.2f}</p>
                    <p><strong>P&L Percentage:</strong> {position.unrealized_pl_percent:+.1f}%</p>
                    <p><strong>Portfolio Weight:</strong> {position.current_allocation:.1f}%</p>
                    <p><strong>Sector:</strong> {position.sector}</p>
                    <p><strong>Risk Level:</strong> {position.risk_level}</p>
                </div>
            </div>
            
            <div style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3 style="color: {rec_color};">🤖 AI RECOMMENDATION: {position.ai_recommendation}</h3>
                <p><strong>Confidence:</strong> {position.ai_confidence}%</p>
                <p><strong>Position Sizing:</strong> {position.position_size_rec}</p>
                <p><strong>Target Allocation:</strong> {position.target_allocation:.1f}%</p>
            </div>
            
            <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;">
                <h3>📝 Investment Thesis</h3>
                <p style="line-height: 1.6;">{position.thesis}</p>
            </div>
            
            <div style="margin-top: 20px; text-align: center;">
                <button onclick="document.getElementById('stockModal').style.display='none'" 
                        style="background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                    Close
                </button>
            </div>
            '''
            
            return html
        
        return asyncio.run(get_details())
    
    except Exception as e:
        return f"<h3>❌ Error</h3><p>Failed to load {ticker}: {str(e)}</p>"

def run_market_analysis():
    try:
        import asyncio
        from polygon_market_engine import PolygonMarketEngine
        from live_portfolio_engine import LivePortfolioEngine
        
        async def analyze():
            # Get portfolio tickers
            portfolio_engine = LivePortfolioEngine()
            positions = await portfolio_engine.get_live_portfolio()
            tickers = [pos.ticker for pos in positions[:5]]  # Limit for demo
            
            # Run Polygon analysis
            polygon_engine = PolygonMarketEngine()
            current_session = polygon_engine.get_current_session()
            analysis = await polygon_engine.analyze_portfolio_session(tickers)
            
            result = "📈 POLYGON.IO MARKET ANALYSIS\n"
            result += "=" * 45 + "\n"
            result += f"🕐 Current Session: {current_session.upper()}\n\n"
            
            # Session insights
            for ticker, data in analysis['tickers'].items():
                result += f"📊 {ticker}:\n"
                
                snapshot = data.get('snapshot')
                if snapshot:
                    result += f"   💰 Price: ${snapshot.price:.2f}\n"
                    result += f"   📈 Spread: {snapshot.spread_percent:.2f}%\n"
                    result += f"   📊 Volume: {snapshot.volume:,}\n"
                
                news = data.get('news', [])
                if news:
                    result += f"   📰 Latest: {news[0].title[:50]}...\n"
                    result += f"   📊 Sentiment: {news[0].sentiment}\n"
                
                options = data.get('options_flow', [])
                if options:
                    total_premium = sum(opt.premium for opt in options)
                    result += f"   🎯 Options Flow: ${total_premium:,.0f}\n"
                
                alerts = data.get('alerts', [])
                if alerts:
                    result += f"   ⚠️ Alerts: {len(alerts)} items\n"
                
                result += "\n"
            
            # Recommendations
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                result += "🤖 AI RECOMMENDATIONS:\n"
                for rec in recommendations:
                    result += f"• {rec['ticker']}: {rec['action']} - {rec['reason']}\n"
            
            return result
        
        return asyncio.run(analyze())
    
    except Exception as e:
        return f"❌ Market analysis failed: {str(e)}\n\n💡 Configure POLYGON_API_KEY in Secrets"

def run_slack_test():
    try:
        import asyncio
        from slack_trading_bot import SlackTradingBot, TradeRecommendation
        from live_portfolio_engine import LivePortfolioEngine
        from datetime import datetime, timedelta
        
        async def test_slack():
            slack_bot = SlackTradingBot()
            
            # Get sample portfolio data
            portfolio_engine = LivePortfolioEngine()
            positions = await portfolio_engine.get_live_portfolio()
            summary = portfolio_engine.generate_portfolio_summary(positions)
            
            # Create sample recommendation
            if positions:
                top_position = positions[0]
                sample_rec = TradeRecommendation(
                    id=f"test_{datetime.now().timestamp()}",
                    ticker=top_position.ticker,
                    action=top_position.ai_recommendation,
                    quantity=50,
                    current_price=top_position.current_price,
                    reason="Test recommendation from web interface",
                    confidence=top_position.ai_confidence,
                    expiry=datetime.now() + timedelta(hours=1)
                )
                
                # Prepare test data
                portfolio_data = {
                    'summary': {
                        'total_value': summary['total_value'],
                        'total_pl': summary['total_pl'],
                        'total_pl_percent': summary['total_pl_percent'],
                        'winners_count': summary['winners_count'],
                        'losers_count': summary['losers_count']
                    },
                    'positions': [
                        {
                            'ticker': pos.ticker,
                            'current_price': pos.current_price,
                            'day_change_percent': pos.day_change_percent,
                            'unrealized_pl_percent': pos.unrealized_pl_percent
                        }
                        for pos in positions[:3]
                    ]
                }
                
                market_analysis = {
                    'alerts': [
                        f"📊 Test alert for {top_position.ticker}",
                        "💡 This is a test message from the web interface"
                    ]
                }
                
                # Send test update
                await slack_bot.send_portfolio_update(
                    'test', portfolio_data, market_analysis, [sample_rec]
                )
                
                return "✅ Test message sent to Slack!\n\nCheck your trading channel for the portfolio update."
            else:
                return "⚠️ No portfolio positions found for test"
        
        return asyncio.run(test_slack())
    
    except Exception as e:
        return f"❌ Slack test failed: {str(e)}\n\n💡 Configure SLACK_WEBHOOK_URL in Secrets"

def get_help_info():
    return """📖 HELP & DOCUMENTATION
========================

🔑 API SETUP:
• Get Claude API: https://console.anthropic.com/
• Get OpenAI API: https://platform.openai.com/api-keys
• Get Alpaca API: https://app.alpaca.markets/
• Add keys to Replit Secrets tab

🚀 SYSTEM FEATURES:
• Real-time stock discovery using live market data
• AI-powered analysis with Claude vs ChatGPT debates
• Portfolio optimization and risk management
• Safety systems prevent trading with mock data

🧪 TESTING:
• API Check: Verify if API keys are configured
• Safety Check: Validate system safety (shows issues)
• Stock Discovery: Test discovery with real market data
• Portfolio Analysis: Analyze your current holdings

💡 TROUBLESHOOTING:
• If API errors: Check Secrets tab configuration
• If no opportunities: Normal during low volatility
• If imports fail: Dependencies should auto-install
• System uses real-time data when APIs are configured

📊 CURRENT STATUS:
• System ready for commands
• All functions available through web interface
• Real-time data integration active
• Safe trading mode enabled"""

def run_console_version():
    """Run the original console version"""
    print("🚀 AI TRADING SYSTEM v2.0")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💰 Real-Time Stock Discovery & Portfolio Analysis")
    print()
    
    print("🔍 SYSTEM MENU:")
    print("1. 🔑 Check API Keys & Setup")
    print("2. 🛡️ Validate System Safety") 
    print("3. 📊 Discover New Stocks")
    print("4. 💰 Analyze Your Portfolio")
    print("5. 🚀 Start Full Trading System")
    print("6. 🧪 Quick Market Check")
    print("7. 📖 Help & Documentation")
    print()
    
    while True:
        try:
            choice = input("➤ Enter choice (1-7) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("👋 System stopped. Happy trading!")
                break
                
            elif choice == '1':
                print(run_api_check())
                
            elif choice == '2':
                print(run_safety_check())
                
            elif choice == '3':
                print(run_stock_discovery())
                
            elif choice == '4':
                print(run_portfolio_analysis())
                
            elif choice == '5':
                start_full_system()
                
            elif choice == '6':
                print(run_market_check())
                
            elif choice == '7':
                print(get_help_info())
                
            else:
                print("❌ Invalid choice. Please enter 1-7 or 'q'")
                
            print("\n" + "─" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 System stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def start_full_system():
    """Start the full autonomous trading system"""
    print("\n🚀 STARTING FULL TRADING SYSTEM...")
    
    try:
        # First run safety check
        from trading_safety_validator import emergency_trading_safety_check
        
        is_safe, violations = emergency_trading_safety_check()
        
        if not is_safe:
            print("🛑 SYSTEM BLOCKED FOR SAFETY")
            print("❌ Cannot start with mock data detected")
            print("💡 Configure API keys first")
            return
        
        print("✅ Safety check passed")
        print("🚀 Starting autonomous system...")
        
        # Run the full system
        os.system("python3 utils/start_autonomous_system.py")
        
    except ImportError:
        print("❌ Full system not available. Upload start_autonomous_system.py")
    except Exception as e:
        print(f"❌ System start failed: {e}")

# Portfolio Web Interface Functions
def generate_portfolio_tiles():
    """Generate HTML for portfolio tiles"""
    return generate_portfolio_tiles_html()

def generate_portfolio_tiles_html():
    """Generate portfolio tiles with live data"""
    try:
        import asyncio
        from live_portfolio_engine import LivePortfolioEngine
        
        # Get live portfolio
        engine = LivePortfolioEngine()
        positions = asyncio.run(engine.get_live_portfolio())
        
        if not positions:
            return '<div class="loading-tile"><p>No positions found</p></div>'
        
        html = ""
        for pos in positions:
            # Color based on performance
            color_class = "gain" if pos.unrealized_pl >= 0 else "loss"
            ai_color = {"BUY": "#4CAF50", "SELL": "#F44336", "HOLD": "#FF9800"}.get(pos.ai_recommendation, "#999")
            
            html += f'''
            <div class="stock-tile {color_class}" onclick="showStockDetails('{pos.ticker}')">
                <div class="stock-header">
                    <h3>{pos.ticker}</h3>
                    <span class="stock-price">${pos.current_price:.2f}</span>
                </div>
                <div class="stock-info">
                    <div class="stock-change {color_class}">
                        {pos.day_change_percent:+.1f}% today
                    </div>
                    <div class="stock-value">
                        ${pos.market_value:,.0f} ({pos.current_allocation:.1f}%)
                    </div>
                    <div class="stock-pl {color_class}">
                        P&L: ${pos.unrealized_pl:+,.0f} ({pos.unrealized_pl_percent:+.1f}%)
                    </div>
                </div>
                <div class="ai-recommendation" style="background: {ai_color}">
                    {pos.ai_recommendation} {pos.ai_confidence}%
                </div>
                <div class="stock-risk risk-{pos.risk_level.lower()}">
                    {pos.risk_level} RISK
                </div>
            </div>
            '''
        
        return html
        
    except Exception as e:
        return f'<div class="loading-tile"><p>❌ Error: {str(e)}</p></div>'

def generate_stock_details_html(ticker):
    """Generate detailed stock analysis HTML"""
    try:
        import asyncio
        from live_portfolio_engine import LivePortfolioEngine
        
        # Get position details
        engine = LivePortfolioEngine()
        positions = asyncio.run(engine.get_live_portfolio())
        
        # Find the specific position
        position = None
        for pos in positions:
            if pos.ticker == ticker:
                position = pos
                break
        
        if not position:
            return f'<h3>❌ Position Not Found</h3><p>{ticker} not in portfolio</p>'
        
        # Color based on performance
        color = "#4CAF50" if position.unrealized_pl >= 0 else "#F44336"
        ai_color = {"BUY": "#4CAF50", "SELL": "#F44336", "HOLD": "#FF9800"}.get(position.ai_recommendation, "#999")
        
        html = f'''
        <h2>{position.ticker} - {position.company_name}</h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
            <div>
                <h3>📊 Position Details</h3>
                <p><strong>Shares:</strong> {position.shares:,.0f}</p>
                <p><strong>Current Price:</strong> ${position.current_price:.2f}</p>
                <p><strong>Market Value:</strong> ${position.market_value:,.2f}</p>
                <p><strong>Portfolio Weight:</strong> {position.current_allocation:.1f}%</p>
                <p><strong>Cost Basis:</strong> ${position.cost_basis:.2f}</p>
            </div>
            
            <div>
                <h3>📈 Performance</h3>
                <p style="color: {color}"><strong>Daily Change:</strong> {position.day_change_percent:+.1f}%</p>
                <p style="color: {color}"><strong>Unrealized P&L:</strong> ${position.unrealized_pl:+,.2f}</p>
                <p style="color: {color}"><strong>Total Return:</strong> {position.unrealized_pl_percent:+.1f}%</p>
                <p><strong>Sector:</strong> {position.sector}</p>
                <p><strong>Risk Level:</strong> {position.risk_level}</p>
            </div>
        </div>
        
        <div style="background: {ai_color}; padding: 15px; border-radius: 10px; margin: 20px 0;">
            <h3>🤖 AI Recommendation</h3>
            <p><strong>Action:</strong> {position.ai_recommendation} (Confidence: {position.ai_confidence}%)</p>
            <p><strong>Position Sizing:</strong> {position.position_size_rec}</p>
            <p><strong>Target Allocation:</strong> {position.target_allocation:.1f}%</p>
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 20px 0;">
            <h3>📝 Investment Thesis</h3>
            <p style="line-height: 1.6;">{position.thesis}</p>
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 20px 0;">
            <h3>📊 Technical Analysis</h3>
            <p>• Current trend: {"Bullish" if position.day_change >= 0 else "Bearish"}</p>
            <p>• Portfolio impact: {"High" if position.current_allocation > 15 else "Medium" if position.current_allocation > 5 else "Low"}</p>
            <p>• Risk assessment: {position.risk_level} volatility expected</p>
        </div>
        
        <div style="margin-top: 20px;">
            <h3>🎯 Next Actions</h3>
            <ul style="line-height: 1.6;">
        '''
        
        # Add specific recommendations based on AI analysis
        if position.ai_recommendation == "BUY":
            html += '<li>✅ Consider increasing position if market conditions remain favorable</li>'
            html += '<li>📈 Monitor for entry points on any pullbacks</li>'
        elif position.ai_recommendation == "SELL":
            html += '<li>⚠️ Consider reducing position or taking profits</li>'
            html += '<li>📉 Watch for deteriorating fundamentals</li>'
        else:
            html += '<li>⏸️ Maintain current position size</li>'
            html += '<li>👀 Monitor for significant developments</li>'
        
        html += f'''
            <li>🎯 Target portfolio allocation: {position.target_allocation:.1f}%</li>
            <li>⚖️ Risk management: {position.risk_level} risk position</li>
            </ul>
        </div>
        '''
        
        return html
        
    except Exception as e:
        return f'<h3>❌ Error</h3><p>Failed to load {ticker} details: {str(e)}</p>'

if __name__ == "__main__":
    # Check if running in Replit (web mode) or console
    if os.getenv('REPLIT_ENVIRONMENT'):
        print("🌐 Starting web interface for Replit...")
        app.run(host='0.0.0.0', port=8080, debug=False)
    else:
        # Run console version for local development
        run_console_version()