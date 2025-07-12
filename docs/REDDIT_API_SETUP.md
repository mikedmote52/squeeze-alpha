# 🚀 Reddit API Setup Guide

Get **FREE** access to Reddit sentiment analysis for your Squeeze Alpha system!

## 📋 **Step-by-Step Setup**

### **1. Create Reddit Account**
- Go to [reddit.com](https://reddit.com) and create an account (if you don't have one)
- Verify your email address

### **2. Create Reddit App**
- Go to [reddit.com/prefs/apps](https://reddit.com/prefs/apps)
- Click **"Create App"** or **"Create Another App"**
- Fill out the form:
  - **Name**: `Squeeze Alpha Bot`
  - **App type**: Select **"script"**
  - **Description**: `AI trading sentiment analysis`
  - **About URL**: Leave blank
  - **Redirect URI**: `http://localhost:8080` (required but not used)
- Click **"Create app"**

### **3. Get Your API Credentials**
After creating the app, you'll see:
- **Client ID**: The string under your app name (looks like: `abc123def456`)
- **Client Secret**: The "secret" field (looks like: `xyz789uvw012-abc456`)

### **4. Add to Replit Secrets**
In your Replit project:
1. Click the **"Secrets"** tab (lock icon)
2. Add these two secrets:
   - **Key**: `REDDIT_CLIENT_ID` **Value**: Your client ID
   - **Key**: `REDDIT_CLIENT_SECRET` **Value**: Your client secret

### **5. Test the Integration**
- Run your Replit app
- Click any stock ticker
- You should see enhanced thesis with Reddit sentiment!

## 🎯 **What You'll Get**

### **General Market Sentiment**
- **r/wallstreetbets**: Meme stock momentum (weighted 1.5x)
- **r/stocks**: General market sentiment  
- **r/investing**: Long-term sentiment (weighted 0.5x)

### **Ticker-Specific Analysis**
- **Daily mentions** of your holdings across all trading subreddits
- **Sentiment analysis** using WSB keywords (moon, rocket, diamond hands, etc.)
- **Engagement weighting** (higher upvotes = more influence)
- **Subreddit weighting** (WSB gets 2x weight for momentum)

## 📊 **Sentiment Impact**

### **Very Bullish Reddit (+15% success probability)**
- **Example**: "VIGL exhibits micro-float characteristics with strong Reddit momentum - 100% success probability"

### **Bullish Reddit (+8% success probability)**  
- **Example**: "AMD shows technical strength with positive Reddit sentiment supporting breakout"

### **Bearish Reddit (-15% success probability)**
- **Example**: "WOLF technical analysis suggests caution due to negative Reddit sentiment"

## 🔥 **WSB Keywords Tracked**

**Bullish**: moon, rocket, diamond hands, hodl, squeeze, pump, yolo, ape, tendies, lambo, stonks

**Bearish**: crash, dump, puts, sell, short, drop, rip, dead, overvalued, bubble

## ⚡ **API Limits**
- **Free tier**: 60 requests per minute
- **Your usage**: ~10 requests per thesis generation
- **Recommendation**: Perfect for real-time analysis

## 🚨 **Troubleshooting**

### **"Auth failed" error**
- Double-check your Client ID and Secret in Replit
- Make sure you selected "script" app type
- Verify your Reddit account is verified

### **"No data" results**
- Reddit API can be slow sometimes - this is normal
- System falls back to general market analysis
- Try again in a few minutes

## 🎉 **Ready to Go!**

Once set up, your system will automatically:
- **Detect meme stock momentum** before institutional players
- **Identify Reddit squeeze targets** 
- **Warn about bearish sentiment** shifts
- **Track WSB favorites** and sentiment changes
- **Enhance success probabilities** with social data

Your Squeeze Alpha system just became **retail sentiment aware**! 🚀