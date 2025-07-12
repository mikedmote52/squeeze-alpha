# 🧪 QUICK TEST COMMANDS - See Your System in Action

## 🚀 IMMEDIATE TESTS (Run These First)

### **1. Check Your Replit Secrets Setup**
```bash
python3 setup_replit_secrets.py
```
**What you'll see**: Status of your API keys in Replit Secrets

### **2. Validate System Safety**
```bash
python3 core/trading_safety_validator.py
```
**What you'll see**: Comprehensive safety check - shows what's real vs mock

### **3. Test Real-Time Stock Discovery**
```bash
python3 core/real_time_stock_discovery.py
```
**What you'll see**: Live market scanning finding real opportunities like AMC

### **4. Analyze Your Current Holdings**
```bash
python3 -c "
import sys; sys.path.append('core')
import asyncio, yfinance as yf
from datetime import datetime

async def quick_portfolio():
    holdings = ['AMD', 'NVAX', 'WOLF', 'BTBT', 'CRWV', 'VIGL']
    print('📊 YOUR HOLDINGS - LIVE DATA')
    print('=' * 40)
    for ticker in holdings:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='2d')
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                print(f'{ticker}: \${current:.2f} ({change:+.1f}%)')
        except: pass

asyncio.run(quick_portfolio())
"
```
**What you'll see**: Real-time analysis of your actual holdings

---

## 🔍 DISCOVERY TESTS

### **5. Test Full Discovery Pipeline**
```bash
python3 -c "
import sys; sys.path.append('core')
import asyncio
from real_time_stock_discovery import RealTimeStockDiscovery

async def test_discovery():
    discovery = RealTimeStockDiscovery()
    candidates = await discovery.discover_live_explosive_opportunities('today')
    print(f'Found {len(candidates)} real opportunities!')
    for c in candidates[:2]:
        print(f'• {c.ticker}: {c.price_change_1d:+.1f}%, {c.volume_spike:.1f}x volume')

asyncio.run(test_discovery())
"
```

### **6. Test AI Analysis (Shows Safety Protection)**
```bash
python3 -c "
import sys; sys.path.append('core')
import asyncio
from enhanced_ai_consensus import EnhancedAIConsensus

async def test_ai():
    ai = EnhancedAIConsensus()
    try:
        result = await ai.get_real_claude_analysis('AAPL', {}, {}, '', '')
        print('✅ Real Claude analysis working!')
    except Exception as e:
        print(f'🚨 Safety Protection: {str(e)[:80]}...')
        print('💡 Add ANTHROPIC_API_KEY to Replit Secrets for real AI')

asyncio.run(test_ai())
"
```

---

## 📊 PORTFOLIO TESTS

### **7. Test Portfolio Engine Safety**
```bash
python3 -c "
import sys; sys.path.append('core')
import asyncio
from real_time_portfolio_engine import RealTimePortfolioEngine

async def test_portfolio():
    portfolio = RealTimePortfolioEngine()
    try:
        positions = await portfolio.get_live_portfolio_positions()
        print('✅ Real portfolio data available!')
    except Exception as e:
        print(f'🚨 Safety Protection: {str(e)[:80]}...')
        print('💡 Add ALPACA keys to Replit Secrets for real portfolio')

asyncio.run(test_portfolio())
"
```

---

## 🚀 SYSTEM STARTUP TESTS

### **8. Test System Startup Protection**
```bash
python3 start_autonomous_system.py
```
**What you'll see**: 
- If APIs missing: Safety block with clear instructions
- If APIs configured: System starts with real data

### **9. Quick Market Scan**
```bash
python3 -c "
import yfinance as yf
from datetime import datetime

print('📊 QUICK MARKET SCAN')
print('=' * 30)
print(f'⏰ {datetime.now().strftime(\"%H:%M %Z\")}')

# Check some movers
tickers = ['SPY', 'QQQ', 'AMC', 'GME', 'TSLA']
for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='2d')
        if len(hist) >= 2:
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            change = ((current - prev) / prev) * 100
            volume = hist['Volume'].iloc[-1] / 1e6
            print(f'{ticker}: \${current:.2f} ({change:+.1f}%) Vol: {volume:.1f}M')
    except: pass
"
```

---

## 🎯 WHAT TO EXPECT

### **Before API Keys:**
```
🚨 CRITICAL ERROR: API keys not configured
🛑 TRADING DISABLED: Safety protection active
💡 Configure Replit Secrets for real data
```

### **After API Keys:**
```
✅ SAFETY CHECK PASSED
🔍 Found 2 real opportunities: AMC (+10.8%), [others]
🤖 Real AI analysis: Claude vs ChatGPT debate
📊 Portfolio: AMD +1.9%, BLNK -5.4%
```

### **Discovery Results:**
- **Real stocks** with actual price moves
- **Live volume spikes** and momentum
- **Genuine market opportunities**
- **No mock recommendations**

---

## 🔧 IF SOMETHING DOESN'T WORK

### **Import Errors:**
```bash
pip install yfinance aiohttp pandas
```

### **API Errors:**
- Check **Replit Secrets tab**
- Verify **exact key names**
- **Restart Repl** after adding secrets

### **No Opportunities Found:**
- ✅ **Normal** during low-volatility periods
- ✅ **System working** correctly
- Try different timeframes: `'week'` or `'month'`

---

**Run these commands in your updated Replit to see your enhanced AI trading system in action! 🚀**