#!/usr/bin/env python3
"""
CatalystOpportunity Schema
Structured data class for real catalyst events
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class CatalystOpportunity:
    """Real catalyst opportunity with verifiable data"""
    ticker: str
    catalyst_type: str  # 'FDA_APPROVAL', 'SEC_FILING', 'EARNINGS', 'M&A', 'PARTNERSHIP'
    event_date: datetime
    confidence_score: float  # 0.0-1.0 based on data quality
    estimated_upside: Optional[float]  # % potential upside
    estimated_downside: Optional[float]  # % potential downside
    source: str  # 'FDA.gov', 'SEC.gov', 'EDGAR', etc.
    source_url: str  # Direct link to source
    headline: str  # Brief description
    details: Dict[str, Any]  # Additional metadata
    discovered_at: datetime
    
    def __post_init__(self):
        """Validate data after initialization"""
        if not self.ticker or len(self.ticker) > 6:
            raise ValueError(f"Invalid ticker: {self.ticker}")
        
        if self.confidence_score < 0 or self.confidence_score > 1:
            raise ValueError(f"Confidence score must be 0-1: {self.confidence_score}")
        
        if not self.source_url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid source URL: {self.source_url}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'ticker': self.ticker,
            'catalyst_type': self.catalyst_type,
            'event_date': self.event_date.isoformat(),
            'confidence_score': self.confidence_score,
            'estimated_upside': self.estimated_upside,
            'estimated_downside': self.estimated_downside,
            'source': self.source,
            'source_url': self.source_url,
            'headline': self.headline,
            'details': self.details,
            'discovered_at': self.discovered_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CatalystOpportunity':
        """Create from dictionary"""
        return cls(
            ticker=data['ticker'],
            catalyst_type=data['catalyst_type'],
            event_date=datetime.fromisoformat(data['event_date']),
            confidence_score=data['confidence_score'],
            estimated_upside=data.get('estimated_upside'),
            estimated_downside=data.get('estimated_downside'),
            source=data['source'],
            source_url=data['source_url'],
            headline=data['headline'],
            details=data.get('details', {}),
            discovered_at=datetime.fromisoformat(data['discovered_at'])
        )
    
    def is_urgent(self, days_threshold: int = 7) -> bool:
        """Check if catalyst is happening soon"""
        days_until = (self.event_date - datetime.now()).days
        return 0 <= days_until <= days_threshold
    
    def get_risk_reward_ratio(self) -> Optional[float]:
        """Calculate risk/reward ratio if both upside and downside are available"""
        if self.estimated_upside and self.estimated_downside:
            return abs(self.estimated_upside / self.estimated_downside)
        return None