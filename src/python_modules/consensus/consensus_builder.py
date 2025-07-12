"""
Consensus Builder
Builds consensus from multi-agent analysis
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..utils.config import get_config
from .multi_agent_analyzer import ConsensusResult

class ConsensusBuilder:
    """Builds final consensus from AI analysis"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
    
    async def build_final_consensus(self, consensus_result: ConsensusResult) -> Dict[str, Any]:
        """Build final consensus from multi-agent analysis"""
        try:
            final_consensus = consensus_result.final_consensus
            
            # Extract key recommendations
            recommendations = []
            if 'top_opportunities' in final_consensus:
                recommendations = final_consensus['top_opportunities']
            
            # Build consensus summary
            consensus_summary = {
                'consensus_score': consensus_result.consensus_score,
                'agreement_level': consensus_result.agreement_level,
                'recommendations': recommendations,
                'key_insights': final_consensus.get('key_insights', []),
                'risk_assessment': final_consensus.get('risk_assessment', ''),
                'implementation_plan': final_consensus.get('final_plan', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            return consensus_summary
            
        except Exception as e:
            self.logger.error(f"Error building consensus: {e}")
            return {}