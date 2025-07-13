#!/usr/bin/env python3
"""
Interactive Stock Tiles System
Live stock tiles with AI consultant integration
"""

import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class StockTile:
    """Interactive stock tile with live data"""
    symbol: str
    company_name: str
    current_price: float
    price_change: float
    price_change_pct: float
    volume: int
    market_cap: float
    pe_ratio: Optional[float]
    day_high: float
    day_low: float
    fifty_two_week_high: float
    fifty_two_week_low: float
    avg_volume: int
    beta: Optional[float]
    dividend_yield: Optional[float]
    earnings_date: Optional[str]
    analyst_target: Optional[float]
    recommendation: str
    news_headlines: List[str]
    key_metrics: Dict[str, Any]
    ai_analysis: Dict[str, str]  # Claude and ChatGPT analysis
    last_updated: datetime

class InteractiveStockTiles:
    """System for creating interactive stock tiles"""
    
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY', '')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        
        # Default watchlist - will be enhanced with portfolio holdings
        self.default_watchlist = [
            'AAPL', 'NVDA', 'MSFT', 'GOOGL', 'TSLA', 
            'AMD', 'META', 'AMZN', 'NFLX', 'SPY'
        ]
    
    async def get_stock_tiles(self, symbols: List[str] = None, filter_type: str = "all") -> List[StockTile]:
        """Get interactive stock tiles with live data"""
        
        if symbols is None:
            symbols = self.default_watchlist
        
        tiles = []
        
        for symbol in symbols:
            try:
                tile = await self.create_stock_tile(symbol)
                if tile:
                    tiles.append(tile)
            except Exception as e:
                logger.error(f"Error creating tile for {symbol}: {e}")
                continue
        
        # Apply filters
        filtered_tiles = self.apply_filters(tiles, filter_type)
        
        return filtered_tiles
    
    async def create_stock_tile(self, symbol: str) -> Optional[StockTile]:
        """Create a single stock tile with comprehensive data"""
        
        try:
            # Get stock data
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="5d")
            
            if hist.empty:
                return None
            
            # Calculate metrics
            current_price = hist['Close'].iloc[-1]
            previous_close = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else current_price)
            
            price_change = current_price - previous_close
            price_change_pct = (price_change / previous_close * 100) if previous_close > 0 else 0
            
            # Get news headlines
            news_headlines = await self.get_recent_news(symbol)
            
            # Get AI analysis
            ai_analysis = await self.get_ai_analysis(symbol, current_price, price_change_pct, news_headlines)
            
            # Create tile
            tile = StockTile(
                symbol=symbol,
                company_name=info.get('longName', symbol),
                current_price=current_price,
                price_change=price_change,
                price_change_pct=price_change_pct,
                volume=hist['Volume'].iloc[-1],
                market_cap=info.get('marketCap', 0),
                pe_ratio=info.get('trailingPE'),
                day_high=info.get('dayHigh', hist['High'].iloc[-1]),
                day_low=info.get('dayLow', hist['Low'].iloc[-1]),
                fifty_two_week_high=info.get('fiftyTwoWeekHigh', 0),
                fifty_two_week_low=info.get('fiftyTwoWeekLow', 0),
                avg_volume=info.get('averageVolume', 0),
                beta=info.get('beta'),
                dividend_yield=info.get('dividendYield'),
                earnings_date=self.format_earnings_date(info.get('earningsDate')),
                analyst_target=info.get('targetMeanPrice'),
                recommendation=info.get('recommendationKey', 'hold'),
                news_headlines=news_headlines,
                key_metrics=self.calculate_key_metrics(info, hist),
                ai_analysis=ai_analysis,
                last_updated=datetime.now()
            )
            
            return tile
            
        except Exception as e:
            logger.error(f"Error creating tile for {symbol}: {e}")
            return None
    
    async def get_recent_news(self, symbol: str) -> List[str]:
        """Get recent news headlines for a stock"""
        
        try:
            stock = yf.Ticker(symbol)
            news = stock.news
            
            headlines = []
            for article in news[:3]:  # Top 3 headlines
                title = article.get('title', '')
                if title:
                    headlines.append(title)
            
            return headlines
            
        except Exception as e:
            logger.error(f"Error getting news for {symbol}: {e}")
            return []
    
    async def get_ai_analysis(self, symbol: str, price: float, change_pct: float, news: List[str]) -> Dict[str, str]:
        """Get AI analysis from Claude and ChatGPT"""
        
        analysis = {
            'claude_analysis': '',
            'chatgpt_analysis': '',
            'consensus': '',
            'key_points': []
        }
        
        try:
            # Prepare context for AI analysis
            context = f"""
            Stock: {symbol}
            Current Price: ${price:.2f}
            Daily Change: {change_pct:+.1f}%
            Recent News: {'; '.join(news[:2]) if news else 'No recent news'}
            
            Provide a brief analysis focusing on:
            1. Current technical setup
            2. Key support/resistance levels
            3. Upcoming catalysts
            4. Risk/reward assessment
            5. Short-term outlook (1-2 weeks)
            
            Keep analysis concise (2-3 sentences max).
            """
            
            # Get Claude analysis
            claude_analysis = await self.get_claude_analysis(context)
            analysis['claude_analysis'] = claude_analysis
            
            # Get ChatGPT analysis  
            chatgpt_analysis = await self.get_chatgpt_analysis(context)
            analysis['chatgpt_analysis'] = chatgpt_analysis
            
            # Generate consensus
            analysis['consensus'] = self.generate_consensus(claude_analysis, chatgpt_analysis, change_pct)
            
        except Exception as e:
            logger.error(f"Error getting AI analysis for {symbol}: {e}")
            analysis['consensus'] = "Analysis unavailable"
        
        return analysis
    
    async def get_claude_analysis(self, context: str) -> str:
        """Get analysis from Claude"""
        
        if not self.anthropic_api_key:
            return "Claude API not configured"
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=150,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": f"As a professional stock analyst, analyze this stock:\n\n{context}"
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude analysis error: {e}")
            return "Claude analysis error"
    
    async def get_chatgpt_analysis(self, context: str) -> str:
        """Get analysis from ChatGPT via OpenRouter"""
        
        if not self.openrouter_api_key:
            return "OpenRouter API not configured"
        
        try:
            headers = {
                'Authorization': f'Bearer {self.openrouter_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'openai/gpt-4',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a professional stock analyst. Provide concise, actionable analysis.'
                    },
                    {
                        'role': 'user',
                        'content': f"Analyze this stock:\n\n{context}"
                    }
                ],
                'max_tokens': 150,
                'temperature': 0.3
            }
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return "ChatGPT analysis error"
                
        except Exception as e:
            logger.error(f"ChatGPT analysis error: {e}")
            return "ChatGPT analysis error"
    
    def generate_consensus(self, claude: str, chatgpt: str, change_pct: float) -> str:
        """Generate consensus from both AI analyses"""
        
        if "error" in claude.lower() and "error" in chatgpt.lower():
            return "⚠️ Analysis unavailable"
        
        # Determine sentiment based on price change and AI analyses
        if change_pct > 3:
            sentiment = "🟢 Bullish"
        elif change_pct < -3:
            sentiment = "🔴 Bearish"
        else:
            sentiment = "🟡 Neutral"
        
        # Look for common themes in both analyses
        common_words = ['support', 'resistance', 'breakout', 'bullish', 'bearish', 'earnings', 'catalyst']
        themes = []
        
        for word in common_words:
            if word in claude.lower() and word in chatgpt.lower():
                themes.append(word)
        
        consensus = f"{sentiment}"
        if themes:
            consensus += f" | Key themes: {', '.join(themes[:2])}"
        
        return consensus
    
    def calculate_key_metrics(self, info: Dict, hist) -> Dict[str, Any]:
        """Calculate key trading metrics"""
        
        current_price = hist['Close'].iloc[-1]
        
        metrics = {
            'rsi': self.calculate_rsi(hist['Close']),
            'volume_ratio': hist['Volume'].iloc[-1] / info.get('averageVolume', 1),
            'distance_from_52w_high': ((current_price - info.get('fiftyTwoWeekHigh', current_price)) / info.get('fiftyTwoWeekHigh', current_price)) * 100,
            'distance_from_52w_low': ((current_price - info.get('fiftyTwoWeekLow', current_price)) / info.get('fiftyTwoWeekLow', current_price)) * 100,
            'momentum_5d': ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100 if len(hist) >= 5 else 0
        }
        
        return metrics
    
    def calculate_rsi(self, prices, periods: int = 14) -> float:
        """Calculate RSI indicator"""
        
        try:
            if len(prices) < periods + 1:
                return 50.0  # Neutral RSI
            
            deltas = prices.diff()
            gains = deltas.where(deltas > 0, 0)
            losses = -deltas.where(deltas < 0, 0)
            
            avg_gain = gains.rolling(periods).mean()
            avg_loss = losses.rolling(periods).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi.iloc[-1])
            
        except:
            return 50.0
    
    def format_earnings_date(self, earnings_date) -> Optional[str]:
        """Format earnings date for display"""
        
        try:
            if earnings_date:
                if hasattr(earnings_date, 'strftime'):
                    return earnings_date.strftime('%Y-%m-%d')
                return str(earnings_date)
            return None
        except:
            return None
    
    def apply_filters(self, tiles: List[StockTile], filter_type: str) -> List[StockTile]:
        """Apply filters to stock tiles"""
        
        if filter_type == "gainers":
            return sorted([t for t in tiles if t.price_change_pct > 0], 
                         key=lambda x: x.price_change_pct, reverse=True)
        
        elif filter_type == "losers":
            return sorted([t for t in tiles if t.price_change_pct < 0], 
                         key=lambda x: x.price_change_pct)
        
        elif filter_type == "volume":
            return sorted(tiles, key=lambda x: x.volume, reverse=True)
        
        elif filter_type == "market_cap":
            return sorted(tiles, key=lambda x: x.market_cap, reverse=True)
        
        elif filter_type == "volatility":
            return sorted(tiles, key=lambda x: abs(x.price_change_pct), reverse=True)
        
        else:  # "all" or default
            return sorted(tiles, key=lambda x: x.market_cap, reverse=True)

# Quick access function
async def get_stock_tiles_for_streamlit(symbols: List[str] = None, filter_type: str = "all") -> List[StockTile]:
    """Get stock tiles for Streamlit display"""
    
    try:
        tiles_system = InteractiveStockTiles()
        return await tiles_system.get_stock_tiles(symbols, filter_type)
    except Exception as e:
        logger.error(f"Error getting stock tiles: {e}")
        return []

# Test function
async def main():
    """Test the stock tiles system"""
    
    tiles_system = InteractiveStockTiles()
    tiles = await tiles_system.get_stock_tiles(['AAPL', 'NVDA', 'TSLA'])
    
    for tile in tiles:
        print(f"{tile.symbol}: ${tile.current_price:.2f} ({tile.price_change_pct:+.1f}%)")
        print(f"Consensus: {tile.ai_analysis['consensus']}")
        print()

if __name__ == "__main__":
    asyncio.run(main())