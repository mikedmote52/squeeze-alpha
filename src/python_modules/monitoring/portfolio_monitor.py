"""
Real-time Portfolio Monitoring
Based on portfolio_monitoring_optimization.json
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..utils.config import get_config
from ..utils.logging_system import get_logger
from ..execution.position_manager import get_position_manager
from ..intelligence.market_data import get_market_data_provider

@dataclass
class PortfolioAlert:
    """Portfolio alert"""
    alert_type: str
    severity: str  # 'LOW', 'MEDIUM', 'HIGH'
    message: str
    symbol: Optional[str] = None
    current_value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: datetime = None

class PortfolioMonitor:
    """Real-time portfolio monitoring system"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.trading_logger = get_logger()
        self.position_manager = get_position_manager()
        self.market_data = get_market_data_provider()
        
        self.alerts = []
        self.monitoring_active = False
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start real-time portfolio monitoring"""
        try:
            self.monitoring_active = True
            self.logger.info("Started portfolio monitoring")
            
            while self.monitoring_active:
                await self._check_portfolio_health()
                await asyncio.sleep(interval_seconds)
                
        except Exception as e:
            self.logger.error(f"Portfolio monitoring error: {e}")
    
    def stop_monitoring(self):
        """Stop portfolio monitoring"""
        self.monitoring_active = False
        self.logger.info("Stopped portfolio monitoring")
    
    async def _check_portfolio_health(self):
        """Check portfolio health and generate alerts"""
        try:
            # Get current portfolio data
            positions = await self.position_manager.get_current_positions()
            portfolio_summary = await self.position_manager.get_portfolio_summary()
            
            if not portfolio_summary:
                return
            
            # Check for alerts
            alerts = []
            
            # Check daily P&L
            if portfolio_summary.day_pl_percent < -5:
                alerts.append(PortfolioAlert(
                    alert_type='DAILY_LOSS',
                    severity='HIGH',
                    message=f"Daily P&L down {portfolio_summary.day_pl_percent:.2f}%",
                    current_value=portfolio_summary.day_pl_percent,
                    threshold=-5.0,
                    timestamp=datetime.now()
                ))
            
            # Check individual positions
            for position in positions:
                if position.unrealized_pl_percent < -15:
                    alerts.append(PortfolioAlert(
                        alert_type='POSITION_LOSS',
                        severity='HIGH',
                        message=f"{position.symbol} down {position.unrealized_pl_percent:.2f}%",
                        symbol=position.symbol,
                        current_value=position.unrealized_pl_percent,
                        threshold=-15.0,
                        timestamp=datetime.now()
                    ))
            
            # Store alerts
            self.alerts.extend(alerts)
            
            # Log alerts
            for alert in alerts:
                self.logger.warning(f"Portfolio Alert: {alert.message}")
                
        except Exception as e:
            self.logger.error(f"Error checking portfolio health: {e}")
    
    async def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get portfolio monitoring summary"""
        try:
            portfolio_summary = await self.position_manager.get_portfolio_summary()
            positions = await self.position_manager.get_current_positions()
            
            recent_alerts = [a for a in self.alerts if 
                           (datetime.now() - a.timestamp).total_seconds() < 3600]  # Last hour
            
            return {
                'portfolio_value': portfolio_summary.portfolio_value if portfolio_summary else 0,
                'daily_pnl': portfolio_summary.day_pl if portfolio_summary else 0,
                'daily_pnl_percent': portfolio_summary.day_pl_percent if portfolio_summary else 0,
                'position_count': len(positions),
                'active_alerts': len(recent_alerts),
                'high_severity_alerts': len([a for a in recent_alerts if a.severity == 'HIGH']),
                'monitoring_status': 'ACTIVE' if self.monitoring_active else 'INACTIVE',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring summary: {e}")
            return {}