#!/usr/bin/env python3
"""
Live Portfolio Integration - Alpaca & SoFi
Shows real holdings from multiple brokers in mobile app
"""

import os
import yfinance as yf
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class PortfolioHolding:
    """Individual stock holding"""
    symbol: str
    quantity: float
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pl: float
    unrealized_pl_pct: float
    broker: str  # "Alpaca", "SoFi", "Manual"
    last_updated: datetime

@dataclass
class PortfolioSummary:
    """Complete portfolio summary"""
    total_value: float
    total_cost: float
    total_unrealized_pl: float
    total_unrealized_pl_pct: float
    holdings: List[PortfolioHolding]
    top_gainer: Optional[PortfolioHolding]
    top_loser: Optional[PortfolioHolding]
    broker_breakdown: Dict[str, float]

class LivePortfolioIntegration:
    """Integration with Alpaca and SoFi for live portfolio data"""
    
    def __init__(self):
        # API credentials
        self.alpaca_api_key = os.getenv('ALPACA_API_KEY', '')
        self.alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY', '')
        self.alpaca_base_url = "https://paper-api.alpaca.markets"  # Use paper for safety
        
        # SoFi doesn't have public API, so we'll use manual entry or screen scraping
        # For now, we'll focus on Alpaca + manual holdings
        
    async def get_live_portfolio(self) -> PortfolioSummary:
        """Get complete live portfolio from all sources"""
        
        all_holdings = []
        
        # Get Alpaca holdings
        alpaca_holdings = await self.get_alpaca_holdings()
        all_holdings.extend(alpaca_holdings)
        
        # Get manual/other holdings (for SoFi positions)
        manual_holdings = await self.get_manual_holdings()
        all_holdings.extend(manual_holdings)
        
        # Update current prices for all holdings
        updated_holdings = await self.update_current_prices(all_holdings)
        
        # Calculate summary
        summary = self.calculate_portfolio_summary(updated_holdings)
        
        return summary
    
    async def get_alpaca_holdings(self) -> List[PortfolioHolding]:
        """Get holdings from Alpaca account"""
        
        holdings = []
        
        if not self.alpaca_api_key or not self.alpaca_secret_key:
            logger.info("Alpaca credentials not configured")
            return holdings
        
        try:
            # Alpaca API headers
            headers = {
                'APCA-API-KEY-ID': self.alpaca_api_key,
                'APCA-API-SECRET-KEY': self.alpaca_secret_key,
                'Content-Type': 'application/json'
            }
            
            # Get positions
            positions_url = f"{self.alpaca_base_url}/v2/positions"
            response = requests.get(positions_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                positions = response.json()
                
                for position in positions:
                    holding = PortfolioHolding(
                        symbol=position['symbol'],
                        quantity=float(position['qty']),
                        avg_cost=float(position['avg_entry_price']),
                        current_price=float(position['current_price']),
                        market_value=float(position['market_value']),
                        unrealized_pl=float(position['unrealized_pl']),
                        unrealized_pl_pct=float(position['unrealized_plpc']) * 100,
                        broker="Alpaca",
                        last_updated=datetime.now()
                    )
                    holdings.append(holding)
                    
                logger.info(f"Retrieved {len(holdings)} Alpaca positions")
            else:
                logger.error(f"Alpaca API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching Alpaca holdings: {e}")
        
        return holdings
    
    async def get_manual_holdings(self) -> List[PortfolioHolding]:
        """Get manually entered holdings (for SoFi, Robinhood, etc.)"""
        
        try:
            # Import manual holdings configuration
            import sys
            import os
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
            sys.path.append(config_path)
            
            from manual_holdings import get_all_manual_holdings
            manual_positions = get_all_manual_holdings()
            
        except ImportError:
            logger.info("Manual holdings config not found, using example data")
            # Fallback example data
            manual_positions = [
                # Example - replace these in config/manual_holdings.py
                {'symbol': 'AAPL', 'quantity': 10, 'avg_cost': 175.00, 'broker': 'SoFi'},
                {'symbol': 'NVDA', 'quantity': 5, 'avg_cost': 450.00, 'broker': 'SoFi'},
            ]
        
        holdings = []
        
        for position in manual_positions:
            # We'll get current price in the update_current_prices method
            holding = PortfolioHolding(
                symbol=position['symbol'],
                quantity=position['quantity'],
                avg_cost=position['avg_cost'],
                current_price=0.0,  # Will be updated
                market_value=0.0,   # Will be calculated
                unrealized_pl=0.0,  # Will be calculated
                unrealized_pl_pct=0.0,  # Will be calculated
                broker=position['broker'],
                last_updated=datetime.now()
            )
            holdings.append(holding)
        
        return holdings
    
    async def update_current_prices(self, holdings: List[PortfolioHolding]) -> List[PortfolioHolding]:
        """Update current prices and calculate P&L for all holdings"""
        
        if not holdings:
            return holdings
        
        # Get unique symbols
        symbols = list(set(h.symbol for h in holdings))
        
        # Fetch current prices
        current_prices = {}
        
        try:
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    current_prices[symbol] = float(hist['Close'].iloc[-1])
                else:
                    logger.warning(f"Could not get price for {symbol}")
                    current_prices[symbol] = 0.0
                    
        except Exception as e:
            logger.error(f"Error fetching prices: {e}")
        
        # Update holdings with current prices
        for holding in holdings:
            current_price = current_prices.get(holding.symbol, 0.0)
            
            if current_price > 0:
                holding.current_price = current_price
                holding.market_value = holding.quantity * current_price
                holding.unrealized_pl = holding.market_value - (holding.quantity * holding.avg_cost)
                
                if holding.avg_cost > 0:
                    holding.unrealized_pl_pct = (holding.unrealized_pl / (holding.quantity * holding.avg_cost)) * 100
                else:
                    holding.unrealized_pl_pct = 0.0
        
        return holdings
    
    def calculate_portfolio_summary(self, holdings: List[PortfolioHolding]) -> PortfolioSummary:
        """Calculate portfolio summary statistics"""
        
        if not holdings:
            return PortfolioSummary(
                total_value=0.0,
                total_cost=0.0,
                total_unrealized_pl=0.0,
                total_unrealized_pl_pct=0.0,
                holdings=[],
                top_gainer=None,
                top_loser=None,
                broker_breakdown={}
            )
        
        # Calculate totals
        total_value = sum(h.market_value for h in holdings)
        total_cost = sum(h.quantity * h.avg_cost for h in holdings)
        total_unrealized_pl = sum(h.unrealized_pl for h in holdings)
        total_unrealized_pl_pct = (total_unrealized_pl / total_cost * 100) if total_cost > 0 else 0.0
        
        # Find top gainer and loser
        gainers = [h for h in holdings if h.unrealized_pl_pct > 0]
        losers = [h for h in holdings if h.unrealized_pl_pct < 0]
        
        top_gainer = max(gainers, key=lambda x: x.unrealized_pl_pct) if gainers else None
        top_loser = min(losers, key=lambda x: x.unrealized_pl_pct) if losers else None
        
        # Broker breakdown
        broker_breakdown = {}
        for holding in holdings:
            if holding.broker not in broker_breakdown:
                broker_breakdown[holding.broker] = 0.0
            broker_breakdown[holding.broker] += holding.market_value
        
        return PortfolioSummary(
            total_value=total_value,
            total_cost=total_cost,
            total_unrealized_pl=total_unrealized_pl,
            total_unrealized_pl_pct=total_unrealized_pl_pct,
            holdings=holdings,
            top_gainer=top_gainer,
            top_loser=top_loser,
            broker_breakdown=broker_breakdown
        )
    
    def format_portfolio_for_mobile(self, summary: PortfolioSummary) -> str:
        """Format portfolio summary for mobile display"""
        
        if not summary.holdings:
            return "📱 **LIVE PORTFOLIO**\n\nNo holdings found. Add your Alpaca API keys or update manual holdings."
        
        # Header
        output = "📱 **LIVE PORTFOLIO TRACKER**\n"
        output += "=" * 50 + "\n\n"
        
        # Portfolio summary
        pl_emoji = "🟢" if summary.total_unrealized_pl >= 0 else "🔴"
        output += f"💰 **PORTFOLIO SUMMARY**\n"
        output += f"   • **Total Value**: ${summary.total_value:,.2f}\n"
        output += f"   • **Total Cost**: ${summary.total_cost:,.2f}\n"
        output += f"   • **P&L**: {pl_emoji} ${summary.total_unrealized_pl:+,.2f} ({summary.total_unrealized_pl_pct:+.1f}%)\n\n"
        
        # Broker breakdown
        output += f"🏦 **BROKER BREAKDOWN**\n"
        for broker, value in summary.broker_breakdown.items():
            pct = (value / summary.total_value * 100) if summary.total_value > 0 else 0
            output += f"   • **{broker}**: ${value:,.2f} ({pct:.1f}%)\n"
        output += "\n"
        
        # Top performers
        if summary.top_gainer:
            output += f"🚀 **TOP GAINER**: {summary.top_gainer.symbol} ({summary.top_gainer.unrealized_pl_pct:+.1f}%)\n"
        if summary.top_loser:
            output += f"📉 **TOP LOSER**: {summary.top_loser.symbol} ({summary.top_loser.unrealized_pl_pct:+.1f}%)\n"
        output += "\n"
        
        # Individual holdings
        output += f"📊 **HOLDINGS ({len(summary.holdings)} positions)**\n"
        output += "-" * 50 + "\n"
        
        # Sort by market value (largest first)
        sorted_holdings = sorted(summary.holdings, key=lambda x: x.market_value, reverse=True)
        
        for holding in sorted_holdings:
            pl_emoji = "🟢" if holding.unrealized_pl >= 0 else "🔴"
            output += f"**{holding.symbol}** ({holding.broker})\n"
            output += f"   • Shares: {holding.quantity:,.0f} @ ${holding.avg_cost:.2f}\n"
            output += f"   • Current: ${holding.current_price:.2f}\n"
            output += f"   • Value: ${holding.market_value:,.2f}\n"
            output += f"   • P&L: {pl_emoji} ${holding.unrealized_pl:+,.2f} ({holding.unrealized_pl_pct:+.1f}%)\n\n"
        
        # Footer
        output += f"⏰ **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        output += f"📱 Live data from Alpaca API + Manual entries"
        
        return output

# Quick access function for Streamlit
async def get_live_portfolio_for_mobile() -> str:
    """Quick function to get formatted portfolio for mobile display"""
    
    try:
        portfolio_engine = LivePortfolioIntegration()
        summary = await portfolio_engine.get_live_portfolio()
        return portfolio_engine.format_portfolio_for_mobile(summary)
    except Exception as e:
        return f"❌ Portfolio error: {str(e)}"

# Test function
async def main():
    """Test the portfolio integration"""
    
    engine = LivePortfolioIntegration()
    summary = await engine.get_live_portfolio()
    formatted_output = engine.format_portfolio_for_mobile(summary)
    print(formatted_output)

if __name__ == "__main__":
    asyncio.run(main())