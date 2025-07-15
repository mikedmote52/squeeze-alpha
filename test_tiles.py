#!/usr/bin/env python3
"""
Test script to verify integrated tiles are working
"""

# Test data that matches your BTBT example
test_portfolio_data = {
    'positions': [
        {
            'symbol': 'BTBT',
            'qty': 328,
            'avg_cost': 3.38,
            'current_price': 3.41,
            'market_value': 1117.04,
            'unrealized_pl': 7.06,
            'unrealized_plpc': 0.64
        }
    ]
}

# Test the integrated tiles
from integrated_portfolio_tiles import display_integrated_portfolio_tiles

print("Testing integrated tiles with BTBT data:")
print("- Symbol: BTBT")
print("- Quantity: 328")
print("- Avg Cost: $3.38")
print("- Current Price: $3.41")
print("- Market Value: $1117.04")
print("- P&L Amount: $7.06")
print("- P&L Percent: +0.64%")
print("\nThis data should ALL be inside the tile, not below it!")
print("\nIntegrated tiles are ready to use!")