"""
SQUEEZE ALPHA - Institutional-Grade Short-Squeeze Detection System
Recreating the 60% monthly return system with advanced squeeze analytics
"""

import logging
import asyncio
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import json

from ..utils.config import get_config
from ..utils.logging_system import get_logger

@dataclass
class SqueezeMetrics:
    """Advanced short squeeze quantitative metrics"""
    short_interest_percent: float = 0.0      # % of float short
    days_to_cover: float = 0.0               # Days to cover short position
    borrow_rate: float = 0.0                 # Cost to borrow shares (APR)
    float_shares: int = 0                    # Available floating shares
    short_shares: int = 0                    # Total shares short
    utilization_rate: float = 0.0            # % of available shares borrowed
    reg_sho_threshold: bool = False          # On RegSHO threshold list
    cost_to_borrow_trend: str = "stable"     # increasing/decreasing/stable
    recent_short_change: float = 0.0         # Recent change in short interest

@dataclass  
class CatalystEvent:
    """Catalyst event with probability weighting"""
    event_type: str                          # earnings, fda, merger, etc.
    event_date: datetime                     # When event occurs
    probability: float                       # 0-1 probability of positive outcome
    impact_magnitude: float                  # Expected % move if positive
    market_awareness: float                  # 0-1 how well known the catalyst is
    timeline_certainty: float               # 0-1 certainty of timing
    catalyst_score: float = 0.0             # Calculated weighted score

@dataclass
class SqueezeCandidate:
    """Individual short squeeze opportunity"""
    ticker: str
    company_name: str
    price: float
    market_cap: float
    
    # Squeeze Metrics
    squeeze_metrics: SqueezeMetrics
    
    # Catalysts
    catalysts: List[CatalystEvent]
    
    # Scores (0-100)
    quant_score: float = 0.0                 # 40% weight - Short metrics
    catalyst_score: float = 0.0             # 35% weight - Event catalysts  
    risk_score: float = 0.0                 # 25% weight - Risk factors
    total_squeeze_score: float = 0.0        # Final weighted score
    
    # Risk Scenarios
    base_case_return: float = 0.0           # 60% probability expected return
    bull_case_return: float = 0.0           # 25% probability max upside
    bear_case_return: float = 0.0           # 15% probability downside
    
    # Execution Plan
    entry_price_target: float = 0.0
    stop_loss: float = 0.0
    profit_target_1: float = 0.0            # 30% gain target
    profit_target_2: float = 0.0            # 60% gain target  
    profit_target_3: float = 0.0            # 100%+ moonshot target
    
    position_size_percent: float = 0.0      # % of portfolio to allocate
    risk_reward_ratio: float = 0.0
    squeeze_probability: float = 0.0        # Overall squeeze probability

