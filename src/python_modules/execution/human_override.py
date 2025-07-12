"""
Human Override System
Based on human_override_system.json
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..utils.config import get_config
from ..utils.slack_integration import get_slack_bot

@dataclass
class OverrideRequest:
    """Human override request"""
    request_id: str
    recommendations: List[Dict[str, Any]]
    reason: str
    timestamp: datetime
    status: str  # 'PENDING', 'APPROVED', 'REJECTED'

class HumanOverrideSystem:
    """Human override and approval system"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.slack_bot = get_slack_bot()
        self.pending_requests = {}
    
    async def check_override_required(self, recommendations: List[Dict[str, Any]]) -> bool:
        """Check if human override is required"""
        try:
            for rec in recommendations:
                # High risk trades require approval
                if rec.get('risk_level') == 'High':
                    return True
                
                # Large position sizes require approval
                position_size = rec.get('position_size', 0)
                if position_size > 800:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking override requirement: {e}")
            return True  # Default to requiring approval on error
    
    async def request_approval(self, recommendations: List[Dict[str, Any]]) -> str:
        """Request human approval"""
        try:
            request_id = f"override_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            override_request = OverrideRequest(
                request_id=request_id,
                recommendations=recommendations,
                reason="High-risk trades detected",
                timestamp=datetime.now(),
                status='PENDING'
            )
            
            self.pending_requests[request_id] = override_request
            
            # Send Slack alert
            await self.slack_bot.send_high_risk_alert(recommendations)
            
            self.logger.info(f"Override request created: {request_id}")
            return request_id
            
        except Exception as e:
            self.logger.error(f"Error requesting approval: {e}")
            return ""
    
    def approve_request(self, request_id: str) -> bool:
        """Approve override request"""
        if request_id in self.pending_requests:
            self.pending_requests[request_id].status = 'APPROVED'
            return True
        return False
    
    def reject_request(self, request_id: str) -> bool:
        """Reject override request"""
        if request_id in self.pending_requests:
            self.pending_requests[request_id].status = 'REJECTED'
            return True
        return False