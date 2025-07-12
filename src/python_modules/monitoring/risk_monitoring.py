"""
Risk Monitoring and Alerts
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..utils.config import get_config
from ..execution.position_manager import get_position_manager

@dataclass 
class RiskAlert:
    """Risk alert structure"""
    alert_type: str
    severity: str
    message: str
    current_value: float
    threshold: float
    timestamp: datetime

class RiskMonitor:
    """Risk monitoring system"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.position_manager = get_position_manager()
        self.risk_alerts = []
    
    async def check_risk_limits(self) -> List[RiskAlert]:
        """Check all risk limits and generate alerts"""
        try:
            alerts = []
            
            # Check position limits
            limit_check = await self.position_manager.check_position_limits()
            
            for violation in limit_check.get('violations', []):
                alerts.append(RiskAlert(
                    alert_type=violation['type'],
                    severity=violation['severity'],
                    message=f"Risk limit exceeded: {violation['type']}",
                    current_value=violation['current'],
                    threshold=violation['limit'],
                    timestamp=datetime.now()
                ))
            
            self.risk_alerts = alerts
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error checking risk limits: {e}")
            return []
    
    async def get_risk_summary(self) -> Dict[str, Any]:
        """Get risk monitoring summary"""
        try:
            alerts = await self.check_risk_limits()
            
            return {
                'total_alerts': len(alerts),
                'high_severity': len([a for a in alerts if a.severity == 'HIGH']),
                'risk_status': 'HIGH' if any(a.severity == 'HIGH' for a in alerts) else 'NORMAL',
                'alerts': [{'type': a.alert_type, 'message': a.message} for a in alerts],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting risk summary: {e}")
            return {}