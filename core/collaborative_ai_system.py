#!/usr/bin/env python3
"""
Collaborative AI Trading System
Claude, ChatGPT, and Grok have actual conversations about explosive opportunities
"""

import requests
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os

class CollaborativeAISystem:
    """AI models have structured conversations about explosive trading opportunities"""
    
    def __init__(self):
        self.openrouter_api_key = "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"
        
        # Large-cap stocks to AVOID in all conversations
        self.forbidden_stocks = {
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META',
            'BRK.A', 'BRK.B', 'TSM', 'LLY', 'V', 'UNH', 'JNJ', 'WMT',
            'XOM', 'JPM', 'PG', 'MA', 'HD', 'ORCL', 'COST', 'ABBV'
        }
        
        self.conversation_history = []
    
    async def run_collaborative_analysis(self, symbol: str, context: str = "") -> Dict[str, Any]:
        """Run full collaborative analysis with AI models discussing together"""
        
        print(f"🎯 Starting collaborative AI analysis for {symbol}")
        
        # Step 1: Claude provides catalyst analysis
        claude_analysis = await self.get_claude_catalyst_analysis(symbol, context)
        
        # Step 2: Grok verifies Claude's data
        grok_verification = await self.get_grok_verification(symbol, claude_analysis)
        
        # Step 3: ChatGPT provides technical validation based on Claude + Grok
        chatgpt_technical = await self.get_chatgpt_technical_validation(symbol, claude_analysis, grok_verification)
        
        # Step 4: Final collaborative consensus
        consensus = await self.get_collaborative_consensus(symbol, claude_analysis, grok_verification, chatgpt_technical)
        
        # Compile full conversation
        conversation_result = {
            "symbol": symbol,
            "context": context,
            "conversation_flow": [
                {"step": 1, "agent": "Claude", "role": "Catalyst Intelligence", "analysis": claude_analysis},
                {"step": 2, "agent": "Grok", "role": "Data Verification", "analysis": grok_verification},
                {"step": 3, "agent": "ChatGPT", "role": "Technical Execution", "analysis": chatgpt_technical},
                {"step": 4, "agent": "Team", "role": "Collaborative Consensus", "analysis": consensus}
            ],
            "final_recommendation": consensus,
            "conversation_timestamp": datetime.now().isoformat(),
            "source": "Real Collaborative AI Analysis"
        }
        
        # Store conversation for analysis
        self.conversation_history.append(conversation_result)
        
        return conversation_result
    
    async def get_claude_catalyst_analysis(self, symbol: str, context: str) -> Dict[str, Any]:
        """Claude analyzes for explosive catalyst opportunities"""
        
        prompt = f"""
CLAUDE - CATALYST INTELLIGENCE OFFICER

You are in a collaborative trading discussion with ChatGPT and Grok.

MISSION: Analyze {symbol} for EXPLOSIVE catalyst opportunities only.

FORBIDDEN: Do NOT recommend any large-cap stocks: AAPL, TSLA, NVDA, MSFT, GOOGL, AMZN, META, etc.

FOCUS AREAS:
1. FDA approvals and clinical trial results
2. Earnings surprises for small-cap companies  
3. Acquisition rumors and announcements
4. Regulatory decisions and policy changes
5. Short squeeze potential analysis

FOR {symbol}:

1. CATALYST IDENTIFICATION:
   - What specific catalyst is upcoming?
   - Exact timeline (within 14-30 days)
   - Historical success rate for this type of catalyst

2. EXPLOSIVE POTENTIAL:
   - Expected upside percentage (minimum 20%)
   - Catalyst probability score (1-10, need 7+)
   - Why this could create explosive price movement

3. RISK ASSESSMENT:
   - What if the catalyst fails?
   - Major downside scenarios
   - Risk mitigation strategies

4. RECOMMENDATION TO TEAM:
   - BUY/SELL/AVOID with conviction level
   - Position size (3-15% of portfolio)
   - Entry timing and strategy

Context: {context}

Present your analysis for ChatGPT and Grok to validate. Focus ONLY on explosive opportunities, never large-cap safe plays.
        """
        
        return await self.call_ai_model("anthropic/claude-3-sonnet", "Claude", prompt)
    
    async def get_grok_verification(self, symbol: str, claude_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Grok verifies Claude's catalyst analysis for accuracy"""
        
        claude_reasoning = claude_analysis.get('reasoning', 'No analysis provided')
        
        prompt = f"""
GROK - DATA VERIFICATION & ACCURACY OFFICER

You are reviewing Claude's catalyst analysis in our collaborative trading discussion.

CLAUDE'S ANALYSIS FOR {symbol}:
{claude_reasoning}

YOUR VERIFICATION MISSION:
1. Fact-check all numerical claims and percentages
2. Verify catalyst timeline and probability assertions  
3. Cross-check historical precedent data
4. Validate logical consistency of investment thesis
5. Identify missing risk factors or data gaps

VERIFICATION CHECKLIST:
□ Are catalyst dates/timelines accurate?
□ Are success probability claims supported by data?
□ Are upside projections realistic based on precedents?
□ Are risk factors adequately identified?
□ Is the investment thesis logically sound?

RESPONSE FORMAT:
1. DATA VERIFICATION STATUS: ✅ CONFIRMED / ⚠️ CORRECTIONS NEEDED
2. FACTUAL CORRECTIONS: List any errors found
3. MISSING INFORMATION: What data is needed
4. RISK GAPS: Additional risks not mentioned
5. RECOMMENDATION: APPROVE / REVISE / REJECT Claude's analysis

Be thorough and critical. Only approve high-quality explosive opportunities.
        """
        
        return await self.call_ai_model("x-ai/grok-beta", "Grok", prompt)
    
    async def get_chatgpt_technical_validation(self, symbol: str, claude_analysis: Dict[str, Any], grok_verification: Dict[str, Any]) -> Dict[str, Any]:
        """ChatGPT validates technical execution strategy"""
        
        claude_reasoning = claude_analysis.get('reasoning', '')
        grok_reasoning = grok_verification.get('reasoning', '')
        
        prompt = f"""
CHATGPT - TECHNICAL EXECUTION ANALYST

You are reviewing the catalyst opportunity for {symbol} after Claude and Grok's analysis.

CLAUDE'S CATALYST ANALYSIS:
{claude_reasoning}

GROK'S VERIFICATION:
{grok_reasoning}

YOUR TECHNICAL VALIDATION MISSION:
1. Assess technical setup and chart patterns
2. Analyze volume, momentum, and price action
3. Evaluate short interest and squeeze potential
4. Determine optimal entry/exit strategy
5. Calculate position sizing and risk management

TECHNICAL ANALYSIS FOR {symbol}:
1. CHART SETUP:
   - Current technical pattern
   - Support/resistance levels
   - Volume analysis and trends

2. EXECUTION STRATEGY:
   - Best entry price and timing
   - Stop loss placement for risk control
   - Profit target levels

3. SQUEEZE POTENTIAL:
   - Short interest percentage
   - Float analysis
   - Options activity indicators

4. POSITION MANAGEMENT:
   - Recommended portfolio allocation (3-15%)
   - Risk-adjusted position size
   - Portfolio correlation impact

5. FINAL TECHNICAL VERDICT:
   - EXECUTE / WAIT / AVOID
   - Technical confidence level (1-10)
   - Execution timeline recommendations

Validate only explosive opportunities with strong technical confirmation.
        """
        
        return await self.call_ai_model("openai/gpt-4", "ChatGPT", prompt)
    
    async def get_collaborative_consensus(self, symbol: str, claude_analysis: Dict[str, Any], 
                                       grok_verification: Dict[str, Any], 
                                       chatgpt_technical: Dict[str, Any]) -> Dict[str, Any]:
        """Generate collaborative consensus from all three AI analyses"""
        
        claude_reasoning = claude_analysis.get('reasoning', '')
        grok_reasoning = grok_verification.get('reasoning', '')
        chatgpt_reasoning = chatgpt_technical.get('reasoning', '')
        
        prompt = f"""
COLLABORATIVE AI CONSENSUS for {symbol}

You are synthesizing the complete analysis from our specialized AI team:

CLAUDE (Catalyst Intelligence):
{claude_reasoning}

GROK (Data Verification):
{grok_reasoning}

CHATGPT (Technical Execution):
{chatgpt_reasoning}

GENERATE TEAM CONSENSUS:

1. UNIFIED RECOMMENDATION:
   Ticker: {symbol}
   Catalyst: [Specific catalyst type and event]
   Event Date: [Timeline from Claude, verified by Grok]
   Catalyst Probability: [Score 1-10, verified by team]
   Expected Upside: [Percentage with precedent analysis]
   Technical Confirmation: [Entry/exit levels from ChatGPT]
   Risk Factors: [Comprehensive list from all agents]
   Position Size: [3-15% allocation based on conviction]
   Entry Strategy: [Timing and price levels]
   Exit Plan: [Profit targets and stop losses]

2. DATA VERIFICATION: ✅ CONFIRMED / ⚠️ CORRECTIONS NEEDED

3. TEAM CONSENSUS: APPROVED / NEEDS REVISION / REJECT

4. CONFIDENCE LEVEL: [1-10 based on team agreement]

5. IMPLEMENTATION TIMELINE: [When to execute]

Only approve opportunities with:
- 70%+ catalyst success probability
- 20%+ upside potential  
- Strong technical confirmation
- Verified data accuracy
- Team consensus agreement

CRITICAL: Reject any large-cap recommendations (AAPL, TSLA, NVDA, etc.)
        """
        
        return await self.call_ai_model("anthropic/claude-3-sonnet", "Team Consensus", prompt)
    
    async def call_ai_model(self, model: str, agent_name: str, prompt: str) -> Dict[str, Any]:
        """Call OpenRouter API for AI model response"""
        
        if not self.openrouter_api_key:
            return {
                "agent": agent_name,
                "model": model,
                "reasoning": f"{agent_name} analysis unavailable - OpenRouter API key not configured",
                "confidence": 0.3,
                "timestamp": datetime.now().isoformat(),
                "source": "Fallback"
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {self.openrouter_api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:8000',
                'X-Title': 'AI Trading System'
            }
            
            payload = {
                'model': model,
                'messages': [
                    {
                        'role': 'system', 
                        'content': 'You are a specialized AI agent in a collaborative trading system. Focus only on explosive catalyst opportunities. Avoid large-cap safe stocks.'
                    },
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 800,
                'temperature': 0.3
            }
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Extract confidence level from response
                confidence = 0.7  # Default
                if 'high confidence' in ai_response.lower() or 'approved' in ai_response.lower():
                    confidence = 0.85
                elif 'low confidence' in ai_response.lower() or 'reject' in ai_response.lower():
                    confidence = 0.3
                elif 'needs revision' in ai_response.lower():
                    confidence = 0.5
                
                return {
                    "agent": agent_name,
                    "model": model,
                    "reasoning": ai_response,
                    "confidence": confidence,
                    "timestamp": datetime.now().isoformat(),
                    "source": "OpenRouter API"
                }
            else:
                print(f"OpenRouter API error for {agent_name}: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Error text: {response.text}")
                return {
                    "agent": agent_name,
                    "model": model,
                    "reasoning": f"{agent_name} analysis failed - API error {response.status_code}",
                    "confidence": 0.2,
                    "timestamp": datetime.now().isoformat(),
                    "source": "API Error"
                }
                
        except Exception as e:
            print(f"Error calling {agent_name}: {e}")
            return {
                "agent": agent_name,
                "model": model,
                "reasoning": f"{agent_name} analysis failed - {str(e)}",
                "confidence": 0.2,
                "timestamp": datetime.now().isoformat(),
                "source": "Exception"
            }
    
    def save_conversation_log(self, filename: str = None):
        """Save conversation history to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_collaborative_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "session_timestamp": datetime.now().isoformat(),
                "total_conversations": len(self.conversation_history),
                "conversations": self.conversation_history
            }, f, indent=2)
        
        return filename

async def main():
    """Test collaborative AI system"""
    system = CollaborativeAISystem()
    
    # Test with a sample stock
    test_symbol = "SAVA"  # Small biotech with catalyst potential
    
    result = await system.run_collaborative_analysis(
        test_symbol, 
        "Analyzing for explosive catalyst opportunities"
    )
    
    print("\n🤖 COLLABORATIVE AI ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Symbol: {result['symbol']}")
    print(f"Conversation Steps: {len(result['conversation_flow'])}")
    
    for step in result['conversation_flow']:
        print(f"\nStep {step['step']}: {step['agent']} ({step['role']})")
        print(f"Analysis: {step['analysis']['reasoning'][:200]}...")
    
    # Save conversation log
    log_file = system.save_conversation_log()
    print(f"\n💾 Conversation saved to: {log_file}")

if __name__ == "__main__":
    asyncio.run(main())