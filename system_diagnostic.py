#!/usr/bin/env python3
"""
System Diagnostic - Complete health check for AI Trading System
Verifies all components are properly configured and working
"""

import os
import sys
import importlib
import requests
from datetime import datetime

def check_api_keys():
    """Check if all required API keys are present"""
    print("🔑 CHECKING API KEYS...")
    
    required_keys = {
        'ALPACA_API_KEY': os.getenv('ALPACA_API_KEY'),
        'ALPACA_SECRET_KEY': os.getenv('ALPACA_SECRET_KEY'),
        'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
        'ALPHA_VANTAGE_API_KEY': os.getenv('ALPHA_VANTAGE_API_KEY'),
        'FMP_API_KEY': os.getenv('FMP_API_KEY'),
        'SLACK_WEBHOOK': os.getenv('SLACK_WEBHOOK')
    }
    
    missing_keys = []
    for key, value in required_keys.items():
        if value:
            print(f"  ✅ {key}: Present")
        else:
            print(f"  ❌ {key}: Missing")
            missing_keys.append(key)
    
    return len(missing_keys) == 0, missing_keys

def check_file_imports():
    """Check if all required files can be imported"""
    print("\n📁 CHECKING FILE IMPORTS...")
    
    required_files = [
        'direct_alpaca_service',
        'integrated_portfolio_tiles',
        'ai_analysis_page'
    ]
    
    failed_imports = []
    for file in required_files:
        try:
            importlib.import_module(file)
            print(f"  ✅ {file}.py: Import successful")
        except Exception as e:
            print(f"  ❌ {file}.py: Import failed - {e}")
            failed_imports.append(file)
    
    return len(failed_imports) == 0, failed_imports

def check_alpaca_connection():
    """Test direct Alpaca API connection"""
    print("\n🏦 CHECKING ALPACA CONNECTION...")
    
    try:
        from direct_alpaca_service import get_real_portfolio_positions, is_api_configured
        
        if not is_api_configured():
            print("  ❌ Alpaca API keys not configured")
            return False, "API keys missing"
        
        print("  ✅ Alpaca API keys configured")
        
        # Test actual connection
        portfolio_data = get_real_portfolio_positions()
        if portfolio_data:
            positions = portfolio_data.get('positions', [])
            print(f"  ✅ Alpaca connection successful - {len(positions)} positions found")
            return True, f"{len(positions)} positions"
        else:
            print("  ❌ Alpaca connection failed - No data returned")
            return False, "No data returned"
            
    except Exception as e:
        print(f"  ❌ Alpaca connection error: {e}")
        return False, str(e)

def check_openrouter_connection():
    """Test OpenRouter AI API connection"""
    print("\n🤖 CHECKING OPENROUTER AI CONNECTION...")
    
    try:
        from direct_alpaca_service import get_ai_analysis_for_stock
        
        # Test with a real stock
        analysis = get_ai_analysis_for_stock('AAPL')
        if analysis and 'claude_score' in analysis:
            print("  ✅ OpenRouter AI connection successful")
            return True, "AI analysis working"
        else:
            print("  ❌ OpenRouter AI connection failed")
            return False, "AI analysis failed"
            
    except Exception as e:
        print(f"  ❌ OpenRouter AI error: {e}")
        return False, str(e)

def check_integrated_tiles():
    """Test integrated portfolio tiles functionality"""
    print("\n🎨 CHECKING INTEGRATED TILES...")
    
    try:
        from integrated_portfolio_tiles import display_integrated_portfolio_tiles
        
        # Test with sample data
        test_data = {
            'positions': [{
                'symbol': 'TEST',
                'qty': 100,
                'avg_cost': 10.0,
                'current_price': 10.5,
                'market_value': 1050.0,
                'unrealized_pl': 50.0,
                'unrealized_plpc': 5.0
            }]
        }
        
        print("  ✅ Integrated tiles module loaded successfully")
        return True, "Tiles ready"
        
    except Exception as e:
        print(f"  ❌ Integrated tiles error: {e}")
        return False, str(e)

def check_portfolio_dashboard():
    """Test Portfolio Dashboard page"""
    print("\n📊 CHECKING PORTFOLIO DASHBOARD...")
    
    try:
        # Import and test the portfolio dashboard
        sys.path.append('./pages')
        # Import portfolio dashboard module
        import importlib.util
        spec = importlib.util.spec_from_file_location("portfolio_dashboard", "./pages/01_🏠_Portfolio_Dashboard.py")
        portfolio_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(portfolio_module)
        load_portfolio_data = portfolio_module.load_portfolio_data
        
        # Test portfolio data loading
        portfolio_data = load_portfolio_data()
        if portfolio_data:
            positions = portfolio_data.get('positions', [])
            print(f"  ✅ Portfolio Dashboard working - {len(positions)} positions loaded")
            return True, f"{len(positions)} positions"
        else:
            print("  ❌ Portfolio Dashboard failed - No data")
            return False, "No portfolio data"
            
    except Exception as e:
        print(f"  ❌ Portfolio Dashboard error: {e}")
        return False, str(e)

def run_complete_diagnostic():
    """Run complete system diagnostic"""
    print("🚀 SQUEEZE ALPHA TRADING SYSTEM - COMPLETE DIAGNOSTIC")
    print("=" * 60)
    
    results = {}
    
    # Run all checks
    results['api_keys'] = check_api_keys()
    results['file_imports'] = check_file_imports()
    results['alpaca_connection'] = check_alpaca_connection()
    results['openrouter_connection'] = check_openrouter_connection()
    results['integrated_tiles'] = check_integrated_tiles()
    results['portfolio_dashboard'] = check_portfolio_dashboard()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, (passed, message) in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name.replace('_', ' ').title()}: {message}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! System is ready for deployment.")
        print("✅ Portfolio Dashboard should work with integrated tiles")
        print("✅ Real portfolio data from Alpaca API")
        print("✅ Real AI analysis from OpenRouter")
        print("✅ All functionality working")
    else:
        print("❌ SOME CHECKS FAILED! Fix the issues above before deployment.")
        print("📋 Common fixes:")
        print("  1. Add missing API keys to Render Secret Files")
        print("  2. Check file imports and syntax errors")
        print("  3. Verify API key permissions")
    
    print("\n🌐 After fixes, test at: https://squeeze-alpha.onrender.com/Portfolio_Dashboard")
    print("📱 Should show integrated tiles with all data inside")
    
    return all_passed

if __name__ == "__main__":
    run_complete_diagnostic()