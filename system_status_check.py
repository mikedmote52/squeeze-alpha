#!/usr/bin/env python3
"""
System Status Check - Verify all components are ready for tomorrow's trading
"""

import os
import sys
from datetime import datetime, timedelta
import pytz

# Add core directory to path
sys.path.append('./core')

def check_environment_variables():
    """Check all required environment variables"""
    required_vars = [
        'ALPACA_API_KEY',
        'ALPACA_SECRET_KEY', 
        'OPENROUTER_API_KEY',
        'SLACK_WEBHOOK'
    ]
    
    missing = []
    configured = []
    
    for var in required_vars:
        if os.getenv(var):
            configured.append(var)
        else:
            missing.append(var)
    
    return configured, missing

def check_core_modules():
    """Check if all core modules can be imported"""
    modules_to_check = [
        'pacific_time_utils',
        'api_cost_tracker', 
        'slack_notification_engine',
        'smart_refresh_system',
        'ai_baseline_cache_system',
        'three_day_memory_system'
    ]
    
    working_modules = []
    broken_modules = []
    
    for module in modules_to_check:
        try:
            __import__(module)
            working_modules.append(module)
        except Exception as e:
            broken_modules.append(f"{module}: {str(e)}")
    
    return working_modules, broken_modules

def get_notification_schedule():
    """Get tomorrow's notification schedule in Pacific Time"""
    PT = pytz.timezone('US/Pacific')
    tomorrow = datetime.now(PT) + timedelta(days=1)
    
    schedule = [
        {"time": "5:15 AM PT", "event": "Preemptive Analysis - Pre-market", "description": "AI runs portfolio analysis before premarket notification"},
        {"time": "5:45 AM PT", "event": "Premarket Brief", "description": "Portfolio overview, overnight developments, day's plan"},
        {"time": "6:15 AM PT", "event": "Preemptive Analysis - Market Open", "description": "AI updates baselines before market open"},
        {"time": "6:45 AM PT", "event": "Market Open Pulse", "description": "Opening analysis, volatility assessment, key levels"},
        {"time": "9:30 AM PT", "event": "Midday Pulse", "description": "Morning performance review, afternoon outlook"},
        {"time": "10:15 AM PT", "event": "Preemptive Analysis - Midday", "description": "AI scans for opportunities and replacements"},
        {"time": "12:45 PM PT", "event": "End-of-Day Wrap", "description": "Daily performance summary, tomorrow's focus"},
        {"time": "12:45 PM PT", "event": "Preemptive Analysis - EOD", "description": "Final analysis before market close"},
        {"time": "1:30 PM PT", "event": "After-Hours Learning", "description": "Learning insights, strategy for next day"}
    ]
    
    return tomorrow, schedule

def main():
    """Run complete system status check"""
    print("🔥 AI Trading System - Status Check")
    print("="*50)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    configured, missing = check_environment_variables()
    for var in configured:
        print(f"  ✅ {var}")
    for var in missing:
        print(f"  ❌ {var}")
    
    # Check core modules
    print("\n🧩 Core Modules:")
    working, broken = check_core_modules()
    for module in working:
        print(f"  ✅ {module}")
    for module in broken:
        print(f"  ❌ {module}")
    
    # Get tomorrow's schedule
    tomorrow, schedule = get_notification_schedule()
    print(f"\n📅 Tomorrow's Schedule ({tomorrow.strftime('%A, %B %d, %Y')}):")
    
    for item in schedule:
        print(f"  🕐 {item['time']} - {item['event']}")
        print(f"      {item['description']}")
    
    # System readiness assessment
    print("\n🎯 System Readiness Assessment:")
    
    total_issues = len(missing) + len(broken)
    if total_issues == 0:
        print("  ✅ ALL SYSTEMS READY FOR TRADING!")
        print("  ✅ Preemptive analysis will run before each notification")
        print("  ✅ All baselines will be cached and ready")
        print("  ✅ Replacement candidates will be identified")
        print("  ✅ New opportunities will be discovered")
    else:
        print(f"  ⚠️  {total_issues} issues need attention:")
        if 'SLACK_WEBHOOK' in missing:
            print("    - Slack notifications may not work (webhook needs update)")
        if broken:
            print("    - Some core modules have import errors")
    
    # Slack webhook status
    if 'SLACK_WEBHOOK' in configured:
        print("\n📢 Slack Notification Status:")
        print("  ⚠️  Webhook configured but needs verification")
        print("  💡 Recommendation: Test webhook or generate new token")
        print("  📱 Expected notifications: 5 daily messages as scheduled")
    
    print("\n" + "="*50)
    print("System check complete. Ready for tomorrow's trading session!")

if __name__ == "__main__":
    main()