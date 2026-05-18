"""Workflow Execution Logger"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class LogLevel(Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class WorkflowLogger:
    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = log_dir
        self.current_logs = []
        self.workflow_id = None
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def start_workflow(self, workflow_id: str, workflow_name: str) -> None:
        """Initialize logging for a workflow execution"""
        self.workflow_id = workflow_id
        self.current_logs = []
        self.log(
            LogLevel.INFO,
            "System",
            f"Workflow '{workflow_name}' execution started",
            {"workflow_id": workflow_id}
        )

    def log(
        self,
        level: LogLevel,
        agent: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a log entry"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "agent": agent,
            "message": message,
            "metadata": metadata or {}
        }
        self.current_logs.append(log_entry)

    def log_action_start(self, action_id: str, action_type: str) -> None:
        """Log action execution start"""
        self.log(
            LogLevel.INFO,
            f"[{action_type.upper()}]",
            f"Starting action: {action_id}",
            {"action_id": action_id, "action_type": action_type}
        )

    def log_action_success(self, action_id: str, action_type: str, duration: float) -> None:
        """Log action success"""
        self.log(
            LogLevel.SUCCESS,
            f"[{action_type.upper()}]",
            f"✓ Action completed successfully",
            {"action_id": action_id, "duration": duration}
        )

    def log_action_failure(self, action_id: str, action_type: str, error: str) -> None:
        """Log action failure"""
        self.log(
            LogLevel.ERROR,
            f"[{action_type.upper()}]",
            f"✗ Action failed: {error}",
            {"action_id": action_id, "error": error}
        )

    def log_condition_evaluation(self, condition_id: str, condition_text: str, result: bool) -> None:
        """Log condition evaluation"""
        result_text = "TRUE" if result else "FALSE"
        self.log(
            LogLevel.DEBUG,
            "[CONDITION]",
            f"Evaluated: {condition_text} → {result_text}",
            {"condition_id": condition_id, "result": result}
        )

    def log_recovery_activated(self, action_id: str, error: str) -> None:
        """Log recovery system activation"""
        self.log(
            LogLevel.WARNING,
            "[RECOVERY AGENT]",
            f"🔄 Recovery activated for {action_id}",
            {"action_id": action_id, "original_error": error}
        )

    def log_recovery_success(self, action_id: str, strategy: str) -> None:
        """Log successful recovery"""
        self.log(
            LogLevel.SUCCESS,
            "[RECOVERY AGENT]",
            f"✓ Recovery successful using: {strategy}",
            {"action_id": action_id, "strategy": strategy}
        )

    def get_current_logs(self) -> List[Dict[str, Any]]:
        """Get all logs from current execution"""
        return self.current_logs

    def get_logs_by_level(self, level: LogLevel) -> List[Dict[str, Any]]:
        """Get logs filtered by level"""
        return [log for log in self.current_logs if log["level"] == level.value]

    def get_logs_by_agent(self, agent: str) -> List[Dict[str, Any]]:
        """Get logs filtered by agent"""
        return [log for log in self.current_logs if log["agent"] == agent]

    def save_logs(self) -> str:
        """Save current logs to file"""
        if not self.workflow_id:
            return None
        
        filename = f"{self.log_dir}/workflow_{self.workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "workflow_id": self.workflow_id,
                "timestamp": datetime.now().isoformat(),
                "logs": self.current_logs,
                "total_logs": len(self.current_logs),
                "error_count": len(self.get_logs_by_level(LogLevel.ERROR)),
                "success_count": len(self.get_logs_by_level(LogLevel.SUCCESS))
            }, f, indent=2, ensure_ascii=False)
        
        return filename

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary statistics"""
        total_logs = len(self.current_logs)
        success_logs = len(self.get_logs_by_level(LogLevel.SUCCESS))
        error_logs = len(self.get_logs_by_level(LogLevel.ERROR))
        warning_logs = len(self.get_logs_by_level(LogLevel.WARNING))
        
        success_rate = (success_logs / total_logs * 100) if total_logs > 0 else 0
        
        return {
            "total_steps": total_logs,
            "successful_steps": success_logs,
            "failed_steps": error_logs,
            "warnings": warning_logs,
            "success_rate": round(success_rate, 2),
            "duration": self._calculate_duration()
        }

    def _calculate_duration(self) -> str:
        """Calculate total execution duration"""
        if not self.current_logs or len(self.current_logs) < 2:
            return "0s"
        
        first_time = datetime.fromisoformat(self.current_logs[0]["timestamp"])
        last_time = datetime.fromisoformat(self.current_logs[-1]["timestamp"])
        duration = (last_time - first_time).total_seconds()
        
        if duration < 60:
            return f"{duration:.1f}s"
        else:
            return f"{duration/60:.1f}m"


class HistoricalLogger:
    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = log_dir

    def get_all_workflow_executions(self) -> List[Dict[str, Any]]:
        """Get all saved workflow executions"""
        executions = []
        
        if not os.path.exists(self.log_dir):
            return executions
        
        for filename in os.listdir(self.log_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.log_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        executions.append(data)
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
        
        return sorted(executions, key=lambda x: x.get('timestamp', ''), reverse=True)

    def get_workflow_execution_stats(self) -> Dict[str, Any]:
        """Get statistics across all executions"""
        executions = self.get_all_workflow_executions()
        
        if not executions:
            return {
                "total_executions": 0,
                "avg_success_rate": 0,
                "total_failures": 0
            }
        
        total = len(executions)
        avg_success = sum(e.get('logs', [{}])[0].get('success_rate', 0) 
                         for e in executions) / total if total > 0 else 0
        failures = sum(e.get('error_count', 0) for e in executions)
        
        return {
            "total_executions": total,
            "avg_success_rate": round(avg_success, 2),
            "total_failures": failures,
            "executions": executions
        }
