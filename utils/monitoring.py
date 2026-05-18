"""Real-time Execution Monitoring - Track workflow execution with live metrics"""
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
import queue


class AgentStatus(Enum):
    """Agent execution statuses"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    SKIPPED = "skipped"


class EventType(Enum):
    """Event types for execution monitoring"""
    WORKFLOW_START = "workflow_start"
    WORKFLOW_END = "workflow_end"
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    STEP_COMPLETE = "step_complete"
    ERROR_OCCURRED = "error_occurred"
    EMAIL_SENT = "email_sent"
    RECOVERY_TRIGGERED = "recovery_triggered"


@dataclass
class AgentMetrics:
    """Metrics for individual agent execution"""
    agent_name: str
    status: AgentStatus = AgentStatus.IDLE
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: float = 0.0
    success_count: int = 0
    error_count: int = 0
    cpu_usage: float = 0.0
    memory_mb: float = 0.0
    output: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    def get_duration(self) -> float:
        """Get current duration"""
        if self.start_time:
            end = self.end_time or datetime.now()
            return (end - self.start_time).total_seconds()
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["status"] = self.status.value
        if self.start_time:
            data["start_time"] = self.start_time.isoformat()
        if self.end_time:
            data["end_time"] = self.end_time.isoformat()
        data["duration"] = self.get_duration()
        return data


@dataclass
class ExecutionEvent:
    """Execution event for real-time monitoring"""
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    agent_name: Optional[str] = None
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
            "message": self.message,
            "data": self.data
        }


class ExecutionMonitor:
    """Real-time execution monitoring system"""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.workflow_name = "Unknown"
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status = "idle"  # idle, running, completed, failed
        
        # Agent metrics
        self.agents: Dict[str, AgentMetrics] = {}
        
        # Event tracking
        self.events: List[ExecutionEvent] = []
        self.event_queue: queue.Queue = queue.Queue()
        
        # Execution statistics
        self.total_steps = 0
        self.completed_steps = 0
        self.failed_steps = 0
        self.total_duration = 0.0
        
        # Lock for thread safety
        self._lock = threading.Lock()
    
    def start_workflow(self, workflow_name: str):
        """Mark workflow as started"""
        with self._lock:
            self.workflow_name = workflow_name
            self.start_time = datetime.now()
            self.status = "running"
            
            event = ExecutionEvent(
                event_type=EventType.WORKFLOW_START,
                message=f"🚀 Workflow '{workflow_name}' started"
            )
            self._record_event(event)
    
    def end_workflow(self, success: bool = True):
        """Mark workflow as completed"""
        with self._lock:
            self.end_time = datetime.now()
            if self.start_time:
                self.total_duration = (self.end_time - self.start_time).total_seconds()
            
            self.status = "completed" if success else "failed"
            
            event = ExecutionEvent(
                event_type=EventType.WORKFLOW_END,
                message=f"✅ Workflow completed in {self.total_duration:.2f}s" if success else "❌ Workflow failed"
            )
            self._record_event(event)
    
    def start_agent(self, agent_name: str):
        """Mark agent execution as started"""
        with self._lock:
            metrics = AgentMetrics(agent_name=agent_name)
            metrics.status = AgentStatus.RUNNING
            metrics.start_time = datetime.now()
            self.agents[agent_name] = metrics
            
            event = ExecutionEvent(
                event_type=EventType.AGENT_START,
                agent_name=agent_name,
                message=f"▶️ {agent_name} started"
            )
            self._record_event(event)
    
    def end_agent(self, agent_name: str, success: bool = True, 
                  output: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        """Mark agent execution as completed"""
        with self._lock:
            if agent_name in self.agents:
                metrics = self.agents[agent_name]
                metrics.status = AgentStatus.COMPLETED if success else AgentStatus.FAILED
                metrics.end_time = datetime.now()
                metrics.duration = metrics.get_duration()
                metrics.output = output or {}
                metrics.error_message = error
                
                if success:
                    metrics.success_count += 1
                else:
                    metrics.error_count += 1
                
                event = ExecutionEvent(
                    event_type=EventType.AGENT_END,
                    agent_name=agent_name,
                    message=f"✅ {agent_name} completed in {metrics.duration:.2f}s" if success else f"❌ {agent_name} failed",
                    data={"duration": metrics.duration, "success": success}
                )
                self._record_event(event)
    
    def record_event(self, event_type: EventType, message: str, 
                     agent_name: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        """Record a custom event"""
        with self._lock:
            event = ExecutionEvent(
                event_type=event_type,
                agent_name=agent_name,
                message=message,
                data=data or {}
            )
            self._record_event(event)
    
    def _record_event(self, event: ExecutionEvent):
        """Internal method to record event"""
        self.events.append(event)
        try:
            self.event_queue.put_nowait(event)
        except:
            pass
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current execution progress"""
        with self._lock:
            agent_statuses = {}
            for agent_name, metrics in self.agents.items():
                agent_statuses[agent_name] = {
                    "status": metrics.status.value,
                    "duration": metrics.get_duration(),
                    "success": metrics.error_count == 0,
                    "error": metrics.error_message
                }
            
            return {
                "workflow_id": self.workflow_id,
                "workflow_name": self.workflow_name,
                "status": self.status,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "elapsed_time": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                "total_duration": self.total_duration,
                "agent_statuses": agent_statuses,
                "total_steps": self.total_steps,
                "completed_steps": self.completed_steps,
                "failed_steps": self.failed_steps,
                "success_rate": (self.completed_steps / self.total_steps * 100) if self.total_steps > 0 else 0
            }
    
    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent events"""
        with self._lock:
            events = self.events[-limit:]
            return [event.to_dict() for event in events]
    
    def get_agent_metrics(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific agent"""
        with self._lock:
            if agent_name in self.agents:
                return self.agents[agent_name].to_dict()
            return None
    
    def get_all_agent_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all agents"""
        with self._lock:
            return {
                name: metrics.to_dict() 
                for name, metrics in self.agents.items()
            }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary"""
        with self._lock:
            total_success = sum(m.success_count for m in self.agents.values())
            total_errors = sum(m.error_count for m in self.agents.values())
            
            return {
                "workflow_id": self.workflow_id,
                "workflow_name": self.workflow_name,
                "status": self.status,
                "total_duration": self.total_duration,
                "total_agents": len(self.agents),
                "total_success": total_success,
                "total_errors": total_errors,
                "success_rate": (total_success / (total_success + total_errors) * 100) if (total_success + total_errors) > 0 else 0,
                "event_count": len(self.events),
                "agents": self.get_all_agent_metrics()
            }


