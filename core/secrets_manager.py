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
        polygon_key = self.get_api_key('POLYGON_API_KEY')
        slack_webhook = self.get_api_key('SLACK_WEBHOOK_URL')
        
        return {
            'OPENROUTER_API_KEY': openrouter_key,
            'ANTHROPIC_API_KEY': anthropic_key,
            'OPENAI_API_KEY': openai_key,
            'ALPACA_API_KEY': alpaca_key,
            'ALPACA_SECRET_KEY': alpaca_secret,
            'PERPLEXITY_API_KEY': perplexity_key,
            'POLYGON_API_KEY': polygon_key,
            'SLACK_WEBHOOK_URL': slack_webhook
        }
    
    def print_status_report(self):
        keys = self.get_all_api_keys()
        print("🔑 API KEYS STATUS:")
        print("=" * 30)
        
        # Display with better labels
        key_labels = {
            'OPENROUTER_API_KEY': 'OpenRouter (Multi-AI)',
            'ANTHROPIC_API_KEY': 'Anthropic (Claude)',
            'OPENAI_API_KEY': 'OpenAI (ChatGPT)',
            'ALPACA_API_KEY': 'Alpaca (Trading)',
            'ALPACA_SECRET_KEY': 'Alpaca (Secret)',
            'PERPLEXITY_API_KEY': 'Perplexity (Research)',
            'POLYGON_API_KEY': 'Polygon (Real-time Data)',
            'SLACK_WEBHOOK_URL': 'Slack (Notifications)'
        }
        
        for key_name, key_value in keys.items():
            label = key_labels.get(key_name, key_name)
            if key_value:
                preview = key_value[:12] + "..." if len(key_value) > 12 else key_value
                print(f"✅ {label}: {preview}")
            else:
                print(f"❌ {label}: MISSING")
        
        configured_count = sum(1 for v in keys.values() if v)
        if configured_count >= 6:  # Core APIs + Polygon + Slack
            print("\n✅ API keys are configured! System ready for professional trading.")
        elif configured_count >= 4:  # At least core APIs
            print("\n✅ Core APIs configured! Add Polygon & Slack for full features.")
        else:
            print(f"\n💡 Add missing keys to Replit Secrets tab")

# Global instance
secrets = SecretsManager()

# Convenience functions for backward compatibility
def get_anthropic_key():
    return secrets.get_api_key('ANTHROPIC_API_KEY')

def get_openai_key():
    return secrets.get_api_key('OPENAI_API_KEY')

def get_perplexity_key():
    return secrets.get_api_key('PERPLEXITY_API_KEY')

def get_alpaca_key():
    return secrets.get_api_key('ALPACA_API_KEY')

def get_alpaca_secret():
    return secrets.get_api_key('ALPACA_SECRET_KEY')

def get_openrouter_key():
    return secrets.get_api_key('OPENROUTER_API_KEY')