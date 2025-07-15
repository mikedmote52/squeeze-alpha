#!/bin/bash

# AI Trading System - Tonight's Startup Script
echo "🚀 AI TRADING SYSTEM - STARTING FOR TONIGHT'S VERIFICATION"
echo "================================================================"

# Find Python executable
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Python not found. Please install Python 3."
    exit 1
fi

echo "✅ Using Python: $PYTHON"

# Check if we're in the right directory
if [ ! -f "real_ai_backend.py" ]; then
    echo "❌ Not in AI trading system directory"
    echo "💡 Navigate to: cd /Users/michaelmote/Desktop/ai-trading-system-complete"
    exit 1
fi

echo "📁 In correct directory: $(pwd)"

# Step 1: Start the backend
echo ""
echo "🔧 STEP 1: Starting AI Backend..."
echo "Starting backend on port 8000..."

# Kill any existing backend processes
pkill -f "real_ai_backend.py" 2>/dev/null || true
sleep 2

# Start backend in background
nohup $PYTHON real_ai_backend.py > backend_tonight.log 2>&1 &
BACKEND_PID=$!

echo "Backend started with PID: $BACKEND_PID"
echo "Waiting for backend to initialize..."
sleep 5

# Check if backend is responding
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend is responding on http://localhost:8000"
else
    echo "⚠️  Backend may still be starting up..."
fi

# Step 2: Start Streamlit
echo ""
echo "📱 STEP 2: Starting Streamlit Frontend..."
echo "Starting Streamlit on port 8501..."

# Kill any existing Streamlit processes
pkill -f "streamlit" 2>/dev/null || true
sleep 2

# Start Streamlit in background
nohup $PYTHON -m streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 > streamlit_tonight.log 2>&1 &
STREAMLIT_PID=$!

echo "Streamlit started with PID: $STREAMLIT_PID"
echo "Waiting for Streamlit to initialize..."
sleep 8

# Step 3: Show access information
echo ""
echo "🌐 SYSTEM ACCESS INFORMATION"
echo "================================"

# Get local IP address
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo "📱 MOBILE ACCESS:"
echo "   Local: http://localhost:8501"
if [ ! -z "$LOCAL_IP" ]; then
    echo "   Network: http://$LOCAL_IP:8501"
fi

echo ""
echo "🌐 WEB ACCESS:"
echo "   Backend API: http://localhost:8000"
echo "   Frontend: http://localhost:8501"

# Step 4: Test system
echo ""
echo "🧪 STEP 3: Testing System..."

# Test backend
echo "Testing backend connection..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend: WORKING"
else
    echo "❌ Backend: NOT RESPONDING"
    echo "💡 Check backend_tonight.log for errors"
fi

# Test Streamlit
echo "Testing Streamlit connection..."
if curl -s http://localhost:8501/ > /dev/null 2>&1; then
    echo "✅ Streamlit: WORKING"
else
    echo "❌ Streamlit: NOT RESPONDING"
    echo "💡 Check streamlit_tonight.log for errors"
fi

# Step 5: Instructions
echo ""
echo "🎯 VERIFICATION INSTRUCTIONS"
echo "============================"
echo ""
echo "1. 📱 TEST MOBILE ACCESS:"
echo "   - Open phone browser"
echo "   - Go to: http://$LOCAL_IP:8501"
echo "   - Verify portfolio tiles load"
echo ""
echo "2. 🤖 TEST AI ANALYSIS:"
echo "   - Go to 'AI Analysis' page"
echo "   - Enter ticker: SAVA"
echo "   - Watch collaborative AI discussion"
echo "   - Verify no large-cap stocks recommended"
echo ""
echo "3. 🔍 TEST OPPORTUNITY DISCOVERY:"
echo "   - Go to 'Opportunity Discovery' page"
echo "   - Check for explosive catalyst opportunities"
echo "   - Verify small/mid-cap focus"
echo ""
echo "4. 💼 TEST PORTFOLIO:"
echo "   - Go to 'Portfolio Dashboard'"
echo "   - Check iPhone-style tiles"
echo "   - Test optimization recommendations"

echo ""
echo "🔄 AUTOMATED SCHEDULING"
echo "======================="
echo "To enable automated morning analysis:"
echo "   ./setup_autonomous_system.sh"
echo "   Choose option 1 for LaunchAgent"

echo ""
echo "🛑 TO STOP SYSTEM"
echo "================"
echo "   kill $BACKEND_PID    # Stop backend"
echo "   kill $STREAMLIT_PID  # Stop Streamlit"
echo "   Or run: pkill -f 'real_ai_backend|streamlit'"

echo ""
echo "📊 LOG FILES"
echo "============"
echo "   Backend logs: tail -f backend_tonight.log"
echo "   Streamlit logs: tail -f streamlit_tonight.log"

echo ""
echo "🎉 SYSTEM STARTED!"
echo "=================="
echo "✅ Backend running on port 8000"
echo "✅ Frontend running on port 8501"
echo "🚀 Ready for verification and tomorrow's trading!"

# Save process IDs for easy management
echo "BACKEND_PID=$BACKEND_PID" > system_pids.txt
echo "STREAMLIT_PID=$STREAMLIT_PID" >> system_pids.txt
echo "STARTED_AT=$(date)" >> system_pids.txt

echo ""
echo "💾 Process IDs saved to: system_pids.txt"