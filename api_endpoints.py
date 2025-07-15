#!/usr/bin/env python3
"""
API Endpoints for Frontend Integration
Add these routes to your FastAPI backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
import json
import asyncio
from datetime import datetime

# Import your existing modules
from core.dynamic_alpha_discovery import discover_dynamic_alpha_opportunities
from core.catalyst_discovery_engine import discover_real_catalyst_opportunities
from feeds.fda_scraper import get_fda_catalysts
from feeds.sec_monitor import get_sec_catalysts
from live_portfolio_integration import LivePortfolioIntegration

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourfrontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize portfolio integration
portfolio = LivePortfolioIntegration()

@app.get("/api/catalyst-discovery")
async def get_catalyst_opportunities():
    """Get real catalyst opportunities for frontend"""
    try:
        result = await discover_real_catalyst_opportunities()
        
        # Parse the text result and convert to JSON format for frontend
        catalysts = []
        if "FOUND" in result:
            # Extract catalyst data from your engine's output
            # This is a simplified parser - adjust based on your actual output format
            lines = result.split('\n')
            current_catalyst = {}
            
            for line in lines:
                if '**' in line and '.' in line:  # Catalyst header
                    if current_catalyst:
                        catalysts.append(current_catalyst)
                    current_catalyst = {
                        'id': f"catalyst-{len(catalysts)}",
                        'ticker': line.split('**')[1].split(' ')[0] if '**' in line else 'UNKNOWN',
                        'name': line.split('-')[1].strip() if '-' in line else line,
                        'date': datetime.now().isoformat(),
                        'type': 'FDA_APPROVAL',  # Default, you can enhance this
                        'aiProbability': 8,
                        'expectedUpside': 15.0,
                        'source': 'Real Discovery Engine',
                        'description': line
                    }
            
            if current_catalyst:
                catalysts.append(current_catalyst)
        
        return {
            "catalysts": catalysts,
            "lastUpdated": datetime.now().isoformat(),
            "source": "Real Catalyst Discovery Engine"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alpha-discovery")
async def get_alpha_opportunities():
    """Get alpha opportunities for frontend"""
    try:
        result = await discover_dynamic_alpha_opportunities()
        
        # Parse and format for frontend
        opportunities = []
        if "FOUND" in result:
            # Extract opportunities from your engine's output
            lines = result.split('\n')
            current_opp = {}
            
            for line in lines:
                if '**' in line and '.' in line:  # Opportunity header
                    if current_opp:
                        opportunities.append(current_opp)
                    
                    parts = line.split('**')[1].split(' - ') if '**' in line else ['UNKNOWN', 'Unknown Company']
                    ticker = parts[0] if parts else 'UNKNOWN'
                    company = parts[1] if len(parts) > 1 else 'Unknown Company'
                    
                    current_opp = {
                        'id': f"alpha-{len(opportunities)}",
                        'ticker': ticker,
                        'company_name': company,
                        'current_price': 100.0,  # Default, extract from your data
                        'target_price': 115.0,
                        'stop_loss': 90.0,
                        'catalyst_type': 'Dynamic_Discovery',
                        'discovery_reason': 'Market opportunity detected',
                        'confidence_score': 0.75,
                        'rationale': f'{ticker} shows strong potential based on dynamic market analysis'
                    }
            
            if current_opp:
                opportunities.append(current_opp)
        
        return {
            "opportunities": opportunities,
            "lastUpdated": datetime.now().isoformat(),
            "source": "Dynamic Alpha Discovery Engine"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/positions")
async def get_portfolio_positions():
    """Get real Alpaca portfolio positions"""
    try:
        portfolio_data = await portfolio.get_live_portfolio()
        
        if not portfolio_data:
            return {"positions": [], "error": "No portfolio data available"}
        
        positions = []
        if portfolio_data.holdings:
            for holding in portfolio_data.holdings:
                positions.append({
                    "symbol": holding.symbol,
                    "qty": holding.qty,
                    "market_value": holding.market_value,
                    "current_price": holding.current_price,
                    "unrealized_pl": holding.unrealized_pl,
                    "unrealized_plpc": holding.unrealized_plpc
                })
        
        return {
            "positions": positions,
            "lastUpdated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/performance")
async def get_portfolio_performance():
    """Get portfolio performance metrics"""
    try:
        portfolio_data = await portfolio.get_live_portfolio()
        
        if not portfolio_data:
            return {"error": "No portfolio data available"}
        
        return {
            "totalEquity": portfolio_data.total_equity,
            "dayPL": portfolio_data.unrealized_pl,
            "totalPL": portfolio_data.total_pl,
            "lastUpdated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks/{symbol}")
async def get_stock_data(symbol: str):
    """Get real-time stock data"""
    try:
        import yfinance as yf
        
        stock = yf.Ticker(symbol)
        hist = stock.history(period="2d")
        info = stock.info
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        daily_change = current_price - prev_close
        daily_change_percent = (daily_change / prev_close) * 100
        
        return {
            "symbol": symbol,
            "currentPrice": current_price,
            "dailyChange": daily_change,
            "dailyChangePercent": daily_change_percent,
            "volume": hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0,
            "marketCap": info.get('marketCap', 0),
            "lastUpdated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai-analysis")
async def get_ai_analysis(request_data: dict):
    """Get AI analysis via OpenRouter"""
    try:
        symbol = request_data.get('symbol')
        context = request_data.get('context', '')
        
        # Placeholder for AI analysis - integrate with your OpenRouter setup
        agents = [
            {
                "name": "Claude",
                "confidence": 0.85,
                "reasoning": f"Positive outlook for {symbol} based on technical analysis",
                "lastUpdated": datetime.now().isoformat()
            },
            {
                "name": "ChatGPT", 
                "confidence": 0.78,
                "reasoning": f"Moderate bullish sentiment for {symbol}",
                "lastUpdated": datetime.now().isoformat()
            },
            {
                "name": "Grok",
                "confidence": 0.72,
                "reasoning": f"Mixed signals for {symbol}, proceed with caution",
                "lastUpdated": datetime.now().isoformat()
            }
        ]
        
        return {
            "agents": agents,
            "symbol": symbol,
            "context": context,
            "lastUpdated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trades/execute")
async def execute_trade(order_data: dict):
    """Execute trade via Alpaca"""
    try:
        # Use your existing Alpaca integration
        # This is a placeholder - integrate with your real trading system
        
        return {
            "orderId": f"order-{datetime.now().timestamp()}",
            "status": "submitted",
            "symbol": order_data.get('symbol'),
            "qty": order_data.get('qty'),
            "side": order_data.get('side'),
            "executedAt": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fda-catalysts")
async def get_fda_catalysts_api():
    """Get FDA catalysts from real scraper"""
    try:
        catalysts = await get_fda_catalysts()
        return {
            "catalysts": catalysts,
            "source": "FDA.gov",
            "lastUpdated": datetime.now().isoformat()
        }
    except Exception as e:
        return {"catalysts": [], "error": str(e)}

@app.get("/api/sec-catalysts") 
async def get_sec_catalysts_api():
    """Get SEC catalysts from real monitor"""
    try:
        catalysts = await get_sec_catalysts()
        return {
            "catalysts": catalysts,
            "source": "SEC EDGAR",
            "lastUpdated": datetime.now().isoformat()
        }
    except Exception as e:
        return {"catalysts": [], "error": str(e)}

# WebSocket for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send periodic updates
            update = {
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(update))
            await asyncio.sleep(30)  # Send update every 30 seconds
    except:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)