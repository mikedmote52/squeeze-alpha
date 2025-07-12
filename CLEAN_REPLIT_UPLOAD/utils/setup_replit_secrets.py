#!/usr/bin/env python3
"""
Replit Secrets Setup Helper
Guide for setting up API keys in Replit
"""

import os

def setup_replit_secrets():
    print("🔑 REPLIT API KEYS SETUP GUIDE")
    print("=" * 50)
    print()
    
    print("📍 STEP 1: Access Replit Secrets")
    print("   1. Look for 'Secrets' tab in the left sidebar")
    print("   2. If you don't see it, click the lock icon 🔒")
    print("   3. Or go to Tools → Secrets")
    print()
    
    print("🔐 STEP 2: Add These API Keys")
    print("   Click 'New Secret' for each:")
    print()
    
    secrets_to_add = [
        ("OPENROUTER_API_KEY", "Your OpenRouter API key (sk-or-v1-...)"),
        ("ANTHROPIC_API_KEY", "Your Claude API key (sk-ant-...)"),
        ("OPENAI_API_KEY", "Your OpenAI API key (sk-...)"),
        ("ALPACA_API_KEY", "Your Alpaca trading API key"),
        ("ALPACA_SECRET_KEY", "Your Alpaca secret key"),
        ("PERPLEXITY_API_KEY", "Your Perplexity API key (pplx-...)")
    ]
    
    for key_name, description in secrets_to_add:
        current_value = os.getenv(key_name)
        status = "✅ CONFIGURED" if current_value else "❌ MISSING"
        
        print(f"   Key: {key_name}")
        print(f"   Description: {description}")
        print(f"   Status: {status}")
        if current_value:
            preview = current_value[:8] + "..." if len(current_value) > 8 else current_value
            print(f"   Current: {preview}")
        print()
    
    print("🚀 STEP 3: Restart Your Repl")
    print("   After adding secrets:")
    print("   1. Stop your current run")
    print("   2. Click Run again")
    print("   3. Test the 🔑 Check API Keys button")
    print()
    
    print("💡 HELPFUL LINKS:")
    print("   • Claude API: https://console.anthropic.com/")
    print("   • OpenAI API: https://platform.openai.com/api-keys")
    print("   • OpenRouter: https://openrouter.ai/keys")
    print("   • Alpaca Trading: https://app.alpaca.markets/")
    print("   • Perplexity: https://www.perplexity.ai/settings/api")


def check_current_secrets():
    print("\n🔍 CURRENT SECRETS STATUS:")
    print("=" * 40)
    
    secrets_to_check = [
        "OPENROUTER_API_KEY",
        "ANTHROPIC_API_KEY", 
        "OPENAI_API_KEY",
        "ALPACA_API_KEY",
        "ALPACA_SECRET_KEY",
        "PERPLEXITY_API_KEY"
    ]
    
    configured = 0
    total = len(secrets_to_check)
    
    for secret_name in secrets_to_check:
        value = os.getenv(secret_name)
        if value:
            configured += 1
            preview = value[:8] + "..." if len(value) > 8 else value
            print(f"✅ {secret_name}: {preview}")
        else:
            print(f"❌ {secret_name}: Not found")
    
    print(f"\n📊 Progress: {configured}/{total} secrets configured")
    
    if configured == total:
        print("🎉 All secrets configured! Your system is ready!")
    else:
        print(f"⚠️ {total - configured} secrets missing. Add them in Replit Secrets tab.")


if __name__ == "__main__":
    setup_replit_secrets()
    check_current_secrets()