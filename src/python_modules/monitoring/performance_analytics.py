"""
Performance Analytics and Reporting
Based on analytics_dashboard.json
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..utils.config import get_config
from ..utils.logging_system import get_logger
from ..execution.position_manager import get_position_manager

@dataclass
class PerformanceMetrics:
    """Performance metrics structure"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    calmar_ratio: float

class PerformanceAnalytics:
    """Portfolio performance analytics engine"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.trading_logger = get_logger()
        self.position_manager = get_position_manager()
    
    async def calculate_performance_metrics(self, days: int = 30) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        try:
            # Get historical data
            historical_data = self.trading_logger.get_historical_data(days)
            
            if not historical_data or 'trades' not in historical_data:
                return self._default_metrics()
            
            trades_df = historical_data['trades']
            
            # Calculate returns
            returns = self._calculate_returns(trades_df)
            
            # Calculate metrics
            total_return = self._calculate_total_return(returns)
            annualized_return = self._calculate_annualized_return(total_return, days)
            volatility = self._calculate_volatility(returns)
            sharpe_ratio = self._calculate_sharpe_ratio(returns, volatility)
            max_drawdown = self._calculate_max_drawdown(returns)
            win_rate = self._calculate_win_rate(trades_df)
            avg_win, avg_loss = self._calculate_avg_win_loss(trades_df)
            profit_factor = self._calculate_profit_factor(avg_win, avg_loss, win_rate)
            calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
            
            return PerformanceMetrics(
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                avg_win=avg_win,
                avg_loss=avg_loss,
                profit_factor=profit_factor,
                calmar_ratio=calmar_ratio
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return self._default_metrics()
    
    def _default_metrics(self) -> PerformanceMetrics:
        """Return default metrics when calculation fails"""
        return PerformanceMetrics(
            total_return=0.0,
            annualized_return=0.0,
            volatility=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            avg_win=0.0,
            avg_loss=0.0,
            profit_factor=0.0,
            calmar_ratio=0.0
        )
    
    def _calculate_returns(self, trades_df: pd.DataFrame) -> List[float]:
        """Calculate daily returns from trades"""
        try:
            if trades_df.empty:
                return []
            
            # Simple return calculation (would be more sophisticated in production)
            returns = []
            for _, trade in trades_df.iterrows():
                if 'entry_price' in trade and 'current_price' in trade:
                    ret = (trade['current_price'] - trade['entry_price']) / trade['entry_price']
                    returns.append(ret)
            
            return returns
        except:
            return []
    
    def _calculate_total_return(self, returns: List[float]) -> float:
        """Calculate total return"""
        if not returns:
            return 0.0
        return sum(returns) * 100
    
    def _calculate_annualized_return(self, total_return: float, days: int) -> float:
        """Calculate annualized return"""
        if days <= 0:
            return 0.0
        return (total_return / days) * 365
    
    def _calculate_volatility(self, returns: List[float]) -> float:
        """Calculate volatility"""
        if len(returns) < 2:
            return 0.0
        return np.std(returns) * np.sqrt(252) * 100  # Annualized
    
    def _calculate_sharpe_ratio(self, returns: List[float], volatility: float) -> float:
        """Calculate Sharpe ratio"""
        if volatility == 0 or not returns:
            return 0.0
        avg_return = np.mean(returns) * 252 * 100  # Annualized
        risk_free_rate = 2.0  # 2% risk-free rate
        return (avg_return - risk_free_rate) / volatility
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not returns:
            return 0.0
        
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return abs(np.min(drawdown)) * 100
    
    def _calculate_win_rate(self, trades_df: pd.DataFrame) -> float:
        """Calculate win rate"""
        if trades_df.empty:
            return 0.0
        
        winning_trades = len(trades_df[trades_df.get('pnl', 0) > 0])
        total_trades = len(trades_df)
        
        return (winning_trades / total_trades) * 100 if total_trades > 0 else 0.0
    
    def _calculate_avg_win_loss(self, trades_df: pd.DataFrame) -> tuple:
        """Calculate average win and loss"""
        if trades_df.empty:
            return 0.0, 0.0
        
        winning_trades = trades_df[trades_df.get('pnl', 0) > 0]['pnl']
        losing_trades = trades_df[trades_df.get('pnl', 0) < 0]['pnl']
        
        avg_win = winning_trades.mean() if not winning_trades.empty else 0.0
        avg_loss = abs(losing_trades.mean()) if not losing_trades.empty else 0.0
        
        return avg_win, avg_loss
    
    def _calculate_profit_factor(self, avg_win: float, avg_loss: float, win_rate: float) -> float:
        """Calculate profit factor"""
        if avg_loss == 0:
            return 0.0
        
        gross_profit = avg_win * (win_rate / 100)
        gross_loss = avg_loss * ((100 - win_rate) / 100)
        
        return gross_profit / gross_loss if gross_loss > 0 else 0.0
    
    async def generate_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            metrics = await self.calculate_performance_metrics(days)
            portfolio_summary = await self.position_manager.get_portfolio_summary()
            
            return {
                'performance_metrics': {
                    'total_return': metrics.total_return,
                    'annualized_return': metrics.annualized_return,
                    'volatility': metrics.volatility,
                    'sharpe_ratio': metrics.sharpe_ratio,
                    'max_drawdown': metrics.max_drawdown,
                    'win_rate': metrics.win_rate,
                    'profit_factor': metrics.profit_factor
                },
                'current_portfolio': {
                    'value': portfolio_summary.portfolio_value if portfolio_summary else 0,
                    'daily_pnl': portfolio_summary.day_pl if portfolio_summary else 0,
                    'total_pnl': portfolio_summary.total_pl if portfolio_summary else 0
                },
                'report_period': f"{days} days",
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {}