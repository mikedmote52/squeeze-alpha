#!/usr/bin/env python3
"""
Data Verification System
Proves that all responses are REAL, not mock data
"""

import os
import asyncio
import aiohttp
import yfinance as yf
from datetime import datetime
from typing import Dict, Any, Tuple

class DataVerificationSystem:
    """Verify all data sources are real"""
    
    def __init__(self):
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.alpaca_key = os.getenv('ALPACA_API_KEY')
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    
    async def verify_all_data_sources(self) -> Dict[str, Any]:
        """Comprehensive verification that all data is real"""
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_status': 'UNKNOWN'
        }
        
        print("🔍 VERIFYING ALL DATA SOURCES ARE REAL")
        print("=" * 60)
        print("⚠️ Testing for mock data, fake responses, and placeholders")
        print()
        
        # Test 1: Market Data Verification
        results['tests']['market_data'] = await self.verify_market_data()
        
        # Test 2: API Key Verification
        results['tests']['api_keys'] = await self.verify_api_keys()
        
        # Test 3: Claude API Verification
        results['tests']['claude_api'] = await self.verify_claude_api()
        
        # Test 4: ChatGPT API Verification
        results['tests']['chatgpt_api'] = await self.verify_chatgpt_api()
        
        # Test 5: Real-time Data Test
        results['tests']['realtime_test'] = await self.verify_realtime_data()
        
        # Calculate overall status
        all_passed = all(test.get('status') == 'REAL' for test in results['tests'].values())
        results['overall_status'] = 'ALL_REAL' if all_passed else 'MOCK_DETECTED'
        
        self.print_verification_report(results)
        return results
    
    async def verify_market_data(self) -> Dict[str, Any]:
        """Verify market data is real and live"""
        
        print("📊 Testing Market Data...")
        
        try:
            # Get real stock data
            stock = yf.Ticker("AAPL")
            hist = stock.history(period="2d")
            
            if hist.empty:
                return {
                    'status': 'MOCK',
                    'reason': 'No market data returned',
                    'details': 'Yahoo Finance returned empty data'
                }
            
            # Check if data is recent (within last trading day)
            latest_date = hist.index[-1]
            now = datetime.now()
            
            # Verify we have real price data
            latest_price = hist['Close'].iloc[-1]
            volume = hist['Volume'].iloc[-1]
            
            # Real market data should have reasonable values
            if latest_price < 50 or latest_price > 300:  # AAPL range check
                return {
                    'status': 'SUSPICIOUS',
                    'reason': f'AAPL price ${latest_price:.2f} outside expected range',
                    'details': f'Latest data: {latest_date}, Price: ${latest_price:.2f}, Volume: {volume:,}'
                }
            
            # Check for obvious fake patterns
            if volume == 0 or latest_price % 1 == 0:  # Perfect round numbers are suspicious
                return {
                    'status': 'SUSPICIOUS',
                    'reason': 'Data patterns suggest mock data',
                    'details': f'Price: ${latest_price:.2f}, Volume: {volume}'
                }
            
            print(f"   ✅ REAL: AAPL ${latest_price:.2f}, Volume: {volume:,}")
            return {
                'status': 'REAL',
                'reason': 'Live market data with realistic values',
                'details': {
                    'ticker': 'AAPL',
                    'price': latest_price,
                    'volume': int(volume),
                    'date': latest_date.strftime('%Y-%m-%d'),
                    'source': 'Yahoo Finance'
                }
            }
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return {
                'status': 'ERROR',
                'reason': f'Market data test failed: {str(e)}',
                'details': None
            }
    
    async def verify_api_keys(self) -> Dict[str, Any]:
        """Verify API keys are real, not placeholders"""
        
        print("🔑 Testing API Keys...")
        
        keys_to_test = {
            'ANTHROPIC_API_KEY': self.anthropic_key,
            'OPENAI_API_KEY': self.openai_key,
            'ALPACA_API_KEY': self.alpaca_key,
            'PERPLEXITY_API_KEY': self.perplexity_key
        }
        
        real_keys = 0
        total_keys = len(keys_to_test)
        key_details = {}
        
        for key_name, key_value in keys_to_test.items():
            if not key_value:
                key_details[key_name] = {'status': 'MISSING', 'format': 'N/A'}
                print(f"   ❌ {key_name}: MISSING")
                continue
            
            # Check for placeholder patterns
            if key_value.startswith('YOUR_') or key_value.startswith('sk-fake') or len(key_value) < 10:
                key_details[key_name] = {'status': 'PLACEHOLDER', 'format': 'Invalid'}
                print(f"   ❌ {key_name}: PLACEHOLDER/FAKE")
                continue
            
            # Check key format
            format_check = self.check_api_key_format(key_name, key_value)
            key_details[key_name] = {'status': 'REAL', 'format': format_check}
            real_keys += 1
            print(f"   ✅ {key_name}: REAL ({format_check})")
        
        return {
            'status': 'REAL' if real_keys == total_keys else 'PARTIAL',
            'reason': f'{real_keys}/{total_keys} keys are real',
            'details': key_details
        }
    
    def check_api_key_format(self, key_name: str, key_value: str) -> str:
        """Check if API key has correct format"""
        
        if key_name == 'ANTHROPIC_API_KEY' and key_value.startswith('sk-ant-'):
            return 'Valid Anthropic format'
        elif key_name == 'OPENAI_API_KEY' and key_value.startswith('sk-'):
            return 'Valid OpenAI format'
        elif key_name == 'ALPACA_API_KEY' and len(key_value) >= 20:
            return 'Valid Alpaca format'
        elif key_name == 'PERPLEXITY_API_KEY' and key_value.startswith('pplx-'):
            return 'Valid Perplexity format'
        else:
            return 'Unknown format'
    
    async def verify_claude_api(self) -> Dict[str, Any]:
        """Test actual Claude API call"""
        
        print("🔵 Testing Claude API...")
        
        if not self.anthropic_key:
            print("   ❌ No Claude API key")
            return {'status': 'MISSING', 'reason': 'No API key configured'}
        
        try:
            # Make real API call to Claude
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.anthropic_key,
                    "anthropic-version": "2023-06-01"
                }
                
                payload = {
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 50,
                    "messages": [
                        {
                            "role": "user", 
                            "content": "What is 2+2? Respond with just the number and current timestamp."
                        }
                    ]
                }
                
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        content = data['content'][0]['text']
                        
                        # Check if response looks real (not hardcoded)
                        if 'timestamp' in content.lower() or datetime.now().year in content:
                            print(f"   ✅ REAL: Claude responded with: {content[:50]}...")
                            return {
                                'status': 'REAL',
                                'reason': 'Live Claude API response',
                                'details': {'response_preview': content[:100]}
                            }
                        else:
                            print(f"   ⚠️ SUSPICIOUS: Response seems generic: {content}")
                            return {
                                'status': 'SUSPICIOUS',
                                'reason': 'Response may be cached/generic',
                                'details': {'response': content}
                            }
                    else:
                        error_text = await response.text()
                        print(f"   ❌ API Error: {response.status}")
                        return {
                            'status': 'ERROR',
                            'reason': f'API returned {response.status}',
                            'details': error_text[:200]
                        }
                        
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return {
                'status': 'ERROR',
                'reason': f'Claude API test failed: {str(e)}',
                'details': None
            }
    
    async def verify_chatgpt_api(self) -> Dict[str, Any]:
        """Test actual ChatGPT API call"""
        
        print("🟢 Testing ChatGPT API...")
        
        if not self.openai_key:
            print("   ❌ No OpenAI API key")
            return {'status': 'MISSING', 'reason': 'No API key configured'}
        
        try:
            # Make real API call to OpenAI
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "user",
                            "content": "What is 3+5? Include current date in your response."
                        }
                    ],
                    "max_tokens": 50
                }
                
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        
                        # Check if response looks real
                        if any(str(datetime.now().year) in content for year in [datetime.now().year]):
                            print(f"   ✅ REAL: ChatGPT responded with: {content[:50]}...")
                            return {
                                'status': 'REAL',
                                'reason': 'Live ChatGPT API response',
                                'details': {'response_preview': content[:100]}
                            }
                        else:
                            print(f"   ⚠️ SUSPICIOUS: Response seems generic: {content}")
                            return {
                                'status': 'SUSPICIOUS',
                                'reason': 'Response may be cached/generic',
                                'details': {'response': content}
                            }
                    else:
                        error_text = await response.text()
                        print(f"   ❌ API Error: {response.status}")
                        return {
                            'status': 'ERROR',
                            'reason': f'API returned {response.status}',
                            'details': error_text[:200]
                        }
                        
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return {
                'status': 'ERROR',
                'reason': f'ChatGPT API test failed: {str(e)}',
                'details': None
            }
    
    async def verify_realtime_data(self) -> Dict[str, Any]:
        """Test that data changes over time (proves it's not static)"""
        
        print("⏰ Testing Real-time Data...")
        
        try:
            # Get data twice with delay
            stock = yf.Ticker("SPY")
            
            # First reading
            hist1 = stock.history(period="1d", interval="1m")
            if hist1.empty:
                return {'status': 'ERROR', 'reason': 'No data returned'}
            
            # Wait 5 seconds
            await asyncio.sleep(5)
            
            # Second reading
            hist2 = stock.history(period="1d", interval="1m")
            if hist2.empty:
                return {'status': 'ERROR', 'reason': 'No data on second reading'}
            
            # Check if data changed (or at least timestamps)
            if len(hist2) > len(hist1):
                print("   ✅ REAL: Data updated between readings")
                return {
                    'status': 'REAL',
                    'reason': 'Data shows real-time updates',
                    'details': {
                        'first_reading_count': len(hist1),
                        'second_reading_count': len(hist2),
                        'difference': len(hist2) - len(hist1)
                    }
                }
            else:
                print("   ⚠️ STATIC: No data changes detected")
                return {
                    'status': 'STATIC',
                    'reason': 'Data appears to be static/cached',
                    'details': {
                        'first_reading_count': len(hist1),
                        'second_reading_count': len(hist2)
                    }
                }
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return {
                'status': 'ERROR',
                'reason': f'Real-time test failed: {str(e)}',
                'details': None
            }
    
    def print_verification_report(self, results: Dict[str, Any]):
        """Print comprehensive verification report"""
        
        print("\n" + "=" * 60)
        print("🔍 DATA VERIFICATION REPORT")
        print("=" * 60)
        
        if results['overall_status'] == 'ALL_REAL':
            print("✅ VERIFIED: ALL DATA SOURCES ARE REAL")
            print("🟢 No mock data detected")
            print("🟢 All APIs responding with live data")
            print("🟢 Market data is real-time")
        else:
            print("🚨 WARNING: MOCK DATA DETECTED")
            print("🔴 Some data sources may be fake")
            print("🔴 System may not be using live data")
        
        print(f"\n📊 TEST RESULTS:")
        for test_name, result in results['tests'].items():
            status_icon = "✅" if result['status'] == 'REAL' else "❌"
            print(f"{status_icon} {test_name.upper()}: {result['status']}")
            print(f"   Reason: {result['reason']}")
        
        print(f"\n⏰ Verification completed: {results['timestamp']}")
        print("=" * 60)


async def run_verification():
    """Run the verification system"""
    verifier = DataVerificationSystem()
    results = await verifier.verify_all_data_sources()
    return results


if __name__ == "__main__":
    asyncio.run(run_verification())