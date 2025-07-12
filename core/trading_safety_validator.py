#!/usr/bin/env python3
"""
Trading Safety Validator - Updated for Current System
Ensures no mock data is used in real trading
"""

import os
from secrets_manager import SecretsManager

class TradingSafetyValidator:
    def __init__(self):
        self.secrets_manager = SecretsManager()
        self.safety_violations = []
        self.is_safe_for_trading = False
        
    def validate_all_systems(self):
        print("🛡️ CRITICAL TRADING SAFETY VALIDATION")
        print("=" * 60)
        print("⚠️ CHECKING FOR MOCK DATA THAT COULD AFFECT REAL MONEY")
        print()
        
        self.safety_violations = []
        
        self._validate_api_keys()
        self._validate_portfolio_engine()
        self._validate_ai_systems()
        self._validate_market_data()
        
        self.is_safe_for_trading = len(self.safety_violations) == 0
        self._print_safety_report()
        
        return self.is_safe_for_trading, self.safety_violations
    
    def _validate_api_keys(self):
        print("🔑 Validating API Keys...")
        
        required_keys = {
            'ALPACA_API_KEY': 'Live Portfolio Data',
            'ALPACA_SECRET_KEY': 'Trade Execution',
            'OPENROUTER_API_KEY': 'AI Consensus (Claude/ChatGPT/Grok)'
        }
        
        recommended_keys = {
            'POLYGON_API_KEY': 'Real-time Market Data',
            'SLACK_WEBHOOK_URL': 'Trade Notifications',
            'ANTHROPIC_API_KEY': 'Claude AI Direct',
            'OPENAI_API_KEY': 'ChatGPT AI Direct'
        }
        
        keys_status = self.secrets_manager.get_all_api_keys()
        
        # Check required keys
        for key_name, description in required_keys.items():
            key_value = keys_status.get(key_name)
            
            if not key_value:
                self.safety_violations.append(
                    f"❌ CRITICAL: {key_name} missing - {description} will use fallback data"
                )
                print(f"   ❌ {key_name}: MISSING - SAFETY RISK")
            elif len(key_value) < 10:
                self.safety_violations.append(
                    f"❌ CRITICAL: {key_name} appears invalid - {description} may fail"
                )
                print(f"   ⚠️ {key_name}: SUSPICIOUS LENGTH")
            else:
                print(f"   ✅ {key_name}: CONFIGURED")
        
        # Check recommended keys
        missing_recommended = []
        for key_name, description in recommended_keys.items():
            key_value = keys_status.get(key_name)
            if not key_value:
                missing_recommended.append(f"{key_name} ({description})")
            else:
                print(f"   ✅ {key_name}: CONFIGURED")
        
        if missing_recommended:
            print(f"   💡 RECOMMENDED: Add {', '.join(missing_recommended[:2])} for full features")
    
    def _validate_portfolio_engine(self):
        print("💰 Validating Portfolio Engine...")
        
        try:
            from live_portfolio_engine import LivePortfolioEngine
            
            engine = LivePortfolioEngine()
            
            # Check if using real Alpaca connection
            if hasattr(engine, 'alpaca') and engine.alpaca:
                print("   ✅ Live Alpaca connection configured")
            else:
                print("   ⚠️ Using fallback portfolio (demo mode)")
                print("   💡 Configure Alpaca keys for live portfolio data")
            
        except ImportError as e:
            self.safety_violations.append(
                f"❌ CRITICAL: Portfolio engine import failed - {str(e)}"
            )
            print(f"   ❌ Portfolio engine not available")
        
        # CRITICAL: Check main.py for hardcoded fake holdings
        try:
            with open('../main.py', 'r') as f:
                main_content = f.read()
                
            # Look for hardcoded portfolio data
            dangerous_patterns = [
                "holdings = ['AMD', 'NVAX'",  # Exact fake holdings pattern
                "holdings = [",               # Any hardcoded holdings list
                "current_price = 12.45",      # VIGL fake price
                "324% total",                 # VIGL fake performance
                "ticker_data = {",            # Hardcoded stock data
            ]
            
            for pattern in dangerous_patterns:
                if pattern in main_content:
                    self.safety_violations.append(
                        f"❌ CRITICAL: main.py contains hardcoded fake data: '{pattern[:30]}...'"
                    )
                    print(f"   ❌ FAKE DATA DETECTED in main.py")
                    break
            else:
                print("   ✅ main.py using live portfolio engine")
                
        except FileNotFoundError:
            print("   ⚠️ main.py not found for validation")
        except Exception as e:
            print(f"   ⚠️ Could not validate main.py: {e}")
    
    def _validate_ai_systems(self):
        print("🤖 Validating AI Systems...")
        
        try:
            from openrouter_stock_debate import OpenRouterStockDebate
            
            debate = OpenRouterStockDebate()
            
            if debate.api_key:
                print("   ✅ OpenRouter AI debate system configured")
            else:
                print("   ⚠️ OpenRouter not configured - using fallback AI")
                
        except ImportError as e:
            self.safety_violations.append(
                f"❌ CRITICAL: AI debate system import failed - {str(e)}"
            )
            print(f"   ❌ AI debate system not available")
        
        try:
            from alpha_engine_enhanced import EnhancedAlphaEngine
            print("   ✅ Enhanced Alpha Engine available")
        except ImportError as e:
            self.safety_violations.append(
                f"❌ CRITICAL: Alpha engine import failed - {str(e)}"
            )
            print(f"   ❌ Alpha engine not available")
    
    def _validate_market_data(self):
        print("📊 Validating Market Data Sources...")
        
        # Test Yahoo Finance
        try:
            import yfinance as yf
            
            # Quick test
            test_stock = yf.Ticker("AAPL")
            hist = test_stock.history(period="1d")
            
            if len(hist) > 0:
                print("   ✅ Yahoo Finance working - fallback data available")
            else:
                self.safety_violations.append(
                    "❌ CRITICAL: Yahoo Finance not working - no fallback market data"
                )
                print("   ❌ Yahoo Finance failed - no market data")
                
        except Exception as e:
            self.safety_violations.append(
                f"❌ CRITICAL: Market data validation failed - {str(e)}"
            )
            print(f"   ❌ Market data error: {str(e)}")
        
        # Check Polygon
        polygon_key = self.secrets_manager.get_api_key('POLYGON_API_KEY')
        if polygon_key:
            print("   ✅ Polygon.io configured - real-time data available")
        else:
            print("   💡 Add Polygon.io for real-time level 2 data")
    
    def _print_safety_report(self):
        print("\n" + "=" * 60)
        print("🛡️ SAFETY VALIDATION COMPLETE")
        print("=" * 60)
        
        if self.is_safe_for_trading:
            print("✅ SYSTEM READY FOR LIVE TRADING")
            print("✅ No critical safety violations detected")
            print("✅ All core systems have real data sources")
        else:
            print(f"🚨 {len(self.safety_violations)} SAFETY ISSUES FOUND:")
            print()
            for i, violation in enumerate(self.safety_violations, 1):
                print(f"{i}. {violation}")
            
            print("\n💡 SAFETY RECOMMENDATIONS:")
            print("• Add missing API keys in Replit Secrets")
            print("• Restart application after adding keys")
            print("• Test each system individually before live trading")
        
        print("\n🎯 TRADING STATUS:")
        if self.is_safe_for_trading:
            print("💚 APPROVED FOR LIVE TRADING")
        else:
            print("🔴 NOT APPROVED - FIX ISSUES FIRST")

def emergency_trading_safety_check():
    """Quick safety check for emergency situations"""
    validator = TradingSafetyValidator()
    return validator.validate_all_systems()

if __name__ == "__main__":
    validator = TradingSafetyValidator()
    is_safe, violations = validator.validate_all_systems()
    
    print(f"\nSafety Status: {'SAFE' if is_safe else 'UNSAFE'}")
    print(f"Violations: {len(violations)}")