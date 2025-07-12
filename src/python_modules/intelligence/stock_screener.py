"""
Multi-Agent Stock Screener
Based on multi_agent_stock_screener.json
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..utils.config import get_config
from ..utils.logging_system import get_logger, ScreenerCandidate

@dataclass
class ScreeningCriteria:
    """AGGRESSIVE PROFIT-HUNTING CRITERIA - Maximum gains in minimum time"""
    # EXPLOSIVE OPPORTUNITY PARAMETERS
    market_cap_min: float = 10000000    # $10M - Include micro caps for 10x potential
    market_cap_max: float = 2000000000  # $2B - Exclude slow large caps
    price_min: float = 0.50             # Include sub-$1 explosive opportunities  
    price_max: float = 100.0            # Exclude overpriced stocks
    
    # MOMENTUM & VOLUME REQUIREMENTS
    volume_spike_min: float = 3.0       # 300% volume spike minimum
    daily_volume_min: int = 1000000     # 1M+ daily volume for liquidity
    price_change_1d_min: float = 0.05   # 5%+ daily move minimum
    price_change_5d_min: float = 0.15   # 15%+ weekly momentum
    
    # TECHNICAL BREAKOUT SIGNALS
    rsi_oversold_max: float = 35.0      # Oversold bounce plays
    rsi_momentum_min: float = 60.0      # Momentum breakouts
    macd_bullish: bool = True           # MACD turning bullish
    breakout_resistance: bool = True    # Breaking key resistance
    
    # SHORT SQUEEZE POTENTIAL  
    short_interest_min: float = 15.0    # 15%+ short interest for squeeze
    days_to_cover_min: float = 3.0      # 3+ days to cover
    
    # SECTOR FOCUS
    exclude_penny_stocks: bool = False  # Include ALL explosive opportunities
    exclude_etfs: bool = True
    max_candidates: int = 20            # Focus on top opportunities only
    
    # PROFIT OPTIMIZATION
    momentum_weight: float = 3.0        # 3x weight on momentum
    catalyst_weight: float = 4.0        # 4x weight on catalysts  
    volume_weight: float = 2.5          # 2.5x weight on volume
    breakout_weight: float = 3.5        # 3.5x weight on breakouts

@dataclass
class StockCandidate:
    """Individual stock candidate data"""
    ticker: str
    company_name: str
    price: float
    market_cap: float
    volume: int
    avg_volume: float
    volume_spike_ratio: float
    short_interest: float
    rsi: float
    macd_signal: str
    bollinger_position: str
    support_resistance: Dict[str, float]
    catalyst_score: float
    technical_score: float
    volume_score: float
    squeeze_score: float
    total_score: float
    rationale: str

class TechnicalAnalyzer:
    """Technical analysis utilities"""
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return 50.0
    
    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
        """Calculate MACD indicator"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            
            return {
                "macd": macd_line.iloc[-1],
                "signal": signal_line.iloc[-1],
                "histogram": histogram.iloc[-1],
                "signal_direction": "bullish" if histogram.iloc[-1] > 0 else "bearish"
            }
        except:
            return {"macd": 0, "signal": 0, "histogram": 0, "signal_direction": "neutral"}
    
    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, Any]:
        """Calculate Bollinger Bands"""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            current_price = prices.iloc[-1]
            current_sma = sma.iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            
            # Determine position
            if current_price > current_upper:
                position = "above_upper"
            elif current_price < current_lower:
                position = "below_lower"
            elif current_price > current_sma:
                position = "above_middle"
            else:
                position = "below_middle"
            
            return {
                "upper": current_upper,
                "middle": current_sma,
                "lower": current_lower,
                "position": position,
                "width": (current_upper - current_lower) / current_sma
            }
        except:
            return {"upper": 0, "middle": 0, "lower": 0, "position": "neutral", "width": 0}
    
    @staticmethod
    def find_support_resistance(prices: pd.Series, window: int = 5) -> Dict[str, float]:
        """Find support and resistance levels"""
        try:
            highs = prices.rolling(window=window).max()
            lows = prices.rolling(window=window).min()
            
            # Find recent support and resistance
            recent_high = highs.tail(20).max()
            recent_low = lows.tail(20).min()
            
            return {
                "support": recent_low,
                "resistance": recent_high,
                "current": prices.iloc[-1]
            }
        except:
            return {"support": 0, "resistance": 0, "current": 0}

