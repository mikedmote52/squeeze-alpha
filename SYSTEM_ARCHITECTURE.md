# AI Trading System - Technical Architecture

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Streamlit)                        │
├─────────────────────────────────────────────────────────────────┤
│  📊 Portfolio Dashboard  │  🔍 Discovery  │  🤖 AI Analysis     │
│  - Live positions        │  - Catalysts   │  - Multi-model      │
│  - P&L tracking         │  - Momentum    │  - Collaborative     │
│  - Trade execution      │  - Filtering   │  - Real-time        │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTP/REST API
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│  🔄 API Router          │  📈 Analysis Engine  │  💾 Data Layer │
│  - Portfolio endpoints  │  - AI coordination   │  - Caching     │
│  - Trade execution     │  - Market scanning   │  - Memory      │
│  - Discovery APIs      │  - Risk management   │  - Baselines   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ External APIs
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                           │
├─────────────────────────────────────────────────────────────────┤
│  🏦 Alpaca API          │  🤖 OpenRouter       │  📊 Market Data │
│  - Portfolio data      │  - Claude/GPT/Grok   │  - Alpha Vantage│
│  - Trade execution     │  - AI analysis       │  - Finnhub      │
│  - Real-time prices    │  - Collaborative AI  │  - FRED/FDA     │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
ai-trading-system-complete/
├── 🎯 CORE APPLICATION
│   ├── streamlit_app.py              # Main dashboard (8501)
│   ├── real_ai_backend.py           # FastAPI backend (8000)
│   └── requirements.txt             # Dependencies
│
├── 📱 FRONTEND PAGES
│   └── pages/
│       ├── 02_🔍_Opportunity_Discovery.py
│       ├── 03_🤖_AI_Analysis.py
│       └── 04_🧠_Portfolio_Memory.py
│
├── 🧠 CORE AI SYSTEMS
│   └── core/
│       ├── collaborative_ai_system.py      # Multi-model discussions
│       ├── explosive_catalyst_discovery.py # FDA/SEC scanner
│       ├── explosive_opportunity_engine.py # Momentum scanner
│       ├── portfolio_memory_engine.py      # Historical analysis
│       ├── ai_analysis_cache.py           # Caching system
│       └── streamlit_backend_bridge.py    # API integration
│
├── 🔧 DEPLOYMENT
│   ├── Dockerfile                   # Docker configuration
│   ├── .env                        # Environment variables
│   └── railway.toml                # Deployment config
│
└── 📚 DOCUMENTATION
    ├── CLAUDE_SYSTEM_GUIDE.md       # This guide
    └── SYSTEM_ARCHITECTURE.md       # Technical details
```

## 🔄 Data Flow Architecture

### **1. Portfolio Data Flow**
```
Alpaca API → Backend Cache → Frontend Display → User Action → Trade Execution
     ↓              ↓              ↓              ↓              ↓
  Real positions   Fast loading   Live updates   Button click   Real trades
```

### **2. AI Analysis Flow**
```
User Request → Backend → OpenRouter API → AI Models → Collaborative Analysis → Recommendation
     ↓             ↓            ↓             ↓              ↓                ↓
  Click button   Route API   Claude/GPT    Multi-model    Consensus        Action plan
```

### **3. Discovery Flow**
```
Scheduled Scan → Multiple APIs → Filtering → AI Validation → Opportunity Alert → User Decision
      ↓              ↓            ↓            ↓               ↓               ↓
  Every 30min    FDA/SEC/Market  Quality     AI confidence   Slack notify   Trade/ignore
