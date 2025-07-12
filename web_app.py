#!/usr/bin/env python3
"""
Squeeze Alpha Web Application
Interactive trading interface for Replit deployment
"""

from flask import Flask, render_template, jsonify, request
import asyncio
import json
from datetime import datetime
from core.live_portfolio_engine import LivePortfolioEngine
from core.trade_execution_engine import TradeExecutionEngine
from core.secrets_manager import SecretsManager

app = Flask(__name__)
app.secret_key = 'squeeze_alpha_2024'

# Global instances
portfolio_engine = None
trade_engine = None

@app.route('/')
def index():
    """Main portfolio dashboard"""
    return render_template('index.html')

@app.route('/trades')
def trade_execution_page():
    """Trade execution interface"""
    return render_template('trade_execution.html')

@app.route('/api/portfolio')
async def get_portfolio():
    """API endpoint to get portfolio data"""
    try:
        global portfolio_engine
        if not portfolio_engine:
            portfolio_engine = LivePortfolioEngine()
        
        portfolio = await portfolio_engine.get_live_portfolio()
        portfolio_summary = await portfolio_engine.generate_portfolio_summary()
        
        # Convert portfolio positions to serializable format
        positions = []
        for pos in portfolio:
            positions.append({
                'ticker': pos.ticker,
                'company_name': pos.company_name,
                'shares': pos.shares,
                'current_price': pos.current_price,
                'market_value': pos.market_value,
                'cost_basis': pos.cost_basis,
                'unrealized_pl': pos.unrealized_pl,
                'unrealized_pl_percent': pos.unrealized_pl_percent,
                'day_change': pos.day_change,
                'day_change_percent': pos.day_change_percent,
                'sector': pos.sector,
                'ai_recommendation': pos.ai_recommendation,
                'ai_confidence': pos.ai_confidence,
                'position_size_rec': pos.position_size_rec,
                'thesis': pos.thesis,
                'risk_level': pos.risk_level,
                'target_allocation': pos.target_allocation,
                'current_allocation': pos.current_allocation
            })
        
        return jsonify({
            'success': True,
            'portfolio': positions,
            'summary': portfolio_summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trade-recommendations')
async def get_trade_recommendations():
    """Generate and return trade recommendations"""
    try:
        global portfolio_engine, trade_engine
        
        if not portfolio_engine:
            portfolio_engine = LivePortfolioEngine()
        if not trade_engine:
            trade_engine = TradeExecutionEngine()
        
        # Get current portfolio
        portfolio = await portfolio_engine.get_live_portfolio()
        
        # Generate trade recommendations
        recommendations = trade_engine.create_trade_recommendations(portfolio)
        
        # Convert to serializable format
        rec_data = []
        for rec in recommendations:
            rec_data.append({
                'ticker': rec.ticker,
                'action': rec.action,
                'current_shares': rec.current_shares,
                'current_value': rec.current_value,
                'recommended_shares': rec.recommended_shares,
                'recommended_value': rec.recommended_value,
                'confidence': rec.confidence,
                'reasoning': rec.reasoning,
                'risk_level': rec.risk_level,
                'user_shares': rec.user_shares,
                'user_value': rec.user_value,
                'approved': rec.approved,
                'execution_priority': rec.execution_priority
            })
        
        return jsonify({
            'success': True,
            'recommendations': rec_data,
            'total_count': len(rec_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/adjust-recommendation', methods=['POST'])
def adjust_recommendation():
    """Adjust a trade recommendation"""
    try:
        global trade_engine
        if not trade_engine:
            return jsonify({'success': False, 'error': 'Trade engine not initialized'}), 400
        
        data = request.json
        ticker = data.get('ticker')
        user_shares = data.get('user_shares')
        user_value = data.get('user_value')
        approved = data.get('approved')
        
        success = trade_engine.adjust_recommendation(
            ticker=ticker,
            user_shares=user_shares,
            user_value=user_value,
            approved=approved
        )
        
        if success:
            # Get updated portfolio impact
            impact = trade_engine.get_portfolio_impact_preview()
            return jsonify({
                'success': True,
                'impact': impact
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Recommendation not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/portfolio-impact')
def get_portfolio_impact():
    """Get portfolio impact preview"""
    try:
        global trade_engine
        if not trade_engine:
            return jsonify({'success': False, 'error': 'Trade engine not initialized'}), 400
        
        impact = trade_engine.get_portfolio_impact_preview()
        return jsonify({
            'success': True,
            'impact': impact
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/execute-trades', methods=['POST'])
async def execute_trades():
    """Execute approved trades"""
    try:
        global trade_engine
        if not trade_engine:
            return jsonify({'success': False, 'error': 'Trade engine not initialized'}), 400
        
        data = request.json
        dry_run = data.get('dry_run', True)
        
        # Execute trades
        executions = await trade_engine.execute_approved_trades(dry_run=dry_run)
        
        # Convert executions to serializable format
        exec_data = []
        for execution in executions:
            exec_data.append({
                'ticker': execution.ticker,
                'action': execution.action,
                'shares': execution.shares,
                'price': execution.price,
                'total_value': execution.total_value,
                'timestamp': execution.timestamp,
                'order_id': execution.order_id,
                'status': execution.status,
                'execution_notes': execution.execution_notes
            })
        
        # Save execution history
        trade_engine.save_execution_history()
        
        return jsonify({
            'success': True,
            'executions': exec_data,
            'total_executed': len(exec_data),
            'mode': 'live' if not dry_run else 'dry_run'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/execution-history')
def get_execution_history():
    """Get trade execution history"""
    try:
        global trade_engine
        if not trade_engine:
            return jsonify({'success': False, 'error': 'Trade engine not initialized'}), 400
        
        # Load execution history from file if available
        try:
            with open('trade_execution_history.json', 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []
        
        return jsonify({
            'success': True,
            'history': history,
            'total_trades': len(history)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-status')
def get_market_status():
    """Get current market status and trading session info"""
    try:
        from datetime import datetime, time
        import pytz
        
        # Get current time in market timezone
        market_tz = pytz.timezone('America/New_York')
        now = datetime.now(market_tz)
        
        # Market hours (9:30 AM - 4:00 PM ET)
        market_open = time(9, 30)
        market_close = time(16, 0)
        current_time = now.time()
        
        is_market_day = now.weekday() < 5  # Monday = 0, Friday = 4
        is_market_hours = market_open <= current_time <= market_close
        
        market_status = {
            'is_open': is_market_day and is_market_hours,
            'current_time': now.strftime('%H:%M:%S ET'),
            'next_open': 'Monday 9:30 AM ET' if not is_market_day else 'Tomorrow 9:30 AM ET',
            'next_close': '4:00 PM ET' if is_market_hours else 'Market Closed',
            'trading_mode': 'PAPER' if 'paper' in (trade_engine.alpaca_base_url if trade_engine else '') else 'LIVE'
        }
        
        return jsonify({
            'success': True,
            'market_status': market_status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def run_async_route(func):
    """Wrapper to run async functions in Flask routes"""
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

# Apply async wrapper to async routes
app.route('/api/portfolio')(run_async_route(get_portfolio))
app.route('/api/trade-recommendations')(run_async_route(get_trade_recommendations))
app.route('/api/execute-trades', methods=['POST'])(run_async_route(execute_trades))

if __name__ == '__main__':
    print("🚀 Starting Squeeze Alpha Web Application...")
    print("=" * 50)
    
    # Test API keys
    secrets = SecretsManager()
    alpaca_key = secrets.get_api_key('ALPACA_API_KEY')
    
    if alpaca_key:
        print("✅ Alpaca API configured")
    else:
        print("⚠️  Alpaca API not configured")
    
    print("\n🌐 Web interface available at:")
    print("   📊 Portfolio Dashboard: http://localhost:5000/")
    print("   🎯 Trade Execution: http://localhost:5000/trades")
    print("   📈 API Endpoints: http://localhost:5000/api/")
    print("\n🔥 Ready for portfolio optimization!")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)