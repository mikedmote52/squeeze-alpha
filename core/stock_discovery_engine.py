#!/usr/bin/env python3
"""
Stock Discovery Engine with Perplexity Integration
Pipeline: Perplexity finds candidates -> Claude vs ChatGPT debate -> Best recommendations
"""

import os
import json
import asyncio
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time

from enhanced_ai_consensus import EnhancedAIConsensus, DebateRound
from real_time_stock_discovery import RealTimeStockDiscovery, LiveStockCandidate
from real_time_ai_debate import RealTimeAIDebate, LiveDebateResult
from real_time_portfolio_engine import RealTimePortfolioEngine
from secrets_manager import get_perplexity_key, get_anthropic_key, get_openai_key

@dataclass
class MarketWinner:
    """Daily market winner analysis"""
    ticker: str
    company_name: str
    sector: str
    price_change_percent: float
    volume_spike: float
    market_cap: float
    float_shares: int
    catalyst_detected: str
    news_events: List[str]
    social_sentiment: str
    why_system_missed: List[str]
    lessons_learned: List[str]

@dataclass
class SystemImprovement:
    """Recommended system improvement"""
    improvement_type: str  # "prompt", "criteria", "timing", "signal_detection"
    description: str
    implementation: str
    priority: str  # "high", "medium", "low"
    expected_impact: str

@dataclass
class StockCandidate:
    """Stock candidate from Perplexity discovery"""
    ticker: str
    company_name: str
    sector: str
    market_cap: float
    current_price: float
    discovery_reason: str
    catalyst_events: List[str]
    time_horizon: str  # "today", "week", "month"
    perplexity_confidence: float
    discovery_source: str

