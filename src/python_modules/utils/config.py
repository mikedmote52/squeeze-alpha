"""
Configuration Management for AI Trading System
"""

import os
import json
import logging
from dataclasses import dataclass
from typing import Dict, Optional, Any
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env file in project root (go up 3 levels from utils/config.py)
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
    else:
        print(f"⚠️  No .env file found at {env_path}")
except ImportError:
    print("⚠️  python-dotenv not available, using system environment variables only")

@dataclass
class APICredentials:
    """API credentials configuration"""
    alpaca_api_key: str = ""
    alpaca_secret: str = ""
    alpaca_base_url: str = "https://paper-api.alpaca.markets"
    
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    polygon_api_key: str = ""
    alpha_vantage_api_key: str = ""
    
    slack_oauth_token: str = ""
    slack_webhook_url: str = ""
    
    google_sheets_credentials: str = ""
    google_sheets_id: str = ""

@dataclass
class RiskControls:
    """AGGRESSIVE PROFIT-HUNTING RISK MANAGEMENT"""
    # POSITION SIZING FOR MAXIMUM GAINS
    max_position_size: float = 2000.0      # $2K per position for bigger gains
    max_daily_exposure: float = 0.80       # 80% exposure for explosive opportunities
    max_weekly_drawdown: float = 0.25      # Accept higher drawdown for higher returns
    min_stock_price: float = 0.50          # Include penny stocks for 10x potential
    max_positions: int = 5                 # Focus on best opportunities only
    max_single_position_percent: float = 0.35  # 35% max in one explosive play
    
    # MOMENTUM-BASED RISK CONTROLS
    trailing_stop_percent: float = 0.15    # 15% trailing stop to lock profits
    profit_target_1: float = 0.25          # Take 25% profit on momentum
    profit_target_2: float = 0.50          # Take 50% profit on explosive moves
    max_hold_days: int = 30                # Exit stale positions quickly

@dataclass
class BracketOrderSettings:
    """EXPLOSIVE PROFIT-TAKING CONFIGURATION"""
    take_profit_1: float = 0.30            # 30% profit target 1
    take_profit_2: float = 0.75            # 75% profit target 2 for explosive moves
    take_profit_3: float = 1.50            # 150% profit target for 10x opportunities
    stop_loss: float = -0.20               # Wider stop loss for volatility
    tp1_quantity_percent: float = 0.30     # Take 30% profit early
    tp2_quantity_percent: float = 0.40     # Take 40% on big moves  
    tp3_quantity_percent: float = 0.30     # Let 30% ride for maximum gains

@dataclass
class TradingConfig:
    """AGGRESSIVE PROFIT-HUNTING EXECUTION"""
    market_hours_only: bool = False        # Trade pre/post market for momentum
    avoid_first_15_min: bool = False       # Trade opening momentum
    avoid_last_30_min: bool = False        # Trade closing momentum  
    position_sizing_method: str = "aggressive_momentum"
    base_amount: float = 2000.0            # $2K base for bigger gains
    momentum_multiplier: float = 1.5       # 1.5x size on high conviction
    breakout_multiplier: float = 2.0       # 2x size on breakouts

