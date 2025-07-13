#!/usr/bin/env python3
"""
Discovery System Performance Tracker
Tracks Alpha Engine vs Catalyst Engine performance and recommends best system
"""

import os
import json
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import time

@dataclass
class SystemRecommendation:
    """System recommendation with performance data"""
    ticker: str
    system_source: str  # "alpha_engine" or "catalyst_engine"
    recommendation_date: datetime
    entry_price: float
    current_price: Optional[float] = None
    exit_price: Optional[float] = None
    return_pct: Optional[float] = None
    days_held: Optional[int] = None
    status: str = "active"  # "active", "closed", "stopped_out"
    confidence_score: float = 0.0
    actual_outcome: str = "pending"  # "win", "loss", "break_even"

@dataclass
class SystemPerformance:
    """Performance metrics for each discovery system"""
    system_name: str
    total_recommendations: int
    active_positions: int
    closed_positions: int
    total_return: float
    average_return: float
    win_rate: float
    average_winner: float
    average_loser: float
    best_pick: Dict[str, Any]
    worst_pick: Dict[str, Any]
    sharpe_ratio: float
    max_drawdown: float
    last_30_days_return: float
    success_rate_by_confidence: Dict[str, float]

class DiscoverySystemTracker:
    """Tracks performance of Alpha Engine vs Catalyst Engine"""
    
    def __init__(self):
        # File paths for persistent storage
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.recommendations_file = os.path.join(base_dir, "data", "system_recommendations.json")
        self.performance_file = os.path.join(base_dir, "data", "system_performance.json")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.recommendations_file), exist_ok=True)
        
        # Load existing data
        self.recommendations = self.load_recommendations()
        
    def track_alpha_engine_recommendation(self, ticker: str, entry_price: float, confidence: float) -> str:
        """Track a recommendation from the Alpha Engine"""
        
        recommendation = SystemRecommendation(
            ticker=ticker,
            system_source="alpha_engine",
            recommendation_date=datetime.now(),
            entry_price=entry_price,
            confidence_score=confidence
        )
        
        self.recommendations.append(recommendation)
        self.save_recommendations()
        
        return f"✅ Tracking Alpha Engine recommendation: {ticker} at ${entry_price:.2f}"
    
    def track_catalyst_engine_recommendation(self, ticker: str, entry_price: float, confidence: float, catalyst_type: str) -> str:
        """Track a recommendation from the Catalyst Engine"""
        
        recommendation = SystemRecommendation(
            ticker=ticker,
            system_source="catalyst_engine",
            recommendation_date=datetime.now(),
            entry_price=entry_price,
            confidence_score=confidence
        )
        
        self.recommendations.append(recommendation)
        self.save_recommendations()
        
        return f"✅ Tracking Catalyst Engine recommendation: {ticker} at ${entry_price:.2f} ({catalyst_type})"
    
    async def update_all_positions(self) -> str:
        """Update current prices and performance for all active positions"""
        
        updated_count = 0
        
        for rec in self.recommendations:
            if rec.status == "active":
                try:
                    # Get current price
                    stock = yf.Ticker(rec.ticker)
                    current_price = stock.history(period="1d")['Close'].iloc[-1]
                    
                    # Update recommendation
                    rec.current_price = current_price
                    rec.return_pct = ((current_price - rec.entry_price) / rec.entry_price) * 100
                    rec.days_held = (datetime.now() - rec.recommendation_date).days
                    
                    # Check if it should be closed (stop loss or target hit)
                    if rec.return_pct <= -15:  # 15% stop loss
                        rec.status = "stopped_out"
                        rec.exit_price = current_price
                        rec.actual_outcome = "loss"
                    elif rec.return_pct >= 25:  # 25% profit target
                        rec.status = "closed"
                        rec.exit_price = current_price
                        rec.actual_outcome = "win"
                    
                    updated_count += 1
                    
                except Exception as e:
                    print(f"Error updating {rec.ticker}: {e}")
                    continue
        
        self.save_recommendations()
        
        return f"📊 Updated {updated_count} active positions"
    
    async def generate_system_comparison_report(self) -> str:
        """Generate comprehensive comparison of both systems"""
        
        # Update all positions first
        await self.update_all_positions()
        
        # Calculate performance for each system
        alpha_performance = self.calculate_system_performance("alpha_engine")
        catalyst_performance = self.calculate_system_performance("catalyst_engine")
        
        # Generate report
        report = "📊 **DISCOVERY SYSTEM PERFORMANCE COMPARISON**\n"
        report += "=" * 60 + "\n\n"
        
        # Alpha Engine Performance
        report += "🔥 **ALPHA ENGINE PERFORMANCE**\n"
        report += f"   • Total Recommendations: {alpha_performance.total_recommendations}\n"
        report += f"   • Win Rate: {alpha_performance.win_rate:.1f}%\n"
        report += f"   • Average Return: {alpha_performance.average_return:+.1f}%\n"
        report += f"   • Total Return: {alpha_performance.total_return:+.1f}%\n"
        report += f"   • Best Pick: {alpha_performance.best_pick.get('ticker', 'None')} ({alpha_performance.best_pick.get('return', 0):+.1f}%)\n"
        report += f"   • Active Positions: {alpha_performance.active_positions}\n\n"
        
        # Catalyst Engine Performance  
        report += "🎯 **CATALYST ENGINE PERFORMANCE**\n"
        report += f"   • Total Recommendations: {catalyst_performance.total_recommendations}\n"
        report += f"   • Win Rate: {catalyst_performance.win_rate:.1f}%\n"
        report += f"   • Average Return: {catalyst_performance.average_return:+.1f}%\n"
        report += f"   • Total Return: {catalyst_performance.total_return:+.1f}%\n"
        report += f"   • Best Pick: {catalyst_performance.best_pick.get('ticker', 'None')} ({catalyst_performance.best_pick.get('return', 0):+.1f}%)\n"
        report += f"   • Active Positions: {catalyst_performance.active_positions}\n\n"
        
        # Head-to-Head Comparison
        report += "🏆 **HEAD-TO-HEAD COMPARISON**\n"
        
        if alpha_performance.total_return > catalyst_performance.total_return:
            winner = "Alpha Engine"
            advantage = alpha_performance.total_return - catalyst_performance.total_return
        else:
            winner = "Catalyst Engine"
            advantage = catalyst_performance.total_return - alpha_performance.total_return
        
        report += f"   • **WINNER**: {winner} (+{advantage:.1f}% advantage)\n"
        
        if alpha_performance.win_rate > catalyst_performance.win_rate:
            report += f"   • **Higher Win Rate**: Alpha Engine ({alpha_performance.win_rate:.1f}% vs {catalyst_performance.win_rate:.1f}%)\n"
        else:
            report += f"   • **Higher Win Rate**: Catalyst Engine ({catalyst_performance.win_rate:.1f}% vs {alpha_performance.win_rate:.1f}%)\n"
        
        # Recommendations
        report += "\n🎯 **SYSTEM RECOMMENDATIONS**\n"
        
        if alpha_performance.total_return > catalyst_performance.total_return * 1.2:
            report += "   • **PRIMARY**: Use Alpha Engine for most trades\n"
            report += "   • **SECONDARY**: Use Catalyst Engine for binary events only\n"
        elif catalyst_performance.total_return > alpha_performance.total_return * 1.2:
            report += "   • **PRIMARY**: Use Catalyst Engine for most trades\n" 
            report += "   • **SECONDARY**: Use Alpha Engine for momentum plays only\n"
        else:
            report += "   • **BALANCED**: Both systems performing similarly\n"
            report += "   • **STRATEGY**: Use Alpha Engine in trending markets, Catalyst Engine in volatile markets\n"
        
        # Market Condition Recommendations
        report += "\n📈 **MARKET CONDITION STRATEGY**\n"
        current_vix = self.get_current_vix()
        
        if current_vix > 25:
            report += f"   • **High Volatility** (VIX: {current_vix:.1f}) → **Use Catalyst Engine**\n"
            report += "   • Binary events perform better in volatile markets\n"
        elif current_vix < 15:
            report += f"   • **Low Volatility** (VIX: {current_vix:.1f}) → **Use Alpha Engine**\n"
            report += "   • Momentum strategies work better in calm markets\n"
        else:
            report += f"   • **Normal Volatility** (VIX: {current_vix:.1f}) → **Use Both Systems**\n"
            report += "   • Balanced approach recommended\n"
        
        # Recent Performance Trend
        report += "\n📊 **RECENT PERFORMANCE (Last 30 Days)**\n"
        report += f"   • Alpha Engine: {alpha_performance.last_30_days_return:+.1f}%\n"
        report += f"   • Catalyst Engine: {catalyst_performance.last_30_days_return:+.1f}%\n"
        
        return report
    
    def calculate_system_performance(self, system_name: str) -> SystemPerformance:
        """Calculate performance metrics for a specific system"""
        
        system_recs = [r for r in self.recommendations if r.system_source == system_name]
        
        if not system_recs:
            return SystemPerformance(
                system_name=system_name,
                total_recommendations=0,
                active_positions=0,
                closed_positions=0,
                total_return=0.0,
                average_return=0.0,
                win_rate=0.0,
                average_winner=0.0,
                average_loser=0.0,
                best_pick={},
                worst_pick={},
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                last_30_days_return=0.0,
                success_rate_by_confidence={}
            )
        
        # Basic counts
        total_recs = len(system_recs)
        active_positions = len([r for r in system_recs if r.status == "active"])
        closed_positions = len([r for r in system_recs if r.status in ["closed", "stopped_out"]])
        
        # Calculate returns for closed positions
        closed_recs = [r for r in system_recs if r.status in ["closed", "stopped_out"] and r.return_pct is not None]
        
        if closed_recs:
            returns = [r.return_pct for r in closed_recs]
            total_return = sum(returns)
            average_return = total_return / len(returns)
            
            # Win/loss analysis
            winners = [r for r in closed_recs if r.return_pct > 0]
            losers = [r for r in closed_recs if r.return_pct <= 0]
            
            win_rate = (len(winners) / len(closed_recs)) * 100 if closed_recs else 0
            average_winner = sum(r.return_pct for r in winners) / len(winners) if winners else 0
            average_loser = sum(r.return_pct for r in losers) / len(losers) if losers else 0
            
            # Best and worst picks
            best_pick = max(closed_recs, key=lambda x: x.return_pct)
            worst_pick = min(closed_recs, key=lambda x: x.return_pct)
            
            # Last 30 days performance
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_recs = [r for r in closed_recs if r.recommendation_date >= thirty_days_ago]
            last_30_days_return = sum(r.return_pct for r in recent_recs) if recent_recs else 0
            
        else:
            total_return = average_return = win_rate = 0.0
            average_winner = average_loser = 0.0
            best_pick = worst_pick = {}
            last_30_days_return = 0.0
        
        return SystemPerformance(
            system_name=system_name,
            total_recommendations=total_recs,
            active_positions=active_positions,
            closed_positions=closed_positions,
            total_return=total_return,
            average_return=average_return,
            win_rate=win_rate,
            average_winner=average_winner,
            average_loser=average_loser,
            best_pick={
                'ticker': best_pick.ticker if closed_recs else 'None',
                'return': best_pick.return_pct if closed_recs else 0
            },
            worst_pick={
                'ticker': worst_pick.ticker if closed_recs else 'None', 
                'return': worst_pick.return_pct if closed_recs else 0
            },
            sharpe_ratio=0.0,  # Would calculate with risk-free rate
            max_drawdown=0.0,  # Would calculate max peak-to-trough
            last_30_days_return=last_30_days_return,
            success_rate_by_confidence={}
        )
    
    def get_current_vix(self) -> float:
        """Get current VIX level for market condition assessment"""
        try:
            vix = yf.Ticker("^VIX")
            current_vix = vix.history(period="1d")['Close'].iloc[-1]
            return float(current_vix)
        except:
            return 20.0  # Default moderate volatility
    
    def load_recommendations(self) -> List[SystemRecommendation]:
        """Load recommendations from JSON file"""
        try:
            if os.path.exists(self.recommendations_file):
                with open(self.recommendations_file, 'r') as f:
                    data = json.load(f)
                
                recommendations = []
                for item in data:
                    # Convert date string back to datetime
                    item['recommendation_date'] = datetime.fromisoformat(item['recommendation_date'])
                    recommendations.append(SystemRecommendation(**item))
                
                return recommendations
            return []
        except Exception as e:
            print(f"Error loading recommendations: {e}")
            return []
    
    def save_recommendations(self):
        """Save recommendations to JSON file"""
        try:
            # Convert to serializable format
            data = []
            for rec in self.recommendations:
                rec_dict = asdict(rec)
                rec_dict['recommendation_date'] = rec.recommendation_date.isoformat()
                data.append(rec_dict)
            
            with open(self.recommendations_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving recommendations: {e}")

# Example usage and testing
async def main():
    """Test the discovery system tracker"""
    
    tracker = DiscoverySystemTracker()
    
    # Simulate some recommendations for testing
    tracker.track_alpha_engine_recommendation("NVDA", 450.0, 0.85)
    tracker.track_catalyst_engine_recommendation("SAVA", 25.0, 0.90, "FDA_APPROVAL")
    
    # Generate comparison report
    report = await tracker.generate_system_comparison_report()
    print(report)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())