#!/usr/bin/env python3
"""
AI Analysis Cache System
Prevents repeated API calls and backend crashes during scheduled analysis periods
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading
from pathlib import Path

class AIAnalysisCache:
    """
    Caches AI analysis results to prevent repeated API calls
    Only refreshes during scheduled periods or when forced
    """
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "ai_analysis_cache.json"
        self.lock = threading.Lock()
        
        # Load existing cache
        self.cache = self._load_cache()
        
        # Cache settings
        self.cache_duration_minutes = 30  # Cache valid for 30 minutes
        self.scheduled_refresh_hours = [5, 9, 13, 17]  # 5:30am, 9:30am, 1:30pm, 5:30pm PT
        
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _get_cache_key(self, symbol: str, analysis_type: str, purchase_price: float = None) -> str:
        """Generate cache key for analysis"""
        key = f"{symbol}_{analysis_type}"
        if purchase_price:
            key += f"_{purchase_price}"
        return key
    
    def _is_cache_valid(self, timestamp: str) -> bool:
        """Check if cache entry is still valid"""
        try:
            cache_time = datetime.fromisoformat(timestamp)
            expiry_time = cache_time + timedelta(minutes=self.cache_duration_minutes)
            return datetime.now() < expiry_time
        except:
            return False
    
    def _is_scheduled_refresh_time(self) -> bool:
        """Check if current time is within scheduled refresh window"""
        now = datetime.now()
        current_hour = now.hour
        
        # Check if we're within 30 minutes of scheduled refresh time
        for scheduled_hour in self.scheduled_refresh_hours:
            if abs(current_hour - scheduled_hour) <= 0.5:  # 30 minute window
                return True
        return False
    
    def get_analysis(self, symbol: str, analysis_type: str, purchase_price: float = None) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis if available and valid
        
        Args:
            symbol: Stock symbol
            analysis_type: Type of analysis (full, collaborative, etc.)
            purchase_price: Purchase price for position analysis
            
        Returns:
            Cached analysis dict or None if not available/expired
        """
        with self.lock:
            cache_key = self._get_cache_key(symbol, analysis_type, purchase_price)
            
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if self._is_cache_valid(entry['timestamp']):
                    print(f"🎯 Cache HIT: {symbol} {analysis_type} (cached at {entry['timestamp']})")
                    return entry['data']
                else:
                    print(f"🎯 Cache EXPIRED: {symbol} {analysis_type}")
                    # Remove expired entry
                    del self.cache[cache_key]
                    self._save_cache()
            
            print(f"🎯 Cache MISS: {symbol} {analysis_type}")
            return None
    
    def set_analysis(self, symbol: str, analysis_type: str, data: Dict[str, Any], purchase_price: float = None):
        """
        Cache analysis result
        
        Args:
            symbol: Stock symbol
            analysis_type: Type of analysis
            data: Analysis result to cache
            purchase_price: Purchase price for position analysis
        """
        with self.lock:
            cache_key = self._get_cache_key(symbol, analysis_type, purchase_price)
            
            entry = {
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'symbol': symbol,
                'analysis_type': analysis_type,
                'purchase_price': purchase_price
            }
            
            self.cache[cache_key] = entry
            self._save_cache()
            
            print(f"🎯 Cached: {symbol} {analysis_type} at {entry['timestamp']}")
    
    def should_refresh_analysis(self, symbol: str, analysis_type: str, purchase_price: float = None) -> bool:
        """
        Determine if analysis should be refreshed
        
        Returns True if:
        - No cached data exists
        - Cached data is expired
        - Currently in scheduled refresh window
        """
        with self.lock:
            cache_key = self._get_cache_key(symbol, analysis_type, purchase_price)
            
            # No cache = refresh
            if cache_key not in self.cache:
                return True
                
            # Expired cache = refresh
            if not self._is_cache_valid(self.cache[cache_key]['timestamp']):
                return True
                
            # During scheduled refresh window = refresh
            if self._is_scheduled_refresh_time():
                return True
                
            return False
    
    def clear_cache(self):
        """Clear all cached analysis"""
        with self.lock:
            self.cache = {}
            self._save_cache()
            print("🎯 Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_entries = len(self.cache)
            valid_entries = sum(1 for entry in self.cache.values() 
                              if self._is_cache_valid(entry['timestamp']))
            
            return {
                'total_entries': total_entries,
                'valid_entries': valid_entries,
                'expired_entries': total_entries - valid_entries,
                'cache_duration_minutes': self.cache_duration_minutes,
                'scheduled_refresh_hours': self.scheduled_refresh_hours,
                'next_scheduled_refresh': self._get_next_refresh_time()
            }
    
    def _get_next_refresh_time(self) -> str:
        """Get next scheduled refresh time"""
        now = datetime.now()
        today_refreshes = [now.replace(hour=h, minute=30, second=0, microsecond=0) 
                          for h in self.scheduled_refresh_hours]
        
        future_refreshes = [t for t in today_refreshes if t > now]
        
        if future_refreshes:
            return future_refreshes[0].isoformat()
        else:
            # Next refresh is tomorrow at first scheduled time
            tomorrow = now + timedelta(days=1)
            next_refresh = tomorrow.replace(hour=self.scheduled_refresh_hours[0], 
                                          minute=30, second=0, microsecond=0)
            return next_refresh.isoformat()

# Global cache instance
ai_cache = AIAnalysisCache()