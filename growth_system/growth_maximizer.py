#!/usr/bin/env python3
"""
GROWTH MAXIMIZATION ENGINE
Integrated with existing AI trading system to maximize investment growth over short time periods
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

# Add core modules to path
sys.path.append('./core')
sys.path.append('./utils')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GrowthMaximizer:
    """
    Core growth maximization engine that integrates with existing AI trading system
    """
    
    def __init__(self):
        self.goal = "Maximize investment growth over short time periods"
        self.active_opportunities = []
        self.position_targets = {}
        self.risk_limits = {
            'max_position_size': 0.25,  # 25% max per position
            'max_daily_loss': 0.05,     # 5% max daily loss
            'growth_target': 0.15       # 15% growth target
        }
        self.performance_metrics = {
            'total_return': 0.0,
            'win_rate': 0.0,
            'avg_hold_time': 0.0,
            'opportunities_found': 0
        }
        
    def scan_for_growth_opportunities(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scan market data for high-growth opportunities
        """
        opportunities = []
        
        if not market_data or 'symbols' not in market_data:
            return opportunities
            
        for symbol, data in market_data['symbols'].items():
            if self._is_growth_opportunity(symbol, data):
                opportunity = {
                    'symbol': symbol,
                    'growth_score': self._calculate_growth_score(data),
                    'entry_price': data.get('current_price', 0),
                    'target_price': self._calculate_target_price(data),
                    'risk_level': self._assess_risk(data),
                    'timeframe': '1-3 days',
                    'confidence': self._calculate_confidence(data),
                    'timestamp': datetime.now().isoformat()
                }
                opportunities.append(opportunity)
                
        # Sort by growth score (highest first)
        opportunities.sort(key=lambda x: x['growth_score'], reverse=True)
        
        # Limit to top 10 opportunities
        return opportunities[:10]
    
    def _is_growth_opportunity(self, symbol: str, data: Dict[str, Any]) -> bool:
        """
        Determine if a symbol represents a growth opportunity
        """
        # Basic filters
        if not data.get('current_price') or data.get('current_price') <= 0:
            return False
            
        # Volume requirement (lowered threshold)
        if data.get('volume', 0) < 50000:
            return False
            
        # Price movement analysis (more lenient)
        price_change = data.get('price_change_percent', 0)
        if price_change < -15 or price_change > 25:  # Avoid extreme moves
            return False
            
        # Always consider stocks with positive momentum
        if price_change > 0:
            return True
            
        # Technical indicators
        rsi = data.get('rsi', 50)
        if 25 <= rsi <= 75:  # Broader RSI range
            return True
            
        # Momentum indicators
        if data.get('momentum_score', 0) > 5:
            return True
            
        # Market conditions
        if data.get('sector_performance', 0) > 0:
            return True
            
        return False
    
    def _calculate_growth_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate growth potential score (0-100)
        """
        score = 0
        
        # Volume score (20 points)
        volume = data.get('volume', 0)
        if volume > 1000000:
            score += 20
        elif volume > 500000:
            score += 15
        elif volume > 100000:
            score += 10
            
        # Price momentum (25 points)
        price_change = data.get('price_change_percent', 0)
        if 2 <= price_change <= 8:
            score += 25
        elif 0 <= price_change <= 2:
            score += 15
            
        # RSI score (20 points)
        rsi = data.get('rsi', 50)
        if 30 <= rsi <= 40:  # Oversold but recovering
            score += 20
        elif 60 <= rsi <= 70:  # Strong momentum
            score += 15
            
        # Technical indicators (20 points)
        if data.get('macd_signal') == 'bullish':
            score += 10
        if data.get('moving_average_trend') == 'upward':
            score += 10
            
        # Market conditions (15 points)
        if data.get('sector_performance', 0) > 0:
            score += 15
            
        return min(score, 100)
    
    def _calculate_target_price(self, data: Dict[str, Any]) -> float:
        """
        Calculate target price based on growth analysis
        """
        current_price = data.get('current_price', 0)
        if current_price <= 0:
            return 0
            
        # Base target: 8-15% growth
        base_growth = 0.12  # 12% target
        
        # Adjust based on volatility
        volatility = data.get('volatility', 0.2)
        if volatility > 0.3:
            base_growth *= 1.5  # Higher target for volatile stocks
        elif volatility < 0.1:
            base_growth *= 0.8  # Lower target for stable stocks
            
        return current_price * (1 + base_growth)
    
    def _assess_risk(self, data: Dict[str, Any]) -> str:
        """
        Assess risk level for the opportunity
        """
        risk_score = 0
        
        # Volatility risk
        volatility = data.get('volatility', 0.2)
        if volatility > 0.4:
            risk_score += 3
        elif volatility > 0.2:
            risk_score += 2
        else:
            risk_score += 1
            
        # Beta risk
        beta = data.get('beta', 1.0)
        if beta > 1.5:
            risk_score += 2
        elif beta > 1.0:
            risk_score += 1
            
        # Recent performance risk
        recent_performance = data.get('recent_performance', 0)
        if recent_performance < -0.2:
            risk_score += 2
            
        if risk_score >= 6:
            return 'high'
        elif risk_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """
        Calculate confidence level (0-1)
        """
        confidence = 0.5  # Base confidence
        
        # Volume confidence
        volume = data.get('volume', 0)
        if volume > 1000000:
            confidence += 0.2
        elif volume > 500000:
            confidence += 0.1
            
        # Technical indicators confidence
        if data.get('macd_signal') == 'bullish':
            confidence += 0.1
        if data.get('moving_average_trend') == 'upward':
            confidence += 0.1
            
        # Market conditions confidence
        if data.get('sector_performance', 0) > 0.05:
            confidence += 0.1
            
        return min(confidence, 1.0)
    
    def optimize_position_sizes(self, opportunities: List[Dict[str, Any]], 
                              portfolio_value: float) -> Dict[str, float]:
        """
        Optimize position sizes for maximum growth
        """
        position_sizes = {}
        
        if not opportunities or portfolio_value <= 0:
            return position_sizes
            
        # Calculate total allocation budget
        total_budget = portfolio_value * 0.8  # Use 80% of portfolio
        
        # Weight opportunities by growth score and confidence
        weighted_opportunities = []
        total_weight = 0
        
        for opp in opportunities:
            weight = opp['growth_score'] * opp['confidence']
            
            # Adjust for risk
            if opp['risk_level'] == 'high':
                weight *= 0.5
            elif opp['risk_level'] == 'medium':
                weight *= 0.8
                
            weighted_opportunities.append({
                'symbol': opp['symbol'],
                'weight': weight,
                'entry_price': opp['entry_price']
            })
            total_weight += weight
            
        # Allocate positions
        for opp in weighted_opportunities:
            if total_weight > 0:
                allocation_percent = opp['weight'] / total_weight
                position_value = total_budget * allocation_percent
                
                # Apply position limits
                max_position_value = portfolio_value * self.risk_limits['max_position_size']
                position_value = min(position_value, max_position_value)
                
                if position_value > 0 and opp['entry_price'] > 0:
                    position_sizes[opp['symbol']] = position_value / opp['entry_price']
                    
        return position_sizes
    
    def execute_growth_strategy(self, market_data: Dict[str, Any], 
                              portfolio_value: float) -> Dict[str, Any]:
        """
        Execute the complete growth maximization strategy
        """
        logger.info("🚀 Executing Growth Maximization Strategy")
        
        # Step 1: Scan for opportunities
        opportunities = self.scan_for_growth_opportunities(market_data)
        self.active_opportunities = opportunities
        
        # Step 2: Optimize position sizes
        position_sizes = self.optimize_position_sizes(opportunities, portfolio_value)
        
        # Step 3: Generate trading signals
        trading_signals = []
        for symbol, shares in position_sizes.items():
            if shares > 0:
                signal = {
                    'symbol': symbol,
                    'action': 'BUY',
                    'quantity': round(shares, 2),
                    'signal_strength': self._get_signal_strength(symbol, opportunities),
                    'expected_return': self._calculate_expected_return(symbol, opportunities),
                    'timestamp': datetime.now().isoformat()
                }
                trading_signals.append(signal)
        
        # Step 4: Update performance metrics
        self.performance_metrics['opportunities_found'] = len(opportunities)
        
        return {
            'strategy': 'growth_maximization',
            'opportunities_found': len(opportunities),
            'trading_signals': trading_signals,
            'top_opportunities': opportunities[:5],
            'portfolio_allocation': position_sizes,
            'expected_growth': self._calculate_expected_portfolio_growth(opportunities, position_sizes),
            'risk_assessment': self._assess_portfolio_risk(opportunities, position_sizes),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_signal_strength(self, symbol: str, opportunities: List[Dict[str, Any]]) -> str:
        """
        Get signal strength for a symbol
        """
        for opp in opportunities:
            if opp['symbol'] == symbol:
                score = opp['growth_score']
                if score >= 80:
                    return 'STRONG'
                elif score >= 60:
                    return 'MODERATE'
                else:
                    return 'WEAK'
        return 'WEAK'
    
    def _calculate_expected_return(self, symbol: str, opportunities: List[Dict[str, Any]]) -> float:
        """
        Calculate expected return for a symbol
        """
        for opp in opportunities:
            if opp['symbol'] == symbol:
                current_price = opp['entry_price']
                target_price = opp['target_price']
                if current_price > 0:
                    return (target_price - current_price) / current_price
        return 0.0
    
    def _calculate_expected_portfolio_growth(self, opportunities: List[Dict[str, Any]], 
                                           position_sizes: Dict[str, float]) -> float:
        """
        Calculate expected portfolio growth
        """
        total_expected_return = 0
        total_weight = 0
        
        for symbol, shares in position_sizes.items():
            expected_return = self._calculate_expected_return(symbol, opportunities)
            weight = shares  # Simple weight by shares
            total_expected_return += expected_return * weight
            total_weight += weight
            
        if total_weight > 0:
            return total_expected_return / total_weight
        return 0.0
    
    def _assess_portfolio_risk(self, opportunities: List[Dict[str, Any]], 
                             position_sizes: Dict[str, float]) -> str:
        """
        Assess overall portfolio risk
        """
        risk_scores = {'low': 1, 'medium': 2, 'high': 3}
        total_risk_score = 0
        total_positions = 0
        
        for symbol, shares in position_sizes.items():
            for opp in opportunities:
                if opp['symbol'] == symbol:
                    risk_score = risk_scores.get(opp['risk_level'], 2)
                    total_risk_score += risk_score
                    total_positions += 1
                    break
        
        if total_positions > 0:
            avg_risk_score = total_risk_score / total_positions
            if avg_risk_score >= 2.5:
                return 'high'
            elif avg_risk_score >= 1.5:
                return 'medium'
            else:
                return 'low'
        return 'medium'
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get current performance summary
        """
        return {
            'goal': self.goal,
            'active_opportunities': len(self.active_opportunities),
            'performance_metrics': self.performance_metrics,
            'risk_limits': self.risk_limits,
            'last_update': datetime.now().isoformat()
        }

