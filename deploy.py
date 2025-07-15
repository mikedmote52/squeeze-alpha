#!/usr/bin/env python3
"""
Automated Deployment Script for AI Trading System
Run this to deploy both frontend and backend automatically
"""

import subprocess
import os
import sys
import json
import time
from pathlib import Path

def run_command(cmd, cwd=None, capture_output=False):
    """Run a shell command with error handling"""
    print(f"Running: {cmd}")
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
            return result.stdout.strip(), result.stderr.strip()
        else:
            subprocess.run(cmd, shell=True, cwd=cwd, check=True)
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e}")
        return False

def check_dependencies():
    """Check if required tools are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Node.js
    stdout, stderr = run_command("node --version", capture_output=True)
    if not stdout:
        print("❌ Node.js not found. Please install Node.js 16+")
        return False
    print(f"✅ Node.js: {stdout}")
    
    # Check Python
    stdout, stderr = run_command("python3 --version", capture_output=True)
    if not stdout:
        print("❌ Python3 not found. Please install Python 3.8+")
        return False
    print(f"✅ Python: {stdout}")
    
    return True

def setup_backend():
    """Set up Python backend"""
    print("🐍 Setting up Python backend...")
    
    # Install required packages
    packages = [
        "fastapi",
        "uvicorn",
        "yfinance", 
        "requests",
        "beautifulsoup4",
        "aiohttp",
        "python-multipart",
        "python-dotenv"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        if not run_command(f"pip3 install {package}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    
    print("✅ Backend setup complete!")

def setup_frontend():
    """Set up React frontend"""
    print("⚛️  Setting up React frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install dependencies
    if not run_command("npm install", cwd=frontend_dir):
        print("❌ Failed to install frontend dependencies")
        return False
    
    # Create .env file if it doesn't exist
    env_file = frontend_dir / ".env"
    if not env_file.exists():
        env_example = frontend_dir / ".env.example"
        if env_example.exists():
            with open(env_example) as f:
                env_content = f.read()
            
            with open(env_file, "w") as f:
                f.write(env_content)
            
            print("📝 Created .env file from .env.example")
            print("⚠️  Please edit frontend/.env with your API keys!")
        else:
            # Create basic .env
            basic_env = """# API Configuration
REACT_APP_API_URL=http://localhost:3000
REACT_APP_PYTHON_BACKEND_URL=http://localhost:8000

# WebSocket Configuration  
REACT_APP_WS_URL=ws://localhost:8000/ws

# Debug Mode
REACT_APP_DEBUG=true
"""
            with open(env_file, "w") as f:
                f.write(basic_env)
            print("📝 Created basic .env file")
    
    print("✅ Frontend setup complete!")
    return True

def start_backend():
    """Start the Python backend server"""
    print("🚀 Starting Python backend...")
    
    # Start the API server in background
    try:
        backend_process = subprocess.Popen([
            "python3", "-c", 
            """
import uvicorn
from api_endpoints import app
print('🔥 Backend starting on http://localhost:8000')
uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)
"""
        ])
        
        # Give it time to start
        time.sleep(3)
        
        # Check if it's running
        stdout, stderr = run_command("curl -s http://localhost:8000/docs", capture_output=True)
        if "FastAPI" in stdout or "swagger" in stdout.lower():
            print("✅ Backend started successfully!")
            print("📚 API docs: http://localhost:8000/docs")
            return backend_process
        else:
            print("⚠️  Backend may not be fully ready yet...")
            return backend_process
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the React frontend"""
    print("🌐 Starting React frontend...")
    
    frontend_dir = Path("frontend")
    
    try:
        frontend_process = subprocess.Popen([
            "npm", "start"
        ], cwd=frontend_dir)
        
        print("✅ Frontend starting on http://localhost:3000")
        print("⏳ This may take 30-60 seconds to compile...")
        
        return frontend_process
        
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main deployment function"""
    print("🚀 AI Trading System - Automated Deployment")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup backend
    setup_backend()
    
    # Setup frontend  
    if not setup_frontend():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎯 Starting services...")
    
    # Start backend
    backend_proc = start_backend()
    if not backend_proc:
        print("❌ Could not start backend")
        sys.exit(1)
    
    # Start frontend
    frontend_proc = start_frontend()
    if not frontend_proc:
        print("❌ Could not start frontend")
        backend_proc.terminate()
        sys.exit(1)
    
    print("\n" + "🎉" * 20)
    print("🎉 DEPLOYMENT SUCCESSFUL! 🎉")
    print("🎉" * 20)
    print("\n📍 Your AI Trading System is running:")
    print("   🌐 Frontend:  http://localhost:3000")
    print("   🐍 Backend:   http://localhost:8000")
    print("   📚 API Docs:  http://localhost:8000/docs")
    print("\n⚠️  Important:")
    print("   • Edit frontend/.env with your real API keys")
    print("   • Both servers are running in development mode")
    print("   • Press Ctrl+C to stop both services")
    
    print("\n⏳ Services starting... Check the URLs above in 1-2 minutes")
    
    try:
        # Keep both processes running
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("✅ Services stopped")

if __name__ == "__main__":
    main()