"""
Comprehensive Logging System for AI Trading System
Based on complete_logging_system.json
"""

import os
import json
import logging
import gspread
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import pandas as pd
from google.oauth2.service_account import Credentials

from .config import get_config

@dataclass
class ScreenerCandidate:
    """Data class for screener candidate logging"""
    timestamp: str
    ticker: str
    company_name: str
    total_score: float
    volume_score: float
    technical_score: float
    squeeze_score: float
    catalyst_score: float
    price: float
    market_cap: float
    volume_spike_ratio: float
    short_interest: float
    rationale: str
    selected_for_analysis: bool

@dataclass
class AISelection:
    """Data class for AI selection logging"""
    timestamp: str
    ticker: str
    decision: str
    ai_confidence_score: float
    claude_rating: float
    chatgpt_rating: float
    consensus_level: str
    recommended_action: str
    position_size: float
    rationale: str
    risk_factors: str
    social_sentiment_score: float

@dataclass
class TradeExecution:
    """Data class for trade execution logging"""
    timestamp: str
    ticker: str
    action: str
    quantity: int
    entry_price: float
    position_size_dollars: float
    tp1_price: float
    tp2_price: float
    sl_price: float
    rationale: str
    order_id: str
    status: str

@dataclass
class PerformanceMetrics:
    """Data class for performance tracking"""
    timestamp: str
    ticker: str
    entry_date: str
    current_price: float
    price_change_percent: float
    volume_vs_average: float
    volatility: float
    max_gain: float
    max_loss: float
    current_vs_entry: float
    periods: Dict[str, float]

@dataclass
class DailySummary:
    """Data class for daily summary logging"""
    date: str
    portfolio_value: float
    daily_pnl: float
    position_count: int
    cash_balance: float
    stocks_screened: int
    recommendations_made: int
    consensus_agreement: float
    highest_conviction_pick: str
    trades_executed: int
    trades_pending: int
    trades_rejected: int
    total_exposure: float
    winning_positions: int
    losing_positions: int
    best_performer: str
    worst_performer: str

