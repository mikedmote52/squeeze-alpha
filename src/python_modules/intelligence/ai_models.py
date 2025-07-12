"""
AI Models Interface
Handles OpenAI and Claude API interactions
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Import optional dependencies with graceful handling
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

from ..utils.config import get_config

@dataclass
class AIResponse:
    """AI model response data"""
    content: str
    model: str
    tokens_used: int
    response_time: float
    timestamp: datetime
    success: bool
    error: Optional[str] = None

class AIModelInterface(ABC):
    """Abstract base class for AI models"""
    
    @abstractmethod
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion"""
        pass
    
    @abstractmethod
    async def analyze_investment(self, data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Analyze investment data"""
        pass

class OpenAIClient(AIModelInterface):
    """OpenAI API client"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI package not available. Install with: pip install openai")
            self.client = None
            return
            
        try:
            self.client = openai.AsyncOpenAI(
                api_key=self.config.get_api_key('openai')
            )
        except Exception as e:
            self.logger.error(f"Error initializing OpenAI client: {e}")
            self.client = None
    
    async def chat_completion(self, messages: List[Dict[str, str]], 
                            model: str = "gpt-4o", 
                            temperature: float = 0.7,
                            max_tokens: int = 2000,
                            **kwargs) -> str:
        """Generate chat completion"""
        try:
            if not self.client:
                raise Exception("OpenAI client not initialized")
            
            start_time = datetime.now()
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Log response
            ai_response = AIResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                response_time=response_time,
                timestamp=end_time,
                success=True
            )
            
            self.logger.info(f"OpenAI completion successful: {tokens_used} tokens, {response_time:.2f}s")
            
            return content
            
        except Exception as e:
            self.logger.error(f"OpenAI completion error: {e}")
            return f"Error: {str(e)}"
    
    async def analyze_investment(self, data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Analyze investment data using ChatGPT"""
        try:
            system_prompt = """
            You are an expert investment analyst with deep knowledge of financial markets, 
            technical analysis, and risk management. Provide detailed, actionable investment 
            analysis based on the provided data.
            
            Your response should be structured JSON with the following keys:
            - analysis: detailed analysis of the data
            - recommendations: specific investment recommendations
            - risk_assessment: risk factors and mitigation strategies
            - confidence_score: confidence level (0-1)
            - key_factors: list of most important factors
            - suggested_actions: specific actions to take
            """
            
            user_prompt = f"""
            Context: {context}
            
            Data to analyze:
            {json.dumps(data, indent=2)}
            
            Please provide a comprehensive investment analysis focusing on:
            1. Current market conditions and trends
            2. Technical indicators and patterns
            3. Risk/reward assessment
            4. Specific buy/sell/hold recommendations
            5. Position sizing suggestions
            6. Exit strategies
            
            Respond with structured JSON only.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await self.chat_completion(messages, temperature=0.3)
            
            # Parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "analysis": response,
                    "recommendations": [],
                    "risk_assessment": "Unable to parse structured response",
                    "confidence_score": 0.5,
                    "key_factors": [],
                    "suggested_actions": []
                }
                
        except Exception as e:
            self.logger.error(f"Error in investment analysis: {e}")
            return {
                "analysis": f"Error: {str(e)}",
                "recommendations": [],
                "risk_assessment": "Analysis failed",
                "confidence_score": 0.0,
                "key_factors": [],
                "suggested_actions": []
            }
    
    async def counter_analysis(self, original_analysis: Dict[str, Any], 
                             market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide counter-analysis to challenge original recommendations"""
        try:
            system_prompt = """
            You are a contrarian investment analyst whose role is to challenge and critique 
            investment recommendations. Look for flaws, risks, and alternative perspectives 
            that might have been overlooked.
            
            Your response should be structured JSON with the following keys:
            - critique: detailed critique of the original analysis
            - alternative_view: alternative interpretation of the data
            - additional_risks: risks not mentioned in original analysis
            - counter_recommendations: different recommendations
            - confidence_score: confidence in your counter-analysis (0-1)
            - key_concerns: list of primary concerns
            """
            
            user_prompt = f"""
            Original Analysis to Challenge:
            {json.dumps(original_analysis, indent=2)}
            
            Market Data:
            {json.dumps(market_data, indent=2)}
            
            Please provide a thorough counter-analysis that:
            1. Challenges the original recommendations
            2. Identifies potential blind spots
            3. Highlights overlooked risks
            4. Provides alternative interpretations
            5. Suggests different approaches
            6. Questions underlying assumptions
            
            Be thorough and contrarian in your analysis.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await self.chat_completion(messages, temperature=0.4)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "critique": response,
                    "alternative_view": "Unable to parse structured response",
                    "additional_risks": [],
                    "counter_recommendations": [],
                    "confidence_score": 0.5,
                    "key_concerns": []
                }
                
        except Exception as e:
            self.logger.error(f"Error in counter-analysis: {e}")
            return {
                "critique": f"Error: {str(e)}",
                "alternative_view": "Analysis failed",
                "additional_risks": [],
                "counter_recommendations": [],
                "confidence_score": 0.0,
                "key_concerns": []
            }

