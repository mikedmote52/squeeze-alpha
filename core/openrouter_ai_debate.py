#!/usr/bin/env python3
"""
OpenRouter AI Debate System
Claude vs ChatGPT vs Grok - Real-time stock analysis debates
"""

import os
import asyncio
import aiohttp
import json
from typing import Dict, List, Any
from datetime import datetime

class OpenRouterAIDebate:
    """Multi-AI debate system using OpenRouter API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Available models through OpenRouter
        self.models = {
            'claude': 'anthropic/claude-3-sonnet',
            'chatgpt': 'openai/gpt-4',
            'grok': 'x-ai/grok-beta'
        }
    
    async def debate_stock_analysis(self, ticker: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a 3-way AI debate on a stock"""
        
        print(f"🤖 STARTING AI DEBATE: {ticker}")
        print("=" * 50)
        print("🔵 Claude vs 🟢 ChatGPT vs 🟠 Grok")
        print()
        
        # Round 1: Initial Analysis
        claude_analysis = await self.get_claude_analysis(ticker, market_data)
        chatgpt_analysis = await self.get_chatgpt_analysis(ticker, market_data)
        grok_analysis = await self.get_grok_analysis(ticker, market_data)
        
        # Round 2: Counter-Arguments
        claude_counter = await self.get_claude_counter(ticker, chatgpt_analysis, grok_analysis)
        chatgpt_counter = await self.get_chatgpt_counter(ticker, claude_analysis, grok_analysis)
        grok_counter = await self.get_grok_counter(ticker, claude_analysis, chatgpt_analysis)
        
        # Round 3: Final Consensus
        final_consensus = await self.get_final_consensus(ticker, {
            'claude': [claude_analysis, claude_counter],
            'chatgpt': [chatgpt_analysis, chatgpt_counter],
            'grok': [grok_analysis, grok_counter]
        })
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'round_1': {
                'claude': claude_analysis,
                'chatgpt': chatgpt_analysis,
                'grok': grok_analysis
            },
            'round_2': {
                'claude_counter': claude_counter,
                'chatgpt_counter': chatgpt_counter,
                'grok_counter': grok_counter
            },
            'final_consensus': final_consensus,
            'recommendation': self.extract_recommendation(final_consensus)
        }
    
    async def get_claude_analysis(self, ticker: str, market_data: Dict[str, Any]) -> str:
        """Get Claude's initial analysis"""
        
        prompt = f"""As Claude (Anthropic AI), analyze {ticker} stock:

MARKET DATA:
- Current Price: ${market_data.get('current_price', 'N/A')}
- Volume Spike: {market_data.get('volume_spike', 'N/A')}x
- Price Change: {market_data.get('price_change', 'N/A')}%
- Market Cap: ${market_data.get('market_cap', 'N/A'):,.0f}

Provide your analysis focusing on:
1. Technical patterns and momentum
2. Risk assessment and volatility
3. Your recommendation (BUY/SELL/HOLD) with confidence level

Be thorough but concise. This will be debated by ChatGPT and Grok."""
        
        return await self.call_openrouter_api('claude', prompt)
    
    async def get_chatgpt_analysis(self, ticker: str, market_data: Dict[str, Any]) -> str:
        """Get ChatGPT's initial analysis"""
        
        prompt = f"""As ChatGPT (OpenAI), analyze {ticker} stock:

MARKET DATA:
- Current Price: ${market_data.get('current_price', 'N/A')}
- Volume Spike: {market_data.get('volume_spike', 'N/A')}x
- Price Change: {market_data.get('price_change', 'N/A')}%
- Market Cap: ${market_data.get('market_cap', 'N/A'):,.0f}

Provide your analysis focusing on:
1. Fundamental analysis and market context
2. Trading opportunities and timing
3. Your recommendation (BUY/SELL/HOLD) with confidence level

Be analytical and data-driven. This will be debated by Claude and Grok."""
        
        return await self.call_openrouter_api('chatgpt', prompt)
    
    async def get_grok_analysis(self, ticker: str, market_data: Dict[str, Any]) -> str:
        """Get Grok's initial analysis"""
        
        prompt = f"""As Grok (xAI), analyze {ticker} stock with your signature wit and insight:

MARKET DATA:
- Current Price: ${market_data.get('current_price', 'N/A')}
- Volume Spike: {market_data.get('volume_spike', 'N/A')}x
- Price Change: {market_data.get('price_change', 'N/A')}%
- Market Cap: ${market_data.get('market_cap', 'N/A'):,.0f}

Provide your analysis with:
1. Mathematical verification of claims
2. Contrarian perspective if warranted
3. Your recommendation (BUY/SELL/HOLD) with confidence level

Use your unique perspective to challenge conventional wisdom. This will be debated by Claude and ChatGPT."""
        
        return await self.call_openrouter_api('grok', prompt)
    
    async def get_claude_counter(self, ticker: str, chatgpt_view: str, grok_view: str) -> str:
        """Get Claude's counter-argument"""
        
        prompt = f"""As Claude, respond to these analyses of {ticker}:

CHATGPT'S VIEW:
{chatgpt_view}

GROK'S VIEW:
{grok_view}

Provide your counter-arguments:
1. Where do you agree/disagree with their analyses?
2. What critical factors did they miss?
3. Refine or defend your original recommendation

Be diplomatic but firm in your analysis."""
        
        return await self.call_openrouter_api('claude', prompt)
    
    async def get_chatgpt_counter(self, ticker: str, claude_view: str, grok_view: str) -> str:
        """Get ChatGPT's counter-argument"""
        
        prompt = f"""As ChatGPT, respond to these analyses of {ticker}:

CLAUDE'S VIEW:
{claude_view}

GROK'S VIEW:
{grok_view}

Provide your counter-arguments:
1. Where do you agree/disagree with their analyses?
2. What market dynamics did they overlook?
3. Refine or defend your original recommendation

Be analytical and evidence-based in your response."""
        
        return await self.call_openrouter_api('chatgpt', prompt)
    
    async def get_grok_counter(self, ticker: str, claude_view: str, chatgpt_view: str) -> str:
        """Get Grok's counter-argument"""
        
        prompt = f"""As Grok, respond to these analyses of {ticker}:

CLAUDE'S VIEW:
{claude_view}

CHATGPT'S VIEW:
{chatgpt_view}

Provide your counter-arguments with wit:
1. Check their math and logic for errors
2. What obvious things did they miss?
3. Refine or defend your original recommendation

Use humor where appropriate but maintain analytical rigor."""
        
        return await self.call_openrouter_api('grok', prompt)
    
    async def get_final_consensus(self, ticker: str, all_debates: Dict[str, List[str]]) -> str:
        """Get final consensus from all three AIs"""
        
        prompt = f"""FINAL CONSENSUS ROUND for {ticker}

Based on this debate between Claude, ChatGPT, and Grok:

CLAUDE'S POSITIONS:
Round 1: {all_debates['claude'][0]}
Round 2: {all_debates['claude'][1]}

CHATGPT'S POSITIONS:
Round 1: {all_debates['chatgpt'][0]}
Round 2: {all_debates['chatgpt'][1]}

GROK'S POSITIONS:
Round 1: {all_debates['grok'][0]}
Round 2: {all_debates['grok'][1]}

Provide a FINAL CONSENSUS that:
1. Synthesizes the best insights from all three
2. Identifies the strongest arguments
3. Gives a clear BUY/SELL/HOLD recommendation
4. Includes a confidence score (0-100%)
5. Suggests position sizing and risk management

This is the final trading decision - be decisive."""
        
        return await self.call_openrouter_api('claude', prompt)  # Use Claude for final synthesis
    
    async def call_openrouter_api(self, model_key: str, prompt: str) -> str:
        """Call OpenRouter API with specified model"""
        
        if not self.api_key:
            return f"❌ No OpenRouter API key - returning mock response for {model_key}"
        
        model = self.models.get(model_key, self.models['claude'])
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-trading-system.replit.app",
            "X-Title": "AI Trading System"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        print(f"❌ OpenRouter API error ({response.status}): {error_text}")
                        return f"❌ API Error: {response.status}"
        
        except Exception as e:
            print(f"❌ Error calling {model_key}: {e}")
            return f"❌ Error: {str(e)}"
    
    def extract_recommendation(self, consensus: str) -> Dict[str, Any]:
        """Extract structured recommendation from consensus"""
        
        # Simple keyword extraction
        recommendation = "HOLD"
        confidence = 50
        
        if "BUY" in consensus.upper() or "BULLISH" in consensus.upper():
            recommendation = "BUY"
            confidence = 75
        elif "SELL" in consensus.upper() or "BEARISH" in consensus.upper():
            recommendation = "SELL"
            confidence = 70
        
        # Try to extract confidence score
        import re
        confidence_match = re.search(r'(\d{1,3})%', consensus)
        if confidence_match:
            confidence = int(confidence_match.group(1))
        
        return {
            'action': recommendation,
            'confidence': confidence,
            'summary': consensus[:200] + "..." if len(consensus) > 200 else consensus
        }


# Test function
async def test_ai_debate():
    """Test the AI debate system"""
    
    debate = OpenRouterAIDebate()
    
    # Mock market data
    market_data = {
        'current_price': 145.67,
        'volume_spike': 3.2,
        'price_change': 12.5,
        'market_cap': 2_500_000_000
    }
    
    result = await debate.debate_stock_analysis('AMC', market_data)
    
    print("🎯 DEBATE RESULTS:")
    print(f"Ticker: {result['ticker']}")
    print(f"Final Recommendation: {result['recommendation']['action']} ({result['recommendation']['confidence']}%)")
    print(f"Summary: {result['recommendation']['summary']}")


if __name__ == "__main__":
    asyncio.run(test_ai_debate())