class GoogleSheetsLogger:
    """Google Sheets integration for logging"""
    
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.spreadsheet = None
        self.logger = logging.getLogger(__name__)
        
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Google Sheets client"""
        try:
            if os.path.exists(self.credentials_path):
                scope = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                
                credentials = Credentials.from_service_account_file(
                    self.credentials_path, scopes=scope
                )
                
                self.client = gspread.authorize(credentials)
                self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
                
            else:
                self.logger.warning(f"Google Sheets credentials not found at {self.credentials_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Sheets client: {e}")
    
    def _get_or_create_worksheet(self, worksheet_name: str) -> Optional[Any]:
        """Get or create worksheet by name"""
        try:
            if not self.spreadsheet:
                return None
                
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=worksheet_name, rows=1000, cols=30
                )
                self.logger.info(f"Created new worksheet: {worksheet_name}")
            
            return worksheet
            
        except Exception as e:
            self.logger.error(f"Error accessing worksheet {worksheet_name}: {e}")
            return None
    
    def append_row(self, worksheet_name: str, data: List[Any]) -> bool:
        """Append row to worksheet"""
        try:
            worksheet = self._get_or_create_worksheet(worksheet_name)
            if worksheet:
                worksheet.append_row(data)
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error appending to {worksheet_name}: {e}")
            return False
    
    def update_row(self, worksheet_name: str, row_data: Dict[str, Any], key_column: str, key_value: Any) -> bool:
        """Update specific row based on key column"""
        try:
            worksheet = self._get_or_create_worksheet(worksheet_name)
            if not worksheet:
                return False
            
            # Find the row with matching key
            records = worksheet.get_all_records()
            for i, record in enumerate(records):
                if record.get(key_column) == key_value:
                    # Update the row
                    row_num = i + 2  # +2 for header and 0-based index
                    col_headers = worksheet.row_values(1)
                    
                    for col, value in row_data.items():
                        if col in col_headers:
                            col_index = col_headers.index(col) + 1
                            worksheet.update_cell(row_num, col_index, value)
                    
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating row in {worksheet_name}: {e}")
            return False

class TradingLogger:
    """Main logging system for AI trading system"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Google Sheets logger
        self.sheets_logger = None
        if (self.config.api_credentials.google_sheets_credentials and 
            self.config.api_credentials.google_sheets_id):
            self.sheets_logger = GoogleSheetsLogger(
                self.config.api_credentials.google_sheets_credentials,
                self.config.api_credentials.google_sheets_id
            )
        
        # Ensure log directories exist
        self._setup_log_directories()
    
    def _setup_log_directories(self) -> None:
        """Create log directories if they don't exist"""
        log_dirs = [
            "logs/daily_summaries",
            "logs/trades",
            "logs/screening",
            "logs/performance",
            "logs/ai_selections"
        ]
        
        for log_dir in log_dirs:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    def log_screener_candidate(self, candidate: ScreenerCandidate) -> None:
        """Log screener candidate results"""
        try:
            # Log to Google Sheets
            if self.sheets_logger:
                data = list(asdict(candidate).values())
                self.sheets_logger.append_row("Screener_Candidates", data)
            
            # Log to local file
            log_file = f"logs/screening/screener_{datetime.now().strftime('%Y%m%d')}.json"
            with open(log_file, 'a') as f:
                json.dump(asdict(candidate), f)
                f.write('\n')
            
            self.logger.info(f"Logged screener candidate: {candidate.ticker}")
            
        except Exception as e:
            self.logger.error(f"Error logging screener candidate: {e}")
    
    def log_ai_selection(self, selection: AISelection) -> None:
        """Log AI selection decisions"""
        try:
            # Log to Google Sheets
            if self.sheets_logger:
                data = list(asdict(selection).values())
                self.sheets_logger.append_row("AI_Selections", data)
            
            # Log to local file
            log_file = f"logs/ai_selections/ai_selection_{datetime.now().strftime('%Y%m%d')}.json"
            with open(log_file, 'a') as f:
                json.dump(asdict(selection), f)
                f.write('\n')
            
            self.logger.info(f"Logged AI selection: {selection.ticker} - {selection.decision}")
            
        except Exception as e:
            self.logger.error(f"Error logging AI selection: {e}")
    
    def log_trade_execution(self, trade: TradeExecution) -> None:
        """Log trade execution details"""
        try:
            # Log to Google Sheets
            if self.sheets_logger:
                data = list(asdict(trade).values())
                self.sheets_logger.append_row("Trade_History", data)
            
            # Log to local file
            log_file = f"logs/trades/trades_{datetime.now().strftime('%Y%m%d')}.json"
            with open(log_file, 'a') as f:
                json.dump(asdict(trade), f)
                f.write('\n')
            
            self.logger.info(f"Logged trade execution: {trade.ticker} {trade.action} - {trade.status}")
            
        except Exception as e:
            self.logger.error(f"Error logging trade execution: {e}")
    
    def log_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        """Log performance tracking data"""
        try:
            # Log to Google Sheets
            if self.sheets_logger:
                # Flatten the periods dictionary
                data_dict = asdict(metrics)
                periods_data = data_dict.pop('periods')
                
                # Add period data as separate columns
                for period, value in periods_data.items():
                    data_dict[f'return_{period}'] = value
                
                data = list(data_dict.values())
                self.sheets_logger.append_row("Performance_Metrics", data)
            
            # Log to local file
            log_file = f"logs/performance/performance_{datetime.now().strftime('%Y%m%d')}.json"
            with open(log_file, 'a') as f:
                json.dump(asdict(metrics), f)
                f.write('\n')
            
            self.logger.info(f"Logged performance metrics: {metrics.ticker}")
            
        except Exception as e:
            self.logger.error(f"Error logging performance metrics: {e}")
    
    def log_daily_summary(self, summary: DailySummary) -> None:
        """Log daily workflow summary"""
        try:
            # Log to Google Sheets
            if self.sheets_logger:
                data = list(asdict(summary).values())
                self.sheets_logger.append_row("Daily_Summaries", data)
            
            # Log to local file
            log_file = f"logs/daily_summaries/summary_{summary.date}.json"
            with open(log_file, 'w') as f:
                json.dump(asdict(summary), f, indent=2)
            
            self.logger.info(f"Logged daily summary for {summary.date}")
            
        except Exception as e:
            self.logger.error(f"Error logging daily summary: {e}")
    
    def update_position_performance(self, ticker: str, performance_data: Dict[str, Any]) -> None:
        """Update position performance in tracking sheet"""
        try:
            if self.sheets_logger:
                self.sheets_logger.update_row("Portfolio_Positions", performance_data, "ticker", ticker)
            
            self.logger.info(f"Updated position performance: {ticker}")
            
        except Exception as e:
            self.logger.error(f"Error updating position performance: {e}")
    
    def get_historical_data(self, lookback_days: int = 30) -> Dict[str, pd.DataFrame]:
        """Load historical data for analysis"""
        try:
            historical_data = {}
            
            # Load from local files
            end_date = datetime.now()
            for i in range(lookback_days):
                date = end_date - pd.Timedelta(days=i)
                date_str = date.strftime('%Y%m%d')
                
                # Load different data types
                data_types = {
                    'screening': f"logs/screening/screener_{date_str}.json",
                    'ai_selections': f"logs/ai_selections/ai_selection_{date_str}.json",
                    'trades': f"logs/trades/trades_{date_str}.json",
                    'performance': f"logs/performance/performance_{date_str}.json"
                }
                
                for data_type, file_path in data_types.items():
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            data = [json.loads(line) for line in f]
                            
                        if data_type not in historical_data:
                            historical_data[data_type] = []
                        historical_data[data_type].extend(data)
            
            # Convert to DataFrames
            for data_type, data in historical_data.items():
                if data:
                    historical_data[data_type] = pd.DataFrame(data)
            
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Error loading historical data: {e}")
            return {}
    
    def analyze_ai_accuracy(self, days: int = 30) -> Dict[str, float]:
        """Analyze AI recommendation accuracy"""
        try:
            historical_data = self.get_historical_data(days)
            
            if 'ai_selections' not in historical_data or 'performance' not in historical_data:
                return {}
            
            ai_selections = historical_data['ai_selections']
            performance = historical_data['performance']
            
            # Calculate accuracy metrics
            accuracy_metrics = {}
            
            # Overall accuracy
            total_selections = len(ai_selections)
            profitable_selections = len(ai_selections[ai_selections['decision'] == 'BUY'])
            
            if total_selections > 0:
                accuracy_metrics['overall_accuracy'] = profitable_selections / total_selections
            
            # Consensus accuracy
            high_consensus = ai_selections[ai_selections['consensus_level'] == 'HIGH']
            if len(high_consensus) > 0:
                accuracy_metrics['high_consensus_accuracy'] = len(high_consensus) / len(ai_selections)
            
            return accuracy_metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing AI accuracy: {e}")
            return {}

# Global logger instance
_logger = None

def get_logger() -> TradingLogger:
    """Get global logger instance"""
    global _logger
    if _logger is None:
        _logger = TradingLogger()
    return _logger