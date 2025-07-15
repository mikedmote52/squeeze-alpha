#!/usr/bin/env python3
"""
Explosive Catalyst Discovery Engine
Focuses specifically on small/mid-cap stocks with catalyst-driven explosive potential
NO LARGE-CAP SAFE STOCKS
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio

class ExplosiveCatalystDiscovery:
    """Discovers explosive catalyst opportunities, avoiding large-cap safe stocks"""
    
    def __init__(self):
        # Large-cap stocks to AVOID (market cap > $100B typically)
        self.avoid_large_caps = {
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META',
            'BRK.A', 'BRK.B', 'TSM', 'LLY', 'V', 'UNH', 'JNJ', 'WMT',
            'XOM', 'JPM', 'PG', 'MA', 'HD', 'ORCL', 'COST', 'ABBV',
            'BAC', 'AVGO', 'KO', 'CRM', 'MRK', 'CVX', 'TMO', 'ACN',
            'ADBE', 'LIN', 'MCD', 'ABT', 'CSCO', 'NFLX', 'WFC', 'NKE',
            'DIS', 'QCOM', 'VZ', 'DHR', 'PM', 'TXN', 'AMGN', 'BMY',
            'NEE', 'RTX', 'UNP', 'PFE', 'LOW', 'COP', 'T', 'SPGI'
        }
        
        # Focus sectors for explosive catalyst plays
        self.catalyst_sectors = {
            'biotech': ['small_cap_biotech', 'clinical_trials', 'fda_approvals'],
            'energy': ['oil_exploration', 'renewable_energy', 'battery_tech'],
            'technology': ['ai_software', 'cybersecurity', 'semiconductors'],
            'gaming': ['mobile_gaming', 'esports', 'vr_ar'],
            'fintech': ['crypto_exposure', 'payment_processing', 'lending'],
            'healthcare': ['medical_devices', 'telehealth', 'drug_discovery']
        }
    
    async def discover_explosive_opportunities(self) -> List[Dict[str, Any]]:
        """Discover explosive catalyst opportunities"""
        
        opportunities = []
        
        # 1. Biotech catalyst opportunities (FDA approvals, clinical trials)
        biotech_opps = await self.find_biotech_catalysts()
        opportunities.extend(biotech_opps)
        
        # 2. Earnings surprise candidates (small-cap only)
        earnings_opps = await self.find_earnings_catalysts()
        opportunities.extend(earnings_opps)
        
        # 3. Short squeeze candidates
        squeeze_opps = await self.find_short_squeeze_opportunities()
        opportunities.extend(squeeze_opps)
        
        # 4. Acquisition targets
        acquisition_opps = await self.find_acquisition_targets()
        opportunities.extend(acquisition_opps)
        
        # 5. Technology breakthrough candidates
        tech_opps = await self.find_tech_breakthrough_opportunities()
        opportunities.extend(tech_opps)
        
        # Filter out large-caps and return top opportunities
        filtered_opportunities = self.filter_explosive_opportunities(opportunities)
        
        return filtered_opportunities[:10]  # Top 10 explosive opportunities
    
    async def find_biotech_catalysts(self) -> List[Dict[str, Any]]:
        """Find biotech stocks with upcoming catalysts"""
        biotech_candidates = []
        
        # Small-cap biotech tickers known for catalyst events
        biotech_tickers = [
            'SAVA', 'BIIB', 'GILD', 'REGN', 'VRTX', 'IONS', 'SRPT', 'BMRN',
            'ACAD', 'HALO', 'SAGE', 'FOLD', 'ARVN', 'BEAM', 'EDIT', 'NTLA',
            'CRSP', 'PACB', 'ILMN', 'VEEV', 'DXCM', 'TDOC', 'PTON', 'ROKU',
            'NVAX', 'MRNA', 'BNTX', 'VAXX', 'INO', 'OCGN', 'CYDY', 'ATOS'
        ]
        
        for ticker in biotech_tickers:
            try:
                # Skip if it's a large-cap stock we want to avoid
                if ticker in self.avoid_large_caps:
                    continue
                    
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="5d")
                
                # Check if it's actually small/mid-cap (< $50B market cap)
                market_cap = info.get('marketCap', 0)
                if market_cap > 50_000_000_000:  # Skip if > $50B market cap
                    continue
                
                if not hist.empty and market_cap > 100_000_000:  # > $100M minimum
                    # Calculate volatility (indicator of catalyst potential)
                    high = hist['High'].max()
                    low = hist['Low'].min()
                    current = hist['Close'].iloc[-1]
                    volatility = (high - low) / current
                    
                    # Look for high volatility indicating potential catalysts
                    if volatility > 0.15:  # >15% range indicates catalyst activity
                        biotech_candidates.append({
                            'ticker': ticker,
                            'company_name': info.get('longName', ticker),
                            'sector': 'Biotechnology',
                            'market_cap': market_cap,
                            'current_price': float(current),
                            'catalyst_type': 'Biotech Catalyst',
                            'volatility': volatility,
                            'opportunity_score': min(volatility * 100, 95)  # Cap at 95%
                        })
                        
            except Exception as e:
                continue
        
        return biotech_candidates
    
    async def find_earnings_catalysts(self) -> List[Dict[str, Any]]:
        """Find small-cap stocks with earnings surprise potential"""
        earnings_candidates = []
        
        # Small-cap growth stocks that could have earnings surprises
        growth_tickers = [
            'PLTR', 'SNOW', 'NET', 'CRWD', 'ZS', 'OKTA', 'DDOG', 'ESTC',
            'FSLY', 'CFLT', 'S', 'ZM', 'ASAN', 'MNDY', 'GTLB',
            'COIN', 'HOOD', 'SOFI', 'PYPL', 'AFRM', 'UPST', 'LC',
            'RBLX', 'U', 'PINS', 'SNAP', 'SPOT', 'NFLX', 'DIS'
        ]
        
        for ticker in growth_tickers:
            try:
                # Skip large-caps
                if ticker in self.avoid_large_caps:
                    continue
                    
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="10d")
                
                market_cap = info.get('marketCap', 0)
                if market_cap > 50_000_000_000:  # Skip if > $50B
                    continue
                
                if not hist.empty and market_cap > 500_000_000:  # > $500M minimum
                    # Check for unusual volume (earnings anticipation)
                    current_volume = hist['Volume'].iloc[-1]
                    avg_volume = hist['Volume'].mean()
                    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                    
                    # Look for volume spikes indicating earnings anticipation
                    if volume_ratio > 1.5:  # 50% volume increase
                        earnings_candidates.append({
                            'ticker': ticker,
                            'company_name': info.get('longName', ticker),
                            'sector': info.get('sector', 'Technology'),
                            'market_cap': market_cap,
                            'current_price': float(hist['Close'].iloc[-1]),
                            'catalyst_type': 'Earnings Surprise',
                            'volume_ratio': volume_ratio,
                            'opportunity_score': min(volume_ratio * 30, 85)  # Cap at 85%
                        })
                        
            except Exception as e:
                continue
        
        return earnings_candidates
    
    async def find_short_squeeze_opportunities(self) -> List[Dict[str, Any]]:
        """Find stocks with short squeeze potential"""
        squeeze_candidates = []
        
        # Stocks known for high short interest and squeeze potential
        squeeze_tickers = [
            'GME', 'AMC', 'CLOV', 'WISH', 'CLNE', 'WKHS',
            'SPCE', 'LCID', 'RIVN', 'NIO', 'XPEV', 'LI', 'NKLA', 'GOEV',
            'OPAD', 'GREE', 'ATER', 'LGVN', 'RELI'
        ]
        
        for ticker in squeeze_tickers:
            try:
                # Skip large-caps
                if ticker in self.avoid_large_caps:
                    continue
                    
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="5d")
                
                market_cap = info.get('marketCap', 0)
                if market_cap > 20_000_000_000:  # Skip if > $20B for squeeze plays
                    continue
                
                if not hist.empty and market_cap > 50_000_000:  # > $50M minimum
                    # Get short ratio and float data if available
                    short_ratio = info.get('shortRatio', 0)
                    float_shares = info.get('floatShares', info.get('sharesOutstanding', 0))
                    
                    # Calculate price momentum
                    if len(hist) >= 2:
                        price_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]
                        volume_spike = hist['Volume'].iloc[-1] / hist['Volume'].mean() if hist['Volume'].mean() > 0 else 1
                        
                        # Look for short squeeze indicators
                        squeeze_score = 0
                        if short_ratio > 5:  # High short ratio
                            squeeze_score += 30
                        if volume_spike > 2:  # Volume spike
                            squeeze_score += 25
                        if price_change > 0.05:  # Price momentum
                            squeeze_score += 20
                        if float_shares < 50_000_000:  # Small float
                            squeeze_score += 25
                        
                        if squeeze_score > 40:  # Minimum threshold
                            squeeze_candidates.append({
                                'ticker': ticker,
                                'company_name': info.get('longName', ticker),
                                'sector': info.get('sector', 'Various'),
                                'market_cap': market_cap,
                                'current_price': float(hist['Close'].iloc[-1]),
                                'catalyst_type': 'Short Squeeze',
                                'short_ratio': short_ratio,
                                'opportunity_score': min(squeeze_score, 90)
                            })
                            
            except Exception as e:
                continue
        
        return squeeze_candidates
    
    async def find_acquisition_targets(self) -> List[Dict[str, Any]]:
        """Find potential acquisition targets"""
        acquisition_candidates = []
        
        # Small-cap stocks that could be acquisition targets
        target_tickers = [
            'PINS', 'SNAP', 'UBER', 'LYFT', 'DASH', 'ABNB',
            'ROKU', 'FUBO', 'PARA', 'WBD', 'NFLX',
            'SPOT', 'SKLZ', 'DKNG', 'PENN', 'MGM', 'WYNN', 'LVS', 'BYD'
        ]
        
        for ticker in target_tickers:
            try:
                # Skip large-caps
                if ticker in self.avoid_large_caps:
                    continue
                    
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="30d")
                
                market_cap = info.get('marketCap', 0)
                if market_cap > 30_000_000_000:  # Skip if > $30B
                    continue
                
                if not hist.empty and market_cap > 1_000_000_000:  # > $1B minimum
                    # Check for unusual activity (acquisition rumors)
                    current_volume = hist['Volume'].iloc[-1]
                    avg_volume = hist['Volume'].mean()
                    
                    # Look for value metrics that make it attractive for acquisition
                    pe_ratio = info.get('trailingPE', 0)
                    price_to_book = info.get('priceToBook', 0)
                    
                    acquisition_score = 0
                    if 0 < pe_ratio < 20:  # Reasonable valuation
                        acquisition_score += 20
                    if 0 < price_to_book < 3:  # Not overvalued
                        acquisition_score += 15
                    if current_volume > avg_volume * 1.3:  # Volume increase
                        acquisition_score += 25
                    if market_cap < 10_000_000_000:  # Digestible size
                        acquisition_score += 20
                    
                    if acquisition_score > 35:
                        acquisition_candidates.append({
                            'ticker': ticker,
                            'company_name': info.get('longName', ticker),
                            'sector': info.get('sector', 'Technology'),
                            'market_cap': market_cap,
                            'current_price': float(hist['Close'].iloc[-1]),
                            'catalyst_type': 'Acquisition Target',
                            'pe_ratio': pe_ratio,
                            'opportunity_score': min(acquisition_score, 85)
                        })
                        
            except Exception as e:
                continue
        
        return acquisition_candidates
    
    async def find_tech_breakthrough_opportunities(self) -> List[Dict[str, Any]]:
        """Find technology breakthrough opportunities"""
        tech_candidates = []
        
        # Small-cap tech stocks with breakthrough potential
        tech_tickers = [
            'PLTR', 'SNOW', 'AI', 'PATH', 'SOUN', 'BBAI', 'GFAI', 'AITX',
            'IONQ', 'RGTI', 'QUBT', 'ARQQ', 'IBM', 'GOOGL', 'MSFT', 'NVDA',
            'SMCI', 'CORZ', 'RIOT', 'MARA', 'HUT', 'BITF', 'COIN', 'HOOD'
        ]
        
        for ticker in tech_tickers:
            try:
                # Skip large-caps
                if ticker in self.avoid_large_caps:
                    continue
                    
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="10d")
                
                market_cap = info.get('marketCap', 0)
                if market_cap > 25_000_000_000:  # Skip if > $25B
                    continue
                
                if not hist.empty and market_cap > 200_000_000:  # > $200M minimum
                    # Check for technology sector exposure
                    sector = info.get('sector', '').lower()
                    industry = info.get('industry', '').lower()
                    
                    tech_keywords = ['technology', 'software', 'artificial', 'intelligence', 
                                   'quantum', 'blockchain', 'crypto', 'cybersecurity']
                    
                    has_tech_exposure = any(keyword in sector or keyword in industry 
                                          for keyword in tech_keywords)
                    
                    if has_tech_exposure:
                        # Calculate momentum and volatility
                        if len(hist) >= 5:
                            recent_return = (hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]
                            volatility = hist['Close'].std() / hist['Close'].mean()
                            
                            tech_score = 0
                            if recent_return > 0.1:  # 10% recent gain
                                tech_score += 25
                            if volatility > 0.05:  # High volatility
                                tech_score += 20
                            if market_cap < 5_000_000_000:  # Small enough for explosive growth
                                tech_score += 30
                            
                            if tech_score > 40:
                                tech_candidates.append({
                                    'ticker': ticker,
                                    'company_name': info.get('longName', ticker),
                                    'sector': info.get('sector', 'Technology'),
                                    'market_cap': market_cap,
                                    'current_price': float(hist['Close'].iloc[-1]),
                                    'catalyst_type': 'Tech Breakthrough',
                                    'recent_return': recent_return,
                                    'opportunity_score': min(tech_score, 85)
                                })
                                
            except Exception as e:
                continue
        
        return tech_candidates
    
    def filter_explosive_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and rank explosive opportunities"""
        
        # Remove any large-cap stocks that slipped through
        filtered = []
        for opp in opportunities:
            ticker = opp['ticker']
            market_cap = opp.get('market_cap', 0)
            
            # Skip large-caps
            if ticker in self.avoid_large_caps:
                continue
            
            # Skip if market cap is too large (> $50B for most, > $20B for squeezes)
            max_cap = 20_000_000_000 if opp['catalyst_type'] == 'Short Squeeze' else 50_000_000_000
            if market_cap > max_cap:
                continue
            
            # Only include opportunities with good scores
            if opp.get('opportunity_score', 0) > 40:
                filtered.append(opp)
        
        # Sort by opportunity score
        filtered.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
        
        return filtered

async def main():
    """Test the explosive catalyst discovery"""
    discovery = ExplosiveCatalystDiscovery()
    opportunities = await discovery.discover_explosive_opportunities()
    
    print("🚀 EXPLOSIVE CATALYST OPPORTUNITIES (NO LARGE-CAPS)")
    print("=" * 60)
    
    for i, opp in enumerate(opportunities, 1):
        print(f"\n{i}. {opp['ticker']} - {opp['company_name']}")
        print(f"   Catalyst: {opp['catalyst_type']}")
        print(f"   Market Cap: ${opp['market_cap']:,.0f}")
        print(f"   Price: ${opp['current_price']:.2f}")
        print(f"   Opportunity Score: {opp['opportunity_score']:.0f}%")

if __name__ == "__main__":
    asyncio.run(main())