#!/usr/bin/env python3
"""
REAL-TIME Portfolio Engine - 100% Live Portfolio Data
No mock data - everything is real portfolio performance and live market data
"""

import os
import json
import yfinance as yf
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import pandas as pd

@dataclass
class LivePosition:
    """Real-time portfolio position"""
    ticker: str
    shares: float
    market_value: float
    cost_basis: float
    unrealized_pl: float
    unrealized_pl_percent: float
    current_price: float
    day_change: float
    day_change_percent: float
    sector: str
    market_cap: Optional[float]
    volume_today: int
    avg_volume: int
    volume_ratio: float
    news_today: List[str]
    analyst_rating: str
    last_updated: str

class RealTimePortfolioEngine:
    """Real-time portfolio analysis with live market data"""
    
    def __init__(self):
        # API keys
        self.alpaca_api_key = os.getenv('ALPACA_API_KEY', '')
        self.alpaca_secret = os.getenv('ALPACA_SECRET_KEY', '')
        self.alpaca_base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        # REMOVED: Hardcoded fallback positions for trading safety
        # NEVER use fake portfolio data for real money decisions
        
        # Initialize Alpaca if configured
        self.alpaca = None
        if self.alpaca_api_key and self.alpaca_secret:
            try:
                self.alpaca = tradeapi.REST(
                    self.alpaca_api_key,
                    self.alpaca_secret,
                    self.alpaca_base_url,
                    api_version='v2'
                )
                print("✅ Alpaca API connected for live portfolio data")
            except Exception as e:
                print(f"⚠️ Alpaca API connection failed: {e}")
                self.alpaca = None
    
    async def get_live_portfolio_positions(self) -> List[LivePosition]:
        """Get real-time portfolio positions with live market data"""
        
        print("📊 FETCHING LIVE PORTFOLIO DATA...")
        
        positions = []
        
        if self.alpaca:
            # Get real Alpaca positions
            positions = await self.get_alpaca_positions()
        else:
            # SAFETY: Never use fake portfolio data for real money decisions
            print("🚨 CRITICAL ERROR: NO REAL BROKER CONNECTION")
            print("🛑 TRADING DISABLED: Cannot operate without real portfolio data")
            print("💡 FIX: Configure ALPACA_API_KEY and ALPACA_SECRET_KEY")
            
            raise RuntimeError(
                "TRADING SAFETY VIOLATION: No real broker connection available. "
                "Real money trading requires verified portfolio data from broker APIs. "
                "Configure Alpaca credentials for real portfolio access."
            )
        
        print(f"✅ Retrieved {len(positions)} live portfolio positions")
        return positions
    
    async def get_alpaca_positions(self) -> List[LivePosition]:
        """Get real positions from Alpaca account"""
        
        positions = []
        
        try:
            # Get account positions
            alpaca_positions = self.alpaca.list_positions()
            
            for pos in alpaca_positions:
                # Get live market data for each position
                live_data = await self.get_live_stock_data(pos.symbol)
                
                if live_data:
                    position = LivePosition(
                        ticker=pos.symbol,
                        shares=float(pos.qty),
                        market_value=float(pos.market_value),
                        cost_basis=float(pos.cost_basis),
                        unrealized_pl=float(pos.unrealized_pl),
                        unrealized_pl_percent=float(pos.unrealized_plpc) * 100,
                        current_price=float(pos.current_price),
                        day_change=live_data["day_change"],
                        day_change_percent=live_data["day_change_percent"],
                        sector=live_data["sector"],
                        market_cap=live_data["market_cap"],
                        volume_today=live_data["volume_today"],
                        avg_volume=live_data["avg_volume"],
                        volume_ratio=live_data["volume_ratio"],
                        news_today=live_data["news_today"],
                        analyst_rating=live_data["analyst_rating"],
                        last_updated=datetime.now().isoformat()
                    )
                    positions.append(position)
                    print(f"   📈 {pos.symbol}: ${float(pos.market_value):,.0f} ({float(pos.unrealized_plpc)*100:+.1f}%)")
        
        except Exception as e:
            print(f"❌ Error getting Alpaca positions: {e}")
            print("🚨 CRITICAL ERROR: REAL PORTFOLIO DATA UNAVAILABLE")
            print("🛑 TRADING DISABLED: Cannot fallback to fake data for real money decisions")
            
            raise RuntimeError(
                f"TRADING SAFETY VIOLATION: Real portfolio data failed ({e}). "
                "System cannot fallback to mock data for safety reasons. "
                "Fix Alpaca API connection before trading."
            )
        
        return positions
    
    async def get_fallback_positions(self) -> List[LivePosition]:
        """DANGER: This method uses FAKE portfolio data and is DISABLED for trading safety"""
        
        print("🚨 CRITICAL ERROR: NO REAL PORTFOLIO DATA AVAILABLE")
        print("🛑 TRADING DISABLED: Cannot use fake portfolio data for real money decisions")
        print("💡 FIX: Configure ALPACA_API_KEY and ALPACA_SECRET_KEY for real portfolio data")
        
        # SAFETY: Never return fake portfolio data that could affect trading
        raise RuntimeError(
            "TRADING SAFETY VIOLATION: Attempted to use fake portfolio data. "
            "Real money trading requires real portfolio connections. "
            "Configure Alpaca API keys for real portfolio data."
        )
    
    async def get_live_stock_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive live stock data"""
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get price data
            hist = stock.history(period="10d")
            if len(hist) < 2:
                return None
            
            # Get company info
            info = stock.info
            
            # Calculate metrics
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2]
            day_change = current_price - previous_close
            day_change_percent = (day_change / previous_close) * 100
            
            # Volume analysis
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].iloc[:-1].mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Get news
            news_today = await self.get_stock_news(ticker)
            
            # Get analyst rating
            analyst_rating = await self.get_analyst_rating(ticker)
            
            return {
                "current_price": current_price,
                "day_change": day_change,
                "day_change_percent": day_change_percent,
                "sector": info.get('sector', 'Unknown'),
                "market_cap": info.get('marketCap'),
                "volume_today": int(current_volume),
                "avg_volume": int(avg_volume),
                "volume_ratio": volume_ratio,
                "news_today": news_today,
                "analyst_rating": analyst_rating
            }
        
        except Exception as e:
            print(f"❌ Error getting live data for {ticker}: {e}")
            return None
    
    async def get_stock_news(self, ticker: str) -> List[str]:
        """Get today's news for a stock"""
        
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            today_news = []
            today = datetime.now().date()
            
            for article in news[:10]:  # Check recent articles
                try:
                    # Parse article timestamp
                    pub_time = datetime.fromtimestamp(article.get('providerPublishTime', 0))
                    if pub_time.date() == today:
                        title = article.get('title', '')
                        if len(title) > 10:  # Valid title
                            today_news.append(title)
                except:
                    continue
            
            return today_news[:3]  # Top 3 today's news
        
        except:
            return []
    
    async def get_analyst_rating(self, ticker: str) -> str:
        """Get analyst rating for stock"""
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get recommendation from info
            recommendation = info.get('recommendationKey', '')
            
            if recommendation:
                rating_map = {
                    'strong_buy': 'Strong Buy',
                    'buy': 'Buy',
                    'hold': 'Hold',
                    'sell': 'Sell',
                    'strong_sell': 'Strong Sell'
                }
                return rating_map.get(recommendation.lower(), recommendation.title())
            
            return 'No Rating'
        
        except:
            return 'No Rating'
    
    async def calculate_portfolio_metrics(self, positions: List[LivePosition]) -> Dict[str, Any]:
        """Calculate real-time portfolio performance metrics"""
        
        if not positions:
            return {
                "total_value": 0,
                "total_day_change": 0,
                "total_day_change_percent": 0,
                "total_unrealized_pl": 0,
                "total_unrealized_pl_percent": 0,
                "position_count": 0,
                "winning_positions": 0,
                "losing_positions": 0
            }
        
        total_value = sum(pos.market_value for pos in positions)
        total_day_change = sum(pos.day_change * pos.shares for pos in positions)
        total_unrealized_pl = sum(pos.unrealized_pl for pos in positions)
        
        winning_positions = len([p for p in positions if p.day_change_percent > 0])
        losing_positions = len([p for p in positions if p.day_change_percent < 0])
        
        return {
            "total_value": total_value,
            "total_day_change": total_day_change,
            "total_day_change_percent": (total_day_change / (total_value - total_day_change)) * 100 if total_value > total_day_change else 0,
            "total_unrealized_pl": total_unrealized_pl,
            "total_unrealized_pl_percent": (total_unrealized_pl / (total_value - total_unrealized_pl)) * 100 if total_value > total_unrealized_pl else 0,
            "position_count": len(positions),
            "winning_positions": winning_positions,
            "losing_positions": losing_positions,
            "win_rate": (winning_positions / len(positions)) * 100 if positions else 0
        }
    
    async def get_top_performers(self, positions: List[LivePosition], count: int = 5) -> List[LivePosition]:
        """Get top performing positions today"""
        
        sorted_positions = sorted(positions, key=lambda x: x.day_change_percent, reverse=True)
        return sorted_positions[:count]
    
    async def get_worst_performers(self, positions: List[LivePosition], count: int = 5) -> List[LivePosition]:
        """Get worst performing positions today"""
        
        sorted_positions = sorted(positions, key=lambda x: x.day_change_percent)
        return sorted_positions[:count]
    
    async def get_high_volume_positions(self, positions: List[LivePosition]) -> List[LivePosition]:
        """Get positions with unusual volume today"""
        
        high_volume = [pos for pos in positions if pos.volume_ratio > 2.0]  # 2x+ normal volume
        return sorted(high_volume, key=lambda x: x.volume_ratio, reverse=True)
    
    async def get_positions_with_news(self, positions: List[LivePosition]) -> List[LivePosition]:
        """Get positions with news today"""
        
        with_news = [pos for pos in positions if pos.news_today]
        return sorted(with_news, key=lambda x: len(x.news_today), reverse=True)


# Example usage
async def main():
    """Test real-time portfolio engine"""
    
    portfolio = RealTimePortfolioEngine()
    
    # Get live positions
    positions = await portfolio.get_live_portfolio_positions()
    
    # Calculate metrics
    metrics = await portfolio.calculate_portfolio_metrics(positions)
    
    print(f"\n📊 LIVE PORTFOLIO METRICS:")
    print(f"Total Value: ${metrics['total_value']:,.0f}")
    print(f"Day Change: ${metrics['total_day_change']:+,.0f} ({metrics['total_day_change_percent']:+.1f}%)")
    print(f"Unrealized P&L: ${metrics['total_unrealized_pl']:+,.0f} ({metrics['total_unrealized_pl_percent']:+.1f}%)")
    print(f"Win Rate: {metrics['win_rate']:.1f}% ({metrics['winning_positions']}/{metrics['position_count']})")
    
    # Top performers
    top_performers = await portfolio.get_top_performers(positions, 3)
    print(f"\n🏆 TOP PERFORMERS:")
    for pos in top_performers:
        print(f"   {pos.ticker}: {pos.day_change_percent:+.1f}% (${pos.market_value:,.0f})")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())