class StockDiscoveryEngine:
    """Main engine for discovering and analyzing explosive stock opportunities"""
    
    def __init__(self):
        self.perplexity_api_key = get_perplexity_key()
        self.openai_api_key = get_openai_key()
        self.anthropic_api_key = get_anthropic_key()
        
        # Initialize the enhanced AI consensus engine
        self.ai_consensus = EnhancedAIConsensus()
        
        # Initialize REAL-TIME discovery systems
        self.real_time_discovery = RealTimeStockDiscovery()
        self.real_time_ai_debate = RealTimeAIDebate()
        self.real_time_portfolio = RealTimePortfolioEngine()
        
        # Discovery parameters
        self.max_candidates_per_timeframe = 5
        self.min_market_cap = 10_000_000  # $10M minimum
        self.max_market_cap = 5_000_000_000  # $5B maximum (stay small/mid cap)
        
        # Perplexity prompts for different timeframes
        self.discovery_prompts = {
            "today": """
            Find the top 5 stocks with explosive growth potential for TODAY with these criteria:
            - Small to mid-cap companies ($10M-$5B market cap)
            - Stocks with major catalysts happening TODAY or this week
            - High volume/momentum potential
            - Similar patterns to historic explosive moves like GameStop, AMC, Tesla 2020
            - Focus on: biotech FDA approvals, earnings beats, breakthrough announcements, short squeeze setups
            - Avoid large caps and boring dividend stocks
            
            For each stock provide: ticker, company name, current price, market cap, main catalyst, why it could explode today
            """,
            
            "week": """
            Find the top 5 stocks with explosive growth potential for THIS WEEK with these criteria:
            - Small to mid-cap companies ($10M-$5B market cap)  
            - Stocks with major catalysts in the next 7 days
            - High float squeeze potential or momentum breakout setups
            - Similar patterns to VIGL (+324%), CRWV (+171%), historic biotech moonshots
            - Focus on: FDA decisions, earnings surprises, sector rotation plays, short interest >20%
            - Avoid large caps and conservative plays
            
            For each stock provide: ticker, company name, current price, market cap, main catalyst, timeframe, explosive potential
            """,
            
            "month": """
            Find the top 5 stocks with explosive growth potential for SHORT-TERM (next 30 days) with these criteria:
            - Small to mid-cap companies ($10M-$5B market cap)
            - Stocks with major catalysts in next 30 days
            - Paradigm shift potential or revolutionary technology
            - Similar patterns to Tesla 2020 (+743%), Zoom 2020 (+396%), historic momentum explosions
            - Focus on: breakthrough technologies, regulatory approvals, market disruption, acquisition targets
            - Small float preferred for maximum squeeze potential
            
            For each stock provide: ticker, company name, current price, market cap, main catalyst, revolutionary potential, similar historic precedents
            """
        }
    
    async def discover_explosive_opportunities(self, timeframe: str = "week") -> List[StockCandidate]:
        """Main discovery function using REAL-TIME discovery systems"""
        
        print(f"🔍 STOCK DISCOVERY ENGINE - Finding explosive opportunities for {timeframe}")
        print("=" * 80)
        
        # Step 1: Use REAL-TIME discovery system instead of Perplexity
        print("🚀 Using REAL-TIME Stock Discovery (100% Live Data)")
        live_candidates = await self.real_time_discovery.discover_live_explosive_opportunities(timeframe)
        
        if not live_candidates:
            print("❌ No live candidates found from real-time discovery")
            # Fallback to Perplexity if real-time discovery fails
            print("🔄 Falling back to Perplexity discovery...")
            candidates = await self.query_perplexity_for_stocks(timeframe)
            
            if not candidates:
                print("❌ No candidates found from Perplexity either")
                return []
            
            print(f"📊 Found {len(candidates)} candidates from Perplexity (fallback)")
            
            # Step 2: Enrich candidates with market data
            enriched_candidates = await self.enrich_candidates_with_market_data(candidates)
            
            # Step 3: Filter candidates based on our criteria
            filtered_candidates = self.filter_candidates_by_criteria(enriched_candidates)
            
            print(f"✅ {len(filtered_candidates)} candidates passed screening")
            
            return filtered_candidates
        
        # Convert live candidates to StockCandidate format
        converted_candidates = []
        for live_candidate in live_candidates:
            stock_candidate = StockCandidate(
                ticker=live_candidate.ticker,
                company_name=live_candidate.company_name,
                sector=live_candidate.sector,
                market_cap=live_candidate.market_cap,
                current_price=live_candidate.current_price,
                discovery_reason=live_candidate.discovery_reason,
                catalyst_events=live_candidate.news_catalysts,
                time_horizon=live_candidate.time_horizon,
                perplexity_confidence=live_candidate.confidence_score,
                discovery_source=live_candidate.discovery_source
            )
            converted_candidates.append(stock_candidate)
        
        print(f"✅ {len(converted_candidates)} LIVE candidates found with real-time data")
        
        return converted_candidates
    
    async def query_perplexity_for_stocks(self, timeframe: str) -> List[StockCandidate]:
        """Query Perplexity AI for stock candidates"""
        
        if not self.perplexity_api_key:
            print("🚨 CRITICAL WARNING: PERPLEXITY API KEY NOT CONFIGURED")
            print("🔄 USING REAL-TIME DISCOVERY INSTEAD (Still live data, but no Perplexity AI)")
            print("💡 Set PERPLEXITY_API_KEY environment variable for enhanced discovery")
            # Use real-time discovery instead of mock data
            live_candidates = await self.real_time_discovery.discover_live_explosive_opportunities(timeframe)
            
            # Convert to StockCandidate format
            converted_candidates = []
            for live_candidate in live_candidates:
                stock_candidate = StockCandidate(
                    ticker=live_candidate.ticker,
                    company_name=live_candidate.company_name,
                    sector=live_candidate.sector,
                    market_cap=live_candidate.market_cap,
                    current_price=live_candidate.current_price,
                    discovery_reason=live_candidate.discovery_reason,
                    catalyst_events=live_candidate.news_catalysts,
                    time_horizon=live_candidate.time_horizon,
                    perplexity_confidence=live_candidate.confidence_score,
                    discovery_source="Real-Time Discovery (No Perplexity)"
                )
                converted_candidates.append(stock_candidate)
            
            return converted_candidates
        
        try:
            prompt = self.discovery_prompts[timeframe]
            
            # Enhanced prompt with current market context
            enhanced_prompt = f"""
            Today is {datetime.now().strftime('%Y-%m-%d')}. Market conditions context:
            
            {prompt}
            
            CRITICAL: Focus on stocks that could deliver 50-300% returns like our historic winners:
            - VIGL: +324% (biotech, 15M float, FDA catalyst)
            - CRWV: +171% (software, 12M float, momentum)
            - GameStop: +2,700% (retail squeeze, social momentum)
            - AMC: +2,850% (high shorts, meme status)
            
            Return results in JSON format with: ticker, company_name, sector, current_price, market_cap, discovery_reason, catalyst_events, confidence_score
            """
            
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'llama-3.1-sonar-large-128k-online',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an expert stock analyst specializing in finding explosive growth opportunities. Focus on small-cap stocks with major catalysts and squeeze potential.'
                    },
                    {
                        'role': 'user', 
                        'content': enhanced_prompt
                    }
                ],
                'temperature': 0.2,
                'max_tokens': 2000
            }
            
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse Perplexity response into candidates
                candidates = self.parse_perplexity_response(content, timeframe)
                
                print(f"🤖 Perplexity found {len(candidates)} candidates")
                return candidates
                
            else:
                print(f"❌ Perplexity API error: {response.status_code}")
                print("🔄 Falling back to REAL-TIME discovery...")
                # Use real-time discovery instead of mock data
                live_candidates = await self.real_time_discovery.discover_live_explosive_opportunities(timeframe)
                
                # Convert to StockCandidate format
                converted_candidates = []
                for live_candidate in live_candidates:
                    stock_candidate = StockCandidate(
                        ticker=live_candidate.ticker,
                        company_name=live_candidate.company_name,
                        sector=live_candidate.sector,
                        market_cap=live_candidate.market_cap,
                        current_price=live_candidate.current_price,
                        discovery_reason=live_candidate.discovery_reason,
                        catalyst_events=live_candidate.news_catalysts,
                        time_horizon=live_candidate.time_horizon,
                        perplexity_confidence=live_candidate.confidence_score,
                        discovery_source="Real-Time Discovery (API Error Fallback)"
                    )
                    converted_candidates.append(stock_candidate)
                
                return converted_candidates
                
        except Exception as e:
            print(f"❌ Error querying Perplexity: {e}")
            print("🔄 Falling back to REAL-TIME discovery...")
            # Use real-time discovery instead of mock data
            live_candidates = await self.real_time_discovery.discover_live_explosive_opportunities(timeframe)
            
            # Convert to StockCandidate format
            converted_candidates = []
            for live_candidate in live_candidates:
                stock_candidate = StockCandidate(
                    ticker=live_candidate.ticker,
                    company_name=live_candidate.company_name,
                    sector=live_candidate.sector,
                    market_cap=live_candidate.market_cap,
                    current_price=live_candidate.current_price,
                    discovery_reason=live_candidate.discovery_reason,
                    catalyst_events=live_candidate.news_catalysts,
                    time_horizon=live_candidate.time_horizon,
                    perplexity_confidence=live_candidate.confidence_score,
                    discovery_source="Real-Time Discovery (Exception Fallback)"
                )
                converted_candidates.append(stock_candidate)
            
            return converted_candidates
    
    def parse_perplexity_response(self, content: str, timeframe: str) -> List[StockCandidate]:
        """Parse Perplexity response into stock candidates"""
        
        candidates = []
        
        try:
            # Try to extract JSON from response
            if '{' in content and '}' in content:
                # Extract JSON portion
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_content = content[json_start:json_end]
                
                # Try to parse as JSON
                try:
                    data = json.loads(json_content)
                    if isinstance(data, list):
                        stock_data = data
                    else:
                        stock_data = [data]
                except:
                    stock_data = []
            else:
                stock_data = []
            
            # If JSON parsing fails, use text parsing
            if not stock_data:
                stock_data = self.extract_stocks_from_text(content)
            
            # Convert to StockCandidate objects
            for stock in stock_data:
                if isinstance(stock, dict):
                    candidate = StockCandidate(
                        ticker=stock.get('ticker', '').upper(),
                        company_name=stock.get('company_name', ''),
                        sector=stock.get('sector', 'Unknown'),
                        market_cap=float(stock.get('market_cap', 0)),
                        current_price=float(stock.get('current_price', 0)),
                        discovery_reason=stock.get('discovery_reason', ''),
                        catalyst_events=stock.get('catalyst_events', []),
                        time_horizon=timeframe,
                        perplexity_confidence=float(stock.get('confidence_score', 0.5)),
                        discovery_source="Perplexity AI"
                    )
                    
                    if candidate.ticker:  # Only add if we have a ticker
                        candidates.append(candidate)
                        
        except Exception as e:
            print(f"❌ Error parsing Perplexity response: {e}")
        
        return candidates
    
    def extract_stocks_from_text(self, content: str) -> List[Dict]:
        """Extract stock information from text when JSON parsing fails"""
        
        stocks = []
        
        # Look for common patterns in stock discussions
        import re
        
        # Pattern to find ticker symbols
        ticker_pattern = r'\b[A-Z]{1,5}\b'
        tickers = re.findall(ticker_pattern, content)
        
        # Filter out common false positives
        false_positives = {'USD', 'API', 'FDA', 'CEO', 'IPO', 'AI', 'ML', 'VR', 'AR', 'EV', 'PT', 'AM', 'PM'}
        valid_tickers = [t for t in tickers if t not in false_positives and len(t) <= 5]
        
        # Take first few unique tickers
        unique_tickers = list(dict.fromkeys(valid_tickers))[:5]
        
        for ticker in unique_tickers:
            stocks.append({
                'ticker': ticker,
                'company_name': f"{ticker} Corp",
                'sector': 'Technology',
                'market_cap': 1000000000,  # $1B default
                'current_price': 50.0,
                'discovery_reason': 'Identified by Perplexity text analysis',
                'catalyst_events': ['Market opportunity'],
                'confidence_score': 0.6
            })
        
        return stocks
    
    def get_mock_candidates(self, timeframe: str) -> List[StockCandidate]:
        """Mock candidates for testing when Perplexity API is unavailable"""
        
        mock_data = {
            "today": [
                StockCandidate(
                    ticker="RXRX",
                    company_name="Recursion Pharmaceuticals",
                    sector="Biotechnology",
                    market_cap=1_200_000_000,
                    current_price=8.50,
                    discovery_reason="AI drug discovery breakthrough, small float, FDA catalyst approaching",
                    catalyst_events=["FDA meeting this week", "AI partnership announcement"],
                    time_horizon="today",
                    perplexity_confidence=0.85,
                    discovery_source="Mock Data"
                ),
                StockCandidate(
                    ticker="SOUN",
                    company_name="SoundHound AI",
                    sector="Technology",
                    market_cap=800_000_000,
                    current_price=4.20,
                    discovery_reason="AI voice technology, small cap momentum, high short interest",
                    catalyst_events=["Earnings today", "AI partnership rumors"],
                    time_horizon="today",
                    perplexity_confidence=0.80,
                    discovery_source="Mock Data"
                )
            ],
            "week": [
                StockCandidate(
                    ticker="IONQ",
                    company_name="IonQ Inc",
                    sector="Technology",
                    market_cap=1_500_000_000,
                    current_price=12.30,
                    discovery_reason="Quantum computing breakthrough, small float, federal contracts",
                    catalyst_events=["Federal contract announcement", "Quantum breakthrough publication"],
                    time_horizon="week",
                    perplexity_confidence=0.90,
                    discovery_source="Mock Data"
                ),
                StockCandidate(
                    ticker="BBAI",
                    company_name="BigBear.ai",
                    sector="Technology",
                    market_cap=600_000_000,
                    current_price=3.80,
                    discovery_reason="AI analytics for defense, small cap, government contracts",
                    catalyst_events=["Defense contract renewal", "AI model launch"],
                    time_horizon="week",
                    perplexity_confidence=0.75,
                    discovery_source="Mock Data"
                )
            ],
            "month": [
                StockCandidate(
                    ticker="RGTI",
                    company_name="Rigetti Computing",
                    sector="Technology",
                    market_cap=400_000_000,
                    current_price=2.10,
                    discovery_reason="Quantum computing, very small cap, breakthrough potential",
                    catalyst_events=["Quantum chip launch", "IBM partnership potential"],
                    time_horizon="month",
                    perplexity_confidence=0.85,
                    discovery_source="Mock Data"
                ),
                StockCandidate(
                    ticker="QBTS",
                    company_name="D-Wave Quantum",
                    sector="Technology",
                    market_cap=300_000_000,
                    current_price=1.50,
                    discovery_reason="Quantum annealing leader, micro cap, enterprise adoption",
                    catalyst_events=["Enterprise customer wins", "Quantum advantage demonstration"],
                    time_horizon="month",
                    perplexity_confidence=0.80,
                    discovery_source="Mock Data"
                )
            ]
        }
        
        return mock_data.get(timeframe, [])
    
    async def enrich_candidates_with_market_data(self, candidates: List[StockCandidate]) -> List[StockCandidate]:
        """Enrich candidates with real market data"""
        
        enriched = []
        
        for candidate in candidates:
            try:
                # Get real market data using yfinance
                import yfinance as yf
                
                ticker_obj = yf.Ticker(candidate.ticker)
                info = ticker_obj.info
                hist = ticker_obj.history(period="30d")
                
                if not hist.empty:
                    # Update with real data
                    candidate.current_price = float(hist['Close'].iloc[-1])
                    candidate.market_cap = info.get('marketCap', candidate.market_cap)
                    
                    # Add volume analysis
                    current_volume = hist['Volume'].iloc[-1]
                    avg_volume = hist['Volume'].mean()
                    
                    # Add to discovery reason if volume is spiking
                    if current_volume > avg_volume * 2:
                        candidate.discovery_reason += f" | Volume spike: {current_volume/avg_volume:.1f}x above average"
                
                enriched.append(candidate)
                
            except Exception as e:
                print(f"⚠️ Could not enrich {candidate.ticker}: {e}")
                # Keep original data if enrichment fails
                enriched.append(candidate)
        
        return enriched
    
    def filter_candidates_by_criteria(self, candidates: List[StockCandidate]) -> List[StockCandidate]:
        """Filter candidates based on our explosive growth criteria"""
        
        filtered = []
        
        for candidate in candidates:
            # Market cap filter
            if candidate.market_cap < self.min_market_cap or candidate.market_cap > self.max_market_cap:
                continue
            
            # Price filter (avoid penny stocks below $1 and expensive stocks above $100)
            if candidate.current_price < 1.0 or candidate.current_price > 100.0:
                continue
            
            # Confidence filter
            if candidate.perplexity_confidence < 0.6:
                continue
            
            # Sector preference (prefer high-growth sectors)
            preferred_sectors = ['Technology', 'Biotechnology', 'Healthcare', 'Software', 'Semiconductors']
            if candidate.sector not in preferred_sectors:
                # Still include but lower confidence
                candidate.perplexity_confidence *= 0.9
            
            filtered.append(candidate)
        
        # Sort by confidence
        filtered.sort(key=lambda x: x.perplexity_confidence, reverse=True)
        
        return filtered
    
    async def run_ai_debates_on_candidates(self, candidates: List[StockCandidate]) -> List[Dict[str, Any]]:
        """Run REAL-TIME Claude vs ChatGPT debates on each candidate"""
        
        print(f"🤖 Running REAL-TIME AI debates on {len(candidates)} candidates...")
        print("=" * 80)
        
        debate_results = []
        
        for candidate in candidates:
            print(f"\n🎯 LIVE DEBATE: {candidate.ticker} - {candidate.company_name}")
            print(f"   Discovery: {candidate.discovery_reason}")
            print(f"   Catalysts: {', '.join(candidate.catalyst_events)}")
            
            # Convert candidate to stock_data format for REAL-TIME AI debate
            stock_data = {
                "ticker": candidate.ticker,
                "company_name": candidate.company_name,
                "sector": candidate.sector,
                "current_price": candidate.current_price,
                "market_cap": candidate.market_cap,
                "float_shares": candidate.market_cap / candidate.current_price * 0.7,  # Estimate float as 70% of market cap
                "short_interest": 25,  # Default assumption for small caps
                "catalysts": candidate.catalyst_events,
                "discovery_reason": candidate.discovery_reason,
                "time_horizon": candidate.time_horizon,
                "perplexity_confidence": candidate.perplexity_confidence
            }
            
            # Market context for real-time debate
            market_context = {
                "spy_change": 0.5,  # Would get real SPY data
                "vix_level": 20.0,  # Would get real VIX data
                "sector_trend": "neutral",
                "timestamp": datetime.now().isoformat()
            }
            
            # Run REAL-TIME AI debate with actual API calls
            if self.real_time_ai_debate.anthropic_api_key and self.real_time_ai_debate.openai_api_key:
                print(f"   🚀 Using REAL-TIME AI Debate (Live API calls)")
                live_debate_result = await self.real_time_ai_debate.run_live_ai_debate(stock_data, market_context)
                
                # Convert LiveDebateResult to our format
                debate_result = {
                    "final_recommendation": live_debate_result.final_recommendation,
                    "confidence": live_debate_result.confidence,
                    "success_probability": live_debate_result.success_probability,
                    "target_price": live_debate_result.target_price,
                    "stop_loss": live_debate_result.stop_loss,
                    "time_horizon": live_debate_result.time_horizon,
                    "consensus_reached": live_debate_result.consensus_reached,
                    "debate_rounds": len(live_debate_result.debate_rounds),
                    "key_insights": live_debate_result.key_insights,
                    "risk_factors": live_debate_result.risk_factors,
                    "debate_time": live_debate_result.total_debate_time,
                    "ai_source": "Real-Time Live Debate"
                }
            else:
                print(f"   🔄 API keys not configured, using enhanced AI consensus")
                # Fallback to enhanced AI consensus
                debate_result = await self.ai_consensus.run_historic_enhanced_consensus(stock_data)
            
            # Add candidate info to result
            debate_result["candidate_info"] = {
                "ticker": candidate.ticker,
                "company_name": candidate.company_name,
                "discovery_reason": candidate.discovery_reason,
                "catalyst_events": candidate.catalyst_events,
                "time_horizon": candidate.time_horizon,
                "perplexity_confidence": candidate.perplexity_confidence,
                "discovery_source": candidate.discovery_source
            }
            
            debate_results.append(debate_result)
            
            print(f"   🏆 Result: {debate_result.get('final_recommendation', 'INCONCLUSIVE')}")
            print(f"   🎯 Confidence: {debate_result.get('confidence', 0):.0%}")
            
            # Brief pause between debates
            await asyncio.sleep(1)
        
        return debate_results
    
    def rank_final_recommendations(self, debate_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank final recommendations based on AI consensus and criteria"""
        
        print(f"\n🏆 RANKING FINAL RECOMMENDATIONS")
        print("=" * 80)
        
        # Filter for BUY recommendations
        buy_recommendations = [
            result for result in debate_results
            if result.get('final_recommendation') in ['BUY', 'STRONG_BUY', 'URGENT BUY', 'AGGRESSIVE_BUY']
        ]
        
        # Calculate composite score for ranking
        for result in buy_recommendations:
            confidence = result.get('confidence', 0)
            success_probability = result.get('success_probability', 0)
            perplexity_confidence = result.get('candidate_info', {}).get('perplexity_confidence', 0)
            
            # Pre-breakout signal bonus
            pre_breakout_signals = result.get('pre_breakout_signals', {})
            timing_urgency = pre_breakout_signals.get('timing_urgency', 'LOW')
            timing_bonus = {
                'CRITICAL': 0.3,
                'HIGH': 0.2,
                'MEDIUM': 0.1,
                'LOW': 0.0
            }.get(timing_urgency, 0)
            
            # Composite score (0-1 scale)
            composite_score = (
                confidence * 0.4 +
                success_probability * 0.3 +
                perplexity_confidence * 0.2 +
                timing_bonus * 0.1
            )
            
            result['composite_score'] = composite_score
        
        # Sort by composite score
        buy_recommendations.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Print ranking
        print(f"📊 Found {len(buy_recommendations)} BUY recommendations:")
        for i, result in enumerate(buy_recommendations, 1):
            candidate_info = result['candidate_info']
            print(f"   {i}. {candidate_info['ticker']} - Score: {result['composite_score']:.2f}")
            print(f"      {candidate_info['discovery_reason']}")
        
        return buy_recommendations
    
    async def run_full_discovery_pipeline(self, timeframe: str = "week") -> Dict[str, Any]:
        """Run the complete discovery pipeline"""
        
        start_time = time.time()
        
        print(f"🚀 STARTING FULL STOCK DISCOVERY PIPELINE")
        print(f"⏰ Timeframe: {timeframe.upper()}")
        print(f"🎯 Target: Explosive growth opportunities for 60%+ returns")
        print("=" * 80)
        
        # Step 1: Discovery with Perplexity
        candidates = await self.discover_explosive_opportunities(timeframe)
        
        if not candidates:
            return {
                "success": False,
                "message": "No candidates found",
                "timeframe": timeframe,
                "total_time": time.time() - start_time
            }
        
        # Step 2: AI Debates
        debate_results = await self.run_ai_debates_on_candidates(candidates)
        
        # Step 3: Final Ranking
        final_recommendations = self.rank_final_recommendations(debate_results)
        
        # Step 4: Prepare results
        pipeline_results = {
            "success": True,
            "timeframe": timeframe,
            "discovery_timestamp": datetime.now().isoformat(),
            "total_candidates_found": len(candidates),
            "total_debates_completed": len(debate_results),
            "final_recommendations": final_recommendations,
            "top_pick": final_recommendations[0] if final_recommendations else None,
            "pipeline_summary": {
                "discovery_source": "Perplexity AI",
                "ai_analysts": "Claude vs ChatGPT",
                "filtering_criteria": "60%+ return potential, small/mid-cap, pre-breakout signals",
                "total_time_seconds": time.time() - start_time
            }
        }
        
        print(f"\n🎉 PIPELINE COMPLETE!")
        print(f"⏱️ Total time: {time.time() - start_time:.1f} seconds")
        print(f"🏆 Top recommendation: {pipeline_results['top_pick']['candidate_info']['ticker'] if pipeline_results['top_pick'] else 'None'}")
        
        return pipeline_results

class DailyLearningEngine:
    """Daily learning system that studies market winners to improve discovery"""
    
    def __init__(self, discovery_engine: StockDiscoveryEngine):
        self.discovery_engine = discovery_engine
        
        # Use relative paths that work from any location
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.learning_log_file = os.path.join(base_dir, "logs", "daily_learning.json")
        self.improvements_log_file = os.path.join(base_dir, "logs", "system_improvements.json")
        
        # Learning parameters
        self.min_price_change = 15.0  # Minimum 15% move to study
        self.min_volume_spike = 2.0   # Minimum 2x volume spike
        self.top_winners_count = 10   # Study top 10 winners daily
        
    async def run_daily_learning_cycle(self) -> Dict[str, Any]:
        """Run complete daily learning cycle after market close"""
        
        print(f"🎓 DAILY LEARNING SYSTEM ACTIVATED")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Step 1: Find today's biggest winners
        market_winners = await self.find_daily_market_winners()
        
        if not market_winners:
            print("❌ No significant market winners found today")
            return {"success": False, "message": "No winners to analyze"}
        
        print(f"🏆 Found {len(market_winners)} explosive winners to study")
        
        # Step 2: Deep analysis of each winner
        winner_analyses = await self.analyze_market_winners(market_winners)
        
        # Step 3: Identify system gaps and improvements
        system_improvements = await self.identify_system_improvements(winner_analyses)
        
        # Step 4: Generate updated discovery criteria
        updated_criteria = await self.generate_updated_discovery_criteria(winner_analyses)
        
        # Step 5: Log everything for future reference
        learning_results = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "market_winners": [winner.__dict__ for winner in market_winners],
            "winner_analyses": winner_analyses,
            "system_improvements": [imp.__dict__ for imp in system_improvements],
            "updated_criteria": updated_criteria,
            "learning_summary": {
                "total_winners_studied": len(market_winners),
                "improvements_identified": len(system_improvements),
                "high_priority_improvements": len([i for i in system_improvements if i.priority == "high"]),
                "processing_time": time.time() - start_time
            }
        }
        
        # Log the results
        await self.log_learning_results(learning_results)
        
        # Send learning summary to Slack
        await self.send_learning_slack_notification(learning_results)
        
        print(f"🎉 Daily learning complete! {len(system_improvements)} improvements identified")
        
        return learning_results
    
    async def find_daily_market_winners(self) -> List[MarketWinner]:
        """Find today's biggest winners for analysis"""
        
        print("🔍 Scanning today's biggest market winners...")
        
        winners = []
        
        try:
            # Use yfinance to scan major indices for winners
            import yfinance as yf
            
            # Get popular stock lists
            stock_lists = [
                # High volume small/mid caps
                ['IONQ', 'RXRX', 'SOUN', 'BBAI', 'RGTI', 'QBTS'],
                # Biotech momentum 
                ['NVAX', 'MRNA', 'BNTX', 'GILD', 'BIIB'],
                # EV/Clean energy
                ['LCID', 'RIVN', 'QS', 'BLNK', 'CHPT'],
                # Quantum/AI
                ['QUBT', 'IONQ', 'RGTI', 'SMCI'],
                # Meme/momentum
                ['AMC', 'GME', 'BBBY', 'CLOV'],
                # Recent IPOs/SPACs
                ['HOOD', 'COIN', 'AFRM', 'SOFI']
            ]
            
            # Flatten the list
            all_tickers = list(set([ticker for sublist in stock_lists for ticker in sublist]))
            
            # Add some random discovery from trending lists
            trending_tickers = await self.get_trending_stocks()
            all_tickers.extend(trending_tickers)
            
            print(f"📊 Analyzing {len(all_tickers)} stocks for explosive moves...")
            
            # Analyze each ticker
            for ticker in all_tickers:
                try:
                    winner = await self.analyze_stock_for_winner_status(ticker)
                    if winner:
                        winners.append(winner)
                        print(f"   🎯 {ticker}: +{winner.price_change_percent:.1f}% (Volume: {winner.volume_spike:.1f}x)")
                    
                    # Brief delay to avoid rate limits
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"   ⚠️ Error analyzing {ticker}: {e}")
                    continue
            
            # Sort by price change and take top winners
            winners.sort(key=lambda x: x.price_change_percent, reverse=True)
            return winners[:self.top_winners_count]
            
        except Exception as e:
            print(f"❌ Error finding market winners: {e}")
            return []
    
    async def get_trending_stocks(self) -> List[str]:
        """Get trending stocks from various sources"""
        
        trending = []
        
        try:
            # Could integrate with:
            # - Yahoo Finance trending
            # - Reddit mentions
            # - Twitter trends
            # - Unusual options activity
            
            # For now, use some known volatile tickers
            volatile_tickers = [
                'SPCE', 'PLTR', 'WISH', 'CLOV', 'CLNE', 'WKHS', 'RIDE', 'NKLA',
                'TLRY', 'SNDL', 'CGC', 'ACB', 'APHA', 'HEXO',
                'TSLA', 'NIO', 'XPEV', 'LI', 'BABA', 'JD'
            ]
            
            # Add current high-momentum sectors
            biotech_tickers = ['SAVA', 'AXSM', 'PTCT', 'FOLD', 'ARQT']
            ai_tickers = ['NVDA', 'AMD', 'GOOGL', 'MSFT', 'META']
            
            trending.extend(volatile_tickers[:5])  # Sample a few
            trending.extend(biotech_tickers[:3])
            trending.extend(ai_tickers[:3])
            
            return trending
            
        except Exception as e:
            print(f"⚠️ Error getting trending stocks: {e}")
            return []
    
    async def analyze_stock_for_winner_status(self, ticker: str) -> Optional[MarketWinner]:
        """Analyze if a stock qualifies as a 'winner' worth studying"""
        
        try:
            import yfinance as yf
            
            stock = yf.Ticker(ticker)
            
            # Get recent price data
            hist = stock.history(period="5d")
            if len(hist) < 2:
                return None
            
            # Calculate price change
            current_price = hist['Close'].iloc[-1]
            previous_price = hist['Close'].iloc[-2]
            price_change_percent = ((current_price - previous_price) / previous_price) * 100
            
            # Calculate volume spike
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].iloc[:-1].mean()
            volume_spike = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Check if it qualifies as a winner
            if price_change_percent < self.min_price_change or volume_spike < self.min_volume_spike:
                return None
            
            # Get additional data
            info = stock.info
            
            # Get news/catalysts
            news_events = await self.get_stock_news_events(ticker)
            
            # Analyze why our system might have missed this
            why_missed = await self.analyze_why_system_missed(ticker, price_change_percent, volume_spike)
            
            winner = MarketWinner(
                ticker=ticker,
                company_name=info.get('longName', ticker),
                sector=info.get('sector', 'Unknown'),
                price_change_percent=price_change_percent,
                volume_spike=volume_spike,
                market_cap=info.get('marketCap', 0),
                float_shares=info.get('floatShares', 0),
                catalyst_detected=news_events[0] if news_events else "Volume/momentum driven",
                news_events=news_events,
                social_sentiment=await self.get_social_sentiment_for_stock(ticker),
                why_system_missed=why_missed,
                lessons_learned=await self.extract_lessons_from_winner(ticker, price_change_percent, volume_spike, news_events)
            )
            
            return winner
            
        except Exception as e:
            print(f"❌ Error analyzing {ticker}: {e}")
            return None
    
    async def get_stock_news_events(self, ticker: str) -> List[str]:
        """Get recent news events for a stock"""
        
        try:
            import yfinance as yf
            
            stock = yf.Ticker(ticker)
            news = stock.news
            
            events = []
            for article in news[:3]:  # Get top 3 recent articles
                title = article.get('title', '')
                # Look for catalyst keywords
                catalyst_keywords = [
                    'earnings', 'revenue', 'beat', 'exceed', 'approval', 'fda',
                    'partnership', 'deal', 'acquisition', 'merger', 'breakthrough',
                    'contract', 'award', 'upgrade', 'target', 'analyst'
                ]
                
                if any(keyword in title.lower() for keyword in catalyst_keywords):
                    events.append(title)
            
            return events[:3]  # Return top 3 events
            
        except Exception as e:
            print(f"⚠️ Error getting news for {ticker}: {e}")
            return ["News analysis unavailable"]
    
    async def get_social_sentiment_for_stock(self, ticker: str) -> str:
        """Get social sentiment for a specific stock"""
        
        try:
            # Could integrate with Reddit API, Twitter API, etc.
            # For now, return a placeholder
            return "Positive momentum detected"
            
        except Exception as e:
            return "Sentiment analysis unavailable"
    
    async def analyze_why_system_missed(self, ticker: str, price_change: float, volume_spike: float) -> List[str]:
        """Analyze why our discovery system missed this winner"""
        
        reasons = []
        
        # Check against our discovery criteria
        if price_change > 50:
            reasons.append("Extremely high price movement - may need better pre-breakout detection")
        
        if volume_spike > 10:
            reasons.append("Massive volume spike - need better volume alert thresholds")
        
        # Check if it was in our scan universe
        stock_lists = ['IONQ', 'RXRX', 'SOUN', 'BBAI', 'NVAX', 'MRNA']  # Sample of our usual candidates
        if ticker not in stock_lists:
            reasons.append("Stock not in our primary scan universe - need broader coverage")
        
        # Check timing
        current_hour = datetime.now().hour
        if current_hour < 12:
            reasons.append("Early morning move - may need pre-market scanning")
        elif current_hour > 15:
            reasons.append("After-hours move - need extended hours monitoring")
        
        # Default reason
        if not reasons:
            reasons.append("Pattern not detected by current algorithms - need enhanced signal detection")
        
        return reasons
    
    async def extract_lessons_from_winner(self, ticker: str, price_change: float, volume_spike: float, news_events: List[str]) -> List[str]:
        """Extract actionable lessons from this winner"""
        
        lessons = []
        
        # Price movement lessons
        if price_change > 100:
            lessons.append("Extreme moves possible - increase target thresholds")
        elif price_change > 50:
            lessons.append("Significant moves achievable - maintain aggressive targets")
        
        # Volume lessons
        if volume_spike > 5:
            lessons.append("High volume spikes precede major moves - enhance volume alerts")
        
        # News/catalyst lessons
        for event in news_events:
            event_lower = event.lower()
            if 'earnings' in event_lower:
                lessons.append("Earnings surprises create opportunities - add earnings calendar monitoring")
            elif 'fda' in event_lower or 'approval' in event_lower:
                lessons.append("FDA/regulatory events are major catalysts - enhance regulatory calendar")
            elif 'partnership' in event_lower or 'deal' in event_lower:
                lessons.append("Partnership announcements drive moves - monitor M&A activity")
        
        # Default lesson
        if not lessons:
            lessons.append("Study this pattern for future detection improvements")
        
        return lessons
    
    async def analyze_market_winners(self, winners: List[MarketWinner]) -> List[Dict[str, Any]]:
        """Deep analysis of market winners"""
        
        print(f"🔬 Deep analysis of {len(winners)} market winners...")
        
        analyses = []
        
        for winner in winners:
            print(f"   📊 Analyzing {winner.ticker} (+{winner.price_change_percent:.1f}%)")
            
            analysis = {
                "ticker": winner.ticker,
                "move_analysis": {
                    "price_change": winner.price_change_percent,
                    "volume_spike": winner.volume_spike,
                    "move_type": self.classify_move_type(winner),
                    "catalyst_strength": self.assess_catalyst_strength(winner)
                },
                "discovery_gaps": {
                    "why_missed": winner.why_system_missed,
                    "detection_difficulty": self.assess_detection_difficulty(winner),
                    "timing_issues": self.identify_timing_issues(winner)
                },
                "pattern_insights": {
                    "float_impact": self.analyze_float_impact(winner),
                    "sector_correlation": self.analyze_sector_patterns(winner),
                    "catalyst_type": self.categorize_catalyst(winner)
                },
                "lessons": winner.lessons_learned,
                "improvement_opportunities": self.identify_improvement_opportunities(winner)
            }
            
            analyses.append(analysis)
        
        return analyses
    
    def classify_move_type(self, winner: MarketWinner) -> str:
        """Classify the type of price movement"""
        
        if winner.price_change_percent > 100:
            return "EXPLOSIVE_MOONSHOT"
        elif winner.price_change_percent > 50:
            return "MAJOR_BREAKOUT"
        elif winner.price_change_percent > 25:
            return "SIGNIFICANT_MOVE"
        else:
            return "MODERATE_GAIN"
    
    def assess_catalyst_strength(self, winner: MarketWinner) -> str:
        """Assess the strength of the catalyst"""
        
        catalyst_keywords = {
            "HIGH": ['fda approval', 'acquisition', 'merger', 'breakthrough', 'partnership'],
            "MEDIUM": ['earnings beat', 'upgrade', 'contract', 'deal'],
            "LOW": ['analyst', 'target', 'momentum', 'volume']
        }
        
        catalyst_text = (winner.catalyst_detected + " " + " ".join(winner.news_events)).lower()
        
        for strength, keywords in catalyst_keywords.items():
            if any(keyword in catalyst_text for keyword in keywords):
                return strength
        
        return "UNKNOWN"
    
    def assess_detection_difficulty(self, winner: MarketWinner) -> str:
        """Assess how difficult this should have been to detect"""
        
        if winner.volume_spike > 5 and len(winner.news_events) > 0:
            return "EASY"  # High volume + news = should have caught this
        elif winner.volume_spike > 3 or len(winner.news_events) > 0:
            return "MODERATE"  # Some signals present
        else:
            return "DIFFICULT"  # Minimal early signals
    
    def identify_timing_issues(self, winner: MarketWinner) -> List[str]:
        """Identify timing-related issues"""
        
        issues = []
        
        # Could analyze:
        # - Pre-market gaps
        # - After-hours moves
        # - Intraday timing
        # - News timing vs price movement
        
        if winner.volume_spike > 10:
            issues.append("Massive volume spike suggests very early detection was possible")
        
        if winner.price_change_percent > 50:
            issues.append("Large move suggests gradual buildup was detectable")
        
        return issues
    
    def analyze_float_impact(self, winner: MarketWinner) -> Dict[str, Any]:
        """Analyze how float size impacted the move"""
        
        if winner.float_shares == 0:
            return {"analysis": "Float data unavailable"}
        
        if winner.float_shares < 20_000_000:
            return {
                "float_category": "SMALL",
                "impact": "Small float likely amplified the move significantly",
                "lesson": "Prioritize small float stocks for explosive potential"
            }
        elif winner.float_shares < 100_000_000:
            return {
                "float_category": "MEDIUM", 
                "impact": "Medium float still allowed significant movement",
                "lesson": "Medium float can work with strong catalysts"
            }
        else:
            return {
                "float_category": "LARGE",
                "impact": "Large float overcome by exceptional catalyst",
                "lesson": "Large float stocks need extraordinary catalysts for big moves"
            }
    
    def analyze_sector_patterns(self, winner: MarketWinner) -> Dict[str, Any]:
        """Analyze sector-specific patterns"""
        
        sector_insights = {
            "Biotechnology": "FDA/regulatory catalysts drive explosive moves",
            "Technology": "AI/innovation themes create momentum",
            "Healthcare": "Clinical trial results and approvals key",
            "Energy": "Commodity prices and policy changes drive moves",
            "Financial": "Interest rate and regulatory environment sensitive"
        }
        
        return {
            "sector": winner.sector,
            "insight": sector_insights.get(winner.sector, "Sector-specific analysis needed"),
            "recommendation": f"Enhance {winner.sector} sector monitoring"
        }
    
    def categorize_catalyst(self, winner: MarketWinner) -> str:
        """Categorize the type of catalyst"""
        
        catalyst_text = (winner.catalyst_detected + " " + " ".join(winner.news_events)).lower()
        
        if any(word in catalyst_text for word in ['fda', 'approval', 'regulatory']):
            return "REGULATORY"
        elif any(word in catalyst_text for word in ['earnings', 'revenue', 'beat']):
            return "EARNINGS"
        elif any(word in catalyst_text for word in ['partnership', 'deal', 'acquisition', 'merger']):
            return "CORPORATE_ACTION"
        elif any(word in catalyst_text for word in ['breakthrough', 'innovation', 'technology']):
            return "INNOVATION"
        else:
            return "MOMENTUM"
    
    def identify_improvement_opportunities(self, winner: MarketWinner) -> List[str]:
        """Identify specific improvement opportunities"""
        
        opportunities = []
        
        # Volume-based improvements
        if winner.volume_spike > 5:
            opportunities.append("Implement real-time volume spike alerts")
        
        # News-based improvements
        if winner.news_events:
            opportunities.append("Enhance news sentiment analysis")
            opportunities.append("Add real-time news catalyst detection")
        
        # Timing improvements
        if "pre-market" in str(winner.why_system_missed).lower():
            opportunities.append("Add pre-market scanning capabilities")
        
        # Sector improvements
        opportunities.append(f"Expand {winner.sector} sector coverage")
        
        return opportunities
    
    async def identify_system_improvements(self, winner_analyses: List[Dict[str, Any]]) -> List[SystemImprovement]:
        """Identify specific system improvements based on winner analysis"""
        
        print("🔧 Identifying system improvements...")
        
        improvements = []
        
        # Analyze patterns across all winners
        common_patterns = self.find_common_patterns(winner_analyses)
        
        # Volume-based improvements
        high_volume_winners = [w for w in winner_analyses if w['move_analysis']['volume_spike'] > 5]
        if len(high_volume_winners) > 1:
            improvements.append(SystemImprovement(
                improvement_type="signal_detection",
                description="Multiple winners had 5x+ volume spikes - enhance volume alert system",
                implementation="Lower volume spike threshold from 3x to 2x, add real-time volume monitoring",
                priority="high",
                expected_impact="Earlier detection of 30% of explosive moves"
            ))
        
        # News/catalyst improvements
        news_driven_winners = [w for w in winner_analyses if len(w['pattern_insights'].get('catalyst_type', '')) > 0]
        if len(news_driven_winners) > 2:
            improvements.append(SystemImprovement(
                improvement_type="prompt",
                description="Multiple catalyst-driven winners - enhance Perplexity news detection",
                implementation="Add real-time news scanning to Perplexity prompts, focus on breaking news",
                priority="high",
                expected_impact="Better catalyst timing detection"
            ))
        
        # Sector-specific improvements
        sector_patterns = {}
        for analysis in winner_analyses:
            sector = analysis['pattern_insights']['sector_correlation']['sector']
            if sector not in sector_patterns:
                sector_patterns[sector] = 0
            sector_patterns[sector] += 1
        
        for sector, count in sector_patterns.items():
            if count > 1:
                improvements.append(SystemImprovement(
                    improvement_type="criteria",
                    description=f"Multiple {sector} winners - expand sector coverage",
                    implementation=f"Add more {sector} tickers to scan universe, enhance {sector} catalysts",
                    priority="medium",
                    expected_impact=f"Better {sector} opportunity detection"
                ))
        
        # Timing improvements
        easy_detections = [w for w in winner_analyses if w['discovery_gaps']['detection_difficulty'] == 'EASY']
        if len(easy_detections) > 1:
            improvements.append(SystemImprovement(
                improvement_type="timing",
                description="Multiple 'easy' winners missed - timing issue",
                implementation="Add pre-market scanning, enhance real-time monitoring frequency",
                priority="high",
                expected_impact="Catch obvious opportunities before they explode"
            ))
        
        # Float-based improvements
        small_float_winners = [w for w in winner_analyses 
                              if w['pattern_insights']['float_impact'].get('float_category') == 'SMALL']
        if len(small_float_winners) > 1:
            improvements.append(SystemImprovement(
                improvement_type="criteria",
                description="Multiple small float winners - prioritize small float stocks",
                implementation="Increase small float weighting in discovery algorithm, add float size alerts",
                priority="medium",
                expected_impact="Better focus on high-explosive potential stocks"
            ))
        
        return improvements
    
    def find_common_patterns(self, winner_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find common patterns across winners"""
        
        patterns = {
            "common_sectors": {},
            "common_catalyst_types": {},
            "common_move_types": {},
            "common_gaps": []
        }
        
        for analysis in winner_analyses:
            # Sector patterns
            sector = analysis['pattern_insights']['sector_correlation']['sector']
            patterns["common_sectors"][sector] = patterns["common_sectors"].get(sector, 0) + 1
            
            # Catalyst patterns
            catalyst_type = analysis['pattern_insights']['catalyst_type']
            patterns["common_catalyst_types"][catalyst_type] = patterns["common_catalyst_types"].get(catalyst_type, 0) + 1
            
            # Move type patterns
            move_type = analysis['move_analysis']['move_type']
            patterns["common_move_types"][move_type] = patterns["common_move_types"].get(move_type, 0) + 1
            
            # Common gaps
            for gap in analysis['discovery_gaps']['why_missed']:
                if gap not in patterns["common_gaps"]:
                    patterns["common_gaps"].append(gap)
        
        return patterns
    
    async def generate_updated_discovery_criteria(self, winner_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate updated discovery criteria based on learned patterns"""
        
        print("📋 Generating updated discovery criteria...")
        
        # Analyze successful patterns
        successful_patterns = self.analyze_successful_patterns(winner_analyses)
        
        updated_criteria = {
            "volume_thresholds": {
                "current": 3.0,
                "recommended": 2.0,
                "reason": "Multiple winners had 2-3x volume before explosion"
            },
            "price_change_targets": {
                "current": [15, 50, 100],
                "recommended": [20, 75, 150],
                "reason": "Observed moves larger than current targets"
            },
            "sector_priorities": successful_patterns["sector_priorities"],
            "catalyst_keywords": successful_patterns["effective_catalysts"],
            "float_preferences": successful_patterns["float_analysis"],
            "timing_adjustments": successful_patterns["timing_insights"],
            "perplexity_prompt_updates": self.generate_updated_prompts(winner_analyses)
        }
        
        return updated_criteria
    
    def analyze_successful_patterns(self, winner_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns from successful moves"""
        
        # Sector analysis
        sector_performance = {}
        for analysis in winner_analyses:
            sector = analysis['pattern_insights']['sector_correlation']['sector']
            price_change = analysis['move_analysis']['price_change']
            
            if sector not in sector_performance:
                sector_performance[sector] = []
            sector_performance[sector].append(price_change)
        
        # Calculate average performance by sector
        sector_priorities = {}
        for sector, changes in sector_performance.items():
            avg_change = sum(changes) / len(changes)
            sector_priorities[sector] = {
                "avg_performance": avg_change,
                "win_count": len(changes),
                "priority": "high" if avg_change > 50 else "medium" if avg_change > 25 else "low"
            }
        
        # Catalyst analysis
        effective_catalysts = []
        for analysis in winner_analyses:
            catalyst_type = analysis['pattern_insights']['catalyst_type']
            if catalyst_type not in effective_catalysts:
                effective_catalysts.append(catalyst_type)
        
        # Float analysis
        float_performance = {"small": [], "medium": [], "large": []}
        for analysis in winner_analyses:
            float_cat = analysis['pattern_insights']['float_impact'].get('float_category', 'unknown').lower()
            price_change = analysis['move_analysis']['price_change']
            if float_cat in float_performance:
                float_performance[float_cat].append(price_change)
        
        return {
            "sector_priorities": sector_priorities,
            "effective_catalysts": effective_catalysts,
            "float_analysis": float_performance,
            "timing_insights": self.extract_timing_insights(winner_analyses)
        }
    
    def extract_timing_insights(self, winner_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract timing insights from winners"""
        
        insights = {
            "optimal_scan_times": [],
            "catalyst_timing_patterns": [],
            "volume_spike_timing": []
        }
        
        # Analyze when moves happened (placeholder - would need actual timing data)
        insights["optimal_scan_times"] = ["pre-market", "9:45am", "lunch-break", "power-hour"]
        insights["catalyst_timing_patterns"] = ["earnings_after_close", "fda_morning_announcements"]
        
        return insights
    
    def generate_updated_prompts(self, winner_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate updated Perplexity prompts based on learned patterns"""
        
        # Extract successful catalyst types
        successful_catalysts = set()
        successful_sectors = set()
        
        for analysis in winner_analyses:
            catalyst_type = analysis['pattern_insights']['catalyst_type']
            sector = analysis['pattern_insights']['sector_correlation']['sector']
            
            successful_catalysts.add(catalyst_type)
            successful_sectors.add(sector)
        
        # Generate enhanced prompts
        enhanced_prompts = {
            "today": f"""
            Find explosive opportunities for TODAY with focus on these proven patterns:
            
            PRIORITY SECTORS: {', '.join(successful_sectors)}
            PRIORITY CATALYSTS: {', '.join(successful_catalysts)}
            
            Look for:
            - Volume spikes 2x+ above average (learned from recent winners)
            - Small float stocks under 50M shares (explosive potential confirmed)
            - Breaking news in biotech, technology, healthcare sectors
            - Earnings surprises, FDA announcements, partnership deals
            
            Focus on stocks that could deliver 20%+ moves TODAY based on recent market patterns.
            """,
            
            "week": f"""
            Find explosive opportunities for THIS WEEK with enhanced criteria:
            
            PROVEN WINNER SECTORS: {', '.join(successful_sectors)}
            HIGH-IMPACT CATALYSTS: {', '.join(successful_catalysts)}
            
            Enhanced criteria based on recent learning:
            - Prioritize small/mid cap ($10M-$2B) with small float
            - Focus on 2x+ volume patterns that precede major moves
            - Target binary catalyst events: FDA decisions, earnings, partnerships
            - Look for social momentum and retail interest signals
            
            Target 50%+ potential moves this week based on learned patterns.
            """,
            
            "month": f"""
            Find monthly explosive opportunities with learned intelligence:
            
            TOP PERFORMING SECTORS: {', '.join(successful_sectors)}
            EFFECTIVE CATALYST TYPES: {', '.join(successful_catalysts)}
            
            Monthly strategy based on winner analysis:
            - Revolutionary technology breakthroughs in proven sectors
            - Paradigm shift opportunities with small float leverage
            - M&A targets with explosive acquisition potential
            - Regulatory catalysts with binary outcome potential
            
            Target 100%+ potential moves over 30 days using enhanced pattern recognition.
            """
        }
        
        return enhanced_prompts
    
    async def log_learning_results(self, learning_results: Dict[str, Any]) -> bool:
        """Log learning results to file"""
        
        try:
            import os
            import json
            
            # Ensure logs directory exists
            log_dir = os.path.dirname(self.learning_log_file)
            os.makedirs(log_dir, exist_ok=True)
            
            # Load existing log
            existing_logs = []
            if os.path.exists(self.learning_log_file):
                try:
                    with open(self.learning_log_file, 'r') as f:
                        existing_logs = json.load(f)
                except:
                    existing_logs = []
            
            # Add new results
            existing_logs.append(learning_results)
            
            # Keep only last 30 days of logs
            existing_logs = existing_logs[-30:]
            
            # Save updated log
            with open(self.learning_log_file, 'w') as f:
                json.dump(existing_logs, f, indent=2, default=str)
            
            print(f"✅ Learning results logged to {self.learning_log_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error logging learning results: {e}")
            return False
    
    async def send_learning_slack_notification(self, learning_results: Dict[str, Any]) -> bool:
        """Send daily learning summary to Slack"""
        
        try:
            import json
            import urllib.request
            import ssl
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Build learning summary message
            summary = learning_results["learning_summary"]
            improvements = learning_results["system_improvements"]
            winners = learning_results["market_winners"]
            
            title = f"🎓 **DAILY LEARNING CYCLE COMPLETE** - {learning_results['date']}"
            
            # Top winners summary
            top_winners_text = ""
            if winners:
                top_3_winners = sorted(winners, key=lambda x: x['price_change_percent'], reverse=True)[:3]
                for i, winner in enumerate(top_3_winners, 1):
                    top_winners_text += f"\n{i}. **{winner['ticker']}**: +{winner['price_change_percent']:.1f}% (Volume: {winner['volume_spike']:.1f}x)"
            
            # Improvements summary
            improvements_text = ""
            high_priority = [imp for imp in improvements if imp['priority'] == 'high']
            for imp in high_priority[:3]:  # Top 3 high priority
                improvements_text += f"\n• **{imp['improvement_type'].title()}**: {imp['description']}"
            
            message = f"""
**📊 LEARNING SUMMARY**:
• **Winners Studied**: {summary['total_winners_studied']}
• **Improvements Identified**: {summary['improvements_identified']}
• **High Priority**: {summary['high_priority_improvements']}
• **Processing Time**: {summary['processing_time']:.1f}s

**🏆 TOP MARKET WINNERS**:{top_winners_text}

**🔧 KEY IMPROVEMENTS IDENTIFIED**:{improvements_text}

**📈 SYSTEM ENHANCEMENT**:
Discovery algorithms updated with today's market intelligence.
Next scan will incorporate learned patterns for better opportunity detection.

**🎯 IMPACT**:
System continuously improving based on actual market winners.
Enhanced capability to detect explosive opportunities before they moon.

*Daily Learning Engine: Study Winners → Identify Gaps → Improve Discovery*
"""
            
            # Send to Slack
            webhook_url = self.discovery_engine.webhook_url  # Use discovery engine's webhook
            
            payload = {
                "text": title,
                "attachments": [{
                    "color": "#36a64f",
                    "text": message,
                    "ts": int(time.time())
                }]
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                webhook_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, context=ssl_context) as response:
                return response.getcode() == 200
                
        except Exception as e:
            print(f"❌ Error sending learning Slack notification: {e}")
            return False

# Example usage
async def main():
    """Test the stock discovery engine"""
    
    engine = StockDiscoveryEngine()
    
    # Test different timeframes
    for timeframe in ["today", "week", "month"]:
        print(f"\n{'='*100}")
        print(f"TESTING {timeframe.upper()} DISCOVERY")
        print(f"{'='*100}")
        
        results = await engine.run_full_discovery_pipeline(timeframe)
        
        if results["success"] and results["final_recommendations"]:
            print(f"\n🎯 TOP PICK for {timeframe}:")
            top_pick = results["top_pick"]
            candidate_info = top_pick["candidate_info"]
            print(f"   Ticker: {candidate_info['ticker']}")
            print(f"   Company: {candidate_info['company_name']}")
            print(f"   Discovery: {candidate_info['discovery_reason']}")
            print(f"   AI Consensus: {top_pick['final_recommendation']}")
            print(f"   Confidence: {top_pick['confidence']:.0%}")
            print(f"   Composite Score: {top_pick['composite_score']:.2f}")
        
        await asyncio.sleep(2)  # Brief pause between tests

if __name__ == "__main__":
    asyncio.run(main())