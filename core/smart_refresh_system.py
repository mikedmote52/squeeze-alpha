#!/usr/bin/env python3
"""
Smart Refresh System
Manages intelligent refresh timing based on market conditions and volatility
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
import pytz
from dataclasses import dataclass

from pacific_time_utils import get_pacific_time, get_market_status
from api_cost_tracker import log_api_call

@dataclass
class RefreshEvent:
    """Represents a refresh event"""
    timestamp: datetime
    trigger: str  # "scheduled", "volatility", "manual", "news"
    reason: str
    data_refreshed: List[str]

class SmartRefreshSystem:
    """Manages intelligent refresh timing to minimize API costs while maximizing responsiveness"""
    
    def __init__(self):
        self.refresh_history = []
        self.last_refresh = {}
        self.volatility_threshold = 0.02  # 2% price change triggers refresh
        self.volume_threshold = 1.5  # 1.5x average volume triggers refresh
        
        # Scheduled refresh times (PT)
        self.scheduled_refreshes = {
            "premarket_scan": {"hour": 5, "minute": 30},
            "market_open": {"hour": 6, "minute": 30},
            "morning_check": {"hour": 8, "minute": 30},
            "midday_check": {"hour": 10, "minute": 30}, 
            "afternoon_check": {"hour": 12, "minute": 0},
            "market_close": {"hour": 13, "minute": 0},
            "afterhours_wrap": {"hour": 14, "minute": 0}
        }
        
        self.last_volatility_check = None
        self.baseline_prices = {}
        self.baseline_volumes = {}
    
    def should_refresh_portfolio(self, current_data: Dict = None) -> Dict:
        """Determine if portfolio should be refreshed based on smart logic"""
        now_pt = get_pacific_time()
        market_status = get_market_status()
        
        refresh_decision = {
            "should_refresh": False,
            "reason": "",
            "priority": "low",
            "data_to_refresh": []
        }
        
        # Always refresh if no data
        if not current_data:
            refresh_decision.update({
                "should_refresh": True,
                "reason": "No current data available",
                "priority": "high",
                "data_to_refresh": ["portfolio", "opportunities", "market_data"]
            })
            return refresh_decision
        
        # Check scheduled refresh times
        scheduled_reason = self._check_scheduled_refresh(now_pt, market_status)
        if scheduled_reason:
            refresh_decision.update({
                "should_refresh": True,
                "reason": scheduled_reason,
                "priority": "medium",
                "data_to_refresh": ["portfolio", "opportunities"] if "premarket" in scheduled_reason else ["portfolio"]
            })
            return refresh_decision
        
        # Check volatility-based refresh (only during market hours)
        if market_status["is_trading"]:
            volatility_reason = self._check_volatility_refresh(current_data)
            if volatility_reason:
                refresh_decision.update({
                    "should_refresh": True,
                    "reason": volatility_reason,
                    "priority": "high",
                    "data_to_refresh": ["portfolio", "market_data"]
                })
                return refresh_decision
        
        # Check if data is stale (more than 30 minutes old)
        last_update = current_data.get('last_updated')
        if last_update:
            if isinstance(last_update, str):
                last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
            
            # Convert to PT for comparison
            if last_update.tzinfo:
                last_update_pt = last_update.astimezone(pytz.timezone('US/Pacific'))
            else:
                last_update_pt = last_update
                
            time_since_update = (now_pt - last_update_pt).total_seconds() / 60
            
            if time_since_update > 30:  # More than 30 minutes old
                refresh_decision.update({
                    "should_refresh": True,
                    "reason": f"Data stale ({time_since_update:.0f} minutes old)",
                    "priority": "medium",
                    "data_to_refresh": ["portfolio"]
                })
                return refresh_decision
        
        return refresh_decision
    
    def _check_scheduled_refresh(self, now_pt: datetime, market_status: Dict) -> Optional[str]:
        """Check if current time matches scheduled refresh"""
        
        # Only check on trading days
        if market_status["session"] == "weekend":
            return None
        
        for refresh_name, timing in self.scheduled_refreshes.items():
            target_time = now_pt.replace(
                hour=timing["hour"], 
                minute=timing["minute"], 
                second=0, 
                microsecond=0
            )
            
            # Check if within 2 minutes of scheduled time
            time_diff = abs((now_pt - target_time).total_seconds() / 60)
            
            if time_diff <= 2:
                # Check if we've already refreshed for this event today
                today_key = f"{now_pt.date()}_{refresh_name}"
                if today_key not in self.last_refresh:
                    self.last_refresh[today_key] = now_pt
                    return f"Scheduled refresh: {refresh_name}"
        
        return None
    
    def _check_volatility_refresh(self, current_data: Dict) -> Optional[str]:
        """Check if portfolio volatility warrants immediate refresh"""
        
        positions = current_data.get('positions', [])
        if not positions:
            return None
        
        # Check if we've done volatility check recently (minimum 5 minutes between checks)
        if self.last_volatility_check:
            time_since_last = (get_pacific_time() - self.last_volatility_check).total_seconds() / 60
            if time_since_last < 5:
                return None
        
        high_volatility_detected = False
        volatile_symbols = []
        
        for position in positions:
            symbol = position['symbol']
            current_price = position['current_price']
            current_plpc = abs(position['unrealized_plpc'])
            
            # Store baseline if not exists
            if symbol not in self.baseline_prices:
                self.baseline_prices[symbol] = current_price
                continue
            
            # Calculate price change from baseline
            baseline_price = self.baseline_prices[symbol]
            price_change = abs((current_price - baseline_price) / baseline_price)
            
            # Check if significant move (>2% from baseline OR >5% total P&L change)
            if price_change > self.volatility_threshold or current_plpc > 5:
                high_volatility_detected = True
                volatile_symbols.append(f"{symbol} ({price_change*100:.1f}%)")
                
                # Update baseline
                self.baseline_prices[symbol] = current_price
        
        if high_volatility_detected:
            self.last_volatility_check = get_pacific_time()
            return f"High volatility detected: {', '.join(volatile_symbols)}"
        
        return None
    
    def should_refresh_opportunities(self) -> Dict:
        """Determine if opportunities should be refreshed"""
        now_pt = get_pacific_time()
        market_status = get_market_status()
        
        refresh_decision = {
            "should_refresh": False,
            "reason": "",
            "priority": "low"
        }
        
        # Refresh opportunities less frequently to save API costs
        last_opp_refresh = self.last_refresh.get('opportunities')
        
        if not last_opp_refresh:
            # First time - always refresh
            refresh_decision.update({
                "should_refresh": True,
                "reason": "Initial opportunity scan",
                "priority": "high"
            })
            self.last_refresh['opportunities'] = now_pt
            return refresh_decision
        
        time_since_opp_refresh = (now_pt - last_opp_refresh).total_seconds() / 60
        
        # Refresh opportunities based on market session
        if market_status["session"] == "premarket" and time_since_opp_refresh > 60:
            # Every hour during pre-market
            refresh_decision.update({
                "should_refresh": True,
                "reason": "Pre-market opportunity scan",
                "priority": "medium"
            })
            self.last_refresh['opportunities'] = now_pt
        
        elif market_status["is_trading"] and time_since_opp_refresh > 120:
            # Every 2 hours during market hours
            refresh_decision.update({
                "should_refresh": True,
                "reason": "Market hours opportunity scan",
                "priority": "medium"
            })
            self.last_refresh['opportunities'] = now_pt
        
        elif market_status["session"] == "afterhours" and time_since_opp_refresh > 180:
            # Every 3 hours after market
            refresh_decision.update({
                "should_refresh": True,
                "reason": "After-hours opportunity scan",
                "priority": "low"
            })
            self.last_refresh['opportunities'] = now_pt
        
        return refresh_decision
    
    def log_refresh_event(self, trigger: str, reason: str, data_refreshed: List[str]):
        """Log a refresh event for analysis"""
        event = RefreshEvent(
            timestamp=get_pacific_time(),
            trigger=trigger,
            reason=reason,
            data_refreshed=data_refreshed
        )
        
        self.refresh_history.append(event)
        
        # Keep only last 100 events
        if len(self.refresh_history) > 100:
            self.refresh_history = self.refresh_history[-100:]
        
        # Log API call for cost tracking
        api_calls = len(data_refreshed)
        log_api_call("smart_refresh", "system_refresh", success=True)
        
        print(f"📊 Smart Refresh: {reason} (refreshed: {', '.join(data_refreshed)})")
    
    def get_refresh_stats(self) -> Dict:
        """Get refresh statistics for analysis"""
        if not self.refresh_history:
            return {"total_refreshes": 0, "avg_per_day": 0, "triggers": {}}
        
        total_refreshes = len(self.refresh_history)
        
        # Count triggers
        trigger_counts = {}
        for event in self.refresh_history:
            trigger_counts[event.trigger] = trigger_counts.get(event.trigger, 0) + 1
        
        # Calculate average per day (last 7 days)
        recent_events = [e for e in self.refresh_history 
                        if (get_pacific_time() - e.timestamp).days <= 7]
        avg_per_day = len(recent_events) / 7 if recent_events else 0
        
        return {
            "total_refreshes": total_refreshes,
            "avg_per_day": round(avg_per_day, 1),
            "triggers": trigger_counts,
            "last_refresh": self.refresh_history[-1].timestamp if self.refresh_history else None
        }
    
    def trigger_preemptive_analysis_if_needed(self, portfolio_data: Dict = None) -> Dict:
        """Trigger preemptive analysis before major scheduled refreshes"""
        now_pt = get_pacific_time()
        market_status = get_market_status()
        
        # Only run on trading days
        if market_status["session"] == "weekend":
            return {"status": "skipped", "reason": "weekend"}
        
        # Key times that warrant preemptive analysis (15 minutes before scheduled refreshes)
        preemptive_times = {
            "pre_premarket": {"hour": 5, "minute": 15},  # Before premarket scan
            "pre_market_open": {"hour": 6, "minute": 15},  # Before market open
            "pre_midday": {"hour": 10, "minute": 15},  # Before midday check
            "pre_market_close": {"hour": 12, "minute": 45}  # Before market close
        }
        
        for analysis_name, timing in preemptive_times.items():
            target_time = now_pt.replace(
                hour=timing["hour"], 
                minute=timing["minute"], 
                second=0, 
                microsecond=0
            )
            
            # Check if within 3 minutes of preemptive time
            time_diff = abs((now_pt - target_time).total_seconds() / 60)
            
            if time_diff <= 3:
                # Check if we've already run preemptive analysis for this cycle today
                today_key = f"{now_pt.date()}_{analysis_name}"
                if today_key not in self.last_refresh:
                    try:
                        # Import here to avoid circular imports
                        from ai_baseline_cache_system import ai_baseline_cache
                        
                        print(f"🎯 Triggering preemptive analysis for {analysis_name}")
                        
                        # Run preemptive analysis if portfolio data available
                        if portfolio_data:
                            analysis_results = ai_baseline_cache.run_preemptive_cycle_analysis(portfolio_data)
                            
                            # Mark as completed
                            self.last_refresh[today_key] = now_pt
                            
                            # Log the event
                            self.log_refresh_event(
                                trigger="preemptive_analysis",
                                reason=f"Preemptive analysis: {analysis_name}",
                                data_refreshed=["baselines", "portfolio_analysis", "replacement_candidates"]
                            )
                            
                            return {
                                "status": "completed",
                                "analysis_name": analysis_name,
                                "results_summary": analysis_results.get("upgraded_summary", ""),
                                "replacement_count": len(analysis_results.get("replacement_candidates", [])),
                                "opportunity_count": len(analysis_results.get("new_opportunities", [])),
                                "timestamp": now_pt.isoformat()
                            }
                        else:
                            return {
                                "status": "skipped", 
                                "reason": "No portfolio data available for preemptive analysis"
                            }
                            
                    except Exception as e:
                        print(f"Error in preemptive analysis: {e}")
                        return {
                            "status": "error",
                            "reason": str(e),
                            "timestamp": now_pt.isoformat()
                        }
        
        return {"status": "not_needed", "reason": "Not within preemptive analysis window"}

# Global instance
smart_refresh = SmartRefreshSystem()

def should_refresh_portfolio(current_data: Dict = None) -> Dict:
    """Check if portfolio should be refreshed"""
    return smart_refresh.should_refresh_portfolio(current_data)

def should_refresh_opportunities() -> Dict:
    """Check if opportunities should be refreshed"""
    return smart_refresh.should_refresh_opportunities()

def log_refresh_event(trigger: str, reason: str, data_refreshed: List[str]):
    """Log a refresh event"""
    smart_refresh.log_refresh_event(trigger, reason, data_refreshed)

def trigger_preemptive_analysis_if_needed(portfolio_data: Dict = None) -> Dict:
    """Trigger preemptive analysis if within scheduled window"""
    return smart_refresh.trigger_preemptive_analysis_if_needed(portfolio_data)