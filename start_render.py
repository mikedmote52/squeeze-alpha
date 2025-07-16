#!/usr/bin/env python3
"""
Render deployment script - Run Streamlit app with embedded backend
"""

import os
import subprocess
import sys
import threading
import time

def start_backend():
    """Start the FastAPI backend in a separate thread"""
    try:
        print("🔧 Starting FastAPI backend...")
        # Run the real backend on port 8000
        subprocess.run([
            "python", "-m", "uvicorn", 
            "real_ai_backend:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload", "false"
        ], check=False)  # Don't exit if backend fails
    except Exception as e:
        print(f"⚠️ Backend failed: {e}")

def main():
    """Start both backend and Streamlit app"""
    
    # Set port from environment (Render provides this)
    port = int(os.environ.get("PORT", 8501))
    
    print(f"🚀 Starting AI Trading System on port {port}")
    print("📊 Full system with backend and frontend")
    
    # Start backend in background thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(5)
    
    # Set backend URL for Streamlit
    os.environ["BACKEND_URL"] = "http://localhost:8000"
    
    # Run Streamlit app on the main port
    try:
        subprocess.run([
            "streamlit", 
            "run", 
            "streamlit_app.py", 
            "--server.port", str(port),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()