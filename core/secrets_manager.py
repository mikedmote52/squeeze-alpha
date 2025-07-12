import os
from dotenv import load_dotenv

class SecretsManager:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.is_replit = True
    
    def get_api_key(self, key_name):
        return os.getenv(key_name)
    
    def get_all_api_keys(self):
        # Core Trading APIs
        openrouter_key = self.get_api_key('OPENROUTER_API_KEY')
        anthropic_key = self.get_api_key('ANTHROPIC_API_KEY')
        openai_key = self.get_api_key('OPENAI_API_KEY')
        alpaca_key = self.get_api_key('ALPACA_API_KEY')
        alpaca_secret = self.get_api_key('ALPACA_SECRET_KEY')
        perplexity_key = self.get_api_key('PERPLEXITY_API_KEY')
        
        # Social Media & Content APIs
        twitter_key = self.get_api_key('TWITTER_API_KEY')
        twitter_secret = self.get_api_key('TWITTER_API_SECRET')
        youtube_key = self.get_api_key('YOUTUBE_API_KEY')
        reddit_id = self.get_api_key('REDDIT_CLIENT_ID')
        reddit_secret = self.get_api_key('REDDIT_CLIENT_SECRET')
        
        # Financial Data APIs
        alpha_vantage = self.get_api_key('ALPHA_VANTAGE_API_KEY')
        fmp_key = self.get_api_key('FMP_API_KEY')
        fred_key = self.get_api_key('FRED_API_KEY')
        fda_key = self.get_api_key('FDA_API_KEY')
        news_key = self.get_api_key('NEWS_API_KEY')
        finnhub_key = self.get_api_key('FINNHUB_API_KEY')
        polygon_key = self.get_api_key('POLYGON_API_KEY')
        
        # Notification APIs
        slack_webhook = self.get_api_key('SLACK_WEBHOOK_URL')
        
        return {
            'OPENROUTER_API_KEY': openrouter_key,
            'ANTHROPIC_API_KEY': anthropic_key,
            'OPENAI_API_KEY': openai_key,
            'ALPACA_API_KEY': alpaca_key,
            'ALPACA_SECRET_KEY': alpaca_secret,
            'PERPLEXITY_API_KEY': perplexity_key,
            'TWITTER_API_KEY': twitter_key,
            'TWITTER_API_SECRET': twitter_secret,
            'YOUTUBE_API_KEY': youtube_key,
            'REDDIT_CLIENT_ID': reddit_id,
            'REDDIT_CLIENT_SECRET': reddit_secret,
            'ALPHA_VANTAGE_API_KEY': alpha_vantage,
            'FMP_API_KEY': fmp_key,
            'FRED_API_KEY': fred_key,
            'FDA_API_KEY': fda_key,
            'NEWS_API_KEY': news_key,
            'FINNHUB_API_KEY': finnhub_key,
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
            'TWITTER_API_KEY': 'Twitter (Social Sentiment)',
            'TWITTER_API_SECRET': 'Twitter (API Secret)',
            'YOUTUBE_API_KEY': 'YouTube (Financial Content)',
            'REDDIT_CLIENT_ID': 'Reddit (WSB Sentiment)',
            'REDDIT_CLIENT_SECRET': 'Reddit (Client Secret)',
            'ALPHA_VANTAGE_API_KEY': 'Alpha Vantage (Market Data)',
            'FMP_API_KEY': 'Financial Modeling Prep',
            'FRED_API_KEY': 'FRED (Economic Data)',
            'FDA_API_KEY': 'FDA (Regulatory Events)',
            'NEWS_API_KEY': 'News API (Breaking News)',
            'FINNHUB_API_KEY': 'Finnhub (Market Data)',
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
        total_count = len(keys)
        
        print(f"\n📊 API SUMMARY: {configured_count}/{total_count} APIs configured")
        
        if configured_count >= 15:  # Most APIs configured
            print("✅ COMPREHENSIVE INTELLIGENCE READY!")
            print("🧠 Hedge fund-level market analysis available")
        elif configured_count >= 10:  # Many APIs configured
            print("✅ ADVANCED INTELLIGENCE READY!")
            print("📈 Professional-grade market analysis available")
        elif configured_count >= 5:  # Core APIs configured
            print("✅ CORE FUNCTIONALITY READY!")
            print("💡 Add more APIs for enhanced intelligence")
        else:
            print("⚠️ MORE APIs NEEDED FOR FULL FUNCTIONALITY")
            print("💡 Add missing API keys to .env file")

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