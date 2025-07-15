# AI Trading System

Production-ready AI trading system with multi-agent consensus, risk management, and comprehensive monitoring.

## 🎯 Features

### 🤖 Multi-Agent AI System
- **Claude + ChatGPT Consensus**: 4-step collaborative analysis workflow
- **Disagreement Resolution**: Identifies and resolves conflicting AI opinions
- **Confidence Scoring**: Tracks consensus strength across all recommendations

### 📊 Ad6.   ced Intelligence
- **Stock Screening**: Multi-criteria screening with technical analysis
- **Social Sentiment**: Reddit, Twitter, and Congressional trading analysis
- **Market Data**: Multi-source data aggregation (Polygon, Alpha Vantage, Yahoo)

### 🛡️ Risk Management
- **Position Sizing**: Automated position sizing with exposure limits
- **Bracket Orders**: Take profit levels and stop-loss protection
- **Human Override**: Approval system for high-risk trades

### 📈 Monitoring & Analytics
- **Real-time Monitoring**: Portfolio health checks and alerts
- **Performance Analytics**: Sharpe ratio, drawdown, win rate tracking
- **Risk Monitoring**: Continuous risk limit monitoring

### 🔗 Integrations
- **Slack**: Interactive notifications and command system
- **N8N**: Workflow orchestration and automation
- **Google Sheets**: Comprehensive logging and data backup

## 🚀 Quick Start

### 1. Installation
```bash
# Clone and setup
cd ai-trading-system-complete
pip install -r requirements.txt
```

### 2. Configuration
Create `config/config.json`:
```json
{
  "api_credentials": {
    "alpaca_api_key": "YOUR_ALPACA_KEY",
    "alpaca_secret": "YOUR_ALPACA_SECRET",
    "openai_api_key": "YOUR_OPENAI_KEY",
    "anthropic_api_key": "YOUR_ANTHROPIC_KEY",
    "slack_oauth_token": "YOUR_SLACK_TOKEN"
  }
}
```

### 3. Start the System
```bash
# Start FastAPI server
python start_server.py

# Or directly with uvicorn
uvicorn app:app --app-dir src --reload
```

### 4. Access Endpoints
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Dashboard**: http://localhost:8000/api/dashboard

## 📡 API Endpoints

### Intelligence
- `POST /webhook/stock-screener` - Stock screening
- `POST /webhook/social-sentiment` - Sentiment analysis
- `GET /api/screening/candidates` - Get screening results

### AI Consensus
- `POST /webhook/ai-consensus` - Multi-agent analysis

### Trading
- `POST /webhook/execute-trades` - Execute trades
- `GET /api/positions` - Current positions
- `GET /api/portfolio/summary` - Portfolio summary

### Monitoring
- `GET /api/dashboard` - Complete dashboard
- `GET /api/analytics/performance` - Performance metrics
- `GET /api/risk/status` - Risk monitoring

## 🔧 N8N Integration

### Webhook URLs
```
http://localhost:8000/webhook/stock-screener
http://localhost:8000/webhook/social-sentiment  
http://localhost:8000/webhook/ai-consensus
http://localhost:8000/webhook/execute-trades
```

### Example N8N Workflow
```json
{
  "nodes": [
    {
      "name": "Daily Trigger",
      "type": "n8n-nodes-base.scheduleTrigger"
    },
    {
      "name": "Stock Screening",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:8000/webhook/stock-screener",
        "method": "POST"
      }
    }
  ]
}
```

## 🛠️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   N8N Workflows │───▶│  FastAPI Server  │───▶│  Trading APIs   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Slack Alerts    │◀───│  Core Modules    │───▶│ Data Sources    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Google Sheets    │
                       │ Logging          │
                       └──────────────────┘
```

## 📦 Module Structure

```
src/
├── app.py                          # FastAPI application
└── python_modules/
    ├── utils/                      # Core utilities
    │   ├── config.py              # Configuration management
    │   ├── logging_system.py      # Comprehensive logging
    │   ├── slack_integration.py   # Slack notifications
    │   ├── n8n_interface.py       # N8N integration
    │   └── scheduler.py           # Workflow scheduling
    ├── intelligence/               # AI and data gathering
    │   ├── stock_screener.py      # Stock screening engine
    │   ├── social_sentiment.py    # Sentiment analysis
    │   ├── ai_models.py           # AI model interfaces
    │   └── market_data.py         # Market data provider
    ├── consensus/                  # AI consensus system
    │   ├── multi_agent_analyzer.py # Multi-agent analysis
    │   ├── consensus_builder.py    # Consensus building
    │   └── recommendation_engine.py # Final recommendations
    ├── execution/                  # Trade execution
    │   ├── position_manager.py     # Portfolio management
    │   ├── trade_executor.py       # Trade execution
    │   ├── risk_manager.py         # Risk management
    │   └── human_override.py       # Human oversight
    └── monitoring/                 # Analytics and monitoring
        ├── portfolio_monitor.py    # Real-time monitoring
        ├── performance_analytics.py # Performance metrics
        ├── risk_monitoring.py      # Risk monitoring
        └── dashboard.py            # Analytics dashboard
```

## 🔒 Security Features

- **Paper Trading**: Default Alpaca paper trading environment
- **Risk Limits**: Configurable position size and exposure limits
- **Human Override**: Manual approval for high-risk trades
- **API Key Management**: Secure credential handling

## 📊 Monitoring

### Real-time Alerts
- Daily P&L thresholds
- Individual position losses
- Risk limit violations
- System health issues

### Performance Tracking
- Sharpe ratio calculation
- Maximum drawdown monitoring
- Win rate analysis
- Risk-adjusted returns

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: Check `/docs` endpoint when server is running
- **Issues**: Create GitHub issue for bugs
- **Features**: Submit feature request via GitHub

---

**Built with ❤️ for systematic trading**