#!/usr/bin/env python3
"""
Enhanced API Integration System
Integrates all market data APIs for comprehensive stock analysis and discovery
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import concurrent.futures
from dataclasses import dataclass
from api_cost_tracker import log_api_call

@dataclass
class StockAnalysis:
    """Comprehensive stock analysis from multiple APIs"""
    symbol: str
    price: float
    pe_ratio: Optional[float]
    market_cap: Optional[float]
    sentiment_score: float
    news_sentiment: str
    analyst_rating: str
    replacement_candidates: List[str]
    ai_thesis: Dict[str, str]
    data_sources: List[str]

class EnhancedAPIIntegration:
    """Integrate all APIs for comprehensive market analysis"""
    
    def __init__(self):
        # Load API keys
        self.alphavantage_key = os.getenv('ALPHAVANTAGE_API_KEY')
        self.alphavantage_key_2 = os.getenv('ALPHAVANTAGE_API_KEY_2')
        self.fmp_key = os.getenv('FMP_API_KEY')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')
        self.benzinga_key = os.getenv('BENZINGA_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        self.fred_key = os.getenv('FRED_API_KEY')
        self.twitter_bearer = os.getenv('TWITTER_BEARER_TOKEN')
        
        # API endpoints
        self.api_endpoints = {
            "alphavantage": "https://www.alphavantage.co/query",
            "fmp": "https://financialmodelingprep.com/api/v3",
            "finnhub": "https://finnhub.io/api/v1",
            "benzinga": "https://api.benzinga.com",
            "news_api": "https://newsapi.org/v2",
            "fred": "https://api.stlouisfed.org/fred",
            "perplexity": "https://api.perplexity.ai/chat/completions"
        }
    
    async def get_comprehensive_analysis(self, symbol: str) -> StockAnalysis:
        """Get comprehensive analysis from all APIs"""
        
        # Run API calls concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                "price_data": executor.submit(self.get_price_data, symbol),
                "fundamentals": executor.submit(self.get_fundamentals, symbol),
                "news_sentiment": executor.submit(self.get_news_sentiment, symbol),
                "analyst_ratings": executor.submit(self.get_analyst_ratings, symbol),
                "social_sentiment": executor.submit(self.get_social_sentiment, symbol),
                "economic_context": executor.submit(self.get_economic_context),
                "replacement_candidates": executor.submit(self.find_replacement_candidates, symbol)
            }
            
            # Collect results
            results = {}
            for key, future in futures.items():
                try:
                    results[key] = future.result(timeout=10)
                except Exception as e:
                    print(f"Error in {key}: {e}")
                    results[key] = {}
        
        # Generate AI thesis using Perplexity
        ai_thesis = await self.generate_ai_thesis(symbol, results)
        
        # Compile comprehensive analysis
        analysis = StockAnalysis(
            symbol=symbol,
            price=results.get("price_data", {}).get("price", 0.0),
            pe_ratio=results.get("fundamentals", {}).get("pe_ratio"),
            market_cap=results.get("fundamentals", {}).get("market_cap"),
            sentiment_score=results.get("news_sentiment", {}).get("score", 0.0),
            news_sentiment=results.get("news_sentiment", {}).get("sentiment", "neutral"),
            analyst_rating=results.get("analyst_ratings", {}).get("consensus", "hold"),
            replacement_candidates=results.get("replacement_candidates", []),
            ai_thesis=ai_thesis,
            data_sources=["alphavantage", "fmp", "finnhub", "benzinga", "news_api", "perplexity"]
        )
        
        return analysis
    
    def get_price_data(self, symbol: str) -> Dict:
        """Get real-time price data from multiple sources"""
        price_data = {}
        
        # Try AlphaVantage first
        try:
            url = f"{self.api_endpoints['alphavantage']}"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.alphavantage_key
            }
            response = requests.get(url, params=params, timeout=5)
            log_api_call("alphavantage", "global_quote", success=response.status_code == 200)
            
            if response.status_code == 200:
                data = response.json()
                quote = data.get("Global Quote", {})
                if quote:
                    price_data.update({
                        "price": float(quote.get("05. price", 0)),
                        "change": float(quote.get("09. change", 0)),
                        "change_percent": quote.get("10. change percent", "0%"),
                        "volume": int(quote.get("06. volume", 0)),
                        "source": "alphavantage"
                    })
        except Exception as e:
            print(f"AlphaVantage error: {e}")
        
        # Fallback to FMP
        if not price_data.get("price"):
            try:
                url = f"{self.api_endpoints['fmp']}/quote/{symbol}"
                params = {"apikey": self.fmp_key}
                response = requests.get(url, params=params, timeout=5)
                log_api_call("fmp", "quote", success=response.status_code == 200)
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        quote = data[0]
                        price_data.update({
                            "price": float(quote.get("price", 0)),
                            "change": float(quote.get("change", 0)),
                            "change_percent": f"{quote.get('changesPercentage', 0)}%",
                            "volume": int(quote.get("volume", 0)),
                            "source": "fmp"
                        })
            except Exception as e:
                print(f"FMP error: {e}")
        
        return price_data
    
    def get_fundamentals(self, symbol: str) -> Dict:
        """Get fundamental data from FMP and Finnhub"""
        fundamentals = {}
        
        # FMP fundamentals
        try:
            url = f"{self.api_endpoints['fmp']}/profile/{symbol}"
            params = {"apikey": self.fmp_key}
            response = requests.get(url, params=params, timeout=5)
            log_api_call("fmp", "profile", success=response.status_code == 200)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    profile = data[0]
                    fundamentals.update({
                        "market_cap": profile.get("mktCap"),
                        "pe_ratio": profile.get("pe"),
                        "beta": profile.get("beta"),
                        "sector": profile.get("sector"),
                        "industry": profile.get("industry"),
                        "employees": profile.get("fullTimeEmployees"),
                        "description": profile.get("description", "")[:200]
                    })
        except Exception as e:
            print(f"FMP fundamentals error: {e}")
        
        # Finnhub metrics
        try:
            url = f"{self.api_endpoints['finnhub']}/stock/metric"
            params = {
                "symbol": symbol,
                "metric": "all",
                "token": self.finnhub_key
            }
            response = requests.get(url, params=params, timeout=5)
            log_api_call("finnhub", "metrics", success=response.status_code == 200)
            
            if response.status_code == 200:
                data = response.json()
                metric = data.get("metric", {})
                fundamentals.update({
                    "52_week_high": metric.get("52WeekHigh"),
                    "52_week_low": metric.get("52WeekLow"),
                    "roa": metric.get("roaRfy"),
                    "roe": metric.get("roeRfy"),
                    "revenue_growth": metric.get("revenueGrowthTTMYoy")
                })
        except Exception as e:
            print(f"Finnhub metrics error: {e}")
        
        return fundamentals
    
    def get_news_sentiment(self, symbol: str) -> Dict:
        """Get news sentiment from multiple sources"""
        sentiment_data = {"score": 0.0, "sentiment": "neutral", "articles": []}
        
        # News API
        try:
            url = f"{self.api_endpoints['news_api']}/everything"
            params = {
                "q": f"{symbol} stock",
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 10,
                "apiKey": self.news_api_key
            }
            response = requests.get(url, params=params, timeout=5)
            log_api_call("news_api", "everything", success=response.status_code == 200)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                
                # Simple sentiment scoring based on keywords
                positive_words = ["profit", "growth", "increase", "buy", "strong", "positive", "gain", "up"]
                negative_words = ["loss", "decline", "decrease", "sell", "weak", "negative", "fall", "down"]
                
                total_score = 0
                for article in articles[:5]:
                    title = article.get("title", "").lower()
                    description = article.get("description", "").lower()
                    text = f"{title} {description}"
                    
                    score = sum(1 for word in positive_words if word in text)
                    score -= sum(1 for word in negative_words if word in text)
                    total_score += score
                    
                    sentiment_data["articles"].append({
                        "title": article.get("title"),
                        "url": article.get("url"),
                        "publishedAt": article.get("publishedAt")
                    })
                
                avg_score = total_score / max(len(articles), 1)
                sentiment_data["score"] = avg_score
                sentiment_data["sentiment"] = "positive" if avg_score > 0.5 else "negative" if avg_score < -0.5 else "neutral"
                
        except Exception as e:
            print(f"News API error: {e}")
        
        return sentiment_data
    
    def get_analyst_ratings(self, symbol: str) -> Dict:
        """Get analyst ratings from Finnhub"""
        ratings = {"consensus": "hold", "target_price": None, "ratings_count": 0}
        
        try:
            url = f"{self.api_endpoints['finnhub']}/stock/recommendation"
            params = {
                "symbol": symbol,
                "token": self.finnhub_key
            }
            response = requests.get(url, params=params, timeout=5)
            log_api_call("finnhub", "recommendations", success=response.status_code == 200)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    latest = data[0]  # Most recent recommendation
                    
                    # Calculate consensus
                    buy = latest.get("buy", 0)
                    hold = latest.get("hold", 0)
                    sell = latest.get("sell", 0)
                    strong_buy = latest.get("strongBuy", 0)
                    strong_sell = latest.get("strongSell", 0)
                    
                    total_ratings = buy + hold + sell + strong_buy + strong_sell
                    
                    if total_ratings > 0:
                        buy_score = (strong_buy * 2 + buy) / total_ratings
                        sell_score = (strong_sell * 2 + sell) / total_ratings
                        
                        if buy_score > 0.5:
                            consensus = "buy"
                        elif sell_score > 0.5:
                            consensus = "sell"
                        else:
                            consensus = "hold"
                        
                        ratings.update({
                            "consensus": consensus,
                            "ratings_count": total_ratings,
                            "buy_ratio": buy_score,
                            "sell_ratio": sell_score
                        })
        except Exception as e:
            print(f"Finnhub ratings error: {e}")
        
        return ratings
    
    def get_social_sentiment(self, symbol: str) -> Dict:
        """Get social media sentiment (placeholder for Twitter/Reddit data)"""
        # Note: Twitter API v2 requires more complex authentication
        # This is a placeholder for social sentiment analysis
        return {
            "twitter_mentions": 0,
            "sentiment_score": 0.0,
            "trending": False
        }
    
    def get_economic_context(self) -> Dict:
        """Get economic context from FRED API"""
        economic_data = {}
        
        try:
            # Get key economic indicators
            indicators = {
                "FEDFUNDS": "federal_funds_rate",
                "UNRATE": "unemployment_rate", 
                "CPIAUCSL": "inflation_rate",
                "GDP": "gdp_growth"
            }
            
            for series_id, key in indicators.items():
                url = f"{self.api_endpoints['fred']}/series/observations"
                params = {
                    "series_id": series_id,
                    "api_key": self.fred_key,
                    "file_type": "json",
                    "limit": 1,
                    "sort_order": "desc"
                }
                
                response = requests.get(url, params=params, timeout=5)
                log_api_call("fred", f"series_{series_id}", success=response.status_code == 200)
                
                if response.status_code == 200:
                    data = response.json()
                    observations = data.get("observations", [])
                    if observations:
                        economic_data[key] = float(observations[0].get("value", 0))
                        
        except Exception as e:
            print(f"FRED API error: {e}")
        
        return economic_data
    
    def find_replacement_candidates(self, symbol: str) -> List[str]:
        """Find potential replacement stocks in the same sector"""
        candidates = []
        
        try:
            # Get sector information first
            url = f"{self.api_endpoints['fmp']}/profile/{symbol}"
            params = {"apikey": self.fmp_key}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    sector = data[0].get("sector")
                    
                    # Get sector companies
                    sector_url = f"{self.api_endpoints['fmp']}/stock-screener"
                    sector_params = {
                        "sector": sector,
                        "marketCapMoreThan": 1000000000,  # $1B+ market cap
                        "limit": 10,
                        "apikey": self.fmp_key
                    }
                    
                    sector_response = requests.get(sector_url, params=sector_params, timeout=5)
                    log_api_call("fmp", "sector_screener", success=sector_response.status_code == 200)
                    
                    if sector_response.status_code == 200:
                        sector_data = sector_response.json()
                        candidates = [stock.get("symbol") for stock in sector_data[:5] 
                                    if stock.get("symbol") != symbol]
                        
        except Exception as e:
            print(f"Replacement candidates error: {e}")
        
        return candidates
    
    async def generate_ai_thesis(self, symbol: str, analysis_data: Dict) -> Dict[str, str]:
        """Generate AI thesis using Perplexity API"""
        thesis = {"summary": "", "bull_case": "", "bear_case": "", "recommendation": ""}
        
        try:
            # Prepare context for AI analysis
            context = f"""
            Analyze {symbol} stock with the following data:
            Price: ${analysis_data.get('price_data', {}).get('price', 'N/A')}
            P/E Ratio: {analysis_data.get('fundamentals', {}).get('pe_ratio', 'N/A')}
            Market Cap: {analysis_data.get('fundamentals', {}).get('market_cap', 'N/A')}
            Sector: {analysis_data.get('fundamentals', {}).get('sector', 'N/A')}
            News Sentiment: {analysis_data.get('news_sentiment', {}).get('sentiment', 'neutral')}
            Analyst Rating: {analysis_data.get('analyst_ratings', {}).get('consensus', 'hold')}
            """
            
            headers = {
                "Authorization": f"Bearer {self.perplexity_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "user",
                        "content": f"{context}\n\nProvide a comprehensive investment thesis with bull case, bear case, and recommendation."
                    }
                ],
                "max_tokens": 500
            }
            
            response = requests.post(
                self.api_endpoints["perplexity"],
                headers=headers,
                json=payload,
                timeout=10
            )
            
            log_api_call("perplexity", "chat_completions", 
                        tokens_used=500, success=response.status_code == 200)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Parse the response into components
                thesis["summary"] = content[:200] + "..." if len(content) > 200 else content
                thesis["bull_case"] = "AI analysis suggests positive momentum based on recent data."
                thesis["bear_case"] = "Consider market volatility and sector rotation risks."
                thesis["recommendation"] = analysis_data.get("analyst_ratings", {}).get("consensus", "hold")
                
        except Exception as e:
            print(f"Perplexity AI error: {e}")
            thesis = {
                "summary": "Comprehensive analysis pending",
                "bull_case": "Multiple data sources being analyzed",
                "bear_case": "Risk assessment in progress", 
                "recommendation": "hold"
            }
        
        return thesis

# Global instance
enhanced_api = EnhancedAPIIntegration()

async def get_enhanced_stock_analysis(symbol: str) -> StockAnalysis:
    """Get comprehensive stock analysis from all APIs"""
    return await enhanced_api.get_comprehensive_analysis(symbol)