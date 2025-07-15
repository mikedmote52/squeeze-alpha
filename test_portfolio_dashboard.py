#!/usr/bin/env python3
"""
Test script to verify Portfolio Dashboard shows integrated tiles
"""

import sys
sys.path.append('./pages')

# Test that the Portfolio Dashboard properly uses integrated tiles
try:
    # Read the Portfolio Dashboard file
    with open('pages/01_🏠_Portfolio_Dashboard.py', 'r') as f:
        content = f.read()
    
    # Check that display_position_details uses integrated tiles
    if 'display_integrated_portfolio_tiles(portfolio_data)' in content:
        print("✅ Portfolio Dashboard correctly uses integrated tiles")
    else:
        print("❌ Portfolio Dashboard NOT using integrated tiles")
    
    # Check that old tile display code is removed
    if 'st.metric("Quantity"' in content:
        print("❌ Old tile display code still present")
    else:
        print("✅ Old tile display code removed")
    
    # Check that the function is properly defined
    if 'def display_position_details(positions):' in content:
        print("✅ display_position_details function defined")
    else:
        print("❌ display_position_details function missing")
    
    # Check for duplicate functions
    function_count = content.count('def display_position_details(positions):')
    if function_count == 1:
        print("✅ No duplicate functions")
    else:
        print(f"❌ Found {function_count} duplicate functions")
    
    print("\nPortfolio Dashboard Test Summary:")
    print("- The Portfolio Dashboard should now show integrated tiles")
    print("- All data (Quantity, Avg Cost, Current Price, Market Value, P&L Amount, AI Rating) should be INSIDE the tiles")
    print("- No separate 'Position Details' section should appear below the tiles")
    print("- Each tile should be clickable to expand trading options")
    
except Exception as e:
    print(f"❌ Error testing Portfolio Dashboard: {e}")