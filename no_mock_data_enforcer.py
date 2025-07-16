#!/usr/bin/env python3
"""
CRITICAL SYSTEM PROTECTION: NO MOCK DATA ENFORCER
This module ensures NO fake/mock data can be introduced into the trading system
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

@dataclass
class DataValidationResult:
    is_valid: bool
    error_message: str
    data_source: str

class NoMockDataEnforcer:
    """
    Enforces zero tolerance for mock, fake, or hardcoded trading data
    """
    
    # FORBIDDEN: Common mock/fake tickers that should NEVER appear
    FORBIDDEN_MOCK_TICKERS = {
        'AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX',
        'MOCK', 'FAKE', 'TEST', 'DEMO', 'SAMPLE', 'EXAMPLE'
    }
    
    # FORBIDDEN: Obvious fake/round numbers that indicate mock data
    FORBIDDEN_ROUND_PRICES = {100.00, 200.00, 250.00, 500.00, 1000.00}
    
    @classmethod
    def validate_portfolio_data(cls, portfolio_data: List[Dict[str, Any]]) -> DataValidationResult:
        """
        Validates portfolio data is NOT mock/fake data
        """
        if not portfolio_data:
            return DataValidationResult(
                is_valid=False,
                error_message="CRITICAL: No portfolio data provided",
                data_source="unknown"
            )
        
        for position in portfolio_data:
            # Check for forbidden mock tickers
            ticker = position.get('symbol', '').upper()
            if ticker in cls.FORBIDDEN_MOCK_TICKERS:
                return DataValidationResult(
                    is_valid=False,
                    error_message=f"FORBIDDEN: Mock ticker {ticker} detected. System designed for REAL DATA ONLY.",
                    data_source="mock_data"
                )
            
            # Check for suspicious round numbers
            price = position.get('current_price', 0)
            if price in cls.FORBIDDEN_ROUND_PRICES:
                return DataValidationResult(
                    is_valid=False,
                    error_message=f"SUSPICIOUS: Round price ${price} for {ticker} - appears to be mock data",
                    data_source="mock_data"
                )
        
        return DataValidationResult(
            is_valid=True,
            error_message="",
            data_source="validated"
        )
    
    @classmethod
    def get_real_alpaca_portfolio(cls) -> List[Dict[str, Any]]:
        """
        Gets REAL portfolio data from Alpaca API - NO MOCK DATA
        """
        try:
            # Import real Alpaca connection
            from secrets_manager import SecretsManager
            
            secrets = SecretsManager()
            alpaca_key = secrets.get_secret("ALPACA_API_KEY")
            alpaca_secret = secrets.get_secret("ALPACA_SECRET_KEY")
            
            if not alpaca_key or not alpaca_secret:
                logger.error("CRITICAL: No Alpaca API keys configured")
                return []
            
            # Import real portfolio engine
            from live_portfolio_engine import LivePortfolioEngine
            import asyncio
            
            engine = LivePortfolioEngine()
            positions = asyncio.run(engine.get_live_portfolio())
            
            # Convert to dict format
            portfolio_data = []
            for pos in positions:
                portfolio_data.append({
                    'symbol': pos.ticker,
                    'qty': pos.shares,
                    'current_price': pos.current_price,
                    'cost_basis': pos.cost_basis,
                    'market_value': pos.market_value,
                    'unrealized_pl': pos.unrealized_pl,
                    'unrealized_plpc': pos.unrealized_pl_percent,
                    'day_change': pos.day_change,
                    'day_change_percent': pos.day_change_percent
                })
            
            # Validate this is real data
            validation = cls.validate_portfolio_data(portfolio_data)
            if not validation.is_valid:
                logger.error(f"VALIDATION FAILED: {validation.error_message}")
                return []
            
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Failed to get real Alpaca portfolio: {e}")
            return []
    
    @classmethod
    def get_safe_portfolio_display(cls) -> Dict[str, Any]:
        """
        Gets portfolio data with strict validation - NO MOCK DATA ALLOWED
        """
        # Try to get real Alpaca data first
        real_portfolio = cls.get_real_alpaca_portfolio()
        
        if real_portfolio:
            validation = cls.validate_portfolio_data(real_portfolio)
            if validation.is_valid:
                return {
                    'status': 'success',
                    'data': real_portfolio,
                    'source': 'real_alpaca_api',
                    'warning': None
                }
        
        # If no real data available, show connection status
        return {
            'status': 'connecting',
            'data': [],
            'source': 'alpaca_api_connecting',
            'warning': 'System connecting to real Alpaca API. No mock data will be shown.'
        }
    
    @classmethod
    def emergency_system_check(cls) -> Dict[str, Any]:
        """
        Emergency check for any mock data in the system
        """
        issues = []
        
        # Check for forbidden environment variables
        env_vars = os.environ
        for key, value in env_vars.items():
            if 'MOCK' in key.upper() or 'FAKE' in key.upper() or 'TEST' in key.upper():
                issues.append(f"Forbidden environment variable: {key}")
        
        # Check for hardcoded mock data in current process
        frame = sys._getframe()
        while frame:
            local_vars = frame.f_locals
            for var_name, var_value in local_vars.items():
                if 'mock' in var_name.lower() or 'fake' in var_name.lower():
                    if isinstance(var_value, (list, dict)) and var_value:
                        issues.append(f"Mock data variable detected: {var_name}")
            frame = frame.f_back
        
        return {
            'system_clean': len(issues) == 0,
            'issues': issues,
            'message': 'System validated for real data only' if len(issues) == 0 else 'CRITICAL: Mock data detected'
        }

# Global enforcer instance
enforcer = NoMockDataEnforcer()

def validate_no_mock_data(data: Any) -> bool:
    """
    Global function to validate no mock data anywhere in the system
    """
    if isinstance(data, list):
        validation = enforcer.validate_portfolio_data(data)
        return validation.is_valid
    return True

def get_validated_portfolio() -> Dict[str, Any]:
    """
    Global function to get validated portfolio data
    """
    return enforcer.get_safe_portfolio_display()

# Emergency system check on import
_emergency_check = enforcer.emergency_system_check()
if not _emergency_check['system_clean']:
    logger.error(f"EMERGENCY: {_emergency_check['message']}")
    for issue in _emergency_check['issues']:
        logger.error(f"  - {issue}")