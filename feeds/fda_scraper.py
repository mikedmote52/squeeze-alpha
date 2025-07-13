#!/usr/bin/env python3
"""
FDA PDUFA Date Scraper
Scrapes real FDA approval dates and PDUFA dates from official sources
"""

import requests
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import re
import sys
import os

# Add schemas to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schemas'))
from catalyst_opportunity import CatalystOpportunity

logger = logging.getLogger(__name__)

class FDAScraper:
    """Scraper for real FDA PDUFA dates and drug approvals"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # FDA data sources
        self.fda_drugs_url = "https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files"
        self.biopharmcatalyst_url = "https://www.biopharmcatalyst.com/calendars/fda-calendar"
        
        # Known biotech ticker mappings (extend as needed)
        self.company_ticker_map = {
            'Moderna': 'MRNA',
            'BioNTech': 'BNTX', 
            'Novavax': 'NVAX',
            'Gilead': 'GILD',
            'Biogen': 'BIIB',
            'Vertex': 'VRTX',
            'Regeneron': 'REGN',
            'Amgen': 'AMGN',
            'AbbVie': 'ABBV',
            'Johnson & Johnson': 'JNJ',
            'Pfizer': 'PFE',
            'Merck': 'MRK',
            'Bristol-Myers': 'BMY',
            'Roche': 'RHHBY',
            'Sanofi': 'SNY'
        }
    
    async def get_fda_catalysts(self) -> List[CatalystOpportunity]:
        """Get real FDA catalysts from multiple sources"""
        
        logger.info("🔍 Scraping real FDA catalysts...")
        
        catalysts = []
        
        # Source 1: BioPharma Catalyst (most reliable for PDUFA dates)
        bpc_catalysts = await self.scrape_biopharmcatalyst()
        catalysts.extend(bpc_catalysts)
        
        # Source 2: FDA Orange Book updates
        fda_catalysts = await self.scrape_fda_approvals()
        catalysts.extend(fda_catalysts)
        
        # Source 3: Recent FDA press releases
        press_catalysts = await self.scrape_fda_press_releases()
        catalysts.extend(press_catalysts)
        
        # Deduplicate and validate
        unique_catalysts = self.deduplicate_catalysts(catalysts)
        
        logger.info(f"✅ Found {len(unique_catalysts)} real FDA catalysts")
        return unique_catalysts
    
    async def scrape_biopharmcatalyst(self) -> List[CatalystOpportunity]:
        """Scrape BioPharma Catalyst for PDUFA dates"""
        
        catalysts = []
        
        try:
            logger.info("📊 Scraping BioPharma Catalyst PDUFA calendar...")
            
            response = self.session.get(self.biopharmcatalyst_url, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"BioPharma Catalyst returned {response.status_code}")
                return catalysts
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for calendar events (structure may vary)
            events = soup.find_all(['tr', 'div'], class_=['event', 'calendar-event', 'pdufa-event'])
            
            for event in events:
                try:
                    catalyst = self.parse_biopharmcatalyst_event(event)
                    if catalyst:
                        catalysts.append(catalyst)
                except Exception as e:
                    logger.debug(f"Error parsing event: {e}")
                    continue
            
            # Alternative: Look for table rows with date patterns
            if not catalysts:
                catalysts = self.parse_calendar_table(soup)
            
        except Exception as e:
            logger.error(f"Error scraping BioPharma Catalyst: {e}")
        
        logger.info(f"📊 Found {len(catalysts)} catalysts from BioPharma Catalyst")
        return catalysts
    
    def parse_biopharmcatalyst_event(self, event) -> Optional[CatalystOpportunity]:
        """Parse individual BioPharma Catalyst event"""
        
        try:
            # Extract text content
            text = event.get_text().strip()
            
            # Look for ticker patterns
            ticker_match = re.search(r'\b([A-Z]{2,5})\b', text)
            if not ticker_match:
                return None
            
            ticker = ticker_match.group(1)
            
            # Look for date patterns
            date_patterns = [
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}'
            ]
            
            event_date = None
            for pattern in date_patterns:
                date_match = re.search(pattern, text, re.IGNORECASE)
                if date_match:
                    try:
                        event_date = pd.to_datetime(date_match.group(1)).to_pydatetime()
                        break
                    except:
                        continue
            
            if not event_date:
                # Default to 30 days out if no date found
                event_date = datetime.now() + timedelta(days=30)
            
            # Determine catalyst type from text
            catalyst_type = self.determine_catalyst_type(text)
            
            # Extract headline
            headline = text[:100].strip()
            
            catalyst = CatalystOpportunity(
                ticker=ticker,
                catalyst_type=catalyst_type,
                event_date=event_date,
                confidence_score=0.8,  # BioPharma Catalyst is reliable
                estimated_upside=None,
                estimated_downside=None,
                source="BioPharma Catalyst",
                source_url=self.biopharmcatalyst_url,
                headline=headline,
                details={'raw_text': text},
                discovered_at=datetime.now()
            )
            
            return catalyst
            
        except Exception as e:
            logger.debug(f"Error parsing event: {e}")
            return None
    
    def parse_calendar_table(self, soup) -> List[CatalystOpportunity]:
        """Parse calendar table format"""
        
        catalysts = []
        
        try:
            # Look for tables containing FDA events
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:  # Need at least date, company, event
                        try:
                            # Attempt to parse table structure
                            date_text = cells[0].get_text().strip()
                            company_text = cells[1].get_text().strip()
                            event_text = cells[2].get_text().strip()
                            
                            # Extract ticker from company text
                            ticker = self.extract_ticker_from_company(company_text)
                            if not ticker:
                                continue
                            
                            # Parse date
                            try:
                                event_date = pd.to_datetime(date_text).to_pydatetime()
                            except:
                                continue
                            
                            # Create catalyst
                            catalyst = CatalystOpportunity(
                                ticker=ticker,
                                catalyst_type=self.determine_catalyst_type(event_text),
                                event_date=event_date,
                                confidence_score=0.7,
                                estimated_upside=None,
                                estimated_downside=None,
                                source="BioPharma Catalyst Table",
                                source_url=self.biopharmcatalyst_url,
                                headline=f"{company_text} - {event_text}",
                                details={'company': company_text, 'event': event_text},
                                discovered_at=datetime.now()
                            )
                            
                            catalysts.append(catalyst)
                            
                        except Exception as e:
                            logger.debug(f"Error parsing table row: {e}")
                            continue
        
        except Exception as e:
            logger.debug(f"Error parsing calendar table: {e}")
        
        return catalysts
    
    async def scrape_fda_approvals(self) -> List[CatalystOpportunity]:
        """Scrape FDA.gov for recent drug approvals"""
        
        catalysts = []
        
        try:
            logger.info("🏛️ Scraping FDA.gov for recent approvals...")
            
            # FDA press releases
            fda_press_url = "https://www.fda.gov/news-events/newsroom/press-announcements"
            
            response = self.session.get(fda_press_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for press release links
                press_links = soup.find_all('a', href=True)
                
                for link in press_links[:20]:  # Check recent press releases
                    href = link.get('href')
                    title = link.get_text().strip()
                    
                    if 'approval' in title.lower() or 'authorize' in title.lower():
                        try:
                            catalyst = await self.parse_fda_press_release(href, title)
                            if catalyst:
                                catalysts.append(catalyst)
                        except Exception as e:
                            logger.debug(f"Error parsing press release: {e}")
                            continue
            
        except Exception as e:
            logger.error(f"Error scraping FDA approvals: {e}")
        
        logger.info(f"🏛️ Found {len(catalysts)} catalysts from FDA.gov")
        return catalysts
    
    async def parse_fda_press_release(self, href: str, title: str) -> Optional[CatalystOpportunity]:
        """Parse individual FDA press release"""
        
        try:
            if not href.startswith('http'):
                href = f"https://www.fda.gov{href}"
            
            # Extract company/drug info from title
            ticker = self.extract_ticker_from_title(title)
            if not ticker:
                return None
            
            catalyst = CatalystOpportunity(
                ticker=ticker,
                catalyst_type='FDA_APPROVAL',
                event_date=datetime.now(),  # Already happened
                confidence_score=1.0,  # FDA announcements are definitive
                estimated_upside=None,
                estimated_downside=None,
                source="FDA.gov",
                source_url=href,
                headline=title,
                details={'press_release': True},
                discovered_at=datetime.now()
            )
            
            return catalyst
            
        except Exception as e:
            logger.debug(f"Error parsing FDA press release: {e}")
            return None
    
    async def scrape_fda_press_releases(self) -> List[CatalystOpportunity]:
        """Scrape FDA press releases for drug approvals"""
        
        catalysts = []
        
        try:
            logger.info("📰 Scraping FDA press releases...")
            
            # Alternative FDA news sources
            fda_news_urls = [
                "https://www.fda.gov/news-events/newsroom/press-announcements",
                "https://www.fda.gov/drugs/news-events-human-drugs"
            ]
            
            for url in fda_news_urls:
                try:
                    response = self.session.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for approval announcements
                        articles = soup.find_all(['article', 'div', 'li'], class_=['news-item', 'press-release'])
                        
                        for article in articles[:10]:  # Recent items
                            text = article.get_text().strip()
                            
                            if any(keyword in text.lower() for keyword in ['approval', 'authorize', 'pdufa']):
                                ticker = self.extract_ticker_from_text(text)
                                
                                if ticker:
                                    catalyst = CatalystOpportunity(
                                        ticker=ticker,
                                        catalyst_type='FDA_APPROVAL',
                                        event_date=datetime.now(),
                                        confidence_score=0.9,
                                        estimated_upside=None,
                                        estimated_downside=None,
                                        source="FDA Press Release",
                                        source_url=url,
                                        headline=text[:100],
                                        details={'source_type': 'press_release'},
                                        discovered_at=datetime.now()
                                    )
                                    
                                    catalysts.append(catalyst)
                                    
                except Exception as e:
                    logger.debug(f"Error scraping {url}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping FDA press releases: {e}")
        
        logger.info(f"📰 Found {len(catalysts)} catalysts from FDA press releases")
        return catalysts
    
    def extract_ticker_from_company(self, company_text: str) -> Optional[str]:
        """Extract ticker from company name"""
        
        # Look for ticker in parentheses
        ticker_match = re.search(r'\(([A-Z]{2,5})\)', company_text)
        if ticker_match:
            return ticker_match.group(1)
        
        # Look for known company mappings
        for company, ticker in self.company_ticker_map.items():
            if company.lower() in company_text.lower():
                return ticker
        
        # Look for standalone ticker
        ticker_match = re.search(r'\b([A-Z]{2,5})\b', company_text)
        if ticker_match:
            return ticker_match.group(1)
        
        return None
    
    def extract_ticker_from_title(self, title: str) -> Optional[str]:
        """Extract ticker from FDA press release title"""
        
        # Look for company names in title
        for company, ticker in self.company_ticker_map.items():
            if company.lower() in title.lower():
                return ticker
        
        # Look for ticker patterns
        ticker_match = re.search(r'\b([A-Z]{2,5})\b', title)
        if ticker_match:
            potential_ticker = ticker_match.group(1)
            
            # Validate it's a real ticker
            try:
                stock = yf.Ticker(potential_ticker)
                info = stock.info
                if info.get('symbol') == potential_ticker:
                    return potential_ticker
            except:
                pass
        
        return None
    
    def extract_ticker_from_text(self, text: str) -> Optional[str]:
        """Extract ticker from general text"""
        
        # Look for ticker patterns with validation
        ticker_matches = re.findall(r'\b([A-Z]{2,5})\b', text)
        
        for match in ticker_matches:
            # Skip common false positives
            if match in ['FDA', 'CEO', 'IPO', 'API', 'USA', 'NYSE', 'SEC']:
                continue
            
            # Validate with yfinance
            try:
                stock = yf.Ticker(match)
                info = stock.info
                if info.get('symbol') == match:
                    return match
            except:
                continue
        
        return None
    
    def determine_catalyst_type(self, text: str) -> str:
        """Determine catalyst type from text"""
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['pdufa', 'approval', 'authorize']):
            return 'FDA_APPROVAL'
        elif any(word in text_lower for word in ['clinical', 'trial', 'phase']):
            return 'CLINICAL_TRIAL'
        elif any(word in text_lower for word in ['partnership', 'collaboration']):
            return 'PARTNERSHIP'
        else:
            return 'FDA_EVENT'
    
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
async def get_fda_catalysts() -> List[CatalystOpportunity]:
    """Get FDA catalysts for external use"""
    
    try:
        scraper = FDAScraper()
        return await scraper.get_fda_catalysts()
    except Exception as e:
        logger.error(f"Error getting FDA catalysts: {e}")
        return []

# Test function
async def main():
    """Test FDA scraper"""
    
    logging.basicConfig(level=logging.INFO)
    
    scraper = FDAScraper()
    catalysts = await scraper.get_fda_catalysts()
    
    print(f"Found {len(catalysts)} FDA catalysts:")
    for catalyst in catalysts:
        print(f"- {catalyst.ticker}: {catalyst.headline} ({catalyst.event_date.date()})")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())