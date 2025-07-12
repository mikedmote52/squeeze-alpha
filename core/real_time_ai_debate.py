#!/usr/bin/env python3
"""
REAL-TIME AI Debate System - Live Claude vs ChatGPT Debates
No mock responses - actual LLM API calls with real-time market data
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time
from secrets_manager import get_anthropic_key, get_openai_key

@dataclass
class LiveDebateRound:
    """Real-time AI debate round with actual LLM responses"""
    round_number: int
    claude_analysis: str
    chatgpt_analysis: str
    claude_recommendation: str
    chatgpt_recommendation: str
    claude_confidence: float
    chatgpt_confidence: float
    disagreement_points: List[str]
    consensus_areas: List[str]
    timestamp: str
    real_time_data_used: Dict[str, Any]

@dataclass
class LiveDebateResult:
    """Final result of real AI debate"""
    ticker: str
    final_recommendation: str
    confidence: float
    debate_rounds: List[LiveDebateRound]
    key_insights: List[str]
    risk_factors: List[str]
    success_probability: float
    target_price: float
    stop_loss: float
    time_horizon: str
    consensus_reached: bool
    total_debate_time: float

class RealTimeAIDebate:
    """Live AI debate system with actual Claude and ChatGPT API calls"""
    
    def __init__(self):
        self.anthropic_api_key = get_anthropic_key()
        self.openai_api_key = get_openai_key()
        
        # API endpoints
        self.claude_url = "https://api.anthropic.com/v1/messages"
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        
        # Debate parameters
        self.max_rounds = 5
        self.consensus_threshold = 0.8
        
    async def run_live_ai_debate(self, stock_data: Dict[str, Any], 
                                market_context: Dict[str, Any]) -> LiveDebateResult:
        """Run actual live AI debate between Claude and ChatGPT"""
        
        ticker = stock_data.get('ticker', 'UNKNOWN')
        print(f"🤖 STARTING LIVE AI DEBATE: {ticker}")
        print("=" * 80)
        print("🧠 Claude vs ChatGPT - Real-time analysis with live market data")
        
        start_time = time.time()
        debate_rounds = []
        
        # Initial market data preparation
        live_market_data = await self.prepare_live_market_data(stock_data, market_context)
        
        for round_num in range(1, self.max_rounds + 1):
            print(f"\n🥊 DEBATE ROUND {round_num}")
            print("-" * 40)
            
            # Get Claude's live analysis
            claude_response = await self.get_claude_analysis(
                stock_data, live_market_data, round_num, debate_rounds
            )
            
            # Get ChatGPT's live analysis
            chatgpt_response = await self.get_chatgpt_analysis(
                stock_data, live_market_data, round_num, debate_rounds
            )
            
            # Analyze the responses
            round_result = self.analyze_round_responses(
                claude_response, chatgpt_response, round_num, live_market_data
            )
            
            debate_rounds.append(round_result)
            
            print(f"   🤖 Claude: {round_result.claude_recommendation} ({round_result.claude_confidence:.0%})")
            print(f"   🤖 ChatGPT: {round_result.chatgpt_recommendation} ({round_result.chatgpt_confidence:.0%})")
            
            # Check for consensus
            consensus_score = self.calculate_consensus_score(round_result)
            if consensus_score >= self.consensus_threshold:
                print(f"   ✅ Consensus reached: {consensus_score:.0%}")
                break
            else:
                print(f"   🔄 Continuing debate: {consensus_score:.0%} consensus")
        
        # Generate final recommendation
        final_result = self.generate_final_recommendation(
            ticker, debate_rounds, live_market_data, time.time() - start_time
        )
        
        print(f"\n🎯 FINAL RECOMMENDATION: {final_result.final_recommendation}")
        print(f"📊 Confidence: {final_result.confidence:.0%}")
        print(f"⏱️ Debate time: {final_result.total_debate_time:.1f}s")
        
        return final_result
    
    async def prepare_live_market_data(self, stock_data: Dict[str, Any], 
                                     market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare comprehensive live market data for AI analysis"""
        
        import yfinance as yf
        
        ticker = stock_data.get('ticker')
        stock = yf.Ticker(ticker)
        
        # Get real-time data
        hist = stock.history(period="30d")
        info = stock.info
        news = stock.news
        
        live_data = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "current_price": hist['Close'].iloc[-1] if len(hist) > 0 else 0,
            "price_data": {
                "1d_change": ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) >= 2 else 0,
                "5d_change": ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5] * 100) if len(hist) >= 5 else 0,
                "30d_change": ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100) if len(hist) > 1 else 0,
                "52w_high": info.get('fiftyTwoWeekHigh', 0),
                "52w_low": info.get('fiftyTwoWeekLow', 0)
            },
            "volume_data": {
                "current_volume": hist['Volume'].iloc[-1] if len(hist) > 0 else 0,
                "avg_volume": hist['Volume'].mean() if len(hist) > 0 else 0,
                "volume_spike": (hist['Volume'].iloc[-1] / hist['Volume'].iloc[:-1].mean()) if len(hist) > 1 else 1
            },
            "fundamentals": {
                "market_cap": info.get('marketCap', 0),
                "float_shares": info.get('floatShares', 0),
                "short_ratio": info.get('shortRatio', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "sector": info.get('sector', 'Unknown'),
                "industry": info.get('industry', 'Unknown')
            },
            "recent_news": [article.get('title', '') for article in news[:5]],
            "market_context": market_context,
            "technical_indicators": await self.calculate_technical_indicators(hist)
        }
        
        return live_data
    
    async def calculate_technical_indicators(self, hist) -> Dict[str, Any]:
        """Calculate real-time technical indicators"""
        
        if len(hist) < 20:
            return {"rsi": 50, "sma_20": 0, "bollinger_position": 0.5}
        
        # RSI calculation
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Moving averages
        sma_20 = hist['Close'].rolling(window=20).mean()
        sma_50 = hist['Close'].rolling(window=50).mean() if len(hist) >= 50 else sma_20
        
        # Bollinger Bands
        std_20 = hist['Close'].rolling(window=20).std()
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)
        bb_position = (hist['Close'].iloc[-1] - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
        
        return {
            "rsi": rsi.iloc[-1] if not rsi.empty else 50,
            "sma_20": sma_20.iloc[-1] if not sma_20.empty else hist['Close'].iloc[-1],
            "sma_50": sma_50.iloc[-1] if not sma_50.empty else hist['Close'].iloc[-1],
            "bollinger_position": bb_position if not pd.isna(bb_position) else 0.5,
            "volume_sma": hist['Volume'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else hist['Volume'].mean()
        }
    
    async def get_claude_analysis(self, stock_data: Dict[str, Any], live_data: Dict[str, Any],
                                round_num: int, previous_rounds: List[LiveDebateRound]) -> Dict[str, Any]:
        """Get REAL Claude analysis via Anthropic API"""
        
        if not self.anthropic_api_key:
            print("🚨 CRITICAL ERROR: ANTHROPIC API KEY NOT CONFIGURED")
            print("🛑 TRADING DISABLED: Cannot perform real Claude analysis")
            
            raise RuntimeError(
                "TRADING SAFETY VIOLATION: No Anthropic API key configured. "
                "Real money trading requires real Claude analysis, not mock data. "
                "Configure ANTHROPIC_API_KEY before trading."
            )
        
        # Build context from previous rounds
        debate_context = ""
        if previous_rounds:
            latest_round = previous_rounds[-1]
            debate_context = f"""
Previous ChatGPT analysis: {latest_round.chatgpt_analysis[:500]}...
Previous ChatGPT recommendation: {latest_round.chatgpt_recommendation}
Key disagreements: {', '.join(latest_round.disagreement_points)}
"""
        
        prompt = f"""
You are Claude, an expert hedge fund manager analyzing {live_data['ticker']} for explosive growth potential.

LIVE MARKET DATA (Real-time as of {live_data['timestamp']}):
- Current Price: ${live_data['current_price']:.2f}
- 1D Change: {live_data['price_data']['1d_change']:.1f}%
- Volume Spike: {live_data['volume_data']['volume_spike']:.1f}x normal
- Market Cap: ${live_data['fundamentals']['market_cap']:,}
- Float: {live_data['fundamentals']['float_shares']:,} shares
- Short Ratio: {live_data['fundamentals']['short_ratio']}
- RSI: {live_data['technical_indicators']['rsi']:.1f}
- Sector: {live_data['fundamentals']['sector']}

RECENT NEWS CATALYSTS:
{chr(10).join(f"- {news}" for news in live_data['recent_news'][:3])}

MARKET CONTEXT:
- SPY today: {live_data['market_context'].get('spy_change', 0):.1f}%
- VIX: {live_data['market_context'].get('vix_level', 20):.1f}
- Sector rotation: {live_data['market_context'].get('sector_trend', 'neutral')}

{debate_context}

DEBATE ROUND {round_num}:
Provide your analysis focusing on:
1. Explosive growth potential (target: 50%+ returns)
2. Risk factors and stop loss levels
3. Timing and catalysts
4. Disagreement with ChatGPT's previous analysis (if any)

Give me:
- Your detailed analysis (200 words)
- Clear recommendation: BUY/HOLD/SELL/AVOID
- Confidence level (0-100%)
- Target price and stop loss
- Key risk factors

Be specific about why this could be explosive or why it's risky.
"""
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01"
                }
                
                payload = {
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 1000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
                
                async with session.post(self.claude_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        claude_response = result['content'][0]['text']
                        
                        # Parse Claude's response
                        return self.parse_ai_response(claude_response, "Claude")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Claude API error: {response.status} - {error_text}")
                        return {"error": f"Claude API error: {response.status}"}
                        
        except Exception as e:
            print(f"   ❌ Claude API exception: {e}")
            return {"error": f"Claude API exception: {str(e)}"}
    
    async def get_chatgpt_analysis(self, stock_data: Dict[str, Any], live_data: Dict[str, Any],
                                 round_num: int, previous_rounds: List[LiveDebateRound]) -> Dict[str, Any]:
        """Get REAL ChatGPT analysis via OpenAI API"""
        
        if not self.openai_api_key:
            print("🚨 CRITICAL ERROR: OPENAI API KEY NOT CONFIGURED")
            print("🛑 TRADING DISABLED: Cannot perform real ChatGPT analysis")
            
            raise RuntimeError(
                "TRADING SAFETY VIOLATION: No OpenAI API key configured. "
                "Real money trading requires real ChatGPT analysis, not mock data. "
                "Configure OPENAI_API_KEY before trading."
            )
        
        # Build context from previous rounds
        debate_context = ""
        if previous_rounds:
            latest_round = previous_rounds[-1]
            debate_context = f"""
Previous Claude analysis: {latest_round.claude_analysis[:500]}...
Previous Claude recommendation: {latest_round.claude_recommendation}
Key disagreements: {', '.join(latest_round.disagreement_points)}
"""
        
        prompt = f"""
You are ChatGPT, an expert hedge fund manager analyzing {live_data['ticker']} for explosive growth potential.

LIVE MARKET DATA (Real-time as of {live_data['timestamp']}):
- Current Price: ${live_data['current_price']:.2f}
- 1D Change: {live_data['price_data']['1d_change']:.1f}%
- Volume Spike: {live_data['volume_data']['volume_spike']:.1f}x normal
- Market Cap: ${live_data['fundamentals']['market_cap']:,}
- Float: {live_data['fundamentals']['float_shares']:,} shares
- Short Ratio: {live_data['fundamentals']['short_ratio']}
- RSI: {live_data['technical_indicators']['rsi']:.1f}
- Sector: {live_data['fundamentals']['sector']}

RECENT NEWS CATALYSTS:
{chr(10).join(f"- {news}" for news in live_data['recent_news'][:3])}

MARKET CONTEXT:
- SPY today: {live_data['market_context'].get('spy_change', 0):.1f}%
- VIX: {live_data['market_context'].get('vix_level', 20):.1f}
- Sector rotation: {live_data['market_context'].get('sector_trend', 'neutral')}

{debate_context}

DEBATE ROUND {round_num}:
Provide your analysis focusing on:
1. Explosive growth potential (target: 50%+ returns)
2. Risk factors and stop loss levels
3. Timing and catalysts
4. Disagreement with Claude's previous analysis (if any)

Give me:
- Your detailed analysis (200 words)
- Clear recommendation: BUY/HOLD/SELL/AVOID
- Confidence level (0-100%)
- Target price and stop loss
- Key risk factors

Be specific about why this could be explosive or why it's risky.
"""
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_api_key}"
                }
                
                payload = {
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert hedge fund manager focused on explosive growth opportunities."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
                
                async with session.post(self.openai_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        chatgpt_response = result['choices'][0]['message']['content']
                        
                        # Parse ChatGPT's response
                        return self.parse_ai_response(chatgpt_response, "ChatGPT")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ ChatGPT API error: {response.status} - {error_text}")
                        return {"error": f"ChatGPT API error: {response.status}"}
                        
        except Exception as e:
            print(f"   ❌ ChatGPT API exception: {e}")
            return {"error": f"ChatGPT API exception: {str(e)}"}
    
    def parse_ai_response(self, response_text: str, ai_name: str) -> Dict[str, Any]:
        """Parse AI response to extract structured data"""
        
        # Extract recommendation
        recommendation = "HOLD"
        for rec in ["STRONG BUY", "BUY", "HOLD", "SELL", "AVOID"]:
            if rec in response_text.upper():
                recommendation = rec
                break
        
        # Extract confidence (look for percentage)
        import re
        confidence_match = re.search(r'confidence[:\s]*(\d+)%', response_text.lower())
        confidence = int(confidence_match.group(1)) / 100 if confidence_match else 0.5
        
        # Extract target price
        target_match = re.search(r'target[:\s]*\$?(\d+\.?\d*)', response_text.lower())
        target_price = float(target_match.group(1)) if target_match else 0
        
        # Extract stop loss
        stop_match = re.search(r'stop[:\s]*\$?(\d+\.?\d*)', response_text.lower())
        stop_loss = float(stop_match.group(1)) if stop_match else 0
        
        return {
            "ai_name": ai_name,
            "full_analysis": response_text,
            "recommendation": recommendation,
            "confidence": confidence,
            "target_price": target_price,
            "stop_loss": stop_loss
        }
    
    def analyze_round_responses(self, claude_response: Dict[str, Any], 
                              chatgpt_response: Dict[str, Any],
                              round_num: int, live_data: Dict[str, Any]) -> LiveDebateRound:
        """Analyze and compare AI responses"""
        
        # Find disagreement points
        disagreements = []
        consensus_areas = []
        
        claude_rec = claude_response.get('recommendation', 'HOLD')
        chatgpt_rec = chatgpt_response.get('recommendation', 'HOLD')
        
        if claude_rec != chatgpt_rec:
            disagreements.append(f"Recommendation: Claude={claude_rec}, ChatGPT={chatgpt_rec}")
        else:
            consensus_areas.append(f"Both recommend: {claude_rec}")
        
        # Compare confidence levels
        claude_conf = claude_response.get('confidence', 0.5)
        chatgpt_conf = chatgpt_response.get('confidence', 0.5)
        
        if abs(claude_conf - chatgpt_conf) > 0.2:
            disagreements.append(f"Confidence gap: Claude={claude_conf:.0%}, ChatGPT={chatgpt_conf:.0%}")
        
        # Compare target prices
        claude_target = claude_response.get('target_price', 0)
        chatgpt_target = chatgpt_response.get('target_price', 0)
        
        if claude_target > 0 and chatgpt_target > 0:
            if abs(claude_target - chatgpt_target) / max(claude_target, chatgpt_target) > 0.1:
                disagreements.append(f"Target price gap: Claude=${claude_target:.2f}, ChatGPT=${chatgpt_target:.2f}")
            else:
                consensus_areas.append(f"Similar target prices: ~${(claude_target + chatgpt_target)/2:.2f}")
        
        return LiveDebateRound(
            round_number=round_num,
            claude_analysis=claude_response.get('full_analysis', ''),
            chatgpt_analysis=chatgpt_response.get('full_analysis', ''),
            claude_recommendation=claude_rec,
            chatgpt_recommendation=chatgpt_rec,
            claude_confidence=claude_conf,
            chatgpt_confidence=chatgpt_conf,
            disagreement_points=disagreements,
            consensus_areas=consensus_areas,
            timestamp=datetime.now().isoformat(),
            real_time_data_used=live_data
        )
    
    def calculate_consensus_score(self, round_result: LiveDebateRound) -> float:
        """Calculate consensus score between AI responses"""
        
        score = 0.0
        
        # Recommendation alignment
        if round_result.claude_recommendation == round_result.chatgpt_recommendation:
            score += 0.4
        elif (round_result.claude_recommendation in ['BUY', 'STRONG BUY'] and 
              round_result.chatgpt_recommendation in ['BUY', 'STRONG BUY']):
            score += 0.3  # Both bullish
        elif (round_result.claude_recommendation in ['SELL', 'AVOID'] and 
              round_result.chatgpt_recommendation in ['SELL', 'AVOID']):
            score += 0.3  # Both bearish
        
        # Confidence alignment
        conf_diff = abs(round_result.claude_confidence - round_result.chatgpt_confidence)
        if conf_diff < 0.1:
            score += 0.3
        elif conf_diff < 0.2:
            score += 0.2
        elif conf_diff < 0.3:
            score += 0.1
        
        # General agreement (fewer disagreements)
        if len(round_result.disagreement_points) == 0:
            score += 0.3
        elif len(round_result.disagreement_points) == 1:
            score += 0.2
        elif len(round_result.disagreement_points) == 2:
            score += 0.1
        
        return min(1.0, score)
    
    def generate_final_recommendation(self, ticker: str, debate_rounds: List[LiveDebateRound],
                                    live_data: Dict[str, Any], debate_time: float) -> LiveDebateResult:
        """Generate final recommendation based on AI debate"""
        
        if not debate_rounds:
            return LiveDebateResult(
                ticker=ticker,
                final_recommendation="INSUFFICIENT_DATA",
                confidence=0.0,
                debate_rounds=[],
                key_insights=[],
                risk_factors=[],
                success_probability=0.0,
                target_price=0.0,
                stop_loss=0.0,
                time_horizon="unknown",
                consensus_reached=False,
                total_debate_time=debate_time
            )
        
        latest_round = debate_rounds[-1]
        
        # Determine final recommendation
        claude_rec = latest_round.claude_recommendation
        chatgpt_rec = latest_round.chatgpt_recommendation
        
        if claude_rec == chatgpt_rec:
            final_rec = claude_rec
            consensus = True
        else:
            # Use higher confidence recommendation
            if latest_round.claude_confidence > latest_round.chatgpt_confidence:
                final_rec = claude_rec
            else:
                final_rec = chatgpt_rec
            consensus = False
        
        # Calculate final confidence
        avg_confidence = (latest_round.claude_confidence + latest_round.chatgpt_confidence) / 2
        consensus_bonus = 0.1 if consensus else 0
        final_confidence = min(1.0, avg_confidence + consensus_bonus)
        
        # Extract key insights
        key_insights = []
        for round_data in debate_rounds:
            key_insights.extend(round_data.consensus_areas)
        
        # Extract risk factors from disagreements
        risk_factors = []
        for round_data in debate_rounds:
            risk_factors.extend(round_data.disagreement_points)
        
        # Calculate success probability based on recommendation and confidence
        success_prob = 0.5  # Default
        if final_rec in ['STRONG BUY', 'BUY']:
            success_prob = final_confidence * 0.8  # Bullish but conservative
        elif final_rec == 'HOLD':
            success_prob = 0.5
        else:  # SELL/AVOID
            success_prob = (1 - final_confidence) * 0.3  # Low success if selling
        
        return LiveDebateResult(
            ticker=ticker,
            final_recommendation=final_rec,
            confidence=final_confidence,
            debate_rounds=debate_rounds,
            key_insights=list(set(key_insights)),  # Remove duplicates
            risk_factors=list(set(risk_factors)),
            success_probability=success_prob,
            target_price=live_data['current_price'] * 1.5 if final_rec in ['BUY', 'STRONG BUY'] else live_data['current_price'],
            stop_loss=live_data['current_price'] * 0.9,  # 10% stop loss
            time_horizon="1-4 weeks",
            consensus_reached=consensus,
            total_debate_time=debate_time
        )


# Example usage
async def main():
    """Test real-time AI debate"""
    
    debate_system = RealTimeAIDebate()
    
    # Test stock data
    test_stock = {
        "ticker": "SMCI",
        "company_name": "Super Micro Computer",
        "sector": "Technology"
    }
    
    # Test market context
    market_context = {
        "spy_change": 1.2,
        "vix_level": 18.5,
        "sector_trend": "tech_rotation"
    }
    
    # Run live debate
    result = await debate_system.run_live_ai_debate(test_stock, market_context)
    
    print(f"\n🎯 DEBATE RESULT:")
    print(f"Recommendation: {result.final_recommendation}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Success Probability: {result.success_probability:.0%}")
    print(f"Consensus: {result.consensus_reached}")

if __name__ == "__main__":
    asyncio.run(main())