```

## 🎛️ Key Components

### **Frontend Components (Streamlit)**

#### **Main Dashboard (`streamlit_app.py`)**
- **Purpose**: Central portfolio management and trading interface
- **Key Features**:
  - Live position tracking with P&L
  - AI analysis tiles for each position
  - Trade execution buttons (Buy More, Sell All, Sell Half)
  - Portfolio health summary
  - Risk management alerts

#### **Opportunity Discovery (`pages/02_🔍_Opportunity_Discovery.py`)**
- **Purpose**: Real-time market scanning and opportunity identification
- **Key Features**:
  - Catalyst discovery (FDA approvals, SEC filings)
  - Momentum scanning (explosive growth potential)
  - Quality filtering (volume, market cap, liquidity)
  - AI explanations when no opportunities found

#### **AI Analysis (`pages/03_🤖_AI_Analysis.py`)**
- **Purpose**: Deep dive into multi-model AI discussions
- **Key Features**:
  - Claude, ChatGPT, Grok collaborative analysis
  - Bull/bear case presentations
  - Model consensus and disagreements
  - Historical analysis tracking

### **Backend Components (FastAPI)**

#### **Core API (`real_ai_backend.py`)**
- **Purpose**: Central API hub for all system operations
- **Key Endpoints**:
  - `/api/portfolio/positions` - Current portfolio
  - `/api/trades/execute` - Trade execution
  - `/api/ai-analysis` - AI model coordination
  - `/api/catalyst-discovery` - Market opportunities
  - `/api/alpha-discovery` - Momentum opportunities

#### **AI Analysis Engine (`core/collaborative_ai_system.py`)**
- **Purpose**: Coordinate multi-model AI discussions
- **Key Features**:
  - OpenRouter API integration
  - Model consensus building
  - Confidence scoring
  - Reasoning extraction

#### **Discovery Systems**
- **Catalyst Discovery** (`core/explosive_catalyst_discovery.py`)
  - FDA approval calendar monitoring
  - SEC filing analysis
  - Earnings surprise detection
  - Acquisition target identification

- **Momentum Scanner** (`core/explosive_opportunity_engine.py`)
  - 100%+ growth potential identification
  - Volume surge detection
  - Technical breakout patterns
  - Liquidity filtering

### **Data Management**

#### **Caching System (`core/ai_analysis_cache.py`)**
- **Purpose**: Optimize API usage and response times
- **Features**:
  - 30-minute TTL for AI analysis
  - Scheduled refresh at market hours
  - Memory-efficient storage
  - Fallback mechanisms

#### **Portfolio Memory (`core/portfolio_memory_engine.py`)**
- **Purpose**: Historical analysis and trend tracking
- **Features**:
  - 3-day rolling analysis
  - Position performance tracking
  - Thesis validation
  - Pattern recognition

## 🔌 External Integrations

### **Trading Platform**
- **Alpaca API** (Paper Trading)
  - Portfolio positions
  - Trade execution
  - Real-time pricing
  - Account management

### **AI Services**
- **OpenRouter API**
  - Claude 3.5 Sonnet
  - GPT-4 Turbo
  - Grok integration
  - Multi-model routing

### **Market Data**
- **Alpha Vantage**: Stock fundamentals
- **Finnhub**: Real-time prices
- **FRED API**: Economic indicators
- **FDA API**: Drug approvals
- **SEC API**: Corporate filings

### **Notifications**
- **Slack Webhook**: Real-time alerts
- **Email**: Daily summaries
- **Push**: Mobile notifications

## 🛠️ Development Workflow

### **Local Development**
1. **Backend**: `python real_ai_backend.py` (port 8000)
2. **Frontend**: `streamlit run streamlit_app.py` (port 8501)
3. **Environment**: Copy `.env` file with API keys

### **Deployment Process**
1. **Git Push**: Code changes to main branch
2. **Auto-Deploy**: Render.com detects changes
3. **Docker Build**: Uses Dockerfile with Python 3.11
4. **Service Start**: Both backend and frontend in same container
5. **Health Check**: Verify endpoints are responding

### **Testing Strategy**
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint validation
- **E2E Tests**: Full workflow testing
- **Performance Tests**: Response time monitoring

## 🚨 Critical System Requirements

### **Data Integrity**
- All portfolio data must be real (no mock data)
- AI analysis must use current market conditions
- Trade execution must connect to real Alpaca API
- Discovery results must be filtered and validated

### **Performance Requirements**
- AI analysis response time: <10 seconds
- Portfolio data refresh: <5 seconds
- Discovery scan completion: <60 seconds
- Trade execution: <3 seconds

### **Security Requirements**
- API keys stored in environment variables
- No sensitive data in code repository
- Secure HTTPS connections for all APIs
- Rate limiting on external API calls

### **Reliability Requirements**
- 99%+ uptime for core trading functions
- Graceful fallback for failed AI calls
- Retry mechanisms for network failures
- Data validation for all external inputs

## 📊 Monitoring & Alerts

### **System Health**
- API response times
- Error rates by endpoint
- Cache hit/miss ratios
- External API quota usage

### **Trading Performance**
- Portfolio P&L tracking
- Trade execution success rate
- Discovery opportunity quality
- AI recommendation accuracy

### **Cost Management**
- API call tracking by service
- Daily/weekly/monthly spend limits
- Cost per analysis calculation
- Optimization recommendations

---

**This architecture supports real-time trading with collaborative AI analysis while maintaining system reliability and performance.**