class StockScreener:
    """Main stock screening engine"""
    
    def __init__(self, criteria: Optional[ScreeningCriteria] = None):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.trading_logger = get_logger()
        self.criteria = criteria or ScreeningCriteria()
        self.technical_analyzer = TechnicalAnalyzer()
        
        # S&P 500 universe (simplified - in production this would be more comprehensive)
        self.universe = self._get_stock_universe()
    
    def _get_stock_universe(self) -> List[str]:
        """Get stock universe for explosive opportunities screening"""
        try:
            # EXPLOSIVE SMALL-CAP UNIVERSE - High growth potential stocks
            explosive_universe = [
                # Quantum Computing & Future Tech
                'QUBT', 'IONQ', 'RGTI', 'QBTS', 'IBM',
                
                # AI & Machine Learning Small Caps
                'RXRX', 'SOUN', 'BBAI', 'AI', 'SMCI', 'AGIX',
                
                # Semiconductors & Hardware
                'WOLF', 'FORM', 'CRUS', 'MPWR', 'SWKS', 'QRVO',
                
                # Biotech & Pharmaceuticals
                'SAVA', 'BIIB', 'GILD', 'MRNA', 'BNTX', 'NVAX',
                
                # EV & Clean Energy
                'SPCE', 'LCID', 'RIVN', 'QS', 'BLNK', 'CHPT',
                
                # Space & Defense
                'RKLB', 'ASTS', 'PL', 'LMT', 'RTX',
                
                # Fintech Disruptors
                'SOFI', 'HOOD', 'COIN', 'SQ', 'AFRM', 'UPST',
                
                # Cybersecurity Small Caps
                'CRWD', 'ZS', 'OKTA', 'NET', 'DDOG',
                
                # Gaming & Metaverse
                'RBLX', 'U', 'MTTR', 'TTWO', 'EA',
                
                # Meme/Momentum Stocks
                'AMC', 'GME', 'BBBY', 'CLOV', 'WISH',
                
                # Cannabis & Psychedelics
                'CGC', 'TLRY', 'SNDL', 'ACB', 'CRON',
                
                # Include some large caps for comparison
                'NVDA', 'TSLA', 'META', 'GOOGL', 'AAPL', 'MSFT'
            ]
            
            self.logger.info(f"Loaded explosive universe with {len(explosive_universe)} candidates")
            return explosive_universe
            
        except Exception as e:
            self.logger.error(f"Error getting stock universe: {e}")
            return []
    
    def _get_stock_data(self, ticker: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        """Get stock data for analysis"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            if data.empty:
                return None
            
            return data
            
        except Exception as e:
            self.logger.debug(f"Error getting data for {ticker}: {e}")
            return None
    
    def _get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """Get stock fundamental information"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "company_name": info.get("longName", ticker),
                "market_cap": info.get("marketCap", 0),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "short_interest": info.get("shortPercentFloat", 0) * 100 if info.get("shortPercentFloat") else 0,
                "avg_volume": info.get("averageVolume", 0),
                "float_shares": info.get("floatShares", 0)
            }
            
        except Exception as e:
            self.logger.debug(f"Error getting info for {ticker}: {e}")
            return {
                "company_name": ticker,
                "market_cap": 0,
                "sector": "Unknown",
                "industry": "Unknown",
                "short_interest": 0,
                "avg_volume": 0,
                "float_shares": 0
            }
    
    def _calculate_scores(self, ticker: str, data: pd.DataFrame, info: Dict[str, Any]) -> Dict[str, float]:
        """Calculate various screening scores"""
        try:
            current_price = data['Close'].iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            avg_volume = info.get("avg_volume", current_volume)
            
            # Volume score (0-100)
            volume_spike = current_volume / avg_volume if avg_volume > 0 else 1.0
            volume_score = min(100, volume_spike * 25)
            
            # Technical score (0-100)
            rsi = self.technical_analyzer.calculate_rsi(data['Close'])
            macd = self.technical_analyzer.calculate_macd(data['Close'])
            bollinger = self.technical_analyzer.calculate_bollinger_bands(data['Close'])
            
            technical_score = 0
            if 45 <= rsi <= 65:  # Neutral RSI
                technical_score += 30
            if macd['signal_direction'] == 'bullish':
                technical_score += 40
            if bollinger['position'] in ['above_middle', 'below_lower']:
                technical_score += 30
            
            # Squeeze score (compression + volume)
            squeeze_score = 0
            if bollinger['width'] < 0.1:  # Tight bollinger bands
                squeeze_score += 50
            if volume_spike > 1.5:  # Volume spike
                squeeze_score += 50
            
            # Catalyst score (based on various factors)
            catalyst_score = 0
            if info.get("short_interest", 0) > 10:  # High short interest
                catalyst_score += 40
            if volume_spike > 2.0:  # High volume spike
                catalyst_score += 30
            if current_price > 10:  # Not a penny stock
                catalyst_score += 30
            
            # Total score
            total_score = (volume_score * 0.25 + technical_score * 0.35 + 
                          squeeze_score * 0.25 + catalyst_score * 0.15)
            
            return {
                "volume_score": volume_score,
                "technical_score": technical_score,
                "squeeze_score": squeeze_score,
                "catalyst_score": catalyst_score,
                "total_score": total_score
            }
            
        except Exception as e:
            self.logger.debug(f"Error calculating scores for {ticker}: {e}")
            return {
                "volume_score": 0,
                "technical_score": 0,
                "squeeze_score": 0,
                "catalyst_score": 0,
                "total_score": 0
            }
    
    def _analyze_stock(self, ticker: str) -> Optional[StockCandidate]:
        """Analyze individual stock"""
        try:
            # Get stock data
            data = self._get_stock_data(ticker)
            if data is None or data.empty:
                return None
            
            info = self._get_stock_info(ticker)
            
            # Apply basic filters
            current_price = data['Close'].iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            market_cap = info.get("market_cap", 0)
            
            # Filter out stocks that don't meet criteria
            if current_price < self.criteria.price_min or current_price > self.criteria.price_max:
                return None
            
            if market_cap < self.criteria.market_cap_min:
                return None
            
            # Calculate technical indicators
            rsi = self.technical_analyzer.calculate_rsi(data['Close'])
            macd = self.technical_analyzer.calculate_macd(data['Close'])
            bollinger = self.technical_analyzer.calculate_bollinger_bands(data['Close'])
            support_resistance = self.technical_analyzer.find_support_resistance(data['Close'])
            
            # Calculate scores
            scores = self._calculate_scores(ticker, data, info)
            
            # Generate rationale
            rationale_parts = []
            if scores['volume_score'] > 60:
                rationale_parts.append("High volume spike")
            if scores['technical_score'] > 60:
                rationale_parts.append("Strong technical setup")
            if scores['squeeze_score'] > 60:
                rationale_parts.append("Compression pattern")
            if info.get("short_interest", 0) > 10:
                rationale_parts.append("High short interest")
            
            rationale = ", ".join(rationale_parts) if rationale_parts else "Standard screening criteria"
            
            # Calculate volume spike ratio
            avg_volume = info.get("avg_volume", current_volume)
            volume_spike_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            return StockCandidate(
                ticker=ticker,
                company_name=info.get("company_name", ticker),
                price=current_price,
                market_cap=market_cap,
                volume=current_volume,
                avg_volume=avg_volume,
                volume_spike_ratio=volume_spike_ratio,
                short_interest=info.get("short_interest", 0),
                rsi=rsi,
                macd_signal=macd['signal_direction'],
                bollinger_position=bollinger['position'],
                support_resistance=support_resistance,
                catalyst_score=scores['catalyst_score'],
                technical_score=scores['technical_score'],
                volume_score=scores['volume_score'],
                squeeze_score=scores['squeeze_score'],
                total_score=scores['total_score'],
                rationale=rationale
            )
            
        except Exception as e:
            self.logger.debug(f"Error analyzing {ticker}: {e}")
            return None
    
    def screen_stocks(self, max_workers: int = 10) -> List[StockCandidate]:
        """Screen stocks using multiple criteria"""
        try:
            self.logger.info(f"Starting stock screening with {len(self.universe)} candidates")
            
            candidates = []
            
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_ticker = {
                    executor.submit(self._analyze_stock, ticker): ticker 
                    for ticker in self.universe
                }
                
                # Collect results
                for future in as_completed(future_to_ticker):
                    ticker = future_to_ticker[future]
                    try:
                        result = future.result()
                        if result and result.total_score > 30:  # Minimum score threshold
                            candidates.append(result)
                            
                            # Log candidate
                            screener_candidate = ScreenerCandidate(
                                timestamp=datetime.now().isoformat(),
                                ticker=result.ticker,
                                company_name=result.company_name,
                                total_score=result.total_score,
                                volume_score=result.volume_score,
                                technical_score=result.technical_score,
                                squeeze_score=result.squeeze_score,
                                catalyst_score=result.catalyst_score,
                                price=result.price,
                                market_cap=result.market_cap,
                                volume_spike_ratio=result.volume_spike_ratio,
                                short_interest=result.short_interest,
                                rationale=result.rationale,
                                selected_for_analysis=result.total_score > 70
                            )
                            
                            self.trading_logger.log_screener_candidate(screener_candidate)
                            
                    except Exception as e:
                        self.logger.debug(f"Error processing {ticker}: {e}")
            
            # Sort by total score
            candidates.sort(key=lambda x: x.total_score, reverse=True)
            
            # Limit results
            candidates = candidates[:self.criteria.max_candidates]
            
            self.logger.info(f"Stock screening completed. Found {len(candidates)} candidates")
            
            return candidates
            
        except Exception as e:
            self.logger.error(f"Error in stock screening: {e}")
            return []
    
    def get_top_candidates(self, limit: int = 10) -> List[StockCandidate]:
        """Get top candidates from screening"""
        try:
            candidates = self.screen_stocks()
            return candidates[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting top candidates: {e}")
            return []
    
    def screen_with_custom_criteria(self, custom_criteria: Dict[str, Any]) -> List[StockCandidate]:
        """Screen with custom criteria"""
        try:
            # Update criteria
            for key, value in custom_criteria.items():
                if hasattr(self.criteria, key):
                    setattr(self.criteria, key, value)
            
            return self.screen_stocks()
            
        except Exception as e:
            self.logger.error(f"Error screening with custom criteria: {e}")
            return []
    
    def get_candidate_summary(self, candidates: List[StockCandidate]) -> Dict[str, Any]:
        """Get summary of screening results"""
        try:
            if not candidates:
                return {
                    "total_candidates": 0,
                    "average_score": 0,
                    "top_score": 0,
                    "high_conviction": 0,
                    "sectors": {}
                }
            
            scores = [c.total_score for c in candidates]
            high_conviction = len([c for c in candidates if c.total_score > 70])
            
            return {
                "total_candidates": len(candidates),
                "average_score": np.mean(scores),
                "top_score": max(scores),
                "high_conviction": high_conviction,
                "top_tickers": [c.ticker for c in candidates[:5]],
                "summary": f"Found {len(candidates)} candidates, {high_conviction} high conviction"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting candidate summary: {e}")
            return {}