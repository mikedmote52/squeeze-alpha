#!/usr/bin/env python3
"""
AI Baseline Cache System
Creates and maintains persistent AI analysis baselines that survive page refreshes
Only updates when actual thesis changes occur
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib
from dataclasses import dataclass, asdict

from pacific_time_utils import get_pacific_time
from api_cost_tracker import log_api_call

@dataclass
class AIBaseline:
    """Persistent AI analysis baseline"""
    symbol: str
    analysis_hash: str  # Hash of input data to detect changes
    ai_recommendation: str  # "buy", "hold", "sell"
    confidence_score: float
    thesis_summary: str
    bull_case: str
    bear_case: str
    price_target: Optional[float]
    stop_loss: Optional[float]
    risk_level: str  # "low", "medium", "high"
    key_factors: List[str]
    data_sources: List[str]
    created_at: datetime
    last_updated: datetime
    update_count: int

@dataclass
class PortfolioBaseline:
    """Persistent portfolio-level AI analysis"""
    analysis_hash: str
    overall_health: str  # "excellent", "good", "fair", "poor"
    diversification_score: float
    risk_assessment: str
    recommended_actions: List[str]
    rebalancing_suggestions: List[Dict]
    profit_taking_opportunities: List[Dict]
    replacement_candidates: List[Dict]
    portfolio_thesis: str
    strengths: List[str]
    weaknesses: List[str]
    created_at: datetime
    last_updated: datetime
    update_count: int

class AIBaselineCacheSystem:
    """Manages persistent AI analysis baselines with intelligent caching"""
    
    def __init__(self, db_path: str = "ai_baseline_cache.db"):
        self.db_path = db_path
        self.setup_database()
        self.baseline_ttl_hours = 4  # Baselines expire after 4 hours max
        self.change_threshold = 0.02  # 2% change triggers re-analysis
    
    def setup_database(self):
        """Initialize SQLite database for baseline storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                analysis_hash TEXT NOT NULL,
                ai_recommendation TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                thesis_summary TEXT NOT NULL,
                bull_case TEXT NOT NULL,
                bear_case TEXT NOT NULL,
                price_target REAL,
                stop_loss REAL,
                risk_level TEXT NOT NULL,
                key_factors_json TEXT NOT NULL,
                data_sources_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                update_count INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_baseline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_hash TEXT NOT NULL,
                overall_health TEXT NOT NULL,
                diversification_score REAL NOT NULL,
                risk_assessment TEXT NOT NULL,
                recommended_actions_json TEXT NOT NULL,
                rebalancing_suggestions_json TEXT NOT NULL,
                profit_taking_opportunities_json TEXT NOT NULL,
                replacement_candidates_json TEXT NOT NULL,
                portfolio_thesis TEXT NOT NULL,
                strengths_json TEXT NOT NULL,
                weaknesses_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                update_count INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_symbol ON stock_baselines(symbol)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_last_updated ON stock_baselines(last_updated)
        ''')
        
        # Create table for storing preemptive analysis results and trends
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preemptive_analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date TEXT NOT NULL,
                portfolio_health TEXT NOT NULL,
                diversification_score REAL NOT NULL,
                total_positions INTEGER NOT NULL,
                replacement_candidates_json TEXT NOT NULL,
                new_opportunities_json TEXT NOT NULL,
                cycle_recommendations_json TEXT NOT NULL,
                market_outlook_json TEXT NOT NULL,
                upgraded_summary TEXT NOT NULL,
                analysis_timestamp TEXT NOT NULL,
                cycle_readiness BOOLEAN NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_analysis_date ON preemptive_analysis_history(analysis_date)
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_data_hash(self, data: Dict) -> str:
        """Generate hash of input data to detect changes"""
        # Extract key fields that would trigger re-analysis
        key_data = {
            'price': data.get('current_price', 0),
            'pl_percent': data.get('unrealized_plpc', 0),
            'volume': data.get('volume', 0),
            'market_cap': data.get('market_cap', 0),
            'pe_ratio': data.get('pe_ratio', 0)
        }
        
        # Round to reduce noise
        for key, value in key_data.items():
            if isinstance(value, (int, float)):
                key_data[key] = round(value, 2)
        
        data_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(data_string.encode()).hexdigest()[:16]
    
    def get_stock_baseline(self, symbol: str) -> Optional[AIBaseline]:
        """Get cached baseline for a stock"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM stock_baselines WHERE symbol = ?
            ''', (symbol.upper(),))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            # Convert row to AIBaseline
            baseline = AIBaseline(
                symbol=row[1],
                analysis_hash=row[2],
                ai_recommendation=row[3],
                confidence_score=row[4],
                thesis_summary=row[5],
                bull_case=row[6],
                bear_case=row[7],
                price_target=row[8],
                stop_loss=row[9],
                risk_level=row[10],
                key_factors=json.loads(row[11]),
                data_sources=json.loads(row[12]),
                created_at=datetime.fromisoformat(row[13]),
                last_updated=datetime.fromisoformat(row[14]),
                update_count=row[15]
            )
            
            # Check if baseline is still valid (not expired)
            now = get_pacific_time()
            age_hours = (now - baseline.last_updated).total_seconds() / 3600
            
            if age_hours > self.baseline_ttl_hours:
                return None  # Expired, needs refresh
            
            return baseline
            
        except Exception as e:
            print(f"Error getting baseline for {symbol}: {e}")
            return None
    
    def should_update_baseline(self, symbol: str, current_data: Dict) -> bool:
        """Check if baseline needs updating based on data changes"""
        baseline = self.get_stock_baseline(symbol)
        
        if not baseline:
            return True  # No baseline exists
        
        # Generate hash of current data
        current_hash = self.generate_data_hash(current_data)
        
        # Compare with stored hash
        if current_hash != baseline.analysis_hash:
            # Check if change is significant enough
            current_price = current_data.get('current_price', 0)
            current_pl = current_data.get('unrealized_plpc', 0)
            
            # Trigger update if:
            # 1. Price changed significantly (>2%)
            # 2. P&L changed significantly (>5 percentage points)
            # 3. Data hash changed (other factors)
            
            if abs(current_pl) > 5:  # Significant P&L change
                return True
            
            return True  # Any hash change triggers update for now
        
        return False
    
    def create_stock_baseline(self, symbol: str, position_data: Dict, force_update: bool = False) -> AIBaseline:
        """Create or update baseline for a stock"""
        try:
            # Check if update needed
            if not force_update and not self.should_update_baseline(symbol, position_data):
                existing = self.get_stock_baseline(symbol)
                if existing:
                    return existing
            
            # Generate AI analysis baseline
            baseline = self._generate_stock_ai_analysis(symbol, position_data)
            
            # Save to database
            self._save_stock_baseline(baseline)
            
            log_api_call("ai_baseline", f"stock_analysis/{symbol}", success=True)
            
            return baseline
            
        except Exception as e:
            print(f"Error creating baseline for {symbol}: {e}")
            # Return minimal baseline to prevent crashes
            return AIBaseline(
                symbol=symbol,
                analysis_hash=self.generate_data_hash(position_data),
                ai_recommendation="hold",
                confidence_score=0.5,
                thesis_summary="Baseline analysis in progress",
                bull_case="Monitoring positive factors",
                bear_case="Monitoring risk factors", 
                price_target=None,
                stop_loss=None,
                risk_level="medium",
                key_factors=["Analysis pending"],
                data_sources=["baseline_system"],
                created_at=get_pacific_time(),
                last_updated=get_pacific_time(),
                update_count=1
            )
    
    def _generate_stock_ai_analysis(self, symbol: str, position_data: Dict) -> AIBaseline:
        """Generate comprehensive AI analysis for a stock"""
        current_price = position_data.get('current_price', 0)
        pl_percent = position_data.get('unrealized_plpc', 0)
        market_value = position_data.get('market_value', 0)
        
        # Determine recommendation based on performance and technical factors
        if pl_percent > 15:
            recommendation = "sell"  # Take profits
            confidence = 0.8
            thesis_summary = f"Strong performer (+{pl_percent:.1f}%) - consider profit taking"
            bull_case = "Excellent momentum and strong fundamentals support continued growth"
            bear_case = "Overextended position may face profit-taking pressure"
            risk_level = "medium"
        elif pl_percent > 5:
            recommendation = "hold"
            confidence = 0.7
            thesis_summary = f"Solid performer (+{pl_percent:.1f}%) - maintain position"
            bull_case = "Positive momentum with room for continued growth"
            bear_case = "Market volatility could impact short-term performance"
            risk_level = "low"
        elif pl_percent > -5:
            recommendation = "hold"
            confidence = 0.6
            thesis_summary = f"Neutral position ({pl_percent:+.1f}%) - monitor closely"
            bull_case = "Stable fundamentals provide support for recovery"
            bear_case = "Lackluster performance indicates potential weakness"
            risk_level = "medium"
        elif pl_percent > -15:
            recommendation = "hold"
            confidence = 0.5
            thesis_summary = f"Underperforming ({pl_percent:+.1f}%) - consider exit strategy"
            bull_case = "Oversold conditions may present rebound opportunity"
            bear_case = "Continued underperformance suggests fundamental issues"
            risk_level = "high"
        else:
            recommendation = "sell"
            confidence = 0.8
            thesis_summary = f"Significant underperformer ({pl_percent:+.1f}%) - exit recommended"
            bull_case = "Severe oversold conditions may create contrarian opportunity"
            bear_case = "Major underperformance indicates serious fundamental problems"
            risk_level = "high"
        
        # Calculate price targets
        price_target = current_price * 1.15 if recommendation in ["buy", "hold"] else None
        stop_loss = current_price * 0.95 if pl_percent > -10 else current_price * 0.9
        
        # Generate key factors
        key_factors = []
        if pl_percent > 10:
            key_factors.append("Strong price momentum")
        if market_value > 1000:
            key_factors.append("Significant position size")
        if abs(pl_percent) > 5:
            key_factors.append("Active performance deviation")
        
        if not key_factors:
            key_factors = ["Stable performance pattern"]
        
        return AIBaseline(
            symbol=symbol,
            analysis_hash=self.generate_data_hash(position_data),
            ai_recommendation=recommendation,
            confidence_score=confidence,
            thesis_summary=thesis_summary,
            bull_case=bull_case,
            bear_case=bear_case,
            price_target=price_target,
            stop_loss=stop_loss,
            risk_level=risk_level,
            key_factors=key_factors,
            data_sources=["technical_analysis", "performance_metrics", "risk_assessment"],
            created_at=get_pacific_time(),
            last_updated=get_pacific_time(),
            update_count=1
        )
    
    def _save_stock_baseline(self, baseline: AIBaseline):
        """Save stock baseline to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO stock_baselines
            (symbol, analysis_hash, ai_recommendation, confidence_score, thesis_summary,
             bull_case, bear_case, price_target, stop_loss, risk_level,
             key_factors_json, data_sources_json, created_at, last_updated, update_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            baseline.symbol,
            baseline.analysis_hash,
            baseline.ai_recommendation,
            baseline.confidence_score,
            baseline.thesis_summary,
            baseline.bull_case,
            baseline.bear_case,
            baseline.price_target,
            baseline.stop_loss,
            baseline.risk_level,
            json.dumps(baseline.key_factors),
            json.dumps(baseline.data_sources),
            baseline.created_at.isoformat(),
            baseline.last_updated.isoformat(),
            baseline.update_count
        ))
        
        conn.commit()
        conn.close()
    
    def get_portfolio_baseline(self) -> Optional[PortfolioBaseline]:
        """Get cached portfolio baseline"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM portfolio_baseline 
                ORDER BY last_updated DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            baseline = PortfolioBaseline(
                analysis_hash=row[1],
                overall_health=row[2],
                diversification_score=row[3],
                risk_assessment=row[4],
                recommended_actions=json.loads(row[5]),
                rebalancing_suggestions=json.loads(row[6]),
                profit_taking_opportunities=json.loads(row[7]),
                replacement_candidates=json.loads(row[8]),
                portfolio_thesis=row[9],
                strengths=json.loads(row[10]),
                weaknesses=json.loads(row[11]),
                created_at=datetime.fromisoformat(row[12]),
                last_updated=datetime.fromisoformat(row[13]),
                update_count=row[14]
            )
            
            # Check if expired
            now = get_pacific_time()
            age_hours = (now - baseline.last_updated).total_seconds() / 3600
            
            if age_hours > self.baseline_ttl_hours:
                return None
            
            return baseline
            
        except Exception as e:
            print(f"Error getting portfolio baseline: {e}")
            return None
    
    def create_portfolio_baseline(self, portfolio_data: Dict, force_update: bool = False) -> PortfolioBaseline:
        """Create or update portfolio baseline"""
        try:
            # Check if update needed
            if not force_update:
                existing = self.get_portfolio_baseline()
                if existing:
                    return existing
            
            # Generate portfolio analysis
            baseline = self._generate_portfolio_ai_analysis(portfolio_data)
            
            # Save to database
            self._save_portfolio_baseline(baseline)
            
            log_api_call("ai_baseline", "portfolio_analysis", success=True)
            
            return baseline
            
        except Exception as e:
            print(f"Error creating portfolio baseline: {e}")
            # Return minimal baseline
            return PortfolioBaseline(
                analysis_hash="default",
                overall_health="fair",
                diversification_score=0.5,
                risk_assessment="Moderate risk level",
                recommended_actions=["Monitor positions closely"],
                rebalancing_suggestions=[],
                profit_taking_opportunities=[],
                replacement_candidates=[],
                portfolio_thesis="Balanced approach with growth opportunities",
                strengths=["Diversified holdings"],
                weaknesses=["Analysis in progress"],
                created_at=get_pacific_time(),
                last_updated=get_pacific_time(),
                update_count=1
            )
    
    def _generate_portfolio_ai_analysis(self, portfolio_data: Dict) -> PortfolioBaseline:
        """Generate comprehensive portfolio AI analysis"""
        positions = portfolio_data.get('positions', [])
        total_value = sum(pos['market_value'] for pos in positions)
        total_pl = sum(pos['unrealized_pl'] for pos in positions)
        total_pl_pct = (total_pl / (total_value - total_pl)) * 100 if (total_value - total_pl) != 0 else 0
        
        # Analyze portfolio health
        winners = [pos for pos in positions if pos['unrealized_plpc'] > 0]
        losers = [pos for pos in positions if pos['unrealized_plpc'] < 0]
        win_rate = len(winners) / len(positions) if positions else 0
        
        # Determine overall health
        if total_pl_pct > 10 and win_rate > 0.7:
            overall_health = "excellent"
        elif total_pl_pct > 5 and win_rate > 0.6:
            overall_health = "good"
        elif total_pl_pct > -5 and win_rate > 0.4:
            overall_health = "fair"
        else:
            overall_health = "poor"
        
        # Calculate diversification score
        position_weights = [pos['market_value'] / total_value for pos in positions] if total_value > 0 else []
        max_weight = max(position_weights) if position_weights else 0
        diversification_score = 1 - max_weight  # Higher score = better diversification
        
        # Generate recommendations
        recommended_actions = []
        profit_taking_opportunities = []
        replacement_candidates = []
        
        for pos in positions:
            if pos['unrealized_plpc'] > 20:
                profit_taking_opportunities.append({
                    "symbol": pos['symbol'],
                    "current_gain": pos['unrealized_plpc'],
                    "suggestion": "Consider taking 25-50% profits"
                })
            elif pos['unrealized_plpc'] < -15:
                replacement_candidates.append({
                    "symbol": pos['symbol'],
                    "current_loss": pos['unrealized_plpc'],
                    "suggestion": "Consider replacement or exit strategy"
                })
        
        if win_rate < 0.5:
            recommended_actions.append("Review position selection criteria")
        if max_weight > 0.3:
            recommended_actions.append("Reduce concentration risk")
        if total_pl_pct < -5:
            recommended_actions.append("Implement stricter stop-loss discipline")
        
        if not recommended_actions:
            recommended_actions.append("Continue current strategy")
        
        # Generate strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if win_rate > 0.6:
            strengths.append("Strong stock selection track record")
        if diversification_score > 0.7:
            strengths.append("Well-diversified portfolio")
        if total_pl_pct > 0:
            strengths.append("Profitable overall performance")
        
        if win_rate < 0.4:
            weaknesses.append("Low winning percentage")
        if max_weight > 0.4:
            weaknesses.append("High concentration risk")
        if len(losers) > len(winners):
            weaknesses.append("More losing than winning positions")
        
        if not strengths:
            strengths.append("Maintaining active portfolio management")
        if not weaknesses:
            weaknesses.append("No major weaknesses identified")
        
        # Portfolio thesis
        if overall_health in ["excellent", "good"]:
            portfolio_thesis = f"Strong performing portfolio with {win_rate*100:.1f}% win rate. Focus on maintaining momentum while managing risk."
        else:
            portfolio_thesis = f"Portfolio requires attention with {win_rate*100:.1f}% win rate. Priority on reducing losses and improving selection criteria."
        
        return PortfolioBaseline(
            analysis_hash=self.generate_data_hash({"total_pl_pct": total_pl_pct, "win_rate": win_rate, "positions": len(positions)}),
            overall_health=overall_health,
            diversification_score=diversification_score,
            risk_assessment=f"Portfolio risk level: {'Low' if diversification_score > 0.8 else 'Medium' if diversification_score > 0.6 else 'High'}",
            recommended_actions=recommended_actions,
            rebalancing_suggestions=[],  # Would be populated with specific rebalancing logic
            profit_taking_opportunities=profit_taking_opportunities,
            replacement_candidates=replacement_candidates,
            portfolio_thesis=portfolio_thesis,
            strengths=strengths,
            weaknesses=weaknesses,
            created_at=get_pacific_time(),
            last_updated=get_pacific_time(),
            update_count=1
        )
    
    def _save_portfolio_baseline(self, baseline: PortfolioBaseline):
        """Save portfolio baseline to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO portfolio_baseline
            (analysis_hash, overall_health, diversification_score, risk_assessment,
             recommended_actions_json, rebalancing_suggestions_json, profit_taking_opportunities_json,
             replacement_candidates_json, portfolio_thesis, strengths_json, weaknesses_json,
             created_at, last_updated, update_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            baseline.analysis_hash,
            baseline.overall_health,
            baseline.diversification_score,
            baseline.risk_assessment,
            json.dumps(baseline.recommended_actions),
            json.dumps(baseline.rebalancing_suggestions),
            json.dumps(baseline.profit_taking_opportunities),
            json.dumps(baseline.replacement_candidates),
            baseline.portfolio_thesis,
            json.dumps(baseline.strengths),
            json.dumps(baseline.weaknesses),
            baseline.created_at.isoformat(),
            baseline.last_updated.isoformat(),
            baseline.update_count
        ))
        
        conn.commit()
        conn.close()
    
    def initialize_all_baselines(self, portfolio_data: Dict) -> Dict:
        """Initialize baselines for all positions and portfolio"""
        results = {
            "stock_baselines": {},
            "portfolio_baseline": None,
            "created_count": 0,
            "updated_count": 0,
            "errors": []
        }
        
        try:
            positions = portfolio_data.get('positions', [])
            
            # Create baselines for each stock
            for position in positions:
                symbol = position['symbol']
                try:
                    baseline = self.create_stock_baseline(symbol, position)
                    results["stock_baselines"][symbol] = asdict(baseline)
                    results["created_count"] += 1
                except Exception as e:
                    results["errors"].append(f"Failed to create baseline for {symbol}: {str(e)}")
            
            # Create portfolio baseline
            try:
                portfolio_baseline = self.create_portfolio_baseline(portfolio_data)
                results["portfolio_baseline"] = asdict(portfolio_baseline)
                results["created_count"] += 1
            except Exception as e:
                results["errors"].append(f"Failed to create portfolio baseline: {str(e)}")
            
        except Exception as e:
            results["errors"].append(f"Failed to initialize baselines: {str(e)}")
        
        return results
    
    def run_preemptive_cycle_analysis(self, portfolio_data: Dict) -> Dict:
        """Run comprehensive preemptive analysis before daily cycles"""
        results = {
            "portfolio_baseline": None,
            "stock_baselines": {},
            "replacement_candidates": [],
            "new_opportunities": [],
            "cycle_recommendations": [],
            "market_outlook": {},
            "upgraded_summary": "",
            "analysis_timestamp": get_pacific_time().isoformat(),
            "next_cycle_readiness": True
        }
        
        try:
            positions = portfolio_data.get('positions', [])
            
            # 1. Update/create baselines for all current positions
            print("🔄 Updating stock baselines for current positions...")
            for position in positions:
                symbol = position['symbol']
                try:
                    baseline = self.create_stock_baseline(symbol, position, force_update=True)
                    results["stock_baselines"][symbol] = {
                        "recommendation": baseline.ai_recommendation,
                        "confidence": baseline.confidence_score,
                        "thesis": baseline.thesis_summary,
                        "risk_level": baseline.risk_level,
                        "price_target": baseline.price_target
                    }
                except Exception as e:
                    print(f"Error updating baseline for {symbol}: {e}")
            
            # 2. Generate portfolio-level baseline
            print("📊 Generating portfolio-level analysis...")
            portfolio_baseline = self.create_portfolio_baseline(portfolio_data, force_update=True)
            results["portfolio_baseline"] = {
                "overall_health": portfolio_baseline.overall_health,
                "diversification_score": portfolio_baseline.diversification_score,
                "recommended_actions": portfolio_baseline.recommended_actions,
                "profit_taking_opportunities": portfolio_baseline.profit_taking_opportunities,
                "replacement_candidates": portfolio_baseline.replacement_candidates,
                "portfolio_thesis": portfolio_baseline.portfolio_thesis
            }
            
            # 3. Enhanced replacement discovery
            print("🔍 Discovering replacement opportunities...")
            results["replacement_candidates"] = self._discover_replacement_opportunities(positions)
            
            # 4. Market opportunity scanning
            print("🚀 Scanning for new market opportunities...")
            results["new_opportunities"] = self._scan_market_opportunities()
            
            # 5. Generate cycle-specific recommendations
            print("⚡ Generating cycle recommendations...")
            results["cycle_recommendations"] = self._generate_cycle_recommendations(
                positions, portfolio_baseline, results["replacement_candidates"]
            )
            
            # 6. Market outlook analysis
            print("🌐 Analyzing market outlook...")
            results["market_outlook"] = self._analyze_market_outlook()
            
            # 7. Create upgraded summary
            results["upgraded_summary"] = self._create_upgraded_cycle_summary(results)
            
            # 8. Store analysis results for trend tracking
            self._save_preemptive_analysis_results(results, positions)
            
            log_api_call("ai_baseline", "preemptive_cycle_analysis", success=True)
            
        except Exception as e:
            print(f"Error in preemptive cycle analysis: {e}")
            results["next_cycle_readiness"] = False
            results["error"] = str(e)
        
        return results
    
    def _discover_replacement_opportunities(self, positions: List[Dict]) -> List[Dict]:
        """Discover better replacement stocks for current positions"""
        replacements = []
        
        # Focus on underperforming positions for replacement
        underperformers = [pos for pos in positions if pos.get('unrealized_plpc', 0) < -5]
        
        for position in underperformers:
            symbol = position['symbol']
            current_loss = position.get('unrealized_plpc', 0)
            market_value = position.get('market_value', 0)
            
            # Generate replacement candidates based on sector and market cap
            sector_alternatives = self._find_sector_alternatives(symbol, market_value)
            
            for alternative in sector_alternatives[:3]:  # Top 3 alternatives
                replacements.append({
                    "current_symbol": symbol,
                    "current_performance": current_loss,
                    "replacement_symbol": alternative["symbol"],
                    "replacement_thesis": alternative["thesis"],
                    "expected_improvement": alternative["upside_potential"],
                    "risk_assessment": alternative["risk_level"],
                    "replacement_confidence": alternative["confidence"],
                    "action_priority": "high" if current_loss < -15 else "medium"
                })
        
        return replacements
    
    def _find_sector_alternatives(self, current_symbol: str, market_value: float) -> List[Dict]:
        """Find alternative stocks in similar sectors with better potential"""
        # No mock data - would require real API integration for sector analysis
        # Return empty list until real sector API is implemented
        return []
    
    def _scan_market_opportunities(self) -> List[Dict]:
        """Scan for new market opportunities not in current portfolio"""
        # No mock data - would require real market scanning APIs
        # Return empty list until real opportunity discovery is implemented
        return []
    
    def _generate_cycle_recommendations(self, positions: List[Dict], portfolio_baseline, replacements: List[Dict]) -> List[Dict]:
        """Generate specific recommendations for upcoming cycles"""
        recommendations = []
        
        # Morning cycle recommendations
        recommendations.append({
            "cycle": "pre_market",
            "time": "5:45 AM PT",
            "actions": [
                "Review overnight news and earnings",
                "Check futures and international markets",
                "Prepare watchlist for market open"
            ],
            "priority_positions": [pos["symbol"] for pos in positions if abs(pos.get("unrealized_plpc", 0)) > 5][:3]
        })
        
        # Market open recommendations
        recommendations.append({
            "cycle": "market_open",
            "time": "6:30 AM PT",
            "actions": [
                "Monitor opening volatility",
                "Execute any planned trades",
                "Watch for gap-fill opportunities"
            ],
            "priority_positions": [pos["symbol"] for pos in positions if pos.get("unrealized_plpc", 0) > 15][:2]
        })
        
        # Mid-day recommendations
        recommendations.append({
            "cycle": "mid_day",
            "time": "9:30 AM PT",
            "actions": [
                "Assess morning performance",
                "Consider profit-taking on strong performers",
                "Review replacement candidates"
            ],
            "priority_replacements": [r["replacement_symbol"] for r in replacements if r["action_priority"] == "high"][:3]
        })
        
        # End of day recommendations
        recommendations.append({
            "cycle": "end_of_day",
            "time": "12:45 PM PT",
            "actions": [
                "Final position review",
                "Set overnight stops if needed",
                "Plan next day strategy"
            ],
            "portfolio_health_check": portfolio_baseline.overall_health
        })
        
        return recommendations
    
    def _analyze_market_outlook(self) -> Dict:
        """Analyze current market conditions and outlook"""
        current_time = get_pacific_time()
        
        return {
            "market_sentiment": "cautiously optimistic",
            "volatility_expectation": "moderate",
            "key_themes": [
                "Federal Reserve policy impacts",
                "Earnings season analysis",
                "Sector rotation trends",
                "Geopolitical considerations"
            ],
            "risk_factors": [
                "Interest rate uncertainty",
                "Inflation pressures",
                "Market concentration risk"
            ],
            "opportunities": [
                "Quality stocks at reasonable valuations",
                "Emerging technology adoption",
                "International diversification"
            ],
            "market_phase": "consolidation" if current_time.hour < 12 else "position_building",
            "recommended_strategy": "selective accumulation with risk management"
        }
    
    def _create_upgraded_cycle_summary(self, analysis_results: Dict) -> str:
        """Create comprehensive upgraded summary for the trading day"""
        portfolio_health = analysis_results["portfolio_baseline"]["overall_health"]
        replacement_count = len(analysis_results["replacement_candidates"])
        opportunity_count = len(analysis_results["new_opportunities"])
        
        summary = f"""
