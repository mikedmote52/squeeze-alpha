# 🔧 REPLIT TROUBLESHOOTING - Fix "Run Button Not Working"

## 🚨 IMMEDIATE FIXES

### **Problem: "Run" Button Does Nothing**

**Solution 1: Upload Required Files**
Upload these 3 files to make Run button work:
- `main.py` (Main entry point)
- `.replit` (Run configuration)  
- `replit.nix` (Environment setup)

**Solution 2: Try Manual Commands**
If Run button still doesn't work, use the Shell tab:

```bash
# Test basic functionality
python3 main.py

# Or run specific tests
python3 setup_replit_secrets.py
python3 core/trading_safety_validator.py
python3 core/real_time_stock_discovery.py
```

---

## 🛠️ STEP-BY-STEP FIX

### **Step 1: Check File Structure**
Your Replit should have:
```
├── main.py                    ← Main entry point
├── .replit                    ← Run configuration
├── replit.nix                 ← Environment setup
├── core/
│   ├── trading_safety_validator.py
│   ├── secrets_manager.py
│   ├── real_time_stock_discovery.py
│   └── [other core files]
├── setup_replit_secrets.py
└── test_api_keys.py
```

### **Step 2: Install Dependencies**
In Shell tab, run:
```bash
pip install yfinance pandas aiohttp requests
```

### **Step 3: Test Individual Components**
```bash
# Test 1: Check if Python works
python3 --version

# Test 2: Test API setup
python3 setup_replit_secrets.py

# Test 3: Test safety system
python3 core/trading_safety_validator.py

# Test 4: Test discovery
python3 core/real_time_stock_discovery.py
```

---

## 🔍 COMMON ISSUES & FIXES

### **Issue 1: Import Errors**
```
ModuleNotFoundError: No module named 'yfinance'
```
**Fix:**
```bash
pip install yfinance pandas aiohttp
```

### **Issue 2: File Not Found**
```
FileNotFoundError: [Errno 2] No such file or directory
```
**Fix:** Make sure you uploaded all required files from `FILES_TO_UPLOAD.txt`

### **Issue 3: Permission Errors**
```
PermissionError: [Errno 13] Permission denied
```
**Fix:**
```bash
chmod +x main.py
python3 main.py
```

### **Issue 4: Secrets Not Loading**
```
❌ ANTHROPIC_API_KEY: MISSING
```
**Fix:** 
1. Click "Secrets" tab in Replit sidebar
2. Add your API keys exactly as shown
3. Restart your Repl (stop and run again)

---

## 🚀 ALTERNATIVE LAUNCH METHODS

### **Method 1: Direct Shell Commands**
```bash
# Quick discovery test
python3 -c "
import sys; sys.path.append('core')
from real_time_stock_discovery import RealTimeStockDiscovery
import asyncio

async def test():
    discovery = RealTimeStockDiscovery()
    candidates = await discovery.discover_live_explosive_opportunities('today')
    print(f'Found {len(candidates)} opportunities!')
    for c in candidates[:2]:
        print(f'• {c.ticker}: {c.price_change_1d:+.1f}%')

asyncio.run(test())
"
```

### **Method 2: Portfolio Analysis**
```bash
# Quick portfolio check
python3 -c "
import yfinance as yf
holdings = ['AMD', 'NVAX', 'WOLF', 'BTBT']
print('📊 PORTFOLIO CHECK')
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
"
```

### **Method 3: API Status Check**
```bash
# Check API configuration
python3 -c "
import os
print('🔑 API STATUS:')
print(f'Anthropic: {\"✅\" if os.getenv(\"ANTHROPIC_API_KEY\") else \"❌\"}')
print(f'OpenAI: {\"✅\" if os.getenv(\"OPENAI_API_KEY\") else \"❌\"}')
print(f'Alpaca: {\"✅\" if os.getenv(\"ALPACA_API_KEY\") else \"❌\"}')
print(f'Perplexity: {\"✅\" if os.getenv(\"PERPLEXITY_API_KEY\") else \"❌\"}')
"
```

---

## 🎯 EXPECTED WORKING OUTPUT

### **When Run Button Works:**
```
🚀 AI TRADING SYSTEM - REPLIT LAUNCHER
============================================================
📅 2024-07-11 15:30:00

🔍 AVAILABLE COMMANDS:
1. 🔑 Check API Keys Status
2. 🛡️ Run Safety Validation
3. 📊 Test Stock Discovery
4. 💰 Analyze Portfolio
5. 🚀 Start Full System
6. 🧪 Quick Market Scan

Enter your choice (1-6) or 'q' to quit:
```

### **When Discovery Works:**
```
🔍 REAL-TIME STOCK DISCOVERY - TODAY
================================================================================
📊 Scanning live market data for explosive opportunities...
✅ Found 2 real-time explosive opportunities

🎯 TOP REAL-TIME OPPORTUNITIES:
1. AMC - AMC Entertainment Holdings, Inc.
   Price: $3.33 (+10.8% today)
   Volume: 2.4x normal
```

---

## ⚡ QUICK START CHECKLIST

- [ ] Upload `main.py`, `.replit`, `replit.nix`
- [ ] Upload all files from `FILES_TO_UPLOAD.txt`
- [ ] Add API keys to Secrets tab
- [ ] Install dependencies: `pip install yfinance pandas aiohttp`
- [ ] Test Run button or use Shell commands
- [ ] Verify API status with option 1 in menu

---

**If nothing works, try the Shell commands directly - they'll show you exactly what's happening! 🔧**