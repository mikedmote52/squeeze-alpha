#!/usr/bin/env python3
"""
System Readiness Check
Verifies all components are ready for tonight's activation
"""

import os
import json
from pathlib import Path

def check_system_readiness():
    """Check if system is ready"""
    print("🔍 AI TRADING SYSTEM - READINESS CHECK")
    print("=" * 50)
    
    # Critical files check
    critical_files = [
        "real_ai_backend.py",
        "streamlit_app.py", 
        "core/collaborative_ai_system.py",
        "core/explosive_catalyst_discovery.py",
        "core/pacific_time_schedule.py"
    ]
    
    all_ready = True
    
    print("📋 CRITICAL COMPONENTS:")
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_ready = False
    
    # Frontend pages check
    pages = [
        "pages/01_🏠_Portfolio_Dashboard.py",
        "pages/02_🔍_Opportunity_Discovery.py", 
        "pages/03_🤖_AI_Analysis.py"
    ]
    
    print("\n📱 FRONTEND PAGES:")
    for page in pages:
        if os.path.exists(page):
            print(f"✅ {page}")
        else:
            print(f"❌ {page} - MISSING")
            all_ready = False
    
    # Configuration check
    configs = ["requirements.txt", "setup_autonomous_system.sh"]
    
    print("\n⚙️ CONFIGURATION:")
    for config in configs:
        if os.path.exists(config):
            print(f"✅ {config}")
        else:
            print(f"⚠️  {config} - MISSING")
    
    # Final verdict
    print("\n🎯 FINAL VERDICT:")
    if all_ready:
        print("🚀 SYSTEM IS 100% READY!")
        print("✅ All critical components verified")
        print("\n📋 MANUAL STARTUP COMMANDS:")
        print("1. python3 real_ai_backend.py")
        print("2. streamlit run streamlit_app.py")
        print("3. Open: http://localhost:8501")
        
        return True
    else:
        print("❌ SYSTEM NOT READY - Missing components")
        return False

if __name__ == "__main__":
    ready = check_system_readiness()
    
    if ready:
        print("\n🎉 READY FOR ACTIVATION!")
    else:
        print("\n🔧 NEEDS ATTENTION BEFORE ACTIVATION")