"""
Analytics Dashboard
Comprehensive trading system dashboard
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..utils.config import get_config
from .portfolio_monitor import PortfolioMonitor
from .performance_analytics import PerformanceAnalytics
from .risk_monitoring import RiskMonitor
from ..execution.position_manager import get_position_manager

class AnalyticsDashboard:
    """Main analytics dashboard"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.portfolio_monitor = PortfolioMonitor()
        self.performance_analytics = PerformanceAnalytics()
        self.risk_monitor = RiskMonitor()
        self.position_manager = get_position_manager()
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        try:
            # Get all dashboard components
            portfolio_summary = await self.position_manager.get_portfolio_summary()
            positions = await self.position_manager.get_current_positions()
            monitoring_summary = await self.portfolio_monitor.get_monitoring_summary()
            performance_metrics = await self.performance_analytics.calculate_performance_metrics()
            risk_summary = await self.risk_monitor.get_risk_summary()
            
            return {
                'portfolio': {
                    'total_value': portfolio_summary.portfolio_value if portfolio_summary else 0,
                    'daily_pnl': portfolio_summary.day_pl if portfolio_summary else 0,
                    'daily_pnl_percent': portfolio_summary.day_pl_percent if portfolio_summary else 0,
                    'total_pnl': portfolio_summary.total_pl if portfolio_summary else 0,
                    'position_count': len(positions),
                    'buying_power': portfolio_summary.buying_power if portfolio_summary else 0
                },
                'performance': {
                    'total_return': performance_metrics.total_return,
                    'sharpe_ratio': performance_metrics.sharpe_ratio,
                    'max_drawdown': performance_metrics.max_drawdown,
                    'win_rate': performance_metrics.win_rate,
                    'volatility': performance_metrics.volatility
                },
                'risk': {
                    'status': risk_summary.get('risk_status', 'UNKNOWN'),
                    'total_alerts': risk_summary.get('total_alerts', 0),
                    'high_severity_alerts': risk_summary.get('high_severity', 0)
                },
                'monitoring': {
                    'status': monitoring_summary.get('monitoring_status', 'INACTIVE'),
                    'active_alerts': monitoring_summary.get('active_alerts', 0)
                },
                'positions': [
                    {
                        'symbol': p.symbol,
                        'quantity': p.quantity,
                        'market_value': p.market_value,
                        'unrealized_pl': p.unrealized_pl,
                        'unrealized_pl_percent': p.unrealized_pl_percent
                    } for p in positions[:10]  # Top 10 positions
                ],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    async def get_summary_stats(self) -> Dict[str, Any]:
        """Get key summary statistics"""
        try:
            dashboard_data = await self.get_dashboard_data()
            
            return {
                'portfolio_value': dashboard_data['portfolio']['total_value'],
                'daily_pnl': dashboard_data['portfolio']['daily_pnl'],
                'position_count': dashboard_data['portfolio']['position_count'],
                'risk_status': dashboard_data['risk']['status'],
                'win_rate': dashboard_data['performance']['win_rate'],
                'sharpe_ratio': dashboard_data['performance']['sharpe_ratio']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting summary stats: {e}")
            return {}