#!/usr/bin/env python3
"""
Simple Stock Discovery Engine
Real-time stock opportunities using live market data
"""

import asyncio
import yfinance as yf
from datetime import datetime

class LiveStockCandidate:
    def __init__(self, ticker, company_name, current_price, price_change_1d, volume_spike, discovery_reason, confidence_score):
        self.ticker = ticker
        self.company_name = company_name
        self.current_price = current_price
        self.price_change_1d = price_change_1d
        self.volume_spike = volume_spike
        self.discovery_reason = discovery_reason
        self.confidence_score = confidence_score

class RealTimeStockDiscovery:
    def __init__(self):
        self.min_volume_spike = 2.0
        self.min_price_change = 5.0
    
    async def discover_live_explosive_opportunities(self, timeframe="today"):
        print(f"🔍 REAL-TIME STOCK DISCOVERY - {timeframe.upper()}")
        print("=" * 80)
        print("📊 Scanning live market data for explosive opportunities...")
        
        candidates = []
        
        # Scan popular volatile stocks
        volume_candidates = await self.scan_volume_spikes()
        candidates.extend(volume_candidates)
        
        # Remove duplicates and rank by confidence
        unique_candidates = self.deduplicate_and_rank(candidates)
        
        print(f"✅ Found {len(unique_candidates)} real-time explosive opportunities")
        return unique_candidates[:10]
    
    async def scan_volume_spikes(self):
        print("📈 Scanning for real-time volume spikes...")
        candidates = []
        
        try:
            # Popular active stocks for scanning
            active_stocks = [
                'AMC', 'GME', 'BBBY', 'SNDL', 'SPCE', 'PLTR', 'SOFI', 'LCID',
                'NVDA', 'AMD', 'TSLA', 'NFLX', 'ROKU', 'ZOOM', 'PTON',
                'MRNA', 'BNTX', 'NVAX', 'SAVA', 'OXY', 'DVN', 'CLF'
            ]
            
            for ticker in active_stocks[:20]:  # Limit to prevent timeout
                try:
                    stock = yf.Ticker(ticker)
                    
                    # Get recent trading data
                    hist = stock.history(period="10d", interval="1d")
                    if len(hist) < 5:
                        continue
                    
                    # Calculate volume spike
                    current_volume = hist['Volume'].iloc[-1]
                    avg_volume = hist['Volume'].iloc[:-1].mean()
                    volume_spike = current_volume / avg_volume if avg_volume > 0 else 1
                    
                    # Calculate price changes
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    price_change = ((current_price - prev_price) / prev_price) * 100
                    
                    # Filter for significant activity
                    if volume_spike >= self.min_volume_spike and abs(price_change) >= 3.0:
                        
                        # Get company info
                        info = stock.info
                        company_name = info.get('longName', ticker)
                        
                        candidate = LiveStockCandidate(
                            ticker=ticker,
                            company_name=company_name,
                            current_price=current_price,
                            price_change_1d=price_change,
                            volume_spike=volume_spike,
                            discovery_reason=f"Volume spike {volume_spike:.1f}x normal with {price_change:.1f}% price move",
                            confidence_score=min(0.9, volume_spike / 10)
                        )
                        
                        candidates.append(candidate)
                        print(f"   🎯 {ticker}: {volume_spike:.1f}x volume, {price_change:.1f}% price move")
                        
                        # Limit results
                        if len(candidates) >= 10:
                            break
                    
                    # Brief delay to avoid rate limits
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"   ⚠️ Error scanning {ticker}: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Error in volume spike scan: {e}")
        
        print(f"   📈 Found {len(candidates)} volume spike candidates")
        return candidates
    
    def deduplicate_and_rank(self, candidates):
        # Remove duplicates by ticker
        seen_tickers = set()
        unique_candidates = []
        
        for candidate in candidates:
            if candidate.ticker not in seen_tickers:
                seen_tickers.add(candidate.ticker)
                unique_candidates.append(candidate)
        
        # Sort by confidence score (highest first)
        unique_candidates.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return unique_candidates


if __name__ == "__main__":
    async def test_discovery():
        discovery = RealTimeStockDiscovery()
        candidates = await discovery.discover_live_explosive_opportunities('today')
        
        print(f"\n🎯 TOP REAL-TIME OPPORTUNITIES:")
        for i, candidate in enumerate(candidates[:5], 1):
            print(f"\n{i}. {candidate.ticker} - {candidate.company_name}")
            print(f"   💰 Price: ${candidate.current_price:.2f}")
            print(f"   📈 Change: {candidate.price_change_1d:+.1f}% today")
            print(f"   📊 Volume: {candidate.volume_spike:.1f}x normal")
            print(f"   🎯 Reason: {candidate.discovery_reason}")
            print(f"   ⭐ Confidence: {candidate.confidence_score:.0%}")
    
    asyncio.run(test_discovery())