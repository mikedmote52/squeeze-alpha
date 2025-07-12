#!/usr/bin/env python3
"""
Market Session Scheduler - Automated portfolio analysis at key market times
Integrates Polygon data, AI analysis, and Slack notifications
"""

import os
import asyncio
import schedule
import time
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketSessionScheduler:
    """Automated market session analyzer with Slack updates"""
    
    def __init__(self):
        self.pt_tz = pytz.timezone('US/Pacific')
        self.running = False
        
        # Import engines
        from live_portfolio_engine import LivePortfolioEngine
        from polygon_market_engine import PolygonMarketEngine
        from slack_trading_bot import SlackTradingBot
        from alpha_engine_enhanced import EnhancedAlphaEngine
        from openrouter_stock_debate import OpenRouterStockDebate
        
        self.portfolio_engine = LivePortfolioEngine()
        self.polygon_engine = PolygonMarketEngine()
        self.slack_bot = SlackTradingBot()
        self.alpha_engine = EnhancedAlphaEngine()
        self.debate_engine = OpenRouterStockDebate()
    
    async def analyze_session(self, session_name: str):
        """Comprehensive session analysis with all data sources"""
        
        logger.info(f"🕐 Starting {session_name} analysis...")
        
        try:
            # 1. Get live portfolio data
            positions = await self.portfolio_engine.get_live_portfolio()
            summary = self.portfolio_engine.generate_portfolio_summary(positions)
            
            # 2. Get Polygon market data
            tickers = [pos.ticker for pos in positions]
            polygon_analysis = await self.polygon_engine.analyze_portfolio_session(tickers)
            
            # 3. Session-specific analysis
            session_insights = await self.generate_session_insights(
                session_name, positions, polygon_analysis
            )
            
            # 4. Generate AI recommendations
            recommendations = await self.generate_ai_recommendations(
                session_name, positions, polygon_analysis, session_insights
            )
            
            # 5. Send Slack update
            await self.send_session_update(
                session_name, positions, summary, polygon_analysis, 
                session_insights, recommendations
            )
            
            logger.info(f"✅ {session_name} analysis complete")
            
        except Exception as e:
            logger.error(f"❌ Session analysis error: {e}")
            await self.slack_bot.send_simple_alert(
                f"⚠️ {session_name} Analysis Error",
                f"Failed to complete analysis: {str(e)}",
                "danger"
            )
    
    async def generate_session_insights(self, session: str, positions: List, 
                                      polygon_data: Dict) -> Dict[str, Any]:
        """Generate session-specific insights"""
        
        insights = {
            'session': session,
            'key_events': [],
            'risk_alerts': [],
            'opportunities': []
        }
        
        if session == 'premarket':
            # Pre-market: Focus on overnight moves and news
            for pos in positions:
                ticker_data = polygon_data['tickers'].get(pos.ticker, {})
                news = ticker_data.get('news', [])
                
                # Check for significant news
                if news:
                    negative_news = [n for n in news if n.sentiment == 'NEGATIVE']
                    if negative_news:
                        insights['risk_alerts'].append({
                            'ticker': pos.ticker,
                            'alert': f"Negative news: {negative_news[0].title}",
                            'action': 'MONITOR'
                        })
                
                # Check for pre-market gaps
                snapshot = ticker_data.get('snapshot')
                if snapshot and abs(snapshot.price - pos.current_price) / pos.current_price > 0.05:
                    insights['key_events'].append({
                        'ticker': pos.ticker,
                        'event': f"Pre-market gap: {((snapshot.price - pos.current_price) / pos.current_price * 100):.1f}%"
                    })
        
        elif session == 'open':
            # Opening bell: Volume and volatility analysis
            for pos in positions:
                ticker_data = polygon_data['tickers'].get(pos.ticker, {})
                snapshot = ticker_data.get('snapshot')
                
                if snapshot and snapshot.volume > 1_000_000:
                    insights['key_events'].append({
                        'ticker': pos.ticker,
                        'event': f"High opening volume: {snapshot.volume:,}"
                    })
                    
                    # Check for opening volatility
                    if snapshot.spread_percent > 1.0:
                        insights['risk_alerts'].append({
                            'ticker': pos.ticker,
                            'alert': f"Wide spread: {snapshot.spread_percent:.2f}%",
                            'action': 'WAIT_FOR_LIQUIDITY'
                        })
        
        elif session == 'midday':
            # Midday: Trend assessment
            for pos in positions:
                if pos.day_change_percent > 5:
                    insights['opportunities'].append({
                        'ticker': pos.ticker,
                        'opportunity': 'Consider profit-taking on strong gain',
                        'confidence': 75
                    })
                elif pos.day_change_percent < -5:
                    insights['risk_alerts'].append({
                        'ticker': pos.ticker,
                        'alert': 'Significant intraday decline',
                        'action': 'ASSESS_STOP_LOSS'
                    })
        
        elif session == 'close':
            # Closing hour: Position management
            for pos in positions:
                ticker_data = polygon_data['tickers'].get(pos.ticker, {})
                options = ticker_data.get('options_flow', [])
                
                if options:
                    total_premium = sum(opt.premium for opt in options)
                    if total_premium > 500_000:
                        insights['key_events'].append({
                            'ticker': pos.ticker,
                            'event': f"Large options flow: ${total_premium:,.0f}"
                        })
                
                # EOD position recommendations
                if pos.unrealized_pl_percent > 20:
                    insights['opportunities'].append({
                        'ticker': pos.ticker,
                        'opportunity': 'Strong performer - consider trimming',
                        'confidence': 80
                    })
        
        elif session == 'aftermarket':
            # After-hours: Next day preparation
            insights['key_events'].append({
                'event': 'Market closed - reviewing after-hours activity'
            })
            
            # Check for earnings or events tomorrow
            for pos in positions:
                # This would check earnings calendar
                pass
        
        return insights
    
    async def generate_ai_recommendations(self, session: str, positions: List,
                                        polygon_data: Dict, insights: Dict) -> List[Dict]:
        """Generate AI-powered trade recommendations"""
        
        from slack_trading_bot import TradeRecommendation
        recommendations = []
        
        for pos in positions:
            # Skip if position too small
            if pos.market_value < 1000:
                continue
            
            # Get ticker-specific data
            ticker_insights = [
                item for item in insights.get('risk_alerts', []) 
                if item.get('ticker') == pos.ticker
            ]
            
            # Session-specific recommendation logic
            if session == 'premarket' and ticker_insights:
                # Conservative pre-market
                if any('Negative news' in alert.get('alert', '') for alert in ticker_insights):
                    rec = TradeRecommendation(
                        id=f"{pos.ticker}_{session}_{datetime.now().timestamp()}",
                        ticker=pos.ticker,
                        action='TRIM',
                        quantity=int(pos.shares * 0.25),  # Trim 25%
                        current_price=pos.current_price,
                        reason="Negative pre-market news - risk reduction",
                        confidence=70,
                        expiry=datetime.now() + timedelta(hours=1)
                    )
                    recommendations.append(rec)
            
            elif session == 'open':
                # Opening volatility trades
                if pos.day_change_percent > 10 and pos.unrealized_pl_percent > 50:
                    rec = TradeRecommendation(
                        id=f"{pos.ticker}_{session}_{datetime.now().timestamp()}",
                        ticker=pos.ticker,
                        action='SELL',
                        quantity=int(pos.shares * 0.5),  # Sell half
                        current_price=pos.current_price,
                        reason="Extreme gain on opening - lock in profits",
                        confidence=85,
                        expiry=datetime.now() + timedelta(minutes=30)
                    )
                    recommendations.append(rec)
            
            elif session == 'close':
                # End of day position management
                if pos.ai_recommendation == 'SELL' and pos.ai_confidence > 80:
                    rec = TradeRecommendation(
                        id=f"{pos.ticker}_{session}_{datetime.now().timestamp()}",
                        ticker=pos.ticker,
                        action='SELL',
                        quantity=int(pos.shares),
                        current_price=pos.current_price,
                        reason=f"AI sell signal ({pos.ai_confidence}%) - EOD exit",
                        confidence=pos.ai_confidence,
                        expiry=datetime.now() + timedelta(minutes=15)
                    )
                    recommendations.append(rec)
                
                # Also check for new opportunities
                if session == 'close' and len(recommendations) == 0:
                    # Run alpha discovery for tomorrow
                    new_opportunities = await self.alpha_engine.discover_alpha_opportunities('swing')
                    for opp in new_opportunities[:1]:  # Top opportunity
                        if opp.confidence_score > 0.8:
                            rec = TradeRecommendation(
                                id=f"{opp.ticker}_new_{datetime.now().timestamp()}",
                                ticker=opp.ticker,
                                action='BUY',
                                quantity=100,  # Starter position
                                current_price=opp.current_price,
                                reason=f"New alpha opportunity: {opp.discovery_reason}",
                                confidence=int(opp.confidence_score * 100),
                                expiry=datetime.now() + timedelta(hours=16)  # Next day
                            )
                            recommendations.append(rec)
        
        return recommendations
    
    async def send_session_update(self, session: str, positions: List, summary: Dict,
                                polygon_data: Dict, insights: Dict, recommendations: List):
        """Send comprehensive update to Slack"""
        
        # Prepare portfolio data
        portfolio_data = {
            'summary': summary,
            'positions': [
                {
                    'ticker': pos.ticker,
                    'current_price': pos.current_price,
                    'day_change_percent': pos.day_change_percent,
                    'unrealized_pl_percent': pos.unrealized_pl_percent,
                    'market_value': pos.market_value,
                    'ai_recommendation': pos.ai_recommendation,
                    'ai_confidence': pos.ai_confidence
                }
                for pos in positions
            ]
        }
        
        # Prepare market analysis with insights
        market_analysis = {
            'session': session,
            'alerts': [],
            'insights': insights
        }
        
        # Add alerts from insights
        for alert in insights.get('risk_alerts', []):
            market_analysis['alerts'].append(
                f"⚠️ {alert['ticker']}: {alert['alert']} - {alert['action']}"
            )
        
        for event in insights.get('key_events', []):
            if 'ticker' in event:
                market_analysis['alerts'].append(
                    f"📌 {event['ticker']}: {event['event']}"
                )
            else:
                market_analysis['alerts'].append(f"📌 {event['event']}")
        
        # Send to Slack
        await self.slack_bot.send_portfolio_update(
            session, portfolio_data, market_analysis, recommendations
        )
    
    def schedule_sessions(self):
        """Schedule analysis for each market session"""
        
        # Define session times (PT)
        sessions = {
            'premarket': '05:45',
            'open': '06:45',
            'midday': '09:30',
            'close': '12:45',
            'aftermarket': '13:30'
        }
        
        # Schedule each session
        for session_name, time_str in sessions.items():
            schedule.every().monday.at(time_str).do(
                lambda s=session_name: asyncio.create_task(self.analyze_session(s))
            )
            schedule.every().tuesday.at(time_str).do(
                lambda s=session_name: asyncio.create_task(self.analyze_session(s))
            )
            schedule.every().wednesday.at(time_str).do(
                lambda s=session_name: asyncio.create_task(self.analyze_session(s))
            )
            schedule.every().thursday.at(time_str).do(
                lambda s=session_name: asyncio.create_task(self.analyze_session(s))
            )
            schedule.every().friday.at(time_str).do(
                lambda s=session_name: asyncio.create_task(self.analyze_session(s))
            )
        
        logger.info("📅 Scheduled market session updates:")
        for session, time_str in sessions.items():
            logger.info(f"  - {session}: {time_str} PT")
    
    async def run(self):
        """Run the scheduler"""
        
        self.running = True
        self.schedule_sessions()
        
        # Send startup notification
        await self.slack_bot.send_simple_alert(
            "🚀 Market Session Scheduler Started",
            "Automated analysis scheduled for: premarket, open, midday, close, aftermarket",
            "good"
        )
        
        # Run scheduler
        while self.running:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False


# Example usage
async def main():
    scheduler = MarketSessionScheduler()
    
    # Test immediate session analysis
    current_session = scheduler.polygon_engine.get_current_session()
    await scheduler.analyze_session(current_session)
    
    # Start scheduler (for production)
    # await scheduler.run()


if __name__ == "__main__":
    asyncio.run(main())