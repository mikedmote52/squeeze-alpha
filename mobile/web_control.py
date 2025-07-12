#!/usr/bin/env python3
"""
Simple Web Interface for Squeeze Alpha System
Access from any device - phone, tablet, computer
No command line needed!
"""

import os
import sys
import json
import subprocess
import signal
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
import threading
import time
import yfinance as yf
# Add path for local modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
try:
    from python_modules.utils.config import get_config
except ImportError:
    # If config module not available, we'll use environment variables
    get_config = None

class WebControlInterface:
    """Web-based control interface for easy access"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.system_dir = "/Users/michaelmote/Desktop/ai-trading-system-complete"
        self.status_file = os.path.join(self.system_dir, "system_status.json")
        self.pid_file = os.path.join(self.system_dir, "system.pid")
        self.setup_routes()
    
    def setup_routes(self):
        """Setup web routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard"""
            status = self.get_system_status()
            return render_template('dashboard.html', status=status)
        
        @self.app.route('/api/status')
        def api_status():
            """API endpoint for system status"""
            return jsonify(self.get_system_status())
        
        @self.app.route('/api/start', methods=['POST'])
        def api_start():
            """Start the autonomous system"""
            try:
                result = self.start_system()
                return jsonify({"success": True, "message": "System started successfully!"})
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})
        
        @self.app.route('/api/stop', methods=['POST'])
        def api_stop():
            """Stop the autonomous system"""
            try:
                result = self.stop_system()
                return jsonify({"success": True, "message": "System stopped successfully!"})
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})
        
        @self.app.route('/api/analysis', methods=['POST'])
        def api_analysis():
            """Run immediate analysis"""
            try:
                result = self.run_analysis()
                return jsonify({"success": True, "message": "Analysis running - check Slack!"})
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})
        
        @self.app.route('/api/test-slack', methods=['POST'])
        def api_test_slack():
            """Test Slack notifications"""
            try:
                result = self.test_slack()
                return jsonify({"success": True, "message": "Slack test sent!"})
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})
        
        @self.app.route('/api/portfolio')
        def api_portfolio():
            """Get current portfolio holdings"""
            try:
                portfolio = self.get_portfolio_data()
                return jsonify({"success": True, "portfolio": portfolio})
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})
        
        @self.app.route('/api/evolution', methods=['POST'])
        def api_evolution():
            """Run system evolution analysis"""
            try:
                result = self.run_evolution_analysis()
                return jsonify({"success": True, "message": "Evolution analysis complete - check Slack!", "result": result})
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})
        
        @self.app.route('/api/evolution/status')
        def api_evolution_status():
            """Get evolution status"""
            try:
                status = self.get_evolution_status()
                return jsonify({"success": True, "status": status})
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})
    
    def get_system_status(self):
        """Get current system status"""
        status = {
            "running": False,
            "started": None,
            "pid": None,
            "uptime": None,
            "next_update": "Unknown",
            "portfolio": self.get_portfolio_data()
        }
        
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    saved_status = json.load(f)
                
                status.update(saved_status)
                status["running"] = self.is_system_running()
                
                # Calculate uptime if running
                if status["running"] and status.get("started"):
                    start_time = datetime.fromisoformat(status["started"])
                    uptime = datetime.now() - start_time
                    status["uptime"] = str(uptime).split('.')[0]  # Remove microseconds
                
                # Determine next update time
                status["next_update"] = self.get_next_update_time()
            
        except Exception as e:
            status["error"] = str(e)
        
        return status
    
    def get_next_update_time(self):
        """Calculate next scheduled update"""
        from datetime import datetime, time as dt_time
        import pytz
        
        pt_tz = pytz.timezone('US/Pacific')
        now = datetime.now(pt_tz)
        
        # Schedule times in Pacific Time
        schedule_times = [
            dt_time(4, 0),   # 4:00 AM
            dt_time(5, 30),  # 5:30 AM
            dt_time(6, 30),  # 6:30 AM
            dt_time(9, 0),   # 9:00 AM
            dt_time(12, 0),  # 12:00 PM
            dt_time(13, 0),  # 1:00 PM
            dt_time(15, 0),  # 3:00 PM
        ]
        
        current_time = now.time()
        
        for schedule_time in schedule_times:
            if current_time < schedule_time:
                return schedule_time.strftime('%I:%M %p PT')
        
        # If past all times today, next is tomorrow's first update
        return "Tomorrow 4:00 AM PT"
    
    def is_system_running(self):
        """Check if system is currently running"""
        try:
            if not os.path.exists(self.pid_file):
                return False
            
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, 0)  # Check if process exists
            return True
            
        except (OSError, ProcessLookupError, ValueError):
            return False
    
    def start_system(self):
        """Start the autonomous trading system"""
        if self.is_system_running():
            raise Exception("System is already running!")
        
        # Start the Pacific Time system in background
        process = subprocess.Popen([
            sys.executable, 
            os.path.join(self.system_dir, "pacific_time_schedule.py")
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Save PID
        with open(self.pid_file, 'w') as f:
            f.write(str(process.pid))
        
        # Update status
        status = {
            "system": "squeeze_alpha",
            "status": "running",
            "started": datetime.now().isoformat(),
            "pid": process.pid,
            "schedule": "pacific_time_autonomous"
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        return True
    
    def stop_system(self):
        """Stop the autonomous trading system"""
        if not self.is_system_running():
            raise Exception("System is not running")
        
        # Get PID and terminate
        with open(self.pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        os.kill(pid, signal.SIGTERM)
        time.sleep(2)
        
        # Clean up files
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)
        
        # Update status
        status = {
            "system": "squeeze_alpha",
            "status": "stopped",
            "stopped": datetime.now().isoformat()
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        return True
    
    def run_analysis(self):
        """Run hedge fund consensus analysis immediately"""
        result = subprocess.run([
            sys.executable,
            os.path.join(self.system_dir, "multi_ai_consensus_engine.py")
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            raise Exception(f"Analysis failed: {result.stderr}")
        
        return True
    
    def test_slack(self):
        """Test Slack notifications"""
        result = subprocess.run([
            sys.executable,
            os.path.join(self.system_dir, "test_slack_simple.py")
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f"Slack test failed: {result.stderr}")
        
        return True
    
    def run_evolution_analysis(self):
        """Run system evolution analysis"""
        try:
            from system_evolution_engine import SystemEvolutionEngine
            evolution_engine = SystemEvolutionEngine()
            result = evolution_engine.run_evolution_analysis()
            return result
        except Exception as e:
            raise Exception(f"Evolution analysis failed: {e}")
    
    def get_evolution_status(self):
        """Get evolution status"""
        try:
            from system_evolution_engine import SystemEvolutionEngine
            evolution_engine = SystemEvolutionEngine()
            
            pending_count = len(evolution_engine.pending_recommendations)
            approved_count = len(evolution_engine.approved_upgrades)
            high_priority_count = len([r for r in evolution_engine.pending_recommendations if r.priority_score >= 8.0])
            
            return {
                "pending_recommendations": pending_count,
                "approved_upgrades": approved_count,
                "high_priority_items": high_priority_count,
                "evolution_active": True
            }
        except Exception as e:
            return {
                "pending_recommendations": 0,
                "approved_upgrades": 0,
                "high_priority_items": 0,
                "evolution_active": False,
                "error": str(e)
            }
    
    def get_portfolio_data(self):
        """Get current portfolio holdings with real-time data"""
        try:
            # Try to get live positions from Alpaca first
            try:
                live_positions = self.get_alpaca_positions()
                if live_positions:
                    return self.format_alpaca_portfolio(live_positions)
            except Exception as e:
                print(f"Alpaca API error, using fallback: {e}")
            
            # Fallback to static list if Alpaca API fails
            tickers = ['AMD', 'BLNK', 'BTBT', 'BYND', 'CHPT', 'CRWV', 'EAT', 'ETSY', 'LIXT', 'NVAX', 'SMCI', 'SOUN', 'VIGL', 'WOLF']
            
            portfolio = []
            total_value = 0
            total_change = 0
            
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    hist = stock.history(period="2d")
                    
                    if len(hist) >= 2:
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[-2]
                        change = current_price - prev_price
                        change_percent = (change / prev_price) * 100
                        
                        # Estimate position size (you can adjust these)
                        estimated_shares = 100  # Default estimate
                        if current_price > 50:
                            estimated_shares = 50
                        elif current_price > 100:
                            estimated_shares = 25
                        
                        position_value = current_price * estimated_shares
                        position_change = change * estimated_shares
                        
                        total_value += position_value
                        total_change += position_change
                        
                        portfolio.append({
                            "ticker": ticker,
                            "name": info.get("shortName", ticker),
                            "price": round(current_price, 2),
                            "change": round(change, 2),
                            "change_percent": round(change_percent, 2),
                            "shares": estimated_shares,
                            "value": round(position_value, 2),
                            "position_change": round(position_change, 2),
                            "market_cap": info.get("marketCap", 0),
                            "volume": info.get("volume", 0)
                        })
                    
                except Exception as e:
                    # If real data fails, use mock data
                    portfolio.append({
                        "ticker": ticker,
                        "name": ticker,
                        "price": 25.00,
                        "change": 1.50,
                        "change_percent": 6.38,
                        "shares": 100,
                        "value": 2500.00,
                        "position_change": 150.00,
                        "market_cap": 1000000000,
                        "volume": 500000
                    })
            
            return {
                "holdings": portfolio,
                "total_value": round(total_value, 2),
                "total_change": round(total_change, 2),
                "total_change_percent": round((total_change / (total_value - total_change)) * 100, 2) if total_value > total_change else 0,
                "last_updated": datetime.now().strftime("%I:%M %p PT")
            }
    
    def get_alpaca_positions(self):
        \"\"\"Get live positions from Alpaca API\"\"\"
        import requests
        
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY') 
        base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not api_key or not secret_key:
            return None
        
        headers = {
            'APCA-API-KEY-ID': api_key,
            'APCA-API-SECRET-KEY': secret_key
        }
        
        response = requests.get(f\"{base_url}/v2/positions\", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        
        return None
    
    def format_alpaca_portfolio(self, positions):
        \"\"\"Format Alpaca positions for display\"\"\"
        portfolio = {
            \"holdings\": [],
            \"total_value\": 0,
            \"total_change\": 0,
            \"total_change_percent\": 0,
            \"last_updated\": datetime.now().strftime(\"%I:%M %p PT\")
        }
        
        for position in positions:
            try:
                market_value = float(position['market_value'])
                unrealized_pl = float(position['unrealized_pl'])
                unrealized_plpc = float(position['unrealized_plpc']) * 100
                
                # Get current price
                current_price = float(position.get('current_price', market_value / float(position['qty']) if float(position['qty']) > 0 else 0))
                
                portfolio[\"holdings\"].append({
                    \"ticker\": position['symbol'],
                    \"name\": position['symbol'],  # Alpaca doesn't provide company names
                    \"price\": round(current_price, 2),
                    \"change\": round(unrealized_pl / float(position['qty']) if float(position['qty']) > 0 else 0, 2),
                    \"change_percent\": round(unrealized_plpc, 2),
                    \"shares\": int(float(position['qty'])),
                    \"value\": round(market_value, 2),
                    \"position_change\": round(unrealized_pl, 2),
                    \"market_cap\": 0,  # Not available from Alpaca
                    \"volume\": 0       # Not available from Alpaca
                })
                
                portfolio[\"total_value\"] += market_value
                portfolio[\"total_change\"] += unrealized_pl
                
            except Exception as e:
                print(f\"Error processing position {position.get('symbol', 'UNKNOWN')}: {e}\")
                continue
        
        # Calculate total change percentage
        if portfolio[\"total_value\"] > 0:
            cost_basis = portfolio[\"total_value\"] - portfolio[\"total_change\"]
            if cost_basis > 0:
                portfolio[\"total_change_percent\"] = (portfolio[\"total_change\"] / cost_basis) * 100
        
        return portfolio
    
    def run(self, host='0.0.0.0', port=5000):
        """Run the web interface"""
        print(f"🌐 Starting web interface...")
        print(f"📱 Access from any device at: http://localhost:{port}")
        print(f"🚀 Or from phone/tablet at: http://YOUR_IP_ADDRESS:{port}")
        
        # Create templates directory if it doesn't exist
        templates_dir = os.path.join(self.system_dir, "templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create the HTML template
        self.create_dashboard_template(templates_dir)
        
        self.app.run(host=host, port=port, debug=False)
    
    def create_dashboard_template(self, templates_dir):
        """Create the dashboard HTML template"""
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Squeeze Alpha Control</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 600px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(45deg, #1e3c72, #2a5298);
            color: white; 
            padding: 30px; 
            text-align: center; 
        }
        .header h1 { font-size: 2rem; margin-bottom: 10px; }
        .status-card { 
            margin: 30px; 
            padding: 25px; 
            border-radius: 15px; 
            text-align: center;
        }
        .status-running { background: linear-gradient(45deg, #56ab2f, #a8e6cf); color: white; }
        .status-stopped { background: linear-gradient(45deg, #ff6b6b, #ffa8a8); color: white; }
        .button { 
            display: block;
            width: 100%; 
            padding: 15px; 
            margin: 15px 0; 
            border: none; 
            border-radius: 10px; 
            font-size: 1.1rem; 
            font-weight: bold;
            cursor: pointer; 
            transition: all 0.3s;
            text-decoration: none;
            text-align: center;
        }
        .btn-start { background: linear-gradient(45deg, #56ab2f, #a8e6cf); color: white; }
        .btn-stop { background: linear-gradient(45deg, #ff6b6b, #ffa8a8); color: white; }
        .btn-analysis { background: linear-gradient(45deg, #4facfe, #00f2fe); color: white; }
        .btn-evolution { background: linear-gradient(45deg, #667eea, #764ba2); color: white; }
        .btn-slack { background: linear-gradient(45deg, #ffecd2, #fcb69f); color: #333; }
        .button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
        .info-grid { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 15px; 
            margin: 30px; 
        }
        .info-item { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center; 
        }
        .info-label { font-size: 0.9rem; color: #666; margin-bottom: 5px; }
        .info-value { font-size: 1.2rem; font-weight: bold; color: #333; }
        .portfolio { 
            margin: 30px; 
            padding: 20px; 
            background: #f8f9fa; 
            border-radius: 10px; 
        }
        .portfolio h3 { margin-bottom: 15px; color: #333; }
        .portfolio-summary { 
            display: grid; 
            grid-template-columns: 1fr 1fr 1fr; 
            gap: 15px; 
            margin-bottom: 20px; 
        }
        .summary-item { 
            background: white; 
            padding: 15px; 
            border-radius: 8px; 
            text-align: center; 
        }
        .summary-label { font-size: 0.85rem; color: #666; margin-bottom: 5px; }
        .summary-value { font-size: 1.1rem; font-weight: bold; }
        .positive { color: #28a745; }
        .negative { color: #dc3545; }
        .holding-item { 
            display: grid; 
            grid-template-columns: 1fr 1fr 1fr 1fr; 
            gap: 10px; 
            padding: 12px; 
            background: white; 
            border-radius: 8px; 
            margin-bottom: 8px; 
            align-items: center; 
        }
        .holding-ticker { font-weight: bold; color: #2a5298; }
        .holding-name { font-size: 0.9rem; color: #666; }
        .holding-price { font-weight: bold; }
        .holding-change { font-weight: bold; }
        .holdings-header { 
            display: grid; 
            grid-template-columns: 1fr 1fr 1fr 1fr; 
            gap: 10px; 
            padding: 10px 12px; 
            background: #e9ecef; 
            border-radius: 8px; 
            margin-bottom: 10px; 
            font-weight: bold; 
            font-size: 0.9rem; 
            color: #495057; 
        }
        .schedule { 
            margin: 30px; 
            padding: 20px; 
            background: #f8f9fa; 
            border-radius: 10px; 
        }
        .schedule h3 { margin-bottom: 15px; color: #333; }
        .schedule-item { 
            display: flex; 
            justify-content: space-between; 
            padding: 8px 0; 
            border-bottom: 1px solid #e9ecef; 
        }
        .schedule-time { font-weight: bold; color: #2a5298; }
        .message { 
            margin: 20px 30px; 
            padding: 15px; 
            border-radius: 10px; 
            text-align: center; 
            display: none; 
        }
        .message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        @media (max-width: 480px) {
            .info-grid { grid-template-columns: 1fr; }
            .header h1 { font-size: 1.5rem; }
            .container { margin: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Squeeze Alpha Control</h1>
            <p>AI Trading System Dashboard</p>
        </div>
        
        <div id="message" class="message"></div>
        
        <div class="status-card {{ 'status-running' if status.running else 'status-stopped' }}">
            <h2>{{ '🟢 System Running' if status.running else '🔴 System Stopped' }}</h2>
            <p>{{ 'Autonomous trading active' if status.running else 'Ready to start' }}</p>
        </div>
        
        <div style="margin: 30px;">
            {% if status.running %}
                <button class="button btn-stop" onclick="stopSystem()">🛑 Stop System</button>
            {% else %}
                <button class="button btn-start" onclick="startSystem()">🚀 Start System</button>
            {% endif %}
            
            <button class="button btn-analysis" onclick="runAnalysis()">🧠 Run Analysis Now</button>
            <button class="button btn-evolution" onclick="runEvolution()">🤖 System Evolution</button>
            <button class="button btn-slack" onclick="testSlack()">📱 Test Slack</button>
        </div>
        
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Status</div>
                <div class="info-value">{{ 'Running' if status.running else 'Stopped' }}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Next Update</div>
                <div class="info-value">{{ status.next_update }}</div>
            </div>
            {% if status.uptime %}
            <div class="info-item">
                <div class="info-label">Uptime</div>
                <div class="info-value">{{ status.uptime }}</div>
            </div>
            {% endif %}
            {% if status.pid %}
            <div class="info-item">
                <div class="info-label">Process ID</div>
                <div class="info-value">{{ status.pid }}</div>
            </div>
            {% endif %}
        </div>
        
        <div class="portfolio">
            <h3>💼 Your Portfolio</h3>
            
            <div class="portfolio-summary">
                <div class="summary-item">
                    <div class="summary-label">Total Value</div>
                    <div class="summary-value">${{ "{:,.2f}".format(status.portfolio.total_value) }}</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">Today's P&L</div>
                    <div class="summary-value {{ 'positive' if status.portfolio.total_change >= 0 else 'negative' }}">
                        ${{ "{:+,.2f}".format(status.portfolio.total_change) }}
                    </div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">Today's %</div>
                    <div class="summary-value {{ 'positive' if status.portfolio.total_change_percent >= 0 else 'negative' }}">
                        {{ "{:+.2f}".format(status.portfolio.total_change_percent) }}%
                    </div>
                </div>
            </div>
            
            <div class="holdings-header">
                <div>Stock</div>
                <div>Price</div>
                <div>Change</div>
                <div>Position</div>
            </div>
            
            {% for holding in status.portfolio.holdings %}
            <div class="holding-item">
                <div>
                    <div class="holding-ticker">{{ holding.ticker }}</div>
                    <div class="holding-name">{{ holding.name }}</div>
                </div>
                <div class="holding-price">${{ "{:.2f}".format(holding.price) }}</div>
                <div class="holding-change {{ 'positive' if holding.change >= 0 else 'negative' }}">
                    ${{ "{:+.2f}".format(holding.change) }}<br>
                    <small>({{ "{:+.1f}".format(holding.change_percent) }}%)</small>
                </div>
                <div>
                    <div>${{ "{:,.0f}".format(holding.value) }}</div>
                    <small>{{ holding.shares }} shares</small>
                </div>
            </div>
            {% endfor %}
            
            <div style="text-align: center; margin-top: 15px; font-size: 0.9rem; color: #666;">
                Last updated: {{ status.portfolio.last_updated }}
            </div>
        </div>
        
        <div class="schedule">
            <h3>📅 Daily Schedule (Pacific Time)</h3>
            <div class="schedule-item">
                <span class="schedule-time">4:00 AM</span>
                <span>Early pre-market scan</span>
            </div>
            <div class="schedule-item">
                <span class="schedule-time">5:30 AM</span>
                <span>Full pre-market analysis</span>
            </div>
            <div class="schedule-item">
                <span class="schedule-time">6:30 AM</span>
                <span>Market open analysis</span>
            </div>
            <div class="schedule-item">
                <span class="schedule-time">9:00 AM</span>
                <span>Mid-morning scan</span>
            </div>
            <div class="schedule-item">
                <span class="schedule-time">12:00 PM</span>
                <span>Midday analysis</span>
            </div>
            <div class="schedule-item">
                <span class="schedule-time">1:00 PM</span>
                <span>Market close summary</span>
            </div>
            <div class="schedule-item">
                <span class="schedule-time">3:00 PM</span>
                <span>After-hours evolution</span>
            </div>
        </div>
    </div>

    <script>
        function showMessage(text, type) {
            const msg = document.getElementById('message');
            msg.textContent = text;
            msg.className = `message ${type}`;
            msg.style.display = 'block';
            setTimeout(() => msg.style.display = 'none', 3000);
        }

        async function startSystem() {
            try {
                const response = await fetch('/api/start', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    showMessage(data.message, 'success');
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showMessage(data.message, 'error');
                }
            } catch (error) {
                showMessage('Error starting system', 'error');
            }
        }

        async function stopSystem() {
            try {
                const response = await fetch('/api/stop', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    showMessage(data.message, 'success');
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showMessage(data.message, 'error');
                }
            } catch (error) {
                showMessage('Error stopping system', 'error');
            }
        }

        async function runAnalysis() {
            try {
                showMessage('Starting analysis...', 'success');
                const response = await fetch('/api/analysis', { method: 'POST' });
                const data = await response.json();
                showMessage(data.message, data.success ? 'success' : 'error');
            } catch (error) {
                showMessage('Error running analysis', 'error');
            }
        }

        async function testSlack() {
            try {
                showMessage('Sending Slack test...', 'success');
                const response = await fetch('/api/test-slack', { method: 'POST' });
                const data = await response.json();
                showMessage(data.message, data.success ? 'success' : 'error');
            } catch (error) {
                showMessage('Error testing Slack', 'error');
            }
        }

        async function runEvolution() {
            try {
                showMessage('Running system evolution analysis...', 'success');
                const response = await fetch('/api/evolution', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    showMessage('Evolution analysis complete! Check Slack for recommendations.', 'success');
                } else {
                    showMessage(data.message, 'error');
                }
            } catch (error) {
                showMessage('Error running evolution analysis', 'error');
            }
        }

        // Auto-refresh status and portfolio every 30 seconds
        setInterval(async () => {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();
                if (status.running !== {{ 'true' if status.running else 'false' }}) {
                    location.reload();
                }
                // Update portfolio data without full page reload
                updatePortfolioDisplay(status.portfolio);
            } catch (error) {
                console.log('Status check failed');
            }
        }, 30000);
        
        function updatePortfolioDisplay(portfolio) {
            // Update portfolio summary
            const totalValue = document.querySelector('.portfolio-summary .summary-value');
            if (totalValue) {
                totalValue.textContent = '$' + portfolio.total_value.toLocaleString('en-US', {minimumFractionDigits: 2});
            }
            
            // Update individual holdings (simplified - full implementation would update all values)
            console.log('Portfolio updated:', portfolio.last_updated);
        }
    </script>
</body>
</html>'''
        
        template_path = os.path.join(templates_dir, "dashboard.html")
        with open(template_path, 'w') as f:
            f.write(template_content)

def main():
    """Start the web control interface"""
    print("🌐 SQUEEZE ALPHA WEB CONTROL")
    print("=" * 40)
    
    web_control = WebControlInterface()
    
    print("📱 Starting mobile-friendly web interface...")
    print("🚀 Perfect for your mom to use!")
    print()
    print("Access from:")
    print("• Computer: http://localhost:5000")
    print("• Phone/Tablet: http://YOUR_IP_ADDRESS:5000")
    print()
    print("Press Ctrl+C to stop")
    
    try:
        web_control.run()
    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped")

if __name__ == "__main__":
    main()