def main():
    """
    Test the growth maximizer - NO MOCK DATA
    """
    print("🚀 Growth Maximizer Test - REAL DATA ONLY")
    print("=" * 50)
    print("🛡️  ZERO MOCK DATA POLICY ENFORCED")
    print("=" * 50)
    
    # Initialize growth maximizer
    growth_maximizer = GrowthMaximizer()
    
    # NO SAMPLE DATA - Must connect to real data sources
    print("⚠️  This component requires real market data connection")
    print("   Use integrated_growth_system.py for complete functionality")
    print("   Growth maximizer ready to process real market data")
    
    # Show system capabilities without mock data
    print("\n🎯 System Capabilities:")
    print("   • Real-time opportunity scanning")
    print("   • Growth score calculation (0-100)")
    print("   • Position size optimization")
    print("   • Risk assessment (low/medium/high)")
    print("   • Trading signal generation")
    
    print("\n🔍 Current Configuration:")
    print(f"   • Goal: {growth_maximizer.goal}")
    print(f"   • Max Position Size: {growth_maximizer.risk_limits['max_position_size']:.1%}")
    print(f"   • Max Daily Loss: {growth_maximizer.risk_limits['max_daily_loss']:.1%}")
    print(f"   • Growth Target: {growth_maximizer.risk_limits['growth_target']:.1%}")
    
    print("\n🛡️  NO MOCK DATA WAS USED IN THIS TEST")

if __name__ == "__main__":
    main()