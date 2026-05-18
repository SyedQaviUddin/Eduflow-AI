"""Scheduler Agent - Manages scheduled workflow triggers and time-based conditions"""
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from utils.logger import WorkflowLogger, LogLevel

class SchedulerAgent:
    """Orchestrates scheduled workflow execution with date/time conditions"""
    
    def __init__(self, logger: WorkflowLogger = None):
        self.logger = logger or WorkflowLogger()
        self.scheduled_jobs = {}
        self.active_threads = {}
        self.logger.log(LogLevel.INFO, "Scheduler", "Scheduler Agent initialized")
    
    def parse_schedule_request(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Parse natural language schedule requests
        Examples:
        - "After 18 May 2026, every day at 9:00 AM, send notification..."
        - "Daily at 9:00 AM starting from tomorrow..."
        - "Every day at 9 AM if date > May 18"
        """
        import re
        
        # Extract date patterns
        date_pattern = r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})'
        dates = re.findall(date_pattern, prompt, re.IGNORECASE)
        
        # Extract time patterns (9:00 AM, 9 AM, 09:00, etc.)
        time_pattern = r'(\d{1,2}):?(\d{0,2})\s*(?:AM|PM|am|pm)?|(\d{1,2})\s*(?:AM|PM|am|pm)'
        times = re.findall(time_pattern, prompt)
        
        # Extract frequency
        frequency = "daily" if "every day" in prompt.lower() or "daily" in prompt.lower() else None
        
        # Extract condition keywords
        has_condition = "after" in prompt.lower() or "if" in prompt.lower()
        
        if dates and times and frequency:
            return {
                "has_schedule": True,
                "dates": dates,
                "times": times,
                "frequency": frequency,
                "has_condition": has_condition
            }
        return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string like "18 May 2026" to datetime
        """
        import re
        
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        # Pattern: "18 May 2026"
        match = re.match(r'(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})', date_str.strip())
        if match:
            day = int(match.group(1))
            month_name = match.group(2).lower()
            year = int(match.group(3))
            
            if month_name in months:
                try:
                    return datetime(year, months[month_name], day)
                except ValueError:
                    self.logger.log(f"Invalid date: {date_str}", LogLevel.WARNING)
                    return None
        
        return None
    
    def parse_time(self, time_str: str) -> Optional[tuple]:
        """
        Parse time string like "9:00 AM" to (hour, minute)
        Returns: (hour, minute) in 24-hour format
        """
        import re
        
        # Handle "9:00 AM" or "9 AM" or "09:00"
        match = re.search(r'(\d{1,2}):?(\d{0,2})\s*(?:AM|PM|am|pm)?', time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            
            # Check for AM/PM
            if 'pm' in time_str.lower() or 'PM' in time_str:
                if hour != 12:
                    hour += 12
            elif 'am' in time_str.lower() or 'AM' in time_str:
                if hour == 12:
                    hour = 0
            
            return (hour, minute)
        
        return (9, 0)  # Default to 9:00 AM
    
    def extract_schedule_components(self, prompt: str) -> Dict[str, Any]:
        """
        Extract all scheduling components from natural language prompt
        """
        schedule_info = self.parse_schedule_request(prompt)
        
        if not schedule_info:
            return None
        
        components = {
            "trigger": "daily_schedule",
            "frequency": schedule_info.get("frequency", "daily"),
            "time": None,
            "condition": None,
            "threshold_date": None
        }
        
        # Parse first date if available
        if schedule_info.get("dates"):
            threshold_date = self.parse_date(schedule_info["dates"][0])
            if threshold_date:
                components["threshold_date"] = threshold_date.isoformat()
                components["condition"] = f"current_date > {threshold_date.strftime('%Y-%m-%d')}"
        
        # Parse first time if available
        if schedule_info.get("times"):
            time_tuple = self.parse_time(str(schedule_info["times"][0]))
            if time_tuple:
                components["time"] = f"{time_tuple[0]:02d}:{time_tuple[1]:02d}"
                components["trigger"] = f"daily_schedule_{time_tuple[0]:02d}am" if time_tuple[0] < 12 else f"daily_schedule_{time_tuple[0]-12:02d}pm"
        
        return components
    
    def create_scheduled_workflow(self, base_workflow: Dict[str, Any], 
                                schedule_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance base workflow with scheduling information
        """
        workflow = base_workflow.copy()
        
        # Update trigger
        workflow["trigger"] = schedule_info.get("trigger", "daily_schedule_9am")
        
        # Add condition if threshold date exists
        if schedule_info.get("threshold_date"):
            threshold_date = schedule_info["threshold_date"]
            condition = {
                "id": "date_condition_1",
                "type": "date_condition",
                "operator": "greater_than",
                "threshold_date": threshold_date,
                "expression": f"current_date > {threshold_date}"
            }
            
            if "conditions" not in workflow:
                workflow["conditions"] = []
            workflow["conditions"].append(condition)
        
        # Add schedule metadata
        workflow["schedule"] = {
            "frequency": schedule_info.get("frequency", "daily"),
            "time": schedule_info.get("time", "09:00"),
            "trigger": schedule_info.get("trigger", "daily_schedule_9am"),
            "enabled": True
        }
        
        self.logger.log(
            LogLevel.INFO,
            "Scheduler",
            f"Scheduled workflow created: {workflow.get('name')} "
            f"at {schedule_info.get('time')} {schedule_info.get('frequency')}"
        )
        
        return workflow
    
    def should_execute_now(self, workflow: Dict[str, Any]) -> bool:
        """
        Check if workflow should execute based on current time and conditions
        """
        from datetime import datetime, time
        
        schedule = workflow.get("schedule", {})
        if not schedule.get("enabled"):
            return False
        
        # Parse scheduled time
        scheduled_time_str = schedule.get("time", "09:00")
        try:
            hour, minute = map(int, scheduled_time_str.split(":"))
            scheduled_time = time(hour, minute)
        except:
            return False
        
        # Check if current time is within 5 minutes of scheduled time
        now = datetime.now().time()
        current_minutes = now.hour * 60 + now.minute
        scheduled_minutes = hour * 60 + minute
        
        # Allow 5-minute window
        if abs(current_minutes - scheduled_minutes) <= 5:
            # Check date conditions
            conditions = workflow.get("conditions", [])
            for condition in conditions:
                if condition.get("type") == "date_condition":
                    if not self._check_date_condition(condition):
                        return False
            return True
        
        return False
    
    def _check_date_condition(self, condition: Dict[str, Any]) -> bool:
        """
        Evaluate date condition
        """
        from datetime import datetime
        
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
        except:
            return False
        
        return False
    
    def register_scheduled_job(self, job_id: str, workflow: Dict[str, Any], 
                             execution_callback: Callable) -> None:
        """
        Register a scheduled job for periodic execution
        """
        self.scheduled_jobs[job_id] = {
            "workflow": workflow,
            "callback": execution_callback,
            "created_at": datetime.now().isoformat(),
            "last_executed": None,
            "execution_count": 0,
            "active": True
        }
        
        self.logger.log(f"Scheduled job registered: {job_id}", LogLevel.INFO)
    
    def unregister_scheduled_job(self, job_id: str) -> None:
        """
        Unregister a scheduled job
        """
        if job_id in self.scheduled_jobs:
            self.scheduled_jobs[job_id]["active"] = False
            self.logger.log(f"Scheduled job unregistered: {job_id}", LogLevel.INFO)
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get current status of a scheduled job
        """
        if job_id not in self.scheduled_jobs:
            return None
        
        job = self.scheduled_jobs[job_id]
        return {
            "id": job_id,
            "active": job["active"],
            "created_at": job["created_at"],
            "last_executed": job["last_executed"],
            "execution_count": job["execution_count"],
            "workflow_name": job["workflow"].get("name")
        }
    
    def list_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """
        List all scheduled jobs
        """
        jobs = []
        for job_id, job_info in self.scheduled_jobs.items():
            if job_info["active"]:
                jobs.append(self.get_job_status(job_id))
        return jobs


# Global scheduler instance
_scheduler_instance = None

def get_scheduler_agent(logger: WorkflowLogger = None) -> SchedulerAgent:
    """Lazy singleton pattern for scheduler agent"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = SchedulerAgent(logger)
    return _scheduler_instance
