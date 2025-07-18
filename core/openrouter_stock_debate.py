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
            
            # Generate conversation thesis summary
            conversation_thesis = self.generate_conversation_thesis({
                'claude': claude_analysis,
                'chatgpt': chatgpt_analysis,
                'grok': grok_analysis
            }, final_consensus)
            
            return {
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'analyses': {
                    'claude': claude_analysis,
                    'chatgpt': chatgpt_analysis,
                    'grok': grok_analysis
                },
                'final_consensus': final_consensus,
                'conversation_thesis': conversation_thesis,
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
    
    def generate_conversation_thesis(self, analyses, consensus):
        """Generate brief summary of AI reasoning and debate"""
        
        # Extract key points from each AI
        claude_stance = self.extract_stance(analyses['claude'])
        chatgpt_stance = self.extract_stance(analyses['chatgpt'])
        grok_stance = self.extract_stance(analyses['grok'])
        
        # Identify agreements and disagreements
        stances = [claude_stance, chatgpt_stance, grok_stance]
        agreements = []
        disagreements = []
        
        # Check for consensus
        buy_votes = sum(1 for stance in stances if 'BUY' in stance.upper())
        sell_votes = sum(1 for stance in stances if 'SELL' in stance.upper())
        hold_votes = sum(1 for stance in stances if 'HOLD' in stance.upper())
        
        if buy_votes >= 2:
            agreements.append("Majority favors BUY")
        elif sell_votes >= 2:
            agreements.append("Majority favors SELL") 
        elif hold_votes >= 2:
            agreements.append("Majority favors HOLD")
        else:
            disagreements.append("Split decision - no clear consensus")
        
        # Identify key reasoning themes
        reasoning_themes = []
        all_text = f"{analyses['claude']} {analyses['chatgpt']} {analyses['grok']}".upper()
        
        if 'VOLUME' in all_text:
            reasoning_themes.append("Volume analysis")
        if 'RISK' in all_text:
            reasoning_themes.append("Risk assessment")
        if 'TECHNICAL' in all_text or 'CHART' in all_text:
            reasoning_themes.append("Technical analysis")
        if 'FUNDAMENTAL' in all_text:
            reasoning_themes.append("Fundamental factors")
        if 'MOMENTUM' in all_text:
            reasoning_themes.append("Momentum considerations")
        
        # Generate thesis summary
        thesis = "🧠 AI CONVERSATION THESIS:\n\n"
        
        thesis += f"🔵 Claude: {claude_stance}\n"
        thesis += f"🟢 ChatGPT: {chatgpt_stance}\n"
        thesis += f"🟠 Grok: {grok_stance}\n\n"
        
        if agreements:
            thesis += f"✅ Agreement: {', '.join(agreements)}\n"
        
        if disagreements:
            thesis += f"⚡ Debate Points: {', '.join(disagreements)}\n"
        
        if reasoning_themes:
            thesis += f"🎯 Key Factors: {', '.join(reasoning_themes)}\n"
        
        # Add reasoning quality
        if buy_votes == 3:
            thesis += "\n💪 Strong Consensus: All AIs aligned on BUY"
        elif sell_votes == 3:
            thesis += "\n💪 Strong Consensus: All AIs aligned on SELL"
        elif buy_votes == 2 or sell_votes == 2:
            thesis += "\n📊 Moderate Consensus: 2/3 AIs agree"
        else:
            thesis += "\n🤔 No Clear Consensus: AIs have different views"
        
        return thesis
    
    def extract_stance(self, analysis):
        """Extract main stance from AI analysis"""
        
        analysis_upper = analysis.upper()
        
        if 'BUY' in analysis_upper and 'SELL' not in analysis_upper:
            return "Recommends BUY"
        elif 'SELL' in analysis_upper and 'BUY' not in analysis_upper:
            return "Recommends SELL"
        elif 'HOLD' in analysis_upper:
            return "Recommends HOLD"
        else:
            return "Mixed signals"
    
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

    def get_stock_analysis(self, ticker):
        """Simple stock analysis for refresh functionality"""
        try:
            # Run async debate in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.debate_stock(ticker, 0, 0, 1.0))
            loop.close()
            
            if 'error' in result:
                return f"Error getting analysis for {ticker}: {result['error']}"
            
            return result.get('final_thesis', f"Analysis complete for {ticker}")
            
        except Exception as e:
            return f"Error analyzing {ticker}: {str(e)}"

    def get_simple_validation(self, ticker, prompt):
        """Simple validation for thesis checking"""
        try:
            # Use Claude for simple validation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.call_openrouter_api('claude', prompt))
            loop.close()
            
            if isinstance(result, dict) and 'error' in result:
                return f"UNKNOWN - Error: {result['error']}"
            
            return result or "UNKNOWN - No response"
            
        except Exception as e:
            return f"UNKNOWN - Error: {str(e)}"


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
    print(f"\n{result['conversation_thesis']}")


if __name__ == "__main__":
    asyncio.run(test_openrouter_debate())