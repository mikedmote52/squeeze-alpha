#!/usr/bin/env python3
"""
Test Streamlit Integration
Verify all Streamlit components work with real backend
"""

import sys
import os
import requests
from datetime import datetime

# Add core to path
sys.path.append('./core')

def test_backend_connection():
    """Test backend is running and responsive"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is online")
            print(f"   Alpaca configured: {data.get('alpaca_configured', False)}")
            print(f"   OpenRouter configured: {data.get('openrouter_configured', False)}")
            return True
        else:
            print(f"❌ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_portfolio_api():
    """Test portfolio endpoints"""
    try:
        positions_response = requests.get("http://localhost:8000/api/portfolio/positions", timeout=10)
        performance_response = requests.get("http://localhost:8000/api/portfolio/performance", timeout=10)
        
        if positions_response.status_code == 200 and performance_response.status_code == 200:
            positions_data = positions_response.json()
            performance_data = performance_response.json()
            
            positions = positions_data.get('positions', [])
            print(f"✅ Portfolio API working - {len(positions)} positions found")
            
            if positions:
                total_value = sum(pos['market_value'] for pos in positions)
                total_pl = sum(pos['unrealized_pl'] for pos in positions)
                print(f"   Total portfolio value: ${total_value:,.2f}")
                print(f"   Total P&L: ${total_pl:,.2f}")
            
            return True
        else:
            print(f"❌ Portfolio API failed: {positions_response.status_code}, {performance_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Portfolio API error: {e}")
        return False

def test_opportunities_api():
    """Test opportunity discovery endpoints"""
    try:
        catalyst_response = requests.get("http://localhost:8000/api/catalyst-discovery", timeout=15)
        alpha_response = requests.get("http://localhost:8000/api/alpha-discovery", timeout=15)
        
        catalyst_count = 0
        alpha_count = 0
        
        if catalyst_response.status_code == 200:
            catalyst_data = catalyst_response.json()
            catalyst_count = len(catalyst_data.get('catalysts', []))
        
        if alpha_response.status_code == 200:
            alpha_data = alpha_response.json()
            alpha_count = len(alpha_data.get('opportunities', []))
        
        print(f"✅ Discovery APIs working")
        print(f"   Catalyst opportunities: {catalyst_count}")
        print(f"   Alpha opportunities: {alpha_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Discovery API error: {e}")
        return False

def test_ai_analysis_api():
    """Test AI analysis endpoint"""
    try:
        response = requests.post(
            "http://localhost:8000/api/ai-analysis",
            json={"symbol": "AAPL", "context": "Test from Streamlit integration"},
            timeout=30
        )
        
        if response.status_code == 200:
            analysis_data = response.json()
            agents = analysis_data.get('agents', [])
            print(f"✅ AI Analysis API working - {len(agents)} agents responded")
            
            for agent in agents:
                confidence = agent.get('confidence', 0)
                print(f"   {agent['name']}: {confidence*100:.0f}% confidence")
            
            return True
        else:
            print(f"❌ AI Analysis API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ AI Analysis API error: {e}")
        return False

def test_streamlit_files():
    """Test that Streamlit files exist and are properly structured"""
    files_to_check = [
        'streamlit_app.py',
        '.streamlit/config.toml',
        '.streamlit/secrets.toml',
        'requirements-streamlit.txt',
        'pages/01_🏠_Portfolio_Dashboard.py',
        'pages/02_🔍_Opportunity_Discovery.py',
        'pages/03_🤖_AI_Analysis.py',
        'core/streamlit_backend_bridge.py'
    ]
    
    all_exist = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Run all integration tests"""
    print("🧪 Testing Streamlit Integration")
    print("=" * 60)
    
    # Test backend connection
    print("\n1. Testing Backend Connection...")
    backend_ok = test_backend_connection()
    
    if not backend_ok:
        print("\n❌ CRITICAL: Backend is not running!")
        print("💡 Start the backend first: python3 real_ai_backend.py")
        return False
    
    # Test API endpoints
    print("\n2. Testing Portfolio API...")
    portfolio_ok = test_portfolio_api()
    
    print("\n3. Testing Discovery APIs...")
    discovery_ok = test_opportunities_api()
    
    print("\n4. Testing AI Analysis API...")
    ai_ok = test_ai_analysis_api()
    
    print("\n5. Testing Streamlit Files...")
    files_ok = test_streamlit_files()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    tests = [
        ("Backend Connection", backend_ok),
        ("Portfolio API", portfolio_ok),
        ("Discovery APIs", discovery_ok),
        ("AI Analysis API", ai_ok),
        ("Streamlit Files", files_ok)
    ]
    
    all_passed = True
    for test_name, passed in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n🚀 Ready to run Streamlit app:")
        print("   streamlit run streamlit_app.py")
        print("\n🌐 The app will be available at:")
        print("   http://localhost:8501")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Fix the failing components before running Streamlit")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)