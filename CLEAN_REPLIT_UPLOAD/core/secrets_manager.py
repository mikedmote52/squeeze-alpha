import os

class SecretsManager:
    def __init__(self):
        self.is_replit = True
    
    def get_api_key(self, key_name):
        return os.getenv(key_name)
    
    def get_all_api_keys(self):
        openrouter_key = self.get_api_key('OPENROUTER_API_KEY')
        anthropic_key = self.get_api_key('ANTHROPIC_API_KEY')
        openai_key = self.get_api_key('OPENAI_API_KEY')
        alpaca_key = self.get_api_key('ALPACA_API_KEY')
        alpaca_secret = self.get_api_key('ALPACA_SECRET_KEY')
        perplexity_key = self.get_api_key('PERPLEXITY_API_KEY')
        
        return {
            'OPENROUTER_API_KEY': openrouter_key,
            'ANTHROPIC_API_KEY': anthropic_key,
            'OPENAI_API_KEY': openai_key,
            'ALPACA_API_KEY': alpaca_key,
            'ALPACA_SECRET_KEY': alpaca_secret,
            'PERPLEXITY_API_KEY': perplexity_key
        }
    
    def print_status_report(self):
        keys = self.get_all_api_keys()
        print("🔑 API KEYS STATUS:")
        print("=" * 30)
        
        for key_name, key_value in keys.items():
            if key_value:
                preview = key_value[:12] + "..." if len(key_value) > 12 else key_value
                print(f"✅ {key_name}: {preview}")
            else:
                print(f"❌ {key_name}: MISSING")
        
        configured_count = sum(1 for v in keys.values() if v)
        if configured_count == len(keys):
            print("\n✅ API keys are configured! System ready for real-time data.")
        else:
            print(f"\n💡 Add missing keys to Replit Secrets tab")

secrets = SecretsManager()