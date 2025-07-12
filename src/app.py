"""
FastAPI Application for AI Trading System
HTTP endpoints for all trading workflows
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime

# Import all modules
from python_modules.intelligence.stock_screener import StockScreener
from python_modules.intelligence.social_sentiment import SocialSentimentAnalyzer
from python_modules.intelligence.ai_models import get_ai_manager
from python_modules.intelligence.market_data import get_market_data_provider

from python_modules.consensus.multi_agent_analyzer import get_multi_agent_analyzer
from python_modules.consensus.consensus_builder import ConsensusBuilder
from python_modules.consensus.recommendation_engine import RecommendationEngine

from python_modules.execution import get_position_manager, get_trade_executor, get_human_override_system

from python_modules.monitoring import get_portfolio_monitor, get_performance_analytics, get_risk_monitor, get_analytics_dashboard

from python_modules.utils.slack_integration import get_slack_bot
from python_modules.utils.logging_system import get_logger
from python_modules.utils.scheduler import get_scheduler

# Pydantic models for request/response
class StockScreeningRequest(BaseModel):
    criteria: Optional[Dict[str, Any]] = None
    max_candidates: Optional[int] = 50

class SentimentAnalysisRequest(BaseModel):
    tickers: List[str]
    max_posts_per_source: Optional[int] = 100
    sentiment_weight: Optional[str] = "equal"

class AIAnalysisRequest(BaseModel):
    current_positions: Dict[str, Any]
    social_sentiment: Dict[str, Any]
    creative_screening: Dict[str, Any]
    market_data: Dict[str, Any]

class TradeExecutionRequest(BaseModel):
    recommendations: List[Dict[str, Any]]

class OverrideRequest(BaseModel):
    request_id: str
    action: str  # 'approve' or 'reject'

# Initialize FastAPI app
app = FastAPI(
    title="AI Trading System API",
    description="Production-ready AI trading system with multi-agent consensus",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
logger = logging.getLogger(__name__)

# Stock Screening Endpoints
@app.post("/webhook/stock-screener", tags=["Intelligence"])
async def stock_screener_webhook(request: StockScreeningRequest):
    """Stock screening webhook for N8N"""
    try:
        screener = StockScreener(request.criteria)
        candidates = screener.screen_stocks()
        
        return {
            "success": True,
            "candidates": len(candidates),
            "top_picks": [
                {
                    "ticker": c.ticker,
                    "score": c.total_score,
                    "rationale": c.rationale
                } for c in candidates[:10]
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/screening/candidates", tags=["Intelligence"])
async def get_screening_candidates():
    """Get latest stock screening candidates"""
    try:
        screener = StockScreener()
        candidates = screener.get_top_candidates(20)
        
        return {
            "candidates": [
                {
                    "ticker": c.ticker,
                    "company_name": c.company_name,
                    "total_score": c.total_score,
                    "price": c.price,
                    "rationale": c.rationale
                } for c in candidates
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Social Sentiment Endpoints
@app.post("/webhook/social-sentiment", tags=["Intelligence"])
async def social_sentiment_webhook(request: SentimentAnalysisRequest):
    """Social sentiment analysis webhook"""
    try:
        analyzer = SocialSentimentAnalyzer()
        results = await analyzer.analyze_social_sentiment(
            request.tickers,
            request.max_posts_per_source,
            request.sentiment_weight
        )
        
        return {
            "success": True,
            "validation_results": results.get("validation_results", {}),
            "summary": results.get("validation_summary", {}),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI Consensus Endpoints
@app.post("/webhook/ai-consensus", tags=["Consensus"])
async def ai_consensus_webhook(request: AIAnalysisRequest):
    """Multi-agent AI consensus webhook"""
    try:
        analyzer = get_multi_agent_analyzer()
        consensus_result = await analyzer.run_multi_agent_analysis(
            request.current_positions,
            request.social_sentiment,
            request.creative_screening,
            request.market_data
        )
        
        return {
            "success": True,
            "consensus_score": consensus_result.consensus_score,
            "agreement_level": consensus_result.agreement_level,
            "final_consensus": consensus_result.final_consensus,
            "total_tokens": consensus_result.total_tokens,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trade Execution Endpoints
@app.post("/webhook/execute-trades", tags=["Execution"])
async def execute_trades_webhook(request: TradeExecutionRequest):
    """Trade execution webhook"""
    try:
        executor = get_trade_executor()
        results = await executor.execute_recommendations(request.recommendations)
        
        return {
            "success": True,
            "executed_trades": results["successful_trades"],
            "failed_trades": results["failed_trades"],
            "total_exposure": results["total_exposure"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/positions", tags=["Execution"])
async def get_current_positions():
    """Get current portfolio positions"""
    try:
        position_manager = get_position_manager()
        positions = await position_manager.get_current_positions()
        
        return {
            "positions": [
                {
                    "symbol": p.symbol,
                    "quantity": p.quantity,
                    "market_value": p.market_value,
                    "unrealized_pl": p.unrealized_pl,
                    "unrealized_pl_percent": p.unrealized_pl_percent
                } for p in positions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/summary", tags=["Execution"])
async def get_portfolio_summary():
    """Get portfolio summary"""
    try:
        position_manager = get_position_manager()
        summary = await position_manager.get_portfolio_summary()
        
        if not summary:
            raise HTTPException(status_code=404, detail="Portfolio summary not available")
        
        return {
            "total_equity": summary.total_equity,
            "buying_power": summary.buying_power,
            "day_pl": summary.day_pl,
            "day_pl_percent": summary.day_pl_percent,
            "position_count": summary.position_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Human Override Endpoints
@app.post("/api/override/action", tags=["Override"])
async def handle_override_action(request: OverrideRequest):
    """Handle human override action"""
    try:
        override_system = get_human_override_system()
        if not override_system:
            raise HTTPException(status_code=503, detail="Human override system not available")
        
        if request.action == "approve":
            success = override_system.approve_request(request.request_id)
        elif request.action == "reject":
            success = override_system.reject_request(request.request_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        return {"success": success, "request_id": request.request_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Monitoring Endpoints
@app.get("/api/dashboard", tags=["Monitoring"])
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        dashboard = get_analytics_dashboard()
        if not dashboard:
            raise HTTPException(status_code=503, detail="Analytics dashboard not available")
        data = await dashboard.get_dashboard_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/portfolio", tags=["Monitoring"])
async def get_portfolio_monitoring():
    """Get portfolio monitoring status"""
    try:
        monitor = get_portfolio_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Portfolio monitor not available")
        summary = await monitor.get_monitoring_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/performance", tags=["Monitoring"])
async def get_performance_analytics():
    """Get performance analytics"""
    try:
        analytics = get_performance_analytics()
        if not analytics:
            raise HTTPException(status_code=503, detail="Performance analytics not available")
        metrics = await analytics.calculate_performance_metrics()
        
        return {
            "total_return": metrics.total_return,
            "sharpe_ratio": metrics.sharpe_ratio,
            "max_drawdown": metrics.max_drawdown,
            "win_rate": metrics.win_rate,
            "volatility": metrics.volatility
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk/status", tags=["Monitoring"])
async def get_risk_status():
    """Get risk monitoring status"""
    try:
        risk_monitor = get_risk_monitor()
        if not risk_monitor:
            raise HTTPException(status_code=503, detail="Risk monitor not available")
        summary = await risk_monitor.get_risk_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Slack Integration Endpoints
@app.post("/api/slack/command", tags=["Integration"])
async def handle_slack_command(command: str, data: Dict[str, Any]):
    """Handle Slack slash commands"""
    try:
        slack_bot = get_slack_bot()
        response = slack_bot.handle_slash_command(command, data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/slack/interaction", tags=["Integration"])
async def handle_slack_interaction(data: Dict[str, Any]):
    """Handle Slack interactive actions"""
    try:
        slack_bot = get_slack_bot()
        response = slack_bot.handle_interactive_action(data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Status Endpoints
@app.get("/health", tags=["System"])
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/system/status", tags=["System"])
async def get_system_status():
    """Get comprehensive system status"""
    try:
        return {
            "api_status": "online",
            "components": {
                "ai_models": "ready",
                "market_data": "connected",
                "trade_execution": "ready",
                "monitoring": "active",
                "slack_integration": "connected"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background task endpoints
@app.post("/api/system/start-monitoring", tags=["System"])
async def start_monitoring(background_tasks: BackgroundTasks):
    """Start portfolio monitoring"""
    try:
        monitor = get_portfolio_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Portfolio monitor not available")
        background_tasks.add_task(monitor.start_monitoring, 60)  # 60 second intervals
        return {"message": "Portfolio monitoring started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)