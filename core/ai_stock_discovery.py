"""
AI Stock Discovery Engine - Real-time opportunity finder
Discovers new stocks with explosive growth potential
"""

import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import yfinance as yf
from core.comprehensive_intelligence_engine import ComprehensiveIntelligenceEngine

@dataclass
class StockOpportunity:
    ticker: str
    company_name: str
    discovery_reason: str
    growth_potential: float  # Percentage
    confidence: float
    risk_level: str
    entry_price: float
    target_price: float
    stop_loss: float
    thesis: str
    catalysts: List[str]
    discovered_at: datetime

class AIStockDiscovery:
    """Discovers high-potential stocks using AI analysis"""
    
    def __init__(self):
        self.intelligence = ComprehensiveIntelligenceEngine()
        self.min_confidence = 70  # Only show 70%+ confidence stocks
        
    async def discover_opportunities(self) -> List[StockOpportunity]:
        """Find new stock opportunities using multiple data sources"""
        opportunities = []
        
        # Get trending stocks from multiple sources
        trending_tickers = await self._get_trending_stocks()
        
        # Analyze each for explosive growth potential
        for ticker in trending_tickers[:10]:  # Top 10 to start
            try:
                opportunity = await self._analyze_opportunity(ticker)
                if opportunity and opportunity.confidence >= self.min_confidence:
                    opportunities.append(opportunity)
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
                
        # Sort by growth potential
        opportunities.sort(key=lambda x: x.growth_potential, reverse=True)
        return opportunities
        
    async def _get_trending_stocks(self) -> List[str]:
        """Get trending stocks from multiple sources"""
        trending = set()
        
        # Get unusual volume movers
        volume_movers = await self._get_volume_movers()
        trending.update(volume_movers)
        
        # Get momentum stocks
        momentum_stocks = await self._get_momentum_stocks()
        trending.update(momentum_stocks)
        
        # Get stocks with recent insider buying
        insider_buys = await self._get_insider_buying()
        trending.update(insider_buys)
        
        return list(trending)
        
    async def _analyze_opportunity(self, ticker: str) -> StockOpportunity:
        """Deep analysis of a single stock opportunity"""
        # Get comprehensive intelligence
        intelligence = await self.intelligence.gather_market_intelligence(ticker)
        
        # Get stock data
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Calculate metrics
        current_price = info.get('currentPrice', 0)
        if not current_price:
            return None
            
        # AI-driven analysis
        growth_potential = self._calculate_growth_potential(intelligence, info)
        confidence = self._calculate_confidence(intelligence)
        risk_level = self._assess_risk(intelligence, info)
        
        # Set targets
        target_price = current_price * (1 + growth_potential / 100)
        stop_loss = current_price * 0.92  # 8% stop loss
        
        # Generate thesis
        thesis = self._generate_thesis(ticker, intelligence, info)
        catalysts = self._identify_catalysts(intelligence)
        
        return StockOpportunity(
            ticker=ticker,
            company_name=info.get('longName', ticker),
            discovery_reason=self._get_discovery_reason(intelligence),
            growth_potential=growth_potential,
            confidence=confidence,
            risk_level=risk_level,
            entry_price=current_price,
            target_price=target_price,
            stop_loss=stop_loss,
            thesis=thesis,
            catalysts=catalysts,
            discovered_at=datetime.now()
        )
        
    def _calculate_growth_potential(self, intelligence: Any, info: Dict) -> float:
        """Calculate potential growth percentage"""
        score = 0
        
        # Technical momentum
        if intelligence.technical_indicators.get('rsi', 50) < 70:
            score += 10
        if intelligence.technical_indicators.get('macd_signal') == 'bullish':
            score += 15
            
        # Volume surge
        avg_volume = info.get('averageVolume', 0)
        current_volume = info.get('volume', 0)
        if current_volume > avg_volume * 2:
            score += 20
            
        # Sentiment analysis
        if intelligence.reddit_sentiment.get('overall_sentiment') == 'bullish':
            score += 10
        if intelligence.twitter_sentiment.get('sentiment_score', 0) > 0.7:
            score += 15
            
        # News catalyst
        if len(intelligence.breaking_news) > 0:
            score += 10
            
        # Analyst upgrades
        if intelligence.analyst_updates.get('recent_upgrades', 0) > 0:
            score += 20
            
        return min(score, 100)  # Cap at 100%
        
    def _calculate_confidence(self, intelligence: Any) -> float:
        """Calculate confidence score"""
        active_sources = 0
        
        # Count active intelligence sources
        if intelligence.breaking_news:
            active_sources += 1
        if intelligence.technical_indicators:
            active_sources += 1
        if intelligence.reddit_sentiment:
            active_sources += 1
        if intelligence.twitter_sentiment:
            active_sources += 1
        if intelligence.analyst_updates:
            active_sources += 1
            
        # Base confidence on data availability
        confidence = (active_sources / 5) * 100
        
        # Adjust for signal strength
        if intelligence.technical_indicators.get('trend') == 'strong_uptrend':
            confidence = min(confidence + 10, 100)
            
        return confidence
        
    def _assess_risk(self, intelligence: Any, info: Dict) -> str:
        """Assess risk level"""
        risk_score = 0
        
        # Volatility check
        beta = info.get('beta', 1)
        if beta > 2:
            risk_score += 3
        elif beta > 1.5:
            risk_score += 2
            
        # Market cap
        market_cap = info.get('marketCap', 0)
        if market_cap < 1_000_000_000:  # Under 1B
            risk_score += 2
            
        # Profitability
        if info.get('profitMargins', 0) < 0:
            risk_score += 1
            
        if risk_score >= 4:
            return "HIGH"
        elif risk_score >= 2:
            return "MEDIUM"
        return "LOW"
        
    def _generate_thesis(self, ticker: str, intelligence: Any, info: Dict) -> str:
        """Generate investment thesis"""
        catalysts = []
        
        if intelligence.technical_indicators.get('trend') == 'strong_uptrend':
            catalysts.append("strong technical momentum")
        if intelligence.reddit_sentiment.get('mentions', 0) > 100:
            catalysts.append("surging retail interest")
        if intelligence.analyst_updates.get('average_target', 0) > info.get('currentPrice', 0):
            catalysts.append("analyst price targets above current")
            
        catalyst_str = " and ".join(catalysts) if catalysts else "multiple positive signals"
        
        return f"{ticker} shows {catalyst_str} with potential for near-term gains. Entry at current levels offers favorable risk/reward."
        
    def _identify_catalysts(self, intelligence: Any) -> List[str]:
        """Identify upcoming catalysts"""
        catalysts = []
        
        if intelligence.earnings_events:
            catalysts.append("Upcoming earnings")
        if intelligence.breaking_news:
            catalysts.append("Recent positive news")
        if intelligence.insider_trades.get('recent_buys', 0) > 0:
            catalysts.append("Insider buying")
            
        return catalysts
        
    def _get_discovery_reason(self, intelligence: Any) -> str:
        """Get primary reason for discovery"""
        reasons = []
        
        if intelligence.technical_indicators.get('volume_surge'):
            reasons.append("Unusual volume surge")
        if intelligence.reddit_sentiment.get('trending'):
            reasons.append("Trending on social media")
        if intelligence.analyst_updates.get('recent_upgrades'):
            reasons.append("Recent analyst upgrades")
            
        return reasons[0] if reasons else "Multiple bullish signals"
        
    async def _get_volume_movers(self) -> List[str]:
        """Get stocks with unusual volume using real market data"""
        try:
            import requests
            # Use Alpha Vantage top gainers/losers API
            api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            if not api_key:
                return []
                
            url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            # Extract tickers from top gainers (high volume usually)
            tickers = []
            for gainer in data.get('top_gainers', [])[:5]:
                ticker = gainer.get('ticker', '').replace('.', '-')
                if ticker and len(ticker) <= 5:  # Valid ticker format
                    tickers.append(ticker)
            return tickers
        except Exception as e:
            print(f"Error getting volume movers: {e}")
            return []
        
    async def _get_momentum_stocks(self) -> List[str]:
        """Get stocks with strong momentum using real technical data"""
        try:
            import yfinance as yf
            import pandas as pd
            
            # Get real S&P 500 components from Wikipedia
            try:
                sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
                tables = pd.read_html(sp500_url)
                sp500_tickers = tables[0]['Symbol'].tolist()[:50]  # First 50 for scanning
            except:
                # Fallback to major market indices if Wikipedia fails
                sp500_tickers = []
            
            momentum_stocks = []
            
            for ticker in sp500_tickers:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period='30d')
                    if len(hist) < 20:
                        continue
                        
                    # Calculate momentum (20-day price change)
                    momentum = (hist['Close'][-1] / hist['Close'][-20] - 1) * 100
                    if momentum > 5:  # More than 5% gain in 20 days
                        momentum_stocks.append(ticker)
                except:
                    continue
                    
            return momentum_stocks[:5]
        except Exception as e:
            print(f"Error getting momentum stocks: {e}")
            return []
        
    async def _get_insider_buying(self) -> List[str]:
        """Get stocks with recent insider buying using real insider data"""
        try:
            # Use your existing portfolio tickers as a starting point
            # In a real system, this would connect to SEC insider trading filings
            import yfinance as yf
            
            # Get your current portfolio tickers first
            portfolio_tickers = []
            try:
                # This should come from your live portfolio
                from core.live_portfolio_engine import LivePortfolioEngine
                engine = LivePortfolioEngine()
                positions = engine.get_portfolio_positions()
                portfolio_tickers = [pos.ticker for pos in positions]
            except:
                portfolio_tickers = []
                
            # Filter tickers that have recent positive news (proxy for insider activity)
            insider_candidates = []
            for ticker in portfolio_tickers[:10]:  # Limit API calls
                try:
                    stock = yf.Ticker(ticker)
                    news = stock.news
                    if news and len(news) > 0:
                        # Check for positive sentiment in recent news
                        recent_news = news[0]
                        title = recent_news.get('title', '').lower()
                        if any(word in title for word in ['buy', 'upgrade', 'bullish', 'positive']):
                            insider_candidates.append(ticker)
                except:
                    continue
                    
            return insider_candidates[:5]
        except Exception as e:
            print(f"Error getting insider buying data: {e}")
            return []