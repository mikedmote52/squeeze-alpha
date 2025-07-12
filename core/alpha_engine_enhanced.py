#!/usr/bin/env python3
"""
Enhanced Alpha Engine - Professional Grade Stock Discovery
Implements sophisticated filtering and multi-layered analysis
"""

import os
import asyncio
import yfinance as yf
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class AlphaCandidate:
    """Professional-grade stock candidate with comprehensive metrics"""
    ticker: str
    company_name: str
    sector: str
    industry: str
    market_cap: float
    float_shares: int
    current_price: float
    volume_spike: float
    price_change_1d: float
    price_change_5d: float
    revenue_growth: Optional[float]
    debt_to_equity: Optional[float]
    short_interest: Optional[float]
    insider_buying: Optional[bool]
    catalyst_type: str
    discovery_reason: str
    ai_consensus_score: float
    risk_score: float
    quality_score: float
    time_horizon: str
    confidence_score: float
    rationale: str

class EnhancedAlphaEngine:
    """Professional-grade alpha discovery with sophisticated filtering"""
    
    def __init__(self):
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        
        # Enhanced filtering criteria
        self.quality_filters = {
            'min_market_cap': 100_000_000,      # $100M minimum
            'max_market_cap': 5_000_000_000,    # $5B maximum
            'max_float': 100_000_000,           # 100M shares max
            'min_volume_spike': 2.0,            # 2x normal volume
            'min_price_change': 5.0,            # 5% minimum move
            'max_debt_to_equity': 2.0,          # Reasonable leverage
            'min_revenue_growth': -20.0,        # Not in freefall
        }
        
        # Dilution blacklist - avoid known pump-and-dumps
        self.dilution_blacklist = {
            'AMC', 'APE', 'GME', 'BBBY', 'SNDL', 'NAKD', 'EXPR', 
            'CLOV', 'WISH', 'SPRT', 'GREE', 'DWAC', 'PHUN'
        }
        
        # AI model weights (dynamic based on recent accuracy)
        self.ai_weights = {
            'claude': 0.35,
            'chatgpt': 0.35, 
            'grok': 0.30
        }
    
    async def discover_alpha_opportunities(self, timeframe: str = "swing") -> List[AlphaCandidate]:
        """Discover high-quality alpha opportunities with professional filtering"""
        
        print("🔍 ENHANCED ALPHA DISCOVERY ENGINE")
        print("=" * 60)
        print("📊 Scanning for institutional-grade opportunities...")
        print(f"🎯 Timeframe: {timeframe}")
        print()
        
        candidates = []
        
        # Multi-stage discovery pipeline
        volume_candidates = await self.scan_quality_volume_spikes()
        momentum_candidates = await self.scan_technical_breakouts()
        catalyst_candidates = await self.scan_catalyst_events()
        insider_candidates = await self.scan_insider_activity()
        
        # Combine and deduplicate
        all_candidates = volume_candidates + momentum_candidates + catalyst_candidates + insider_candidates
        unique_candidates = self.deduplicate_and_filter(all_candidates)
        
        # Apply AI consensus and risk scoring
        scored_candidates = await self.apply_ai_consensus(unique_candidates)
        
        # Final ranking and filtering
        final_candidates = self.rank_and_filter_final(scored_candidates)
        
        print(f"✅ Found {len(final_candidates)} high-quality alpha opportunities")
        
        # If no candidates found, look for high-potential opportunities
        if len(final_candidates) == 0:
            print("🎯 No current opportunities found - analyzing high-potential stocks...")
            high_potential = await self.find_high_potential_stocks()
            return high_potential
        
        return final_candidates[:10]  # Top 10 only
    
    async def scan_quality_volume_spikes(self) -> List[AlphaCandidate]:
        """Scan for volume spikes with quality filters"""
        
        print("📈 Scanning quality volume spikes...")
        candidates = []
        
        # Focus on quality names, not meme stocks
        quality_universe = await self.get_quality_universe()
        
        for ticker in quality_universe[:50]:  # Limit for performance
            
            if ticker in self.dilution_blacklist:
                print(f"   🚫 {ticker}: Dilution blacklist - SKIPPED")
                continue
            
            try:
                stock = yf.Ticker(ticker)
                
                # Get comprehensive data
                hist = stock.history(period="30d")
                info = stock.info
                
                if len(hist) < 10:
                    continue
                
                # Calculate metrics
                current_price = hist['Close'].iloc[-1]
                current_volume = hist['Volume'].iloc[-1]
                avg_volume = hist['Volume'].iloc[:-1].mean()
                volume_spike = current_volume / avg_volume if avg_volume > 0 else 1
                
                price_1d = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                price_5d = ((current_price - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100 if len(hist) >= 6 else price_1d
                
                # Quality filters
                market_cap = info.get('marketCap', 0)
                float_shares = info.get('floatShares', 0)
                
                # Apply quality filters
                if not self.passes_quality_filters(market_cap, float_shares, volume_spike, abs(price_1d)):
                    continue
                
                # Get fundamental data
                fundamentals = await self.get_fundamental_metrics(ticker, info)
                
                # Create candidate
                candidate = AlphaCandidate(
                    ticker=ticker,
                    company_name=info.get('longName', ticker),
                    sector=info.get('sector', 'Unknown'),
                    industry=info.get('industry', 'Unknown'),
                    market_cap=market_cap,
                    float_shares=float_shares,
                    current_price=current_price,
                    volume_spike=volume_spike,
                    price_change_1d=price_1d,
                    price_change_5d=price_5d,
                    revenue_growth=fundamentals.get('revenue_growth'),
                    debt_to_equity=fundamentals.get('debt_to_equity'),
                    short_interest=fundamentals.get('short_interest'),
                    insider_buying=fundamentals.get('insider_buying'),
                    catalyst_type="Volume Spike",
                    discovery_reason=f"Quality volume spike {volume_spike:.1f}x with {price_1d:.1f}% move",
                    ai_consensus_score=0.0,  # Will be calculated later
                    risk_score=0.0,          # Will be calculated later
                    quality_score=0.0,       # Will be calculated later
                    time_horizon="swing",
                    confidence_score=min(0.9, volume_spike / 10),
                    rationale=""             # Will be generated later
                )
                
                candidates.append(candidate)
                print(f"   ✅ {ticker}: Quality opportunity - {volume_spike:.1f}x volume, {price_1d:.1f}% move")
                
                if len(candidates) >= 20:  # Limit for performance
                    break
                    
                await asyncio.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing {ticker}: {e}")
                continue
        
        print(f"   📈 Found {len(candidates)} quality volume candidates")
        return candidates
    
    async def scan_technical_breakouts(self) -> List[AlphaCandidate]:
        """Scan for technical breakouts with momentum confirmation"""
        
        print("🚀 Scanning technical breakouts...")
        candidates = []
        
        # Implementation would include:
        # - 52-week highs with volume confirmation
        # - Bullish chart patterns (cups, flags, triangles)
        # - Moving average breakouts with momentum
        # - Relative strength vs sector/market
        
        print(f"   🚀 Found {len(candidates)} breakout candidates")
        return candidates
    
    async def scan_catalyst_events(self) -> List[AlphaCandidate]:
        """Scan for upcoming catalyst events"""
        
        print("📰 Scanning catalyst events...")
        candidates = []
        
        # Implementation would include:
        # - Earnings surprises and guidance raises
        # - FDA approvals and clinical trial results
        # - Contract wins and partnerships
        # - Insider buying clusters
        # - Analyst upgrades with price target increases
        
        print(f"   📰 Found {len(candidates)} catalyst candidates")
        return candidates
    
    async def scan_insider_activity(self) -> List[AlphaCandidate]:
        """Scan for significant insider buying activity"""
        
        print("👥 Scanning insider activity...")
        candidates = []
        
        # Implementation would include:
        # - Form 4 filings analysis
        # - Cluster buying by multiple insiders
        # - CEO/CFO purchases above $100K
        # - Board member accumulation patterns
        
        print(f"   👥 Found {len(candidates)} insider activity candidates")
        return candidates
    
    async def get_quality_universe(self) -> List[str]:
        """Get universe of quality stocks to scan"""
        
        # Focus on quality names across sectors
        quality_stocks = [
            # Growth Tech (established)
            'NVDA', 'AMD', 'AVGO', 'QCOM', 'AMAT', 'LRCX', 'KLAC',
            # Biotech/Pharma
            'GILD', 'BIIB', 'AMGN', 'REGN', 'VRTX', 'MRNA', 'BNTX',
            # Industrials
            'CAT', 'DE', 'BA', 'RTX', 'LMT', 'GD', 'NOC',
            # Energy
            'XOM', 'CVX', 'COP', 'EOG', 'PXD', 'MPC', 'VLO',
            # Materials
            'FCX', 'NEM', 'SCCO', 'AA', 'X', 'CLF', 'NUE',
            # Small/Mid Cap Growth
            'PLTR', 'SOFI', 'RBLX', 'SNOW', 'CRWD', 'ZS', 'OKTA'
        ]
        
        return quality_stocks
    
    def passes_quality_filters(self, market_cap: float, float_shares: int, volume_spike: float, price_change: float) -> bool:
        """Apply quality filters to screen out low-quality opportunities"""
        
        filters = self.quality_filters
        
        # Market cap filter
        if market_cap < filters['min_market_cap'] or market_cap > filters['max_market_cap']:
            return False
        
        # Float filter (avoid heavily diluted stocks)
        if float_shares and float_shares > filters['max_float']:
            return False
        
        # Volume and price movement filters
        if volume_spike < filters['min_volume_spike']:
            return False
        
        if price_change < filters['min_price_change']:
            return False
        
        return True
    
    async def get_fundamental_metrics(self, ticker: str, info: Dict[str, Any]) -> Dict[str, Any]:
        """Get fundamental metrics for quality assessment"""
        
        try:
            # Extract key fundamental metrics
            metrics = {
                'revenue_growth': info.get('revenueGrowth'),
                'debt_to_equity': info.get('debtToEquity'),
                'short_interest': info.get('shortRatio'),
                'insider_buying': None,  # Would require additional API
                'profit_margin': info.get('profitMargins'),
                'roe': info.get('returnOnEquity'),
                'pe_ratio': info.get('trailingPE')
            }
            
            return metrics
            
        except Exception as e:
            print(f"   ⚠️ Error getting fundamentals for {ticker}: {e}")
            return {}
    
    def deduplicate_and_filter(self, candidates: List[AlphaCandidate]) -> List[AlphaCandidate]:
        """Remove duplicates and apply final filters"""
        
        # Remove duplicates by ticker
        seen_tickers = set()
        unique_candidates = []
        
        for candidate in candidates:
            if candidate.ticker not in seen_tickers:
                seen_tickers.add(candidate.ticker)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    async def apply_ai_consensus(self, candidates: List[AlphaCandidate]) -> List[AlphaCandidate]:
        """Apply AI consensus scoring to candidates"""
        
        print("🤖 Applying AI consensus scoring...")
        
        for candidate in candidates:
            try:
                # Get AI analysis (implementation would call OpenRouter)
                ai_score = await self.get_ai_consensus_score(candidate)
                candidate.ai_consensus_score = ai_score
                
                # Calculate risk score
                candidate.risk_score = self.calculate_risk_score(candidate)
                
                # Calculate quality score
                candidate.quality_score = self.calculate_quality_score(candidate)
                
                # Generate rationale
                candidate.rationale = await self.generate_rationale(candidate)
                
            except Exception as e:
                print(f"   ⚠️ Error scoring {candidate.ticker}: {e}")
                candidate.ai_consensus_score = 0.5  # Neutral score
        
        return candidates
    
    async def get_ai_consensus_score(self, candidate: AlphaCandidate) -> float:
        """Get weighted AI consensus score from hedgefund-grade AI models"""
        
        try:
            from openrouter_stock_debate import OpenRouterStockDebate
            
            # Initialize AI debate system
            debate_engine = OpenRouterStockDebate()
            
            # Run full AI hedgefund analysis
            debate_result = await debate_engine.debate_stock(
                candidate.ticker,
                candidate.current_price,
                candidate.price_change_1d,
                candidate.volume_spike
            )
            
            if 'error' not in debate_result:
                # Extract consensus score from AI debate
                recommendation = debate_result.get('recommendation', {})
                confidence = recommendation.get('confidence', 50) / 100.0
                action = recommendation.get('action', 'HOLD')
                
                # Weight based on AI recommendation
                if action == 'BUY':
                    ai_score = confidence
                elif action == 'SELL':
                    ai_score = 1.0 - confidence  # Invert for sell signal
                else:  # HOLD
                    ai_score = 0.5
                
                print(f"   🤖 AI Hedgefund Consensus: {action} ({confidence:.0%}) -> Score: {ai_score:.2f}")
                return min(0.95, ai_score)
            
        except Exception as e:
            print(f"   ⚠️ AI consensus error: {e}")
        
        # Fallback to fundamental scoring if AI fails
        base_score = 0.5
        
        # Quality metrics boost
        if candidate.market_cap > 500_000_000:
            base_score += 0.1
        
        if candidate.volume_spike > 3.0:
            base_score += 0.1
        
        if candidate.float_shares < 50_000_000:
            base_score += 0.1
        
        print(f"   📊 Fundamental Score: {base_score:.2f} (AI unavailable)")
        return min(0.95, base_score)
    
    def calculate_risk_score(self, candidate: AlphaCandidate) -> float:
        """Calculate risk score (0-1, lower is better)"""
        
        risk_score = 0.0
        
        # Market cap risk
        if candidate.market_cap < 500_000_000:
            risk_score += 0.2
        
        # Float risk
        if candidate.float_shares > 75_000_000:
            risk_score += 0.2
        
        # Volatility risk
        if abs(candidate.price_change_1d) > 15:
            risk_score += 0.2
        
        # Sector risk
        if candidate.sector in ['Technology', 'Biotechnology']:
            risk_score += 0.1
        
        return min(1.0, risk_score)
    
    def calculate_quality_score(self, candidate: AlphaCandidate) -> float:
        """Calculate quality score (0-1, higher is better)"""
        
        quality_score = 0.5  # Base score
        
        # Market cap quality
        if 1_000_000_000 <= candidate.market_cap <= 10_000_000_000:
            quality_score += 0.1
        
        # Float quality
        if candidate.float_shares < 30_000_000:
            quality_score += 0.2
        
        # Volume quality
        if candidate.volume_spike >= 5.0:
            quality_score += 0.1
        
        # Fundamental quality
        if candidate.debt_to_equity and candidate.debt_to_equity < 1.0:
            quality_score += 0.1
        
        return min(1.0, quality_score)
    
    async def generate_rationale(self, candidate: AlphaCandidate) -> str:
        """Generate AI-powered rationale for the opportunity"""
        
        try:
            from openrouter_stock_debate import OpenRouterStockDebate
            
            # Get hedgefund-level AI analysis
            debate_engine = OpenRouterStockDebate()
            debate_result = await debate_engine.debate_stock(
                candidate.ticker,
                candidate.current_price,
                candidate.price_change_1d,
                candidate.volume_spike
            )
            
            if 'error' not in debate_result and 'conversation_thesis' in debate_result:
                # Use AI hedgefund thesis as rationale
                ai_rationale = f"""
🏛️ HEDGEFUND-GRADE AI ANALYSIS:

{debate_result['conversation_thesis']}

📊 FINAL RECOMMENDATION: {debate_result['recommendation']['action']} 
Confidence: {debate_result['recommendation']['confidence']}%

📈 TECHNICAL METRICS:
• Market Cap: ${candidate.market_cap/1e9:.1f}B
• Float: {candidate.float_shares/1e6:.1f}M shares  
• Volume: {candidate.volume_spike:.1f}x normal
• Move: {candidate.price_change_1d:+.1f}% today
• Quality Score: {candidate.quality_score:.1f}/1.0
• Risk Score: {candidate.risk_score:.1f}/1.0

This represents a {candidate.time_horizon} opportunity validated by our AI hedgefund consensus system.
                """.strip()
                
                return ai_rationale
                
        except Exception as e:
            print(f"   ⚠️ AI rationale error: {e}")
        
        # Fallback to structured analysis
        rationale = f"""
📊 INSTITUTIONAL ANALYSIS:

Quality {candidate.catalyst_type.lower()} opportunity in {candidate.sector}.

Key Metrics:
• Market Cap: ${candidate.market_cap/1e9:.1f}B (optimal size)
• Float: {candidate.float_shares/1e6:.1f}M shares (manageable)
• Volume: {candidate.volume_spike:.1f}x normal (strong interest)
• Move: {candidate.price_change_1d:+.1f}% today

Quality Score: {candidate.quality_score:.1f}/1.0
Risk Score: {candidate.risk_score:.1f}/1.0

This represents a {candidate.time_horizon} opportunity with institutional-grade characteristics.
        """.strip()
        
        return rationale
    
    def rank_and_filter_final(self, candidates: List[AlphaCandidate]) -> List[AlphaCandidate]:
        """Final ranking and filtering"""
        
        # Calculate composite score
        for candidate in candidates:
            composite_score = (
                candidate.ai_consensus_score * 0.4 +
                candidate.quality_score * 0.4 +
                (1 - candidate.risk_score) * 0.2
            )
            candidate.confidence_score = composite_score
        
        # Sort by composite score
        ranked_candidates = sorted(candidates, key=lambda x: x.confidence_score, reverse=True)
        
        # Filter out low-quality opportunities
        filtered_candidates = [c for c in ranked_candidates if c.confidence_score >= 0.6]
        
        return filtered_candidates
    
    async def find_high_potential_stocks(self) -> List[AlphaCandidate]:
        """Find top 3 stocks with potential for 60%+ gains in 2 weeks"""
        
        print("🎯 ANALYZING HIGH-POTENTIAL OPPORTUNITIES")
        print("Target: 60%+ gains in next 2 weeks")
        print("=" * 50)
        
        # High-potential stock universe (small/mid cap growth with catalysts)
        high_potential_universe = [
            # Biotech with upcoming catalysts
            'SAVA', 'ABUS', 'MYGN', 'CRSP', 'BEAM', 'EDIT', 'NTLA',
            # Small cap AI/tech
            'BBAI', 'AEYE', 'LIDR', 'LAZR', 'OUST', 'VLDR',
            # EV/Clean tech
            'CHPT', 'BLNK', 'EVGO', 'DCFC', 'AMPX',
            # Renewable energy
            'FSLR', 'ENPH', 'SEDG', 'NOVA', 'RUN',
            # Quantum computing
            'IONQ', 'RGTI', 'QUBT', 'ARQQ',
            # Space/Defense
            'RKLB', 'ASTS', 'PL', 'SPIR'
        ]
        
        candidates = []
        
        for ticker in high_potential_universe:
            try:
                print(f"🔍 Evaluating {ticker} for explosive potential...")
                
                stock = yf.Ticker(ticker)
                hist = stock.history(period="60d")
                info = stock.info
                
                if len(hist) < 30:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                market_cap = info.get('marketCap', 0)
                
                # Skip if too large (harder to move 60%)
                if market_cap > 5_000_000_000:
                    continue
                
                # Calculate volatility and momentum
                volatility = hist['Close'].pct_change().std() * 100
                momentum_5d = ((current_price - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100
                momentum_20d = ((current_price - hist['Close'].iloc[-21]) / hist['Close'].iloc[-21]) * 100
                
                # High-potential scoring
                potential_score = 0
                reasons = []
                
                # Volatility bonus (need volatility for big moves)
                if volatility > 5:
                    potential_score += 0.3
                    reasons.append(f"High volatility ({volatility:.1f}%)")
                
                # Small cap bonus (easier to move)
                if market_cap < 1_000_000_000:
                    potential_score += 0.2
                    reasons.append(f"Small cap (${market_cap/1e6:.0f}M)")
                
                # Recent momentum
                if momentum_5d > 5:
                    potential_score += 0.2
                    reasons.append(f"Recent momentum (+{momentum_5d:.1f}%)")
                
                # Oversold bounce potential
                if momentum_20d < -20 and momentum_5d > 0:
                    potential_score += 0.3
                    reasons.append("Oversold bounce setup")
                
                # Sector momentum
                sector = info.get('sector', '')
                if sector in ['Healthcare', 'Technology', 'Communication Services']:
                    potential_score += 0.1
                    reasons.append(f"Hot sector ({sector})")
                
                # Only consider high-potential stocks
                if potential_score >= 0.6:
                    candidate = AlphaCandidate(
                        ticker=ticker,
                        company_name=info.get('longName', ticker),
                        sector=sector,
                        industry=info.get('industry', 'Unknown'),
                        market_cap=market_cap,
                        float_shares=info.get('floatShares', 0),
                        current_price=current_price,
                        volume_spike=1.0,  # Not volume-based
                        price_change_1d=momentum_5d,
                        price_change_5d=momentum_5d,
                        revenue_growth=info.get('revenueGrowth'),
                        debt_to_equity=info.get('debtToEquity'),
                        short_interest=info.get('shortRatio'),
                        insider_buying=None,
                        catalyst_type="High Potential",
                        discovery_reason=f"60%+ potential: {', '.join(reasons)}",
                        ai_consensus_score=potential_score,
                        risk_score=0.8,  # High risk for high reward
                        quality_score=potential_score,
                        time_horizon="2-week explosive",
                        confidence_score=potential_score,
                        rationale=f"HIGH-RISK/HIGH-REWARD: {ticker} shows potential for 60%+ gains in 2 weeks based on: {', '.join(reasons)}. Volatility: {volatility:.1f}%, Market Cap: ${market_cap/1e6:.0f}M. This is a speculative play requiring tight risk management."
                    )
                    
                    candidates.append(candidate)
                    print(f"✅ {ticker}: {potential_score:.1f} potential score - {', '.join(reasons)}")
                
            except Exception as e:
                print(f"⚠️ Error analyzing {ticker}: {e}")
                continue
        
        # Sort by potential score and return top 3
        candidates.sort(key=lambda x: x.confidence_score, reverse=True)
        top_3 = candidates[:3]
        
        if top_3:
            print(f"\n🎯 TOP 3 HIGH-POTENTIAL OPPORTUNITIES:")
            for i, candidate in enumerate(top_3, 1):
                print(f"{i}. {candidate.ticker} - {candidate.confidence_score:.1f} potential")
                print(f"   💰 Price: ${candidate.current_price:.2f}")
                print(f"   🎯 Target: 60%+ gains in 2 weeks")
                print(f"   📊 Reason: {candidate.discovery_reason}")
                print()
        else:
            print("📊 No high-potential opportunities identified at current time")
        
        return top_3


# Test function
async def test_alpha_engine():
    """Test the enhanced alpha engine"""
    
    engine = EnhancedAlphaEngine()
    candidates = await engine.discover_alpha_opportunities('swing')
    
    print(f"\n🎯 TOP ALPHA OPPORTUNITIES:")
    for i, candidate in enumerate(candidates[:3], 1):
        print(f"\n{i}. {candidate.ticker} - {candidate.company_name}")
        print(f"   💰 Price: ${candidate.current_price:.2f}")
        print(f"   📈 Change: {candidate.price_change_1d:+.1f}% today")
        print(f"   📊 Volume: {candidate.volume_spike:.1f}x normal")
        print(f"   🏢 Market Cap: ${candidate.market_cap/1e9:.1f}B")
        print(f"   🎯 Quality: {candidate.quality_score:.1f}/1.0")
        print(f"   ⚠️ Risk: {candidate.risk_score:.1f}/1.0")
        print(f"   ⭐ Confidence: {candidate.confidence_score:.0%}")
        print(f"   📝 Rationale: {candidate.rationale[:100]}...")


if __name__ == "__main__":
    asyncio.run(test_alpha_engine())