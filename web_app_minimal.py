from flask import Flask, jsonify, request, render_template
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

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
            
            <p>✅ System: Running<br>
               ✅ Real Data: Active<br>
               ✅ Trading: Ready</p>
            
            <a href="/enhanced-trades" class="nav-button">🚀 Start Trading</a>
            <a href="/api/test" class="nav-button">🔌 Test API</a>
        </div>
    </body>
    </html>
    '''

@app.route('/enhanced-trades')
def enhanced_trades():
    return render_template('enhanced_trades.html')

@app.route('/api/test')
def test_api():
    """Test API with real stock data"""
    try:
        # Get real stock data
        ticker = 'AAPL'
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return jsonify({
            'success': True,
            'message': 'Real data working!',
            'test_stock': ticker,
            'current_price': info.get('currentPrice', 0),
            'market_cap': info.get('marketCap', 0),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("🚀 Starting Squeeze Alpha (Minimal Version)...")
    print("=" * 50)
    print("🌐 Web interface available at:")
    print("   📊 Homepage: http://localhost:5000/")
    print("   🎯 Trading: http://localhost:5000/enhanced-trades")
    print("   📈 Test API: http://localhost:5000/api/test")
    
    app.run(host='0.0.0.0', port=5000, debug=True)