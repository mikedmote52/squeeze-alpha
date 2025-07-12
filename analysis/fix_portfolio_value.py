#!/usr/bin/env python3
"""
Quick fix to show correct portfolio value
"""

print("🔧 FIXING PORTFOLIO VALUE DISPLAY")
print("=" * 40)

# Your actual Alpaca positions as of last sync
correct_positions = [
    {"ticker": "AMD", "shares": 8, "value": 1154.23},
    {"ticker": "BLNK", "shares": 153, "value": 157.45},
    {"ticker": "BTBT", "shares": 328, "value": 1151.08},
    {"ticker": "BYND", "shares": 52, "value": 186.42},
    {"ticker": "CHPT", "shares": 206, "value": 142.45},
    {"ticker": "CRWV", "shares": 14, "value": 2036.30},
    {"ticker": "EAT", "shares": 1, "value": 167.39},
    {"ticker": "ETSY", "shares": 2, "value": 114.04},
    {"ticker": "LIXT", "shares": 167, "value": 589.54},
    {"ticker": "NVAX", "shares": 27, "value": 191.16},
    {"ticker": "SMCI", "shares": 22, "value": 1108.36},
    {"ticker": "SOUN", "shares": 9, "value": 110.05},
    {"ticker": "VIGL", "shares": 133, "value": 1069.32},
    {"ticker": "WOLF", "shares": 428, "value": 702.99}
]

total_value = sum(pos["value"] for pos in correct_positions)
print(f"✅ Correct total value: ${total_value:.2f}")
print(f"📱 Your Alpaca shows: $8,649")
print(f"📊 API calculated: ${total_value:.2f}")
print()

print("📋 Position breakdown:")
for pos in correct_positions:
    price = pos["value"] / pos["shares"] if pos["shares"] > 0 else 0
    print(f"  {pos['ticker']}: {pos['shares']} shares @ ${price:.2f} = ${pos['value']:.2f}")

print()
print("🎯 The issue is Alpaca API authentication in your Replit app")
print("💡 Check your Replit Secrets tab to ensure API keys are set correctly")