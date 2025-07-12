#!/usr/bin/env python3
"""
Replit Secrets Setup Guide
Helps you configure API keys from Replit's Secrets tab
"""

import os
import sys
sys.path.append('core')
from secrets_manager import SecretsManager

def main():
    print("🔑 REPLIT SECRETS SETUP GUIDE")
    print("=" * 60)
    
    # Check if running in Replit
    if os.getenv('REPL_ID'):
        print("✅ Running in Replit environment")
        print(f"📍 Repl ID: {os.getenv('REPL_ID')}")
    else:
        print("❌ Not running in Replit")
        print("💡 This guide is for Replit users")
        return
    
    print()
    
    # Test current secrets
    secrets_manager = SecretsManager()
    status = secrets_manager.test_api_keys()
    
    print("📊 CURRENT STATUS:")
    print(f"✅ Keys Configured: {status['keys_configured']}")
    print(f"❌ Keys Missing: {status['keys_missing']}")
    print()
    
    # Show missing keys
    missing_keys = []
    for key_name, details in status['details'].items():
        if not details['status'].startswith('✅'):
            missing_keys.append(key_name)
    
    if missing_keys:
        print("🚨 MISSING API KEYS:")
        for key in missing_keys:
            print(f"   • {key}")
        print()
        
        print("💡 HOW TO ADD SECRETS IN REPLIT:")
        print("1. 👈 Look at the left sidebar in Replit")
        print("2. 🔐 Click the 'Secrets' tab (lock icon)")
        print("3. ➕ Click 'New Secret' for each missing key")
        print("4. 📝 Add these exact key names:")
        print()
        
        for key in missing_keys:
            print(f"   Key: {key}")
            print(f"   Value: [paste your API key here]")
            print()
        
        print("5. 🔄 After adding all secrets, restart your Repl")
        print("6. 🧪 Run this script again to verify")
        print()
        
        print("🔗 WHERE TO GET API KEYS:")
        if 'ANTHROPIC_API_KEY' in missing_keys:
            print("• Anthropic Claude: https://console.anthropic.com/")
        if 'OPENAI_API_KEY' in missing_keys:
            print("• OpenAI ChatGPT: https://platform.openai.com/api-keys")
        if 'PERPLEXITY_API_KEY' in missing_keys:
            print("• Perplexity AI: https://www.perplexity.ai/settings/api")
        if 'ALPACA_API_KEY' in missing_keys:
            print("• Alpaca Trading: https://app.alpaca.markets/")
        print()
        
        print("💰 ESTIMATED COSTS (daily):")
        print("• Claude API: $2-5")
        print("• OpenAI API: $1-3")
        print("• Perplexity API: $0.50-1")
        print("• Alpaca: Free (paper trading)")
        print()
        
    else:
        print("🎉 ALL API KEYS CONFIGURED!")
        print("✅ Your system should now use real AI analysis")
        print()
        print("🧪 TEST YOUR SETUP:")
        print("Run: python3 test_api_keys.py")
    
    print("=" * 60)
    print("💡 TROUBLESHOOTING:")
    print("• If keys don't work after adding, restart your Repl")
    print("• Make sure key names are EXACTLY as shown above")
    print("• Check for extra spaces in key values")
    print("• Verify API keys are valid on their respective platforms")

if __name__ == "__main__":
    main()