#!/usr/bin/env python3
"""
Slack Notification Engine
Handles all automated Slack notifications for the trading system
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
from dataclasses import dataclass

from pacific_time_utils import get_pacific_time, get_market_status, is_notification_time
from api_cost_tracker import log_api_call

@dataclass
class NotificationEvent:
    """Represents a notification event"""
    event_type: str
    title: str
    message: str
    priority: str  # "high", "medium", "low"
    timestamp: datetime
    data: Dict = None

class SlackNotificationEngine:
    """Manages all Slack notifications for the trading system"""
    
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK')
        self.notification_history = []
        self.last_sent = {}
        
        # Notification schedule (PT times)
        self.schedule = {
            "premarket_brief": {"hour": 5, "minute": 45},
            "market_open_pulse": {"hour": 6, "minute": 45},
            "midday_pulse": {"hour": 9, "minute": 30},
            "end_of_day_wrap": {"hour": 12, "minute": 45},
            "afterhours_learning": {"hour": 13, "minute": 30}
        }
    
    def send_slack_message(self, message: str, title: str = None, priority: str = "medium") -> bool:
        """Send message to Slack webhook"""
        if not self.webhook_url:
            print("⚠️ Slack webhook not configured")
            return False
        
        try:
            # Format message for Slack
            if title:
                formatted_message = f"*{title}*\n{message}"
            else:
                formatted_message = message
            
            # Add priority indicators
            if priority == "high":
                formatted_message = f"🚨 {formatted_message}"
            elif priority == "low":
                formatted_message = f"ℹ️ {formatted_message}"
            
            payload = {
                "text": formatted_message,
                "username": "Squeeze Alpha AI",
                "icon_emoji": ":chart_with_upwards_trend:"
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Log API call for cost tracking
            log_api_call("slack", "webhook", success=response.status_code == 200)
            
            if response.status_code == 200:
                print(f"✅ Slack message sent: {title or 'Notification'}")
                return True
            else:
                print(f"❌ Slack failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Slack error: {e}")
            return False
    
    async def send_premarket_brief(self, portfolio_data: Dict, opportunities: List[Dict]) -> bool:
        """Send pre-market analysis brief"""
        try:
            now_pt = get_pacific_time()
            
            # Portfolio summary
            positions = portfolio_data.get('positions', [])
            total_value = sum(pos['market_value'] for pos in positions)
            total_pl = sum(pos['unrealized_pl'] for pos in positions)
            total_pl_pct = (total_pl / (total_value - total_pl)) * 100 if (total_value - total_pl) != 0 else 0
            
            # Top movers (positions with significant overnight changes)
            significant_movers = []
            for pos in positions:
                if abs(pos['unrealized_plpc']) > 3:  # >3% change
                    direction = "📈" if pos['unrealized_plpc'] > 0 else "📉"
                    significant_movers.append(
                        f"{direction} {pos['symbol']}: {pos['unrealized_plpc']:+.1f}% (${pos['current_price']:.2f})"
                    )
            
            # Top opportunities
            top_opportunities = []
            for opp in opportunities[:3]:
                symbol = opp.get('symbol', 'N/A')
                upside = opp.get('expected_upside', 0)
                confidence = opp.get('confidence_score', 0)
                top_opportunities.append(
                    f"🎯 {symbol}: {upside:.0f}% upside (confidence: {confidence:.0f}%)"
                )
            
            title = f"📊 Pre-Market Brief – {now_pt.strftime('%B %d, %Y')}"
            
            message = f"""```
Portfolio Status:
• Total Value: ${total_value:,.0f}
• P&L: ${total_pl:+,.0f} ({total_pl_pct:+.1f}%)
• Positions: {len(positions)} open

{chr(10).join(significant_movers[:3]) if significant_movers else "• No significant overnight moves"}

Top Opportunities:
{chr(10).join(top_opportunities) if top_opportunities else "• Scanning for opportunities..."}

Market Opens: 6:30 AM PT
```"""
            
            return self.send_slack_message(message, title, "high")
            
        except Exception as e:
            print(f"Error in premarket brief: {e}")
            return False
    
    async def send_market_open_pulse(self, portfolio_data: Dict, market_analysis: Dict) -> bool:
        """Send market open analysis"""
        try:
            now_pt = get_pacific_time()
            
            title = f"🔔 Market Open Pulse – {now_pt.strftime('%H:%M PT')}"
            
            # Market sentiment and key levels
            message = f"""```
Market Pulse:
• Session: Market Hours Active
• Volatility: {market_analysis.get('volatility', 'Normal')}
• Key Resistance: SPY ${market_analysis.get('spy_resistance', 'N/A')}
• Key Support: SPY ${market_analysis.get('spy_support', 'N/A')}

Portfolio Focus:
• Watching {len(portfolio_data.get('positions', []))} positions
• Risk Level: {market_analysis.get('risk_level', 'Moderate')}

Next Update: 9:30 AM PT
```"""
            
            return self.send_slack_message(message, title, "medium")
            
        except Exception as e:
            print(f"Error in market open pulse: {e}")
            return False
    
    async def send_opportunity_alert(self, opportunity: Dict) -> bool:
        """Send immediate opportunity alert"""
        try:
            symbol = opportunity.get('symbol', 'Unknown')
            price = opportunity.get('current_price', 0)
            upside = opportunity.get('expected_upside', 0)
            confidence = opportunity.get('confidence_score', 0)
            catalyst = opportunity.get('catalyst', 'Market movement')
            
            title = f"🚨 OPPORTUNITY ALERT: {symbol}"
            
            message = f"""```
{symbol} - EXPLOSIVE SETUP DETECTED
• Current Price: ${price:.2f}
• Expected Upside: {upside:.0f}%
• AI Confidence: {confidence:.0f}%
• Catalyst: {catalyst}

RECOMMENDED ACTION:
• Entry Zone: ${price * 0.98:.2f} - ${price * 1.02:.2f}
• Target: ${price * (1 + upside/100):.2f}
• Stop Loss: ${price * 0.95:.2f}

⚡ EXECUTE VIA ALPACA IMMEDIATELY
```"""
            
            return self.send_slack_message(message, title, "high")
            
        except Exception as e:
            print(f"Error in opportunity alert: {e}")
            return False
    
    async def send_portfolio_alert(self, alert_type: str, symbol: str, data: Dict) -> bool:
        """Send portfolio-specific alerts"""
        try:
            if alert_type == "profit_target":
                title = f"💰 PROFIT TARGET: {symbol}"
                current_price = data.get('current_price', 0)
                target_price = data.get('target_price', 0)
                gain_pct = data.get('gain_percent', 0)
                
                message = f"""```
{symbol} HIT PROFIT TARGET
• Current: ${current_price:.2f}
• Target: ${target_price:.2f}
• Gain: +{gain_pct:.1f}%

RECOMMENDATION: Consider taking profits
Position size: {data.get('quantity', 'N/A')} shares
```"""
            
            elif alert_type == "stop_loss":
                title = f"⚠️ STOP LOSS ALERT: {symbol}"
                current_price = data.get('current_price', 0)
                stop_price = data.get('stop_price', 0)
                loss_pct = data.get('loss_percent', 0)
                
                message = f"""```
{symbol} APPROACHING STOP LOSS
• Current: ${current_price:.2f}
• Stop: ${stop_price:.2f}
• Loss: {loss_pct:.1f}%

RECOMMENDATION: Consider exit strategy
```"""
            
            elif alert_type == "thesis_invalidated":
                title = f"❌ THESIS CHANGE: {symbol}"
                reason = data.get('reason', 'Market conditions changed')
                
                message = f"""```
{symbol} THESIS INVALIDATED
Reason: {reason}

RECOMMENDATION: Review position
AI suggests: {data.get('ai_recommendation', 'HOLD')}
```"""
            
            else:
                title = f"📊 Portfolio Update: {symbol}"
                message = f"```\n{data.get('message', 'Portfolio update')}\n```"
            
            return self.send_slack_message(message, title, "medium")
            
        except Exception as e:
            print(f"Error in portfolio alert: {e}")
            return False
    
    async def send_end_of_day_summary(self, portfolio_data: Dict, daily_performance: Dict) -> bool:
        """Send end of day portfolio summary"""
        try:
            now_pt = get_pacific_time()
            
            positions = portfolio_data.get('positions', [])
            day_pl = daily_performance.get('day_pl', 0)
            day_pl_pct = daily_performance.get('day_pl_percent', 0)
            
            # Best and worst performers
            if positions:
                best_performer = max(positions, key=lambda x: x['unrealized_plpc'])
                worst_performer = min(positions, key=lambda x: x['unrealized_plpc'])
                best_perf_text = f"{best_performer['symbol']} ({best_performer['unrealized_plpc']:+.1f}%)"
                worst_perf_text = f"{worst_performer['symbol']} ({worst_performer['unrealized_plpc']:+.1f}%)"
            else:
                best_performer = worst_performer = None
                best_perf_text = "N/A"
                worst_perf_text = "N/A"
            
            title = f"📈 End-of-Day Summary – {now_pt.strftime('%B %d')}"
            
            message = f"""```
Daily Performance:
• P&L: ${day_pl:+,.0f} ({day_pl_pct:+.1f}%)
• Best: {best_perf_text}
• Worst: {worst_perf_text}

Tomorrow's Focus:
• {daily_performance.get('tomorrow_focus', 'Continue monitoring positions')}
• Risk Level: {daily_performance.get('risk_assessment', 'Moderate')}

After-hours monitoring active.
```"""
            
            return self.send_slack_message(message, title, "medium")
            
        except Exception as e:
            print(f"Error in end of day summary: {e}")
            return False
    
    async def send_midday_pulse(self, portfolio_data: Dict, midday_analysis: Dict) -> bool:
        """Send midday market pulse notification"""
        try:
            now_pt = get_pacific_time()
            positions = portfolio_data.get('positions', [])
            
            title = f"⚡ Midday Pulse – {now_pt.strftime('%B %d, %I:%M %p PT')}"
            
            # Calculate morning performance
            total_pl = sum(pos['unrealized_pl'] for pos in positions)
            
            # Check for any preemptive analysis results
            preemptive_data = portfolio_data.get('preemptive_analysis', {})
            replacement_count = preemptive_data.get('replacement_count', 0)
            opportunity_count = preemptive_data.get('opportunity_count', 0)
            
            message = f"""```
Morning Assessment:
• Total P&L: ${total_pl:+,.0f}
• Active Positions: {len(positions)}
• Market Status: {midday_analysis.get('morning_performance', 'Monitoring')}

Afternoon Outlook:
• Trend: {midday_analysis.get('afternoon_outlook', 'Stable')}
• Key Levels: {midday_analysis.get('key_levels', 'Watching support/resistance')}

AI Analysis Status:
• Replacement candidates: {replacement_count}
• New opportunities: {opportunity_count}

Next update: End-of-day wrap at 12:45 PM PT
```"""
            
            return self.send_slack_message(message, title, "medium")
            
        except Exception as e:
            print(f"Error in midday pulse: {e}")
            return False
    
    async def send_afterhours_learning(self, portfolio_data: Dict, learning_insights: Dict) -> bool:
        """Send after-hours learning and analysis notification"""
        try:
            now_pt = get_pacific_time()
            positions = portfolio_data.get('positions', [])
            
            title = f"🧠 After-Hours Learning – {now_pt.strftime('%B %d')}"
            
            # Get daily performance
            total_pl = sum(pos['unrealized_pl'] for pos in positions)
            winning_positions = len([p for p in positions if p['unrealized_plpc'] > 0])
            
            message = f"""```
Today's Learning Summary:
• Lessons: {learning_insights.get('todays_lessons', 'Portfolio performed within expectations')}
• Win Rate: {winning_positions}/{len(positions)} positions profitable
• Risk Level: {learning_insights.get('risk_assessment', 'Moderate')}

Tomorrow's Plan:
• Strategy: {learning_insights.get('tomorrows_plan', 'Continue monitoring key positions')}
• Focus Areas: High-probability setups
• Risk Management: Active monitoring

System Status:
• Baselines: Updated and cached
• Analysis: Ready for tomorrow's cycles
• Monitoring: Active through overnight

Sleep well! 🌙 System continues monitoring.
```"""
            
            return self.send_slack_message(message, title, "low")
            
        except Exception as e:
            print(f"Error in afterhours learning: {e}")
            return False
    
    def check_scheduled_notifications(self, portfolio_data: Dict = None, opportunities: List[Dict] = None) -> bool:
        """Check if any scheduled notifications should be sent"""
        market_status = get_market_status()
        current_time = market_status["current_time_pt"]
        
        # Only send on trading days
        if market_status["session"] == "weekend":
            return False
        
        notifications_sent = False
        
        # Check each scheduled notification
        for notification_type, timing in self.schedule.items():
            # Check if it's time for this notification (within 5 minutes)
            if is_notification_time(timing["hour"], timing["minute"], tolerance_minutes=5):
                
                # Check if we've already sent this notification today
                today_key = f"{current_time.date()}_{notification_type}"
                if today_key in self.last_sent:
                    continue
                
                # Run preemptive analysis before major notifications
                enhanced_portfolio_data = portfolio_data
                if portfolio_data and notification_type in ["premarket_brief", "market_open_pulse", "end_of_day_wrap"]:
                    try:
                        from smart_refresh_system import trigger_preemptive_analysis_if_needed
                        preemptive_result = trigger_preemptive_analysis_if_needed(portfolio_data)
                        
                        if preemptive_result.get("status") == "completed":
                            print(f"✅ Preemptive analysis completed before {notification_type}")
                            # Enhanced portfolio data would include analysis results
                            enhanced_portfolio_data = portfolio_data.copy()
                            enhanced_portfolio_data["preemptive_analysis"] = preemptive_result
                    except Exception as e:
                        print(f"Warning: Preemptive analysis failed before {notification_type}: {e}")
                
                # Send appropriate notification with enhanced data
                if notification_type == "premarket_brief" and enhanced_portfolio_data and opportunities:
                    asyncio.create_task(self.send_premarket_brief(enhanced_portfolio_data, opportunities))
                    self.last_sent[today_key] = current_time
                    notifications_sent = True
                
                elif notification_type == "market_open_pulse" and enhanced_portfolio_data:
                    market_analysis = {"volatility": "Normal", "risk_level": "Moderate"}
                    asyncio.create_task(self.send_market_open_pulse(enhanced_portfolio_data, market_analysis))
                    self.last_sent[today_key] = current_time
                    notifications_sent = True
                
                elif notification_type == "midday_pulse" and enhanced_portfolio_data:
                    midday_analysis = {
                        "morning_performance": "Monitoring",
                        "afternoon_outlook": "Stable",
                        "key_levels": "Watching support/resistance"
                    }
                    asyncio.create_task(self.send_midday_pulse(enhanced_portfolio_data, midday_analysis))
                    self.last_sent[today_key] = current_time
                    notifications_sent = True
                
                elif notification_type == "end_of_day_wrap" and enhanced_portfolio_data:
                    daily_performance = {
                        "day_pl": sum(pos['unrealized_pl'] for pos in enhanced_portfolio_data.get('positions', [])),
                        "day_pl_percent": 0,  # Would calculate from daily change
                        "tomorrow_focus": "Monitor current positions"
                    }
                    asyncio.create_task(self.send_end_of_day_summary(enhanced_portfolio_data, daily_performance))
                    self.last_sent[today_key] = current_time
                    notifications_sent = True
                
                elif notification_type == "afterhours_learning" and enhanced_portfolio_data:
                    learning_insights = {
                        "todays_lessons": "Portfolio performed within expectations",
                        "tomorrows_plan": "Continue monitoring key positions",
                        "risk_assessment": "Moderate"
                    }
                    asyncio.create_task(self.send_afterhours_learning(enhanced_portfolio_data, learning_insights))
                    self.last_sent[today_key] = current_time
                    notifications_sent = True
        
        return notifications_sent

# Global instance
slack_engine = SlackNotificationEngine()

async def send_opportunity_alert(opportunity: Dict) -> bool:
    """Send immediate opportunity alert to Slack"""
    return await slack_engine.send_opportunity_alert(opportunity)

async def send_portfolio_alert(alert_type: str, symbol: str, data: Dict) -> bool:
    """Send portfolio alert to Slack"""
    return await slack_engine.send_portfolio_alert(alert_type, symbol, data)

def check_scheduled_notifications(portfolio_data: Dict = None, opportunities: List[Dict] = None) -> bool:
    """Check and send scheduled notifications"""
    return slack_engine.check_scheduled_notifications(portfolio_data, opportunities)