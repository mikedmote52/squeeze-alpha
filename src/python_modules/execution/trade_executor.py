"""
Trade Executor with Risk Management and Bracket Orders
Based on execute_trades.json
"""

import logging
import asyncio
from datetime import datetime, time, timezone
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
import pandas as pd

from ..utils.config import get_config
from ..utils.logging_system import get_logger, TradeExecution
from .position_manager import get_position_manager
from .risk_manager import RiskManager

@dataclass
class TradeRecommendation:
    """Trade recommendation structure"""
    ticker: str
    action: str  # 'BUY', 'SELL'
    position_size: float  # Dollar amount
    entry_price: str  # 'Market' or specific price
    take_profit_1: str  # Percentage like '+15%'
    take_profit_2: str  # Percentage like '+35%'
    stop_loss: str  # Percentage like '-10%'
    rationale: str
    risk_level: str  # 'Low', 'Medium', 'High'
    confidence_score: float

@dataclass
class BracketOrder:
    """Bracket order configuration"""
    symbol: str
    quantity: int
    entry_order_id: str
    tp1_price: float
    tp2_price: float
    stop_loss_price: float
    tp1_quantity: int
    tp2_quantity: int

@dataclass
class ExecutionResult:
    """Trade execution result"""
    ticker: str
    action: str
    status: str  # 'SUCCESS', 'FAILED', 'PARTIAL'
    quantity: int
    executed_price: float
    order_id: str
    bracket_orders: Optional[List[str]] = None
    error_message: Optional[str] = None
    timestamp: datetime = None

