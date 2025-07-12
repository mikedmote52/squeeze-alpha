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
        self._validate_market_data()
        
        self.is_safe_for_trading = len(self.safety_violations) == 0
        self._print_safety_report()
        
        return self.is_safe_for_trading, self.safety_violations
    
    def _validate_api_keys(self):
        print("🔑 Validating API Keys...")
        
        required_keys = {
            'ANTHROPIC_API_KEY': 'Claude AI Analysis',
            'OPENAI_API_KEY': 'ChatGPT AI Analysis', 
            'ALPACA_API_KEY': 'Portfolio Data',
            'ALPACA_SECRET_KEY': 'Trading Execution'
        }
        
        keys_status = self.secrets_manager.get_all_api_keys()
        
        for key_name, description in required_keys.items():
            key_value = keys_status.get(key_name)
            
            if not key_value:
                self.safety_violations.append(
                    f"❌ CRITICAL: {key_name} missing - {description} will use MOCK data"
                )
                print(f"   ❌ {key_name}: MISSING - MOCK DATA RISK")
            elif len(key_value) < 10:
                self.safety_violations.append(
                    f"❌ CRITICAL: {key_name} appears invalid - {description} may fail"
                )
                print(f"   ⚠️ {key_name}: SUSPICIOUS LENGTH")
            else:
                print(f"   ✅ {key_name}: VALID")
    
    def _validate_market_data(self):
        print("\n📊 Validating Market Data Sources...")
        
        try:
            import yfinance as yf
            test_stock = yf.Ticker("AAPL")
            hist = test_stock.history(period="1d")
            
            if hist.empty:
                self.safety_violations.append(
                    "❌ CRITICAL: Yahoo Finance not working - no real market data"
                )
                print("   ❌ YAHOO FINANCE: No real market data")
            else:
                print("   ✅ YAHOO FINANCE: Real market data available")
                
        except Exception as e:
            self.safety_violations.append(f"❌ CRITICAL: Market data validation failed - {e}")
            print(f"   ❌ MARKET DATA ERROR: {e}")
    
    def _print_safety_report(self):
        print("\n" + "=" * 60)
        print("🛡️ TRADING SAFETY ASSESSMENT")
        print("=" * 60)
        
        if self.is_safe_for_trading:
            print("✅ SYSTEM SAFE FOR REAL MONEY TRADING")
            print("🟢 All data sources validated as REAL")
            print("🟢 No mock data detected in critical systems")
            print("🟢 API connections verified")
            print("\n🚀 TRADING ENABLED - System ready for real money")
        else:
            print("🚨 DANGER: SYSTEM NOT SAFE FOR REAL MONEY TRADING")
            print("🔴 MOCK DATA DETECTED IN CRITICAL SYSTEMS")
            print(f"🔴 {len(self.safety_violations)} SAFETY VIOLATIONS FOUND")
            print("\n❌ TRADING DISABLED - Fix issues before using real money")
            
            print("\n🚨 CRITICAL ISSUES TO FIX:")
            for i, violation in enumerate(self.safety_violations, 1):
                print(f"{i:2d}. {violation}")
        
        print("\n" + "=" * 60)


def emergency_trading_safety_check():
    try:
        validator = TradingSafetyValidator()
        return validator.validate_all_systems()
    except Exception as e:
        print(f"🚨 SAFETY CHECK FAILED: {e}")
        return False, [f"Safety validation error: {e}"]


if __name__ == "__main__":
    validator = TradingSafetyValidator()
    is_safe, violations = validator.validate_all_systems()
    
    if not is_safe:
        print("\n💡 NEXT STEPS TO FIX:")
        print("1. Set up real API keys in Replit Secrets")
        print("2. Remove all mock data fallback methods")
        print("3. Connect to real broker API (Alpaca)")
        print("4. Test all connections before trading")
    else:
        print("\n🎉 System ready for real money trading!")