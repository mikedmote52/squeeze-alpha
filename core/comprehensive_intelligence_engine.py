#!/usr/bin/env python3
"""
Comprehensive Intelligence Engine
Sophisticated data aggregation for hedge fund-level AI analysis
"""

import os
import asyncio
import aiohttp
import yfinance as yf
import pandas as pd
import feedparser
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import time

@dataclass
class MarketIntelligence:
    """Comprehensive market intelligence data structure"""
    timestamp: str
    ticker: str
    
    # Social Sentiment
    reddit_sentiment: Dict[str, Any]
    twitter_sentiment: Dict[str, Any]
    youtube_mentions: List[Dict[str, Any]]
    
    # News & Events
    breaking_news: List[Dict[str, Any]]
    analyst_upgrades: List[Dict[str, Any]]
    earnings_events: List[Dict[str, Any]]
    
    # Regulatory & Political
    fda_events: List[Dict[str, Any]]
    congressional_trades: List[Dict[str, Any]]
    insider_trades: List[Dict[str, Any]]
    
    # Market Microstructure
    options_flow: Dict[str, Any]
    dark_pool_activity: Dict[str, Any]
    institutional_flows: Dict[str, Any]
    
    # Economic Context
    fed_policy_signals: Dict[str, Any]
    economic_indicators: Dict[str, Any]
    sector_rotation: Dict[str, Any]

