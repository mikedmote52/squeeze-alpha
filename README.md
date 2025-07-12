# 🚀 Squeeze Alpha - AI Trading System

**Professional-grade AI trading system with multi-model consensus, real-time market analysis, and institutional safety features.**

## 🎯 System Overview

Squeeze Alpha is a sophisticated AI-powered trading system that leverages multiple AI models (Claude, ChatGPT, Grok) to conduct real-time stock analysis and portfolio management. The system features institutional-grade safety protocols, comprehensive market analysis, and automated reporting.

### 🔥 Key Features

- **🤖 Multi-AI Consensus**: Real-time debates between Claude, ChatGPT, and Grok for stock analysis
- **📊 Live Portfolio Management**: Real-time position tracking with AI recommendations
- **🔍 Advanced Stock Discovery**: Professional-grade screening with quality filters
- **📈 Real-time Market Data**: Polygon.io, Yahoo Finance, and Alpaca integration
- **🛡️ Trading Safety**: Comprehensive validation to prevent trading with mock data
- **📱 Professional Web Interface**: Interactive portfolio tiles with detailed analysis
- **⏰ Automated Scheduling**: 5 daily market sessions with performance reports
- **💬 Slack Integration**: Real-time notifications and trade approvals

## 🏗️ System Architecture

```
squeeze-alpha/
├── core/                          # Core trading engines
│   ├── alpha_engine_enhanced.py   # Professional stock discovery
│   ├── live_portfolio_engine.py   # Real-time portfolio management
│   ├── openrouter_stock_debate.py # Multi-AI consensus system
│   ├── real_time_ai_debate.py     # Advanced AI debate engine
│   ├── performance_report_engine.py # Daily analytics and reporting
│   ├── market_session_scheduler.py # Automated trading sessions
│   ├── trading_safety_validator.py # Safety and validation
│   ├── slack_trading_bot.py       # Slack integration
│   └── secrets_manager.py         # API key management
├── utils/                         # Utility functions
├── tests/                         # Automated testing
├── main.py                        # Web interface and API
└── requirements.txt               # Dependencies
```

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/squeeze-alpha.git
cd squeeze-alpha
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.env` file or add to your environment:

```bash
# Required for AI Analysis
OPENROUTER_API_KEY=your_openrouter_key
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_chatgpt_key

# Required for Trading
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret

# Optional but Recommended
POLYGON_API_KEY=your_polygon_key
PERPLEXITY_API_KEY=your_perplexity_key
SLACK_WEBHOOK_URL=your_slack_webhook
```

### 4. Run System Safety Check
```bash
python -c "from core.trading_safety_validator import emergency_trading_safety_check; emergency_trading_safety_check()"
```

### 5. Start the System
```bash
python main.py
```

## 🔑 API Key Setup

### Required APIs:
- **OpenRouter**: Multi-AI access (Claude, ChatGPT, Grok) - [Get API Key](https://openrouter.ai/)
- **Alpaca**: Live trading and portfolio data - [Get API Key](https://app.alpaca.markets/)

### Recommended APIs:
- **Anthropic**: Direct Claude access - [Get API Key](https://console.anthropic.com/)
- **OpenAI**: Direct ChatGPT access - [Get API Key](https://platform.openai.com/api-keys)
- **Polygon.io**: Real-time market data - [Get API Key](https://polygon.io/)

## 🎯 Core Features

### 🤖 Multi-AI Stock Analysis
```python
from core.openrouter_stock_debate import OpenRouterStockDebate

debate = OpenRouterStockDebate()
result = await debate.debate_stock('NVDA', 850.00, 12.5, 8.2)

# Gets real-time analysis from Claude, ChatGPT, and Grok
# Includes conversation thesis and final consensus
```

### 📊 Live Portfolio Management
```python
from core.live_portfolio_engine import LivePortfolioEngine

engine = LivePortfolioEngine()
positions = await engine.get_live_portfolio()

# Real-time positions with AI recommendations
# Detailed thesis for each holding
# Risk analysis and position sizing
```

### 🔍 Enhanced Stock Discovery
```python
from core.alpha_engine_enhanced import EnhancedAlphaEngine

engine = EnhancedAlphaEngine()
candidates = await engine.discover_alpha_opportunities()

