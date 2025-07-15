#!/usr/bin/env python3
"""
Pacific Time Utilities
Handles all time-related functions for the trading system in Pacific Time
"""

from datetime import datetime, timedelta
import pytz
from typing import Tuple, Dict

# Pacific timezone
PT = pytz.timezone('US/Pacific')

def get_pacific_time() -> datetime:
    """Get current Pacific time"""
    return datetime.now(PT)

def get_market_status() -> Dict:
    """Get detailed market status in Pacific Time"""
    now_pt = get_pacific_time()
    
    # Market hours in PT: 6:30 AM - 1:00 PM, Monday-Friday
    market_open_pt = now_pt.replace(hour=6, minute=30, second=0, microsecond=0)
    market_close_pt = now_pt.replace(hour=13, minute=0, second=0, microsecond=0)
    
    # Pre-market: 1:00 AM - 6:30 AM PT
    premarket_open_pt = now_pt.replace(hour=1, minute=0, second=0, microsecond=0)
    
    # After-hours: 1:00 PM - 5:00 PM PT
    afterhours_close_pt = now_pt.replace(hour=17, minute=0, second=0, microsecond=0)
    
    is_weekday = now_pt.weekday() < 5  # Monday = 0, Friday = 4
    
    # Determine market session
    if not is_weekday:
        session = "weekend"
        is_trading = False
    elif premarket_open_pt <= now_pt < market_open_pt:
        session = "premarket"
        is_trading = False
    elif market_open_pt <= now_pt <= market_close_pt:
        session = "market_hours"
        is_trading = True
    elif market_close_pt < now_pt <= afterhours_close_pt:
        session = "afterhours"
        is_trading = False
    else:
        session = "closed"
        is_trading = False
    
    # Calculate time to next session
    if session == "premarket":
        next_session = "Market opens"
        time_to_next = market_open_pt - now_pt
    elif session == "market_hours":
        next_session = "Market closes"
        time_to_next = market_close_pt - now_pt
    elif session == "afterhours":
        next_session = "Market opens tomorrow"
        tomorrow_open = (now_pt + timedelta(days=1)).replace(hour=6, minute=30, second=0, microsecond=0)
        if now_pt.weekday() == 4:  # Friday
            # Next Monday
            tomorrow_open = (now_pt + timedelta(days=3)).replace(hour=6, minute=30, second=0, microsecond=0)
        time_to_next = tomorrow_open - now_pt
    else:
        if now_pt.weekday() >= 5:  # Weekend
            days_until_monday = 7 - now_pt.weekday()
            next_session = "Market opens Monday"
            time_to_next = (now_pt + timedelta(days=days_until_monday)).replace(hour=6, minute=30, second=0, microsecond=0) - now_pt
        else:
            next_session = "Pre-market opens"
            tomorrow_premarket = (now_pt + timedelta(days=1)).replace(hour=1, minute=0, second=0, microsecond=0)
            time_to_next = tomorrow_premarket - now_pt
    
    return {
        "current_time_pt": now_pt,
        "session": session,
        "is_trading": is_trading,
        "is_premarket": session == "premarket",
        "is_afterhours": session == "afterhours", 
        "next_session": next_session,
        "time_to_next": time_to_next,
        "formatted_time": now_pt.strftime("%Y-%m-%d %H:%M:%S PT"),
        "market_open_pt": market_open_pt,
        "market_close_pt": market_close_pt
    }

def is_notification_time(target_hour: int, target_minute: int, tolerance_minutes: int = 5) -> bool:
    """Check if current PT time is within tolerance of target notification time"""
    now_pt = get_pacific_time()
    target_time = now_pt.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    time_diff = abs((now_pt - target_time).total_seconds() / 60)
    return time_diff <= tolerance_minutes

def get_next_trading_day() -> datetime:
    """Get the next trading day in Pacific Time"""
    now_pt = get_pacific_time()
    
    # If it's Friday after market close, next trading day is Monday
    if now_pt.weekday() == 4 and now_pt.hour >= 13:  # Friday after 1 PM PT
        next_trading = now_pt + timedelta(days=3)
    # If it's Saturday or Sunday
    elif now_pt.weekday() >= 5:
        days_until_monday = 7 - now_pt.weekday()
        next_trading = now_pt + timedelta(days=days_until_monday)
    # If it's after market close on weekday
    elif now_pt.weekday() < 4 and now_pt.hour >= 13:  # After 1 PM PT on Mon-Thu
        next_trading = now_pt + timedelta(days=1)
    else:
        # Same day if before market close
        next_trading = now_pt
    
    return next_trading.replace(hour=6, minute=30, second=0, microsecond=0)

def format_time_until(target_time: datetime) -> str:
    """Format time remaining until target time"""
    now_pt = get_pacific_time()
    time_diff = target_time - now_pt
    
    if time_diff.total_seconds() < 0:
        return "Past due"
    
    total_seconds = int(time_diff.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def get_trading_day_schedule() -> Dict:
    """Get the complete trading day schedule for notifications"""
    now_pt = get_pacific_time()
    
    # Define notification times in PT
    schedule = {
        "premarket_brief": now_pt.replace(hour=5, minute=45, second=0, microsecond=0),
        "market_open_pulse": now_pt.replace(hour=6, minute=45, second=0, microsecond=0), 
        "midday_pulse": now_pt.replace(hour=9, minute=30, second=0, microsecond=0),
        "end_of_day_wrap": now_pt.replace(hour=12, minute=45, second=0, microsecond=0),
        "afterhours_learning": now_pt.replace(hour=13, minute=30, second=0, microsecond=0)
    }
    
    # Add next occurrence if time has passed today
    for event, time in schedule.items():
        if time < now_pt:
            # Move to next trading day
            next_trading = get_next_trading_day()
            schedule[event] = time.replace(
                year=next_trading.year,
                month=next_trading.month, 
                day=next_trading.day
            )
    
    return schedule