# 🔑 API SETUP GUIDE - Complete AI Trading System

## Required API Keys

Add these keys to your **Replit Secrets** tab:

### 1. **POLYGON_API_KEY** 🎯
- **Get it:** https://polygon.io/dashboard
- **What it does:** Real-time market data, level 2 quotes, news, options flow
- **Benefits:**
  - Level 2 bid/ask spreads
  - Real-time news sentiment analysis
  - Options flow for unusual activity
  - Pre-market and after-hours data
  - WebSocket support for live updates

### 2. **SLACK_WEBHOOK_URL** 💬
- **Get it:** https://api.slack.com/incoming-webhooks
- **Setup Steps:**
  1. Go to your Slack workspace
  2. Create a new app or use existing
  3. Enable "Incoming Webhooks"
  4. Create webhook for your trading channel
  5. Copy the webhook URL
- **What it does:** Sends portfolio updates and trade recommendations to Slack

### 3. **SLACK_BOT_TOKEN** (Optional) 🤖
- **Get it:** Same Slack app as above
- **What it does:** Interactive buttons for trade approval/modification
- **Format:** `xoxb-your-bot-token`

### 4. **SLACK_TRADING_CHANNEL** (Optional)
- **Default:** `#trading-alerts`
- **What it does:** Specify which Slack channel to use

### 5. **Existing Keys** (Already configured)
- `ALPACA_API_KEY` - Live portfolio data
- `ALPACA_SECRET_KEY` - Alpaca trading
- `OPENROUTER_API_KEY` - Multi-AI debates
- `ANTHROPIC_API_KEY` - Claude analysis
- `OPENAI_API_KEY` - ChatGPT analysis
- `PERPLEXITY_API_KEY` - Research

## 📅 Automated Schedule

Once configured, the system automatically sends updates at:

- **5:45 AM PT** - Pre-market analysis
- **6:45 AM PT** - Opening bell + 15 minutes
- **9:30 AM PT** - Midday assessment  
- **12:45 PM PT** - Close preparation
- **1:30 PM PT** - After-market review

## 🎯 Polygon.io Benefits for Your System

### Real-Time Data Advantages:
1. **Level 2 Quotes** - See actual bid/ask spreads, not just last price
2. **Volume Analysis** - Detect unusual activity before it shows up elsewhere
3. **News Integration** - Get news the moment it breaks, with sentiment analysis
4. **Options Flow** - Track unusual options activity (dark pools, large trades)
5. **Pre/Post Market** - Trade with confidence in extended hours

### Example Polygon Features:
```
📊 VIGL Analysis:
   💰 Price: $12.45 (Bid: $12.40, Ask: $12.50)
   📈 Spread: 0.8% (normal: 2-3%)
   📊 Volume: 2.3M (avg: 800K)
   📰 News: "FDA fast-track designation approved"
   📊 Sentiment: POSITIVE
   🎯 Options: $1.2M unusual call activity
```

## 💬 Slack Integration Features

### Automated Updates:
- **Portfolio Summary** - Total value, P&L, winners/losers
- **Top Movers** - Biggest gainers and losers of the day
- **Market Alerts** - Unusual volume, news, options activity
- **AI Recommendations** - BUY/SELL/HOLD with confidence %

### Interactive Controls:
- **✅ Approve** - Execute trade immediately
- **✏️ Modify** - Adjust quantity or price
- **❌ Reject** - Cancel recommendation
- **📊 Full Analysis** - Get detailed breakdown
- **🔄 Refresh** - Update portfolio data
- **⏸️ Pause Trading** - Emergency stop

### Example Slack Message:
```
💰 MIDDAY Portfolio Update
December 12, 2024 at 9:30 AM PT

Total Value: $125,430.50
Total P&L: 📈 $8,450.25 (+7.2%)
Winners: 🟢 5 positions | Losers: 🔴 3 positions

🏆 Top Movers
• 🟢 VIGL: +15.3% ($12.45)
• 🟢 AMD: +8.2% ($142.30)
• 🔴 WOLF: -5.1% ($18.90)

⚠️ Market Alerts
• 📌 VIGL: High options flow - $2.1M
• ⚠️ WOLF: Wide spread: 3.2% - WAIT_FOR_LIQUIDITY

🤖 AI Trade Recommendations
🟢 BUY SMCI
Quantity: 100 shares @ $285.50
Reason: Technical breakout with volume
Confidence: 82%
[✅ Approve] [✏️ Modify] [❌ Reject]
```

## 🚀 Quick Start

1. **Add API keys** to Replit Secrets
2. **Test Polygon:** Click "Market Analysis" in web interface
3. **Test Slack:** Click "Test Slack" to send sample message
4. **Set up channel:** Create `#trading-alerts` in your Slack
5. **Start scheduler:** System will begin automated updates

## 🔧 Configuration Tips

- **Polygon Free Tier:** 5 calls/minute (sufficient for portfolio tracking)
- **Slack Rate Limits:** 1 message/second (system respects this)
- **Trading Hours:** System detects market sessions automatically
- **Error Handling:** Falls back to Yahoo Finance if Polygon unavailable

Your system is now ready for professional-grade trading with institutional data quality! 🎯