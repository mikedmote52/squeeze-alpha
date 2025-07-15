#!/usr/bin/env python3
"""
Manual Holdings Configuration
Add your SoFi, Robinhood, or other broker holdings here
"""

# Your SoFi Holdings - Update these with your actual positions
SOFI_HOLDINGS = [
    # Format: {'symbol': 'TICKER', 'quantity': shares, 'avg_cost': average_price, 'broker': 'SoFi'}
    
    # Add your actual holdings here - no examples provided
    
    # Add your actual SoFi holdings here:
    
]

# Your Other Broker Holdings (Robinhood, Schwab, etc.)
OTHER_HOLDINGS = [
    # Format: {'symbol': 'TICKER', 'quantity': shares, 'avg_cost': average_price, 'broker': 'BrokerName'}
    
    # Add your other broker holdings here - no examples provided
    
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

Format for entries:
{'symbol': 'TICKER', 'quantity': shares_owned, 'avg_cost': average_purchase_price, 'broker': 'BrokerName'}
"""