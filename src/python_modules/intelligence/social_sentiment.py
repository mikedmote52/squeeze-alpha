"""
Social Sentiment Analysis
Based on social_sentiment.json
"""

import logging
import asyncio
import re
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import requests
import praw
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..utils.config import get_config
from ..utils.logging_system import get_logger
from .ai_models import OpenAIClient

@dataclass
class SentimentData:
    """Individual sentiment data point"""
    source: str
    ticker: str
    content: str
    sentiment: str  # positive, negative, neutral
    sentiment_score: float  # 0-1 scale
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class SocialPost:
    """Social media post data"""
    source: str
    title: str
    content: str
    author: str
    upvotes: int
    comments: int
    url: str
    timestamp: datetime
    tickers: List[str]

@dataclass
class CongressionalTrade:
    """Congressional trading data"""
    representative: str
    ticker: str
    transaction: str  # Purchase, Sale
    amount: str
    date: str
    sentiment: str
    sentiment_score: float
    confidence: float

@dataclass
class ValidationResult:
    """Stock validation result"""
    ticker: str
    validation: str  # strongly_positive, positive, neutral, negative, strongly_negative, insufficient_data
    social_buzz: int
    avg_sentiment: float
    weighted_score: float
    confidence: float
    sources: List[str]
    mention_count: int
    source_breakdown: Dict[str, int]
    sentiment_breakdown: Dict[str, int]

class SentimentAnalyzer:
    """AI-powered sentiment analysis"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.openai_client = OpenAIClient()
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using OpenAI"""
        try:
            prompt = f"""
            You are a financial sentiment analyst. Analyze the sentiment of the given text and respond with only a JSON object containing:
            - 'sentiment': 'positive', 'negative', or 'neutral'
            - 'score': float between 0-1 (0=very negative, 0.5=neutral, 1=very positive)
            - 'confidence': float between 0-1 indicating confidence in the analysis
            
            Text to analyze: "{text[:500]}"
            """
            
            response = await self.openai_client.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a financial sentiment analyst. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = json.loads(response)
            return {
                "sentiment": result.get("sentiment", "neutral"),
                "score": result.get("score", 0.5),
                "confidence": result.get("confidence", 0.7)
            }
            
        except Exception as e:
            self.logger.debug(f"Error analyzing sentiment: {e}")
            return {
                "sentiment": "neutral",
                "score": 0.5,
                "confidence": 0.3
            }

