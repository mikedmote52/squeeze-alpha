import os

class SecretsManager:
    def __init__(self):
        self.is_replit = True
    
    def get_api_key(self, key_name):
        return os.getenv(key_name)
    
    def get_all_api_keys(self):
        openrouter_key = self.get_api_key('OPENROUTER_API_KEY')
        alpaca_key = self.get_api_key('ALPACA_API_KEY')
        alpaca_secret = self.get_api_key('ALPACA_SECRET_KEY')
        
        return {
            'OPENROUTER_API_KEY': openrouter_key,
            'ALPACA_API_KEY': alpaca_key,
            'ALPACA_SECRET_KEY': alpaca_secret
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
        
        if not keys.get('OPENROUTER_API_KEY'):
            print("\n💡 Add OPENROUTER_API_KEY to Replit Secrets")

secrets = SecretsManager()