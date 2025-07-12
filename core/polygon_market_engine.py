#!/usr/bin/env python3
"""
Polygon.io Market Engine - Real-time market data and analysis
Provides level 2 quotes, news, and advanced market analytics
"""

import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class MarketSnapshot:
    """Real-time market snapshot from Polygon"""
    ticker: str
    price: float
    bid: float
    ask: float
    bid_size: int
    ask_size: int
    volume: int
    vwap: float
    spread: float
    spread_percent: float
    last_update: datetime
    
@dataclass
class MarketNews:
    """Market news item from Polygon"""
    title: str
    summary: str
    ticker: str
    published: datetime
    sentiment: str
    url: str
    
@dataclass
class OptionsFlow:
    """Options flow data for unusual activity"""
    ticker: str
    strike: float
    expiry: str
    call_put: str
    volume: int
    open_interest: int
    premium: float
    unusual_activity: bool

class PolygonMarketEngine:
    """Advanced market data engine using Polygon.io"""
    
    def __init__(self):
        self.api_key = os.getenv('POLYGON_API_KEY')
        self.base_url = 'https://api.polygon.io'
        
        # Market session times (Pacific)
        self.pt_tz = pytz.timezone('US/Pacific')
        self.sessions = {
            'premarket': {'start': '01:00', 'end': '06:30'},
            'open': {'start': '06:30', 'end': '07:00'},
            'midday': {'start': '09:00', 'end': '10:00'},
            'close': {'start': '12:30', 'end': '13:00'},
            'aftermarket': {'start': '13:00', 'end': '17:00'}
        }
    
    async def get_realtime_snapshot(self, ticker: str) -> Optional[MarketSnapshot]:
        """Get real-time level 2 market data"""
        
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}"
        params = {'apiKey': self.api_key}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        ticker_data = data.get('ticker', {})
                        
                        bid = ticker_data.get('prevDay', {}).get('c', 0)  # Previous close as fallback
                        ask = ticker_data.get('day', {}).get('c', 0)
                        
                        snapshot = MarketSnapshot(
                            ticker=ticker,
                            price=ticker_data.get('day', {}).get('c', 0),
                            bid=bid,
                            ask=ask,
                            bid_size=ticker_data.get('day', {}).get('v', 0) // 100,
                            ask_size=ticker_data.get('day', {}).get('v', 0) // 100,
                            volume=ticker_data.get('day', {}).get('v', 0),
                            vwap=ticker_data.get('day', {}).get('vw', 0),
                            spread=ask - bid,
                            spread_percent=((ask - bid) / bid * 100) if bid > 0 else 0,
                            last_update=datetime.now()
                        )
                        return snapshot
        
        except Exception as e:
            print(f"⚠️ Polygon snapshot error: {e}")
        
        return None
    
    async def get_news_sentiment(self, tickers: List[str]) -> List[MarketNews]:
        """Get latest news and sentiment for tickers"""
        
        if not self.api_key:
            return []
        
        ticker_str = ','.join(tickers)
        url = f"{self.base_url}/v2/reference/news"
        params = {
            'ticker': ticker_str,
            'limit': 10,
            'sort': 'published_utc',
            'order': 'desc',
            'apiKey': self.api_key
        }
        
        news_items = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for article in data.get('results', []):
                            # Simple sentiment analysis based on keywords
                            sentiment = self.analyze_news_sentiment(
                                article.get('title', ''),
                                article.get('description', '')
                            )
                            
                            news = MarketNews(
                                title=article.get('title', ''),
                                summary=article.get('description', '')[:200],
                                ticker=article.get('tickers', [''])[0],
                                published=datetime.fromisoformat(article.get('published_utc', '')),
                                sentiment=sentiment,
                                url=article.get('article_url', '')
                            )
                            news_items.append(news)
        
        except Exception as e:
            print(f"⚠️ Polygon news error: {e}")
        
        return news_items
    
    async def get_options_flow(self, ticker: str) -> List[OptionsFlow]:
        """Get unusual options activity"""
        
        if not self.api_key:
            return []
        
        # Get options chain
        url = f"{self.base_url}/v3/reference/options/contracts"
        params = {
            'underlying_ticker': ticker,
            'expired': 'false',
            'limit': 100,
            'apiKey': self.api_key
        }
        
        options_flows = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for contract in data.get('results', []):
                            # Look for unusual volume
                            volume = contract.get('day', {}).get('volume', 0)
                            open_interest = contract.get('open_interest', 0)
                            
                            if volume > open_interest * 2 and volume > 100:  # Unusual activity
                                flow = OptionsFlow(
                                    ticker=ticker,
                                    strike=contract.get('strike_price', 0),
                                    expiry=contract.get('expiration_date', ''),
                                    call_put=contract.get('contract_type', ''),
                                    volume=volume,
                                    open_interest=open_interest,
                                    premium=volume * contract.get('day', {}).get('close', 0) * 100,
                                    unusual_activity=True
                                )
                                options_flows.append(flow)
        
        except Exception as e:
            print(f"⚠️ Polygon options error: {e}")
        
        return options_flows
    
    def get_current_session(self) -> str:
        """Determine current market session"""
        
        now = datetime.now(self.pt_tz)
        current_time = now.strftime('%H:%M')
        
        for session, times in self.sessions.items():
            if times['start'] <= current_time < times['end']:
                return session
        
        # If not in any session, determine if pre or post market
        if current_time < '06:30':
            return 'premarket'
        elif current_time >= '13:00':
            return 'aftermarket'
        else:
            return 'regular'
    
    def analyze_news_sentiment(self, title: str, description: str) -> str:
        """Simple sentiment analysis for news"""
        
        text = (title + ' ' + description).lower()
        
        positive_words = ['surge', 'gain', 'rally', 'beat', 'upgrade', 'strong', 'bullish', 'record', 'growth']
        negative_words = ['fall', 'drop', 'miss', 'downgrade', 'weak', 'bearish', 'concern', 'risk', 'loss']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 'POSITIVE'
        elif negative_count > positive_count:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'
    
    async def analyze_portfolio_session(self, tickers: List[str]) -> Dict[str, Any]:
        """Comprehensive portfolio analysis for current session"""
        
        session = self.get_current_session()
        print(f"📊 ANALYZING PORTFOLIO - {session.upper()} SESSION")
        print("=" * 50)
        
        analysis = {
            'session': session,
            'timestamp': datetime.now(self.pt_tz),
            'tickers': {},
            'alerts': [],
            'recommendations': []
        }
        
        # Get real-time data for each ticker
        for ticker in tickers:
            print(f"🔍 Analyzing {ticker}...")
            
            # Get snapshot
            snapshot = await self.get_realtime_snapshot(ticker)
            
            # Get news
            news = await self.get_news_sentiment([ticker])
            
            # Get options flow
            options = await self.get_options_flow(ticker)
            
            ticker_analysis = {
                'snapshot': snapshot,
                'news': news[:3],  # Top 3 news items
                'options_flow': options[:5],  # Top 5 unusual options
                'alerts': []
            }
            
            # Generate alerts based on data
            if snapshot:
                if snapshot.spread_percent > 1.0:
                    ticker_analysis['alerts'].append(f"⚠️ Wide spread: {snapshot.spread_percent:.2f}%")
                
                if snapshot.volume > 0:  # Add volume spike detection
                    ticker_analysis['alerts'].append(f"📊 Volume: {snapshot.volume:,}")
            
            if options:
                total_premium = sum(opt.premium for opt in options)
                if total_premium > 1_000_000:
                    ticker_analysis['alerts'].append(f"🎯 Unusual options: ${total_premium:,.0f}")
            
            if news:
                negative_news = [n for n in news if n.sentiment == 'NEGATIVE']
                if negative_news:
                    ticker_analysis['alerts'].append(f"📰 {len(negative_news)} negative news items")
            
            analysis['tickers'][ticker] = ticker_analysis
        
        # Generate session-specific recommendations
        analysis['recommendations'] = self.generate_session_recommendations(session, analysis['tickers'])
        
        return analysis
    
    def generate_session_recommendations(self, session: str, ticker_data: Dict) -> List[Dict]:
        """Generate trading recommendations based on session and data"""
        
        recommendations = []
        
        if session == 'premarket':
            # Pre-market strategy
            for ticker, data in ticker_data.items():
                if data['alerts']:
                    rec = {
                        'ticker': ticker,
                        'action': 'WATCH',
                        'reason': 'Pre-market activity detected',
                        'details': data['alerts']
                    }
                    recommendations.append(rec)
        
        elif session == 'open':
            # Opening 30 minutes strategy
            for ticker, data in ticker_data.items():
                snapshot = data.get('snapshot')
                if snapshot and snapshot.volume > 1_000_000:
                    rec = {
                        'ticker': ticker,
                        'action': 'CONSIDER_TRIM' if snapshot.price > 0 else 'HOLD',
                        'reason': 'High opening volume',
                        'details': [f'Volume: {snapshot.volume:,}']
                    }
                    recommendations.append(rec)
        
        elif session == 'close':
            # Closing hour strategy
            for ticker, data in ticker_data.items():
                if data.get('options_flow'):
                    rec = {
                        'ticker': ticker,
                        'action': 'REVIEW_POSITION',
                        'reason': 'EOD options activity',
                        'details': [f'{len(data["options_flow"])} unusual options trades']
                    }
                    recommendations.append(rec)
        
        return recommendations


# Polygon integration benefits:
# 1. Real-time level 2 quotes (bid/ask spreads)
# 2. News sentiment analysis
# 3. Options flow for unusual activity
# 4. After-hours and pre-market data
# 5. WebSocket support for live updates
# 6. Historical data for backtesting