class RedditScraper:
    """Reddit data scraper"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.reddit = None
        self._initialize_reddit()
    
    def _initialize_reddit(self):
        """Initialize Reddit API client"""
        try:
            # These would need to be configured in config
            self.reddit = praw.Reddit(
                client_id="YOUR_REDDIT_CLIENT_ID",
                client_secret="YOUR_REDDIT_CLIENT_SECRET",
                user_agent="AI Trading System/1.0"
            )
        except Exception as e:
            self.logger.warning(f"Reddit API not configured: {e}")
    
    def scrape_wallstreetbets(self, tickers: List[str], limit: int = 100) -> List[SocialPost]:
        """Scrape WallStreetBets for ticker mentions"""
        try:
            if not self.reddit:
                return []
            
            posts = []
            subreddit = self.reddit.subreddit("wallstreetbets")
            
            # Search for each ticker
            for ticker in tickers:
                try:
                    search_results = subreddit.search(
                        query=ticker,
                        sort="hot",
                        limit=limit,
                        time_filter="day"
                    )
                    
                    for submission in search_results:
                        # Extract ticker mentions
                        content = f"{submission.title} {submission.selftext}"
                        mentioned_tickers = self._extract_tickers(content, tickers)
                        
                        if mentioned_tickers:
                            posts.append(SocialPost(
                                source="reddit_wsb",
                                title=submission.title,
                                content=submission.selftext[:300],
                                author=str(submission.author),
                                upvotes=submission.ups,
                                comments=submission.num_comments,
                                url=f"https://reddit.com{submission.permalink}",
                                timestamp=datetime.fromtimestamp(submission.created_utc),
                                tickers=mentioned_tickers
                            ))
                            
                except Exception as e:
                    self.logger.debug(f"Error searching for {ticker}: {e}")
            
            return posts
            
        except Exception as e:
            self.logger.error(f"Error scraping Reddit: {e}")
            return []
    
    def _extract_tickers(self, text: str, target_tickers: List[str]) -> List[str]:
        """Extract ticker mentions from text"""
        try:
            found_tickers = []
            
            # Create regex pattern for tickers
            patterns = []
            for ticker in target_tickers:
                patterns.extend([
                    f"\\${ticker}\\b",  # $TICKER
                    f"\\b{ticker}\\b"   # TICKER
                ])
            
            pattern = f"({'|'.join(patterns)})"
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            for match in matches:
                ticker = match.replace('$', '').upper()
                if ticker in target_tickers and ticker not in found_tickers:
                    found_tickers.append(ticker)
            
            return found_tickers
            
        except Exception as e:
            self.logger.debug(f"Error extracting tickers: {e}")
            return []

class TwitterScraper:
    """Twitter data scraper using Selenium"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.driver = None
    
    def _setup_driver(self):
        """Setup Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
        except Exception as e:
            self.logger.warning(f"Could not setup Chrome driver: {e}")
    
    def scrape_twitter(self, tickers: List[str], limit: int = 50) -> List[SocialPost]:
        """Scrape Twitter for ticker mentions"""
        try:
            if not self.driver:
                self._setup_driver()
            
            if not self.driver:
                return []
            
            posts = []
            
            # Create search query
            search_query = " OR ".join([f"${ticker}" for ticker in tickers])
            encoded_query = requests.utils.quote(search_query)
            
            # Navigate to Twitter search
            url = f"https://twitter.com/search?q={encoded_query}&src=typed_query&f=live"
            self.driver.get(url)
            
            # Wait for tweets to load
            wait = WebDriverWait(self.driver, 15)
            tweets = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="tweet"]')))
            
            # Extract tweet data
            for tweet in tweets[:limit]:
                try:
                    text_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                    user_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                    time_element = tweet.find_element(By.CSS_SELECTOR, 'time')
                    
                    tweet_text = text_element.text if text_element else ""
                    user_name = user_element.text if user_element else ""
                    tweet_time = time_element.get_attribute('datetime') if time_element else ""
                    
                    # Extract mentioned tickers
                    mentioned_tickers = self._extract_tickers(tweet_text, tickers)
                    
                    if mentioned_tickers:
                        posts.append(SocialPost(
                            source="twitter",
                            title="",
                            content=tweet_text,
                            author=user_name,
                            upvotes=0,
                            comments=0,
                            url="",
                            timestamp=datetime.fromisoformat(tweet_time.replace('Z', '+00:00')) if tweet_time else datetime.now(),
                            tickers=mentioned_tickers
                        ))
                        
                except Exception as e:
                    self.logger.debug(f"Error parsing tweet: {e}")
            
            return posts
            
        except Exception as e:
            self.logger.error(f"Error scraping Twitter: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
    
    def _extract_tickers(self, text: str, target_tickers: List[str]) -> List[str]:
        """Extract ticker mentions from text"""
        try:
            found_tickers = []
            
            for ticker in target_tickers:
                patterns = [f"\\${ticker}\\b", f"\\b{ticker}\\b"]
                
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        if ticker not in found_tickers:
                            found_tickers.append(ticker)
                        break
            
            return found_tickers
            
        except Exception as e:
            self.logger.debug(f"Error extracting tickers: {e}")
            return []

class CongressionalTradingTracker:
    """Congressional trading data tracker"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
    
    def get_congressional_trades(self, tickers: List[str], limit: int = 100) -> List[CongressionalTrade]:
        """Get congressional trading data"""
        try:
            trades = []
            
            # Use QuiverQuant API (example)
            url = "https://api.quiverquant.com/beta/live/congresstrading"
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; AI Trading System/1.0)",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Filter for target tickers
                relevant_trades = [
                    trade for trade in data 
                    if trade.get('Ticker', '').upper() in [t.upper() for t in tickers]
                ][:limit]
                
                for trade in relevant_trades:
                    sentiment = "positive" if trade.get('Transaction') == "Purchase" else "negative"
                    sentiment_score = 0.8 if sentiment == "positive" else 0.2
                    
                    trades.append(CongressionalTrade(
                        representative=trade.get('Representative', ''),
                        ticker=trade.get('Ticker', '').upper(),
                        transaction=trade.get('Transaction', ''),
                        amount=trade.get('Amount', ''),
                        date=trade.get('Date', ''),
                        sentiment=sentiment,
                        sentiment_score=sentiment_score,
                        confidence=0.9
                    ))
            
            return trades
            
        except Exception as e:
            self.logger.error(f"Error getting congressional trades: {e}")
            return []

