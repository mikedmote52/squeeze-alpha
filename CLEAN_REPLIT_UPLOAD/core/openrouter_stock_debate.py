#!/usr/bin/env python3
"""
OpenRouter Stock Debate System
Claude vs ChatGPT vs Grok - Real-time stock analysis debates
"""

import os
import asyncio
import aiohttp
import json
from datetime import datetime

class OpenRouterStockDebate:
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
    
    async def debate_stock(self, ticker, price, change, volume_spike):
        """Run a 3-way AI debate on a stock"""
        
        print(f"🤖 STARTING AI DEBATE: {ticker}")
        print("=" * 50)
        print("🔵 Claude vs 🟢 ChatGPT vs 🟠 Grok")
        print()
        
        if not self.api_key:
            return {
                'error': 'No OpenRouter API key found',
                'recommendation': 'Configure OPENROUTER_API_KEY in Secrets'
            }
        
        market_data = {
            'ticker': ticker,
            'price': price,
            'change': change,
            'volume_spike': volume_spike
        }
        
        try:
            # Get initial analyses
            claude_analysis = await self.get_claude_analysis(market_data)
            chatgpt_analysis = await self.get_chatgpt_analysis(market_data)
            grok_analysis = await self.get_grok_analysis(market_data)
            
            # Get final consensus
            final_consensus = await self.get_final_consensus(ticker, {
                'claude': claude_analysis,
                'chatgpt': chatgpt_analysis,
                'grok': grok_analysis
            })
            
            return {
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'analyses': {
                    'claude': claude_analysis,
                    'chatgpt': chatgpt_analysis,
                    'grok': grok_analysis
                },
                'final_consensus': final_consensus,
                'recommendation': self.extract_recommendation(final_consensus)
            }
            
        except Exception as e:
            return {
                'error': f'Debate failed: {str(e)}',
                'recommendation': 'Check OpenRouter API key and try again'
            }
    
    async def get_claude_analysis(self, market_data):
        """Get Claude's analysis"""
        
        prompt = f"""As Claude, analyze {market_data['ticker']} stock:

MARKET DATA:
- Current Price: ${market_data['price']:.2f}
- Price Change: {market_data['change']:+.1f}%
- Volume Spike: {market_data['volume_spike']:.1f}x normal

Provide concise analysis:
1. Technical assessment
2. Risk factors
3. BUY/SELL/HOLD recommendation with confidence %

Keep response under 150 words."""
        
        return await self.call_openrouter_api('claude', prompt)
    
    async def get_chatgpt_analysis(self, market_data):
        """Get ChatGPT's analysis"""
        
        prompt = f"""As ChatGPT, analyze {market_data['ticker']} stock:

MARKET DATA:
- Current Price: ${market_data['price']:.2f}
- Price Change: {market_data['change']:+.1f}%
- Volume Spike: {market_data['volume_spike']:.1f}x normal

Provide concise analysis:
1. Market context and fundamentals
2. Trading opportunity assessment
3. BUY/SELL/HOLD recommendation with confidence %

Keep response under 150 words."""
        
        return await self.call_openrouter_api('chatgpt', prompt)
    
    async def get_grok_analysis(self, market_data):
        """Get Grok's analysis"""
        
        prompt = f"""As Grok, analyze {market_data['ticker']} stock with wit and insight:

MARKET DATA:
- Current Price: ${market_data['price']:.2f}
- Price Change: {market_data['change']:+.1f}%
- Volume Spike: {market_data['volume_spike']:.1f}x normal

Provide analysis with your unique perspective:
1. Mathematical verification and contrarian view
2. What others might be missing
3. BUY/SELL/HOLD recommendation with confidence %

Keep response under 150 words, use humor where appropriate."""
        
        return await self.call_openrouter_api('grok', prompt)
    
    async def get_final_consensus(self, ticker, all_analyses):
        """Get final consensus from all analyses"""
        
        prompt = f"""Based on these 3 AI analyses of {ticker}:

CLAUDE'S VIEW: {all_analyses['claude']}

CHATGPT'S VIEW: {all_analyses['chatgpt']}

GROK'S VIEW: {all_analyses['grok']}

Provide FINAL CONSENSUS:
1. Synthesize the best insights
2. Identify strongest arguments
3. Give clear BUY/SELL/HOLD recommendation
4. Include confidence score (0-100%)
5. Suggest position sizing

Keep under 200 words. Be decisive."""
        
        return await self.call_openrouter_api('claude', prompt)
    
    async def call_openrouter_api(self, model_key, prompt):
        """Call OpenRouter API with specified model"""
        
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
            "max_tokens": 300,
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
                        return f"❌ API Error ({response.status}): Check OpenRouter key"
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def extract_recommendation(self, consensus):
        """Extract structured recommendation from consensus"""
        
        # Simple keyword extraction
        recommendation = "HOLD"
        confidence = 50
        
        consensus_upper = consensus.upper()
        
        if "BUY" in consensus_upper or "BULLISH" in consensus_upper:
            recommendation = "BUY"
            confidence = 75
        elif "SELL" in consensus_upper or "BEARISH" in consensus_upper:
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
async def test_openrouter_debate():
    """Test the OpenRouter debate system"""
    
    debate = OpenRouterStockDebate()
    
    # Test with AMC data
    result = await debate.debate_stock('AMC', 3.33, 11.0, 3.0)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print("🎯 AI DEBATE RESULTS:")
    print(f"Ticker: {result['ticker']}")
    print(f"Final Recommendation: {result['recommendation']['action']} ({result['recommendation']['confidence']}%)")
    print(f"Summary: {result['recommendation']['summary']}")


if __name__ == "__main__":
    asyncio.run(test_openrouter_debate())