class Config:
    """Main configuration management class"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._find_config_file()
        self.logger = logging.getLogger(__name__)
        
        # Initialize configurations
        self.api_credentials = APICredentials()
        self.risk_controls = RiskControls()
        self.bracket_orders = BracketOrderSettings()
        self.trading_config = TradingConfig()
        
        # Load configuration
        self._load_config()
    
    def _find_config_file(self) -> str:
        """Find configuration file in common locations"""
        possible_paths = [
            "config/config.json",
            "config.json",
            os.path.expanduser("~/.ai-trading-config.json"),
            "/etc/ai-trading-config.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If no config file found, create default one
        default_path = "config/config.json"
        os.makedirs("config", exist_ok=True)
        self._create_default_config(default_path)
        return default_path
    
    def _create_default_config(self, path: str) -> None:
        """Create a default configuration file"""
        default_config = {
            "api_credentials": {
                "alpaca_api_key": "YOUR_ALPACA_API_KEY",
                "alpaca_secret": "YOUR_ALPACA_SECRET",
                "alpaca_base_url": "https://paper-api.alpaca.markets",
                "openai_api_key": "YOUR_OPENAI_API_KEY",
                "anthropic_api_key": "YOUR_ANTHROPIC_API_KEY",
                "polygon_api_key": "YOUR_POLYGON_API_KEY",
                "alpha_vantage_api_key": "YOUR_ALPHA_VANTAGE_API_KEY",
                "slack_oauth_token": "YOUR_SLACK_OAUTH_TOKEN",
                "slack_webhook_url": "YOUR_SLACK_WEBHOOK_URL",
                "google_sheets_credentials": "path/to/service-account.json",
                "google_sheets_id": "YOUR_GOOGLE_SHEETS_ID"
            },
            "risk_controls": {
                "max_position_size": 900.0,
                "max_daily_exposure": 0.40,
                "max_weekly_drawdown": 0.10,
                "min_stock_price": 5.00,
                "max_positions": 10,
                "max_single_position_percent": 0.15
            },
            "bracket_orders": {
                "take_profit_1": 0.15,
                "take_profit_2": 0.35,
                "stop_loss": -0.10,
                "tp1_quantity_percent": 0.50,
                "tp2_quantity_percent": 0.50
            },
            "trading_config": {
                "market_hours_only": True,
                "avoid_first_15_min": True,
                "avoid_last_30_min": True,
                "position_sizing_method": "fixed_dollar",
                "base_amount": 900.0
            }
        }
        
        with open(path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.logger.info(f"Created default configuration at {path}")
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Load API credentials
                if 'api_credentials' in config_data:
                    creds = config_data['api_credentials']
                    self.api_credentials = APICredentials(**creds)
                
                # Load risk controls
                if 'risk_controls' in config_data:
                    risk = config_data['risk_controls']
                    self.risk_controls = RiskControls(**risk)
                
                # Load bracket order settings
                if 'bracket_orders' in config_data:
                    bracket = config_data['bracket_orders']
                    self.bracket_orders = BracketOrderSettings(**bracket)
                
                # Load trading config
                if 'trading_config' in config_data:
                    trading = config_data['trading_config']
                    self.trading_config = TradingConfig(**trading)
            
            # Override with environment variables
            self._load_from_env()
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            raise
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables"""
        env_mappings = {
            'ALPACA_API_KEY': ('api_credentials', 'alpaca_api_key'),
            'ALPACA_SECRET': ('api_credentials', 'alpaca_secret'),
            'ALPACA_SECRET_KEY': ('api_credentials', 'alpaca_secret'),
            'ALPACA_BASE_URL': ('api_credentials', 'alpaca_base_url'),
            'OPENAI_API_KEY': ('api_credentials', 'openai_api_key'),
            'ANTHROPIC_API_KEY': ('api_credentials', 'anthropic_api_key'),
            'POLYGON_API_KEY': ('api_credentials', 'polygon_api_key'),
            'ALPHA_VANTAGE_API_KEY': ('api_credentials', 'alpha_vantage_api_key'),
            'SLACK_OAUTH_TOKEN': ('api_credentials', 'slack_oauth_token'),
            'SLACK_WEBHOOK_URL': ('api_credentials', 'slack_webhook_url'),
            'GOOGLE_SHEETS_CREDENTIALS': ('api_credentials', 'google_sheets_credentials'),
            'GOOGLE_SHEETS_ID': ('api_credentials', 'google_sheets_id'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                if section == 'api_credentials':
                    setattr(self.api_credentials, key, value)
    
    def get_api_key(self, service: str) -> str:
        """Get API key for a specific service"""
        key_map = {
            'alpaca': self.api_credentials.alpaca_api_key,
            'openai': self.api_credentials.openai_api_key,
            'anthropic': self.api_credentials.anthropic_api_key,
            'polygon': self.api_credentials.polygon_api_key,
            'alpha_vantage': self.api_credentials.alpha_vantage_api_key,
            'slack': self.api_credentials.slack_oauth_token,
        }
        
        key = key_map.get(service.lower())
        if not key or key.startswith('YOUR_'):
            raise ValueError(f"API key for {service} not configured")
        
        return key
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required API keys
        required_keys = ['alpaca_api_key', 'openai_api_key', 'anthropic_api_key']
        for key in required_keys:
            value = getattr(self.api_credentials, key)
            if not value or value.startswith('YOUR_'):
                validation_results['errors'].append(f"Missing required API key: {key}")
                validation_results['valid'] = False
        
        # Check risk controls
        if self.risk_controls.max_position_size <= 0:
            validation_results['errors'].append("max_position_size must be positive")
            validation_results['valid'] = False
        
        if not (0 < self.risk_controls.max_daily_exposure <= 1):
            validation_results['errors'].append("max_daily_exposure must be between 0 and 1")
            validation_results['valid'] = False
        
        # Check bracket order settings
        if self.bracket_orders.take_profit_1 <= 0:
            validation_results['errors'].append("take_profit_1 must be positive")
            validation_results['valid'] = False
        
        if self.bracket_orders.stop_loss >= 0:
            validation_results['errors'].append("stop_loss must be negative")
            validation_results['valid'] = False
        
        return validation_results
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        config_data = {
            'api_credentials': self.api_credentials.__dict__,
            'risk_controls': self.risk_controls.__dict__,
            'bracket_orders': self.bracket_orders.__dict__,
            'trading_config': self.trading_config.__dict__
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        self.logger.info(f"Configuration saved to {self.config_file}")

# Global config instance
_config = None

def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config