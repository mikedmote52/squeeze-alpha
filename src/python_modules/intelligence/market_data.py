"""
Market Data Provider
Handles real-time and historical market data from multiple sources
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor
import polygon
import alpha_vantage

from ..utils.config import get_config

@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    price: float
    volume: int
    change: float
    change_percent: float
    high: float
    low: float
    open: float
    close: float
    timestamp: datetime
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    
@dataclass
class OptionData:
    """Option data structure"""
    symbol: str
    strike: float
    expiration: datetime
    option_type: str  # 'call' or 'put'
    bid: float
    ask: float
    volume: int
    open_interest: int
    implied_volatility: float
    delta: float
    gamma: float
    theta: float
    vega: float

@dataclass
class NewsItem:
    """News item structure"""
    title: str
    summary: str
    url: str
    source: str
    timestamp: datetime
    sentiment: Optional[str] = None
    relevance_score: Optional[float] = None

class PolygonDataProvider:
    """Polygon.io data provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = polygon.RESTClient(api_key)
        self.logger = logging.getLogger(__name__)
    
    async def get_real_time_quote(self, symbol: str) -> Optional[MarketData]:
        """Get real-time quote"""
        try:
            quote = self.client.get_last_quote(symbol)
            
            if quote:
                return MarketData(
                    symbol=symbol,
                    price=quote.bid,  # Using bid as current price
                    volume=0,  # Not available in quote
                    change=0,  # Calculate separately
                    change_percent=0,
                    high=0,
                    low=0,
                    open=0,
                    close=0,
                    timestamp=datetime.fromtimestamp(quote.timestamp / 1000)
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting Polygon quote for {symbol}: {e}")
            return None
    
    async def get_historical_data(self, symbol: str, 
                                 start_date: datetime,
                                 end_date: datetime,
                                 timespan: str = "day") -> List[MarketData]:
        """Get historical data"""
        try:
            aggs = self.client.get_aggs(
                symbol,
                1,
                timespan,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            data = []
            for agg in aggs:
                data.append(MarketData(
                    symbol=symbol,
                    price=agg.close,
                    volume=agg.volume,
                    change=agg.close - agg.open,
                    change_percent=((agg.close - agg.open) / agg.open) * 100,
                    high=agg.high,
                    low=agg.low,
                    open=agg.open,
                    close=agg.close,
                    timestamp=datetime.fromtimestamp(agg.timestamp / 1000)
                ))
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error getting Polygon historical data for {symbol}: {e}")
            return []
    
    async def get_news(self, symbol: str, limit: int = 10) -> List[NewsItem]:
        """Get news for symbol"""
        try:
            news = self.client.get_ticker_news(symbol, limit=limit)
            
            news_items = []
            for item in news:
                news_items.append(NewsItem(
                    title=item.title,
                    summary=item.description or "",
                    url=item.article_url,
                    source=item.publisher.name,
                    timestamp=datetime.fromisoformat(item.published_utc.replace('Z', '+00:00'))
                ))
            
            return news_items
            
        except Exception as e:
            self.logger.error(f"Error getting Polygon news for {symbol}: {e}")
            return []

class AlphaVantageDataProvider:
    """Alpha Vantage data provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.alphavantage.co/query"
    
    async def get_real_time_quote(self, symbol: str) -> Optional[MarketData]:
        """Get real-time quote"""
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                
                return MarketData(
                    symbol=symbol,
                    price=float(quote['05. price']),
                    volume=int(quote['06. volume']),
                    change=float(quote['09. change']),
                    change_percent=float(quote['10. change percent'].replace('%', '')),
                    high=float(quote['03. high']),
                    low=float(quote['04. low']),
                    open=float(quote['02. open']),
                    close=float(quote['08. previous close']),
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting Alpha Vantage quote for {symbol}: {e}")
            return None
    
    async def get_technical_indicators(self, symbol: str, 
                                     indicator: str = "RSI",
                                     interval: str = "daily",
                                     time_period: int = 14) -> Dict[str, Any]:
        """Get technical indicators"""
        try:
            params = {
                'function': indicator,
                'symbol': symbol,
                'interval': interval,
                'time_period': time_period,
                'series_type': 'close',
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error getting Alpha Vantage indicators for {symbol}: {e}")
            return {}

class YFinanceDataProvider:
    """Yahoo Finance data provider"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def get_real_time_quote(self, symbol: str) -> Optional[MarketData]:
        """Get real-time quote"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if info:
                return MarketData(
                    symbol=symbol,
                    price=info.get('currentPrice', 0),
                    volume=info.get('volume', 0),
                    change=info.get('currentPrice', 0) - info.get('previousClose', 0),
                    change_percent=((info.get('currentPrice', 0) - info.get('previousClose', 0)) / info.get('previousClose', 1)) * 100,
                    high=info.get('dayHigh', 0),
                    low=info.get('dayLow', 0),
                    open=info.get('open', 0),
                    close=info.get('previousClose', 0),
                    timestamp=datetime.now(),
                    market_cap=info.get('marketCap'),
                    pe_ratio=info.get('trailingPE')
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting Yahoo Finance quote for {symbol}: {e}")
            return None
    
    async def get_historical_data(self, symbol: str, 
                                 period: str = "1mo",
                                 interval: str = "1d") -> List[MarketData]:
        """Get historical data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            data = []
            for index, row in hist.iterrows():
                data.append(MarketData(
                    symbol=symbol,
                    price=row['Close'],
                    volume=int(row['Volume']),
                    change=row['Close'] - row['Open'],
                    change_percent=((row['Close'] - row['Open']) / row['Open']) * 100,
                    high=row['High'],
                    low=row['Low'],
                    open=row['Open'],
                    close=row['Close'],
                    timestamp=index.to_pydatetime()
                ))
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error getting Yahoo Finance historical data for {symbol}: {e}")
            return []
    
    async def get_options_data(self, symbol: str, 
                              expiration: Optional[str] = None) -> List[OptionData]:
        """Get options data"""
        try:
            ticker = yf.Ticker(symbol)
            
            if expiration:
                options = ticker.option_chain(expiration)
            else:
                expirations = ticker.options
                if expirations:
                    options = ticker.option_chain(expirations[0])
                else:
                    return []
            
            options_data = []
            
            # Process calls
            for _, call in options.calls.iterrows():
                options_data.append(OptionData(
                    symbol=symbol,
                    strike=call['strike'],
                    expiration=datetime.strptime(expiration or expirations[0], "%Y-%m-%d"),
                    option_type='call',
                    bid=call['bid'],
                    ask=call['ask'],
                    volume=int(call['volume']) if not pd.isna(call['volume']) else 0,
                    open_interest=int(call['openInterest']) if not pd.isna(call['openInterest']) else 0,
                    implied_volatility=call['impliedVolatility'],
                    delta=0,  # Would need additional calculation
                    gamma=0,
                    theta=0,
                    vega=0
                ))
            
            # Process puts
            for _, put in options.puts.iterrows():
                options_data.append(OptionData(
                    symbol=symbol,
                    strike=put['strike'],
                    expiration=datetime.strptime(expiration or expirations[0], "%Y-%m-%d"),
                    option_type='put',
                    bid=put['bid'],
                    ask=put['ask'],
                    volume=int(put['volume']) if not pd.isna(put['volume']) else 0,
                    open_interest=int(put['openInterest']) if not pd.isna(put['openInterest']) else 0,
                    implied_volatility=put['impliedVolatility'],
                    delta=0,
                    gamma=0,
                    theta=0,
                    vega=0
                ))
            
            return options_data
            
        except Exception as e:
            self.logger.error(f"Error getting Yahoo Finance options data for {symbol}: {e}")
            return []

class MarketDataProvider:
    """Main market data provider with multiple sources"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize data providers
        self.providers = {}
        
        # Polygon
        try:
            polygon_key = self.config.get_api_key('polygon')
            self.providers['polygon'] = PolygonDataProvider(polygon_key)
        except:
            self.logger.warning("Polygon API not configured")
        
        # Alpha Vantage
        try:
            av_key = self.config.get_api_key('alpha_vantage')
            self.providers['alpha_vantage'] = AlphaVantageDataProvider(av_key)
        except:
            self.logger.warning("Alpha Vantage API not configured")
        
        # Yahoo Finance (always available)
        self.providers['yahoo'] = YFinanceDataProvider()
        
        # Primary provider preference
        self.primary_provider = 'polygon' if 'polygon' in self.providers else 'yahoo'
        
        # Cache for market data
        self.cache = {}
        self.cache_expiry = {}
    
    def _is_cache_valid(self, key: str, expiry_seconds: int = 60) -> bool:
        """Check if cache is still valid"""
        if key not in self.cache or key not in self.cache_expiry:
            return False
        
        return datetime.now() < self.cache_expiry[key]
    
    def _set_cache(self, key: str, data: Any, expiry_seconds: int = 60) -> None:
        """Set cache with expiry"""
        self.cache[key] = data
        self.cache_expiry[key] = datetime.now() + timedelta(seconds=expiry_seconds)
    
    async def get_real_time_quote(self, symbol: str, 
                                 provider: Optional[str] = None) -> Optional[MarketData]:
        """Get real-time quote with fallback"""
        try:
            # Check cache first
            cache_key = f"quote_{symbol}"
            if self._is_cache_valid(cache_key, 30):  # 30 second cache
                return self.cache[cache_key]
            
            # Use specified provider or primary
            provider_name = provider or self.primary_provider
            
            if provider_name in self.providers:
                data = await self.providers[provider_name].get_real_time_quote(symbol)
                if data:
                    self._set_cache(cache_key, data, 30)
                    return data
            
            # Fallback to other providers
            for name, provider_obj in self.providers.items():
                if name != provider_name:
                    data = await provider_obj.get_real_time_quote(symbol)
                    if data:
                        self._set_cache(cache_key, data, 30)
                        return data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting real-time quote for {symbol}: {e}")
            return None
    
    async def get_multiple_quotes(self, symbols: List[str], 
                                 max_workers: int = 10) -> Dict[str, Optional[MarketData]]:
        """Get quotes for multiple symbols"""
        try:
            results = {}
            
            # Use ThreadPoolExecutor for parallel requests
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_symbol = {
                    executor.submit(asyncio.run, self.get_real_time_quote(symbol)): symbol
                    for symbol in symbols
                }
                
                # Collect results
                for future in future_to_symbol:
                    symbol = future_to_symbol[future]
                    try:
                        results[symbol] = future.result()
                    except Exception as e:
                        self.logger.error(f"Error getting quote for {symbol}: {e}")
                        results[symbol] = None
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting multiple quotes: {e}")
            return {}
    
    async def get_historical_data(self, symbol: str,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None,
                                 period: str = "1mo",
                                 provider: Optional[str] = None) -> List[MarketData]:
        """Get historical data"""
        try:
            # Use specified provider or primary
            provider_name = provider or self.primary_provider
            
            if provider_name == 'polygon' and 'polygon' in self.providers:
                if start_date and end_date:
                    return await self.providers['polygon'].get_historical_data(
                        symbol, start_date, end_date
                    )
            
            # Default to Yahoo Finance
            if 'yahoo' in self.providers:
                return await self.providers['yahoo'].get_historical_data(symbol, period)
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting historical data for {symbol}: {e}")
            return []
    
    async def get_options_data(self, symbol: str,
                              expiration: Optional[str] = None) -> List[OptionData]:
        """Get options data"""
        try:
            # Currently only Yahoo Finance supports options
            if 'yahoo' in self.providers:
                return await self.providers['yahoo'].get_options_data(symbol, expiration)
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting options data for {symbol}: {e}")
            return []
    
    async def get_news(self, symbol: str, limit: int = 10) -> List[NewsItem]:
        """Get news for symbol"""
        try:
            # Try Polygon first
            if 'polygon' in self.providers:
                return await self.providers['polygon'].get_news(symbol, limit)
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting news for {symbol}: {e}")
            return []
    
    async def get_technical_indicators(self, symbol: str,
                                     indicator: str = "RSI",
                                     **kwargs) -> Dict[str, Any]:
        """Get technical indicators"""
        try:
            # Use Alpha Vantage for technical indicators
            if 'alpha_vantage' in self.providers:
                return await self.providers['alpha_vantage'].get_technical_indicators(
                    symbol, indicator, **kwargs
                )
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting technical indicators for {symbol}: {e}")
            return {}
    
    async def get_market_summary(self) -> Dict[str, Any]:
        """Get market summary"""
        try:
            # Key market indices
            indices = ['SPY', 'QQQ', 'IWM', 'DIA']
            
            quotes = await self.get_multiple_quotes(indices)
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'indices': {},
                'market_status': 'open'  # Would need to calculate actual market hours
            }
            
            for symbol, quote in quotes.items():
                if quote:
                    summary['indices'][symbol] = {
                        'price': quote.price,
                        'change': quote.change,
                        'change_percent': quote.change_percent
                    }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting market summary: {e}")
            return {}
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        
        for name, provider in self.providers.items():
            try:
                # Simple health check would go here
                status[name] = {
                    'available': True,
                    'type': type(provider).__name__
                }
            except:
                status[name] = {
                    'available': False,
                    'type': type(provider).__name__
                }
        
        return status

# Global market data provider
_market_data_provider = None

def get_market_data_provider() -> MarketDataProvider:
    """Get global market data provider"""
    global _market_data_provider
    if _market_data_provider is None:
        _market_data_provider = MarketDataProvider()
    return _market_data_provider