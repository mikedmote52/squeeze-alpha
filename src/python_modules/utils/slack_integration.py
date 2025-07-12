"""
Slack Integration for AI Trading System
Based on slack_integration.json
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import requests
from slack_sdk import WebClient
from slack_sdk.web import SlackResponse
from slack_sdk.errors import SlackApiError

from .config import get_config

@dataclass
class SlackMessage:
    """Data class for Slack message formatting"""
    text: str
    channel: str = "#trading-alerts"
    blocks: Optional[List[Dict[str, Any]]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    thread_ts: Optional[str] = None

@dataclass
class TradingRecommendation:
    """Data class for trading recommendations"""
    ticker: str
    action: str
    position_size: str
    entry_price: str
    take_profit_1: str
    take_profit_2: str
    stop_loss: str
    rationale: str
    risk_level: str
    confidence_score: float

class SlackBot:
    """Slack integration for trading notifications and commands"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Slack client
        self.client = None
        self.webhook_url = self.config.api_credentials.slack_webhook_url
        
        if self.config.api_credentials.slack_oauth_token:
            self.client = WebClient(token=self.config.api_credentials.slack_oauth_token)
        
        # Command handlers
        self.command_handlers = {
            '/portfolio': self._handle_portfolio_command,
            '/buy': self._handle_buy_command,
            '/sell': self._handle_sell_command,
            '/hold': self._handle_hold_command,
            '/analyze': self._handle_analyze_command,
            '/status': self._handle_status_command,
            '/help': self._handle_help_command
        }
    
    def _create_recommendation_blocks(self, recommendations: List[TradingRecommendation]) -> List[Dict[str, Any]]:
        """Create Slack blocks for trading recommendations"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 AI Trading Recommendations"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{len(recommendations)} recommendations generated*"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        for rec in recommendations:
            # Risk level emoji
            risk_emoji = {
                "Low": "🟢",
                "Medium": "🟡",
                "High": "🔴"
            }.get(rec.risk_level, "⚪")
            
            # Action emoji
            action_emoji = {
                "BUY": "📈",
                "SELL": "📉",
                "HOLD": "⏸️"
            }.get(rec.action, "❓")
            
            # Confidence bar
            confidence_bar = "█" * int(rec.confidence_score * 10) + "░" * (10 - int(rec.confidence_score * 10))
            
            blocks.extend([
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{action_emoji} *{rec.ticker}* - {rec.action} {rec.position_size}\n"
                                f"{risk_emoji} Risk: {rec.risk_level} | Confidence: {confidence_bar} {rec.confidence_score:.1%}\n"
                                f"💰 Entry: {rec.entry_price} | 🎯 TP1: {rec.take_profit_1} | 🎯 TP2: {rec.take_profit_2} | 🛑 SL: {rec.stop_loss}\n"
                                f"📝 *Rationale:* {rec.rationale}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "✅ Approve"
                            },
                            "style": "primary",
                            "value": f"approve_{rec.ticker}",
                            "action_id": f"approve_{rec.ticker}"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "❌ Reject"
                            },
                            "style": "danger",
                            "value": f"reject_{rec.ticker}",
                            "action_id": f"reject_{rec.ticker}"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📊 Analyze"
                            },
                            "value": f"analyze_{rec.ticker}",
                            "action_id": f"analyze_{rec.ticker}"
                        }
                    ]
                },
                {
                    "type": "divider"
                }
            ])
        
        return blocks
    
    def send_webhook_message(self, message: SlackMessage) -> bool:
        """Send message via webhook"""
        try:
            if not self.webhook_url:
                self.logger.warning("Slack webhook URL not configured")
                return False
            
            payload = {
                "text": message.text,
                "channel": message.channel
            }
            
            if message.blocks:
                payload["blocks"] = message.blocks
            
            if message.attachments:
                payload["attachments"] = message.attachments
            
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            self.logger.info(f"Sent Slack webhook message: {message.text[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending Slack webhook message: {e}")
            return False
    
    def send_message(self, message: SlackMessage) -> bool:
        """Send message via Slack API"""
        try:
            if not self.client:
                return self.send_webhook_message(message)
            
            response = self.client.chat_postMessage(
                channel=message.channel,
                text=message.text,
                blocks=message.blocks,
                attachments=message.attachments,
                thread_ts=message.thread_ts
            )
            
            self.logger.info(f"Sent Slack message: {message.text[:50]}...")
            return True
            
        except SlackApiError as e:
            self.logger.error(f"Slack API error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending Slack message: {e}")
            return False
    
    def send_trading_recommendations(self, recommendations: List[TradingRecommendation]) -> bool:
        """Send trading recommendations to Slack"""
        try:
            blocks = self._create_recommendation_blocks(recommendations)
            
            message = SlackMessage(
                text="New AI Trading Recommendations",
                blocks=blocks,
                channel="#trading-alerts"
            )
            
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending trading recommendations: {e}")
            return False
    
    def send_trade_execution_alert(self, trade_results: Dict[str, Any]) -> bool:
        """Send trade execution results"""
        try:
            executed_trades = trade_results.get('executed_trades', [])
            failed_trades = trade_results.get('failed_trades', [])
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🔄 Trade Execution Results"
                    }
                }
            ]
            
            # Executed trades
            if executed_trades:
                blocks.extend([
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*✅ {len(executed_trades)} trades executed successfully:*"
                        }
                    }
                ])
                
                for trade in executed_trades:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"• {trade['ticker']} {trade['action']} {trade['quantity']} shares @ ${trade['fill_price']:.2f}"
                        }
                    })
            
            # Failed trades
            if failed_trades:
                blocks.extend([
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*❌ {len(failed_trades)} trades failed:*"
                        }
                    }
                ])
                
                for trade in failed_trades:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"• {trade['ticker']}: {trade['error']}"
                        }
                    })
            
            message = SlackMessage(
                text="Trade Execution Results",
                blocks=blocks,
                channel="#trading-alerts"
            )
            
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending trade execution alert: {e}")
            return False
    
    def send_daily_summary(self, summary: Dict[str, Any]) -> bool:
        """Send daily trading summary"""
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Daily Trading Summary"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Portfolio Value:*\n${summary.get('portfolio_value', 0):,.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Daily P&L:*\n${summary.get('daily_pnl', 0):,.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Positions:*\n{summary.get('position_count', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Trades Executed:*\n{summary.get('trades_executed', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*AI Consensus:*\n{summary.get('ai_consensus_score', 0):.1%}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Top Pick:*\n{summary.get('top_recommendation', 'None')}"
                        }
                    ]
                }
            ]
            
            message = SlackMessage(
                text="Daily Trading Summary",
                blocks=blocks,
                channel="#trading-summary"
            )
            
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending daily summary: {e}")
            return False
    
    def send_high_risk_alert(self, recommendations: List[TradingRecommendation]) -> bool:
        """Send high-risk trade alert requiring approval"""
        try:
            high_risk_recs = [r for r in recommendations if r.risk_level == "High"]
            
            if not high_risk_recs:
                return True
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 High-Risk Trades Detected"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{len(high_risk_recs)} high-risk trades require approval:*"
                    }
                }
            ]
            
            for rec in high_risk_recs:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• {rec.ticker}: {rec.action} {rec.position_size} - {rec.rationale}"
                    }
                })
            
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Approve All"
                        },
                        "style": "primary",
                        "value": "approve_all",
                        "action_id": "approve_all"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Review Individual"
                        },
                        "value": "review_individual",
                        "action_id": "review_individual"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reject All"
                        },
                        "style": "danger",
                        "value": "reject_all",
                        "action_id": "reject_all"
                    }
                ]
            })
            
            message = SlackMessage(
                text="High-Risk Trades Requiring Approval",
                blocks=blocks,
                channel="#trading-alerts"
            )
            
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending high-risk alert: {e}")
            return False
    
    # Command handlers
    async def _handle_portfolio_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /portfolio command"""
        # This would integrate with portfolio management system
        return {
            "response_type": "ephemeral",
            "text": "Portfolio command received - implementing with portfolio manager"
        }
    
    async def _handle_buy_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /buy command"""
        # This would integrate with trade execution system
        return {
            "response_type": "ephemeral",
            "text": "Buy command received - implementing with trade executor"
        }
    
    async def _handle_sell_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /sell command"""
        # This would integrate with trade execution system
        return {
            "response_type": "ephemeral",
            "text": "Sell command received - implementing with trade executor"
        }
    
    async def _handle_hold_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /hold command"""
        return {
            "response_type": "ephemeral",
            "text": "Hold command received - position marked as hold"
        }
    
    async def _handle_analyze_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /analyze command"""
        # This would integrate with analysis system
        return {
            "response_type": "ephemeral",
            "text": "Analysis command received - implementing with AI analyzer"
        }
    
    async def _handle_status_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /status command"""
        return {
            "response_type": "ephemeral",
            "text": "System status: Online - AI trading system operational"
        }
    
    async def _handle_help_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /help command"""
        help_text = """
*Available Commands:*
• `/portfolio` - Get current portfolio summary
• `/buy [ticker] [quantity]` - Execute buy order
• `/sell [ticker] [quantity]` - Execute sell order
• `/hold [ticker]` - Mark position as hold
• `/analyze [ticker]` - Analyze stock ticker
• `/status` - System status check
• `/help` - Show this help message
        """
        
        return {
            "response_type": "ephemeral",
            "text": help_text
        }
    
    def handle_slash_command(self, command: str, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming slash commands"""
        try:
            handler = self.command_handlers.get(command)
            if handler:
                # Run async handler
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(handler(command_data))
                loop.close()
                return result
            else:
                return {
                    "response_type": "ephemeral",
                    "text": f"Unknown command: {command}. Type `/help` for available commands."
                }
                
        except Exception as e:
            self.logger.error(f"Error handling slash command {command}: {e}")
            return {
                "response_type": "ephemeral",
                "text": "Error processing command. Please try again."
            }
    
    def handle_interactive_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle interactive button actions"""
        try:
            action_id = action_data.get('action_id', '')
            
            if action_id.startswith('approve_'):
                ticker = action_id.replace('approve_', '')
                # Implement approval logic
                return {
                    "response_type": "ephemeral",
                    "text": f"Approved trade for {ticker}"
                }
            
            elif action_id.startswith('reject_'):
                ticker = action_id.replace('reject_', '')
                # Implement rejection logic
                return {
                    "response_type": "ephemeral",
                    "text": f"Rejected trade for {ticker}"
                }
            
            elif action_id.startswith('analyze_'):
                ticker = action_id.replace('analyze_', '')
                # Implement analysis logic
                return {
                    "response_type": "ephemeral",
                    "text": f"Analysis for {ticker} - implementing with AI analyzer"
                }
            
            else:
                return {
                    "response_type": "ephemeral",
                    "text": "Unknown action"
                }
                
        except Exception as e:
            self.logger.error(f"Error handling interactive action: {e}")
            return {
                "response_type": "ephemeral",
                "text": "Error processing action. Please try again."
            }

# Global Slack bot instance
_slack_bot = None

def get_slack_bot() -> SlackBot:
    """Get global Slack bot instance"""
    global _slack_bot
    if _slack_bot is None:
        _slack_bot = SlackBot()
    return _slack_bot