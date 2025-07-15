#!/usr/bin/env python3
"""
Start both backend and frontend for deployment
"""
import os
import subprocess
import threading
import time
import sys

def run_backend():
    """Run the FastAPI backend"""
    print("🚀 Starting backend with your API keys...")
    
    # Set environment variables for your API keys
    os.environ["ALPACA_API_KEY"] = os.getenv("ALPACA_API_KEY", "your_alpaca_key_here")
    os.environ["ALPACA_SECRET_KEY"] = os.getenv("ALPACA_SECRET_KEY", "your_alpaca_secret_here")
    os.environ["OPENROUTER_API_KEY"] = "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"
    os.environ["ALPHA_VANTAGE_API_KEY"] = "IN84O862OXIYYX8B"
    os.environ["FMP_API_KEY"] = "CA25ofSLfa1mBftG4L4oFQvKUwtlhRfU"
    os.environ["SLACK_WEBHOOK"] = "https://hooks.slack.com/services/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"
    
    # Run backend on port 8000
    subprocess.run([sys.executable, "real_ai_backend.py"])

def run_frontend():
    """Run the Streamlit frontend"""
    print("🌐 Starting frontend...")
    
    # Set backend URL to connect to local backend
    os.environ["BACKEND_URL"] = "http://localhost:8000"
    
    # Run frontend on the deployment port
    port = os.getenv("PORT", "8501")
    subprocess.run([
        "streamlit", "run", "streamlit_app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0"
    ])

if __name__ == "__main__":
    # If deployment PORT is set, run appropriate service
    if os.getenv("PORT"):
        # For render deployment - run backend on main port
        print("🚀 Production deployment - starting backend")
        run_backend()
    else:
        # For local development - run both
        print("🔧 Local development - starting both services")
        
        # Start backend in background
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Wait for backend to start
        time.sleep(5)
        
        # Start frontend
        run_frontend()