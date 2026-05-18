"""Scheduling Service - Manages scheduled workflow execution"""
import threading
import time
from datetime import datetime, time as datetime_time
from typing import Dict, Any, Optional, Callable, List
from utils.logger import WorkflowLogger, LogLevel

class SchedulingService:
    """
    Manages scheduled workflow execution with time and date-based conditions
    """
    
    def __init__(self, logger: WorkflowLogger = None):
        self.logger = logger or WorkflowLogger()
        self.scheduled_workflows = {}  # Maps workflow_id -> schedule_config
        self.active_schedulers = {}     # Maps workflow_id -> scheduler_thread
        self.execution_callbacks = {}   # Maps workflow_id -> callback function
        self.lock = threading.Lock()
        self.logger.log(LogLevel.INFO, "Scheduler", "Scheduling Service initialized")
    
    def register_scheduled_workflow(self, workflow_id: str, workflow: Dict[str, Any], 
                                   execution_callback: Callable) -> bool:
        """
        Register a workflow for scheduled execution
        """
        with self.lock:
            # Check if workflow has schedule configuration
            if "schedule" not in workflow:
                self.logger.log(f"Workflow {workflow_id} has no schedule config", LogLevel.WARNING)
                return False
            
            schedule = workflow.get("schedule", {})
            if not schedule.get("enabled", False):
                self.logger.log(f"Workflow {workflow_id} schedule is disabled", LogLevel.WARNING)
                return False
            
            self.scheduled_workflows[workflow_id] = {
                "workflow": workflow,
                "schedule": schedule,
                "registered_at": datetime.now().isoformat(),
                "last_executed": None,
                "execution_count": 0,
                "enabled": True
            }
            
            self.execution_callbacks[workflow_id] = execution_callback
            
            self.logger.log(
                LogLevel.INFO,
                "Scheduler",
                f"Registered scheduled workflow: {workflow_id} - "
                f"{schedule.get('frequency')} at {schedule.get('time')}"
            )
            
            return True
    
    def unregister_scheduled_workflow(self, workflow_id: str) -> None:
        """
        Unregister a scheduled workflow
        """
        with self.lock:
            if workflow_id in self.scheduled_workflows:
                self.scheduled_workflows[workflow_id]["enabled"] = False
                self.logger.log(LogLevel.INFO, "Scheduler", f"Unregistered scheduled workflow: {workflow_id}")
    
    def should_execute_workflow(self, workflow_id: str) -> bool:
        """
        Check if a scheduled workflow should execute now
        """
        with self.lock:
            if workflow_id not in self.scheduled_workflows:
                return False
            
            workflow_info = self.scheduled_workflows[workflow_id]
            if not workflow_info.get("enabled"):
                return False
            
            workflow = workflow_info.get("workflow", {})
            schedule = workflow_info.get("schedule", {})
            
            # Check if current time matches scheduled time
            if not self._matches_scheduled_time(schedule):
                return False
            
            # Check date conditions if present
            conditions = workflow.get("conditions", [])
            for condition in conditions:
                if condition.get("type") == "date_condition":
                    if not self._check_date_condition(condition):
                        return False
            
            # Check if already executed today
            if not self._should_execute_today(workflow_info):
                return False
            
            return True
    
    def _matches_scheduled_time(self, schedule: Dict[str, Any]) -> bool:
        """
        Check if current time matches the scheduled time
        """
        scheduled_time_str = schedule.get("time", "09:00")
        frequency = schedule.get("frequency", "daily")
        
        try:
            hour, minute = map(int, scheduled_time_str.split(":"))
            scheduled_time = datetime_time(hour, minute)
        except:
            return False
        
        now = datetime.now().time()
        
        # Check if within 5-minute window of scheduled time
        scheduled_minutes = hour * 60 + minute
        current_minutes = now.hour * 60 + now.minute
        time_diff = abs(current_minutes - scheduled_minutes)
        
        # Allow 5-minute tolerance window
        return time_diff <= 5
    
    def _check_date_condition(self, condition: Dict[str, Any]) -> bool:
        """
        Evaluate a date-based condition
        """
        from datetime import datetime, date
        
        threshold_str = condition.get("threshold_date", "")
        operator = condition.get("operator", "greater_than")
        
        try:
            threshold_date = datetime.fromisoformat(threshold_str).date()
            today = datetime.now().date()
            
            if operator == "greater_than":
                return today > threshold_date
            elif operator == "greater_than_or_equal":
                return today >= threshold_date
            elif operator == "equal":
                return today == threshold_date
            elif operator == "less_than":
                return today < threshold_date
            elif operator == "less_than_or_equal":
                return today <= threshold_date
        except Exception as e:
            return False
        
        return False
    
    def _should_execute_today(self, workflow_info: Dict[str, Any]) -> bool:
        """
        Check if workflow hasn't already executed today
        """
        from datetime import datetime, date
        
        last_executed = workflow_info.get("last_executed")
        if not last_executed:
            return True
        
        try:
            last_exec_date = datetime.fromisoformat(last_executed).date()
            today = datetime.now().date()
            return last_exec_date != today
        except:
            return True
    
    def mark_executed(self, workflow_id: str) -> None:
        """
        Mark a scheduled workflow as executed
        """
        with self.lock:
            if workflow_id in self.scheduled_workflows:
                self.scheduled_workflows[workflow_id]["last_executed"] = datetime.now().isoformat()
                self.scheduled_workflows[workflow_id]["execution_count"] += 1
    
    def execute_scheduled_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a scheduled workflow
        """
        if workflow_id not in self.execution_callbacks:
            self.logger.log(f"No execution callback for workflow {workflow_id}", LogLevel.WARNING)
            return {"success": False, "error": "No execution callback"}
        
        try:
            callback = self.execution_callbacks[workflow_id]
            result = callback()
            self.mark_executed(workflow_id)
            
            self.logger.log(
                LogLevel.SUCCESS,
                "Scheduler",
                f"Scheduled workflow executed: {workflow_id}"
            )
            
            return {"success": True, "result": result}
        except Exception as e:
            self.logger.log(
                LogLevel.ERROR,
                "Scheduler",
                f"Scheduled workflow execution failed: {str(e)}"
            )
            return {"success": False, "error": str(e)}
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a scheduled workflow
        """
        with self.lock:
            if workflow_id not in self.scheduled_workflows:
                return None
            
            info = self.scheduled_workflows[workflow_id]
            schedule = info.get("schedule", {})
            
            return {
                "workflow_id": workflow_id,
                "enabled": info.get("enabled"),
                "frequency": schedule.get("frequency"),
                "time": schedule.get("time"),
                "registered_at": info.get("registered_at"),
                "last_executed": info.get("last_executed"),
                "execution_count": info.get("execution_count")
            }
    
    def list_scheduled_workflows(self) -> List[Dict[str, Any]]:
        """
        List all scheduled workflows
        """
        with self.lock:
            workflows = []
            for workflow_id in self.scheduled_workflows.keys():
                status = self.get_workflow_status(workflow_id)
                if status:
                    workflows.append(status)
            return workflows


# Global scheduling service instance
_scheduling_service = None

def get_scheduling_service(logger: WorkflowLogger = None) -> SchedulingService:
    """Lazy singleton pattern for scheduling service"""
    global _scheduling_service
    if _scheduling_service is None:
        _scheduling_service = SchedulingService(logger)
    return _scheduling_service
