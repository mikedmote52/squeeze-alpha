"""
AGGRESSIVE PROFIT-HUNTING AI ANALYZER
Coordinates Claude and ChatGPT for MAXIMUM GAIN opportunities
Optimized for explosive short-term profits and momentum plays
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json

from ..utils.config import get_config
from ..utils.logging_system import get_logger, AISelection
from ..intelligence.ai_models import get_ai_manager
from ..intelligence.market_data import get_market_data_provider
from ..intelligence.social_sentiment import SocialSentimentAnalyzer

@dataclass
class AnalysisStep:
    """Individual analysis step in the multi-agent workflow"""
    step_number: int
    agent: str  # 'claude' or 'chatgpt'
    role: str
    prompt: str
    response: Dict[str, Any]
    timestamp: datetime
    tokens_used: int
    processing_time: float

@dataclass
class ConsensusResult:
    """Result of multi-agent consensus analysis"""
    steps: List[AnalysisStep]
    final_consensus: Dict[str, Any]
    consensus_score: float
    agreement_level: str  # 'HIGH', 'MEDIUM', 'LOW'
    key_disagreements: List[str]
    total_tokens: int
    total_time: float
    timestamp: datetime

class MultiAgentAnalyzer:
    """Multi-agent AI analysis system"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.trading_logger = get_logger()
        
        # Initialize components
        self.ai_manager = get_ai_manager()
        self.market_data_provider = get_market_data_provider()
        self.sentiment_analyzer = SocialSentimentAnalyzer()
        
        # Analysis workflow configuration
        self.workflow_steps = [
            {
                "step": 1,
                "agent": "claude",
                "role": "Initial Analyst",
                "prompt_template": self._get_initial_analysis_prompt()
            },
            {
                "step": 2,
                "agent": "chatgpt",
                "role": "Critic",
                "prompt_template": self._get_critic_prompt()
            },
            {
                "step": 3,
                "agent": "claude",
                "role": "Refiner",
                "prompt_template": self._get_refiner_prompt()
            },
            {
                "step": 4,
                "agent": "chatgpt",
                "role": "Final Consensus Builder",
                "prompt_template": self._get_consensus_prompt()
            }
        ]
    
    def _get_initial_analysis_prompt(self) -> str:
        """Get initial analysis prompt template"""
        return """
        You are an expert investment analyst. Please analyze the following data and provide initial investment recommendations:

        Current Portfolio:
        {current_positions}

        Social Sentiment Analysis:
        {social_sentiment}

        Creative Stock Screening Results:
        {creative_screening}

        Market Data:
        {market_data}

        Based on this data, please provide:
        1. Analysis of current portfolio performance and holdings
        2. Recommendations for existing positions (buy more, hold, sell, sell percentage)
        3. New investment opportunities from the screening results
        4. Risk assessment and market outlook
        5. Specific action items with reasoning

        Focus on creative, unconventional opportunities that could generate exponential returns while avoiding mega-cap stocks like AAPL, TSLA, MSFT, etc.

        Respond in structured JSON format with:
        - portfolio_analysis: detailed analysis of current holdings
        - position_recommendations: specific actions for existing positions
        - new_opportunities: new investment opportunities
        - risk_assessment: risk analysis and mitigation strategies
        - market_outlook: overall market perspective
        - action_items: specific actionable recommendations
        - confidence_score: confidence level (0-1)
        """
    
    def _get_critic_prompt(self) -> str:
        """Get critic prompt template"""
        return """
        Review and critique the following investment recommendations from another AI. Suggest improvements, challenge assumptions, and highlight any risks or missed opportunities.

        Original Analysis:
        {previous_analysis}

        Market Context:
        {market_data}

        Please provide:
        1. Critical analysis of the recommendations
        2. Identification of potential blind spots
        3. Alternative perspectives and interpretations
        4. Risk factors that may have been overlooked
        5. Suggestions for improvement
        6. Counter-arguments to the original thesis

        Respond in structured JSON format with:
        - critique: detailed critique of original analysis
        - blind_spots: potential issues missed
        - alternative_view: different interpretation of data
        - additional_risks: risks not previously considered
        - improvements: suggested enhancements
        - counter_arguments: opposing viewpoints
        - confidence_score: confidence in critique (0-1)
        """
    
    def _get_refiner_prompt(self) -> str:
        """Get refiner prompt template"""
        return """
        Refine your previous recommendations based on the following critique from another AI. Address any challenges, fill gaps, and improve your analysis.

        Original Analysis:
        {original_analysis}

        Critique:
        {critique}

        Market Data:
        {market_data}

        Please provide:
        1. Responses to the critique points
        2. Refined recommendations incorporating feedback
        3. Additional analysis addressing blind spots
        4. Updated risk assessment
        5. Improved action items

        Respond in structured JSON format with:
        - critique_responses: responses to each critique point
        - refined_recommendations: updated recommendations
        - additional_analysis: new insights from critique
        - updated_risk_assessment: revised risk analysis
        - improved_actions: enhanced action items
        - confidence_score: confidence in refined analysis (0-1)
        """
    
    def _get_consensus_prompt(self) -> str:
        """Get consensus building prompt template"""
        return """
        Review the refined recommendations below. Summarize the consensus, highlight the strongest opportunities, and provide a final actionable plan for the portfolio manager.

        Refined Recommendations:
        {refined_recommendations}

        Market Context:
        {market_data}

        Social Sentiment:
        {social_sentiment}

        Please provide:
        1. Consensus summary of all analyses
        2. Strongest investment opportunities identified
        3. Final actionable plan with specific steps
        4. Risk management recommendations
        5. Priority ranking of opportunities
        6. Implementation timeline

        Respond in structured JSON format with:
        - consensus_summary: summary of all analyses
        - top_opportunities: ranked list of best opportunities
        - final_plan: specific actionable plan
        - risk_management: risk mitigation strategies
        - priority_ranking: prioritized action items
        - implementation_timeline: suggested timing
        - consensus_score: overall consensus strength (0-1)
        """
    
    async def run_multi_agent_analysis(self, 
                                     current_positions: Dict[str, Any],
                                     social_sentiment: Dict[str, Any],
                                     creative_screening: Dict[str, Any],
                                     market_data: Dict[str, Any]) -> ConsensusResult:
        """Run the complete multi-agent analysis workflow"""
        try:
            self.logger.info("Starting multi-agent analysis workflow")
            
            steps = []
            total_tokens = 0
            total_time = 0.0
            
            # Prepare data context
            data_context = {
                'current_positions': current_positions,
                'social_sentiment': social_sentiment,
                'creative_screening': creative_screening,
                'market_data': market_data
            }
            
            # Execute each step in sequence
            previous_response = None
            
            for step_config in self.workflow_steps:
                self.logger.info(f"Executing step {step_config['step']}: {step_config['role']}")
                
                start_time = datetime.now()
                
                # Prepare prompt for this step
                prompt = await self._prepare_step_prompt(
                    step_config, 
                    data_context, 
                    previous_response
                )
                
                # Execute AI analysis
                if step_config['agent'] == 'claude':
                    response_content = await self.ai_manager.claude_client.chat_completion(
                        messages=[
                            {"role": "system", "content": "You are a sophisticated investment analyst. Respond with valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3
                    )
                else:  # chatgpt
                    response_content = await self.ai_manager.openai_client.chat_completion(
                        messages=[
                            {"role": "system", "content": "You are an expert investment analyst. Respond with valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3
                    )
                
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                # Parse response
                try:
                    response_data = json.loads(response_content)
                except json.JSONDecodeError:
                    self.logger.error(f"Failed to parse JSON response from step {step_config['step']}")
                    response_data = {"error": "Failed to parse JSON response", "raw_response": response_content}
                
                # Create analysis step
                analysis_step = AnalysisStep(
                    step_number=step_config['step'],
                    agent=step_config['agent'],
                    role=step_config['role'],
                    prompt=prompt,
                    response=response_data,
                    timestamp=end_time,
                    tokens_used=len(response_content.split()) * 1.3,  # Rough estimate
                    processing_time=processing_time
                )
                
                steps.append(analysis_step)
                total_tokens += analysis_step.tokens_used
                total_time += processing_time
                
                # Set previous response for next step
                previous_response = response_data
                
                # Log step completion
                self.logger.info(f"Step {step_config['step']} completed in {processing_time:.2f}s")
            
            # Calculate consensus metrics
            consensus_score = self._calculate_consensus_score(steps)
            agreement_level = self._determine_agreement_level(consensus_score)
            key_disagreements = self._identify_disagreements(steps)
            
            # Create final result
            consensus_result = ConsensusResult(
                steps=steps,
                final_consensus=steps[-1].response if steps else {},
                consensus_score=consensus_score,
                agreement_level=agreement_level,
                key_disagreements=key_disagreements,
                total_tokens=total_tokens,
                total_time=total_time,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Multi-agent analysis completed. Consensus score: {consensus_score:.2f}")
            
            return consensus_result
            
        except Exception as e:
            self.logger.error(f"Error in multi-agent analysis: {e}")
            raise
    
    async def _prepare_step_prompt(self, 
                                  step_config: Dict[str, Any],
                                  data_context: Dict[str, Any],
                                  previous_response: Optional[Dict[str, Any]]) -> str:
        """Prepare prompt for a specific analysis step"""
        try:
            template = step_config['prompt_template']
            
            # Base context
            prompt_data = {
                'current_positions': json.dumps(data_context['current_positions'], indent=2),
                'social_sentiment': json.dumps(data_context['social_sentiment'], indent=2),
                'creative_screening': json.dumps(data_context['creative_screening'], indent=2),
                'market_data': json.dumps(data_context['market_data'], indent=2)
            }
            
            # Add step-specific context
            if step_config['step'] == 2:  # Critic
                prompt_data['previous_analysis'] = json.dumps(previous_response, indent=2) if previous_response else "{}"
            
            elif step_config['step'] == 3:  # Refiner
                # Get original analysis (step 1) and critique (step 2)
                original_analysis = data_context.get('step1_response', {})
                critique = previous_response or {}
                prompt_data['original_analysis'] = json.dumps(original_analysis, indent=2)
                prompt_data['critique'] = json.dumps(critique, indent=2)
            
            elif step_config['step'] == 4:  # Consensus Builder
                prompt_data['refined_recommendations'] = json.dumps(previous_response, indent=2) if previous_response else "{}"
            
            # Format template
            return template.format(**prompt_data)
            
        except Exception as e:
            self.logger.error(f"Error preparing prompt for step {step_config['step']}: {e}")
            return step_config['prompt_template']
    
    def _calculate_consensus_score(self, steps: List[AnalysisStep]) -> float:
        """Calculate consensus score based on analysis steps"""
        try:
            if len(steps) < 2:
                return 0.5
            
            # Extract confidence scores from each step
            confidence_scores = []
            for step in steps:
                if 'confidence_score' in step.response:
                    confidence_scores.append(step.response['confidence_score'])
            
            if not confidence_scores:
                return 0.5
            
            # Calculate average confidence
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            
            # Adjust for number of steps (more steps = more validation)
            step_bonus = min(0.1, len(steps) * 0.02)
            
            # Final score
            consensus_score = min(1.0, avg_confidence + step_bonus)
            
            return consensus_score
            
        except Exception as e:
            self.logger.error(f"Error calculating consensus score: {e}")
            return 0.5
    
    def _determine_agreement_level(self, consensus_score: float) -> str:
        """Determine agreement level based on consensus score"""
        if consensus_score >= 0.8:
            return 'HIGH'
        elif consensus_score >= 0.6:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _identify_disagreements(self, steps: List[AnalysisStep]) -> List[str]:
        """Identify key disagreements between AI agents"""
        try:
            disagreements = []
            
            if len(steps) < 2:
                return disagreements
            
            # Compare step 1 (Claude) vs step 2 (ChatGPT critique)
            if len(steps) >= 2:
                claude_step = steps[0]
                chatgpt_step = steps[1]
                
                # Check for critique points
                if 'critique' in chatgpt_step.response:
                    disagreements.append("ChatGPT challenged initial analysis")
                
                if 'counter_arguments' in chatgpt_step.response:
                    disagreements.append("Counter-arguments identified")
                
                if 'additional_risks' in chatgpt_step.response:
                    risks = chatgpt_step.response['additional_risks']
                    if isinstance(risks, list) and len(risks) > 0:
                        disagreements.append(f"Additional risks identified: {len(risks)}")
            
            # Compare confidence scores
            if len(steps) >= 2:
                confidence_scores = []
                for step in steps:
                    if 'confidence_score' in step.response:
                        confidence_scores.append(step.response['confidence_score'])
                
                if len(confidence_scores) >= 2:
                    confidence_variance = max(confidence_scores) - min(confidence_scores)
                    if confidence_variance > 0.3:
                        disagreements.append(f"High confidence variance: {confidence_variance:.2f}")
            
            return disagreements
            
        except Exception as e:
            self.logger.error(f"Error identifying disagreements: {e}")
            return []
    
    async def generate_ai_selections(self, consensus_result: ConsensusResult) -> List[AISelection]:
        """Generate AI selection records for logging"""
        try:
            selections = []
            
            final_consensus = consensus_result.final_consensus
            
            # Extract recommendations
            recommendations = []
            if 'top_opportunities' in final_consensus:
                recommendations.extend(final_consensus['top_opportunities'])
            if 'final_plan' in final_consensus:
                plan = final_consensus['final_plan']
                if isinstance(plan, dict) and 'recommendations' in plan:
                    recommendations.extend(plan['recommendations'])
            
            # Create AI selection records
            for i, rec in enumerate(recommendations):
                if isinstance(rec, dict):
                    ticker = rec.get('ticker', f'UNKNOWN_{i}')
                    
                    # Calculate consensus ratings
                    claude_steps = [s for s in consensus_result.steps if s.agent == 'claude']
                    chatgpt_steps = [s for s in consensus_result.steps if s.agent == 'chatgpt']
                    
                    claude_rating = 0.0
                    chatgpt_rating = 0.0
                    
                    if claude_steps:
                        claude_scores = [s.response.get('confidence_score', 0.5) for s in claude_steps]
                        claude_rating = sum(claude_scores) / len(claude_scores)
                    
                    if chatgpt_steps:
                        chatgpt_scores = [s.response.get('confidence_score', 0.5) for s in chatgpt_steps]
                        chatgpt_rating = sum(chatgpt_scores) / len(chatgpt_scores)
                    
                    selection = AISelection(
                        timestamp=datetime.now().isoformat(),
                        ticker=ticker,
                        decision=rec.get('action', 'UNKNOWN'),
                        ai_confidence_score=consensus_result.consensus_score,
                        claude_rating=claude_rating,
                        chatgpt_rating=chatgpt_rating,
                        consensus_level=consensus_result.agreement_level,
                        recommended_action=rec.get('action', 'HOLD'),
                        position_size=rec.get('position_size', 0),
                        rationale=rec.get('rationale', 'No rationale provided'),
                        risk_factors=rec.get('risk_factors', 'No risk factors identified'),
                        social_sentiment_score=0.5  # Would be filled from sentiment analysis
                    )
                    
                    selections.append(selection)
            
            return selections
            
        except Exception as e:
            self.logger.error(f"Error generating AI selections: {e}")
            return []
    
    async def log_analysis_results(self, consensus_result: ConsensusResult) -> None:
        """Log analysis results for tracking"""
        try:
            # Generate AI selections
            selections = await self.generate_ai_selections(consensus_result)
            
            # Log each selection
            for selection in selections:
                self.trading_logger.log_ai_selection(selection)
            
            # Log summary
            self.logger.info(f"Logged {len(selections)} AI selections from multi-agent analysis")
            
        except Exception as e:
            self.logger.error(f"Error logging analysis results: {e}")
    
    def get_analysis_summary(self, consensus_result: ConsensusResult) -> Dict[str, Any]:
        """Get summary of analysis results"""
        try:
            return {
                'consensus_score': consensus_result.consensus_score,
                'agreement_level': consensus_result.agreement_level,
                'total_steps': len(consensus_result.steps),
                'total_tokens': consensus_result.total_tokens,
                'total_time': consensus_result.total_time,
                'key_disagreements': consensus_result.key_disagreements,
                'agents_used': list(set(step.agent for step in consensus_result.steps)),
                'timestamp': consensus_result.timestamp.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting analysis summary: {e}")
            return {}

# Global multi-agent analyzer
_multi_agent_analyzer = None

def get_multi_agent_analyzer() -> MultiAgentAnalyzer:
    """Get global multi-agent analyzer instance"""
    global _multi_agent_analyzer
    if _multi_agent_analyzer is None:
        _multi_agent_analyzer = MultiAgentAnalyzer()
    return _multi_agent_analyzer