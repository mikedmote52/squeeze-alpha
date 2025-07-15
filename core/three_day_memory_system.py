#!/usr/bin/env python3
"""
3-Day Memory Review System
Analyzes portfolio performance trends over the last 3 trading days for learning and optimization
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass

from pacific_time_utils import get_pacific_time, get_next_trading_day

@dataclass
class DayMemory:
    """Represents one day's portfolio memory"""
    date: str
    total_value: float
    total_pl: float
    total_pl_percent: float
    positions: List[Dict]
    ai_recommendations: List[Dict]
    executed_trades: List[Dict]
    market_conditions: Dict
    lessons_learned: List[str]

@dataclass
class TrendAnalysis:
    """Analysis of 3-day trends"""
    trend_direction: str  # "bullish", "bearish", "sideways"
    confidence: float
    key_patterns: List[str]
    successful_strategies: List[str]
    failed_strategies: List[str]
    optimization_suggestions: List[str]

class ThreeDayMemorySystem:
    """Manages 3-day rolling memory analysis for portfolio optimization"""
    
    def __init__(self, db_path: str = "portfolio_memory_3day.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Initialize database for 3-day memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                total_value REAL NOT NULL,
                total_pl REAL NOT NULL,
                total_pl_percent REAL NOT NULL,
                positions_json TEXT NOT NULL,
                ai_recommendations_json TEXT,
                executed_trades_json TEXT,
                market_conditions_json TEXT,
                lessons_learned_json TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date TEXT NOT NULL,
                trend_direction TEXT NOT NULL,
                confidence REAL NOT NULL,
                key_patterns_json TEXT,
                successful_strategies_json TEXT,
                failed_strategies_json TEXT,
                optimization_suggestions_json TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS position_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                price REAL NOT NULL,
                pl_percent REAL NOT NULL,
                volume_ratio REAL,
                ai_recommendation TEXT,
                actual_performance TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_daily_memory(self, portfolio_data: Dict, ai_recommendations: List[Dict] = None, 
                         executed_trades: List[Dict] = None, market_conditions: Dict = None) -> bool:
        """Save today's portfolio memory"""
        try:
            now_pt = get_pacific_time()
            today = now_pt.strftime('%Y-%m-%d')
            
            positions = portfolio_data.get('positions', [])
            total_value = sum(pos['market_value'] for pos in positions)
            total_pl = sum(pos['unrealized_pl'] for pos in positions)
            total_pl_percent = (total_pl / (total_value - total_pl)) * 100 if (total_value - total_pl) != 0 else 0
            
            # Generate lessons learned
            lessons_learned = self._generate_daily_lessons(positions, ai_recommendations, executed_trades)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or update daily memory
            cursor.execute('''
                INSERT OR REPLACE INTO daily_memories 
                (date, total_value, total_pl, total_pl_percent, positions_json, 
                 ai_recommendations_json, executed_trades_json, market_conditions_json, 
                 lessons_learned_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                today,
                total_value,
                total_pl,
                total_pl_percent,
                json.dumps(positions),
                json.dumps(ai_recommendations or []),
                json.dumps(executed_trades or []),
                json.dumps(market_conditions or {}),
                json.dumps(lessons_learned),
                now_pt.isoformat()
            ))
            
            # Save individual position performance
            for pos in positions:
                cursor.execute('''
                    INSERT OR REPLACE INTO position_performance
                    (symbol, date, price, pl_percent, volume_ratio, ai_recommendation, actual_performance, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pos['symbol'],
                    today,
                    pos['current_price'],
                    pos['unrealized_plpc'],
                    1.0,  # Would calculate actual volume ratio
                    self._get_ai_recommendation_for_symbol(pos['symbol'], ai_recommendations),
                    self._categorize_performance(pos['unrealized_plpc']),
                    now_pt.isoformat()
                ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Daily memory saved for {today}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving daily memory: {e}")
            return False
    
    def get_three_day_analysis(self) -> TrendAnalysis:
        """Analyze portfolio trends over the last 3 trading days"""
        try:
            three_day_memories = self._get_last_three_days_data()
            
            if len(three_day_memories) < 2:
                return TrendAnalysis(
                    trend_direction="insufficient_data",
                    confidence=0.0,
                    key_patterns=["Need more historical data"],
                    successful_strategies=[],
                    failed_strategies=[],
                    optimization_suggestions=["Continue collecting data for trend analysis"]
                )
            
            # Analyze portfolio value trend
            values = [day.total_value for day in three_day_memories]
            pl_percentages = [day.total_pl_percent for day in three_day_memories]
            
            # Calculate trend direction
            if len(values) >= 3:
                trend_direction = self._calculate_trend_direction(values, pl_percentages)
                confidence = self._calculate_trend_confidence(values, pl_percentages)
            else:
                trend_direction = "developing"
                confidence = 0.5
            
            # Identify patterns
            key_patterns = self._identify_key_patterns(three_day_memories)
            
            # Analyze strategy effectiveness
            successful_strategies, failed_strategies = self._analyze_strategy_effectiveness(three_day_memories)
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(
                three_day_memories, trend_direction, successful_strategies, failed_strategies
            )
            
            analysis = TrendAnalysis(
                trend_direction=trend_direction,
                confidence=confidence,
                key_patterns=key_patterns,
                successful_strategies=successful_strategies,
                failed_strategies=failed_strategies,
                optimization_suggestions=optimization_suggestions
            )
            
            # Save analysis to database
            self._save_trend_analysis(analysis)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error in 3-day analysis: {e}")
            return TrendAnalysis(
                trend_direction="error",
                confidence=0.0,
                key_patterns=[f"Analysis error: {str(e)}"],
                successful_strategies=[],
                failed_strategies=[],
                optimization_suggestions=[]
            )
    
    def get_position_trend_analysis(self, symbol: str) -> Dict:
        """Get 3-day trend analysis for specific position"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get last 3 days of data for this symbol
            cursor.execute('''
                SELECT date, price, pl_percent, ai_recommendation, actual_performance
                FROM position_performance 
                WHERE symbol = ?
                ORDER BY date DESC
                LIMIT 3
            ''', (symbol,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < 2:
                return {"error": "Insufficient data for trend analysis"}
            
            # Analyze price and performance trends
            dates = [row[0] for row in rows]
            prices = [row[1] for row in rows]
            pl_percentages = [row[2] for row in rows]
            recommendations = [row[3] for row in rows]
            performances = [row[4] for row in rows]
            
            # Calculate trends
            price_trend = "rising" if prices[0] > prices[-1] else "falling" if prices[0] < prices[-1] else "stable"
            pl_trend = "improving" if pl_percentages[0] > pl_percentages[-1] else "declining" if pl_percentages[0] < pl_percentages[-1] else "stable"
            
            # Check AI recommendation accuracy
            recommendation_accuracy = self._check_recommendation_accuracy(recommendations, performances)
            
            return {
                "symbol": symbol,
                "price_trend": price_trend,
                "performance_trend": pl_trend,
                "price_change_3d": ((prices[0] - prices[-1]) / prices[-1]) * 100 if prices[-1] != 0 else 0,
                "pl_change_3d": pl_percentages[0] - pl_percentages[-1],
                "ai_accuracy": recommendation_accuracy,
                "current_momentum": self._calculate_momentum(pl_percentages),
                "suggested_action": self._suggest_action_based_on_trends(price_trend, pl_trend, recommendation_accuracy)
            }
            
        except Exception as e:
            return {"error": f"Error analyzing {symbol}: {str(e)}"}
    
    def _get_last_three_days_data(self) -> List[DayMemory]:
        """Get memory data for last 3 trading days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, total_value, total_pl, total_pl_percent, positions_json,
                   ai_recommendations_json, executed_trades_json, market_conditions_json,
                   lessons_learned_json
            FROM daily_memories 
            ORDER BY date DESC
            LIMIT 3
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        memories = []
        for row in rows:
            memory = DayMemory(
                date=row[0],
                total_value=row[1],
                total_pl=row[2],
                total_pl_percent=row[3],
                positions=json.loads(row[4]) if row[4] else [],
                ai_recommendations=json.loads(row[5]) if row[5] else [],
                executed_trades=json.loads(row[6]) if row[6] else [],
                market_conditions=json.loads(row[7]) if row[7] else {},
                lessons_learned=json.loads(row[8]) if row[8] else []
            )
            memories.append(memory)
        
        return memories
    
    def _calculate_trend_direction(self, values: List[float], pl_percentages: List[float]) -> str:
        """Calculate overall trend direction"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Calculate value trend
        value_change = (values[0] - values[-1]) / values[-1] * 100
        pl_change = pl_percentages[0] - pl_percentages[-1]
        
        # Weight both value and P&L changes
        combined_trend = (value_change + pl_change) / 2
        
        if combined_trend > 2:
            return "bullish"
        elif combined_trend < -2:
            return "bearish"
        else:
            return "sideways"
    
    def _calculate_trend_confidence(self, values: List[float], pl_percentages: List[float]) -> float:
        """Calculate confidence in trend direction"""
        if len(values) < 3:
            return 0.5
        
        # Check consistency of direction
        value_changes = [values[i] - values[i+1] for i in range(len(values)-1)]
        pl_changes = [pl_percentages[i] - pl_percentages[i+1] for i in range(len(pl_percentages)-1)]
        
        # Check if changes are in same direction
        value_consistency = 1.0 if all(x >= 0 for x in value_changes) or all(x <= 0 for x in value_changes) else 0.5
        pl_consistency = 1.0 if all(x >= 0 for x in pl_changes) or all(x <= 0 for x in pl_changes) else 0.5
        
        return min((value_consistency + pl_consistency) / 2, 0.95)
    
    def _identify_key_patterns(self, memories: List[DayMemory]) -> List[str]:
        """Identify key patterns in portfolio behavior"""
        patterns = []
        
        if len(memories) < 2:
            return ["Insufficient data for pattern analysis"]
        
        # Check for consistent winners/losers
        all_symbols = set()
        for memory in memories:
            all_symbols.update(pos['symbol'] for pos in memory.positions)
        
        for symbol in all_symbols:
            symbol_performance = []
            for memory in memories:
                pos = next((p for p in memory.positions if p['symbol'] == symbol), None)
                if pos:
                    symbol_performance.append(pos['unrealized_plpc'])
            
            if len(symbol_performance) >= 2:
                if all(p > 5 for p in symbol_performance):
                    patterns.append(f"{symbol} showing consistent strong performance")
                elif all(p < -5 for p in symbol_performance):
                    patterns.append(f"{symbol} consistently underperforming")
        
        # Check for portfolio concentration
        latest_memory = memories[0]
        top_position_weight = 0
        if latest_memory.positions:
            total_value = sum(pos['market_value'] for pos in latest_memory.positions)
            max_position = max(latest_memory.positions, key=lambda x: x['market_value'])
            top_position_weight = (max_position['market_value'] / total_value) * 100
            
            if top_position_weight > 30:
                patterns.append(f"High concentration risk: {max_position['symbol']} is {top_position_weight:.1f}% of portfolio")
        
        return patterns if patterns else ["No significant patterns detected"]
    
    def _analyze_strategy_effectiveness(self, memories: List[DayMemory]) -> Tuple[List[str], List[str]]:
        """Analyze which strategies worked and which didn't"""
        successful_strategies = []
        failed_strategies = []
        
        # Analyze AI recommendation accuracy
        for memory in memories:
            for rec in memory.ai_recommendations:
                symbol = rec.get('symbol')
                recommendation = rec.get('action', '').lower()
                confidence = rec.get('confidence', 0)
                
                # Find actual performance
                pos = next((p for p in memory.positions if p['symbol'] == symbol), None)
                if pos:
                    actual_performance = pos['unrealized_plpc']
                    
                    # Check if recommendation was correct
                    if recommendation == 'buy' and actual_performance > 2:
                        successful_strategies.append(f"AI buy recommendation for {symbol} (+{actual_performance:.1f}%)")
                    elif recommendation == 'sell' and actual_performance < -2:
                        successful_strategies.append(f"AI sell recommendation for {symbol} avoided loss")
                    elif recommendation == 'buy' and actual_performance < -5:
                        failed_strategies.append(f"AI buy recommendation for {symbol} resulted in {actual_performance:.1f}% loss")
        
        # Default messages if no specific strategies identified
        if not successful_strategies and not failed_strategies:
            successful_strategies.append("Portfolio maintained stable performance")
        
        return successful_strategies, failed_strategies
    
    def _generate_optimization_suggestions(self, memories: List[DayMemory], trend_direction: str, 
                                         successful_strategies: List[str], failed_strategies: List[str]) -> List[str]:
        """Generate suggestions for portfolio optimization"""
        suggestions = []
        
        if trend_direction == "bearish":
            suggestions.append("Consider defensive positioning - reduce high-beta stocks")
            suggestions.append("Implement stop-loss orders on declining positions")
        elif trend_direction == "bullish":
            suggestions.append("Consider increasing position sizes in winning stocks")
            suggestions.append("Look for breakout opportunities in similar sectors")
        else:
            suggestions.append("Maintain current strategy while monitoring for trend development")
        
        # Analyze failed strategies for improvements
        if failed_strategies:
            suggestions.append("Review AI recommendation criteria to reduce false positives")
            if any("buy" in strategy for strategy in failed_strategies):
                suggestions.append("Tighten entry criteria for buy recommendations")
        
        # Leverage successful strategies
        if successful_strategies:
            winning_symbols = []
            for strategy in successful_strategies:
                if "AI buy recommendation" in strategy and "+" in strategy:
                    # Extract symbol from successful strategy
                    parts = strategy.split()
                    for part in parts:
                        if len(part) <= 5 and part.isalpha():
                            winning_symbols.append(part)
            
            if winning_symbols:
                suggestions.append(f"Consider similar opportunities to successful positions: {', '.join(set(winning_symbols))}")
        
        return suggestions if suggestions else ["Continue current strategy and monitor performance"]
    
    def _generate_daily_lessons(self, positions: List[Dict], ai_recommendations: List[Dict], 
                              executed_trades: List[Dict]) -> List[str]:
        """Generate lessons learned from the day"""
        lessons = []
        
        # Analyze position performance
        if positions:
            best_performer = max(positions, key=lambda x: x['unrealized_plpc'])
            worst_performer = min(positions, key=lambda x: x['unrealized_plpc'])
            
            if best_performer['unrealized_plpc'] > 5:
                lessons.append(f"Strong performance in {best_performer['symbol']} sector")
            
            if worst_performer['unrealized_plpc'] < -5:
                lessons.append(f"Weakness observed in {worst_performer['symbol']} - monitor sector trends")
        
        # Analyze AI recommendations vs actual performance
        if ai_recommendations:
            accurate_recs = 0
            total_recs = len(ai_recommendations)
            
            for rec in ai_recommendations:
                symbol = rec.get('symbol')
                pos = next((p for p in positions if p['symbol'] == symbol), None)
                if pos and rec.get('action') == 'buy' and pos['unrealized_plpc'] > 0:
                    accurate_recs += 1
            
            if total_recs > 0:
                accuracy = (accurate_recs / total_recs) * 100
                lessons.append(f"AI recommendation accuracy: {accuracy:.1f}%")
        
        return lessons if lessons else ["Continue monitoring portfolio performance"]
    
    def _get_ai_recommendation_for_symbol(self, symbol: str, ai_recommendations: List[Dict]) -> str:
        """Get AI recommendation for specific symbol"""
        if not ai_recommendations:
            return "hold"
        
        rec = next((r for r in ai_recommendations if r.get('symbol') == symbol), None)
        return rec.get('action', 'hold') if rec else 'hold'
    
    def _categorize_performance(self, pl_percent: float) -> str:
        """Categorize position performance"""
        if pl_percent > 10:
            return "strong_winner"
        elif pl_percent > 2:
            return "winner"
        elif pl_percent > -2:
            return "neutral"
        elif pl_percent > -10:
            return "loser"
        else:
            return "strong_loser"
    
    def _save_trend_analysis(self, analysis: TrendAnalysis):
        """Save trend analysis to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now_pt = get_pacific_time()
            
            cursor.execute('''
                INSERT INTO trend_analysis
                (analysis_date, trend_direction, confidence, key_patterns_json,
                 successful_strategies_json, failed_strategies_json, 
                 optimization_suggestions_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                now_pt.strftime('%Y-%m-%d'),
                analysis.trend_direction,
                analysis.confidence,
                json.dumps(analysis.key_patterns),
                json.dumps(analysis.successful_strategies),
                json.dumps(analysis.failed_strategies),
                json.dumps(analysis.optimization_suggestions),
                now_pt.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving trend analysis: {e}")

# Global instance
three_day_memory = ThreeDayMemorySystem()

def save_daily_memory(portfolio_data: Dict, ai_recommendations: List[Dict] = None, 
                     executed_trades: List[Dict] = None, market_conditions: Dict = None) -> bool:
    """Save today's portfolio memory"""
    return three_day_memory.save_daily_memory(portfolio_data, ai_recommendations, executed_trades, market_conditions)

def get_three_day_analysis() -> TrendAnalysis:
    """Get 3-day trend analysis"""
    return three_day_memory.get_three_day_analysis()

def get_position_trend_analysis(symbol: str) -> Dict:
    """Get 3-day trend analysis for specific position"""
    return three_day_memory.get_position_trend_analysis(symbol)