class SqueezeAlpha:
    """Institutional-Grade Short-Squeeze Detection System"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.trading_logger = get_logger()
        
        # Squeeze detection parameters
        self.min_short_interest = 20.0       # Minimum 20% short interest
        self.min_days_to_cover = 3.0         # Minimum 3 days to cover
        self.min_borrow_rate = 5.0           # Minimum 5% borrow cost
        self.max_market_cap = 5000000000     # $5B max market cap
        self.min_daily_volume = 500000       # 500K daily volume minimum
        
        # Squeeze universe - high short interest candidates
        self.squeeze_universe = self._get_squeeze_universe()
    
    def _get_squeeze_universe(self) -> List[str]:
        """Get universe of potential squeeze candidates"""
        # High short interest stocks across sectors
        squeeze_candidates = [
            # Meme/Reddit Favorites (Historical squeezers)
            'GME', 'AMC', 'BBBY', 'CLOV', 'WISH', 'WKHS', 'RIDE', 'SPRT',
            
            # Biotech (High short, binary events)  
            'SAVA', 'BIIB', 'GILD', 'MRNA', 'BNTX', 'NVAX', 'SRNE', 'INO',
            
            # EV/Clean Energy (Volatile, high short)
            'NKLA', 'RIDE', 'WKHS', 'QS', 'BLNK', 'CHPT', 'SPCE', 'LCID',
            
            # Fintech Disruptors
            'SOFI', 'HOOD', 'AFRM', 'UPST', 'LC', 'PYPL',
            
            # Cannabis (Regulatory catalysts)
            'TLRY', 'CGC', 'CRON', 'ACB', 'SNDL', 'HEXO',
            
            # Chinese ADRs (Delisting fears)
            'BABA', 'JD', 'PDD', 'BIDU', 'NIO', 'XPEV', 'LI',
            
            # Streaming/Media (Disruption plays)
            'NFLX', 'ROKU', 'FUBO', 'PARA', 'DIS',
            
            # Retail Disruption
            'PTON', 'TDOC', 'ZM', 'DOCN',
            
            # Short Squeeze Veterans
            'BYND', 'PLUG', 'FCEL', 'GEVO', 'KOSS', 'EXPR'
        ]
        
        self.logger.info(f"Loaded squeeze universe: {len(squeeze_candidates)} candidates")
        return squeeze_candidates
    
    def _get_short_interest_data(self, ticker: str) -> Optional[SqueezeMetrics]:
        """Get comprehensive short interest and borrow data"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract short interest metrics
            short_percent = info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0
            shares_short = info.get('sharesShort', 0)
            float_shares = info.get('floatShares', 0)
            avg_volume = info.get('averageVolume', 0)
            
            # Calculate days to cover
            days_to_cover = shares_short / avg_volume if avg_volume > 0 else 0
            
            # Note: Real borrow rate data requires premium data sources
            # For demo, we'll estimate based on short interest level
            estimated_borrow_rate = self._estimate_borrow_rate(short_percent)
            
            return SqueezeMetrics(
                short_interest_percent=short_percent,
                days_to_cover=days_to_cover,
                borrow_rate=estimated_borrow_rate,
                float_shares=float_shares,
                short_shares=shares_short,
                utilization_rate=min(100, short_percent * 1.2),  # Estimate
                reg_sho_threshold=short_percent > 30,  # Estimate threshold status
                cost_to_borrow_trend="increasing" if short_percent > 25 else "stable"
            )
            
        except Exception as e:
            self.logger.debug(f"Error getting short data for {ticker}: {e}")
            return None
    
    def _estimate_borrow_rate(self, short_percent: float) -> float:
        """Estimate borrow rate based on short interest level"""
        if short_percent > 50:
            return 25.0 + (short_percent - 50) * 2  # Very expensive
        elif short_percent > 30:
            return 15.0 + (short_percent - 30) * 0.5  # Expensive  
        elif short_percent > 20:
            return 8.0 + (short_percent - 20) * 0.7   # Moderate
        else:
            return 5.0  # Base rate
    
    def _identify_catalysts(self, ticker: str, info: Dict[str, Any]) -> List[CatalystEvent]:
        """Identify upcoming catalysts for squeeze potential"""
        catalysts = []
        
        try:
            # Earnings catalyst (always present)
            earnings_date = self._get_next_earnings_date(ticker)
            if earnings_date:
                earnings_catalyst = CatalystEvent(
                    event_type="earnings",
                    event_date=earnings_date,
                    probability=0.6,  # 60% chance of positive surprise
                    impact_magnitude=0.15,  # 15% average earnings move
                    market_awareness=0.8,  # Well known
                    timeline_certainty=0.9  # High certainty of timing
                )
                catalysts.append(earnings_catalyst)
            
            # Sector-specific catalysts
            sector = info.get('sector', '').lower()
            
            if 'healthcare' in sector or 'biotechnology' in sector:
                # FDA approval catalyst for biotech
                fda_catalyst = CatalystEvent(
                    event_type="fda_approval",
                    event_date=datetime.now() + timedelta(days=90),
                    probability=0.3,  # 30% FDA approval rate
                    impact_magnitude=0.50,  # 50% move on approval
                    market_awareness=0.6,
                    timeline_certainty=0.4  # FDA timing uncertain
                )
                catalysts.append(fda_catalyst)
            
            if 'technology' in sector:
                # Product launch catalyst
                product_catalyst = CatalystEvent(
                    event_type="product_launch", 
                    event_date=datetime.now() + timedelta(days=60),
                    probability=0.7,  # High probability
                    impact_magnitude=0.25,  # 25% move on successful launch
                    market_awareness=0.5,
                    timeline_certainty=0.6
                )
                catalysts.append(product_catalyst)
            
            # Calculate catalyst scores
            for catalyst in catalysts:
                # Weight by probability, magnitude, and timing certainty
                catalyst.catalyst_score = (
                    catalyst.probability * 0.4 +
                    catalyst.impact_magnitude * 0.3 +
                    catalyst.timeline_certainty * 0.2 +
                    (1 - catalyst.market_awareness) * 0.1  # Less known = higher alpha
                ) * 100
            
        except Exception as e:
            self.logger.debug(f"Error identifying catalysts for {ticker}: {e}")
        
        return catalysts
    
    def _get_next_earnings_date(self, ticker: str) -> Optional[datetime]:
        """Get next earnings date (simplified - would use earnings calendar API)"""
        try:
            # Simplified: estimate next earnings based on quarter
            now = datetime.now()
            # Most companies report quarterly, so next earnings within ~90 days
            return now + timedelta(days=45)  # Average 45 days to next earnings
        except:
            return None
    
    def _calculate_squeeze_scores(self, ticker: str, squeeze_metrics: SqueezeMetrics, 
                                catalysts: List[CatalystEvent], price_data: pd.DataFrame) -> Tuple[float, float, float]:
        """Calculate the three core squeeze scores"""
        
        # 1. QUANTITATIVE SCORE (40% weight) - Short squeeze metrics
        quant_score = 0
        
        # Short interest component (max 40 points)
        if squeeze_metrics.short_interest_percent > 50:
            quant_score += 40
        elif squeeze_metrics.short_interest_percent > 30:
            quant_score += 30 + (squeeze_metrics.short_interest_percent - 30) * 0.5
        elif squeeze_metrics.short_interest_percent > 20:
            quant_score += 20 + (squeeze_metrics.short_interest_percent - 20) * 1.0
        
        # Days to cover component (max 30 points)
        if squeeze_metrics.days_to_cover > 10:
            quant_score += 30
        elif squeeze_metrics.days_to_cover > 5:
            quant_score += 20 + (squeeze_metrics.days_to_cover - 5) * 2
        elif squeeze_metrics.days_to_cover > 3:
            quant_score += 10 + (squeeze_metrics.days_to_cover - 3) * 5
        
        # Borrow rate component (max 30 points)  
        if squeeze_metrics.borrow_rate > 20:
            quant_score += 30
        elif squeeze_metrics.borrow_rate > 10:
            quant_score += 15 + (squeeze_metrics.borrow_rate - 10) * 1.5
        elif squeeze_metrics.borrow_rate > 5:
            quant_score += (squeeze_metrics.borrow_rate - 5) * 3
        
        # 2. CATALYST SCORE (35% weight) - Event-driven upside
        catalyst_score = 0
        if catalysts:
            # Sum weighted catalyst scores
            total_catalyst_value = sum([c.catalyst_score for c in catalysts])
            catalyst_score = min(100, total_catalyst_value)  # Cap at 100
        
        # 3. RISK SCORE (25% weight) - Inverse risk (higher = less risky)
        risk_score = 100  # Start at max, subtract risk factors
        
        # Liquidity risk
        if len(price_data) > 20:
            avg_volume = price_data['Volume'].tail(20).mean()
            if avg_volume < 100000:
                risk_score -= 40  # Very low volume
            elif avg_volume < 500000:
                risk_score -= 20  # Low volume
        
        # Price volatility risk
        if len(price_data) > 20:
            returns = price_data['Close'].pct_change().tail(20)
            volatility = returns.std() * np.sqrt(252)  # Annualized
            if volatility > 1.5:  # >150% annual volatility
                risk_score -= 30
            elif volatility > 1.0:  # >100% annual volatility
                risk_score -= 15
        
        # Business stability (sector-based)
        # Biotech/speculative = higher risk, established = lower risk
        # This would be enhanced with fundamental analysis
        
        return max(0, quant_score), max(0, catalyst_score), max(0, risk_score)
    
    def _model_risk_scenarios(self, candidate: SqueezeCandidate) -> SqueezeCandidate:
        """Model base/bull/bear case scenarios"""
        
        # Base case (60% probability) - Normal squeeze scenario
        base_catalyst_impact = sum([c.impact_magnitude * c.probability for c in candidate.catalysts])
        short_pressure_multiplier = min(3.0, candidate.squeeze_metrics.short_interest_percent / 20)
        candidate.base_case_return = base_catalyst_impact * short_pressure_multiplier * 0.6
        
        # Bull case (25% probability) - Maximum squeeze scenario  
        max_catalyst_impact = max([c.impact_magnitude for c in candidate.catalysts]) if candidate.catalysts else 0.2
        bull_multiplier = min(5.0, candidate.squeeze_metrics.days_to_cover / 3)
        candidate.bull_case_return = max_catalyst_impact * bull_multiplier * 1.5
        
        # Bear case (15% probability) - Squeeze fails, catalyst disappointment
        bear_multiplier = 0.8 - (candidate.squeeze_metrics.short_interest_percent / 100)
        candidate.bear_case_return = -0.3 * bear_multiplier  # Max 30% downside
        
        # Calculate squeeze probability
        candidate.squeeze_probability = min(0.9, 
            (candidate.total_squeeze_score / 100) * 
            (candidate.squeeze_metrics.short_interest_percent / 50) *
            (candidate.squeeze_metrics.days_to_cover / 10)
        )
        
        return candidate
    
    def _create_execution_plan(self, candidate: SqueezeCandidate) -> SqueezeCandidate:
        """Create precise entry/exit execution plan"""
        
        current_price = candidate.price
        
        # Entry strategy - scale in on weakness
        candidate.entry_price_target = current_price * 0.98  # 2% below current
        
        # Stop loss - based on technical support and risk tolerance
        candidate.stop_loss = current_price * 0.85  # 15% stop loss
        
        # Profit targets based on scenario modeling
        candidate.profit_target_1 = current_price * (1 + 0.30)  # 30% gain - take 1/3
        candidate.profit_target_2 = current_price * (1 + 0.60)  # 60% gain - take 1/3  
        candidate.profit_target_3 = current_price * (1 + candidate.bull_case_return)  # Moonshot - let 1/3 ride
        
        # Position sizing based on conviction and risk
        base_position = 0.10  # 10% base allocation
        conviction_multiplier = candidate.total_squeeze_score / 100
        risk_adjustment = candidate.risk_score / 100
        
        candidate.position_size_percent = min(0.15, base_position * conviction_multiplier * risk_adjustment)
        
        # Risk/reward ratio
        potential_gain = candidate.base_case_return
        potential_loss = abs(candidate.bear_case_return)
        candidate.risk_reward_ratio = potential_gain / potential_loss if potential_loss > 0 else 0
        
        return candidate
    
    async def scan_squeeze_opportunities(self, max_workers: int = 10) -> List[SqueezeCandidate]:
        """Main squeeze scanning function - returns ranked opportunities"""
        
        self.logger.info(f"Starting Squeeze Alpha scan of {len(self.squeeze_universe)} candidates")
        
        candidates = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all analysis tasks
            future_to_ticker = {
                executor.submit(self._analyze_squeeze_candidate, ticker): ticker
                for ticker in self.squeeze_universe
            }
            
            # Collect results
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    candidate = future.result()
                    if candidate and candidate.total_squeeze_score > 40:  # Minimum squeeze threshold
                        candidates.append(candidate)
                        
                        self.logger.info(f"Squeeze candidate found: {ticker} (Score: {candidate.total_squeeze_score:.1f})")
                        
                except Exception as e:
                    self.logger.debug(f"Error analyzing {ticker}: {e}")
        
        # Sort by total squeeze score
        candidates.sort(key=lambda x: x.total_squeeze_score, reverse=True)
        
        self.logger.info(f"Squeeze Alpha scan complete: {len(candidates)} qualified opportunities")
        
        return candidates[:10]  # Return top 10 squeeze opportunities
    
    def _analyze_squeeze_candidate(self, ticker: str) -> Optional[SqueezeCandidate]:
        """Analyze individual squeeze candidate"""
        try:
            # Get price data
            stock = yf.Ticker(ticker)
            data = stock.history(period="3mo")
            info = stock.info
            
            if data.empty:
                return None
            
            current_price = data['Close'].iloc[-1]
            market_cap = info.get('marketCap', 0)
            
            # Filter by basic requirements
            if market_cap > self.max_market_cap:
                return None
            
            if data['Volume'].tail(20).mean() < self.min_daily_volume:
                return None
            
            # Get squeeze metrics
            squeeze_metrics = self._get_short_interest_data(ticker)
            if not squeeze_metrics:
                return None
            
            # Filter by squeeze potential
            if squeeze_metrics.short_interest_percent < self.min_short_interest:
                return None
            
            if squeeze_metrics.days_to_cover < self.min_days_to_cover:
                return None
            
            # Identify catalysts
            catalysts = self._identify_catalysts(ticker, info)
            
            # Calculate scores
            quant_score, catalyst_score, risk_score = self._calculate_squeeze_scores(
                ticker, squeeze_metrics, catalysts, data
            )
            
            # Calculate total weighted score
            total_score = (quant_score * 0.40 + catalyst_score * 0.35 + risk_score * 0.25)
            
            # Create candidate
            candidate = SqueezeCandidate(
                ticker=ticker,
                company_name=info.get('longName', ticker),
                price=current_price,
                market_cap=market_cap,
                squeeze_metrics=squeeze_metrics,
                catalysts=catalysts,
                quant_score=quant_score,
                catalyst_score=catalyst_score,
                risk_score=risk_score,
                total_squeeze_score=total_score
            )
            
            # Model scenarios and create execution plan
            candidate = self._model_risk_scenarios(candidate)
            candidate = self._create_execution_plan(candidate)
            
            return candidate
            
        except Exception as e:
            self.logger.debug(f"Error analyzing squeeze candidate {ticker}: {e}")
            return None
    
    def get_top_squeeze_plays(self, limit: int = 5) -> List[SqueezeCandidate]:
        """Get top squeeze opportunities (synchronous wrapper)"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, create new loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.scan_squeeze_opportunities())
                    candidates = future.result()
            else:
                candidates = asyncio.run(self.scan_squeeze_opportunities())
            
            return candidates[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting squeeze plays: {e}")
            return []

# Global instance
_squeeze_alpha = None

def get_squeeze_alpha() -> SqueezeAlpha:
    """Get global Squeeze Alpha instance"""
    global _squeeze_alpha
    if _squeeze_alpha is None:
        _squeeze_alpha = SqueezeAlpha()
    return _squeeze_alpha