# 🔑 API Key Setup Guide

## ⚠️ CRITICAL: Your System is Currently Using Mock Data

Your AI trading system is currently **using mock/fake data** because API keys are not configured. This means:

- **🤖 AI Debates**: Using simulated Claude/ChatGPT responses (NOT real AI analysis)
- **🔍 Stock Discovery**: Using real-time market data but no Perplexity AI enhancement
- **💰 Trading Decisions**: Based on fake AI analysis instead of real AI insights

## 🎯 What You Need to Fix

### 1. **Anthropic Claude API** (CRITICAL)
- **Status**: ❌ Not configured
- **Impact**: All "Claude" responses are fake/simulated
- **Fix**: Set `ANTHROPIC_API_KEY` environment variable

### 2. **OpenAI ChatGPT API** (CRITICAL)
- **Status**: ❌ Not configured  
- **Impact**: All "ChatGPT" responses are fake/simulated
- **Fix**: Set `OPENAI_API_KEY` environment variable

### 3. **Perplexity AI API** (IMPORTANT)
- **Status**: ❌ Not configured
- **Impact**: Missing enhanced stock discovery
- **Fix**: Set `PERPLEXITY_API_KEY` environment variable

### 4. **Yahoo Finance** (WORKING)
- **Status**: ✅ Working
- **Impact**: Real-time stock data is available

## 🛠️ How to Fix This

### Option 1: Environment Variables (Recommended)
```bash
# Add these to your ~/.zshrc or ~/.bashrc
export ANTHROPIC_API_KEY="your-claude-api-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"
export PERPLEXITY_API_KEY="your-perplexity-api-key-here"

# Then restart your terminal or run:
source ~/.zshrc
```

### Option 2: Update Config File
Edit `/Users/michaelmote/Desktop/ai-trading-system-complete/config/config.json`:

```json
{
  "api_credentials": {
    "anthropic_api_key": "your-claude-api-key-here",
    "openai_api_key": "your-openai-api-key-here",
    "perplexity_api_key": "your-perplexity-api-key-here"
  }
}
```

## 🔑 Where to Get API Keys

### Anthropic Claude API
1. Go to: https://console.anthropic.com/
2. Create account and get API key
3. **Cost**: ~$0.03 per 1000 tokens
4. **Usage**: Real Claude analysis for trading decisions

### OpenAI API
1. Go to: https://platform.openai.com/api-keys
2. Create account and get API key
3. **Cost**: ~$0.002 per 1000 tokens (GPT-3.5) or ~$0.03 per 1000 tokens (GPT-4)
4. **Usage**: Real ChatGPT analysis for trading decisions

### Perplexity AI API
1. Go to: https://www.perplexity.ai/settings/api
2. Create account and get API key
3. **Cost**: ~$0.002 per 1000 tokens
4. **Usage**: Enhanced stock discovery with real-time web data

## 🚨 Current System Status

Run this command to check your current status:
```bash
python3 test_api_keys.py
```

## 📊 What Changes After Setup

### Before (Current State - Mock Data):
```
🤖 Claude says: "I think AAPL looks good..." (FAKE - simulated response)
🤖 ChatGPT says: "I disagree because..." (FAKE - simulated response)
🎯 Recommendation: Based on fake AI analysis
```

### After (With Real APIs):
```
🤖 Claude says: "Based on real market analysis..." (✅ REAL API call)
🤖 ChatGPT says: "I see different patterns..." (✅ REAL API call)
🎯 Recommendation: Based on actual AI analysis
```

## 💰 Cost Estimate

Typical daily usage:
- **Claude API**: ~$2-5 per day
- **OpenAI API**: ~$1-3 per day  
- **Perplexity API**: ~$0.50-1 per day

**Total**: ~$3.50-9 per day for full real-time AI analysis

## 🎯 Priority Order

1. **ANTHROPIC_API_KEY** (Highest Priority)
   - Get real Claude analysis instead of fake responses
   
2. **OPENAI_API_KEY** (High Priority)
   - Get real ChatGPT analysis instead of fake responses
   
3. **PERPLEXITY_API_KEY** (Medium Priority)
   - Enhanced stock discovery (system still works without it)

## ✅ Testing Your Setup

After setting up API keys:

1. **Test APIs**: `python3 test_api_keys.py`
2. **Run Discovery**: `python3 core/stock_discovery_engine.py`
3. **Check for Warnings**: Look for 🚨 or 🤖 warnings

## 🔄 Next Steps

1. **Set up at least Anthropic and OpenAI API keys**
2. **Test with the API testing script**
3. **Run a discovery cycle to see real AI analysis**
4. **Monitor for any remaining mock data warnings**

---

**Remember**: Until you set up these API keys, your system is making trading decisions based on **fake AI analysis**. This significantly reduces the effectiveness of your trading system.