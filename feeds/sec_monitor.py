#!/usr/bin/env python3
"""
SEC EDGAR Monitor
Monitors real SEC 8-K filings for M&A, partnerships, and material events
"""

import requests
import feedparser
import yfinance as yf
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import re
import sys
import os
import json

# Add schemas to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schemas'))
from catalyst_opportunity import CatalystOpportunity

logger = logging.getLogger(__name__)

class SECMonitor:
    """Monitor SEC EDGAR filings for real catalyst events"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8'
        })
        
        # SEC data sources
        self.edgar_rss_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        self.sec_api_base = "https://data.sec.gov/submissions"
        self.edgar_search_url = "https://efts.sec.gov/LATEST/search-index"
        
        # Form types to monitor
        self.catalyst_forms = {
            '8-K': 'Material events',
            '8-K/A': 'Material events (amended)',
            'SC 13D': 'Beneficial ownership',
            'SC 13G': 'Beneficial ownership',
            '13F-HR': 'Institutional holdings',
            'DEF 14A': 'Proxy statements'
        }
        
        # Catalyst keywords for 8-K items
        self.catalyst_keywords = {
            'M&A': ['merger', 'acquisition', 'purchase agreement', 'definitive agreement', 'tender offer'],
            'PARTNERSHIP': ['strategic alliance', 'partnership', 'collaboration', 'joint venture'],
            'LITIGATION': ['lawsuit', 'settlement', 'litigation', 'legal proceedings'],
            'EXECUTIVE_CHANGE': ['ceo', 'chief executive', 'resignation', 'appointment'],
            'MATERIAL_AGREEMENT': ['material agreement', 'licensing agreement', 'supply agreement']
        }
    
    async def get_sec_catalysts(self) -> List[CatalystOpportunity]:
        """Get real SEC filing catalysts"""
        
        logger.info("🔍 Monitoring SEC EDGAR for real catalysts...")
        
        catalysts = []
        
        # Source 1: Recent 8-K filings via RSS
        rss_catalysts = await self.monitor_edgar_rss()
        catalysts.extend(rss_catalysts)
        
        # Source 2: SEC API for specific tickers
        api_catalysts = await self.check_sec_api()
        catalysts.extend(api_catalysts)
        
        # Source 3: Recent filings search
        search_catalysts = await self.search_recent_filings()
        catalysts.extend(search_catalysts)
        
        # Deduplicate and validate
        unique_catalysts = self.deduplicate_catalysts(catalysts)
        
        logger.info(f"✅ Found {len(unique_catalysts)} real SEC catalysts")
        return unique_catalysts
    
    async def monitor_edgar_rss(self) -> List[CatalystOpportunity]:
        """Monitor EDGAR RSS feeds for recent filings"""
        
        catalysts = []
        
        try:
            logger.info("📡 Monitoring EDGAR RSS feeds...")
            
            # SEC RSS endpoints
            rss_urls = [
                "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=8-K&company=&dateb=&owner=include&start=0&count=40&output=atom",
                "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=SC+13D&company=&dateb=&owner=include&start=0&count=20&output=atom"
            ]
            
            for rss_url in rss_urls:
                try:
                    # Parse RSS feed
                    feed = feedparser.parse(rss_url)
                    
                    for entry in feed.entries[:20]:  # Recent entries
                        try:
                            catalyst = await self.parse_edgar_entry(entry)
                            if catalyst:
                                catalysts.append(catalyst)
                        except Exception as e:
                            logger.debug(f"Error parsing RSS entry: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error parsing RSS feed {rss_url}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error monitoring EDGAR RSS: {e}")
        
        logger.info(f"📡 Found {len(catalysts)} catalysts from RSS feeds")
        return catalysts
    
    async def parse_edgar_entry(self, entry) -> Optional[CatalystOpportunity]:
        """Parse individual EDGAR RSS entry"""
        
        try:
            title = entry.get('title', '')
            link = entry.get('link', '')
            summary = entry.get('summary', '')
            published = entry.get('published_parsed')
            
            # Extract ticker from title
            ticker = self.extract_ticker_from_filing(title, summary)
            if not ticker:
                return None
            
            # Determine catalyst type
            catalyst_type = self.determine_catalyst_type_from_filing(title, summary)
            
            # Extract filing date
            filing_date = datetime.now()
            if published:
                try:
                    filing_date = datetime(*published[:6])
                except:
                    pass
            
            # Create catalyst
            catalyst = CatalystOpportunity(
                ticker=ticker,
                catalyst_type=catalyst_type,
                event_date=filing_date,
                confidence_score=0.8,  # SEC filings are reliable
                estimated_upside=None,
                estimated_downside=None,
                source="SEC EDGAR",
                source_url=link,
                headline=title[:100],
                details={
                    'filing_type': self.extract_form_type(title),
                    'summary': summary
                },
                discovered_at=datetime.now()
            )
            
            return catalyst
            
        except Exception as e:
            logger.debug(f"Error parsing EDGAR entry: {e}")
            return None
    
    async def check_sec_api(self) -> List[CatalystOpportunity]:
        """Check SEC API for specific company filings"""
        
        catalysts = []
        
        try:
            logger.info("🏛️ Checking SEC API for company filings...")
            
            # Focus on biotech/growth companies with frequent catalysts
            target_tickers = [
                'NVDA', 'AMD', 'TSLA', 'MRNA', 'BNTX', 'NVAX', 'GILD', 'BIIB',
                'PLTR', 'COIN', 'HOOD', 'SOFI', 'IONQ', 'SMCI'
            ]
            
            for ticker in target_tickers:
                try:
                    # Get CIK for ticker
                    cik = await self.get_cik_for_ticker(ticker)
                    if not cik:
                        continue
                    
                    # Get recent filings
                    filings = await self.get_recent_filings(cik, ticker)
                    catalysts.extend(filings)
                    
                except Exception as e:
                    logger.debug(f"Error checking {ticker}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error checking SEC API: {e}")
        
        logger.info(f"🏛️ Found {len(catalysts)} catalysts from SEC API")
        return catalysts
    
    async def get_cik_for_ticker(self, ticker: str) -> Optional[str]:
        """Get SEC CIK number for ticker"""
        
        try:
            # Use SEC company tickers JSON
            tickers_url = "https://www.sec.gov/files/company_tickers.json"
            
            response = self.session.get(tickers_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for entry in data.values():
                    if entry.get('ticker', '').upper() == ticker.upper():
                        return str(entry.get('cik_str', '')).zfill(10)
            
        except Exception as e:
            logger.debug(f"Error getting CIK for {ticker}: {e}")
        
        return None
    
    async def get_recent_filings(self, cik: str, ticker: str) -> List[CatalystOpportunity]:
        """Get recent filings for a specific company"""
        
        catalysts = []
        
        try:
            submissions_url = f"{self.sec_api_base}/CIK{cik}.json"
            
            response = self.session.get(submissions_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                filings = data.get('filings', {}).get('recent', {})
                forms = filings.get('form', [])
                dates = filings.get('filingDate', [])
                accessions = filings.get('accessionNumber', [])
                
                # Check recent filings (last 30 days)
                cutoff_date = datetime.now() - timedelta(days=30)
                
                for i, (form, date_str, accession) in enumerate(zip(forms, dates, accessions)):
                    try:
                        filing_date = datetime.strptime(date_str, '%Y-%m-%d')
                        
                        if filing_date < cutoff_date:
                            continue
                        
                        # Check if it's a catalyst form
                        if form in self.catalyst_forms:
                            
                            # Create filing URL
                            filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession.replace('-', '')}/{accession}.txt"
                            
                            catalyst = CatalystOpportunity(
                                ticker=ticker,
                                catalyst_type='SEC_FILING',
                                event_date=filing_date,
                                confidence_score=0.7,
                                estimated_upside=None,
                                estimated_downside=None,
                                source="SEC API",
                                source_url=filing_url,
                                headline=f"{ticker} filed {form}",
                                details={
                                    'form_type': form,
                                    'accession_number': accession,
                                    'cik': cik
                                },
                                discovered_at=datetime.now()
                            )
                            
                            catalysts.append(catalyst)
                    
                    except Exception as e:
                        logger.debug(f"Error parsing filing {i}: {e}")
                        continue
        
        except Exception as e:
            logger.debug(f"Error getting filings for CIK {cik}: {e}")
        
        return catalysts
    
    async def search_recent_filings(self) -> List[CatalystOpportunity]:
        """Search for recent filings with catalyst keywords"""
        
        catalysts = []
        
        try:
            logger.info("🔍 Searching recent filings for catalyst keywords...")
            
            # Search for filings with M&A keywords
            search_keywords = ['merger', 'acquisition', 'partnership', 'collaboration']
            
            for keyword in search_keywords:
                try:
                    # Use alternative search method
                    results = await self.search_edgar_by_keyword(keyword)
                    catalysts.extend(results)
                    
                except Exception as e:
                    logger.debug(f"Error searching for {keyword}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error searching recent filings: {e}")
        
        logger.info(f"🔍 Found {len(catalysts)} catalysts from filing search")
        return catalysts
    
    async def search_edgar_by_keyword(self, keyword: str) -> List[CatalystOpportunity]:
        """Search EDGAR filings by keyword"""
        
        catalysts = []
        
        try:
            # Use SEC's search interface
            search_url = f"https://www.sec.gov/edgar/search/#/q={keyword}&dateRange=30d&category=form-cat1"
            
            # Alternative: Use RSS search
            rss_search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=8-K&company={keyword}&dateb=&owner=include&start=0&count=20&output=atom"
            
            try:
                feed = feedparser.parse(rss_search_url)
                
                for entry in feed.entries[:10]:
                    catalyst = await self.parse_edgar_entry(entry)
                    if catalyst:
                        catalysts.append(catalyst)
                        
            except Exception as e:
                logger.debug(f"Error parsing search results for {keyword}: {e}")
        
        except Exception as e:
            logger.debug(f"Error searching for {keyword}: {e}")
        
        return catalysts
    
    def extract_ticker_from_filing(self, title: str, summary: str) -> Optional[str]:
        """Extract ticker from SEC filing"""
        
        text = f"{title} {summary}"
        
        # Look for ticker patterns
        ticker_patterns = [
            r'\(([A-Z]{2,5})\)',  # Ticker in parentheses
            r'([A-Z]{2,5})\s+\(',  # Ticker before parentheses
            r'\b([A-Z]{2,5})\b'    # Standalone ticker
        ]
        
        for pattern in ticker_patterns:
            matches = re.findall(pattern, text)
            
            for match in matches:
                # Skip common false positives
                if match in ['SEC', 'EDGAR', 'NYSE', 'NASDAQ', 'LLC', 'INC', 'CORP']:
                    continue
                
                # Validate ticker
                if self.validate_ticker(match):
                    return match
        
        return None
    
    def validate_ticker(self, ticker: str) -> bool:
        """Validate if string is a real ticker"""
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info.get('symbol') == ticker
        except:
            return False
    
    def extract_form_type(self, title: str) -> str:
        """Extract SEC form type from title"""
        
        form_patterns = [
            r'8-K/A',
            r'8-K',
            r'SC 13D/A',
            r'SC 13D',
            r'SC 13G',
            r'10-K',
            r'10-Q',
            r'DEF 14A'
        ]
        
        for pattern in form_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                return pattern
        
        return 'UNKNOWN'
    
    def determine_catalyst_type_from_filing(self, title: str, summary: str) -> str:
        """Determine catalyst type from SEC filing content"""
        
        text = f"{title} {summary}".lower()
        
        for catalyst_type, keywords in self.catalyst_keywords.items():
            if any(keyword in text for keyword in keywords):
                return catalyst_type
        
        # Default based on form type
        if '8-k' in text:
            return 'MATERIAL_EVENT'
        elif 'sc 13d' in text or 'sc 13g' in text:
            return 'OWNERSHIP_CHANGE'
        else:
            return 'SEC_FILING'
    
    def deduplicate_catalysts(self, catalysts: List[CatalystOpportunity]) -> List[CatalystOpportunity]:
        """Remove duplicate catalysts"""
        
        seen = set()
        unique_catalysts = []
        
        for catalyst in catalysts:
            # Create unique key
            key = (catalyst.ticker, catalyst.catalyst_type, catalyst.event_date.date())
            
            if key not in seen:
                seen.add(key)
                unique_catalysts.append(catalyst)
        
        return unique_catalysts

# Quick access function
async def get_sec_catalysts() -> List[CatalystOpportunity]:
    """Get SEC catalysts for external use"""
    
    try:
        monitor = SECMonitor()
        return await monitor.get_sec_catalysts()
    except Exception as e:
        logger.error(f"Error getting SEC catalysts: {e}")
        return []

# Test function
async def main():
    """Test SEC monitor"""
    
    logging.basicConfig(level=logging.INFO)
    
    monitor = SECMonitor()
    catalysts = await monitor.get_sec_catalysts()
    
    print(f"Found {len(catalysts)} SEC catalysts:")
    for catalyst in catalysts:
        print(f"- {catalyst.ticker}: {catalyst.headline} ({catalyst.event_date.date()})")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())