class SocialSentimentAnalyzer:
    """Main social sentiment analysis system"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.trading_logger = get_logger()
        
        # Initialize components
        self.sentiment_analyzer = SentimentAnalyzer()
        self.reddit_scraper = RedditScraper()
        self.twitter_scraper = TwitterScraper()
        self.congress_tracker = CongressionalTradingTracker()
        
        # Sentiment weighting
        self.sentiment_weights = {
            "equal": {"reddit": 0.4, "twitter": 0.4, "congress": 0.2},
            "reddit_heavy": {"reddit": 0.6, "twitter": 0.3, "congress": 0.1},
            "twitter_heavy": {"reddit": 0.3, "twitter": 0.6, "congress": 0.1},
            "congress_heavy": {"reddit": 0.3, "twitter": 0.3, "congress": 0.4}
        }
    
    async def analyze_social_sentiment(self, tickers: List[str], 
                                     max_posts_per_source: int = 100,
                                     sentiment_weight: str = "equal") -> Dict[str, Any]:
        """Analyze social sentiment for given tickers"""
        try:
            self.logger.info(f"Starting social sentiment analysis for {len(tickers)} tickers")
            
            # Scrape data from all sources
            reddit_posts = self.reddit_scraper.scrape_wallstreetbets(tickers, max_posts_per_source)
            twitter_posts = self.twitter_scraper.scrape_twitter(tickers, max_posts_per_source)
            congress_trades = self.congress_tracker.get_congressional_trades(tickers, max_posts_per_source)
            
            # Analyze sentiment for social posts
            all_sentiment_data = []
            
            # Process Reddit posts
            for post in reddit_posts:
                for ticker in post.tickers:
                    sentiment = await self.sentiment_analyzer.analyze_sentiment(post.content)
                    
                    sentiment_data = SentimentData(
                        source="reddit_wsb",
                        ticker=ticker,
                        content=post.content,
                        sentiment=sentiment["sentiment"],
                        sentiment_score=sentiment["score"],
                        confidence=sentiment["confidence"],
                        timestamp=post.timestamp,
                        metadata={
                            "title": post.title,
                            "upvotes": post.upvotes,
                            "comments": post.comments,
                            "url": post.url
                        }
                    )
                    
                    all_sentiment_data.append(sentiment_data)
            
            # Process Twitter posts
            for post in twitter_posts:
                for ticker in post.tickers:
                    sentiment = await self.sentiment_analyzer.analyze_sentiment(post.content)
                    
                    sentiment_data = SentimentData(
                        source="twitter",
                        ticker=ticker,
                        content=post.content,
                        sentiment=sentiment["sentiment"],
                        sentiment_score=sentiment["score"],
                        confidence=sentiment["confidence"],
                        timestamp=post.timestamp,
                        metadata={
                            "author": post.author
                        }
                    )
                    
                    all_sentiment_data.append(sentiment_data)
            
            # Process Congressional trades
            for trade in congress_trades:
                sentiment_data = SentimentData(
                    source="congress",
                    ticker=trade.ticker,
                    content=f"{trade.representative} {trade.transaction} {trade.amount}",
                    sentiment=trade.sentiment,
                    sentiment_score=trade.sentiment_score,
                    confidence=trade.confidence,
                    timestamp=datetime.now(),
                    metadata={
                        "representative": trade.representative,
                        "transaction": trade.transaction,
                        "amount": trade.amount,
                        "date": trade.date
                    }
                )
                
                all_sentiment_data.append(sentiment_data)
            
            # Validate AI recommendations
            validation_results = self._validate_recommendations(all_sentiment_data, tickers, sentiment_weight)
            
            # Create summary
            summary = self._create_summary(validation_results, all_sentiment_data)
            
            return {
                "validation_results": validation_results,
                "validation_summary": summary,
                "social_data": {
                    "total_analyzed": len(all_sentiment_data),
                    "reddit": len([d for d in all_sentiment_data if d.source == "reddit_wsb"]),
                    "twitter": len([d for d in all_sentiment_data if d.source == "twitter"]),
                    "congress": len([d for d in all_sentiment_data if d.source == "congress"])
                },
                "raw_data": [asdict(d) for d in all_sentiment_data]
            }
            
        except Exception as e:
            self.logger.error(f"Error in social sentiment analysis: {e}")
            return {}
    
    def _validate_recommendations(self, sentiment_data: List[SentimentData], 
                                tickers: List[str], sentiment_weight: str) -> Dict[str, ValidationResult]:
        """Validate stock recommendations against social sentiment"""
        try:
            validation_results = {}
            weights = self.sentiment_weights.get(sentiment_weight, self.sentiment_weights["equal"])
            
            for ticker in tickers:
                # Filter data for this ticker
                ticker_data = [d for d in sentiment_data if d.ticker == ticker]
                
                if not ticker_data:
                    validation_results[ticker] = ValidationResult(
                        ticker=ticker,
                        validation="insufficient_data",
                        social_buzz=0,
                        avg_sentiment=0.5,
                        weighted_score=0.5,
                        confidence=0.1,
                        sources=[],
                        mention_count=0,
                        source_breakdown={},
                        sentiment_breakdown={}
                    )
                    continue
                
                # Calculate metrics
                sources = list(set(d.source for d in ticker_data))
                avg_sentiment = sum(d.sentiment_score for d in ticker_data) / len(ticker_data)
                avg_confidence = sum(d.confidence for d in ticker_data) / len(ticker_data)
                
                # Source breakdown
                reddit_data = [d for d in ticker_data if d.source == "reddit_wsb"]
                twitter_data = [d for d in ticker_data if d.source == "twitter"]
                congress_data = [d for d in ticker_data if d.source == "congress"]
                
                # Calculate weighted scores
                reddit_score = sum(d.sentiment_score for d in reddit_data) / len(reddit_data) if reddit_data else 0.5
                twitter_score = sum(d.sentiment_score for d in twitter_data) / len(twitter_data) if twitter_data else 0.5
                congress_score = sum(d.sentiment_score for d in congress_data) / len(congress_data) if congress_data else 0.5
                
                weighted_score = (reddit_score * weights["reddit"] + 
                                twitter_score * weights["twitter"] + 
                                congress_score * weights["congress"])
                
                # Determine validation level
                validation = "neutral"
                if weighted_score > 0.6 and avg_confidence > 0.6:
                    validation = "strongly_positive"
                elif weighted_score > 0.55:
                    validation = "positive"
                elif weighted_score < 0.4 and avg_confidence > 0.6:
                    validation = "strongly_negative"
                elif weighted_score < 0.45:
                    validation = "negative"
                
                # Sentiment breakdown
                sentiment_breakdown = {
                    "positive": len([d for d in ticker_data if d.sentiment == "positive"]),
                    "negative": len([d for d in ticker_data if d.sentiment == "negative"]),
                    "neutral": len([d for d in ticker_data if d.sentiment == "neutral"])
                }
                
                validation_results[ticker] = ValidationResult(
                    ticker=ticker,
                    validation=validation,
                    social_buzz=len(ticker_data),
                    avg_sentiment=avg_sentiment,
                    weighted_score=weighted_score,
                    confidence=avg_confidence,
                    sources=sources,
                    mention_count=len(ticker_data),
                    source_breakdown={
                        "reddit": len(reddit_data),
                        "twitter": len(twitter_data),
                        "congress": len(congress_data)
                    },
                    sentiment_breakdown=sentiment_breakdown
                )
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error validating recommendations: {e}")
            return {}
    
    def _create_summary(self, validation_results: Dict[str, ValidationResult], 
                       sentiment_data: List[SentimentData]) -> Dict[str, Any]:
        """Create validation summary"""
        try:
            if not validation_results:
                return {}
            
            results = list(validation_results.values())
            
            summary = {
                "stronglyPositive": len([r for r in results if r.validation == "strongly_positive"]),
                "positive": len([r for r in results if r.validation == "positive"]),
                "neutral": len([r for r in results if r.validation == "neutral"]),
                "negative": len([r for r in results if r.validation == "negative"]),
                "stronglyNegative": len([r for r in results if r.validation == "strongly_negative"]),
                "insufficientData": len([r for r in results if r.validation == "insufficient_data"])
            }
            
            total_analyzed = len(sentiment_data)
            supported = summary["stronglyPositive"] + summary["positive"]
            challenged = summary["negative"] + summary["stronglyNegative"]
            
            summary["total_analyzed"] = total_analyzed
            summary["supported_recommendations"] = supported
            summary["challenged_recommendations"] = challenged
            summary["validation_summary"] = f"Analyzed {total_analyzed} social signals. {supported} recommendations supported, {challenged} challenged."
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error creating summary: {e}")
            return {}
    
    def get_top_validated_picks(self, validation_results: Dict[str, ValidationResult], 
                               limit: int = 5) -> List[ValidationResult]:
        """Get top validated stock picks"""
        try:
            # Filter positive validations
            positive_results = [
                r for r in validation_results.values() 
                if r.validation in ["strongly_positive", "positive"]
            ]
            
            # Sort by weighted score
            positive_results.sort(key=lambda x: x.weighted_score, reverse=True)
            
            return positive_results[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting top validated picks: {e}")
            return []