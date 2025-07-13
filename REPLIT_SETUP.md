# 🚀 Replit Setup Instructions

## Step 1: Create New Repl
1. Go to https://replit.com
2. Click "Create Repl"
3. Choose "Python"
4. Name it "AI-Trading-System"

## Step 2: Upload Files
Copy these files to your Repl:

### Core Files (REQUIRED):
```
main.py
core/catalyst_discovery_engine.py
core/discovery_system_tracker.py
core/alpha_engine_enhanced.py (if exists)
core/real_time_stock_discovery.py (if exists)
data/README.md
```

### Dependencies File:
Create `requirements.txt`:
```
flask
yfinance
aiohttp
requests
asyncio
dataclasses
```

## Step 3: Environment Variables
In Replit Secrets tab, add:
```
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key  
OPENROUTER_API_KEY=your_openrouter_key
PERPLEXITY_API_KEY=your_perplexity_key (optional)
```

## Step 4: Run
1. Click "Run" button
2. Replit will auto-install dependencies
3. Your app will be live at: https://your-repl-name.your-username.repl.co

## Mobile Access:
- Open the URL on your phone
- Add to home screen for app-like experience
- Works on iOS/Android browsers

## File Structure in Replit:
```
AI-Trading-System/
├── main.py
├── requirements.txt
├── core/
│   ├── catalyst_discovery_engine.py
│   ├── discovery_system_tracker.py
│   └── alpha_engine_enhanced.py
└── data/
    └── README.md
```

## Pro Tips:
- Replit keeps your app running 24/7 (with paid plan)
- Free tier sleeps after inactivity but wakes up instantly
- Mobile interface is automatically responsive
- Can share with friends via public URL