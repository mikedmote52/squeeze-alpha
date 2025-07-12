#!/usr/bin/env python3
"""
Slack Trading Bot - Interactive portfolio updates and trade approvals
Sends scheduled market analysis and allows trade authorization via Slack
"""

import os
import asyncio
import json
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import aiohttp

@dataclass
class TradeRecommendation:
    """Trade recommendation for Slack approval"""
    id: str
    ticker: str
    action: str  # BUY/SELL/TRIM
    quantity: int
    current_price: float
    reason: str
    confidence: int
    expiry: datetime

class SlackTradingBot:
    """Interactive Slack bot for portfolio management"""
    
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.channel = os.getenv('SLACK_TRADING_CHANNEL', '#trading-alerts')
        
        # Pacific timezone for market hours
        self.pt_tz = pytz.timezone('US/Pacific')
        
        # Pending trade recommendations
        self.pending_trades = {}
    
    async def send_portfolio_update(self, session: str, portfolio_data: Dict, 
                                  market_analysis: Dict, recommendations: List[TradeRecommendation]):
        """Send comprehensive portfolio update to Slack"""
        
        # Create rich Slack message with blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"💰 {session.upper()} Portfolio Update",
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*{datetime.now(self.pt_tz).strftime('%B %d, %Y at %I:%M %p PT')}*"
                    }
                ]
            },
            {"type": "divider"}
        ]
        
        # Portfolio Summary Section
        summary = portfolio_data.get('summary', {})
        total_value = summary.get('total_value', 0)
        total_pl = summary.get('total_pl', 0)
        total_pl_percent = summary.get('total_pl_percent', 0)
        
        pl_emoji = "📈" if total_pl >= 0 else "📉"
        
        blocks.append({
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Total Value:*\n${total_value:,.2f}"
                },
                {
                    "type": "mrkdwn", 
                    "text": f"*Total P&L:*\n{pl_emoji} ${total_pl:,.2f} ({total_pl_percent:+.1f}%)"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Winners:*\n🟢 {summary.get('winners_count', 0)} positions"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Losers:*\n🔴 {summary.get('losers_count', 0)} positions"
                }
            ]
        })
        
        # Top Movers Section
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🏆 Top Movers*"
            }
        })
        
        # Best and worst performers
        positions = portfolio_data.get('positions', [])
        if positions:
            sorted_positions = sorted(positions, key=lambda x: x.get('day_change_percent', 0), reverse=True)
            
            movers_text = ""
            # Top 3 gainers
            for pos in sorted_positions[:3]:
                if pos['day_change_percent'] > 0:
                    movers_text += f"• 🟢 *{pos['ticker']}*: {pos['day_change_percent']:+.1f}% (${pos['current_price']:.2f})\n"
            
            # Top 3 losers
            for pos in sorted_positions[-3:]:
                if pos['day_change_percent'] < 0:
                    movers_text += f"• 🔴 *{pos['ticker']}*: {pos['day_change_percent']:+.1f}% (${pos['current_price']:.2f})\n"
            
            if movers_text:
                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": movers_text}
                })
        
        # Market Alerts Section
        if market_analysis.get('alerts'):
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*⚠️ Market Alerts*"
                }
            })
            
            alerts_text = ""
            for alert in market_analysis['alerts'][:5]:  # Top 5 alerts
                alerts_text += f"• {alert}\n"
            
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": alerts_text}
            })
        
        # Trade Recommendations Section
        if recommendations:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🤖 AI Trade Recommendations*"
                }
            })
            
            for rec in recommendations[:3]:  # Top 3 recommendations
                # Store recommendation for callback handling
                self.pending_trades[rec.id] = rec
                
                action_emoji = {
                    'BUY': '🟢',
                    'SELL': '🔴',
                    'TRIM': '✂️',
                    'HOLD': '⏸️'
                }.get(rec.action, '❓')
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{action_emoji} *{rec.action} {rec.ticker}*\n"
                               f"Quantity: {rec.quantity} shares @ ${rec.current_price:.2f}\n"
                               f"Reason: {rec.reason}\n"
                               f"Confidence: {rec.confidence}%"
                    },
                    "accessory": {
                        "type": "overflow",
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "✅ Approve"},
                                "value": f"approve_{rec.id}"
                            },
                            {
                                "text": {"type": "plain_text", "text": "✏️ Modify"},
                                "value": f"modify_{rec.id}"
                            },
                            {
                                "text": {"type": "plain_text", "text": "❌ Reject"},
                                "value": f"reject_{rec.id}"
                            }
                        ],
                        "action_id": f"trade_action_{rec.id}"
                    }
                })
        
        # Quick Actions Section
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📊 Full Analysis"},
                    "value": "full_analysis",
                    "action_id": "full_analysis"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🔄 Refresh"},
                    "value": "refresh",
                    "action_id": "refresh"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "⏸️ Pause Trading"},
                    "value": "pause",
                    "action_id": "pause",
                    "style": "danger"
                }
            ]
        })
        
        # Send message
        await self.send_slack_message(blocks)
    
    async def send_slack_message(self, blocks: List[Dict]):
        """Send message to Slack via webhook"""
        
        if not self.webhook_url:
            print("⚠️ No Slack webhook configured")
            return
        
        payload = {
            "channel": self.channel,
            "username": "AI Trading Bot",
            "icon_emoji": ":moneybag:",
            "blocks": blocks
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        print("✅ Slack message sent successfully")
                    else:
                        print(f"❌ Slack error: {response.status}")
        
        except Exception as e:
            print(f"❌ Failed to send Slack message: {e}")
    
    async def send_simple_alert(self, title: str, message: str, color: str = "good"):
        """Send simple alert message"""
        
        attachments = [{
            "color": color,  # good (green), warning (yellow), danger (red)
            "title": title,
            "text": message,
            "footer": "AI Trading System",
            "ts": int(datetime.now().timestamp())
        }]
        
        payload = {
            "channel": self.channel,
            "username": "AI Trading Bot",
            "icon_emoji": ":chart_with_upwards_trend:",
            "attachments": attachments
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status != 200:
                        print(f"❌ Slack alert failed: {response.status}")
        
        except Exception as e:
            print(f"❌ Failed to send alert: {e}")
    
    async def handle_trade_action(self, action_id: str, value: str, user_id: str):
        """Handle interactive button responses"""
        
        action_type, trade_id = value.split('_', 1)
        trade = self.pending_trades.get(trade_id)
        
        if not trade:
            return {"text": "❌ Trade recommendation expired"}
        
        if action_type == "approve":
            # Execute the trade
            result = await self.execute_trade(trade)
            await self.send_simple_alert(
                f"✅ Trade Approved by {user_id}",
                f"Executing: {trade.action} {trade.quantity} shares of {trade.ticker} at ${trade.current_price:.2f}",
                "good"
            )
            return {"text": f"✅ Trade approved and executed: {result}"}
        
        elif action_type == "modify":
            # Send modification dialog
            return {
                "text": "✏️ Trade modification",
                "response_type": "ephemeral",
                "blocks": [{
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Reply with new quantity (e.g., '50' for 50 shares)"}
                }]
            }
        
        elif action_type == "reject":
            # Cancel the trade
            del self.pending_trades[trade_id]
            await self.send_simple_alert(
                f"❌ Trade Rejected by {user_id}",
                f"Cancelled: {trade.action} {trade.ticker}",
                "danger"
            )
            return {"text": "❌ Trade rejected"}
    
    async def execute_trade(self, trade: TradeRecommendation) -> str:
        """Execute approved trade via Alpaca"""
        try:
            from live_portfolio_engine import LivePortfolioEngine
            import alpaca_trade_api as tradeapi
            import os
            
            # Get Alpaca credentials
            alpaca_key = os.getenv('ALPACA_API_KEY')
            alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
            
            if not alpaca_key or not alpaca_secret:
                return f"❌ BLOCKED: No Alpaca credentials - {trade.action} {trade.quantity} {trade.ticker} @ ${trade.current_price:.2f}"
            
            # Initialize Alpaca API
            alpaca = tradeapi.REST(
                alpaca_key,
                alpaca_secret,
                'https://paper-api.alpaca.markets',  # Paper trading for safety
                api_version='v2'
            )
            
            # Execute trade
            if trade.action == 'BUY':
                order = alpaca.submit_order(
                    symbol=trade.ticker,
                    qty=trade.quantity,
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
            elif trade.action == 'SELL':
                order = alpaca.submit_order(
                    symbol=trade.ticker,
                    qty=trade.quantity,
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
            else:
                return f"❌ INVALID ACTION: {trade.action}"
            
            return f"✅ EXECUTED: {trade.action} {trade.quantity} {trade.ticker} @ ${trade.current_price:.2f} (Order ID: {order.id})"
            
        except Exception as e:
            return f"❌ EXECUTION FAILED: {trade.action} {trade.quantity} {trade.ticker} - {str(e)}"
    
    def schedule_session_updates(self):
        """Schedule updates for each market session"""
        
        schedule_times = {
            'premarket': '08:45',    # 8:45 AM ET
            'open': '09:45',         # 9:45 AM ET (15 min after open)
            'midday': '12:30',       # 12:30 PM ET
            'close': '15:45',        # 3:45 PM ET (15 min before close)
            'aftermarket': '16:30'   # 4:30 PM ET
        }
        
        return schedule_times


# Example scheduled update function
async def send_scheduled_update(session: str):
    """Send scheduled portfolio update for market session"""
    
    from live_portfolio_engine import LivePortfolioEngine
    from polygon_market_engine import PolygonMarketEngine
    
    # Initialize engines
    portfolio_engine = LivePortfolioEngine()
    polygon_engine = PolygonMarketEngine()
    slack_bot = SlackTradingBot()
    
    # Get portfolio data
    positions = await portfolio_engine.get_live_portfolio()
    summary = portfolio_engine.generate_portfolio_summary(positions)
    
    # Get market analysis
    tickers = [pos.ticker for pos in positions]
    market_analysis = await polygon_engine.analyze_portfolio_session(tickers)
    
    # Generate trade recommendations
    recommendations = []
    for pos in positions:
        if pos.ai_recommendation == 'SELL' and pos.ai_confidence > 80:
            rec = TradeRecommendation(
                id=f"{pos.ticker}_{datetime.now().timestamp()}",
                ticker=pos.ticker,
                action='SELL',
                quantity=int(pos.shares),
                current_price=pos.current_price,
                reason=f"AI confidence: {pos.ai_confidence}%, P&L: {pos.unrealized_pl_percent:+.1f}%",
                confidence=pos.ai_confidence,
                expiry=datetime.now() + timedelta(hours=1)
            )
            recommendations.append(rec)
    
    # Prepare portfolio data
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
            for pos in positions
        ]
    }
    
    # Send update to Slack
    await slack_bot.send_portfolio_update(session, portfolio_data, market_analysis, recommendations)