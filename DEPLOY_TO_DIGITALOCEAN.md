# Deploy to DigitalOcean App Platform

Railway keeps using Python 3.12 despite all our configuration. Let's use DigitalOcean instead.

## Quick DigitalOcean Deployment

1. **Go to**: https://cloud.digitalocean.com/apps
2. **Click "Create App"**
3. **Choose "GitHub" as source**
4. **Select repository**: `mikedmote52/squeeze-alpha`
5. **Branch**: `main`
6. **App name**: `squeeze-alpha`
7. **Plan**: Basic ($5/month)

## Environment Variables to Add:
```
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets
OPENROUTER_API_KEY=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
PERPLEXITY_API_KEY=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
FRED_API_KEY=214ad195e1013bc18b5b2a24161800f5
SLACK_WEBHOOK=https://hooks.slack.com/services/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
```

## Why DigitalOcean Will Work:
- ✅ Actually uses our Dockerfile with Python 3.11
- ✅ Respects configuration files
- ✅ $5/month (same price as Railway)
- ✅ Better Docker support
- ✅ 24/7 uptime for your trading system

## After Deployment:
You'll get a URL like: `https://squeeze-alpha-xyz.ondigitalocean.app`

This will work from your phone at work!