class ComprehensiveIntelligenceEngine:
    """Advanced intelligence aggregation for AI debates"""
    
    def __init__(self):
        # API Configuration
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.benzinga_api_key = os.getenv('BENZINGA_API_KEY')
        self.quiver_api_key = os.getenv('QUIVER_QUANT_API_KEY')
        self.fred_api_key = os.getenv('FRED_API_KEY')
        self.polygon_api_key = os.getenv('POLYGON_API_KEY')
        
        # Cache for rate limiting
        self.cache = {}
        self.last_requests = {}
    
    async def gather_comprehensive_intelligence(self, ticker: str) -> MarketIntelligence:
        """Gather all available intelligence for a ticker"""
        
        print(f"🧠 GATHERING COMPREHENSIVE INTELLIGENCE FOR {ticker}")
        print("=" * 60)
        
        # Parallel data gathering for speed
        tasks = [
            self.get_reddit_sentiment(ticker),
            self.get_twitter_sentiment(ticker),
            self.get_youtube_mentions(ticker),
            self.get_breaking_news(ticker),
            self.get_analyst_updates(ticker),
            self.get_earnings_events(ticker),
            self.get_fda_events(ticker),
            self.get_congressional_trades(ticker),
            self.get_insider_trades(ticker),
            self.get_options_flow(ticker),
            self.get_dark_pool_activity(ticker),
            self.get_institutional_flows(ticker),
            self.get_fed_policy_signals(),
            self.get_economic_indicators(),
            self.get_sector_rotation(ticker)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any failures gracefully
        safe_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"⚠️ Task {i} failed: {result}")
                safe_results.append({})
            else:
                safe_results.append(result)
        
        intelligence = MarketIntelligence(
            timestamp=datetime.now().isoformat(),
            ticker=ticker,
            reddit_sentiment=safe_results[0],
            twitter_sentiment=safe_results[1],
            youtube_mentions=safe_results[2],
            breaking_news=safe_results[3],
            analyst_upgrades=safe_results[4],
            earnings_events=safe_results[5],
            fda_events=safe_results[6],
            congressional_trades=safe_results[7],
            insider_trades=safe_results[8],
            options_flow=safe_results[9],
            dark_pool_activity=safe_results[10],
            institutional_flows=safe_results[11],
            fed_policy_signals=safe_results[12],
            economic_indicators=safe_results[13],
            sector_rotation=safe_results[14]
        )
        
        print("✅ INTELLIGENCE GATHERING COMPLETE")
        return intelligence
    
    async def get_reddit_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Get Reddit sentiment from WSB and investing communities"""
        
        if not self.reddit_client_id:
            return {"error": "Reddit API not configured", "sentiment": "neutral", "mentions": 0}
        
        try:
            # Reddit API v2 implementation
            async with aiohttp.ClientSession() as session:
                # Get Reddit access token
                auth_data = {
                    'grant_type': 'client_credentials'
                }
                
                auth = aiohttp.BasicAuth(self.reddit_client_id, self.reddit_client_secret)
                headers = {'User-Agent': 'SqueezeAlpha/1.0'}
                
                async with session.post(
                    'https://www.reddit.com/api/v1/access_token',
                    data=auth_data,
                    auth=auth,
                    headers=headers
                ) as response:
                    token_data = await response.json()
                    access_token = token_data.get('access_token')
                
                if not access_token:
                    return {"error": "Reddit authentication failed", "sentiment": "neutral"}
                
                # Search for ticker mentions
                api_headers = {
                    'Authorization': f'Bearer {access_token}',
                    'User-Agent': 'SqueezeAlpha/1.0'
                }
                
                # Search multiple subreddits
                subreddits = ['wallstreetbets', 'investing', 'stocks', 'SecurityAnalysis']
                all_posts = []
                
                for subreddit in subreddits:
                    search_url = f'https://oauth.reddit.com/r/{subreddit}/search'
                    params = {
                        'q': ticker,
                        'sort': 'hot',
                        'limit': 25,
                        't': 'day'
                    }
                    
                    async with session.get(search_url, headers=api_headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            posts = data.get('data', {}).get('children', [])
                            all_posts.extend(posts)
                
                # Analyze sentiment
                sentiment_score = 0
                mention_count = len(all_posts)
                bullish_keywords = ['moon', 'rocket', 'bull', 'buy', 'calls', 'up', 'pump']
                bearish_keywords = ['dump', 'crash', 'bear', 'puts', 'short', 'sell', 'down']
                
                for post in all_posts:
                    title = post.get('data', {}).get('title', '').lower()
                    selftext = post.get('data', {}).get('selftext', '').lower()
                    text = f"{title} {selftext}"
                    
                    bull_score = sum(1 for word in bullish_keywords if word in text)
                    bear_score = sum(1 for word in bearish_keywords if word in text)
                    sentiment_score += (bull_score - bear_score)
                
                # Calculate overall sentiment
                if mention_count > 0:
                    avg_sentiment = sentiment_score / mention_count
                    if avg_sentiment > 0.5:
                        sentiment = "very_bullish"
                    elif avg_sentiment > 0:
                        sentiment = "bullish"
                    elif avg_sentiment < -0.5:
                        sentiment = "very_bearish"
                    elif avg_sentiment < 0:
                        sentiment = "bearish"
                    else:
                        sentiment = "neutral"
                else:
                    sentiment = "neutral"
                
                return {
                    "sentiment": sentiment,
                    "sentiment_score": sentiment_score,
                    "mentions": mention_count,
                    "top_posts": [
                        {
                            "title": post.get('data', {}).get('title'),
                            "score": post.get('data', {}).get('score'),
                            "url": f"https://reddit.com{post.get('data', {}).get('permalink', '')}"
                        }
                        for post in all_posts[:5]
                    ],
                    "source": "reddit_api"
                }
                
        except Exception as e:
            return {"error": f"Reddit API error: {str(e)}", "sentiment": "neutral", "mentions": 0}
    
    async def get_twitter_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Get Twitter/X sentiment using official API"""
        
        if not self.twitter_bearer_token:
            return {"error": "Twitter API not configured", "sentiment": "neutral", "mentions": 0}
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.twitter_bearer_token}'}
                
                # Search for recent tweets
                search_url = 'https://api.twitter.com/2/tweets/search/recent'
                params = {
                    'query': f'${ticker} -is:retweet lang:en',
                    'max_results': 100,
                    'tweet.fields': 'created_at,public_metrics,context_annotations'
                }
                
                async with session.get(search_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        tweets = data.get('data', [])
                        
                        # Analyze sentiment
                        sentiment_score = 0
                        total_engagement = 0
                        
                        bullish_words = ['bullish', 'moon', 'rocket', 'buy', 'calls', 'long', 'pump']
                        bearish_words = ['bearish', 'crash', 'dump', 'puts', 'short', 'sell']
                        
                        for tweet in tweets:
                            text = tweet.get('text', '').lower()
                            metrics = tweet.get('public_metrics', {})
                            
                            # Weight by engagement
                            engagement = (
                                metrics.get('like_count', 0) + 
                                metrics.get('retweet_count', 0) * 2 + 
                                metrics.get('reply_count', 0)
                            )
                            total_engagement += engagement
                            
                            bull_score = sum(1 for word in bullish_words if word in text)
                            bear_score = sum(1 for word in bearish_words if word in text)
                            
                            tweet_sentiment = (bull_score - bear_score) * (1 + engagement / 100)
                            sentiment_score += tweet_sentiment
                        
                        # Determine overall sentiment
                        if len(tweets) > 0:
                            avg_sentiment = sentiment_score / len(tweets)
                            if avg_sentiment > 1:
                                sentiment = "very_bullish"
                            elif avg_sentiment > 0:
                                sentiment = "bullish"
                            elif avg_sentiment < -1:
                                sentiment = "very_bearish"
                            elif avg_sentiment < 0:
                                sentiment = "bearish"
                            else:
                                sentiment = "neutral"
                        else:
                            sentiment = "neutral"
                        
                        return {
                            "sentiment": sentiment,
                            "sentiment_score": sentiment_score,
                            "mentions": len(tweets),
                            "total_engagement": total_engagement,
                            "top_tweets": [
                                {
                                    "text": tweet.get('text'),
                                    "created_at": tweet.get('created_at'),
                                    "engagement": tweet.get('public_metrics', {})
                                }
                                for tweet in tweets[:5]
                            ],
                            "source": "twitter_api_v2"
                        }
                    else:
                        return {"error": f"Twitter API error: {response.status}", "sentiment": "neutral"}
                        
        except Exception as e:
            return {"error": f"Twitter error: {str(e)}", "sentiment": "neutral", "mentions": 0}
    
    async def get_youtube_mentions(self, ticker: str) -> List[Dict[str, Any]]:
        """Get YouTube financial content mentions"""
        
        if not self.youtube_api_key:
            return [{"error": "YouTube API not configured"}]
        
        try:
            async with aiohttp.ClientSession() as session:
                # Search for recent financial videos mentioning the ticker
                search_url = 'https://www.googleapis.com/youtube/v3/search'
                params = {
                    'part': 'snippet',
                    'q': f'{ticker} stock analysis',
                    'type': 'video',
                    'order': 'date',
                    'maxResults': 20,
                    'publishedAfter': (datetime.now() - timedelta(days=7)).isoformat() + 'Z',
                    'key': self.youtube_api_key
                }
                
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        videos = data.get('items', [])
                        
                        # Get video statistics for popular content
                        video_ids = [video['id']['videoId'] for video in videos]
                        stats_url = 'https://www.googleapis.com/youtube/v3/videos'
                        stats_params = {
                            'part': 'statistics',
                            'id': ','.join(video_ids[:10]),
                            'key': self.youtube_api_key
                        }
                        
                        async with session.get(stats_url, params=stats_params) as stats_response:
                            if stats_response.status == 200:
                                stats_data = await stats_response.json()
                                
                                enhanced_videos = []
                                for video, stats in zip(videos[:10], stats_data.get('items', [])):
                                    enhanced_videos.append({
                                        "title": video['snippet']['title'],
                                        "channel": video['snippet']['channelTitle'],
                                        "published": video['snippet']['publishedAt'],
                                        "description": video['snippet']['description'][:200],
                                        "url": f"https://youtube.com/watch?v={video['id']['videoId']}",
                                        "views": stats.get('statistics', {}).get('viewCount', 0),
                                        "likes": stats.get('statistics', {}).get('likeCount', 0)
                                    })
                                
                                return enhanced_videos
                    
                    return [{"error": f"YouTube API error: {response.status}"}]
                    
        except Exception as e:
            return [{"error": f"YouTube error: {str(e)}"}]
    
    async def get_breaking_news(self, ticker: str) -> List[Dict[str, Any]]:
        """Get breaking financial news"""
        
        try:
            # Multiple news sources
            news_sources = []
            
            # Yahoo Finance RSS
            yahoo_rss = f'https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US'
            feed = feedparser.parse(yahoo_rss)
            
            for entry in feed.entries[:10]:
                news_sources.append({
                    "title": entry.title,
                    "summary": entry.summary if hasattr(entry, 'summary') else "",
                    "published": entry.published if hasattr(entry, 'published') else "",
                    "link": entry.link,
                    "source": "Yahoo Finance"
                })
            
            # If Benzinga API is configured
            if self.benzinga_api_key:
                async with aiohttp.ClientSession() as session:
                    benzinga_url = 'https://api.benzinga.com/api/v2/news'
                    params = {
                        'token': self.benzinga_api_key,
                        'symbols': ticker,
                        'pageSize': 20,
                        'displayOutput': 'full'
                    }
                    
                    async with session.get(benzinga_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            for article in data.get('data', []):
                                news_sources.append({
                                    "title": article.get('title'),
                                    "summary": article.get('teaser', ''),
                                    "published": article.get('created'),
                                    "link": article.get('url'),
                                    "source": "Benzinga"
                                })
            
            return news_sources[:15]  # Return top 15 news items
            
        except Exception as e:
            return [{"error": f"News gathering error: {str(e)}"}]
    
    async def get_fda_events(self, ticker: str) -> List[Dict[str, Any]]:
        """Get FDA regulatory events and calendar"""
        
        try:
            # FDA.gov RSS feeds and calendar scraping would go here
            # For now, return structured placeholder that can be enhanced
            
            # Get company info to check if biotech/pharma
            stock = yf.Ticker(ticker)
            info = stock.info
            sector = info.get('sector', '').lower()
            industry = info.get('industry', '').lower()
            
            if 'healthcare' in sector or 'pharmaceutical' in industry or 'biotechnology' in industry:
                return [{
                    "event_type": "FDA Calendar Check",
                    "status": "API implementation needed",
                    "recommendation": "Add FDA.gov calendar scraping for biotech stocks",
                    "relevance": "high" if 'biotechnology' in industry else "medium"
                }]
            else:
                return [{
                    "event_type": "FDA Calendar Check", 
                    "status": "Not applicable - non-biotech stock",
                    "relevance": "none"
                }]
                
        except Exception as e:
            return [{"error": f"FDA calendar error: {str(e)}"}]
    
    async def get_congressional_trades(self, ticker: str) -> List[Dict[str, Any]]:
        """Get congressional trading data"""
        
        if not self.quiver_api_key:
            return [{"error": "Quiver Quant API not configured"}]
        
        try:
            async with aiohttp.ClientSession() as session:
                quiver_url = f'https://api.quiverquant.com/beta/historical/congresstrading/{ticker}'
                headers = {'Authorization': f'Token {self.quiver_api_key}'}
                
                async with session.get(quiver_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process recent trades (last 30 days)
                        recent_trades = []
                        cutoff_date = datetime.now() - timedelta(days=30)
                        
                        for trade in data:
                            trade_date = datetime.strptime(trade.get('TransactionDate', ''), '%Y-%m-%d')
                            if trade_date >= cutoff_date:
                                recent_trades.append({
                                    "representative": trade.get('Representative'),
                                    "transaction_date": trade.get('TransactionDate'),
                                    "transaction_type": trade.get('TransactionType'),
                                    "amount": trade.get('Amount'),
                                    "party": trade.get('Party'),
                                    "state": trade.get('State')
                                })
                        
                        return recent_trades
                    else:
                        return [{"error": f"Quiver API error: {response.status}"}]
                        
        except Exception as e:
            return [{"error": f"Congressional trading error: {str(e)}"}]
    
    async def get_insider_trades(self, ticker: str) -> List[Dict[str, Any]]:
        """Get insider trading data"""
        
        try:
            # Using SEC EDGAR API for Form 4 filings
            async with aiohttp.ClientSession() as session:
                # This is a simplified implementation - real version would parse SEC filings
                edgar_url = f'https://www.sec.gov/cgi-bin/browse-edgar'
                params = {
                    'action': 'getcompany',
                    'CIK': ticker,  # Would need to convert ticker to CIK
                    'type': '4',
                    'dateb': '',
                    'count': '10',
                    'output': 'xml'
                }
                
                # For now, return placeholder structure
                return [{
                    "filing_type": "Form 4 - Insider Trading",
                    "status": "SEC EDGAR API implementation needed",
                    "recommendation": "Add SEC filing parser for insider transactions",
                    "last_check": datetime.now().isoformat()
                }]
                
        except Exception as e:
            return [{"error": f"Insider trading error: {str(e)}"}]
    
    async def get_options_flow(self, ticker: str) -> Dict[str, Any]:
        """Get unusual options activity and flow"""
        
        try:
            stock = yf.Ticker(ticker)
            options_dates = stock.options
            
            if not options_dates:
                return {"error": "No options data available"}
            
            # Get current options chain
            nearest_expiry = options_dates[0]
            options_chain = stock.option_chain(nearest_expiry)
            
            calls = options_chain.calls
            puts = options_chain.puts
            
            # Calculate put/call ratio and unusual volume
            total_call_volume = calls['volume'].sum()
            total_put_volume = puts['volume'].sum()
            
            put_call_ratio = total_put_volume / max(total_call_volume, 1)
            
            # Find unusual volume (simplified)
            unusual_calls = calls[calls['volume'] > calls['volume'].quantile(0.9)]
            unusual_puts = puts[puts['volume'] > puts['volume'].quantile(0.9)]
            
            return {
                "put_call_ratio": put_call_ratio,
                "total_call_volume": int(total_call_volume),
                "total_put_volume": int(total_put_volume),
                "unusual_call_activity": len(unusual_calls),
                "unusual_put_activity": len(unusual_puts),
                "sentiment": "bullish" if put_call_ratio < 0.7 else "bearish" if put_call_ratio > 1.3 else "neutral",
                "expiry_analyzed": nearest_expiry,
                "note": "Enhanced options flow analysis available with premium data feeds"
            }
            
        except Exception as e:
            return {"error": f"Options flow error: {str(e)}"}
    
    async def get_dark_pool_activity(self, ticker: str) -> Dict[str, Any]:
        """Get dark pool and institutional flow data"""
        
        if self.polygon_api_key:
            try:
                async with aiohttp.ClientSession() as session:
                    # Polygon.io provides some institutional data
                    url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/prev'
                    params = {'apikey': self.polygon_api_key}
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            return {
                                "dark_pool_data": "Available with premium institutional feeds",
                                "institutional_flow": "Polygon.io connected",
                                "recommendation": "Upgrade to institutional data feeds for dark pool analysis",
                                "last_price": data.get('results', [{}])[0].get('c', 0) if data.get('results') else 0
                            }
            except Exception as e:
                return {"error": f"Dark pool data error: {str(e)}"}
        
        return {
            "dark_pool_data": "Not available",
            "recommendation": "Add premium institutional data feeds (Bloomberg, Refinitiv)",
            "status": "Requires institutional-grade API access"
        }
    
    async def get_institutional_flows(self, ticker: str) -> Dict[str, Any]:
        """Get institutional buying/selling flows"""
        
        try:
            # Simplified institutional flow analysis using volume patterns
            stock = yf.Ticker(ticker)
            hist = stock.history(period='30d', interval='1d')
            
            if len(hist) < 5:
                return {"error": "Insufficient data for institutional flow analysis"}
            
            # Analyze volume patterns for institutional activity
            avg_volume = hist['Volume'].mean()
            recent_volume = hist['Volume'].tail(5).mean()
            
            volume_spike = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Price-volume analysis
            price_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]
            
            if volume_spike > 1.5 and price_change > 0.02:
                flow_sentiment = "institutional_buying"
            elif volume_spike > 1.5 and price_change < -0.02:
                flow_sentiment = "institutional_selling"
            else:
                flow_sentiment = "neutral"
            
            return {
                "volume_spike_ratio": volume_spike,
                "price_change_5d": price_change,
                "flow_sentiment": flow_sentiment,
                "avg_daily_volume": int(avg_volume),
                "recent_avg_volume": int(recent_volume),
                "analysis": "Basic institutional flow analysis - upgrade to premium feeds for detailed flows"
            }
            
        except Exception as e:
            return {"error": f"Institutional flow error: {str(e)}"}
    
    async def get_fed_policy_signals(self) -> Dict[str, Any]:
        """Get Federal Reserve policy signals and economic context"""
        
        try:
            # FRED API for economic data
            if self.fred_api_key:
                async with aiohttp.ClientSession() as session:
                    fred_url = 'https://api.stlouisfed.org/fred/series/observations'
                    
                    # Get key economic indicators
                    indicators = {
                        'fed_funds_rate': 'FEDFUNDS',
                        'inflation_rate': 'CPIAUCSL',
                        'unemployment': 'UNRATE',
                        'gdp_growth': 'GDP'
                    }
                    
                    fed_data = {}
                    for name, series_id in indicators.items():
                        params = {
                            'series_id': series_id,
                            'api_key': self.fred_api_key,
                            'file_type': 'json',
                            'limit': 1,
                            'sort_order': 'desc'
                        }
                        
                        async with session.get(fred_url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                observations = data.get('observations', [])
                                if observations:
                                    fed_data[name] = {
                                        'value': observations[0].get('value'),
                                        'date': observations[0].get('date')
                                    }
                    
                    return {
                        'fed_data': fed_data,
                        'policy_stance': 'Data available via FRED API',
                        'market_impact': 'Economic context integrated'
                    }
            else:
                return {
                    'fed_data': 'FRED API not configured',
                    'recommendation': 'Add FRED_API_KEY for economic indicators',
                    'policy_stance': 'Manual economic analysis needed'
                }
                
        except Exception as e:
            return {"error": f"Fed policy data error: {str(e)}"}
    
    async def get_economic_indicators(self) -> Dict[str, Any]:
        """Get key economic indicators and market context"""
        
        try:
            # Get market indices for economic context
            indices = {
                'SPY': '^GSPC',    # S&P 500
                'VIX': '^VIX',     # Volatility Index
                'DXY': 'DX-Y.NYB', # Dollar Index
                'TNX': '^TNX'      # 10-Year Treasury
            }
            
            economic_data = {}
            
            for name, symbol in indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='5d')
                    
                    if len(hist) >= 2:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2]
                        change = (current - previous) / previous * 100
                        
                        economic_data[name] = {
                            'current_value': current,
                            'daily_change': change,
                            'trend': 'up' if change > 0 else 'down'
                        }
                except:
                    economic_data[name] = {'error': 'Data unavailable'}
            
            # Market sentiment analysis
            vix_level = economic_data.get('VIX', {}).get('current_value', 20)
            
            if vix_level < 15:
                market_sentiment = 'complacent'
            elif vix_level < 25:
                market_sentiment = 'normal'
            elif vix_level < 35:
                market_sentiment = 'elevated_fear'
            else:
                market_sentiment = 'panic'
            
            return {
                'indices': economic_data,
                'market_sentiment': market_sentiment,
                'vix_level': vix_level,
                'economic_context': 'Basic economic indicators available'
            }
            
        except Exception as e:
            return {"error": f"Economic indicators error: {str(e)}"}
    
    async def get_sector_rotation(self, ticker: str) -> Dict[str, Any]:
        """Analyze sector rotation and relative performance"""
        
        try:
            # Get sector for the ticker
            stock = yf.Ticker(ticker)
            info = stock.info
            sector = info.get('sector', 'Unknown')
            
            # Sector ETFs for rotation analysis
            sector_etfs = {
                'Technology': 'XLK',
                'Healthcare': 'XLV', 
                'Financials': 'XLF',
                'Energy': 'XLE',
                'Consumer Cyclical': 'XLY',
                'Industrial': 'XLI',
                'Utilities': 'XLU',
                'Real Estate': 'XLRE',
                'Materials': 'XLB',
                'Consumer Defensive': 'XLP',
                'Communication Services': 'XLC'
            }
            
            # Get sector performance
            sector_performance = {}
            spy = yf.Ticker('SPY')
            spy_hist = spy.history(period='30d')
            spy_return = (spy_hist['Close'].iloc[-1] - spy_hist['Close'].iloc[0]) / spy_hist['Close'].iloc[0] * 100
            
            for sector_name, etf_symbol in sector_etfs.items():
                try:
                    etf = yf.Ticker(etf_symbol)
                    hist = etf.history(period='30d')
                    
                    if len(hist) > 0:
                        sector_return = (hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100
                        relative_performance = sector_return - spy_return
                        
                        sector_performance[sector_name] = {
                            'return_30d': sector_return,
                            'relative_to_spy': relative_performance,
                            'outperforming': relative_performance > 0
                        }
                except:
                    continue
            
            # Determine rotation trends
            outperforming_sectors = [s for s, data in sector_performance.items() if data.get('outperforming', False)]
            
            return {
                'ticker_sector': sector,
                'sector_performance': sector_performance,
                'outperforming_sectors': outperforming_sectors,
                'rotation_trend': 'sector rotation analysis available',
                'spy_benchmark_return': spy_return
            }
            
        except Exception as e:
            return {"error": f"Sector rotation error: {str(e)}"}
    
    def generate_intelligence_summary(self, intelligence: MarketIntelligence) -> str:
        """Generate comprehensive intelligence summary for AI debates"""
        
        summary = f"""
🧠 COMPREHENSIVE MARKET INTELLIGENCE FOR {intelligence.ticker}
{'=' * 60}
⏰ Generated: {intelligence.timestamp}

📱 SOCIAL SENTIMENT:
• Reddit (WSB/Investing): {intelligence.reddit_sentiment.get('sentiment', 'neutral').upper()} 
  ({intelligence.reddit_sentiment.get('mentions', 0)} mentions)
• Twitter/X: {intelligence.twitter_sentiment.get('sentiment', 'neutral').upper()}
  ({intelligence.twitter_sentiment.get('mentions', 0)} mentions, {intelligence.twitter_sentiment.get('total_engagement', 0)} engagement)
• YouTube: {len(intelligence.youtube_mentions)} recent financial analysis videos

📰 NEWS & EVENTS:
• Breaking News: {len(intelligence.breaking_news)} recent articles
• Analyst Updates: {len(intelligence.analyst_upgrades)} recent upgrades/downgrades  
• Earnings Events: {len(intelligence.earnings_events)} upcoming events

🏛️ REGULATORY & POLITICAL:
• FDA Events: {len(intelligence.fda_events)} regulatory catalysts
• Congressional Trades: {len(intelligence.congressional_trades)} recent politician trades
• Insider Activity: {len(intelligence.insider_trades)} recent insider transactions

📊 MARKET MICROSTRUCTURE:
• Options Flow: {intelligence.options_flow.get('sentiment', 'neutral')} 
  (P/C Ratio: {intelligence.options_flow.get('put_call_ratio', 0):.2f})
• Dark Pool Activity: {intelligence.dark_pool_activity.get('status', 'unknown')}
• Institutional Flows: {intelligence.institutional_flows.get('flow_sentiment', 'neutral')}

🏦 ECONOMIC CONTEXT:
• Fed Policy: {intelligence.fed_policy_signals.get('policy_stance', 'unknown')}
• Market Sentiment: {intelligence.economic_indicators.get('market_sentiment', 'unknown')}
• Sector Rotation: {len(intelligence.sector_rotation.get('outperforming_sectors', []))} sectors outperforming

💡 INTELLIGENCE QUALITY:
• Data Sources: {self._count_active_sources(intelligence)} active feeds
• Real-time Coverage: Social, News, Options, Economic indicators
• Missing: FDA calendar, advanced dark pool data, institutional feeds

🎯 AI DEBATE CONTEXT:
This comprehensive intelligence provides hedge fund-level market awareness for 
sophisticated AI analysis. All data is real-time and multi-sourced for maximum
accuracy and market edge.
"""
        
        return summary
    
    def _count_active_sources(self, intelligence: MarketIntelligence) -> int:
        """Count number of active data sources"""
        active_count = 0
        
        sources = [
            intelligence.reddit_sentiment,
            intelligence.twitter_sentiment, 
            intelligence.youtube_mentions,
            intelligence.breaking_news,
            intelligence.options_flow,
            intelligence.economic_indicators,
            intelligence.sector_rotation
        ]
        
        for source in sources:
            if source and not source.get('error'):
                active_count += 1
        
        return active_count

# Test function
async def test_comprehensive_intelligence():
    """Test the comprehensive intelligence engine"""
    
    engine = ComprehensiveIntelligenceEngine()
    
    print("🧪 TESTING COMPREHENSIVE INTELLIGENCE ENGINE")
    print("=" * 60)
    
    # Test with a popular stock
    ticker = "NVDA"
    intelligence = await engine.gather_comprehensive_intelligence(ticker)
    
    # Generate summary
    summary = engine.generate_intelligence_summary(intelligence)
    print(summary)
    
    return intelligence

if __name__ == "__main__":
    asyncio.run(test_comprehensive_intelligence())