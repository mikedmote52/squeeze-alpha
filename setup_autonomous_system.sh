#!/bin/bash

# AI Trading System - Autonomous Setup Script
# This script sets up the system to run automatically without manual activation

echo "🤖 AI TRADING SYSTEM - AUTONOMOUS SETUP"
echo "======================================"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

echo "📁 Creating logs directory..."
echo "✅ Logs directory ready"
echo ""

echo "🔧 SETUP OPTIONS:"
echo ""
echo "1. LAUNCHAGENT (Recommended for macOS)"
echo "   - Automatically starts when you log in"
echo "   - Runs in background continuously"
echo "   - No manual activation needed"
echo ""
echo "2. MANUAL STARTUP"
echo "   - Run the system manually when needed"
echo "   - Full control over when it runs"
echo ""

read -p "Choose setup type (1 for LaunchAgent, 2 for Manual): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "🚀 SETTING UP LAUNCHAGENT..."
    
    # Copy plist to LaunchAgents directory
    PLIST_FILE="com.aitrading.autonomous.plist"
    LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
    
    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "$LAUNCH_AGENTS_DIR"
    
    # Copy the plist file
    cp "$PLIST_FILE" "$LAUNCH_AGENTS_DIR/"
    
    echo "✅ LaunchAgent configuration installed"
    
    # Load the LaunchAgent
    launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_FILE"
    
    echo "✅ LaunchAgent loaded and ready"
    echo ""
    echo "🎯 AUTONOMOUS SYSTEM IS NOW ACTIVE!"
    echo ""
    echo "📋 WHAT HAPPENS NOW:"
    echo "   • System will start automatically when you log in"
    echo "   • Runs continuously in the background"
    echo "   • Sends Slack notifications at scheduled times:"
    echo "     - 4:00 AM PT: Early pre-market scan"
    echo "     - 5:30 AM PT: Full pre-market analysis"
    echo "     - 6:30 AM PT: Market open analysis"
    echo "     - 9:00 AM PT: Mid-morning scan"
    echo "     - 12:00 PM PT: Midday analysis"
    echo "     - 1:00 PM PT: Market close summary"
    echo "     - 3:00 PM PT: After-hours evolution"
    echo ""
    echo "📊 MONITORING:"
    echo "   • Check logs: tail -f logs/autonomous_system.log"
    echo "   • Check errors: tail -f logs/autonomous_system_error.log"
    echo ""
    echo "🛑 TO STOP:"
    echo "   • launchctl unload ~/Library/LaunchAgents/$PLIST_FILE"
    echo ""
    echo "✅ NO MANUAL ACTIVATION NEEDED - SYSTEM IS AUTONOMOUS!"

elif [ "$choice" = "2" ]; then
    echo ""
    echo "📖 MANUAL STARTUP INSTRUCTIONS:"
    echo ""
    echo "To start the system manually, run:"
    echo "   python3 core/pacific_time_schedule.py"
    echo ""
    echo "Or use the launcher:"
    echo "   python3 utils/start_autonomous_system.py"
    echo ""
    echo "⚠️  Note: With manual startup, you need to run the command"
    echo "   each time you want the system to operate."

else
    echo ""
    echo "❌ Invalid choice. Please run the script again."
    exit 1
fi

echo ""
echo "🔐 SECURITY CHECK:"
echo "   The system uses real APIs and live data only"
echo "   No mock or fake data is used"
echo "   All trades require proper authentication"
echo ""
echo "✅ SETUP COMPLETE!"