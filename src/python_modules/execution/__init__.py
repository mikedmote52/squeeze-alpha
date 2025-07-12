"""
AI Trading System - Execution Module
"""

# Lazy imports to avoid dependency issues at module level
def get_position_manager():
    """Get position manager instance"""
    try:
        from .position_manager import get_position_manager as _get_position_manager
        return _get_position_manager()
    except ImportError as e:
        import logging
        logging.warning(f"Position manager not available: {e}")
        return None

def get_trade_executor():
    """Get trade executor instance"""
    try:
        from .trade_executor import get_trade_executor as _get_trade_executor
        return _get_trade_executor()
    except ImportError as e:
        import logging
        logging.warning(f"Trade executor not available: {e}")
        return None

def get_risk_manager():
    """Get risk manager instance"""
    try:
        from .risk_manager import RiskManager
        return RiskManager()
    except ImportError as e:
        import logging
        logging.warning(f"Risk manager not available: {e}")
        return None

def get_human_override_system():
    """Get human override system instance"""
    try:
        from .human_override import HumanOverrideSystem
        return HumanOverrideSystem()
    except ImportError as e:
        import logging
        logging.warning(f"Human override system not available: {e}")
        return None

__all__ = [
    'get_position_manager',
    'get_trade_executor', 
    'get_risk_manager',
    'get_human_override_system'
]