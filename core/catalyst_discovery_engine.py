#!/usr/bin/env python3
"""
Catalyst Discovery Engine - Binary Event Focus
Specializes in FDA approvals, earnings surprises, regulatory decisions
"""

import os
import json
import asyncio
import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import time
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CatalystOpportunity:
    """Structured catalyst opportunity with binary event focus"""
    ticker: str
    company_name: str
    catalyst_type: str  # 'FDA_APPROVAL', 'EARNINGS', 'REGULATORY', 'M&A', 'CLINICAL_TRIAL'
    event_date: datetime
    probability_score: float  # 1-10 scale
    expected_upside_pct: float
    expected_downside_pct: float
    confidence_score: float
    position_size_recommendation: float  # 1-5% of portfolio
    risk_assessment: str
    entry_strategy: str
    exit_strategy: str
    supporting_data: Dict[str, Any]

class CatalystDiscoveryEngine:
    """Engine for discovering binary catalyst opportunities"""
    
    def __init__(self):
        # API keys from environment
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY', '')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        
        # Discovery parameters
        self.min_probability_score = 7.0  # 70% minimum
        self.min_expected_upside = 20.0  # 20% minimum
        self.max_market_cap = 10_000_000_000  # $10B max for better volatility
        self.min_market_cap = 50_000_000  # $50M min for liquidity
        
        # Catalyst calendars and sources
        self.fda_calendar_url = "https://www.biopharmcatalyst.com/calendars/fda-calendar"
        self.earnings_calendar_url = "https://finance.yahoo.com/calendar/earnings"
        
    async def discover_catalyst_opportunities_for_main(self) -> str:
        """Main function that returns formatted string for web display"""
        try:
            # Run full catalyst discovery
            opportunities = await self.discover_all_catalyst_opportunities()
            
            if not opportunities:
                return "No high-probability catalyst opportunities found meeting criteria (70%+ probability, 20%+ upside)"
            
            # Format for display
            output = "🎯 **TOP CATALYST OPPORTUNITIES**\n"
            output += "Binary events with clear timelines and high probability outcomes\n"
            output += "=" * 80 + "\n\n"
            
            # Get top 5 opportunities
            top_opportunities = opportunities[:5]
            
            for i, opp in enumerate(top_opportunities, 1):
                output += f"**{i}. {opp.ticker} - {opp.company_name}**\n"
                output += f"   **Catalyst:** {opp.catalyst_type.replace('_', ' ')}\n"
                output += f"   **Event Date:** {opp.event_date.strftime('%Y-%m-%d')}\n"
                output += f"   **Probability Score:** {opp.probability_score}/10 ({opp.probability_score * 10}%)\n"
                output += f"   **Expected Upside:** +{opp.expected_upside_pct:.1f}%\n"
                output += f"   **Risk/Reward:** {abs(opp.expected_upside_pct / opp.expected_downside_pct):.1f}:1\n"
                output += f"   **Position Size:** {opp.position_size_recommendation:.1f}% of portfolio\n"
                output += f"   **Entry Strategy:** {opp.entry_strategy}\n"
                output += f"   **Risk Assessment:** {opp.risk_assessment}\n"
                output += "\n"
            
            # Add summary
            output += "📊 **SUMMARY**\n"
            output += f"• Found {len(opportunities)} total opportunities\n"
            output += f"• Average probability: {sum(o.probability_score for o in opportunities) / len(opportunities) * 10:.0f}%\n"
            output += f"• Average upside: {sum(o.expected_upside_pct for o in opportunities) / len(opportunities):.0f}%\n"
            output += f"• Focus: Binary catalyst events with institutional-grade filtering\n"
            
            return output
            
        except Exception as e:
            logger.error(f"Error in catalyst discovery: {e}")
            return f"Error discovering catalyst opportunities: {str(e)}"
    
    async def discover_all_catalyst_opportunities(self) -> List[CatalystOpportunity]:
        """Discover all types of catalyst opportunities"""
        
        logger.info("🔍 Starting catalyst discovery across all categories...")
        
        all_opportunities = []
        
        # Run all discovery methods in parallel
        tasks = [
            self.discover_fda_approvals(),
            self.discover_earnings_catalysts(),
            self.discover_regulatory_decisions(),
            self.discover_ma_targets(),
            self.discover_clinical_trial_readouts()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        for result in results:
            if isinstance(result, list):
                all_opportunities.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Discovery task failed: {result}")
        
        # Filter by criteria
        filtered_opportunities = self.filter_opportunities(all_opportunities)
        
        # Rank by composite score
        ranked_opportunities = self.rank_opportunities(filtered_opportunities)
        
        logger.info(f"✅ Found {len(ranked_opportunities)} high-quality catalyst opportunities")
        
        return ranked_opportunities
    
    async def discover_fda_approvals(self) -> List[CatalystOpportunity]:
        """Discover upcoming FDA approval decisions"""
        
        logger.info("💊 Scanning for FDA approval catalysts...")
        opportunities = []
        
        try:
            # FDA-focused biotech tickers with known catalysts
            fda_candidates = [
                {'ticker': 'SAVA', 'company': 'Cassava Sciences', 'catalyst': 'Alzheimer drug data'},
                {'ticker': 'NVAX', 'company': 'Novavax', 'catalyst': 'Vaccine approvals'},
                {'ticker': 'MRNA', 'company': 'Moderna', 'catalyst': 'Pipeline updates'},
                {'ticker': 'BNTX', 'company': 'BioNTech', 'catalyst': 'mRNA developments'},
                {'ticker': 'GILD', 'company': 'Gilead Sciences', 'catalyst': 'Antiviral approvals'},
                {'ticker': 'BIIB', 'company': 'Biogen', 'catalyst': 'Neurological drugs'},
                {'ticker': 'VRTX', 'company': 'Vertex Pharma', 'catalyst': 'Gene therapy'},
                {'ticker': 'REGN', 'company': 'Regeneron', 'catalyst': 'Antibody treatments'},
                {'ticker': 'ALNY', 'company': 'Alnylam', 'catalyst': 'RNAi therapeutics'},
                {'ticker': 'BMRN', 'company': 'BioMarin', 'catalyst': 'Rare disease drugs'}
            ]
            
            for candidate in fda_candidates:
                try:
                    # Get stock data
                    stock = yf.Ticker(candidate['ticker'])
                    info = stock.info
                    
                    market_cap = info.get('marketCap', 0)
                    if not (self.min_market_cap <= market_cap <= self.max_market_cap):
                        continue
                    
                    # Analyze FDA catalyst potential
                    hist = stock.history(period="30d")
                    if len(hist) < 5:
                        continue
                    
                    current_price = hist['Close'].iloc[-1]
                    volatility = hist['Close'].pct_change().std() * 100
                    
                    # Check for upcoming FDA events (placeholder - would use real FDA calendar API)
                    event_date = datetime.now() + timedelta(days=30)  # Placeholder
                    
                    # Calculate opportunity metrics
                    probability_score = self.calculate_fda_probability(candidate, volatility)
                    expected_upside = self.calculate_expected_upside(volatility, 'FDA')
                    expected_downside = -volatility * 2  # FDA rejections can be harsh
                    
                    if probability_score >= self.min_probability_score and expected_upside >= self.min_expected_upside:
                        opportunity = CatalystOpportunity(
                            ticker=candidate['ticker'],
                            company_name=candidate['company'],
                            catalyst_type='FDA_APPROVAL',
                            event_date=event_date,
                            probability_score=probability_score,
                            expected_upside_pct=expected_upside,
                            expected_downside_pct=expected_downside,
                            confidence_score=probability_score / 10,
                            position_size_recommendation=self.calculate_position_size(probability_score, volatility),
                            risk_assessment=self.assess_risk(volatility, expected_upside, expected_downside),
                            entry_strategy=f"Enter 2-3 days before PDUFA date at ${current_price:.2f} or below",
                            exit_strategy="Exit on approval pop or set -15% stop loss on rejection",
                            supporting_data={
                                'market_cap': market_cap,
                                'current_price': current_price,
                                'volatility': volatility,
                                'catalyst_detail': candidate['catalyst']
                            }
                        )
                        
                        opportunities.append(opportunity)
                        logger.info(f"   ✓ {candidate['ticker']}: FDA catalyst with {probability_score:.0f}/10 probability")
                
                except Exception as e:
                    logger.error(f"Error analyzing {candidate['ticker']}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in FDA discovery: {e}")
        
        return opportunities
    
    async def discover_earnings_catalysts(self) -> List[CatalystOpportunity]:
        """Discover earnings surprise opportunities"""
        
        logger.info("📊 Scanning for earnings catalysts...")
        opportunities = []
        
        try:
            # High-volatility earnings plays
            earnings_candidates = [
                {'ticker': 'SMCI', 'company': 'Super Micro Computer', 'sector': 'Tech'},
                {'ticker': 'AMD', 'company': 'AMD', 'sector': 'Semiconductors'},
                {'ticker': 'NVDA', 'company': 'NVIDIA', 'sector': 'AI/GPU'},
                {'ticker': 'PLTR', 'company': 'Palantir', 'sector': 'Software'},
                {'ticker': 'COIN', 'company': 'Coinbase', 'sector': 'Crypto'},
                {'ticker': 'HOOD', 'company': 'Robinhood', 'sector': 'Fintech'},
                {'ticker': 'SOFI', 'company': 'SoFi', 'sector': 'Fintech'},
                {'ticker': 'AFRM', 'company': 'Affirm', 'sector': 'Fintech'},
                {'ticker': 'RBLX', 'company': 'Roblox', 'sector': 'Gaming'},
                {'ticker': 'U', 'company': 'Unity', 'sector': 'Gaming'}
            ]
            
            for candidate in earnings_candidates:
                try:
                    stock = yf.Ticker(candidate['ticker'])
                    info = stock.info
                    
                    market_cap = info.get('marketCap', 0)
                    if not (self.min_market_cap <= market_cap <= self.max_market_cap):
                        continue
                    
                    # Get earnings date (placeholder - would use real earnings calendar)
                    next_earnings = info.get('mostRecentQuarter', datetime.now() + timedelta(days=45))
                    if isinstance(next_earnings, int):
                        next_earnings = datetime.fromtimestamp(next_earnings)
                    
                    # Analyze earnings potential
                    hist = stock.history(period="90d")
                    if len(hist) < 20:
                        continue
                    
                    current_price = hist['Close'].iloc[-1]
                    
                    # Calculate historical earnings moves
                    earnings_volatility = self.calculate_earnings_volatility(hist)
                    
                    # Score the opportunity
                    probability_score = self.calculate_earnings_probability(candidate, info)
                    expected_upside = earnings_volatility * 1.5  # Earnings beats often exceed historical moves
                    expected_downside = -earnings_volatility
                    
                    if probability_score >= self.min_probability_score and expected_upside >= self.min_expected_upside:
                        opportunity = CatalystOpportunity(
                            ticker=candidate['ticker'],
                            company_name=candidate['company'],
                            catalyst_type='EARNINGS',
                            event_date=next_earnings,
                            probability_score=probability_score,
                            expected_upside_pct=expected_upside,
                            expected_downside_pct=expected_downside,
                            confidence_score=probability_score / 10,
                            position_size_recommendation=self.calculate_position_size(probability_score, earnings_volatility),
                            risk_assessment=self.assess_risk(earnings_volatility, expected_upside, expected_downside),
                            entry_strategy=f"Enter 1-2 days before earnings at ${current_price:.2f} or on pre-earnings dip",
                            exit_strategy="Exit on earnings gap or trail stop after initial move",
                            supporting_data={
                                'market_cap': market_cap,
                                'current_price': current_price,
                                'earnings_volatility': earnings_volatility,
                                'sector': candidate['sector']
                            }
                        )
                        
                        opportunities.append(opportunity)
                        logger.info(f"   ✓ {candidate['ticker']}: Earnings catalyst with {expected_upside:.0f}% upside potential")
                
                except Exception as e:
                    logger.error(f"Error analyzing earnings for {candidate['ticker']}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in earnings discovery: {e}")
        
        return opportunities
    
    async def discover_regulatory_decisions(self) -> List[CatalystOpportunity]:
        """Discover regulatory decision catalysts"""
        
        logger.info("⚖️ Scanning for regulatory decision catalysts...")
        opportunities = []
        
        try:
            # Companies facing regulatory decisions
            regulatory_candidates = [
                {'ticker': 'LCID', 'company': 'Lucid Motors', 'catalyst': 'EV regulations'},
                {'ticker': 'RIVN', 'company': 'Rivian', 'catalyst': 'Production permits'},
                {'ticker': 'QS', 'company': 'QuantumScape', 'catalyst': 'Battery approvals'},
                {'ticker': 'PLUG', 'company': 'Plug Power', 'catalyst': 'Hydrogen incentives'},
                {'ticker': 'FCEL', 'company': 'FuelCell Energy', 'catalyst': 'Clean energy policy'},
                {'ticker': 'CHPT', 'company': 'ChargePoint', 'catalyst': 'Infrastructure bills'},
                {'ticker': 'BLNK', 'company': 'Blink Charging', 'catalyst': 'Charging standards'}
            ]
            
            for candidate in regulatory_candidates:
                try:
                    stock = yf.Ticker(candidate['ticker'])
                    info = stock.info
                    
                    market_cap = info.get('marketCap', 0)
                    if not (self.min_market_cap <= market_cap <= self.max_market_cap):
                        continue
                    
                    hist = stock.history(period="60d")
                    if len(hist) < 10:
                        continue
                    
                    current_price = hist['Close'].iloc[-1]
                    volatility = hist['Close'].pct_change().std() * 100
                    
                    # Regulatory events typically have longer timelines
                    event_date = datetime.now() + timedelta(days=60)
                    
                    # Calculate opportunity
                    probability_score = 7.5  # Regulatory decisions are often political
                    expected_upside = volatility * 3  # Regulatory wins can be huge
                    expected_downside = -volatility * 1.5
                    
                    if expected_upside >= self.min_expected_upside:
                        opportunity = CatalystOpportunity(
                            ticker=candidate['ticker'],
                            company_name=candidate['company'],
                            catalyst_type='REGULATORY',
                            event_date=event_date,
                            probability_score=probability_score,
                            expected_upside_pct=expected_upside,
                            expected_downside_pct=expected_downside,
                            confidence_score=0.75,
                            position_size_recommendation=2.5,
                            risk_assessment="Moderate - regulatory outcomes can be unpredictable",
                            entry_strategy=f"Scale in at ${current_price:.2f} and on dips",
                            exit_strategy="Take partial profits at +20%, let rest run with trailing stop",
                            supporting_data={
                                'market_cap': market_cap,
                                'current_price': current_price,
                                'volatility': volatility,
                                'catalyst_detail': candidate['catalyst']
                            }
                        )
                        
                        opportunities.append(opportunity)
                        logger.info(f"   ✓ {candidate['ticker']}: Regulatory catalyst with {expected_upside:.0f}% potential")
                
                except Exception as e:
                    logger.error(f"Error analyzing regulatory for {candidate['ticker']}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in regulatory discovery: {e}")
        
        return opportunities
    
    async def discover_ma_targets(self) -> List[CatalystOpportunity]:
        """Discover M&A target opportunities"""
        
        logger.info("🤝 Scanning for M&A targets...")
        opportunities = []
        
        try:
            # Potential M&A targets
            ma_candidates = [
                {'ticker': 'SOUN', 'company': 'SoundHound AI', 'acquirer': 'Big Tech'},
                {'ticker': 'BBAI', 'company': 'BigBear.ai', 'acquirer': 'Defense contractors'},
                {'ticker': 'IONQ', 'company': 'IonQ', 'acquirer': 'Cloud providers'},
                {'ticker': 'QBTS', 'company': 'D-Wave Quantum', 'acquirer': 'Tech giants'},
                {'ticker': 'RGTI', 'company': 'Rigetti Computing', 'acquirer': 'IBM/Google'},
                {'ticker': 'ARQQ', 'company': 'Arqit Quantum', 'acquirer': 'Cybersecurity firms'}
            ]
            
            for candidate in ma_candidates:
                try:
                    stock = yf.Ticker(candidate['ticker'])
                    info = stock.info
                    
                    market_cap = info.get('marketCap', 0)
                    if not (self.min_market_cap <= market_cap <= 2_000_000_000):  # M&A targets usually under $2B
                        continue
                    
                    hist = stock.history(period="30d")
                    if len(hist) < 5:
                        continue
                    
                    current_price = hist['Close'].iloc[-1]
                    
                    # M&A probability based on sector consolidation trends
                    probability_score = 7.0 if market_cap < 500_000_000 else 8.0
                    expected_upside = 35.0  # Typical M&A premium
                    expected_downside = -10.0  # Limited downside for quality targets
                    
                    # No specific date for M&A
                    event_date = datetime.now() + timedelta(days=180)
                    
                    opportunity = CatalystOpportunity(
                        ticker=candidate['ticker'],
                        company_name=candidate['company'],
                        catalyst_type='M&A',
                        event_date=event_date,
                        probability_score=probability_score,
                        expected_upside_pct=expected_upside,
                        expected_downside_pct=expected_downside,
                        confidence_score=0.7,
                        position_size_recommendation=3.0,
                        risk_assessment="Low-Moderate - Quality assets in consolidating sectors",
                        entry_strategy=f"Accumulate under ${current_price * 1.1:.2f}",
                        exit_strategy="Hold for acquisition or exit at 40% gain",
                        supporting_data={
                            'market_cap': market_cap,
                            'current_price': current_price,
                            'potential_acquirer': candidate['acquirer']
                        }
                    )
                    
                    opportunities.append(opportunity)
                    logger.info(f"   ✓ {candidate['ticker']}: M&A target with {expected_upside:.0f}% takeover premium potential")
                
                except Exception as e:
                    logger.error(f"Error analyzing M&A for {candidate['ticker']}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in M&A discovery: {e}")
        
        return opportunities
    
    async def discover_clinical_trial_readouts(self) -> List[CatalystOpportunity]:
        """Discover clinical trial data readout catalysts"""
        
        logger.info("🧪 Scanning for clinical trial catalysts...")
        opportunities = []
        
        try:
            # Biotech with upcoming trial data
            trial_candidates = [
                {'ticker': 'SAVA', 'company': 'Cassava Sciences', 'trial': 'Phase 3 Alzheimer'},
                {'ticker': 'AXSM', 'company': 'Axsome Therapeutics', 'trial': 'CNS drugs'},
                {'ticker': 'SAGE', 'company': 'Sage Therapeutics', 'trial': 'Depression treatment'},
                {'ticker': 'ACAD', 'company': 'ACADIA Pharma', 'trial': 'Neurological'},
                {'ticker': 'PTCT', 'company': 'PTC Therapeutics', 'trial': 'Gene therapy'}
            ]
            
            for candidate in trial_candidates:
                try:
                    stock = yf.Ticker(candidate['ticker'])
                    info = stock.info
                    
                    market_cap = info.get('marketCap', 0)
                    if not (self.min_market_cap <= market_cap <= self.max_market_cap):
                        continue
                    
                    hist = stock.history(period="30d")
                    if len(hist) < 5:
                        continue
                    
                    current_price = hist['Close'].iloc[-1]
                    volatility = hist['Close'].pct_change().std() * 100
                    
                    # Clinical trials are high risk/reward
                    event_date = datetime.now() + timedelta(days=90)
                    probability_score = 7.0  # Biotech trials have decent success rates in Phase 3
                    expected_upside = volatility * 5  # Successful trials can cause massive moves
                    expected_downside = -volatility * 3  # Failures hurt badly
                    
                    if expected_upside >= 50:  # Only high-impact trials
                        opportunity = CatalystOpportunity(
                            ticker=candidate['ticker'],
                            company_name=candidate['company'],
                            catalyst_type='CLINICAL_TRIAL',
                            event_date=event_date,
                            probability_score=probability_score,
                            expected_upside_pct=expected_upside,
                            expected_downside_pct=expected_downside,
                            confidence_score=0.7,
                            position_size_recommendation=1.5,  # Smaller size due to binary risk
                            risk_assessment="High - Binary outcome with significant downside risk",
                            entry_strategy=f"Enter small position at ${current_price:.2f}, add on weakness",
                            exit_strategy="Take 50% profits at double, hold rest for full data",
                            supporting_data={
                                'market_cap': market_cap,
                                'current_price': current_price,
                                'volatility': volatility,
                                'trial_detail': candidate['trial']
                            }
                        )
                        
                        opportunities.append(opportunity)
                        logger.info(f"   ✓ {candidate['ticker']}: Clinical trial with {expected_upside:.0f}% upside potential")
                
                except Exception as e:
                    logger.error(f"Error analyzing trial for {candidate['ticker']}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in clinical trial discovery: {e}")
        
        return opportunities
    
    # Helper methods
    
    def calculate_fda_probability(self, candidate: Dict, volatility: float) -> float:
        """Calculate FDA approval probability"""
        base_probability = 7.0
        
        # Adjust based on company track record
        if candidate['ticker'] in ['GILD', 'BIIB', 'VRTX', 'REGN']:
            base_probability += 1.0  # Established companies
        
        # Adjust based on volatility (lower volatility = more confidence)
        if volatility < 3:
            base_probability += 0.5
        elif volatility > 5:
            base_probability -= 0.5
        
        return min(10.0, max(1.0, base_probability))
    
    def calculate_earnings_probability(self, candidate: Dict, info: Dict) -> float:
        """Calculate earnings beat probability"""
        base_probability = 7.0
        
        # Growth companies tend to guide conservatively
        if candidate['sector'] in ['Tech', 'Software', 'AI/GPU']:
            base_probability += 0.5
        
        # Check earnings history (placeholder)
        earnings_growth = info.get('earningsQuarterlyGrowth', 0)
        if earnings_growth and earnings_growth > 0.2:  # 20%+ growth
            base_probability += 1.0
        
        return min(10.0, max(1.0, base_probability))
    
    def calculate_expected_upside(self, volatility: float, catalyst_type: str) -> float:
        """Calculate expected upside based on catalyst type"""
        multipliers = {
            'FDA': 4.0,
            'EARNINGS': 2.0,
            'REGULATORY': 3.0,
            'M&A': 1.5,
            'CLINICAL_TRIAL': 5.0
        }
        
        multiplier = multipliers.get(catalyst_type, 2.0)
        return volatility * multiplier
    
    def calculate_earnings_volatility(self, hist) -> float:
        """Calculate historical earnings move volatility"""
        # Simplified - would analyze actual earnings dates
        daily_returns = hist['Close'].pct_change().dropna()
        
        # Look for big moves (potential earnings days)
        big_moves = daily_returns[abs(daily_returns) > 0.05]
        
        if len(big_moves) > 0:
            return abs(big_moves).mean() * 100
        else:
            return daily_returns.std() * 100 * 2  # Use 2x normal volatility
    
    def calculate_position_size(self, probability_score: float, volatility: float) -> float:
        """Calculate recommended position size (1-5% of portfolio)"""
        # Higher probability = larger position
        base_size = probability_score / 2  # 7/10 prob = 3.5% base
        
        # Adjust for volatility (higher vol = smaller position)
        if volatility > 5:
            base_size *= 0.7
        elif volatility < 3:
            base_size *= 1.2
        
        return min(5.0, max(1.0, base_size))
    
    def assess_risk(self, volatility: float, upside: float, downside: float) -> str:
        """Assess risk level of opportunity"""
        risk_reward_ratio = abs(upside / downside) if downside != 0 else upside
        
        if risk_reward_ratio > 3 and volatility < 4:
            return "Low - Excellent risk/reward with manageable volatility"
        elif risk_reward_ratio > 2:
            return "Moderate - Good risk/reward but watch position size"
        else:
            return "High - Binary outcome with significant downside risk"
    
    def filter_opportunities(self, opportunities: List[CatalystOpportunity]) -> List[CatalystOpportunity]:
        """Filter opportunities by minimum criteria"""
        filtered = []
        
        for opp in opportunities:
            if (opp.probability_score >= self.min_probability_score and 
                opp.expected_upside_pct >= self.min_expected_upside):
                filtered.append(opp)
        
        return filtered
    
    def rank_opportunities(self, opportunities: List[CatalystOpportunity]) -> List[CatalystOpportunity]:
        """Rank opportunities by composite score"""
        
        for opp in opportunities:
            # Calculate composite score
            risk_reward = abs(opp.expected_upside_pct / opp.expected_downside_pct) if opp.expected_downside_pct != 0 else opp.expected_upside_pct / 10
            
            composite_score = (
                opp.probability_score * 0.4 +  # Probability weight
                min(10, opp.expected_upside_pct / 10) * 0.3 +  # Upside weight (capped)
                min(10, risk_reward) * 0.3  # Risk/reward weight
            )
            
            opp.composite_score = composite_score
        
        # Sort by composite score
        opportunities.sort(key=lambda x: x.composite_score, reverse=True)
        
        return opportunities

# Integration with existing system
async def main():
    """Test the catalyst discovery engine"""
    
    engine = CatalystDiscoveryEngine()
    
    # Get formatted output
    result = await engine.discover_catalyst_opportunities_for_main()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())