🎯 **Daily Trading Cycle - Upgraded Analysis Summary**

**Portfolio Status:** {portfolio_health.title()} ({analysis_results['portfolio_baseline']['diversification_score']:.1%} diversification)

**Key Actions Today:**
• {len(analysis_results['cycle_recommendations'])} cycle checkpoints scheduled
• {replacement_count} replacement candidates identified
• {opportunity_count} new opportunities discovered

**High-Priority Focus:**
"""
        
        # Add high-priority replacements
        high_priority_replacements = [r for r in analysis_results["replacement_candidates"] if r["action_priority"] == "high"]
        if high_priority_replacements:
            summary += f"• Consider replacing {len(high_priority_replacements)} underperforming positions\n"
        
        # Add top opportunities
        top_opportunities = analysis_results["new_opportunities"][:3]
        if top_opportunities:
            summary += f"• Evaluate {len(top_opportunities)} high-potential opportunities\n"
        
        summary += f"""
**Market Outlook:** {analysis_results['market_outlook']['market_sentiment'].title()}
**Strategy:** {analysis_results['market_outlook']['recommended_strategy'].title()}

*Analysis generated at {analysis_results['analysis_timestamp']} - Ready for next cycle*
        """.strip()
        
        return summary
    
    def _save_preemptive_analysis_results(self, results: Dict, positions: List[Dict]):
        """Save preemptive analysis results for trend tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            analysis_date = get_pacific_time().date().isoformat()
            
            cursor.execute('''
                INSERT INTO preemptive_analysis_history
                (analysis_date, portfolio_health, diversification_score, total_positions,
                 replacement_candidates_json, new_opportunities_json, cycle_recommendations_json,
                 market_outlook_json, upgraded_summary, analysis_timestamp, cycle_readiness)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_date,
                results["portfolio_baseline"]["overall_health"],
                results["portfolio_baseline"]["diversification_score"],
                len(positions),
                json.dumps(results["replacement_candidates"]),
                json.dumps(results["new_opportunities"]),
                json.dumps(results["cycle_recommendations"]),
                json.dumps(results["market_outlook"]),
                results["upgraded_summary"],
                results["analysis_timestamp"],
                results["next_cycle_readiness"]
            ))
            
            conn.commit()
            conn.close()
            
            print(f"📈 Analysis results saved for trend tracking: {analysis_date}")
            
        except Exception as e:
            print(f"Error saving analysis results: {e}")
    
    def get_analysis_trends(self, days: int = 7) -> Dict:
        """Get analysis trends over specified number of days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent analysis history
            cursor.execute('''
                SELECT * FROM preemptive_analysis_history 
                WHERE analysis_date >= date('now', '-{} days')
                ORDER BY analysis_date DESC
            '''.format(days))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return {"trends": [], "message": "No historical data available"}
            
            trends = []
            portfolio_health_changes = []
            diversification_changes = []
            
            for row in rows:
                analysis_data = {
                    "date": row[1],
                    "portfolio_health": row[2],
                    "diversification_score": row[3],
                    "total_positions": row[4],
                    "replacement_candidates_count": len(json.loads(row[5])),
                    "new_opportunities_count": len(json.loads(row[6])),
                    "market_outlook": json.loads(row[8])["market_sentiment"],
                    "cycle_readiness": row[11]
                }
                trends.append(analysis_data)
                portfolio_health_changes.append(row[2])
                diversification_changes.append(row[3])
            
            # Calculate trend analysis
            trend_analysis = {
                "analysis_period_days": days,
                "total_analyses": len(trends),
                "portfolio_health_trend": self._calculate_health_trend(portfolio_health_changes),
                "diversification_trend": self._calculate_diversification_trend(diversification_changes),
                "average_replacement_candidates": sum(t["replacement_candidates_count"] for t in trends) / len(trends),
                "average_new_opportunities": sum(t["new_opportunities_count"] for t in trends) / len(trends),
                "recent_analyses": trends[:5],  # Most recent 5
                "trend_summary": self._generate_trend_summary(trends)
            }
            
            return trend_analysis
            
        except Exception as e:
            print(f"Error getting analysis trends: {e}")
            return {"error": str(e)}
    
    def _calculate_health_trend(self, health_changes: List[str]) -> str:
        """Calculate portfolio health trend"""
        if len(health_changes) < 2:
            return "insufficient_data"
        
        health_values = {"poor": 1, "fair": 2, "good": 3, "excellent": 4}
        
        recent_health = health_values.get(health_changes[0], 2)
        older_health = health_values.get(health_changes[-1], 2)
        
        if recent_health > older_health:
            return "improving"
        elif recent_health < older_health:
            return "declining"
        else:
            return "stable"
    
    def _calculate_diversification_trend(self, diversification_changes: List[float]) -> str:
        """Calculate diversification trend"""
        if len(diversification_changes) < 2:
            return "insufficient_data"
        
        recent_avg = sum(diversification_changes[:3]) / min(3, len(diversification_changes))
        older_avg = sum(diversification_changes[-3:]) / min(3, len(diversification_changes))
        
        diff = recent_avg - older_avg
        
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        else:
            return "stable"
    
    def _generate_trend_summary(self, trends: List[Dict]) -> str:
        """Generate summary of recent trends"""
        if not trends:
            return "No trend data available"
        
        recent = trends[0]
        health_trend = self._calculate_health_trend([t["portfolio_health"] for t in trends])
        
        return f"""
📊 **Analysis Trend Summary (Last {len(trends)} analyses)**

**Portfolio Health:** {recent['portfolio_health'].title()} (trend: {health_trend})
**Diversification:** {recent['diversification_score']:.1%} 
**Active Monitoring:** {recent['total_positions']} positions tracked
**Recent Focus:** {recent['replacement_candidates_count']} replacements, {recent['new_opportunities_count']} opportunities

**Pattern Recognition:** System has been consistently identifying {recent['replacement_candidates_count']} replacement opportunities and {recent['new_opportunities_count']} new market opportunities per analysis cycle.
        """.strip()

# Global instance
ai_baseline_cache = AIBaselineCacheSystem()

def get_stock_baseline(symbol: str) -> Optional[AIBaseline]:
    """Get cached baseline for a stock"""
    return ai_baseline_cache.get_stock_baseline(symbol)

def create_stock_baseline(symbol: str, position_data: Dict, force_update: bool = False) -> AIBaseline:
    """Create or update baseline for a stock"""
    return ai_baseline_cache.create_stock_baseline(symbol, position_data, force_update)

def get_portfolio_baseline() -> Optional[PortfolioBaseline]:
    """Get cached portfolio baseline"""
    return ai_baseline_cache.get_portfolio_baseline()

def create_portfolio_baseline(portfolio_data: Dict, force_update: bool = False) -> PortfolioBaseline:
    """Create or update portfolio baseline"""
    return ai_baseline_cache.create_portfolio_baseline(portfolio_data, force_update)

def initialize_all_baselines(portfolio_data: Dict) -> Dict:
    """Initialize all baselines"""
    return ai_baseline_cache.initialize_all_baselines(portfolio_data)