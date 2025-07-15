#!/usr/bin/env python3
"""
Start Trading System
Launches all components for the trading day
"""

import os
import sys
import asyncio
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check environment variables
    required_vars = ['ALPACA_API_KEY', 'ALPACA_SECRET_KEY', 'OPENROUTER_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables found")
    
    # Check if ports are available
    try:
        import socket
        
        # Check if port 8000 (backend) is available
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("⚠️  Port 8000 already in use - backend may already be running")
        else:
            print("✅ Port 8000 available for backend")
            
        # Check if port 8501 (streamlit) is available  
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8501))
        sock.close()
        
        if result == 0:
            print("⚠️  Port 8501 already in use - frontend may already be running")
        else:
            print("✅ Port 8501 available for frontend")
            
    except Exception as e:
        print(f"⚠️  Could not check ports: {e}")
    
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend (FastAPI)...")
    
    try:
        # Start backend with environment variables
        env = os.environ.copy()
        backend_process = subprocess.Popen(
            ['python3', 'real_ai_backend.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give backend time to start
        time.sleep(3)
        
        # Check if backend is running
        if backend_process.poll() is None:
            print("✅ Backend started successfully on http://localhost:8000")
            return backend_process
        else:
            stdout, stderr = backend_process.communicate()
            print(f"❌ Backend failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎨 Starting frontend (Streamlit)...")
    
    try:
        # Start streamlit
        frontend_process = subprocess.Popen(
            ['streamlit', 'run', 'streamlit_app.py', '--server.port=8501', '--server.headless=true'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give frontend time to start
        time.sleep(5)
        
        # Check if frontend is running
        if frontend_process.poll() is None:
            print("✅ Frontend started successfully on http://localhost:8501")
            return frontend_process
        else:
            stdout, stderr = frontend_process.communicate()
            print(f"❌ Frontend failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def initialize_ai_baselines():
    """Initialize AI baselines for faster loading"""
    print("🧠 Initializing AI baselines...")
    
    try:
        sys.path.append('./core')
        from ai_baseline_cache_system import ai_baseline_cache
        
        # Initialize the baseline system
        print("✅ AI baseline cache system ready")
        print("✅ System will prevent 'Loading...' states")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize AI baselines: {e}")
        return False

def display_schedule():
    """Display today's schedule"""
    schedule = [
        ("5:15 AM PT", "Preemptive Analysis - Pre-market"),
        ("5:45 AM PT", "Premarket Brief (Slack notification)"),
        ("6:15 AM PT", "Preemptive Analysis - Market Open"),
        ("6:45 AM PT", "Market Open Pulse (Slack notification)"),
        ("9:30 AM PT", "Midday Pulse (Slack notification)"),
        ("10:15 AM PT", "Preemptive Analysis - Midday"),
        ("12:45 PM PT", "End-of-Day Wrap (Slack notification)"),
        ("1:30 PM PT", "After-Hours Learning (Slack notification)")
    ]
    
    print(f"\n📅 Today's Trading Schedule:")
    for time, event in schedule:
        print(f"  🕐 {time} - {event}")
    
    print(f"\n💡 Notes:")
    print(f"  • Preemptive analysis runs before each major cycle")
    print(f"  • All results are cached to prevent loading delays")
    print(f"  • Analysis results are stored for trend tracking")
    print(f"  • System identifies replacement candidates and new opportunities")

def main():
    """Main startup sequence"""
    print("🔥 AI Trading System Startup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please fix issues and try again.")
        return
    
    print("\n🚀 Starting system components...")
    
    # Start backend
    backend = start_backend()
    if not backend:
        print("❌ Cannot continue without backend")
        return
    
    # Start frontend  
    frontend = start_frontend()
    if not frontend:
        print("⚠️  Frontend failed to start, but backend is running")
    
    # Initialize AI systems
    initialize_ai_baselines()
    
    # Display schedule
    display_schedule()
    
    # Final status
    print("\n" + "=" * 50)
    print("🎯 SYSTEM STARTUP COMPLETE!")
    print(f"📈 Backend: http://localhost:8000")
    if frontend:
        print(f"🖥️  Frontend: http://localhost:8501")
    print(f"⏰ Current PT: {datetime.now().strftime('%I:%M %p')}")
    
    # Slack notification note
    slack_webhook = os.getenv('SLACK_WEBHOOK')
    if slack_webhook:
        print(f"📱 Slack: Webhook configured (may need token refresh)")
    else:
        print(f"📱 Slack: Not configured")
    
    print(f"\n✅ Ready for trading! System will handle notifications automatically.")
    print(f"💤 You can now close this terminal - services are running in background.")

if __name__ == "__main__":
    main()