# Professional-grade filtering
# Excludes dilution stocks (AMC, GME, etc.)
# Includes institutional-quality opportunities
```

## 🛡️ Safety Features

The system includes comprehensive safety protocols:

- **Mock Data Detection**: Prevents trading with fake data
- **API Validation**: Ensures all connections are live
- **Trading Blocks**: Stops execution if safety violations detected
- **Real-time Monitoring**: Continuous system health checks

### Safety Check Example:
```python
from core.trading_safety_validator import TradingSafetyValidator

validator = TradingSafetyValidator()
is_safe, violations = validator.validate_all_systems()

if not is_safe:
    print("🛑 TRADING BLOCKED - Safety violations detected")
```

## 📱 Web Interface

The system includes a professional web interface with:

- **Live Portfolio Tiles**: Clickable holdings with real-time data
- **AI Recommendations**: BUY/SELL/HOLD with confidence levels
- **Stock Detail Modals**: Complete analysis, thesis, and action plans
- **Real-time Updates**: Auto-refresh every 60 seconds
- **Mobile Responsive**: Works on all devices

Access via: `http://localhost:8080` when running

## ⏰ Automated Scheduling

The system runs 5 automated sessions daily:

- **05:45 PT**: Pre-market analysis
- **06:45 PT**: Opening volatility scan
- **09:30 PT**: Mid-day momentum check
- **12:45 PT**: End-of-day summary
- **13:30 PT**: After-hours learning

Each session includes:
- Portfolio performance analysis
- New opportunity discovery
- Risk assessment updates
- Slack notifications

## 📊 Performance Reporting

Comprehensive analytics include:

- **Daily/Weekly/Monthly/Annual** performance reports
- **Risk-adjusted returns** (Sharpe ratio, max drawdown)
- **Win/loss analysis** with trade statistics
- **AI recommendation tracking** and accuracy
- **Improvement suggestions** based on performance

## 🧪 Testing

Run automated tests:
```bash
python -m pytest tests/
```

Test individual components:
```bash
# Test API connections
python core/secrets_manager.py

# Test portfolio engine
python core/live_portfolio_engine.py

# Test stock discovery
python core/alpha_engine_enhanced.py

# Test AI debates
python core/openrouter_stock_debate.py
```

## 🔧 Configuration

### Environment Variables:
- All API keys can be set via environment variables
- Supports `.env` file for local development
- Compatible with Replit Secrets for cloud deployment

### Trading Settings:
- Paper trading enabled by default
- Switch to live trading by updating Alpaca base URL
- Risk management parameters configurable in `core/` modules

## 📚 Documentation

### Core Modules:
- **Alpha Engine**: [alpha_engine_enhanced.py](core/alpha_engine_enhanced.py) - Stock discovery and screening
- **Portfolio Engine**: [live_portfolio_engine.py](core/live_portfolio_engine.py) - Real-time position management
- **AI Debate**: [openrouter_stock_debate.py](core/openrouter_stock_debate.py) - Multi-AI consensus
- **Safety Validator**: [trading_safety_validator.py](core/trading_safety_validator.py) - System safety

### API Integrations:
- **Alpaca**: Live trading and portfolio data
- **Polygon.io**: Real-time market data and news
- **OpenRouter**: Multi-AI model access
- **Slack**: Notifications and approvals

## 🚨 Important Notes

### Safety First:
- **NEVER** trade with real money without thorough testing
- Always run safety validation before live trading
- Use paper trading for initial testing and validation
- Monitor all trades and system behavior closely

### API Rate Limits:
- OpenRouter: 200 requests/minute
- Polygon.io: Varies by plan
- Alpaca: 200 requests/minute
- Plan API usage accordingly

### Legal Disclaimer:
This system is for educational and research purposes. Trading involves substantial risk of loss. Past performance does not guarantee future results. Use at your own risk.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs via [GitHub Issues](https://github.com/yourusername/squeeze-alpha/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/yourusername/squeeze-alpha/discussions)
- **Documentation**: Full docs at [docs/](docs/)

---

**⚡ Built with institutional-grade safety and performance in mind**

*The Squeeze Alpha trading system combines cutting-edge AI with professional trading infrastructure for sophisticated market analysis and portfolio management.*