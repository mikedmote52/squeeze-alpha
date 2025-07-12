#!/bin/bash
# 🚀 QUICK START SCRIPT - One command to start development

echo "🚀 SQUEEZE ALPHA DEVELOPMENT MODE"
echo "=================================="
echo ""

# Check if we're in the right directory
if [[ ! -f "web_control.py" ]]; then
    echo "❌ Please run this from the ai-trading-system-complete directory"
    echo "   cd /Users/michaelmote/Desktop/ai-trading-system-complete"
    exit 1
fi

echo "📁 Current directory: $(pwd)"
echo "✅ Found system files"
echo ""

# Show menu
echo "Choose development mode:"
echo "1. 🌐 Start Local Web Interface (localhost:5000)"
echo "2. 🧠 Run AI Analysis Now"
echo "3. 🤖 Run System Evolution Analysis"
echo "4. 📱 Test Slack Notifications"
echo "5. 📊 Check Portfolio Data"
echo "6. 🎛️ System Control Panel"
echo "7. 📋 Show All Files"
echo "8. 🛠️ Open in VS Code (if installed)"
echo ""

read -p "Enter choice (1-8): " choice

case $choice in
    1)
        echo "🌐 Starting local web interface..."
        echo "📱 Open browser to: http://localhost:5000"
        python3 web_control.py
        ;;
    2)
        echo "🧠 Running AI consensus analysis..."
        python3 multi_ai_consensus_engine.py
        ;;
    3)
        echo "🤖 Running system evolution analysis..."
        python3 system_evolution_engine.py
        ;;
    4)
        echo "📱 Testing Slack notifications..."
        python3 test_slack_simple.py
        ;;
    5)
        echo "📊 Checking portfolio data..."
        python3 -c "
from web_control import WebControlInterface
web = WebControlInterface()
portfolio = web.get_portfolio_data()
print(f'Portfolio Value: \${portfolio[\"total_value\"]:,.2f}')
print(f'Today\\'s P&L: \${portfolio[\"total_change\"]:+,.2f}')
for holding in portfolio['holdings']:
    print(f'  {holding[\"ticker\"]}: \${holding[\"price\"]:.2f} ({holding[\"change_percent\"]:+.1f}%)')
"
        ;;
    6)
        echo "🎛️ Starting system control panel..."
        python3 system_control.py
        ;;
    7)
        echo "📋 System files:"
        ls -la *.py *.md *.txt 2>/dev/null
        echo ""
        echo "📁 Key directories:"
        ls -la src/ templates/ logs/ 2>/dev/null
        ;;
    8)
        if command -v code &> /dev/null; then
            echo "🛠️ Opening in VS Code..."
            code .
        else
            echo "❌ VS Code not found. Install VS Code or use another editor."
        fi
        ;;
    *)
        echo "❌ Invalid choice. Please run again and choose 1-8."
        ;;
esac

echo ""
echo "🎯 For Claude development sessions:"
echo "   Just start Claude terminal from this directory!"
echo "   cd /Users/michaelmote/Desktop/ai-trading-system-complete"