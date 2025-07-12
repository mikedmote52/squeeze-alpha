"""
AI Trading System - Monitoring Module
"""

# Lazy imports to avoid dependency issues at module level
def get_portfolio_monitor():
    """Get portfolio monitor instance"""
    try:
        from .portfolio_monitor import PortfolioMonitor
        return PortfolioMonitor()
    except ImportError as e:
        import logging
        logging.warning(f"Portfolio monitor not available: {e}")
        return None

def get_performance_analytics():
    """Get performance analytics instance"""
    try:
        from .performance_analytics import PerformanceAnalytics
        return PerformanceAnalytics()
    except ImportError as e:
        import logging
        logging.warning(f"Performance analytics not available: {e}")
        return None

def get_risk_monitor():
    """Get risk monitor instance"""
    try:
        from .risk_monitoring import RiskMonitor
        return RiskMonitor()
    except ImportError as e:
        import logging
        logging.warning(f"Risk monitor not available: {e}")
        return None

def get_analytics_dashboard():
    """Get analytics dashboard instance"""
    try:
        from .dashboard import AnalyticsDashboard
        return AnalyticsDashboard()
    except ImportError as e:
        import logging
        logging.warning(f"Analytics dashboard not available: {e}")
        return None

__all__ = [
    'get_portfolio_monitor',
    'get_performance_analytics',
    'get_risk_monitor', 
    'get_analytics_dashboard'
]