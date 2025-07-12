"""
N8N Interface for AI Trading System
Provides integration with N8N workflows and external HTTP endpoints
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from urllib.parse import urljoin

from .config import get_config

@dataclass
class N8NWebhookPayload:
    """Data class for N8N webhook payloads"""
    workflow_id: str
    execution_id: str
    data: Dict[str, Any]
    timestamp: str
    status: str

@dataclass
class WorkflowExecution:
    """Data class for workflow execution tracking"""
    workflow_name: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class N8NInterface:
    """Interface for N8N workflow integration"""
    
    def __init__(self, base_url: str = "http://localhost:5678"):
        self.base_url = base_url
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Track active executions
        self.active_executions: Dict[str, WorkflowExecution] = {}
        
        # Webhook handlers
        self.webhook_handlers: Dict[str, Callable] = {}
        
        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AI-Trading-System/1.0'
        })
    
    def register_webhook_handler(self, webhook_path: str, handler: Callable) -> None:
        """Register a webhook handler function"""
        self.webhook_handlers[webhook_path] = handler
        self.logger.info(f"Registered webhook handler for {webhook_path}")
    
    def trigger_workflow(self, workflow_name: str, data: Dict[str, Any]) -> Optional[str]:
        """Trigger an N8N workflow"""
        try:
            # Generate execution ID
            execution_id = f"{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create execution tracking
            execution = WorkflowExecution(
                workflow_name=workflow_name,
                execution_id=execution_id,
                start_time=datetime.now(),
                inputs=data
            )
            
            self.active_executions[execution_id] = execution
            
            # Trigger workflow via N8N API
            webhook_url = f"{self.base_url}/webhook/{workflow_name}"
            
            response = self.session.post(
                webhook_url,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                execution.status = "completed"
                execution.end_time = datetime.now()
                execution.outputs = response.json()
                
                self.logger.info(f"Successfully triggered workflow: {workflow_name}")
                return execution_id
            else:
                execution.status = "failed"
                execution.error = f"HTTP {response.status_code}: {response.text}"
                
                self.logger.error(f"Failed to trigger workflow {workflow_name}: {execution.error}")
                return None
                
        except Exception as e:
            if execution_id in self.active_executions:
                self.active_executions[execution_id].status = "failed"
                self.active_executions[execution_id].error = str(e)
            
            self.logger.error(f"Error triggering workflow {workflow_name}: {e}")
            return None
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get execution status"""
        return self.active_executions.get(execution_id)
    
    def wait_for_completion(self, execution_id: str, timeout: int = 300) -> Optional[Dict[str, Any]]:
        """Wait for workflow completion"""
        try:
            import time
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                execution = self.get_execution_status(execution_id)
                if execution and execution.status in ["completed", "failed"]:
                    return execution.outputs
                
                time.sleep(1)
            
            # Timeout
            if execution_id in self.active_executions:
                self.active_executions[execution_id].status = "timeout"
                self.active_executions[execution_id].error = "Execution timeout"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error waiting for execution {execution_id}: {e}")
            return None
    
    def handle_webhook(self, webhook_path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhook"""
        try:
            handler = self.webhook_handlers.get(webhook_path)
            if handler:
                return handler(payload)
            else:
                self.logger.warning(f"No handler registered for webhook: {webhook_path}")
                return {"status": "error", "message": "No handler registered"}
                
        except Exception as e:
            self.logger.error(f"Error handling webhook {webhook_path}: {e}")
            return {"status": "error", "message": str(e)}
    
    def create_workflow_payload(self, workflow_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized workflow payload"""
        return {
            "workflow_type": workflow_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "source": "ai-trading-system",
            "version": "1.0"
        }
    
    def trigger_daily_workflow(self, market_data: Dict[str, Any]) -> Optional[str]:
        """Trigger daily trading workflow"""
        try:
            payload = self.create_workflow_payload("daily_trading", {
                "market_data": market_data,
                "config": {
                    "risk_controls": asdict(self.config.risk_controls),
                    "bracket_orders": asdict(self.config.bracket_orders)
                }
            })
            
            return self.trigger_workflow("daily-trading", payload)
            
        except Exception as e:
            self.logger.error(f"Error triggering daily workflow: {e}")
            return None
    
    def trigger_screening_workflow(self, screening_criteria: Dict[str, Any]) -> Optional[str]:
        """Trigger stock screening workflow"""
        try:
            payload = self.create_workflow_payload("stock_screening", {
                "criteria": screening_criteria,
                "timestamp": datetime.now().isoformat()
            })
            
            return self.trigger_workflow("stock-screening", payload)
            
        except Exception as e:
            self.logger.error(f"Error triggering screening workflow: {e}")
            return None
    
    def trigger_ai_analysis_workflow(self, stocks: List[str], market_context: Dict[str, Any]) -> Optional[str]:
        """Trigger AI analysis workflow"""
        try:
            payload = self.create_workflow_payload("ai_analysis", {
                "stocks": stocks,
                "market_context": market_context,
                "ai_config": {
                    "use_claude": True,
                    "use_chatgpt": True,
                    "consensus_required": True
                }
            })
            
            return self.trigger_workflow("ai-analysis", payload)
            
        except Exception as e:
            self.logger.error(f"Error triggering AI analysis workflow: {e}")
            return None
    
    def trigger_trade_execution_workflow(self, recommendations: List[Dict[str, Any]]) -> Optional[str]:
        """Trigger trade execution workflow"""
        try:
            payload = self.create_workflow_payload("trade_execution", {
                "recommendations": recommendations,
                "risk_controls": asdict(self.config.risk_controls),
                "execution_config": asdict(self.config.trading_config)
            })
            
            return self.trigger_workflow("trade-execution", payload)
            
        except Exception as e:
            self.logger.error(f"Error triggering trade execution workflow: {e}")
            return None
    
    def trigger_monitoring_workflow(self, portfolio_data: Dict[str, Any]) -> Optional[str]:
        """Trigger portfolio monitoring workflow"""
        try:
            payload = self.create_workflow_payload("portfolio_monitoring", {
                "portfolio": portfolio_data,
                "timestamp": datetime.now().isoformat()
            })
            
            return self.trigger_workflow("portfolio-monitoring", payload)
            
        except Exception as e:
            self.logger.error(f"Error triggering monitoring workflow: {e}")
            return None
    
    def send_notification(self, message: str, channel: str = "general") -> bool:
        """Send notification via N8N"""
        try:
            payload = self.create_workflow_payload("notification", {
                "message": message,
                "channel": channel,
                "timestamp": datetime.now().isoformat()
            })
            
            execution_id = self.trigger_workflow("notification", payload)
            return execution_id is not None
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return False
    
    def get_workflow_status(self, workflow_name: str) -> Dict[str, Any]:
        """Get workflow status from N8N"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/workflows/{workflow_name}/executions",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            self.logger.error(f"Error getting workflow status: {e}")
            return {"status": "error", "message": str(e)}
    
    def create_webhook_server(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        """Create webhook server for receiving N8N callbacks"""
        try:
            from flask import Flask, request, jsonify
            
            app = Flask(__name__)
            
            @app.route('/webhook/<path:webhook_path>', methods=['POST'])
            def handle_webhook_request(webhook_path):
                try:
                    payload = request.get_json()
                    result = self.handle_webhook(webhook_path, payload)
                    return jsonify(result)
                except Exception as e:
                    return jsonify({"status": "error", "message": str(e)}), 500
            
            @app.route('/health', methods=['GET'])
            def health_check():
                return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})
            
            self.logger.info(f"Starting webhook server on {host}:{port}")
            app.run(host=host, port=port, debug=False)
            
        except Exception as e:
            self.logger.error(f"Error creating webhook server: {e}")
    
    def cleanup_executions(self, max_age_hours: int = 24) -> None:
        """Clean up old execution records"""
        try:
            cutoff_time = datetime.now() - pd.Timedelta(hours=max_age_hours)
            
            to_remove = []
            for execution_id, execution in self.active_executions.items():
                if execution.start_time < cutoff_time:
                    to_remove.append(execution_id)
            
            for execution_id in to_remove:
                del self.active_executions[execution_id]
            
            self.logger.info(f"Cleaned up {len(to_remove)} old executions")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up executions: {e}")

# Global N8N interface instance
_n8n_interface = None

def get_n8n_interface() -> N8NInterface:
    """Get global N8N interface instance"""
    global _n8n_interface
    if _n8n_interface is None:
        _n8n_interface = N8NInterface()
    return _n8n_interface