class MonitoringManager:
    """Manage multiple execution monitors"""
    
    def __init__(self):
        self.monitors: Dict[str, ExecutionMonitor] = {}
        self._lock = threading.Lock()
    
    def create_monitor(self, workflow_id: str) -> ExecutionMonitor:
        """Create a new monitor for a workflow"""
        with self._lock:
            monitor = ExecutionMonitor(workflow_id)
            self.monitors[workflow_id] = monitor
            return monitor
    
    def get_monitor(self, workflow_id: str) -> Optional[ExecutionMonitor]:
        """Get an existing monitor"""
        with self._lock:
            return self.monitors.get(workflow_id)
    
    def get_active_monitors(self) -> List[ExecutionMonitor]:
        """Get all active monitors"""
        with self._lock:
            return [m for m in self.monitors.values() if m.status == "running"]
    
    def get_all_monitors(self) -> Dict[str, ExecutionMonitor]:
        """Get all monitors"""
        with self._lock:
            return self.monitors.copy()


# Global monitoring manager instance
_monitoring_manager = None

def get_monitoring_manager() -> MonitoringManager:
    """Get the global monitoring manager (Streamlit-safe singleton)"""
    global _monitoring_manager
    if _monitoring_manager is None:
        _monitoring_manager = MonitoringManager()
    return _monitoring_manager
