#!/usr/bin/env python3
"""
Enhanced Collaborative AI System with Learning from 63.8% Success
Builds on proven patterns and continuously improves recommendations
"""

import asyncio
import json
import os
import requests
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from portfolio_memory_engine import RecommendationTracker, ThesisSnapshotSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedCollaborativeAI:
    """Enhanced AI system with learning from 63.8% success"""
    
    def __init__(self):
        self.recommendation_tracker = RecommendationTracker()
        self.thesis_system = ThesisSnapshotSystem()
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        
        # Success patterns from 63.8% monthly return
        self.success_patterns = {
            "VIGL": {"gain": 324.0, "float_size": 15000000, "sector": "biotechnology"},
            "CRWV": {"gain": 171.0, "float_size": 12000000, "sector": "software"},
            "AEVA": {"gain": 162.0, "float_size": 18000000, "sector": "technology"},
            "WOLF": {"gain": -25.0, "float_size": 85000000, "sector": "semiconductor"}
        }
    
    async def get_daily_explosive_recommendation(self):
        """Enhanced daily recommendation based on your proven 63.8% method"""
        
        # Update performance data
        self.recommendation_tracker.update_all_performance()
        
        # Get learning insights
        recent_performance = self.recommendation_tracker.get_recent_performance_summary()
        thesis_learning = self.thesis_system.get_learning_summary()
        
        # Build enhanced prompt with learning
        learning_context = self.build_learning_context(recent_performance, thesis_learning)
        
        enhanced_prompt = f"""What stock should I put $100 on today that has a likelihood of giving me 100% returns over the next week?

LEARNING FROM RECENT PERFORMANCE:
{learning_context}

SUCCESS PATTERNS TO REPLICATE:
- VIGL (+324%): Small biotech (15M float), FDA catalyst, perfect timing
- CRWV (+171%): Tiny software (12M float), high shorts (42%), momentum
- AEVA (+162%): Small tech breakthrough, under 20M float

FAILURE PATTERNS TO AVOID:
- WOLF (-25%): Large float (85M shares) killed squeeze potential

Consider:
- Float size (<20M shares = explosive potential)
- Short interest (>30% = squeeze pressure) 
- Upcoming catalysts (FDA, earnings, breakthrough news)
- Sector momentum (biotech, software, AI trending?)
- Pre-breakout timing (catch BEFORE explosion, not after)

Provide ONE specific recommendation with clear reasoning for 100%+ potential."""

        # Get AI recommendation using OpenRouter
        ai_response = await self.call_enhanced_openrouter_api(enhanced_prompt)
        
        # Parse and track recommendation
        ticker, reasoning, entry_price = self.parse_ai_recommendation(ai_response)
        
        if ticker and entry_price:
            self.recommendation_tracker.save_daily_recommendation(
                ticker=ticker,
                ai_model="Enhanced ChatGPT",
                reasoning=reasoning,
                entry_price=entry_price,
                question_type="100% weekly explosive"
            )
        
        return ai_response
    
    def build_learning_context(self, recent_performance, thesis_learning):
        """Build learning context for AI prompts"""
        
        context = ""
        
        if recent_performance["win_rate"] > 0:
            context += f"Win Rate (7 days): {recent_performance['win_rate']:.1f}%\n"
            
        if recent_performance["recent_winners"]:
            context += f"Recent Winners: {', '.join(recent_performance['recent_winners'])}\n"
            
        if recent_performance["recent_losers"]:
            context += f"Recent Losers: {', '.join(recent_performance['recent_losers'])}\n"
            
        if thesis_learning["successful_patterns"]:
            context += f"Successful Patterns: {', '.join(thesis_learning['successful_patterns'])}\n"
        
        context += f"Best AI Model: {recent_performance['best_ai_model']}\n"
        
        if recent_performance["win_rate"] > 60:
            context += "STATUS: Strategy working well - continue current patterns\n"
        elif recent_performance["win_rate"] < 40:
            context += "STATUS: Strategy needs adjustment - avoid recent failure patterns\n"
        
        return context
    
    async def call_enhanced_openrouter_api(self, prompt):
        """Call OpenRouter with enhanced learning prompt"""
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "HTTP-Referer": "https://github.com/mikedmote52/squeeze-alpha",
                    "X-Title": "AI Trading System - Enhanced Learning"
                },
                json={
                    "model": "openai/gpt-4-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.7
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"OpenRouter API error: {response.status_code}")
                return "AI analysis unavailable - check API connections"
                
        except Exception as e:
            logger.error(f"Enhanced AI call failed: {e}")
            return "AI analysis unavailable - check API connections"
    
    def parse_ai_recommendation(self, ai_response):
        """Parse AI response to extract ticker and price"""
        try:
            # Simple parsing - look for ticker symbols and reasoning
            import re
            
            # Look for ticker symbols (1-5 capital letters)
            tickers = re.findall(r'\b[A-Z]{1,5}\b', ai_response)
            
            # Filter out common false positives
            excluded = {'THE', 'AND', 'OR', 'FOR', 'BUT', 'NOT', 'YOU', 'CAN', 'ALL', 'NEW', 'FDA', 'SEC', 'API', 'GPT', 'AI'}
            valid_tickers = [t for t in tickers if t not in excluded]
            
            if valid_tickers:
                ticker = valid_tickers[0]  # First valid ticker
                
                # Get current price
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                
                if not hist.empty:
                    entry_price = float(hist["Close"].iloc[-1])
                    reasoning = ai_response[:200]  # First 200 chars
                    
                    return ticker, reasoning, entry_price
            
            return None, None, None
            
        except Exception as e:
            logger.error(f"Error parsing recommendation: {e}")
            return None, None, None
    
    async def analyze_current_position(self, ticker, position_data):
        """Analyze current position using enhanced AI with learning"""
        
        # Get learning insights
        recent_performance = self.recommendation_tracker.get_recent_performance_summary()
        thesis_learning = self.thesis_system.get_learning_summary()
        
        # Build context for position analysis
        position_context = f"""
        Current Position: {ticker}
        Price: ${position_data.get('current_price', 0):.2f}
        P&L: {position_data.get('unrealized_plpc', 0):+.1f}%
        Market Value: ${position_data.get('market_value', 0):,.0f}
        """
        
        learning_context = self.build_learning_context(recent_performance, thesis_learning)
        
        analysis_prompt = f"""Analyze this current position based on my 63.8% success patterns:

POSITION DETAILS:
{position_context}

LEARNING CONTEXT:
{learning_context}

SUCCESS PATTERNS:
- VIGL pattern: Small biotech, FDA catalyst, explosive potential
- CRWV pattern: Tiny float, high shorts, momentum
- AEVA pattern: Small tech breakthrough

FAILURE PATTERNS:
- WOLF pattern: Large float kills squeeze potential

Based on my proven success patterns, should I:
1. HOLD - position matches success patterns
2. BUY MORE - strong pattern match, add to winner
3. SELL HALF - take profits, reduce risk
4. SELL ALL - exit position, pattern concerns

Provide specific recommendation with reasoning based on my historical patterns."""

        # Get AI analysis
        ai_response = await self.call_enhanced_openrouter_api(analysis_prompt)
        
        return {
            "recommendation": ai_response,
            "learning_context": learning_context,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    async def get_market_sentiment_analysis(self):
        """Get enhanced market sentiment with learning"""
        
        # Get current market data
        spy = yf.Ticker("SPY")
        spy_hist = spy.history(period="5d")
        
        if not spy_hist.empty:
            current_price = float(spy_hist["Close"].iloc[-1])
            prev_price = float(spy_hist["Close"].iloc[-2])
            market_change = ((current_price - prev_price) / prev_price) * 100
        else:
            market_change = 0
        
        # Get learning insights
        recent_performance = self.recommendation_tracker.get_recent_performance_summary()
        
        sentiment_prompt = f"""Analyze current market sentiment for explosive stock opportunities:

MARKET CONDITIONS:
- SPY change: {market_change:+.1f}%
- Current session: {datetime.now().strftime('%A %H:%M')}

MY RECENT PERFORMANCE:
- Win Rate: {recent_performance['win_rate']:.1f}%
- Recent Winners: {', '.join(recent_performance['recent_winners']) if recent_performance['recent_winners'] else 'None'}
- Recent Losers: {', '.join(recent_performance['recent_losers']) if recent_performance['recent_losers'] else 'None'}

Based on current market conditions and my recent performance patterns, what sectors/types of stocks should I focus on today for 100%+ potential?

Consider:
- Market volatility impact on small caps
- Sector rotation opportunities
- Catalyst-driven opportunities (FDA, earnings, breakthroughs)
- Risk management based on recent performance"""

        ai_response = await self.call_enhanced_openrouter_api(sentiment_prompt)
        
        return {
            "sentiment_analysis": ai_response,
            "market_change": market_change,
            "performance_context": recent_performance,
            "timestamp": datetime.now().isoformat()
        }

# Integration functions for backend
async def get_enhanced_daily_recommendation():
    """Get enhanced daily recommendation with learning"""
    enhanced_ai = EnhancedCollaborativeAI()
    return await enhanced_ai.get_daily_explosive_recommendation()

async def analyze_position_with_learning(ticker, position_data):
    """Analyze position with enhanced learning"""
    enhanced_ai = EnhancedCollaborativeAI()
    return await enhanced_ai.analyze_current_position(ticker, position_data)

async def get_market_sentiment_with_learning():
    """Get market sentiment with learning"""
    enhanced_ai = EnhancedCollaborativeAI()
    return await enhanced_ai.get_market_sentiment_analysis()

if __name__ == "__main__":
    # Test the enhanced system
    async def test_enhanced_ai():
        ai = EnhancedCollaborativeAI()
        
        print("🚀 Testing Enhanced AI System...")
        
        # Test daily recommendation
        recommendation = await ai.get_daily_explosive_recommendation()
        print(f"Daily Recommendation: {recommendation}")
        
        # Test market sentiment
        sentiment = await ai.get_market_sentiment_analysis()
        print(f"Market Sentiment: {sentiment}")
    
    asyncio.run(test_enhanced_ai())