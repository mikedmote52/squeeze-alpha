#!/usr/bin/env python3
"""
Streamlit Backend Bridge
Connects Streamlit frontend to existing real backend systems
ZERO MOCK DATA - All connections to real systems
"""

import asyncio
import requests
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamlitBackendBridge:
    """Bridge between Streamlit frontend and existing backend systems"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Test backend connection
        self.backend_online = self._test_backend_connection()
        
    def _test_backend_connection(self) -> bool:
        """Test if backend is online and responsive"""
        try:
            response = self.session.get(f"{self.backend_url}/", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Backend connection successful")
                return True
            else:
                logger.warning(f"⚠️ Backend responded with status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Backend connection failed: {e}")
            return False
    
    def get_backend_status(self) -> Dict[str, Any]:
        """Get backend system status"""
        if not self.backend_online:
            return {
                'status': 'offline',
                'message': 'Backend not responding',
                'alpaca_configured': False,
                'openrouter_configured': False
            }
        
        try:
            response = self.session.get(f"{self.backend_url}/")
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'online',
                    'message': data.get('message', 'Backend online'),
                    'alpaca_configured': data.get('alpaca_configured', False),
                    'openrouter_configured': data.get('openrouter_configured', False),
                    'data_sources': data.get('data_sources', 'Unknown'),
                    'endpoints': data.get('endpoints', [])
                }
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error getting backend status: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_portfolio_data(self) -> Optional[Dict[str, Any]]:
        """Get real portfolio data from backend"""
        if not self.backend_online:
            return None
            
        try:
            # Get positions and performance data
            positions_response = self.session.get(f"{self.backend_url}/api/portfolio/positions")
            performance_response = self.session.get(f"{self.backend_url}/api/portfolio/performance")
            
            if positions_response.status_code == 200 and performance_response.status_code == 200:
                positions_data = positions_response.json()
                performance_data = performance_response.json()
                
                return {
                    'positions': positions_data.get('positions', []),
                    'performance': performance_data,
                    'last_updated': datetime.now().isoformat(),
                    'source': positions_data.get('source', 'Alpaca API'),
                    'error': None
                }
            else:
                error_msg = f"Portfolio API error: positions={positions_response.status_code}, performance={performance_response.status_code}"
                logger.error(error_msg)
                return {'error': error_msg, 'positions': [], 'performance': {}}
                
        except Exception as e:
            logger.error(f"Error getting portfolio data: {e}")
            return {'error': str(e), 'positions': [], 'performance': {}}
    
    def get_opportunities(self) -> List[Dict[str, Any]]:
        """Get real opportunity data from discovery engines"""
        if not self.backend_online:
            return []
            
        opportunities = []
        
        try:
            # Get catalyst discoveries
            catalyst_response = self.session.get(f"{self.backend_url}/api/catalyst-discovery")
            if catalyst_response.status_code == 200:
                catalyst_data = catalyst_response.json()
                
                for catalyst in catalyst_data.get('catalysts', []):
                    opportunities.append({
                        'ticker': catalyst.get('ticker', 'Unknown'),
                        'type': 'Catalyst Discovery',
                        'description': catalyst.get('description', 'No description'),
                        'confidence': catalyst.get('aiProbability', 0),
                        'upside': catalyst.get('expectedUpside', 0),
                        'source': catalyst.get('source', 'FDA/SEC'),
                        'date': catalyst.get('date'),
                        'current_price': catalyst.get('currentPrice', 0),
                        'target_price': catalyst.get('targetPrice', 0),
                        'reasoning': catalyst.get('aiReasoning', ''),
                        'raw_data': catalyst
                    })
            else:
                logger.warning(f"Catalyst discovery API returned {catalyst_response.status_code}")
                
        except Exception as e:
            logger.error(f"Error getting catalyst opportunities: {e}")
        
        try:
            # Get alpha discoveries
            alpha_response = self.session.get(f"{self.backend_url}/api/alpha-discovery")
            if alpha_response.status_code == 200:
                alpha_data = alpha_response.json()
                
                for alpha in alpha_data.get('opportunities', []):
                    opportunities.append({
                        'ticker': alpha.get('ticker', 'Unknown'),
                        'type': 'Alpha Discovery',
                        'description': alpha.get('description', 'No description'),
                        'confidence': alpha.get('confidence', 0),
                        'upside': alpha.get('expectedUpside', 0),
                        'source': alpha.get('source', 'Market Scan'),
                        'current_price': alpha.get('currentPrice', 0),
                        'target_price': alpha.get('targetPrice', 0),
                        'reasoning': alpha.get('aiReasoning', ''),
                        'sector': alpha.get('sector', 'Unknown'),
                        'raw_data': alpha
                    })
            else:
                logger.warning(f"Alpha discovery API returned {alpha_response.status_code}")
                
        except Exception as e:
            logger.error(f"Error getting alpha opportunities: {e}")
        
        logger.info(f"Retrieved {len(opportunities)} total opportunities")
        return opportunities
    
    def run_ai_analysis(self, symbol: str, context: str = "") -> Optional[Dict[str, Any]]:
        """Run AI analysis for a symbol using the backend"""
        if not self.backend_online:
            return None
            
        try:
            payload = {
                "symbol": symbol,
                "context": context or f"Analysis requested from Streamlit interface for {symbol}"
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/ai-analysis",
                json=payload
            )
            
            if response.status_code == 200:
                analysis_data = response.json()
                logger.info(f"✅ AI analysis completed for {symbol}")
                return analysis_data
            else:
                logger.error(f"AI analysis failed for {symbol}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error running AI analysis for {symbol}: {e}")
            return None
    
    def get_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock data for a symbol"""
        if not self.backend_online:
            return None
            
        try:
            response = self.session.get(f"{self.backend_url}/api/stocks/{symbol}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Stock data failed for {symbol}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting stock data for {symbol}: {e}")
            return None
    
    def execute_trade(self, trade_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a trade via the backend"""
        if not self.backend_online:
            return None
            
        try:
            response = self.session.post(
                f"{self.backend_url}/api/trades/execute",
                json=trade_data
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Trade execution failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return None
    
    def log_trade(self, log_data: Dict[str, Any]) -> bool:
        """Log trade data for system learning"""
        if not self.backend_online:
            return False
            
        try:
            response = self.session.post(
                f"{self.backend_url}/api/trades/log",
                json=log_data
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error logging trade: {e}")
            return False
    
    async def get_live_portfolio(self) -> Optional[Dict[str, Any]]:
        """Async wrapper for portfolio data - for compatibility with existing code"""
        return self.get_portfolio_data()
    
    async def discover_opportunities(self) -> List[Dict[str, Any]]:
        """Async wrapper for opportunities - for compatibility with existing code"""
        return self.get_opportunities()
    
    async def run_ai_stock_analysis(self, symbol: str, context: str = "") -> Optional[Dict[str, Any]]:
        """Async wrapper for AI analysis - for compatibility with existing code"""
        return self.run_ai_analysis(symbol, context)

# Global bridge instance
_bridge_instance = None

def get_bridge(backend_url: str = "http://localhost:8000") -> StreamlitBackendBridge:
    """Get or create the global bridge instance"""
    global _bridge_instance
    
    if _bridge_instance is None:
        _bridge_instance = StreamlitBackendBridge(backend_url)
    
    return _bridge_instance

def test_bridge_connection():
    """Test the bridge connection and report status"""
    bridge = get_bridge()
    
    print("🔍 Testing Streamlit Backend Bridge...")
    print("=" * 50)
    
    # Test backend status
    status = bridge.get_backend_status()
    print(f"Backend Status: {status['status']}")
    
    if status['status'] == 'online':
        print(f"✅ Alpaca API: {'Configured' if status.get('alpaca_configured') else 'Not configured'}")
        print(f"✅ OpenRouter API: {'Configured' if status.get('openrouter_configured') else 'Not configured'}")
        print(f"✅ Data Sources: {status.get('data_sources', 'Unknown')}")
        
        # Test portfolio data
        print("\n📊 Testing Portfolio Data...")
        portfolio = bridge.get_portfolio_data()
        if portfolio and not portfolio.get('error'):
            print(f"✅ Portfolio positions: {len(portfolio.get('positions', []))}")
        else:
            print(f"⚠️ Portfolio error: {portfolio.get('error') if portfolio else 'No data'}")
        
        # Test opportunities
        print("\n🔍 Testing Opportunity Discovery...")
        opportunities = bridge.get_opportunities()
        print(f"✅ Opportunities found: {len(opportunities)}")
        
        # Test AI analysis (with a simple symbol)
        print("\n🤖 Testing AI Analysis...")
        analysis = bridge.run_ai_analysis("AAPL", "Test analysis from bridge")
        if analysis:
            agents = analysis.get('agents', [])
            print(f"✅ AI analysis completed: {len(agents)} agents responded")
        else:
            print("⚠️ AI analysis failed")
    
    else:
        print(f"❌ Backend offline: {status.get('message', 'Unknown error')}")
        print("💡 Start the backend with: python real_ai_backend.py")
    
    print("\n" + "=" * 50)
    print("Bridge testing complete!")

if __name__ == "__main__":
    test_bridge_connection()