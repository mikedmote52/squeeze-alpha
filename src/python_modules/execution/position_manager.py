"""
Portfolio Position Manager
Based on get_current_positions.json
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np

from ..utils.config import get_config
from ..utils.logging_system import get_logger
from ..intelligence.market_data import get_market_data_provider

@dataclass
class Position:
    """Individual position data"""
    symbol: str
    quantity: int
    market_value: float
    cost_basis: float
    unrealized_pl: float
    unrealized_pl_percent: float
    current_price: float
    side: str  # 'long' or 'short'
    avg_entry_price: float
    timestamp: datetime

@dataclass
class PortfolioSummary:
    """Portfolio summary metrics"""
    total_equity: float
    buying_power: float
    cash_balance: float
    portfolio_value: float
    total_pl: float
    total_pl_percent: float
    day_pl: float
    day_pl_percent: float
    position_count: int
    long_market_value: float
    short_market_value: float
    timestamp: datetime

@dataclass
class PositionAnalysis:
    """Position analysis and recommendations"""
    symbol: str
    current_allocation: float
    target_allocation: float
    recommendation: str  # 'HOLD', 'BUY', 'SELL', 'REDUCE'
    allocation_delta: float
    risk_score: float
    performance_score: float
    rationale: str

class PositionManager:
    """Portfolio position management system"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.trading_logger = get_logger()
        self.market_data_provider = get_market_data_provider()
        
        # Initialize Alpaca API
        self.alpaca_api = None
        self._initialize_alpaca()
        
        # Position cache
        self.positions_cache = {}
        self.cache_timestamp = None
        self.cache_expiry_seconds = 30
    
    def _initialize_alpaca(self):
        """Initialize Alpaca API connection"""
        try:
            self.alpaca_api = tradeapi.REST(
                key_id=self.config.api_credentials.alpaca_api_key,
                secret_key=self.config.api_credentials.alpaca_secret,
                base_url=self.config.api_credentials.alpaca_base_url,
                api_version='v2'
            )
            
            # Test connection
            account = self.alpaca_api.get_account()
            self.logger.info(f"Connected to Alpaca API. Account status: {account.status}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Alpaca API: {e}")
            self.alpaca_api = None
    
    def _is_cache_valid(self) -> bool:
        """Check if position cache is still valid"""
        if not self.cache_timestamp:
            return False
        
        return (datetime.now() - self.cache_timestamp).total_seconds() < self.cache_expiry_seconds
    
    async def get_current_positions(self, force_refresh: bool = False) -> List[Position]:
        """Get current portfolio positions"""
        try:
            # Check cache first
            if not force_refresh and self._is_cache_valid():
                return list(self.positions_cache.values())
            
            if not self.alpaca_api:
                self.logger.error("Alpaca API not initialized")
                return []
            
            # Get positions from Alpaca
            alpaca_positions = self.alpaca_api.list_positions()
            
            positions = []
            for alpaca_pos in alpaca_positions:
                position = Position(
                    symbol=alpaca_pos.symbol,
                    quantity=int(alpaca_pos.qty),
                    market_value=float(alpaca_pos.market_value),
                    cost_basis=float(alpaca_pos.cost_basis),
                    unrealized_pl=float(alpaca_pos.unrealized_pl),
                    unrealized_pl_percent=float(alpaca_pos.unrealized_plpc) * 100,
                    current_price=float(alpaca_pos.current_price),
                    side=alpaca_pos.side,
                    avg_entry_price=float(alpaca_pos.avg_entry_price),
                    timestamp=datetime.now()
                )
                
                positions.append(position)
                self.positions_cache[position.symbol] = position
            
            self.cache_timestamp = datetime.now()
            
            self.logger.info(f"Retrieved {len(positions)} current positions")
            return positions
            
        except Exception as e:
            self.logger.error(f"Error getting current positions: {e}")
            return []
    
    async def get_portfolio_summary(self) -> Optional[PortfolioSummary]:
        """Get portfolio summary metrics"""
        try:
            if not self.alpaca_api:
                return None
            
            # Get account information
            account = self.alpaca_api.get_account()
            
            # Get portfolio history for daily P&L
            portfolio_history = self.alpaca_api.get_portfolio_history(
                period='1D',
                timeframe='1Min'
            )
            
            # Calculate daily P&L
            day_pl = 0.0
            day_pl_percent = 0.0
            
            if portfolio_history.equity and len(portfolio_history.equity) > 1:
                current_equity = portfolio_history.equity[-1]
                previous_equity = portfolio_history.equity[0]
                
                if previous_equity and previous_equity > 0:
                    day_pl = current_equity - previous_equity
                    day_pl_percent = (day_pl / previous_equity) * 100
            
            # Get current positions for counting
            positions = await self.get_current_positions()
            
            summary = PortfolioSummary(
                total_equity=float(account.equity),
                buying_power=float(account.buying_power),
                cash_balance=float(account.cash),
                portfolio_value=float(account.portfolio_value),
                total_pl=float(account.equity) - float(account.cash),
                total_pl_percent=((float(account.equity) - float(account.cash)) / float(account.cash)) * 100 if float(account.cash) > 0 else 0,
                day_pl=day_pl,
                day_pl_percent=day_pl_percent,
                position_count=len(positions),
                long_market_value=float(account.long_market_value),
                short_market_value=float(account.short_market_value),
                timestamp=datetime.now()
            )
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return None
    
    async def get_position_by_symbol(self, symbol: str) -> Optional[Position]:
        """Get specific position by symbol"""
        try:
            positions = await self.get_current_positions()
            
            for position in positions:
                if position.symbol.upper() == symbol.upper():
                    return position
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting position for {symbol}: {e}")
            return None
    
    async def analyze_positions(self, target_allocations: Dict[str, float] = None) -> List[PositionAnalysis]:
        """Analyze current positions and provide recommendations"""
        try:
            positions = await self.get_current_positions()
            portfolio_summary = await self.get_portfolio_summary()
            
            if not portfolio_summary:
                return []
            
            analyses = []
            total_portfolio_value = portfolio_summary.portfolio_value
            
            for position in positions:
                current_allocation = (position.market_value / total_portfolio_value) * 100 if total_portfolio_value > 0 else 0
                
                # Get target allocation (default to current if not specified)
                target_allocation = 0
                if target_allocations and position.symbol in target_allocations:
                    target_allocation = target_allocations[position.symbol]
                else:
                    target_allocation = current_allocation
                
                allocation_delta = current_allocation - target_allocation
                
                # Calculate risk score (based on position size and volatility)
                risk_score = min(100, current_allocation * 2)  # Simple risk score
                
                # Calculate performance score
                performance_score = 50 + (position.unrealized_pl_percent * 2)  # Simple performance score
                performance_score = max(0, min(100, performance_score))
                
                # Generate recommendation
                recommendation = "HOLD"
                rationale = "Position within target allocation"
                
                if allocation_delta > 5:  # Over-allocated by more than 5%
                    recommendation = "REDUCE"
                    rationale = f"Over-allocated by {allocation_delta:.1f}%"
                elif allocation_delta < -5:  # Under-allocated by more than 5%
                    recommendation = "BUY"
                    rationale = f"Under-allocated by {abs(allocation_delta):.1f}%"
                elif position.unrealized_pl_percent < -15:  # Down more than 15%
                    recommendation = "SELL"
                    rationale = f"Significant loss: {position.unrealized_pl_percent:.1f}%"
                elif position.unrealized_pl_percent > 30:  # Up more than 30%
                    recommendation = "REDUCE"
                    rationale = f"Take profits: {position.unrealized_pl_percent:.1f}% gain"
                
                analysis = PositionAnalysis(
                    symbol=position.symbol,
                    current_allocation=current_allocation,
                    target_allocation=target_allocation,
                    recommendation=recommendation,
                    allocation_delta=allocation_delta,
                    risk_score=risk_score,
                    performance_score=performance_score,
                    rationale=rationale
                )
                
                analyses.append(analysis)
            
            return analyses
            
        except Exception as e:
            self.logger.error(f"Error analyzing positions: {e}")
            return []
    
    async def get_position_performance(self, days: int = 30) -> Dict[str, Dict[str, float]]:
        """Get position performance over specified period"""
        try:
            positions = await self.get_current_positions()
            performance_data = {}
            
            for position in positions:
                # Get historical data
                historical_data = await self.market_data_provider.get_historical_data(
                    position.symbol,
                    period=f"{days}d"
                )
                
                if not historical_data:
                    continue
                
                # Calculate performance metrics
                prices = [d.close for d in historical_data]
                
                if len(prices) > 1:
                    # Calculate various performance metrics
                    returns = pd.Series(prices).pct_change().dropna()
                    
                    performance_data[position.symbol] = {
                        'total_return': ((prices[-1] - prices[0]) / prices[0]) * 100,
                        'volatility': returns.std() * np.sqrt(252) * 100,  # Annualized
                        'max_drawdown': self._calculate_max_drawdown(prices),
                        'sharpe_ratio': self._calculate_sharpe_ratio(returns),
                        'current_price': position.current_price,
                        'unrealized_pl': position.unrealized_pl,
                        'unrealized_pl_percent': position.unrealized_pl_percent
                    }
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Error getting position performance: {e}")
            return {}
    
    def _calculate_max_drawdown(self, prices: List[float]) -> float:
        """Calculate maximum drawdown"""
        try:
            peak = prices[0]
            max_dd = 0
            
            for price in prices:
                if price > peak:
                    peak = price
                
                drawdown = (peak - price) / peak
                if drawdown > max_dd:
                    max_dd = drawdown
            
            return max_dd * 100
            
        except:
            return 0.0
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        try:
            if len(returns) == 0 or returns.std() == 0:
                return 0.0
            
            excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
            return (excess_returns.mean() / returns.std()) * np.sqrt(252)
            
        except:
            return 0.0
    
    async def check_position_limits(self) -> Dict[str, Any]:
        """Check if positions violate risk limits"""
        try:
            positions = await self.get_current_positions()
            portfolio_summary = await self.get_portfolio_summary()
            
            if not portfolio_summary:
                return {}
            
            violations = []
            total_exposure = 0
            
            for position in positions:
                allocation = (position.market_value / portfolio_summary.portfolio_value) * 100
                total_exposure += allocation
                
                # Check individual position limits
                if allocation > self.config.risk_controls.max_single_position_percent * 100:
                    violations.append({
                        'type': 'position_size',
                        'symbol': position.symbol,
                        'current': allocation,
                        'limit': self.config.risk_controls.max_single_position_percent * 100,
                        'severity': 'HIGH'
                    })
            
            # Check total exposure
            if total_exposure > self.config.risk_controls.max_daily_exposure * 100:
                violations.append({
                    'type': 'total_exposure',
                    'current': total_exposure,
                    'limit': self.config.risk_controls.max_daily_exposure * 100,
                    'severity': 'HIGH'
                })
            
            # Check position count
            if len(positions) > self.config.risk_controls.max_positions:
                violations.append({
                    'type': 'position_count',
                    'current': len(positions),
                    'limit': self.config.risk_controls.max_positions,
                    'severity': 'MEDIUM'
                })
            
            return {
                'violations': violations,
                'total_exposure': total_exposure,
                'position_count': len(positions),
                'within_limits': len(violations) == 0
            }
            
        except Exception as e:
            self.logger.error(f"Error checking position limits: {e}")
            return {}
    
    async def get_portfolio_metrics(self) -> Dict[str, Any]:
        """Get comprehensive portfolio metrics"""
        try:
            positions = await self.get_current_positions()
            portfolio_summary = await self.get_portfolio_summary()
            position_analyses = await self.analyze_positions()
            
            if not portfolio_summary:
                return {}
            
            # Calculate additional metrics
            winning_positions = len([p for p in positions if p.unrealized_pl > 0])
            losing_positions = len([p for p in positions if p.unrealized_pl < 0])
            
            # Best and worst performers
            best_performer = max(positions, key=lambda x: x.unrealized_pl_percent) if positions else None
            worst_performer = min(positions, key=lambda x: x.unrealized_pl_percent) if positions else None
            
            # Average allocation
            avg_allocation = 100 / len(positions) if positions else 0
            
            metrics = {
                'portfolio_summary': asdict(portfolio_summary),
                'position_count': len(positions),
                'winning_positions': winning_positions,
                'losing_positions': losing_positions,
                'win_rate': (winning_positions / len(positions)) * 100 if positions else 0,
                'best_performer': {
                    'symbol': best_performer.symbol,
                    'return': best_performer.unrealized_pl_percent
                } if best_performer else None,
                'worst_performer': {
                    'symbol': worst_performer.symbol,
                    'return': worst_performer.unrealized_pl_percent
                } if worst_performer else None,
                'average_allocation': avg_allocation,
                'total_unrealized_pl': sum(p.unrealized_pl for p in positions),
                'positions': [asdict(p) for p in positions],
                'analyses': [asdict(a) for a in position_analyses],
                'timestamp': datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio metrics: {e}")
            return {}

# Global position manager
_position_manager = None

def get_position_manager() -> PositionManager:
    """Get global position manager instance"""
    global _position_manager
    if _position_manager is None:
        _position_manager = PositionManager()
    return _position_manager