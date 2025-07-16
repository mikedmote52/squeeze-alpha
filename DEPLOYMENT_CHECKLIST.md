# 🚀 SQUEEZE ALPHA DEPLOYMENT CHECKLIST

## ✅ ONE-TIME SETUP (Do this once)

### 1. Render Secret Files
Go to Render Dashboard → Your Service → Environment → Secret Files
Create `.env` file with:
```
ALPACA_API_KEY=your_alpaca_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_here
OPENROUTER_API_KEY=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
ALPHA_VANTAGE_API_KEY=IN84O862OXIYYX8B
FMP_API_KEY=CA25ofSLfa1mBftG4L4oFQvKUwtlhRfU
SLACK_WEBHOOK=https://hooks.slack.com/services/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
```

### 2. Verify Files Are Present
- ✅ `direct_alpaca_service.py` - Gets real portfolio data from Alpaca
- ✅ `integrated_portfolio_tiles.py` - Shows all data inside tiles
- ✅ `pages/01_🏠_Portfolio_Dashboard.py` - Portfolio Dashboard page
- ✅ `system_diagnostic.py` - Health check script

## 🔄 EVERY DEPLOYMENT

### 1. Deploy Latest Commit
- Go to Render Dashboard
- Click "Deploy latest commit"
- Wait for deployment to complete

### 2. Test System
- Visit: `https://squeeze-alpha.onrender.com/Portfolio_Dashboard`
- Should see integrated tiles with all data inside
- Data should be real from your Alpaca account

### 3. If Issues Occur
- Check deployment logs in Render
- Look for error messages
- Common issues:
  - Missing API keys → Add to Secret Files
  - Syntax errors → Check recent commits
  - Import errors → Verify file structure

## 🎯 WHAT YOU SHOULD SEE

### Portfolio Dashboard
- URL: `https://squeeze-alpha.onrender.com/Portfolio_Dashboard`
- Tiles with ALL data inside each tile:
  - Quantity
  - Avg Cost  
  - Current Price
  - Market Value
  - P&L Amount
  - AI Rating
- Clickable tiles for trading
- Real portfolio data from Alpaca
- Real AI analysis from OpenRouter

### Mobile Access
- Works on iPhone/Android
- Responsive design
- All functionality available on mobile

## 🚨 TROUBLESHOOTING

### If Portfolio Dashboard Shows No Data
1. Check Alpaca API keys in Render Secret Files
2. Verify keys have correct permissions
3. Check deployment logs for errors

### If AI Analysis Not Working
1. Verify OpenRouter API key in Secret Files
2. Check API key has sufficient credits
3. Test with different stocks

### If Tiles Don't Show All Data Inside
1. Clear browser cache
2. Hard refresh page (Ctrl+F5)
3. Check recent deployment completed

## 📞 SUPPORT

If system still doesn't work after following this checklist:
1. Check deployment logs in Render
2. Run diagnostic script locally: `python3 system_diagnostic.py`
3. Share specific error messages for debugging

## 🎉 SUCCESS CRITERIA

✅ Portfolio Dashboard loads without errors
✅ Real portfolio positions displayed
✅ All 6 data points inside each tile
✅ AI analysis shows real recommendations
✅ Trading buttons functional
✅ Mobile responsive design
✅ No fake/mock data anywhere

This system is now bulletproof and self-contained!