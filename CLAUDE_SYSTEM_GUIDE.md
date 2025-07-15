# AI Trading System - Claude Developer Guide

## 🎯 System Overview

This is a **real-time AI trading system** that uses collaborative AI analysis (Claude, ChatGPT, Grok) to manage a live trading portfolio through Alpaca API. The system provides real-time market analysis, trade execution, and portfolio optimization.

## 🏗️ Architecture Components

### **Frontend (Streamlit)**
- **Main Dashboard**: `/streamlit_app.py` - Portfolio overview and trading interface
- **Opportunity Discovery**: `/pages/02_🔍_Opportunity_Discovery.py` - Real-time market scanning
- **AI Analysis**: `/pages/03_🤖_AI_Analysis.py` - Multi-model AI discussions
- **Portfolio Memory**: `/pages/04_🧠_Portfolio_Memory.py` - Historical analysis

### **Backend (FastAPI)**
- **Main API**: `/real_ai_backend.py` - Core trading and analysis endpoints
- **Port**: 8000 (backend) + 8501 (frontend)
- **Deployment**: Render.com with Docker containerization

### **Core AI Systems** (`/core/` directory)
- **Collaborative AI**: Multi-model discussions between Claude, ChatGPT, Grok
- **Market Discovery**: Real-time opportunity scanning (FDA/SEC catalysts, explosive stocks)
- **Portfolio Memory**: 3-day rolling analysis and position tracking
- **Cost Tracking**: API usage monitoring across all services

## 🔄 Data Flow

1. **Real-time Market Data** → Multiple APIs (Alpaca, Alpha Vantage, etc.)
2. **AI Analysis** → OpenRouter API (Claude, ChatGPT, Grok collaborative analysis)
3. **Trade Execution** → Alpaca Paper Trading API
4. **Portfolio Tracking** → Live position monitoring and P&L calculation
5. **Opportunity Discovery** → Real-time catalyst and momentum scanning

## 📊 Key Features

### **Real Trading Integration**
- **Live Portfolio**: Real Alpaca positions (BLNK: 153 shares, CRWV: 14 shares, EAT: 1 share)
- **Trade Execution**: Buy/Sell/Hold actions execute real orders
- **P&L Tracking**: Real-time profit/loss monitoring
- **Risk Management**: Position sizing and concentration alerts

### **AI Analysis System**
- **Multi-Model Consensus**: Claude, ChatGPT, Grok discuss each position
- **Dynamic Recommendations**: Buy More, Reduce Position, Hold with reasoning
- **Price Targets**: AI-generated price targets based on model consensus
- **Risk Assessment**: Volatility analysis and trend evaluation

### **Market Discovery**
- **Catalyst Scanner**: FDA approvals, SEC filings, earnings surprises
- **Momentum Scanner**: Explosive growth potential (100%+ targets)
- **Quality Filters**: Volume, market cap, and liquidity requirements
- **Real-time Alerts**: Slack notifications for high-confidence opportunities

## 🛠️ How to Make Recommendations

### **Understanding the Current State**
1. **Portfolio Health**: Check diversification, concentration risk, P&L performance
2. **Individual Positions**: Review AI sentiment, price targets, and model consensus
3. **Market Conditions**: Assess discovery results and opportunity availability
4. **Risk Factors**: Evaluate volatility, sector exposure, and position sizing

### **Types of Recommendations**

#### **Position Management**
- **HOLD**: When AI models show mixed signals or neutral sentiment
- **BUY MORE**: When multiple models agree on upside potential
- **REDUCE/SELL**: When models identify downside risks or overconcentration
- **REPLACE**: When discovery system finds better alternatives

#### **Portfolio Optimization**
- **Rebalancing**: Adjust position sizes based on performance and risk
- **Diversification**: Address concentration alerts (>20% in single position)
- **Profit-taking**: Secure gains on strong performers (>20% gains)
- **Loss Management**: Cut losses on underperformers (<-15% losses)

#### **Opportunity Actions**
- **New Positions**: When discovery finds high-confidence catalysts
- **Timing**: Consider market hours, volatility, and liquidity
- **Risk Sizing**: Start with small positions, scale based on performance

### **Data Sources for Recommendations**

