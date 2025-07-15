#!/usr/bin/env python3
"""
API Cost Tracking System
Tracks usage and costs across all APIs to monitor daily/weekly/monthly spending
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
from dataclasses import dataclass, asdict

@dataclass
class APICall:
    """Single API call record"""
    timestamp: str
    api_name: str
    endpoint: str
    cost: float
    tokens_used: int = 0
    request_type: str = "GET"
    success: bool = True

class APIcostTracker:
    """Track API usage and costs across all services"""
    
    def __init__(self, db_path: str = "api_costs.db"):
        self.db_path = db_path
        self.setup_database()
        
        # API cost estimates (per request unless noted)
        self.api_costs = {
            "openrouter": {"base_cost": 0.002, "per_token": 0.000001},  # ~$0.002 per request
            "alphavantage": {"base_cost": 0.001, "daily_limit": 500},    # Free tier
            "finnhub": {"base_cost": 0.0005, "monthly_limit": 60000},   # Free tier
            "fmp": {"base_cost": 0.001, "daily_limit": 250},            # Free tier
            "benzinga": {"base_cost": 0.01, "per_request": True},       # Premium
            "perplexity": {"base_cost": 0.005, "per_token": 0.000002},  # ~$0.005 per request
            "news_api": {"base_cost": 0.0001, "daily_limit": 1000},     # Free tier
            "youtube": {"base_cost": 0.0001, "daily_limit": 10000},     # Free tier
            "twitter": {"base_cost": 0.005, "per_request": True},       # Premium
            "fred": {"base_cost": 0.0001, "daily_limit": 1000},         # Free tier
            "fda": {"base_cost": 0.0001, "unlimited": True},            # Free
            "uphold": {"base_cost": 0.001, "per_request": True},        # Trading fees
            "alpaca": {"base_cost": 0.0001, "unlimited": True},         # Free paper trading
            "yfinance": {"base_cost": 0.0001, "unlimited": True}        # Free
        }
    
    def setup_database(self):
        """Initialize SQLite database for cost tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                api_name TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                cost REAL NOT NULL,
                tokens_used INTEGER DEFAULT 0,
                request_type TEXT DEFAULT 'GET',
                success BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON api_calls(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_api_name 
            ON api_calls(api_name)
        ''')
        
        conn.commit()
        conn.close()
    
    def log_api_call(self, api_name: str, endpoint: str, tokens_used: int = 0, 
                     request_type: str = "GET", success: bool = True) -> float:
        """Log an API call and return estimated cost"""
        cost = self.calculate_cost(api_name, tokens_used)
        
        call = APICall(
            timestamp=datetime.now().isoformat(),
            api_name=api_name,
            endpoint=endpoint,
            cost=cost,
            tokens_used=tokens_used,
            request_type=request_type,
            success=success
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_calls 
            (timestamp, api_name, endpoint, cost, tokens_used, request_type, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (call.timestamp, call.api_name, call.endpoint, call.cost, 
              call.tokens_used, call.request_type, call.success))
        
        conn.commit()
        conn.close()
        
        return cost
    
    def calculate_cost(self, api_name: str, tokens_used: int = 0) -> float:
        """Calculate estimated cost for an API call"""
        api_name = api_name.lower()
        
        if api_name not in self.api_costs:
            return 0.001  # Default small cost for unknown APIs
        
        config = self.api_costs[api_name]
        base_cost = config.get("base_cost", 0.001)
        
        if "per_token" in config and tokens_used > 0:
            token_cost = config["per_token"] * tokens_used
            return base_cost + token_cost
        
        return base_cost
    
    def get_usage_summary(self, days: int = 1) -> Dict:
        """Get usage summary for specified time period"""
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total costs by API
        cursor.execute('''
            SELECT api_name, 
                   COUNT(*) as calls,
                   SUM(cost) as total_cost,
                   SUM(tokens_used) as total_tokens
            FROM api_calls 
            WHERE timestamp >= ? AND success = 1
            GROUP BY api_name
            ORDER BY total_cost DESC
        ''', (start_date,))
        
        api_breakdown = {}
        total_cost = 0
        total_calls = 0
        
        for row in cursor.fetchall():
            api_name, calls, cost, tokens = row
            api_breakdown[api_name] = {
                "calls": calls,
                "cost": round(cost, 4),
                "tokens": tokens or 0,
                "avg_cost_per_call": round(cost / calls, 4) if calls > 0 else 0
            }
            total_cost += cost
            total_calls += calls
        
        # Recent activity
        cursor.execute('''
            SELECT timestamp, api_name, endpoint, cost
            FROM api_calls 
            WHERE timestamp >= ? AND success = 1
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (start_date,))
        
        recent_calls = []
        for row in cursor.fetchall():
            timestamp, api_name, endpoint, cost = row
            recent_calls.append({
                "timestamp": timestamp,
                "api": api_name,
                "endpoint": endpoint,
                "cost": round(cost, 4)
            })
        
        conn.close()
        
        return {
            "period_days": days,
            "total_cost": round(total_cost, 4),
            "total_calls": total_calls,
            "api_breakdown": api_breakdown,
            "recent_calls": recent_calls,
            "estimated_monthly": round(total_cost * (30 / days), 2) if days > 0 else 0
        }
    
    def get_cost_alerts(self) -> List[Dict]:
        """Check for cost alerts and spending patterns"""
        alerts = []
        
        # Daily costs
        daily_summary = self.get_usage_summary(1)
        weekly_summary = self.get_usage_summary(7)
        monthly_summary = self.get_usage_summary(30)
        
        # Alert thresholds
        if daily_summary["total_cost"] > 5.0:
            alerts.append({
                "type": "high_daily_cost",
                "message": f"High daily cost: ${daily_summary['total_cost']:.2f}",
                "severity": "warning"
            })
        
        if monthly_summary["total_cost"] > 100.0:
            alerts.append({
                "type": "high_monthly_cost", 
                "message": f"High monthly cost: ${monthly_summary['total_cost']:.2f}",
                "severity": "error"
            })
        
        # Check for expensive APIs
        for api_name, stats in daily_summary["api_breakdown"].items():
            if stats["cost"] > 2.0:
                alerts.append({
                    "type": "expensive_api",
                    "message": f"{api_name} cost ${stats['cost']:.2f} today",
                    "severity": "info"
                })
        
        return alerts

# Global instance
cost_tracker = APIcostTracker()

def log_api_call(api_name: str, endpoint: str, tokens_used: int = 0, 
                 request_type: str = "GET", success: bool = True) -> float:
    """Convenience function to log API calls"""
    return cost_tracker.log_api_call(api_name, endpoint, tokens_used, request_type, success)

def get_cost_summary(days: int = 1) -> Dict:
    """Convenience function to get cost summary"""
    return cost_tracker.get_usage_summary(days)