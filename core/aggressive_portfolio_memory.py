#!/usr/bin/env python3
"""
Aggressive Portfolio Memory System
Tracks winning/losing patterns for 60% monthly returns
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests

class AggressivePortfolioMemory:
    """Memory system optimized for aggressive 60% monthly returns"""
    
    def __init__(self):
        self.memory_dir = "logs/aggressive_memory"
        self.ensure_memory_dir()
        
    def ensure_memory_dir(self):
        """Create memory directory if it doesn't exist"""
        os.makedirs(self.memory_dir, exist_ok=True)
        
    def log_position_decision(self, symbol: str, action: str, reasoning: str, 
                            current_price: float, purchase_price: float = None,
                            expected_return: float = None):
        """Log aggressive position decisions for learning"""
        
        decision_log = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "action": action,
            "reasoning": reasoning,
            "current_price": current_price,
            "purchase_price": purchase_price,
            "expected_return": expected_return,
            "loss_from_purchase": ((current_price - purchase_price) / purchase_price * 100) if purchase_price else None,
            "decision_type": "aggressive_60_monthly"
        }
        
        # Save to daily log
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = f"{self.memory_dir}/decisions_{date_str}.json"
        
        # Load existing or create new
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = {"date": date_str, "decisions": []}
            
        logs["decisions"].append(decision_log)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
            
        return decision_log
        
    def log_winning_pattern(self, symbol: str, entry_price: float, exit_price: float, 
                          catalyst: str, timeframe_days: int):
        """Log successful explosive winning patterns"""
        
        return_pct = ((exit_price - entry_price) / entry_price) * 100
        
        winner_log = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "return_pct": return_pct,
            "catalyst": catalyst,
            "timeframe_days": timeframe_days,
            "pattern_type": "explosive_winner",
            "monthly_contribution": return_pct  # How much this contributed to monthly goal
        }
        
        # Save to winners log
        winners_file = f"{self.memory_dir}/winning_patterns.json"
        
        if os.path.exists(winners_file):
            with open(winners_file, 'r') as f:
                winners = json.load(f)
        else:
            winners = {"patterns": []}
            
        winners["patterns"].append(winner_log)
        
        with open(winners_file, 'w') as f:
            json.dump(winners, f, indent=2)
            
        return winner_log
        
    def log_losing_pattern(self, symbol: str, entry_price: float, exit_price: float, 
                         reason: str, timeframe_days: int):
        """Log losing patterns to avoid repeating"""
        
        loss_pct = ((exit_price - entry_price) / entry_price) * 100
        
        loser_log = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "loss_pct": loss_pct,
            "reason": reason,
            "timeframe_days": timeframe_days,
            "pattern_type": "losing_pattern",
            "lesson_learned": f"Avoid {reason} patterns, cut losses at 5%"
        }
        
        # Save to losers log
        losers_file = f"{self.memory_dir}/losing_patterns.json"
        
        if os.path.exists(losers_file):
            with open(losers_file, 'r') as f:
                losers = json.load(f)
        else:
            losers = {"patterns": []}
            
        losers["patterns"].append(loser_log)
        
        with open(losers_file, 'w') as f:
            json.dump(losers, f, indent=2)
            
        return loser_log
        
    def get_monthly_performance_summary(self) -> Dict[str, Any]:
        """Calculate monthly performance tracking toward 60% goal"""
        
        # Get current month's decisions
        current_month = datetime.now().strftime("%Y-%m")
        monthly_decisions = []
        
        for filename in os.listdir(self.memory_dir):
            if filename.startswith("decisions_") and current_month in filename:
                with open(f"{self.memory_dir}/{filename}", 'r') as f:
                    daily_log = json.load(f)
                    monthly_decisions.extend(daily_log["decisions"])
        
        # Calculate performance metrics
        sells = [d for d in monthly_decisions if d["action"] == "SELL"]
        buys = [d for d in monthly_decisions if d["action"] == "BUY"]
        
        total_decisions = len(monthly_decisions)
        aggressive_cuts = len([d for d in sells if "aggressively" in d["reasoning"]])
        
        # Get winning patterns
        winners_file = f"{self.memory_dir}/winning_patterns.json"
        monthly_wins = []
        if os.path.exists(winners_file):
            with open(winners_file, 'r') as f:
                winners = json.load(f)
                monthly_wins = [w for w in winners["patterns"] 
                              if w["timestamp"].startswith(current_month)]
        
        total_monthly_return = sum(w["return_pct"] for w in monthly_wins)
        
        return {
            "month": current_month,
            "total_decisions": total_decisions,
            "aggressive_cuts": aggressive_cuts,
            "total_monthly_return": total_monthly_return,
            "target_return": 60.0,
            "progress_to_goal": (total_monthly_return / 60.0) * 100,
            "winning_trades": len(monthly_wins),
            "avg_winner_return": sum(w["return_pct"] for w in monthly_wins) / len(monthly_wins) if monthly_wins else 0,
            "decisions_summary": {
                "sells": len(sells),
                "buys": len(buys),
                "aggressive_loss_cuts": aggressive_cuts
            },
            "last_updated": datetime.now().isoformat()
        }
        
    def get_pattern_insights(self) -> Dict[str, Any]:
        """Get insights from winning/losing patterns"""
        
        insights = {
            "winning_catalysts": {},
            "losing_patterns": {},
            "recommendations": []
        }
        
        # Analyze winning patterns
        winners_file = f"{self.memory_dir}/winning_patterns.json"
        if os.path.exists(winners_file):
            with open(winners_file, 'r') as f:
                winners = json.load(f)
                for pattern in winners["patterns"]:
                    catalyst = pattern["catalyst"]
                    if catalyst not in insights["winning_catalysts"]:
                        insights["winning_catalysts"][catalyst] = []
                    insights["winning_catalysts"][catalyst].append(pattern["return_pct"])
        
        # Analyze losing patterns
        losers_file = f"{self.memory_dir}/losing_patterns.json"
        if os.path.exists(losers_file):
            with open(losers_file, 'r') as f:
                losers = json.load(f)
                for pattern in losers["patterns"]:
                    reason = pattern["reason"]
                    if reason not in insights["losing_patterns"]:
                        insights["losing_patterns"][reason] = []
                    insights["losing_patterns"][reason].append(pattern["loss_pct"])
        
        # Generate recommendations
        if insights["winning_catalysts"]:
            best_catalyst = max(insights["winning_catalysts"].keys(), 
                              key=lambda x: sum(insights["winning_catalysts"][x]))
            insights["recommendations"].append(f"Focus on {best_catalyst} - highest average returns")
        
        if insights["losing_patterns"]:
            worst_pattern = max(insights["losing_patterns"].keys(), 
                              key=lambda x: abs(sum(insights["losing_patterns"][x])))
            insights["recommendations"].append(f"Avoid {worst_pattern} patterns - cut losses at 5%")
        
        return insights

# Global memory instance
aggressive_memory = AggressivePortfolioMemory()