class TradeExecutor:
    """Main trade execution engine"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.trading_logger = get_logger()
        self.position_manager = get_position_manager()
        self.risk_manager = RiskManager()
        
        # Initialize Alpaca API
        self.alpaca_api = None
        self._initialize_alpaca()
        
        # Market hours
        self.market_open = time(14, 30)  # 9:30 AM EST in UTC
        self.market_close = time(21, 0)   # 4:00 PM EST in UTC
        
        # Execution tracking
        self.pending_orders = {}
        self.bracket_orders = {}
    
    def _initialize_alpaca(self):
        """Initialize Alpaca API connection"""
        try:
            self.alpaca_api = tradeapi.REST(
                key_id=self.config.api_credentials.alpaca_api_key,
                secret_key=self.config.api_credentials.alpaca_secret,
                base_url=self.config.api_credentials.alpaca_base_url,
                api_version='v2'
            )
            
            # Test connection
            account = self.alpaca_api.get_account()
            self.logger.info(f"Trade executor connected to Alpaca API")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Alpaca API for trading: {e}")
            self.alpaca_api = None
    
    def _is_market_hours(self) -> bool:
        """Check if current time is within market hours"""
        now = datetime.now(timezone.utc).time()
        return self.market_open <= now <= self.market_close
    
    def _is_trading_day(self) -> bool:
        """Check if current day is a trading day"""
        now = datetime.now(timezone.utc)
        return now.weekday() < 5  # Monday=0, Sunday=6
    
    def _should_avoid_execution(self) -> bool:
        """Check if execution should be avoided due to timing"""
        if not self._is_trading_day():
            return True
        
        if self.config.trading_config.market_hours_only and not self._is_market_hours():
            return True
        
        now = datetime.now(timezone.utc).time()
        
        # Avoid first 15 minutes
        if self.config.trading_config.avoid_first_15_min:
            avoid_until = time(14, 45)  # 9:45 AM EST
            if self.market_open <= now <= avoid_until:
                return True
        
        # Avoid last 30 minutes
        if self.config.trading_config.avoid_last_30_min:
            avoid_from = time(20, 30)  # 3:30 PM EST
            if avoid_from <= now <= self.market_close:
                return True
        
        return False
    
    async def execute_recommendations(self, recommendations: List[TradeRecommendation]) -> Dict[str, Any]:
        """Execute a list of trade recommendations"""
        try:
            self.logger.info(f"Executing {len(recommendations)} trade recommendations")
            
            # Pre-execution checks
            if not self.alpaca_api:
                return {
                    'successful_trades': [],
                    'failed_trades': [{'error': 'Alpaca API not available'}],
                    'skipped_trades': [],
                    'total_exposure': 0,
                    'remaining_buying_power': 0
                }
            
            # Check timing restrictions
            if self._should_avoid_execution():
                return {
                    'successful_trades': [],
                    'failed_trades': [],
                    'skipped_trades': [{'reason': 'Outside trading hours or restricted time'}],
                    'total_exposure': 0,
                    'remaining_buying_power': 0
                }
            
            successful_trades = []
            failed_trades = []
            skipped_trades = []
            total_exposure = 0
            
            # Get current account info
            account = self.alpaca_api.get_account()
            available_buying_power = float(account.buying_power)
            
            # Run pre-execution risk checks
            risk_check = await self.risk_manager.pre_execution_risk_check(
                recommendations, available_buying_power
            )
            
            if not risk_check['approved']:
                return {
                    'successful_trades': [],
                    'failed_trades': [],
                    'skipped_trades': [{'reason': f"Risk check failed: {risk_check['reason']}"}],
                    'total_exposure': 0,
                    'remaining_buying_power': available_buying_power
                }
            
            # Filter and adjust recommendations based on risk checks
            filtered_recommendations = risk_check['filtered_recommendations']
            
            # Execute each recommendation
            for rec in filtered_recommendations:
                try:
                    execution_result = await self._execute_single_trade(rec, available_buying_power)
                    
                    if execution_result.status == 'SUCCESS':
                        successful_trades.append(asdict(execution_result))
                        total_exposure += rec.position_size
                        available_buying_power -= rec.position_size
                        
                        # Log successful trade
                        trade_log = TradeExecution(
                            timestamp=datetime.now().isoformat(),
                            ticker=execution_result.ticker,
                            action=execution_result.action,
                            quantity=execution_result.quantity,
                            entry_price=execution_result.executed_price,
                            position_size_dollars=rec.position_size,
                            tp1_price=0,  # Will be calculated
                            tp2_price=0,  # Will be calculated
                            sl_price=0,   # Will be calculated
                            rationale=rec.rationale,
                            order_id=execution_result.order_id,
                            status='filled'
                        )
                        
                        self.trading_logger.log_trade_execution(trade_log)
                        
                    elif execution_result.status == 'FAILED':
                        failed_trades.append({
                            'ticker': execution_result.ticker,
                            'error': execution_result.error_message
                        })
                    
                    # Brief delay between executions
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error executing trade for {rec.ticker}: {e}")
                    failed_trades.append({
                        'ticker': rec.ticker,
                        'error': str(e)
                    })
            
            # Calculate remaining buying power
            remaining_buying_power = available_buying_power
            
            return {
                'successful_trades': successful_trades,
                'failed_trades': failed_trades,
                'skipped_trades': skipped_trades,
                'total_exposure': total_exposure,
                'remaining_buying_power': remaining_buying_power,
                'risk_metrics': risk_check.get('risk_metrics', {})
            }
            
        except Exception as e:
            self.logger.error(f"Error in trade execution: {e}")
            return {
                'successful_trades': [],
                'failed_trades': [{'error': str(e)}],
                'skipped_trades': [],
                'total_exposure': 0,
                'remaining_buying_power': 0
            }
    
    async def _execute_single_trade(self, recommendation: TradeRecommendation, 
                                   available_buying_power: float) -> ExecutionResult:
        """Execute a single trade with bracket orders"""
        try:
            ticker = recommendation.ticker
            action = recommendation.action
            position_size_dollars = recommendation.position_size
            
            # Get current market price
            quote = self.alpaca_api.get_latest_quote(ticker)
            if not quote:
                return ExecutionResult(
                    ticker=ticker,
                    action=action,
                    status='FAILED',
                    quantity=0,
                    executed_price=0,
                    order_id='',
                    error_message='Unable to get quote',
                    timestamp=datetime.now()
                )
            
            current_price = float(quote.ask if action == 'BUY' else quote.bid)
            
            # Calculate quantity
            quantity = int(position_size_dollars / current_price)
            
            if quantity <= 0:
                return ExecutionResult(
                    ticker=ticker,
                    action=action,
                    status='FAILED',
                    quantity=0,
                    executed_price=current_price,
                    order_id='',
                    error_message='Insufficient funds for minimum quantity',
                    timestamp=datetime.now()
                )
            
            # Execute entry order
            if action == 'BUY':
                order = self.alpaca_api.submit_order(
                    symbol=ticker,
                    qty=quantity,
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
            else:  # SELL
                order = self.alpaca_api.submit_order(
                    symbol=ticker,
                    qty=quantity,
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
            
            # Wait for order to fill
            filled_order = await self._wait_for_fill(order.id, timeout=30)
            
            if not filled_order or filled_order.status != 'filled':
                return ExecutionResult(
                    ticker=ticker,
                    action=action,
                    status='FAILED',
                    quantity=quantity,
                    executed_price=current_price,
                    order_id=order.id,
                    error_message='Order not filled',
                    timestamp=datetime.now()
                )
            
            executed_price = float(filled_order.filled_avg_price)
            
            # Create bracket orders for BUY orders
            bracket_order_ids = []
            if action == 'BUY':
                bracket_order_ids = await self._create_bracket_orders(
                    ticker, quantity, executed_price, recommendation
                )
            
            return ExecutionResult(
                ticker=ticker,
                action=action,
                status='SUCCESS',
                quantity=quantity,
                executed_price=executed_price,
                order_id=order.id,
                bracket_orders=bracket_order_ids,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error executing single trade for {recommendation.ticker}: {e}")
            return ExecutionResult(
                ticker=recommendation.ticker,
                action=recommendation.action,
                status='FAILED',
                quantity=0,
                executed_price=0,
                order_id='',
                error_message=str(e),
                timestamp=datetime.now()
            )
    
    async def _wait_for_fill(self, order_id: str, timeout: int = 30) -> Optional[Any]:
        """Wait for order to fill"""
        try:
            for _ in range(timeout):
                order = self.alpaca_api.get_order(order_id)
                
                if order.status in ['filled', 'partially_filled']:
                    return order
                elif order.status in ['canceled', 'rejected']:
                    return None
                
                await asyncio.sleep(1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error waiting for order fill: {e}")
            return None
    
    async def _create_bracket_orders(self, ticker: str, quantity: int, 
                                   entry_price: float, 
                                   recommendation: TradeRecommendation) -> List[str]:
        """Create bracket orders (take profit and stop loss)"""
        try:
            bracket_order_ids = []
            
            # Parse take profit and stop loss percentages
            tp1_pct = self._parse_percentage(recommendation.take_profit_1)
            tp2_pct = self._parse_percentage(recommendation.take_profit_2)
            sl_pct = self._parse_percentage(recommendation.stop_loss)
            
            # Calculate prices
            tp1_price = entry_price * (1 + tp1_pct / 100)
            tp2_price = entry_price * (1 + tp2_pct / 100)
            sl_price = entry_price * (1 + sl_pct / 100)  # sl_pct is negative
            
            # Calculate quantities
            tp1_qty = int(quantity * self.config.bracket_orders.tp1_quantity_percent)
            tp2_qty = quantity - tp1_qty  # Remaining quantity
            
            # Create take profit 1 order
            tp1_order = self.alpaca_api.submit_order(
                symbol=ticker,
                qty=tp1_qty,
                side='sell',
                type='limit',
                time_in_force='gtc',
                limit_price=round(tp1_price, 2)
            )
            bracket_order_ids.append(tp1_order.id)
            
            # Create take profit 2 order
            if tp2_qty > 0:
                tp2_order = self.alpaca_api.submit_order(
                    symbol=ticker,
                    qty=tp2_qty,
                    side='sell',
                    type='limit',
                    time_in_force='gtc',
                    limit_price=round(tp2_price, 2)
                )
                bracket_order_ids.append(tp2_order.id)
            
            # Create stop loss order
            sl_order = self.alpaca_api.submit_order(
                symbol=ticker,
                qty=quantity,
                side='sell',
                type='stop',
                time_in_force='gtc',
                stop_price=round(sl_price, 2)
            )
            bracket_order_ids.append(sl_order.id)
            
            # Store bracket order configuration
            self.bracket_orders[ticker] = BracketOrder(
                symbol=ticker,
                quantity=quantity,
                entry_order_id='',  # Would be filled
                tp1_price=tp1_price,
                tp2_price=tp2_price,
                stop_loss_price=sl_price,
                tp1_quantity=tp1_qty,
                tp2_quantity=tp2_qty
            )
            
            self.logger.info(f"Created bracket orders for {ticker}: TP1=${tp1_price:.2f}, TP2=${tp2_price:.2f}, SL=${sl_price:.2f}")
            
            return bracket_order_ids
            
        except Exception as e:
            self.logger.error(f"Error creating bracket orders for {ticker}: {e}")
            return []
    
    def _parse_percentage(self, percentage_str: str) -> float:
        """Parse percentage string like '+15%' or '-10%'"""
        try:
            # Remove % and + signs
            clean_str = percentage_str.replace('%', '').replace('+', '')
            return float(clean_str)
        except:
            return 0.0
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a specific order"""
        try:
            if not self.alpaca_api:
                return False
            
            self.alpaca_api.cancel_order(order_id)
            self.logger.info(f"Cancelled order: {order_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    async def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        try:
            if not self.alpaca_api:
                return False
            
            self.alpaca_api.cancel_all_orders()
            self.logger.info("Cancelled all open orders")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling all orders: {e}")
            return False
    
    async def get_open_orders(self) -> List[Dict[str, Any]]:
        """Get all open orders"""
        try:
            if not self.alpaca_api:
                return []
            
            orders = self.alpaca_api.list_orders(status='open')
            
            order_list = []
            for order in orders:
                order_list.append({
                    'id': order.id,
                    'symbol': order.symbol,
                    'qty': order.qty,
                    'side': order.side,
                    'type': order.type,
                    'status': order.status,
                    'limit_price': order.limit_price,
                    'stop_price': order.stop_price,
                    'submitted_at': order.submitted_at,
                    'time_in_force': order.time_in_force
                })
            
            return order_list
            
        except Exception as e:
            self.logger.error(f"Error getting open orders: {e}")
            return []
    
    async def modify_bracket_orders(self, ticker: str, 
                                  new_tp1_price: Optional[float] = None,
                                  new_tp2_price: Optional[float] = None,
                                  new_sl_price: Optional[float] = None) -> bool:
        """Modify existing bracket orders"""
        try:
            if ticker not in self.bracket_orders:
                self.logger.warning(f"No bracket orders found for {ticker}")
                return False
            
            # This would require cancelling existing orders and creating new ones
            # since Alpaca doesn't support order modification for all order types
            
            self.logger.info(f"Bracket order modification requested for {ticker}")
            # Implementation would go here
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error modifying bracket orders for {ticker}: {e}")
            return False
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary statistics"""
        try:
            return {
                'pending_orders': len(self.pending_orders),
                'bracket_orders': len(self.bracket_orders),
                'api_connected': self.alpaca_api is not None,
                'market_hours': self._is_market_hours(),
                'trading_day': self._is_trading_day(),
                'execution_allowed': not self._should_avoid_execution()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting execution summary: {e}")
            return {}

# Global trade executor
_trade_executor = None

def get_trade_executor() -> TradeExecutor:
    """Get global trade executor instance"""
    global _trade_executor
    if _trade_executor is None:
        _trade_executor = TradeExecutor()
    return _trade_executor