# 🎯 Replit Drag & Drop Setup Instructions

## Files Ready for Drag & Drop

I've created 2 simple files in your `ai-trading-system-complete` folder:

### **📂 Files to Drag into Replit:**

1. **`web_app_simple.py`** → Rename to `web_app.py` in Replit
2. **`trade_execution_simple.html`** → Put in `templates/` folder in Replit

## **🚀 Step-by-Step Setup:**

### **1. Create Templates Folder in Replit**
- In Replit, create a new folder called `templates`

### **2. Drag & Drop Files**
- Drag `web_app_simple.py` → Rename to `web_app.py`
- Drag `trade_execution_simple.html` → Put in `templates/trade_execution.html`

### **3. Install Flask**
In Replit Shell:
```bash
pip install flask
```

### **4. Update Your .env File**
Add these lines to your `.env` file in Replit:
```bash
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAACYh3AEAAAAAhLnECQo%2FBzFHd1CzhfWcQFSXKmM%3DR4FGyep7bBaxjnxwNZLTyMhgoawO2ZmXD9snHESZzV8xzdY50O
BENZINGA_API_KEY=bz.JOBHAC4OHSH24DRI7X53W2EE7OXGU4QS
```

### **5. Run Your Trading System**
```bash
python web_app.py
```

### **6. Access Your Trading Interface**
- Click the web preview in Replit
- Go to `/trades` to see your trading interface
- Try the sliders and controls!

## **🎮 What You'll See:**

✅ **Beautiful Trading Interface** with:
- Portfolio overview ($99,809.68)
- AMD recommendation with 85% confidence
- Interactive sliders to adjust share quantities
- Dry run vs live trading toggle
- Execute button with confirmations

✅ **Working Features:**
- Adjust shares with sliders (0-10 shares)
- See dollar amounts update in real-time
- Approve trades with checkboxes
- Toggle between dry run and live modes
- Execute trades with safety confirmations

## **🔥 This Gets You Running Immediately!**

This simplified version gives you the core trading interface experience. Once this works, you can add the advanced features like:
- Real portfolio data from Alpaca
- Live AI recommendations
- Multiple stock analysis
- Complete intelligence integration

**Just drag, drop, and start trading! 🚀**