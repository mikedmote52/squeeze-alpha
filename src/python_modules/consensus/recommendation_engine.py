"""
Recommendation Engine
Final stock recommendations based on consensus
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..utils.config import get_config

@dataclass
class StockRecommendation:
    """Final stock recommendation"""
    ticker: str
    action: str  # BUY, SELL, HOLD
    confidence: float
    position_size: float
    entry_strategy: str
    exit_strategy: str
    risk_level: str
    rationale: str
    timestamp: datetime

class RecommendationEngine:
    """Generates final stock recommendations"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
    
    async def generate_recommendations(self, consensus_data: Dict[str, Any]) -> List[StockRecommendation]:
        """Generate final stock recommendations"""
        try:
            recommendations = []
            
            # Extract recommendations from consensus
            raw_recommendations = consensus_data.get('recommendations', [])
            
            for rec in raw_recommendations:
                if isinstance(rec, dict):
                    recommendation = StockRecommendation(
                        ticker=rec.get('ticker', ''),
                        action=rec.get('action', 'HOLD'),
                        confidence=rec.get('confidence', 0.5),
                        position_size=rec.get('position_size', 0),
                        entry_strategy=rec.get('entry_strategy', 'Market'),
                        exit_strategy=rec.get('exit_strategy', 'Bracket Order'),
                        risk_level=rec.get('risk_level', 'Medium'),
                        rationale=rec.get('rationale', ''),
                        timestamp=datetime.now()
                    )
                    recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []