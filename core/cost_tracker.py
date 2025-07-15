#!/usr/bin/env python3
"""
Simple Cost Tracking System
Tracks API usage with basic SQLite counter
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional

class SimpleCostTracker:
    """Simple SQLite-based API cost tracker"""
    
    def __init__(self, db_path: str = "api_usage.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                ticker TEXT,
                estimated_cost REAL NOT NULL,
                response_cached BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def track_api_call(self, endpoint: str, ticker: Optional[str] = None, 
                      cost_estimate: float = 0.02, cached: bool = False) -> bool:
        """
        Track an API call with cost
        
        Args:
            endpoint: API endpoint called (e.g., 'stock_debate', 'validate_thesis')
            ticker: Stock ticker if applicable 
            cost_estimate: Estimated cost in USD
            cached: Whether response was served from cache
            
        Returns:
            True if call was tracked, False if daily limit exceeded
        """
        try:
            # Check daily limit first
            if not self.check_daily_limit():
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO api_usage (timestamp, endpoint, ticker, estimated_cost, response_cached)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                endpoint,
                ticker,
                cost_estimate,
                cached
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error tracking API call: {e}")
            return True  # Don't block operation if tracking fails
    
    def check_daily_limit(self, limit: int = 50) -> bool:
        """
        Check if daily API call limit is exceeded
        
        Args:
            limit: Maximum API calls per day
            
        Returns:
            True if under limit, False if exceeded
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM api_usage 
                WHERE DATE(timestamp) = ? AND response_cached = FALSE
            """, (today,))
            
            call_count = cursor.fetchone()[0]
            conn.close()
            
            return call_count < limit
            
        except Exception as e:
            print(f"Error checking daily limit: {e}")
            return True  # Allow operation if check fails
    
    def get_usage_stats(self) -> dict:
        """Get basic usage statistics"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Today's calls
            cursor.execute("""
                SELECT COUNT(*), SUM(estimated_cost) FROM api_usage 
                WHERE DATE(timestamp) = ? AND response_cached = FALSE
            """, (today,))
            
            today_calls, today_cost = cursor.fetchone()
            today_cost = today_cost or 0
            
            # Total calls
            cursor.execute("""
                SELECT COUNT(*), SUM(estimated_cost) FROM api_usage 
                WHERE response_cached = FALSE
            """)
            
            total_calls, total_cost = cursor.fetchone()
            total_cost = total_cost or 0
            
            # Recent calls by endpoint
            cursor.execute("""
                SELECT endpoint, COUNT(*) FROM api_usage 
                WHERE DATE(timestamp) = ? AND response_cached = FALSE
                GROUP BY endpoint
            """, (today,))
            
            endpoint_counts = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'today_calls': today_calls or 0,
                'today_cost': round(today_cost, 3),
                'total_calls': total_calls or 0,
                'total_cost': round(total_cost, 2),
                'endpoint_counts': endpoint_counts,
                'daily_limit': 50,
                'remaining_calls': max(0, 50 - (today_calls or 0))
            }
            
        except Exception as e:
            print(f"Error getting usage stats: {e}")
            return {
                'today_calls': 0,
                'today_cost': 0,
                'total_calls': 0,
                'total_cost': 0,
                'endpoint_counts': {},
                'daily_limit': 50,
                'remaining_calls': 50
            }

# Global tracker instance
cost_tracker = SimpleCostTracker()

def track_api_call(endpoint: str, ticker: Optional[str] = None, 
                  cost_estimate: float = 0.02, cached: bool = False) -> bool:
    """Convenience function to track API calls"""
    return cost_tracker.track_api_call(endpoint, ticker, cost_estimate, cached)

def check_daily_limit() -> bool:
    """Convenience function to check daily limit"""
    return cost_tracker.check_daily_limit()

def get_usage_stats() -> dict:
    """Convenience function to get usage stats"""
    return cost_tracker.get_usage_stats()