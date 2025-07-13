#!/usr/bin/env python3
"""
Manual Holdings Configuration
Add your SoFi, Robinhood, or other broker holdings here
"""

# Your SoFi Holdings - Update these with your actual positions
SOFI_HOLDINGS = [
    # Format: {'symbol': 'TICKER', 'quantity': shares, 'avg_cost': average_price, 'broker': 'SoFi'}
    
    # Example entries - replace with your actual holdings:
    # {'symbol': 'AAPL', 'quantity': 25, 'avg_cost': 175.00, 'broker': 'SoFi'},
    # {'symbol': 'NVDA', 'quantity': 10, 'avg_cost': 450.00, 'broker': 'SoFi'},
    # {'symbol': 'MSFT', 'quantity': 15, 'avg_cost': 380.00, 'broker': 'SoFi'},
    # {'symbol': 'GOOGL', 'quantity': 5, 'avg_cost': 2800.00, 'broker': 'SoFi'},
    # {'symbol': 'TSLA', 'quantity': 8, 'avg_cost': 220.00, 'broker': 'SoFi'},
    
    # Add your actual SoFi holdings here:
    
]

# Your Other Broker Holdings (Robinhood, Schwab, etc.)
OTHER_HOLDINGS = [
    # Format: {'symbol': 'TICKER', 'quantity': shares, 'avg_cost': average_price, 'broker': 'BrokerName'}
    
    # Example entries:
    # {'symbol': 'SPY', 'quantity': 50, 'avg_cost': 420.00, 'broker': 'Robinhood'},
    # {'symbol': 'QQQ', 'quantity': 30, 'avg_cost': 350.00, 'broker': 'Schwab'},
    
    # Add your other holdings here:
    
]

def get_all_manual_holdings():
    """Get all manual holdings combined"""
    return SOFI_HOLDINGS + OTHER_HOLDINGS

def get_holdings_by_broker(broker_name):
    """Get holdings for a specific broker"""
    all_holdings = get_all_manual_holdings()
    return [h for h in all_holdings if h['broker'].lower() == broker_name.lower()]

# Instructions for updating:
"""
TO UPDATE YOUR HOLDINGS:

1. Edit the SOFI_HOLDINGS list above
2. Add your actual positions like this:
   {'symbol': 'AAPL', 'quantity': 25, 'avg_cost': 175.00, 'broker': 'SoFi'},

3. For SoFi positions, you can find this info in your SoFi app:
   - Go to Investing tab
   - Click on each stock
   - Note the quantity and average cost

4. Save this file and your mobile app will show live P&L

5. The system will automatically get current prices and calculate gains/losses

Example of a complete entry:
{'symbol': 'NVDA', 'quantity': 10, 'avg_cost': 450.00, 'broker': 'SoFi'},

This means you own 10 shares of NVDA bought at an average price of $450.00
"""