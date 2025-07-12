#!/usr/bin/env python3
"""
Sync Portfolio with Alpaca Account
Get real positions from Alpaca and update system accordingly
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add path for local modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def get_alpaca_positions():
    """Get actual positions from Alpaca account"""
    
    # Get API credentials
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    if not api_key or not secret_key:
        print("❌ Alpaca API credentials not found in environment")
        return None
    
    try:
        # Get positions from Alpaca
        headers = {
            'APCA-API-KEY-ID': api_key,
            'APCA-API-SECRET-KEY': secret_key
        }
        
        response = requests.get(f"{base_url}/v2/positions", headers=headers)
        
        if response.status_code == 200:
            positions = response.json()
            
            print(f"📊 Found {len(positions)} positions in Alpaca account:")
            
            portfolio_data = []
            for position in positions:
                portfolio_data.append({
                    "ticker": position['symbol'],
                    "shares": float(position['qty']),
                    "market_value": float(position['market_value']),
                    "cost_basis": float(position['cost_basis']),
                    "unrealized_pl": float(position['unrealized_pl']),
                    "unrealized_plpc": float(position['unrealized_plpc']) * 100,
                    "side": position['side']
                })
                
                print(f"  {position['symbol']}: {position['qty']} shares, "
                      f"${float(position['market_value']):,.2f} value, "
                      f"{float(position['unrealized_plpc']) * 100:+.1f}% P&L")
            
            return portfolio_data
            
        else:
            print(f"❌ Error fetching positions: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error connecting to Alpaca: {e}")
        return None

def update_replit_portfolio_config(positions):
    """Update Replit configuration with actual portfolio"""
    
    if not positions:
        print("❌ No positions to update")
        return
    
    # Extract just the tickers
    tickers = [pos['ticker'] for pos in positions]
    
    # Update replit_main.py
    replit_file = 'replit_main.py'
    
    if os.path.exists(replit_file):
        try:
            with open(replit_file, 'r') as f:
                content = f.read()
            
            # Find the tickers line and replace it
            old_line = 'tickers = ["NVAX", "BYND", "BLNK", "CHPT", "WOLF", "LIXT"]'
            new_line = f'tickers = {tickers}'
            
            if old_line in content:
                updated_content = content.replace(old_line, new_line)
                
                with open(replit_file, 'w') as f:
                    f.write(updated_content)
                
                print(f"✅ Updated {replit_file} with {len(tickers)} tickers")
            else:
                print(f"⚠️ Could not find ticker line in {replit_file}")
        
        except Exception as e:
            print(f"❌ Error updating {replit_file}: {e}")
    
    # Update web_control.py
    web_file = 'web_control.py'
    
    if os.path.exists(web_file):
        try:
            with open(web_file, 'r') as f:
                content = f.read()
            
            # Find the tickers line and replace it
            old_line = 'tickers = ["NVAX", "BYND", "BLNK", "CHPT", "WOLF", "LIXT"]'
            new_line = f'tickers = {tickers}'
            
            if old_line in content:
                updated_content = content.replace(old_line, new_line)
                
                with open(web_file, 'w') as f:
                    f.write(updated_content)
                
                print(f"✅ Updated {web_file} with {len(tickers)} tickers")
            else:
                print(f"⚠️ Could not find ticker line in {web_file}")
        
        except Exception as e:
            print(f"❌ Error updating {web_file}: {e}")
    
    # Update multi_ai_consensus_engine.py
    ai_file = 'multi_ai_consensus_engine.py'
    
    if os.path.exists(ai_file):
        try:
            with open(ai_file, 'r') as f:
                content = f.read()
            
            # Find the portfolio_tickers line and replace it
            old_line = 'portfolio_tickers = ["NVAX", "BYND", "BLNK", "CHPT", "WOLF", "LIXT"]'
            new_line = f'portfolio_tickers = {tickers}'
            
            if old_line in content:
                updated_content = content.replace(old_line, new_line)
                
                with open(ai_file, 'w') as f:
                    f.write(updated_content)
                
                print(f"✅ Updated {ai_file} with {len(tickers)} tickers")
            else:
                print(f"⚠️ Could not find portfolio_tickers line in {ai_file}")
        
        except Exception as e:
            print(f"❌ Error updating {ai_file}: {e}")
    
    # Save portfolio data
    portfolio_file = 'current_portfolio.json'
    try:
        with open(portfolio_file, 'w') as f:
            json.dump({
                "updated_at": datetime.now().isoformat(),
                "total_positions": len(positions),
                "tickers": tickers,
                "positions": positions
            }, f, indent=2)
        
        print(f"✅ Saved portfolio data to {portfolio_file}")
        
    except Exception as e:
        print(f"❌ Error saving portfolio data: {e}")

def main():
    """Sync portfolio with Alpaca account"""
    
    print("🔄 PORTFOLIO SYNC WITH ALPACA")
    print("=" * 40)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get actual positions
    print("📡 Fetching positions from Alpaca...")
    positions = get_alpaca_positions()
    
    if positions:
        print(f"\n✅ Successfully retrieved {len(positions)} positions")
        
        # Calculate totals
        total_value = sum(pos['market_value'] for pos in positions)
        total_pl = sum(pos['unrealized_pl'] for pos in positions)
        
        print(f"💼 Portfolio Summary:")
        print(f"   Total Value: ${total_value:,.2f}")
        print(f"   Total P&L: ${total_pl:+,.2f}")
        
        # Update configuration files
        print(f"\n🔧 Updating system configuration...")
        update_replit_portfolio_config(positions)
        
        print(f"\n🎯 Next Steps:")
        print(f"1. Upload updated files to Replit:")
        print(f"   - replit_main.py")
        print(f"   - current_portfolio.json")
        print(f"2. Restart your Replit app")
        print(f"3. Your phone app will now show all {len(positions)} positions!")
        
    else:
        print("❌ Could not retrieve portfolio data")
        print("Check your Alpaca API credentials in .env file")

if __name__ == "__main__":
    main()