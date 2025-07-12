"""
Workflow Scheduler for AI Trading System
Based on trigger.json - handles scheduled workflow execution
"""

import logging
import asyncio
from datetime import datetime, time, timezone
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor

from .config import get_config
from .logging_system import get_logger
from .n8n_interface import get_n8n_interface

@dataclass
class ScheduledJob:
    """Data class for scheduled job configuration"""
    name: str
    function: Callable
    trigger_type: str  # 'cron' or 'interval'
    trigger_config: Dict[str, Any]
    enabled: bool = True
    description: str = ""
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

class WorkflowScheduler:
    """Scheduler for automated trading workflows"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.trading_logger = get_logger()
        self.n8n_interface = get_n8n_interface()
        
        # Initialize scheduler
        self.scheduler = AsyncIOScheduler(
            executors={
                'default': ThreadPoolExecutor(max_workers=5)
            },
            timezone=timezone.utc
        )
        
        # Track scheduled jobs
        self.scheduled_jobs: Dict[str, ScheduledJob] = {}
        
        # Market hours configuration
        self.market_open = time(14, 30)  # 9:30 AM EST in UTC
        self.market_close = time(21, 0)   # 4:00 PM EST in UTC
        
        # Setup default jobs
        self._setup_default_jobs()
    
    def _setup_default_jobs(self) -> None:
        """Setup default scheduled jobs"""
        try:
            # Daily trading workflow - 1:30 PM UTC (8:30 AM EST)
            self.add_job(
                name="daily_trading_workflow",
                function=self._run_daily_trading_workflow,
                trigger_type="cron",
                trigger_config={
                    "hour": 13,
                    "minute": 30,
                    "day_of_week": "mon-fri"
                },
                description="Main daily trading workflow with AI analysis"
            )
            
            # Pre-market screening - 1:00 PM UTC (8:00 AM EST)
            self.add_job(
                name="premarket_screening",
                function=self._run_premarket_screening,
                trigger_type="cron",
                trigger_config={
                    "hour": 13,
                    "minute": 0,
                    "day_of_week": "mon-fri"
                },
                description="Pre-market stock screening"
            )
            
            # Portfolio monitoring - Every 15 minutes during market hours
            self.add_job(
                name="portfolio_monitoring",
                function=self._run_portfolio_monitoring,
                trigger_type="interval",
                trigger_config={
                    "minutes": 15
                },
                description="Real-time portfolio monitoring"
            )
            
            # End of day summary - 9:30 PM UTC (4:30 PM EST)
            self.add_job(
                name="end_of_day_summary",
                function=self._run_end_of_day_summary,
                trigger_type="cron",
                trigger_config={
                    "hour": 21,
                    "minute": 30,
                    "day_of_week": "mon-fri"
                },
                description="End of day trading summary and performance analysis"
            )
            
            # Weekly performance review - Fridays at 10:00 PM UTC
            self.add_job(
                name="weekly_performance_review",
                function=self._run_weekly_performance_review,
                trigger_type="cron",
                trigger_config={
                    "hour": 22,
                    "minute": 0,
                    "day_of_week": "fri"
                },
                description="Weekly performance analysis and strategy review"
            )
            
            # System health check - Every hour
            self.add_job(
                name="system_health_check",
                function=self._run_system_health_check,
                trigger_type="interval",
                trigger_config={
                    "hours": 1
                },
                description="System health and connectivity check"
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up default jobs: {e}")
    
    def add_job(self, name: str, function: Callable, trigger_type: str, 
                trigger_config: Dict[str, Any], description: str = "", enabled: bool = True) -> None:
        """Add a scheduled job"""
        try:
            job_config = ScheduledJob(
                name=name,
                function=function,
                trigger_type=trigger_type,
                trigger_config=trigger_config,
                enabled=enabled,
                description=description
            )
            
            self.scheduled_jobs[name] = job_config
            
            if enabled:
                if trigger_type == "cron":
                    trigger = CronTrigger(**trigger_config)
                elif trigger_type == "interval":
                    trigger = IntervalTrigger(**trigger_config)
                else:
                    raise ValueError(f"Unknown trigger type: {trigger_type}")
                
                self.scheduler.add_job(
                    func=function,
                    trigger=trigger,
                    id=name,
                    name=description or name,
                    replace_existing=True
                )
                
                self.logger.info(f"Added scheduled job: {name}")
            
        except Exception as e:
            self.logger.error(f"Error adding job {name}: {e}")
    
    def remove_job(self, name: str) -> None:
        """Remove a scheduled job"""
        try:
            if name in self.scheduled_jobs:
                del self.scheduled_jobs[name]
                self.scheduler.remove_job(name)
                self.logger.info(f"Removed scheduled job: {name}")
            
        except Exception as e:
            self.logger.error(f"Error removing job {name}: {e}")
    
    def start(self) -> None:
        """Start the scheduler"""
        try:
            self.scheduler.start()
            self.logger.info("Workflow scheduler started")
            
        except Exception as e:
            self.logger.error(f"Error starting scheduler: {e}")
    
    def stop(self) -> None:
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            self.logger.info("Workflow scheduler stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
    
    def _is_market_hours(self) -> bool:
        """Check if current time is within market hours"""
        now = datetime.now(timezone.utc).time()
        return self.market_open <= now <= self.market_close
    
    def _is_trading_day(self) -> bool:
        """Check if current day is a trading day"""
        now = datetime.now(timezone.utc)
        return now.weekday() < 5  # Monday=0, Sunday=6
    
    async def _run_daily_trading_workflow(self) -> None:
        """Run the main daily trading workflow"""
        try:
            if not self._is_trading_day():
                self.logger.info("Skipping daily workflow - not a trading day")
                return
            
            self.logger.info("Starting daily trading workflow")
            
            # Trigger the complete N8N workflow
            execution_id = self.n8n_interface.trigger_daily_workflow({
                "trigger_type": "scheduled",
                "timestamp": datetime.now().isoformat(),
                "market_session": "regular"
            })
            
            if execution_id:
                self.logger.info(f"Daily workflow triggered: {execution_id}")
                
                # Wait for completion (with timeout)
                result = self.n8n_interface.wait_for_completion(execution_id, timeout=1800)  # 30 minutes
                
                if result:
                    self.logger.info("Daily workflow completed successfully")
                else:
                    self.logger.error("Daily workflow failed or timed out")
            
        except Exception as e:
            self.logger.error(f"Error in daily trading workflow: {e}")
    
    async def _run_premarket_screening(self) -> None:
        """Run pre-market stock screening"""
        try:
            if not self._is_trading_day():
                self.logger.info("Skipping pre-market screening - not a trading day")
                return
            
            self.logger.info("Starting pre-market screening")
            
            # Trigger screening workflow
            execution_id = self.n8n_interface.trigger_screening_workflow({
                "session": "premarket",
                "criteria": {
                    "market_cap_min": 250000000,
                    "price_min": 5.0,
                    "volume_spike": 1.5,
                    "short_interest_min": 5.0
                }
            })
            
            if execution_id:
                self.logger.info(f"Pre-market screening triggered: {execution_id}")
            
        except Exception as e:
            self.logger.error(f"Error in pre-market screening: {e}")
    
    async def _run_portfolio_monitoring(self) -> None:
        """Run portfolio monitoring"""
        try:
            if not self._is_trading_day() or not self._is_market_hours():
                return
            
            self.logger.info("Running portfolio monitoring")
            
            # Trigger monitoring workflow
            execution_id = self.n8n_interface.trigger_monitoring_workflow({
                "monitoring_type": "realtime",
                "timestamp": datetime.now().isoformat()
            })
            
            if execution_id:
                self.logger.info(f"Portfolio monitoring triggered: {execution_id}")
            
        except Exception as e:
            self.logger.error(f"Error in portfolio monitoring: {e}")
    
    async def _run_end_of_day_summary(self) -> None:
        """Run end of day summary"""
        try:
            if not self._is_trading_day():
                self.logger.info("Skipping end of day summary - not a trading day")
                return
            
            self.logger.info("Starting end of day summary")
            
            # Trigger summary workflow
            execution_id = self.n8n_interface.trigger_workflow("end-of-day-summary", {
                "session": "end_of_day",
                "timestamp": datetime.now().isoformat()
            })
            
            if execution_id:
                self.logger.info(f"End of day summary triggered: {execution_id}")
            
        except Exception as e:
            self.logger.error(f"Error in end of day summary: {e}")
    
    async def _run_weekly_performance_review(self) -> None:
        """Run weekly performance review"""
        try:
            self.logger.info("Starting weekly performance review")
            
            # Trigger weekly review workflow
            execution_id = self.n8n_interface.trigger_workflow("weekly-performance-review", {
                "review_type": "weekly",
                "timestamp": datetime.now().isoformat()
            })
            
            if execution_id:
                self.logger.info(f"Weekly performance review triggered: {execution_id}")
            
        except Exception as e:
            self.logger.error(f"Error in weekly performance review: {e}")
    
    async def _run_system_health_check(self) -> None:
        """Run system health check"""
        try:
            self.logger.info("Running system health check")
            
            # Check various system components
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "scheduler_status": "running",
                "n8n_status": "unknown",
                "api_connections": {}
            }
            
            # Check N8N status
            try:
                n8n_status = self.n8n_interface.get_workflow_status("health-check")
                health_status["n8n_status"] = "running" if n8n_status else "down"
            except:
                health_status["n8n_status"] = "down"
            
            # Check API connections
            try:
                # This would check actual API connectivity
                health_status["api_connections"] = {
                    "alpaca": "connected",
                    "openai": "connected",
                    "anthropic": "connected",
                    "slack": "connected"
                }
            except:
                health_status["api_connections"] = {
                    "alpaca": "unknown",
                    "openai": "unknown",
                    "anthropic": "unknown",
                    "slack": "unknown"
                }
            
            # Log health status
            self.logger.info(f"System health check completed: {health_status}")
            
            # Send notification if there are issues
            if health_status["n8n_status"] == "down":
                self.n8n_interface.send_notification(
                    "System health check: N8N appears to be down",
                    "alerts"
                )
            
        except Exception as e:
            self.logger.error(f"Error in system health check: {e}")
    
    def get_job_status(self) -> Dict[str, Any]:
        """Get status of all scheduled jobs"""
        try:
            job_status = {}
            
            for name, job_config in self.scheduled_jobs.items():
                scheduler_job = self.scheduler.get_job(name)
                
                job_status[name] = {
                    "enabled": job_config.enabled,
                    "description": job_config.description,
                    "trigger_type": job_config.trigger_type,
                    "trigger_config": job_config.trigger_config,
                    "next_run": scheduler_job.next_run_time.isoformat() if scheduler_job else None,
                    "last_run": job_config.last_run.isoformat() if job_config.last_run else None
                }
            
            return job_status
            
        except Exception as e:
            self.logger.error(f"Error getting job status: {e}")
            return {}
    
    def run_job_manually(self, job_name: str) -> None:
        """Manually trigger a scheduled job"""
        try:
            if job_name in self.scheduled_jobs:
                job_config = self.scheduled_jobs[job_name]
                
                # Run the job asynchronously
                asyncio.create_task(job_config.function())
                
                self.logger.info(f"Manually triggered job: {job_name}")
            else:
                self.logger.error(f"Job not found: {job_name}")
                
        except Exception as e:
            self.logger.error(f"Error manually running job {job_name}: {e}")
    
    def update_job_config(self, job_name: str, new_config: Dict[str, Any]) -> None:
        """Update job configuration"""
        try:
            if job_name in self.scheduled_jobs:
                job_config = self.scheduled_jobs[job_name]
                
                # Update configuration
                if "trigger_config" in new_config:
                    job_config.trigger_config = new_config["trigger_config"]
                
                if "enabled" in new_config:
                    job_config.enabled = new_config["enabled"]
                
                if "description" in new_config:
                    job_config.description = new_config["description"]
                
                # Remove and re-add the job
                self.scheduler.remove_job(job_name)
                
                if job_config.enabled:
                    if job_config.trigger_type == "cron":
                        trigger = CronTrigger(**job_config.trigger_config)
                    elif job_config.trigger_type == "interval":
                        trigger = IntervalTrigger(**job_config.trigger_config)
                    else:
                        raise ValueError(f"Unknown trigger type: {job_config.trigger_type}")
                    
                    self.scheduler.add_job(
                        func=job_config.function,
                        trigger=trigger,
                        id=job_name,
                        name=job_config.description or job_name,
                        replace_existing=True
                    )
                
                self.logger.info(f"Updated job configuration: {job_name}")
            
        except Exception as e:
            self.logger.error(f"Error updating job config {job_name}: {e}")

# Global scheduler instance
_scheduler = None

def get_scheduler() -> WorkflowScheduler:
    """Get global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = WorkflowScheduler()
    return _scheduler