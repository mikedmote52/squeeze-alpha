#!/usr/bin/env python3
"""
Squeeze Alpha - AI Trading System Setup
Automated setup and verification script
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("🚀" + "="*60 + "🚀")
    print("    SQUEEZE ALPHA - AI TRADING SYSTEM SETUP")
    print("    Professional-grade AI trading platform")
    print("🚀" + "="*60 + "🚀")
    print()

def check_python_version():
    """Check Python version requirements"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - Compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("💡 Try: pip install --upgrade pip")
        return False

def create_env_file():
    """Create .env file from template"""
    print("\n⚙️ Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        # Copy template to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ Created .env file from template")
        print("📝 Edit .env file to add your API keys")
        return True
    else:
        print("❌ .env.example template not found")
        return False

def test_core_imports():
    """Test core module imports"""
    print("\n🧪 Testing core module imports...")
    
    test_modules = [
        "core.secrets_manager",
        "core.trading_safety_validator", 
        "core.live_portfolio_engine",
        "core.alpha_engine_enhanced",
        "core.openrouter_stock_debate"
    ]
    
    success_count = 0
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module}: {e}")
    
    print(f"\n📊 Import Results: {success_count}/{len(test_modules)} modules loaded")
    return success_count == len(test_modules)

async def test_api_connections():
    """Test API connections"""
    print("\n🔑 Testing API connections...")
    
    try:
        from core.secrets_manager import SecretsManager
        
        secrets = SecretsManager()
        keys = secrets.get_all_api_keys()
        
        configured_count = sum(1 for v in keys.values() if v)
        total_keys = len(keys)
        
        print(f"📊 API Keys: {configured_count}/{total_keys} configured")
        
        if configured_count >= 3:
            print("✅ Sufficient API keys for basic operation")
            return True
        else:
            print("⚠️ Add more API keys for full functionality")
            print("💡 Edit .env file to add missing keys")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

async def run_safety_check():
    """Run comprehensive safety validation"""
    print("\n🛡️ Running safety validation...")
    
    try:
        from core.trading_safety_validator import TradingSafetyValidator
        
        validator = TradingSafetyValidator()
        is_safe, violations = validator.validate_all_systems()
        
        if is_safe:
            print("✅ All safety checks passed")
            print("💚 System ready for operation")
            return True
        else:
            print(f"⚠️ {len(violations)} safety issues found:")
            for violation in violations[:3]:  # Show first 3
                print(f"   • {violation}")
            if len(violations) > 3:
                print(f"   ... and {len(violations) - 3} more")
            print("💡 Fix issues before live trading")
            return False
            
    except Exception as e:
        print(f"❌ Safety check failed: {e}")
        return False

def show_next_steps(all_tests_passed):
    """Show next steps after setup"""
    print("\n" + "="*60)
    print("🎯 SETUP COMPLETE")
    print("="*60)
    
    if all_tests_passed:
        print("✅ System is ready for operation!")
        print()
        print("🚀 Next Steps:")
        print("1. Edit .env file to add your API keys")
        print("2. Run: python main.py")
        print("3. Access web interface at: http://localhost:8080")
        print("4. Start with paper trading for safety")
        print()
        print("📚 Documentation:")
        print("• README.md - Complete system overview")
        print("• .env.example - API key setup guide")
        print("• core/ directory - Core modules documentation")
    else:
        print("⚠️ Setup completed with some issues")
        print()
        print("🔧 Fix These Issues:")
        print("1. Install missing dependencies")
        print("2. Add required API keys to .env")
        print("3. Re-run setup: python setup.py")
        print()
        print("🆘 Need Help?")
        print("• Check README.md for detailed instructions")
        print("• Review error messages above")
        print("• Create GitHub issue for support")
    
    print("\n🛡️ Safety Reminder:")
    print("• ALWAYS use paper trading for testing")
    print("• Never trade with real money until fully tested")
    print("• Monitor all system behavior closely")
    
    print("\n" + "="*60)

async def main():
    """Main setup function"""
    print_banner()
    
    # Track setup success
    steps_passed = 0
    total_steps = 6
    
    # Step 1: Check Python version
    if check_python_version():
        steps_passed += 1
    
    # Step 2: Install dependencies
    if install_dependencies():
        steps_passed += 1
    
    # Step 3: Create environment file
    if create_env_file():
        steps_passed += 1
    
    # Step 4: Test imports
    if test_core_imports():
        steps_passed += 1
    
    # Step 5: Test API connections
    if await test_api_connections():
        steps_passed += 1
    
    # Step 6: Run safety check
    if await run_safety_check():
        steps_passed += 1
    
    # Show results
    all_passed = steps_passed == total_steps
    print(f"\n📊 Setup Results: {steps_passed}/{total_steps} steps completed")
    
    show_next_steps(all_passed)
    
    return all_passed

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)