class ClaudeClient(AIModelInterface):
    """Claude API client"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Claude client
        if not ANTHROPIC_AVAILABLE:
            self.logger.warning("Anthropic package not available. Install with: pip install anthropic")
            self.client = None
            return
            
        try:
            self.client = anthropic.AsyncAnthropic(
                api_key=self.config.get_api_key('anthropic')
            )
        except Exception as e:
            self.logger.error(f"Error initializing Claude client: {e}")
            self.client = None
    
    async def chat_completion(self, messages: List[Dict[str, str]], 
                            model: str = "claude-3-sonnet-20240229",
                            max_tokens: int = 2000,
                            temperature: float = 0.7,
                            **kwargs) -> str:
        """Generate chat completion"""
        try:
            if not self.client:
                raise Exception("Claude client not initialized")
            
            start_time = datetime.now()
            
            # Convert messages to Claude format
            system_message = None
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=user_messages,
                **kwargs
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            # Log response
            ai_response = AIResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                response_time=response_time,
                timestamp=end_time,
                success=True
            )
            
            self.logger.info(f"Claude completion successful: {tokens_used} tokens, {response_time:.2f}s")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Claude completion error: {e}")
            return f"Error: {str(e)}"
    
    async def analyze_investment(self, data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Analyze investment data using Claude"""
        try:
            system_prompt = """
            You are a sophisticated investment analyst with expertise in quantitative analysis, 
            market psychology, and risk management. Your analysis should be thorough, 
            well-reasoned, and actionable.
            
            Provide your analysis in structured JSON format with these keys:
            - analysis: comprehensive analysis
            - recommendations: specific investment recommendations
            - risk_assessment: detailed risk analysis
            - confidence_score: confidence level (0-1)
            - key_factors: most important factors
            - suggested_actions: specific actions to take
            - market_outlook: overall market perspective
            """
            
            user_prompt = f"""
            Investment Analysis Request
            
            Context: {context}
            
            Data to analyze:
            {json.dumps(data, indent=2)}
            
            Please provide a comprehensive investment analysis including:
            1. Technical and fundamental analysis
            2. Market sentiment and positioning
            3. Risk/reward evaluation
            4. Specific investment recommendations
            5. Position sizing and timing
            6. Exit strategy and risk management
            
            Focus on creative, unconventional opportunities that could generate 
            exponential returns while managing downside risk.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await self.chat_completion(messages, temperature=0.3)
            
            # Parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "analysis": response,
                    "recommendations": [],
                    "risk_assessment": "Unable to parse structured response",
                    "confidence_score": 0.5,
                    "key_factors": [],
                    "suggested_actions": [],
                    "market_outlook": "Neutral"
                }
                
        except Exception as e:
            self.logger.error(f"Error in Claude investment analysis: {e}")
            return {
                "analysis": f"Error: {str(e)}",
                "recommendations": [],
                "risk_assessment": "Analysis failed",
                "confidence_score": 0.0,
                "key_factors": [],
                "suggested_actions": [],
                "market_outlook": "Unknown"
            }
    
    async def review_and_consensus(self, chatgpt_analysis: Dict[str, Any], 
                                  market_data: Dict[str, Any],
                                  social_sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Review ChatGPT analysis and build consensus"""
        try:
            system_prompt = """
            You are a senior investment analyst reviewing another AI's analysis. 
            Your role is to critique, refine, and build consensus on investment 
            recommendations.
            
            Provide your consensus in structured JSON format with these keys:
            - review: detailed review of the original analysis
            - consensus_recommendations: refined recommendations
            - risk_assessment: updated risk analysis
            - confidence_score: confidence in consensus (0-1)
            - key_insights: key insights from the analysis
            - final_actions: final recommended actions
            - consensus_level: HIGH/MEDIUM/LOW consensus level
            """
            
            user_prompt = f"""
            Review and Consensus Building
            
            ChatGPT Analysis to Review:
            {json.dumps(chatgpt_analysis, indent=2)}
            
            Market Data:
            {json.dumps(market_data, indent=2)}
            
            Social Sentiment:
            {json.dumps(social_sentiment, indent=2)}
            
            Please review the analysis and provide:
            1. Critique of the original recommendations
            2. Areas of agreement and disagreement
            3. Additional insights from market data
            4. Social sentiment validation
            5. Refined investment recommendations
            6. Consensus-building conclusions
            
            Focus on building a strong consensus that incorporates all available data.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await self.chat_completion(messages, temperature=0.2)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "review": response,
                    "consensus_recommendations": [],
                    "risk_assessment": "Unable to parse structured response",
                    "confidence_score": 0.5,
                    "key_insights": [],
                    "final_actions": [],
                    "consensus_level": "MEDIUM"
                }
                
        except Exception as e:
            self.logger.error(f"Error in Claude review and consensus: {e}")
            return {
                "review": f"Error: {str(e)}",
                "consensus_recommendations": [],
                "risk_assessment": "Analysis failed",
                "confidence_score": 0.0,
                "key_insights": [],
                "final_actions": [],
                "consensus_level": "LOW"
            }

class AIModelManager:
    """Manager for coordinating multiple AI models"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI clients
        self.openai_client = OpenAIClient()
        self.claude_client = ClaudeClient()
        
        # Track usage
        self.usage_stats = {
            "openai": {"requests": 0, "tokens": 0},
            "claude": {"requests": 0, "tokens": 0}
        }
    
    async def get_multi_model_analysis(self, data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Get analysis from multiple AI models"""
        try:
            # Run both analyses in parallel
            chatgpt_task = self.openai_client.analyze_investment(data, context)
            claude_task = self.claude_client.analyze_investment(data, context)
            
            chatgpt_analysis, claude_analysis = await asyncio.gather(
                chatgpt_task, claude_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(chatgpt_analysis, Exception):
                self.logger.error(f"ChatGPT analysis failed: {chatgpt_analysis}")
                chatgpt_analysis = {"error": str(chatgpt_analysis)}
            
            if isinstance(claude_analysis, Exception):
                self.logger.error(f"Claude analysis failed: {claude_analysis}")
                claude_analysis = {"error": str(claude_analysis)}
            
            return {
                "chatgpt_analysis": chatgpt_analysis,
                "claude_analysis": claude_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in multi-model analysis: {e}")
            return {
                "chatgpt_analysis": {"error": str(e)},
                "claude_analysis": {"error": str(e)},
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_consensus_workflow(self, market_data: Dict[str, Any], 
                                   social_sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete AI consensus workflow"""
        try:
            self.logger.info("Starting AI consensus workflow")
            
            # Step 1: Initial ChatGPT analysis
            chatgpt_analysis = await self.openai_client.analyze_investment(
                market_data, "Initial investment analysis"
            )
            
            # Step 2: Claude review and consensus
            claude_consensus = await self.claude_client.review_and_consensus(
                chatgpt_analysis, market_data, social_sentiment
            )
            
            # Step 3: ChatGPT counter-analysis
            chatgpt_counter = await self.openai_client.counter_analysis(
                claude_consensus, market_data
            )
            
            # Step 4: Final Claude refinement
            final_consensus = await self.claude_client.review_and_consensus(
                chatgpt_counter, market_data, social_sentiment
            )
            
            return {
                "step1_chatgpt_initial": chatgpt_analysis,
                "step2_claude_consensus": claude_consensus,
                "step3_chatgpt_counter": chatgpt_counter,
                "step4_final_consensus": final_consensus,
                "workflow_complete": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in consensus workflow: {e}")
            return {
                "error": str(e),
                "workflow_complete": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get AI usage statistics"""
        return self.usage_stats.copy()
    
    def reset_usage_stats(self) -> None:
        """Reset usage statistics"""
        self.usage_stats = {
            "openai": {"requests": 0, "tokens": 0},
            "claude": {"requests": 0, "tokens": 0}
        }

# Global AI model manager
_ai_manager = None

def get_ai_manager() -> AIModelManager:
    """Get global AI model manager"""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIModelManager()
    return _ai_manager