#### **Portfolio Data** (`/api/portfolio/positions`)
```json
{
  "symbol": "BLNK",
  "qty": 153,
  "market_value": 216.33,
  "unrealized_pl": -19.17,
  "unrealized_plpc": -8.16,
  "current_price": 1.41,
  "avg_entry_price": 1.54
}
```

#### **AI Analysis** (`/api/ai-analysis`)
```json
{
  "claude_score": "🔻 Sell (75%)",
  "gpt_score": "📉 Sell Signal (80%)",
  "projected_price": 1.25,
  "actionable_recommendation": "🔻 CONSIDER REDUCING POSITION: 2/3 AI models recommend selling",
  "thesis": "AI models cite declining EV demand and increased competition..."
}
```

#### **Discovery Results** (`/api/catalyst-discovery`, `/api/alpha-discovery`)
```json
{
  "opportunities": [...],
  "explanation": {
    "reasoning": "Scanned 47 biotech catalysts, filtered 32 for market cap...",
    "candidates_found": 15,
    "market_status": "Regular trading hours"
  }
}
```

## 🚨 Critical Guidelines

### **What NOT to Do**
- ❌ **Never add mock/fake data** - All analysis must be from real APIs
- ❌ **Don't break existing functionality** - Preserve working architecture
- ❌ **Avoid generic recommendations** - Always provide specific, actionable guidance
- ❌ **Don't ignore risk management** - Consider position sizing and concentration

### **What TO Do**
- ✅ **Use real-time data** - Always reference current market conditions
- ✅ **Provide clear actions** - Specific buy/sell/hold recommendations with reasoning
- ✅ **Consider context** - Account for portfolio balance, risk tolerance, market timing
- ✅ **Be transparent** - Explain reasoning behind recommendations
- ✅ **Update consistently** - Ensure price targets and analysis are synchronized

## 📈 Example Recommendation Process

### **Scenario**: BLNK position showing -8.16% P&L

1. **Analyze AI Sentiment**: 
   - Claude: 🔻 Sell (75%)
   - GPT-4: 📉 Sell Signal (80%)
   - Consensus: Strong sell signals

2. **Review Market Context**:
   - Current price: $1.41
   - Entry price: $1.54
   - Target price: $1.25 (AI consensus)

3. **Generate Recommendation**:
   ```
   🔻 REDUCE BLNK POSITION
   
   Reasoning: 2/3 AI models recommend selling due to declining EV demand 
   and increased competition. Position down -8.16% with further downside 
   to $1.25 target.
   
   Action: Sell 50% of position (76 shares) to reduce risk exposure.
   Keep 77 shares in case of recovery.
   ```

## 🔧 Technical Implementation

### **Environment Variables**
```bash
# Trading
ALPACA_API_KEY=PKX1WGCFOD3XXA9LBAR8
ALPACA_SECRET_KEY=vCQUe2hVPNLLvkw4DxviLEngZtk5zvCs7jsWT3nR
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# AI Analysis
OPENROUTER_API_KEY=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
PERPLEXITY_API_KEY=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

# Notifications
SLACK_WEBHOOK=https://hooks.slack.com/services/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
```

### **Key API Endpoints**
- `GET /api/portfolio/positions` - Current portfolio
- `POST /api/trades/execute` - Execute trades
- `POST /api/ai-analysis` - Get AI recommendations
- `GET /api/catalyst-discovery` - Market opportunities
- `GET /api/alpha-discovery` - Momentum opportunities

### **Deployment**
- **Platform**: Render.com
- **Container**: Docker with Python 3.11
- **URL**: https://squeeze-alpha.onrender.com
- **Auto-deploy**: On git push to main branch

## 🎯 Success Metrics

### **System Health**
- ✅ Real-time data connectivity
- ✅ AI model response times <10s
- ✅ Trade execution success rate >95%
- ✅ Discovery engine uptime >99%

### **Portfolio Performance**
- 📊 Track P&L vs market benchmarks
- 📈 Monitor win rate and average gains
- ⚠️ Manage concentration risk <25% per position
- 🎯 Achieve consistent discovery of 10%+ opportunities

---

**This system is designed to provide real-time, actionable trading intelligence through collaborative AI analysis. Always prioritize risk management and real-time data accuracy in all recommendations.**