#!/usr/bin/env python3
"""
Trade Execution Engine - Execute AI recommendations with user control
Provides interface for reviewing, adjusting, and executing trades
"""

import os
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import alpaca_trade_api as tradeapi
from core.secrets_manager import SecretsManager

@dataclass
class TradeRecommendation:
    """Individual trade recommendation with adjustable parameters"""
    ticker: str
    action: str  # BUY/SELL/HOLD
    current_shares: int
    current_value: float
    recommended_shares: int
    recommended_value: float
    confidence: int
    reasoning: str
    risk_level: str
    
    # Adjustable by user
    user_shares: int = 0  # User-adjusted share count
    user_value: float = 0.0  # User-adjusted dollar value
    approved: bool = False  # User approval status
    execution_priority: int = 1  # 1-5 (1=highest priority)

@dataclass
class TradeExecution:
    """Trade execution result"""
    ticker: str
    action: str
    shares: int
    price: float
    total_value: float
    timestamp: str
    order_id: str
    status: str  # FILLED/PENDING/REJECTED
    execution_notes: str

class TradeExecutionEngine:
    """Execute portfolio optimization trades with user control"""
    
    def __init__(self):
        self.secrets = SecretsManager()
        self.alpaca_key = self.secrets.get_api_key('ALPACA_API_KEY')
        self.alpaca_secret = self.secrets.get_api_key('ALPACA_SECRET_KEY')
        self.alpaca_base_url = self.secrets.get_api_key('ALPACA_BASE_URL') or 'https://paper-api.alpaca.markets'
        
        # Initialize Alpaca API
        self.alpaca = tradeapi.REST(
            self.alpaca_key,
            self.alpaca_secret,
            self.alpaca_base_url,
            api_version='v2'
        )
        
        self.pending_recommendations = []
        self.execution_history = []
        
    def create_trade_recommendations(self, portfolio_positions: List[Any]) -> List[TradeRecommendation]:
        """Convert portfolio analysis into executable trade recommendations"""
        
        recommendations = []
        
        for position in portfolio_positions:
            if hasattr(position, 'ai_recommendation'):
                
                # Calculate recommended position changes
                current_shares = int(position.shares)
                current_value = float(position.market_value)
                
                if position.ai_recommendation == 'BUY':
                    # Increase position by recommended allocation
                    target_allocation = position.target_allocation / 100
                    portfolio_value = 99809.68  # Current portfolio value
                    target_value = portfolio_value * target_allocation
                    recommended_value = max(target_value - current_value, 0)
                    recommended_shares = int(recommended_value / position.current_price) if position.current_price > 0 else 0
                    
                elif position.ai_recommendation == 'SELL':
                    # Reduce position by 50% or to target allocation
                    if position.position_size_rec == 'DECREASE':
                        if 'IMMEDIATELY' in position.thesis:
                            # Sell 75% for immediate sells
                            recommended_shares = -int(current_shares * 0.75)
                        else:
                            # Sell 50% for regular reduces
                            recommended_shares = -int(current_shares * 0.50)
                    else:
                        recommended_shares = 0
                    recommended_value = recommended_shares * position.current_price
                    
                else:  # HOLD
                    recommended_shares = 0
                    recommended_value = 0.0
                
                if recommended_shares != 0:  # Only include actionable recommendations
                    rec = TradeRecommendation(
                        ticker=position.ticker,
                        action=position.ai_recommendation,
                        current_shares=current_shares,
                        current_value=current_value,
                        recommended_shares=recommended_shares,
                        recommended_value=recommended_value,
                        confidence=position.ai_confidence,
                        reasoning=position.thesis[:100] + "..." if len(position.thesis) > 100 else position.thesis,
                        risk_level=position.risk_level,
                        user_shares=recommended_shares,  # Default to AI recommendation
                        user_value=recommended_value
                    )
                    recommendations.append(rec)
        
        # Sort by confidence (highest first)
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        
        # Assign execution priorities
        for i, rec in enumerate(recommendations):
            rec.execution_priority = min(i + 1, 5)
        
        self.pending_recommendations = recommendations
        return recommendations
    
    def adjust_recommendation(self, ticker: str, user_shares: int = None, 
                            user_value: float = None, approved: bool = None) -> bool:
        """Allow user to adjust trade recommendations"""
        
        for rec in self.pending_recommendations:
            if rec.ticker == ticker:
                if user_shares is not None:
                    rec.user_shares = user_shares
                    # Recalculate value based on current price
                    current_price = rec.current_value / rec.current_shares if rec.current_shares > 0 else 0
                    rec.user_value = user_shares * current_price
                
                if user_value is not None:
                    rec.user_value = user_value
                    # Recalculate shares based on current price
                    current_price = rec.current_value / rec.current_shares if rec.current_shares > 0 else 0
                    rec.user_shares = int(user_value / current_price) if current_price > 0 else 0
                
                if approved is not None:
                    rec.approved = approved
                    
                return True
        
        return False
    
    async def execute_approved_trades(self, dry_run: bool = True) -> List[TradeExecution]:
        """Execute all approved trade recommendations"""
        
        executions = []
        approved_trades = [rec for rec in self.pending_recommendations if rec.approved]
        
        if not approved_trades:
            print("📋 No approved trades to execute")
            return executions
        
        print(f"🔄 Executing {len(approved_trades)} approved trades...")
        print(f"📊 Mode: {'DRY RUN' if dry_run else 'LIVE TRADING'}")
        print("=" * 60)
        
        # Sort by execution priority
        approved_trades.sort(key=lambda x: x.execution_priority)
        
        for rec in approved_trades:
            try:
                execution = await self._execute_single_trade(rec, dry_run)
                executions.append(execution)
                
                # Add delay between trades
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Failed to execute {rec.ticker}: {e}")
                
                execution = TradeExecution(
                    ticker=rec.ticker,
                    action=rec.action,
                    shares=rec.user_shares,
                    price=0.0,
                    total_value=0.0,
                    timestamp=datetime.now().isoformat(),
                    order_id="FAILED",
                    status="REJECTED",
                    execution_notes=f"Execution failed: {str(e)}"
                )
                executions.append(execution)
        
        # Update execution history
        self.execution_history.extend(executions)
        
        # Clear executed recommendations
        self.pending_recommendations = [rec for rec in self.pending_recommendations if not rec.approved]
        
        return executions
    
    async def _execute_single_trade(self, rec: TradeRecommendation, dry_run: bool) -> TradeExecution:
        """Execute a single trade order"""
        
        # Determine order side
        side = 'buy' if rec.user_shares > 0 else 'sell'
        shares = abs(rec.user_shares)
        
        print(f"📈 {rec.ticker}: {side.upper()} {shares} shares (Priority {rec.execution_priority})")
        
        if dry_run:
            # Simulate execution for dry run
            current_price = rec.current_value / rec.current_shares if rec.current_shares > 0 else 0
            
            execution = TradeExecution(
                ticker=rec.ticker,
                action=rec.action,
                shares=rec.user_shares,
                price=current_price,
                total_value=shares * current_price,
                timestamp=datetime.now().isoformat(),
                order_id=f"DRY_RUN_{rec.ticker}_{int(datetime.now().timestamp())}",
                status="SIMULATED",
                execution_notes=f"Dry run: {side} {shares} shares at ~${current_price:.2f}"
            )
            
            print(f"   ✅ Simulated: ${shares * current_price:.2f} @ ${current_price:.2f}/share")
            return execution
        
        else:
            # Execute live trade through Alpaca
            try:
                order = self.alpaca.submit_order(
                    symbol=rec.ticker,
                    qty=shares,
                    side=side,
                    type='market',
                    time_in_force='day'
                )
                
                print(f"   ✅ Order submitted: {order.id}")
                
                # Wait for fill (up to 30 seconds)
                fill_timeout = 30
                for _ in range(fill_timeout):
                    order_status = self.alpaca.get_order(order.id)
                    if order_status.status == 'filled':
                        break
                    await asyncio.sleep(1)
                
                execution = TradeExecution(
                    ticker=rec.ticker,
                    action=rec.action,
                    shares=rec.user_shares,
                    price=float(order_status.filled_avg_price or 0),
                    total_value=float(order_status.filled_qty or 0) * float(order_status.filled_avg_price or 0),
                    timestamp=order_status.filled_at or datetime.now().isoformat(),
                    order_id=order.id,
                    status=order_status.status.upper(),
                    execution_notes=f"Live execution: {order_status.status}"
                )
                
                print(f"   ✅ Filled: ${execution.total_value:.2f} @ ${execution.price:.2f}/share")
                return execution
                
            except Exception as e:
                raise Exception(f"Alpaca order failed: {str(e)}")
    
    def get_portfolio_impact_preview(self) -> Dict[str, Any]:
        """Preview the impact of pending trades on portfolio"""
        
        approved_trades = [rec for rec in self.pending_recommendations if rec.approved]
        
        total_buy_value = sum(rec.user_value for rec in approved_trades if rec.user_shares > 0)
        total_sell_value = sum(abs(rec.user_value) for rec in approved_trades if rec.user_shares < 0)
        net_cash_change = total_sell_value - total_buy_value
        
        return {
            'total_trades': len(approved_trades),
            'buy_orders': len([rec for rec in approved_trades if rec.user_shares > 0]),
            'sell_orders': len([rec for rec in approved_trades if rec.user_shares < 0]),
            'total_buy_value': total_buy_value,
            'total_sell_value': total_sell_value,
            'net_cash_change': net_cash_change,
            'trades_by_confidence': {
                'high_confidence': len([rec for rec in approved_trades if rec.confidence >= 80]),
                'medium_confidence': len([rec for rec in approved_trades if 70 <= rec.confidence < 80]),
                'low_confidence': len([rec for rec in approved_trades if rec.confidence < 70])
            }
        }
    
    def save_execution_history(self, filename: str = "trade_execution_history.json"):
        """Save trade execution history to file"""
        
        history_data = []
        for execution in self.execution_history:
            history_data.append({
                'ticker': execution.ticker,
                'action': execution.action,
                'shares': execution.shares,
                'price': execution.price,
                'total_value': execution.total_value,
                'timestamp': execution.timestamp,
                'order_id': execution.order_id,
                'status': execution.status,
                'execution_notes': execution.execution_notes
            })
        
        with open(filename, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        print(f"💾 Execution history saved to {filename}")

# Example usage and testing
async def test_trade_execution():
    """Test the trade execution interface"""
    
    print("🧪 TESTING TRADE EXECUTION ENGINE")
    print("=" * 50)
    
    # This would typically come from your portfolio analysis
    from core.live_portfolio_engine import LivePortfolioEngine
    
    engine = LivePortfolioEngine()
    portfolio = await engine.get_live_portfolio()
    
    # Create trade execution engine
    trade_engine = TradeExecutionEngine()
    
    # Generate recommendations
    recommendations = trade_engine.create_trade_recommendations(portfolio)
    
    print(f"📊 Generated {len(recommendations)} trade recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec.ticker}: {rec.action} {rec.recommended_shares} shares ({rec.confidence}% confidence)")
    
    # Test adjustments and approvals
    if recommendations:
        # Approve first recommendation with adjustment
        rec = recommendations[0]
        trade_engine.adjust_recommendation(
            ticker=rec.ticker,
            user_shares=int(rec.recommended_shares * 0.8),  # Reduce by 20%
            approved=True
        )
        print(f"✅ Approved {rec.ticker} with 20% reduction")
    
    # Preview impact
    impact = trade_engine.get_portfolio_impact_preview()
    print(f"\n📈 Portfolio Impact Preview:")
    print(f"   Total trades: {impact['total_trades']}")
    print(f"   Net cash change: ${impact['net_cash_change']:,.2f}")
    
    # Execute trades (dry run)
    executions = await trade_engine.execute_approved_trades(dry_run=True)
    print(f"\n✅ Executed {len(executions)} trades (dry run)")

if __name__ == "__main__":
    asyncio.run(test_trade_execution())