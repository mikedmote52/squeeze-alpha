#!/usr/bin/env python3
"""
TRADING SAFETY ENFORCER
Prevents any trading operations when mock data is detected
"""

import functools
from typing import Any, Callable
from trading_safety_validator import TradingSafetyValidator

class TradingSafetyEnforcer:
    """Enforces trading safety by blocking operations when mock data is detected"""
    
    def __init__(self):
        self.validator = TradingSafetyValidator()
        self._safety_checked = False
        self._is_safe = False
    
    def require_real_data(self, func: Callable) -> Callable:
        """Decorator that blocks functions when mock data is detected"""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self._safety_checked:
                print("🛡️ Performing mandatory safety check before trading operation...")
                self._is_safe, violations = self.validator.validate_all_systems()
                self._safety_checked = True
            
            if not self._is_safe:
                error_msg = f"""
🚨 TRADING OPERATION BLOCKED FOR SAFETY 🚨

Function: {func.__name__}
Reason: Mock data detected in critical systems

This operation could affect real money based on fake data.
System will not proceed until all safety violations are fixed.

Run 'python3 core/trading_safety_validator.py' to see issues.
"""
                raise RuntimeError(error_msg)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    def block_if_unsafe(self):
        """Immediately check and block if system is unsafe"""
        is_safe, violations = self.validator.validate_all_systems()
        
        if not is_safe:
            raise RuntimeError(
                "TRADING BLOCKED: Mock data detected in critical systems. "
                "Fix safety violations before proceeding."
            )


# Global enforcer instance
safety_enforcer = TradingSafetyEnforcer()

# Decorator for trading functions
def safe_for_trading(func):
    """Decorator that ensures function only runs with real data"""
    return safety_enforcer.require_real_data(func)

# Emergency stop function
def emergency_stop_if_unsafe():
    """Emergency function to stop trading if unsafe"""
    safety_enforcer.block_if_unsafe()