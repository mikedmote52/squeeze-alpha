#!/bin/bash

# Auto-Start AI Trading System
# This script sets up the system to run automatically without terminals

echo "🚀 Setting up Auto-Start AI Trading System"
echo "========================================="

# 1. Create LaunchAgent for Backend
echo "📋 Creating LaunchAgent for Backend..."

cat > ~/Library/LaunchAgents/com.aitrading.backend.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aitrading.backend</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>/Users/michaelmote/Desktop/ai-trading-system-complete/real_ai_backend.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/michaelmote/Desktop/ai-trading-system-complete</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/Users/michaelmote/Desktop/ai-trading-system-complete/logs/backend_auto.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/michaelmote/Desktop/ai-trading-system-complete/logs/backend_auto_error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

# 2. Create LaunchAgent for Streamlit
echo "📱 Creating LaunchAgent for Streamlit..."

cat > ~/Library/LaunchAgents/com.aitrading.streamlit.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aitrading.streamlit</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>-m</string>
        <string>streamlit</string>
        <string>run</string>
        <string>/Users/michaelmote/Desktop/ai-trading-system-complete/streamlit_app.py</string>
        <string>--server.port</string>
        <string>8501</string>
        <string>--server.address</string>
        <string>0.0.0.0</string>
        <string>--server.headless</string>
        <string>true</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/michaelmote/Desktop/ai-trading-system-complete</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/Users/michaelmote/Desktop/ai-trading-system-complete/logs/streamlit_auto.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/michaelmote/Desktop/ai-trading-system-complete/logs/streamlit_auto_error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

# 3. Create logs directory
mkdir -p /Users/michaelmote/Desktop/ai-trading-system-complete/logs

# 4. Load the LaunchAgents
echo "🔄 Loading LaunchAgents..."
launchctl load ~/Library/LaunchAgents/com.aitrading.backend.plist
launchctl load ~/Library/LaunchAgents/com.aitrading.streamlit.plist

# 5. Start the services
echo "🚀 Starting services..."
launchctl start com.aitrading.backend
sleep 3
launchctl start com.aitrading.streamlit
sleep 5

# 6. Check status
echo ""
echo "📊 System Status:"
if launchctl list | grep com.aitrading.backend > /dev/null; then
    echo "✅ Backend service: RUNNING"
else
    echo "❌ Backend service: NOT RUNNING"
fi

if launchctl list | grep com.aitrading.streamlit > /dev/null; then
    echo "✅ Streamlit service: RUNNING" 
else
    echo "❌ Streamlit service: NOT RUNNING"
fi

# 7. Get network IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo ""
echo "🎉 AUTO-START SETUP COMPLETE!"
echo "============================="
echo ""
echo "📱 PHONE ACCESS:"
echo "   http://$LOCAL_IP:8501"
echo ""
echo "💻 COMPUTER ACCESS:"
echo "   http://localhost:8501"
echo ""
echo "🔄 SYSTEM STATUS:"
echo "   - Runs automatically when you log in"
echo "   - Restarts automatically if it crashes"
echo "   - No terminal windows needed"
echo "   - Access from phone anytime"
echo ""
echo "📋 MANAGEMENT COMMANDS:"
echo "   Stop:    launchctl stop com.aitrading.backend && launchctl stop com.aitrading.streamlit"
echo "   Start:   launchctl start com.aitrading.backend && launchctl start com.aitrading.streamlit"
echo "   Remove:  launchctl unload ~/Library/LaunchAgents/com.aitrading.*.plist"
echo ""
echo "📊 LOGS:"
echo "   Backend: tail -f logs/backend_auto.log"
echo "   Frontend: tail -f logs/streamlit_auto.log"