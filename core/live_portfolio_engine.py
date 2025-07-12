#!/usr/bin/env python3
"""
Live Portfolio Engine - Real-time Alpaca and SOFI integration
Displays current holdings with AI recommendations
"""

import os
import asyncio
import yfinance as yf
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class PortfolioPosition:
    """Individual stock position with AI analysis"""
    ticker: str
    company_name: str
    shares: float
    current_price: float
    market_value: float
    cost_basis: float
    unrealized_pl: float
    unrealized_pl_percent: float
    day_change: float
    day_change_percent: float
    sector: str
    ai_recommendation: str  # BUY/SELL/HOLD
    ai_confidence: float    # 0-100%
    position_size_rec: str  # INCREASE/DECREASE/MAINTAIN
    thesis: str
    risk_level: str        # LOW/MEDIUM/HIGH
    target_allocation: float
    current_allocation: float

class LivePortfolioEngine:
    """Real-time portfolio analysis with AI recommendations"""
    
    def __init__(self):
        self.alpaca_key = os.getenv('ALPACA_API_KEY')
        self.alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
        self.alpaca_base_url = 'https://paper-api.alpaca.markets'  # Paper trading
        
        # Initialize Alpaca API
        if self.alpaca_key and self.alpaca_secret:
            self.alpaca = tradeapi.REST(
                self.alpaca_key,
                self.alpaca_secret,
                self.alpaca_base_url,
                api_version='v2'
            )
        else:
            self.alpaca = None
        
        # Known holdings (fallback if Alpaca not configured)
        self.fallback_holdings = {
            'AMD': 100,
            'NVAX': 50, 
            'WOLF': 75,
            'BTBT': 200,
            'CRWV': 150,
            'VIGL': 300,
            'SMCI': 25,
            'SOUN': 500
        }
    
    async def get_live_portfolio(self) -> List[PortfolioPosition]:
        """Get live portfolio with AI recommendations"""
        
        print("💰 FETCHING LIVE PORTFOLIO...")
        print("=" * 50)
        
        positions = []
        
        # Force re-initialize Alpaca with direct keys from environment
        try:
            import alpaca_trade_api as tradeapi
            from dotenv import load_dotenv
            load_dotenv()
            
            # Get API keys directly
            alpaca_key = os.getenv('ALPACA_API_KEY')
            alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
            
            if alpaca_key and alpaca_secret:
                print(f"🔑 Connecting to Alpaca with key: {alpaca_key[:10]}...")
                
                # Create fresh Alpaca connection with proper error handling
                api = tradeapi.REST(
                    key_id=alpaca_key,
                    secret_key=alpaca_secret,
                    base_url='https://paper-api.alpaca.markets',
                    api_version='v2'
                )
                
                # Test connection and get account info
                account = api.get_account()
                total_portfolio_value = float(account.portfolio_value)
                cash = float(account.cash)
                
                print(f"✅ Alpaca Connected!")
                print(f"   Portfolio Value: ${total_portfolio_value:,.2f}")
                print(f"   Available Cash: ${cash:,.2f}")
                
                # Get actual positions with proper parameters
                alpaca_positions = api.list_positions()
                print(f"   Active Positions: {len(alpaca_positions)}")
                
                # Show position details
                for pos in alpaca_positions:
                    print(f"   ✅ {pos.symbol}: {pos.qty} shares = ${pos.market_value}")
                
                if len(alpaca_positions) == 0:
                    print("❌ No positions found in Alpaca account")
                    print(f"   Account Value: ${total_portfolio_value:,.2f}")
                    print(f"   Available Cash: ${cash:,.2f}")
                    print("💡 Your account has cash but no stock positions")
                    print("🔍 Check your Alpaca dashboard to see if positions exist")
                    return []
                else:
                    print("📊 Processing real Alpaca positions...")
                    for position in alpaca_positions:
                        print(f"   Found: {position.symbol} - {position.qty} shares - ${position.market_value}")
                        
                        # Force comprehensive intelligence analysis
                        print(f"   🧠 Running hedge fund analysis for {position.symbol}...")
                        pos = await self.create_enhanced_position_analysis(
                            position.symbol,
                            float(position.qty),
                            float(position.market_value),
                            float(position.cost_basis) if position.cost_basis else float(position.market_value),
                            float(position.unrealized_pl) if position.unrealized_pl else 0,
                            total_portfolio_value
                        )
                        if pos:
                            positions.append(pos)
                            
            else:
                print("❌ Alpaca API keys not found")
                positions = await self.get_enhanced_demo_portfolio()
                
        except Exception as e:
            print(f"⚠️ Alpaca connection error: {e}")
            print("🔄 Using enhanced demo portfolio")
            positions = await self.get_enhanced_demo_portfolio()
        
        # Sort by portfolio allocation (largest first)
        positions.sort(key=lambda x: x.current_allocation, reverse=True)
        
        return positions
    
    async def get_enhanced_demo_portfolio(self) -> List[PortfolioPosition]:
        """Get enhanced demo portfolio with real market data and hedge fund analysis"""
        
        print("🎯 Creating enhanced demo portfolio with real market data...")
        
        # Realistic portfolio based on current market conditions
        enhanced_holdings = {
            'NVDA': 25,    # AI leader - should get strong BUY
            'AMD': 50,     # AI/datacenter play
            'TSLA': 15,    # EV/tech stock
            'AAPL': 20,    # Large cap tech
            'MSFT': 18,    # Cloud/AI infrastructure
            'GOOGL': 12,   # AI/search
            'META': 10,    # Social/VR
            'AMZN': 8,     # Cloud/commerce
        }
        
        positions = []
        total_value = 100000  # $100k demo portfolio
        
        # Calculate realistic allocations
        for ticker, shares in enhanced_holdings.items():
            try:
                pos = await self.create_position_analysis(
                    ticker, shares, 0, 0, 0, total_value
                )
                if pos:
                    positions.append(pos)
                    print(f"   ✅ {ticker}: {shares} shares - AI analyzing...")
            except Exception as e:
                print(f"   ⚠️ Error analyzing {ticker}: {e}")
        
        return positions
    
    async def get_fallback_portfolio(self) -> List[PortfolioPosition]:
        """Get portfolio using fallback holdings"""
        
        positions = []
        total_value = 0
        
        # First pass: calculate total value
        for ticker, shares in self.fallback_holdings.items():
            try:
                stock = yf.Ticker(ticker)
                price = stock.history(period='1d')['Close'].iloc[-1]
                market_value = shares * price
                total_value += market_value
            except:
                continue
        
        # Second pass: create positions
        for ticker, shares in self.fallback_holdings.items():
            try:
                pos = await self.create_position_analysis(
                    ticker, shares, 0, 0, 0, total_value
                )
                if pos:
                    positions.append(pos)
            except Exception as e:
                print(f"⚠️ Error analyzing {ticker}: {e}")
        
        return positions
    
    async def create_enhanced_position_analysis(self, ticker: str, shares: float,
                                               market_value: float, cost_basis: float,
                                               unrealized_pl: float, total_portfolio_value: float):
        """Create enhanced position analysis with comprehensive intelligence"""
        
        try:
            # Get comprehensive market intelligence
            from core.comprehensive_intelligence_engine import ComprehensiveIntelligenceEngine
            
            intel_engine = ComprehensiveIntelligenceEngine()
            print(f"      📡 Gathering intelligence for {ticker}...")
            intelligence = await intel_engine.gather_comprehensive_intelligence(ticker)
            
            # Get basic stock data
            import yfinance as yf
            stock = yf.Ticker(ticker)
            hist = stock.history(period='5d')
            info = stock.info
            
            if len(hist) < 2:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            day_change = current_price - prev_price
            day_change_percent = (day_change / prev_price) * 100
            
            unrealized_pl_percent = (unrealized_pl / (cost_basis * shares)) * 100 if cost_basis > 0 else 0
            current_allocation = (market_value / total_portfolio_value) * 100
            
            # HEDGE FUND ANALYSIS - Real portfolio optimization
            recommendation, confidence, thesis = await self._hedge_fund_analysis(
                ticker, current_price, day_change_percent, unrealized_pl_percent, 
                current_allocation, intelligence
            )
            
            # Position sizing recommendation
            position_sizing, target_allocation = self._optimal_position_sizing(
                recommendation, confidence, unrealized_pl_percent, current_allocation
            )
            
            position = PortfolioPosition(
                ticker=ticker,
                company_name=info.get('longName', ticker),
                shares=shares,
                current_price=current_price,
                market_value=market_value,
                cost_basis=cost_basis,
                unrealized_pl=unrealized_pl,
                unrealized_pl_percent=unrealized_pl_percent,
                day_change=day_change,
                day_change_percent=day_change_percent,
                sector=info.get('sector', 'Unknown'),
                ai_recommendation=recommendation,
                ai_confidence=confidence,
                position_size_rec=position_sizing,
                thesis=thesis,
                risk_level=self.calculate_risk_level(ticker, day_change_percent, unrealized_pl_percent),
                target_allocation=target_allocation,
                current_allocation=current_allocation
            )
            
            print(f"      ✅ {ticker}: {recommendation} ({confidence}%) - {thesis[:50]}...")
            return position
            
        except Exception as e:
            print(f"      ⚠️ Enhanced analysis failed for {ticker}, using basic: {e}")
            return await self.create_position_analysis(ticker, shares, market_value, cost_basis, unrealized_pl, total_portfolio_value)
    
    async def _hedge_fund_analysis(self, ticker: str, price: float, day_change: float, 
                                 unrealized_pl: float, allocation: float, intelligence) -> tuple:
        """Real hedge fund-level portfolio optimization analysis"""
        
        # PORTFOLIO OPTIMIZATION LOGIC
        score = 0
        factors = []
        
        # 1. PERFORMANCE ANALYSIS (40% weight)
        if unrealized_pl < -10:  # Losing positions
            score -= 30
            factors.append(f"Underperforming: {unrealized_pl:.1f}%")
            if unrealized_pl < -20:  # Major losers
                score -= 20
                factors.append("Major loss - cut immediately")
        elif unrealized_pl > 15:  # Winners
            score += 20
            factors.append(f"Strong performer: +{unrealized_pl:.1f}%")
        
        # 2. DAILY MOMENTUM (20% weight)  
        if day_change < -5:  # Bad day
            score -= 15
            factors.append(f"Weak momentum: {day_change:.1f}%")
        elif day_change > 3:  # Good day
            score += 10
            factors.append(f"Strong momentum: +{day_change:.1f}%")
        
        # 3. SOCIAL SENTIMENT (20% weight)
        reddit_sentiment = intelligence.reddit_sentiment.get('sentiment', 'neutral')
        twitter_sentiment = intelligence.twitter_sentiment.get('sentiment', 'neutral')
        
        if reddit_sentiment in ['bearish', 'very_bearish'] or twitter_sentiment in ['bearish', 'very_bearish']:
            score -= 15
            factors.append("Negative social sentiment")
        elif reddit_sentiment in ['bullish', 'very_bullish'] or twitter_sentiment in ['bullish', 'very_bullish']:
            score += 15
            factors.append("Positive social sentiment")
        
        # 4. POSITION SIZE OPTIMIZATION (20% weight)
        if allocation > 15:  # Over-concentrated
            score -= 10
            factors.append(f"Over-allocated: {allocation:.1f}%")
        elif allocation < 3:  # Under-allocated winners
            if unrealized_pl > 10:
                score += 10
                factors.append("Underweight winner - increase")
        
        # SPECIFIC STOCK ANALYSIS
        if ticker == 'WOLF' and (unrealized_pl < -10 or day_change < -10):
            score -= 25
            factors.append("WOLF: EV sector struggling")
        
        if ticker == 'AMD' and day_change > 0:
            score += 15
            factors.append("AMD: AI semiconductor leader")
        
        if ticker in ['NVAX', 'BYND'] and unrealized_pl < 0:
            score -= 20
            factors.append(f"{ticker}: Struggling sector")
        
        # Convert to recommendation
        if score <= -30:
            recommendation = "SELL"
            confidence = min(95, 80 + abs(score + 30) // 2)
            thesis = f"SELL IMMEDIATELY: {', '.join(factors[:2])}. Portfolio optimization requires cutting losers."
        elif score <= -15:
            recommendation = "SELL"
            confidence = min(85, 70 + abs(score + 15))
            thesis = f"REDUCE POSITION: {', '.join(factors[:2])}. Underperforming allocation."
        elif score >= 25:
            recommendation = "BUY"
            confidence = min(95, 70 + (score - 25))
            thesis = f"STRONG BUY: {', '.join(factors[:2])}. Increase allocation for optimization."
        elif score >= 10:
            recommendation = "BUY"
            confidence = min(85, 60 + (score - 10))
            thesis = f"ACCUMULATE: {', '.join(factors[:2])}. Good addition to portfolio."
        else:
            recommendation = "HOLD"
            confidence = max(55, 65 + score)
            thesis = f"MAINTAIN: {', '.join(factors[:2]) if factors else 'Neutral position'}. No changes needed."
        
        return recommendation, int(confidence), thesis
    
    def _optimal_position_sizing(self, recommendation: str, confidence: int, 
                               unrealized_pl: float, current_allocation: float) -> tuple:
        """Calculate optimal position sizing for portfolio optimization"""
        
        if recommendation == "SELL":
            if confidence > 85:
                return "SELL ALL", 0.0
            else:
                return "REDUCE 50%", max(2.0, current_allocation * 0.5)
        
        elif recommendation == "BUY":
            if confidence > 85:
                return "INCREASE 50%", min(15.0, current_allocation * 1.5)
            else:
                return "ADD 25%", min(12.0, current_allocation * 1.25)
        
        else:  # HOLD
            return "MAINTAIN", current_allocation
    
    async def create_position_analysis(self, ticker: str, shares: float, 
                                     market_value: float, cost_basis: float,
                                     unrealized_pl: float, total_portfolio_value: float) -> Optional[PortfolioPosition]:
        """Create detailed position analysis with AI recommendations"""
        
        try:
            # Get stock data
            stock = yf.Ticker(ticker)
            hist = stock.history(period='5d')
            info = stock.info
            
            if len(hist) < 2:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            day_change = current_price - prev_price
            day_change_percent = (day_change / prev_price) * 100
            
            # Calculate values if not from Alpaca
            if market_value == 0:
                market_value = shares * current_price
                cost_basis = current_price * 0.95  # Estimate
                unrealized_pl = market_value - (cost_basis * shares)
            
            unrealized_pl_percent = (unrealized_pl / (cost_basis * shares)) * 100 if cost_basis > 0 else 0
            current_allocation = (market_value / total_portfolio_value) * 100
            
            # Generate AI recommendation
            ai_rec = await self.generate_ai_recommendation(ticker, current_price, 
                                                         day_change_percent, unrealized_pl_percent)
            
            # Generate thesis
            thesis = await self.generate_stock_thesis(ticker, info, current_price, day_change_percent)
            
            position = PortfolioPosition(
                ticker=ticker,
                company_name=info.get('longName', ticker),
                shares=shares,
                current_price=current_price,
                market_value=market_value,
                cost_basis=cost_basis,
                unrealized_pl=unrealized_pl,
                unrealized_pl_percent=unrealized_pl_percent,
                day_change=day_change,
                day_change_percent=day_change_percent,
                sector=info.get('sector', 'Unknown'),
                ai_recommendation=ai_rec['action'],
                ai_confidence=ai_rec['confidence'],
                position_size_rec=ai_rec['position_sizing'],
                thesis=thesis,
                risk_level=self.calculate_risk_level(ticker, day_change_percent, unrealized_pl_percent),
                target_allocation=ai_rec['target_allocation'],
                current_allocation=current_allocation
            )
            
            return position
            
        except Exception as e:
            print(f"⚠️ Error creating position for {ticker}: {e}")
            return None
    
    async def generate_ai_recommendation(self, ticker: str, price: float, 
                                       day_change: float, unrealized_pl: float) -> Dict[str, Any]:
        """Generate hedge fund-level AI recommendation using comprehensive intelligence"""
        
        try:
            # Import comprehensive intelligence engine
            from core.comprehensive_intelligence_engine import ComprehensiveIntelligenceEngine
            
            # Gather comprehensive market intelligence
            intel_engine = ComprehensiveIntelligenceEngine()
            intelligence = await intel_engine.gather_comprehensive_intelligence(ticker)
            
            # Analyze using comprehensive data
            recommendation, confidence = await self._analyze_with_intelligence(
                ticker, price, day_change, unrealized_pl, intelligence
            )
            
            # Determine position sizing based on analysis
            position_sizing, target_allocation = self._calculate_position_sizing(
                recommendation, confidence, unrealized_pl, intelligence
            )
            
            return {
                'action': recommendation,
                'confidence': confidence,
                'position_sizing': position_sizing,
                'target_allocation': target_allocation,
                'intelligence_used': True,
                'data_sources': self._count_active_sources(intelligence)
            }
            
        except Exception as e:
            print(f"⚠️ Intelligence engine error for {ticker}: {e}")
            # Fallback to basic analysis
            return await self._generate_basic_recommendation(ticker, price, day_change, unrealized_pl)
    
    async def _analyze_with_intelligence(self, ticker: str, price: float, day_change: float, 
                                       unrealized_pl: float, intelligence) -> tuple:
        """Analyze stock using comprehensive intelligence"""
        
        # Initialize scoring system
        score = 0
        confidence_factors = []
        
        # 1. SOCIAL SENTIMENT ANALYSIS (30% weight)
        reddit_sentiment = intelligence.reddit_sentiment.get('sentiment', 'neutral')
        twitter_sentiment = intelligence.twitter_sentiment.get('sentiment', 'neutral')
        
        social_score = 0
        if reddit_sentiment in ['bullish', 'very_bullish']:
            social_score += 15
            confidence_factors.append(f"Reddit bullish ({intelligence.reddit_sentiment.get('mentions', 0)} mentions)")
        elif reddit_sentiment in ['bearish', 'very_bearish']:
            social_score -= 15
            confidence_factors.append(f"Reddit bearish ({intelligence.reddit_sentiment.get('mentions', 0)} mentions)")
        
        if twitter_sentiment in ['bullish', 'very_bullish']:
            social_score += 15
            confidence_factors.append(f"Twitter bullish ({intelligence.twitter_sentiment.get('mentions', 0)} mentions)")
        elif twitter_sentiment in ['bearish', 'very_bearish']:
            social_score -= 15
            confidence_factors.append(f"Twitter bearish ({intelligence.twitter_sentiment.get('mentions', 0)} mentions)")
        
        score += social_score
        
        # 2. NEWS AND ANALYST SENTIMENT (25% weight)
        news_count = len(intelligence.breaking_news)
        analyst_count = len(intelligence.analyst_updates.get('recent_reports', []))
        
        if news_count > 3:
            score += 10
            confidence_factors.append(f"{news_count} recent news articles")
        
        if analyst_count > 0:
            score += 15
            confidence_factors.append(f"{analyst_count} analyst updates")
        
        # 3. OPTIONS FLOW ANALYSIS (20% weight)
        options_sentiment = intelligence.options_flow.get('sentiment', 'neutral')
        put_call_ratio = intelligence.options_flow.get('put_call_ratio', 1.0)
        
        if options_sentiment == 'bullish' or put_call_ratio < 0.7:
            score += 20
            confidence_factors.append(f"Bullish options flow (P/C: {put_call_ratio:.2f})")
        elif options_sentiment == 'bearish' or put_call_ratio > 1.3:
            score -= 20
            confidence_factors.append(f"Bearish options flow (P/C: {put_call_ratio:.2f})")
        
        # 4. TECHNICAL PERFORMANCE (15% weight)
        if unrealized_pl > 15:
            score += 10
            confidence_factors.append(f"Strong performer (+{unrealized_pl:.1f}%)")
        elif unrealized_pl < -15:
            score -= 15
            confidence_factors.append(f"Underperformer ({unrealized_pl:.1f}%)")
        
        if day_change > 3:
            score += 5
            confidence_factors.append(f"Strong daily momentum (+{day_change:.1f}%)")
        elif day_change < -3:
            score -= 5
            confidence_factors.append(f"Weak daily momentum ({day_change:.1f}%)")
        
        # 5. REGULATORY/POLITICAL FACTORS (10% weight)
        congressional_trades = len(intelligence.congressional_trades)
        fda_events = len(intelligence.fda_events)
        
        if congressional_trades > 0:
            score += 5
            confidence_factors.append(f"{congressional_trades} recent congressional trades")
        
        if fda_events > 0:
            score += 5
            confidence_factors.append(f"{fda_events} FDA events scheduled")
        
        # Convert score to recommendation
        if score >= 40:
            recommendation = "BUY"
            confidence = min(95, 70 + (score - 40))
        elif score >= 15:
            recommendation = "HOLD"  
            confidence = min(85, 60 + (score - 15))
        elif score >= -15:
            recommendation = "HOLD"
            confidence = max(55, 65 + score)
        elif score >= -40:
            recommendation = "SELL"
            confidence = min(85, 60 + abs(score + 15))
        else:
            recommendation = "SELL"
            confidence = min(95, 70 + abs(score + 40))
        
        return recommendation, int(confidence)
    
    def _calculate_position_sizing(self, recommendation: str, confidence: int, 
                                 unrealized_pl: float, intelligence) -> tuple:
        """Calculate position sizing based on analysis"""
        
        if recommendation == "BUY" and confidence > 80:
            position_sizing = "INCREASE"
            target_allocation = 15.0
        elif recommendation == "BUY":
            position_sizing = "INCREASE"
            target_allocation = 12.0
        elif recommendation == "SELL" and confidence > 80:
            position_sizing = "DECREASE"
            target_allocation = 2.0
        elif recommendation == "SELL":
            position_sizing = "DECREASE"
            target_allocation = 5.0
        else:
            position_sizing = "MAINTAIN"
            target_allocation = 8.0
        
        # Risk management adjustments
        if unrealized_pl > 50:  # Take profits on big winners
            if target_allocation > 8:
                target_allocation = 8.0
                position_sizing = "DECREASE"
        
        if unrealized_pl < -30:  # Cut losses on big losers
            target_allocation = min(target_allocation, 3.0)
            position_sizing = "DECREASE"
        
        return position_sizing, target_allocation
    
    def _count_active_sources(self, intelligence) -> int:
        """Count active intelligence sources"""
        active_count = 0
        
        # Check dictionary sources (have .get() method)
        dict_sources = [
            intelligence.reddit_sentiment,
            intelligence.twitter_sentiment,
            intelligence.options_flow,
            intelligence.dark_pool_activity,
            intelligence.institutional_flows
        ]
        
        for source in dict_sources:
            if source and not source.get('error'):
                active_count += 1
        
        # Check list sources (don't have .get() method)
        list_sources = [
            intelligence.breaking_news,
            intelligence.earnings_events,
            intelligence.congressional_trades,
            intelligence.fda_events,
            intelligence.insider_trades
        ]
        
        for source in list_sources:
            if source and len(source) > 0 and not (len(source) == 1 and source[0].get('error')):
                active_count += 1
        
        return active_count
    
    async def _generate_basic_recommendation(self, ticker: str, price: float, 
                                           day_change: float, unrealized_pl: float) -> Dict[str, Any]:
        """Fallback basic recommendation if intelligence engine fails"""
        
        # Basic performance-based logic
        if unrealized_pl > 20 and day_change > 3:
            return {'action': 'HOLD', 'confidence': 75, 'position_sizing': 'DECREASE', 'target_allocation': 8.0}
        elif unrealized_pl < -20 and day_change < -3:
            return {'action': 'SELL', 'confidence': 80, 'position_sizing': 'DECREASE', 'target_allocation': 3.0}
        elif day_change > 5:
            return {'action': 'BUY', 'confidence': 70, 'position_sizing': 'INCREASE', 'target_allocation': 12.0}
        else:
            return {'action': 'HOLD', 'confidence': 65, 'position_sizing': 'MAINTAIN', 'target_allocation': 8.0}
    
    async def generate_stock_thesis(self, ticker: str, info: Dict, price: float, day_change: float) -> str:
        """Generate detailed thesis for the stock"""
        
        sector = info.get('sector', 'Unknown')
        market_cap = info.get('marketCap', 0)
        
        # Create thesis based on stock characteristics
        if ticker == 'VIGL':
            thesis = f"Vigil Neuroscience (VIGL) - Biotech with Alzheimer's focus. Recent FDA developments and clinical trial progress. High volatility biotech play with significant upside potential but regulatory risks. Current catalyst-driven momentum."
        
        elif ticker == 'AMD':
            thesis = f"Advanced Micro Devices - AI/datacenter semiconductor leader competing with NVIDIA. Strong fundamentals in CPU/GPU markets. Benefiting from AI boom and server demand. Solid long-term growth story."
        
        elif ticker == 'NVAX':
            thesis = f"Novavax - COVID vaccine company transitioning to combination vaccines. Post-pandemic pivot strategy in progress. Volatile biotech with regulatory dependencies. Risk/reward play on vaccine portfolio expansion."
        
        elif ticker == 'WOLF':
            thesis = f"Wolfspeed - Silicon carbide semiconductor for EV/renewable energy. Clean energy transition play but execution challenges. High growth potential in EV charging and power electronics, but facing competitive pressure."
        
        elif ticker == 'SMCI':
            thesis = f"Super Micro Computer - AI server infrastructure provider. Direct NVIDIA partner benefiting from AI datacenter buildout. Strong fundamentals but accounting concerns. Premium valuation requires continued execution."
        
        else:
            # Generic thesis
            thesis = f"{info.get('longName', ticker)} - {sector} sector position. Market cap: ${market_cap/1e9:.1f}B. Current price action: {day_change:+.1f}% today. Monitoring for momentum and fundamental developments."
        
        return thesis
    
    def calculate_risk_level(self, ticker: str, day_change: float, unrealized_pl: float) -> str:
        """Calculate risk level for position"""
        
        # Biotech = high risk
        if ticker in ['VIGL', 'NVAX']:
            return "HIGH"
        
        # Large cap tech = medium risk
        if ticker in ['AMD', 'SMCI']:
            return "MEDIUM"
        
        # Small cap/speculative = high risk
        if ticker in ['WOLF', 'BTBT', 'SOUN']:
            return "HIGH"
        
        # Based on performance
        if abs(day_change) > 10 or abs(unrealized_pl) > 30:
            return "HIGH"
        elif abs(day_change) > 5 or abs(unrealized_pl) > 15:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_portfolio_summary(self, positions: List[PortfolioPosition]) -> Dict[str, Any]:
        """Generate overall portfolio analysis"""
        
        total_value = sum(pos.market_value for pos in positions)
        total_pl = sum(pos.unrealized_pl for pos in positions)
        total_pl_percent = (total_pl / (total_value - total_pl)) * 100 if total_value > total_pl else 0
        
        winners = [pos for pos in positions if pos.unrealized_pl > 0]
        losers = [pos for pos in positions if pos.unrealized_pl < 0]
        
        buy_recs = [pos for pos in positions if pos.ai_recommendation == 'BUY']
        sell_recs = [pos for pos in positions if pos.ai_recommendation == 'SELL']
        hold_recs = [pos for pos in positions if pos.ai_recommendation == 'HOLD']
        
        return {
            'total_value': total_value,
            'total_pl': total_pl,
            'total_pl_percent': total_pl_percent,
            'winners_count': len(winners),
            'losers_count': len(losers),
            'buy_recommendations': len(buy_recs),
            'sell_recommendations': len(sell_recs),
            'hold_recommendations': len(hold_recs),
            'highest_performer': max(positions, key=lambda x: x.unrealized_pl_percent) if positions else None,
            'lowest_performer': min(positions, key=lambda x: x.unrealized_pl_percent) if positions else None
        }

# Test function
async def test_portfolio_engine():
    """Test the live portfolio engine"""
    
    engine = LivePortfolioEngine()
    positions = await engine.get_live_portfolio()
    summary = engine.generate_portfolio_summary(positions)
    
    print(f"\n💰 PORTFOLIO SUMMARY:")
    print(f"Total Value: ${summary['total_value']:,.2f}")
    print(f"Total P&L: ${summary['total_pl']:,.2f} ({summary['total_pl_percent']:+.1f}%)")
    print(f"Winners: {summary['winners_count']} | Losers: {summary['losers_count']}")
    print(f"AI Recommendations: {summary['buy_recommendations']} BUY | {summary['sell_recommendations']} SELL | {summary['hold_recommendations']} HOLD")
    
    print(f"\n🏆 TOP POSITIONS:")
    for i, pos in enumerate(positions[:3], 1):
        print(f"{i}. {pos.ticker}: ${pos.market_value:,.0f} ({pos.current_allocation:.1f}%) - {pos.ai_recommendation} {pos.ai_confidence}%")

if __name__ == "__main__":
    asyncio.run(test_portfolio_engine())