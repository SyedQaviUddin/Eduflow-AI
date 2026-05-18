"""Reporting Agent - Generates insights and reports"""
import time
from typing import Dict, Any, List
from utils.logger import WorkflowLogger, LogLevel


class ReportingAgent:
    def __init__(self, logger: WorkflowLogger):
        self.logger = logger
        self.name = "Reporting Agent"

    def generate_insights(self, workflow_data: Dict[str, Any], execution_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI insights from workflow execution"""
        self.logger.log_action_start("insights_generation", "reporting")
        
        start_time = time.time()
        time.sleep(0.6)
        
        insights = {
            "workflow_name": workflow_data.get("name", "Unknown"),
            "execution_summary": self._summarize_execution(execution_logs),
            "performance_analysis": self._analyze_performance(execution_logs),
            "anomalies_detected": self._detect_anomalies(execution_logs),
            "optimization_suggestions": self._generate_suggestions(workflow_data, execution_logs),
            "predicted_issues": self._predict_issues(workflow_data, execution_logs)
        }
        
        duration = time.time() - start_time
        self.logger.log_action_success("insights_generation", "reporting", duration)
        
        return insights

    def _summarize_execution(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize workflow execution"""
        total_steps = len(logs)
        success_steps = len([l for l in logs if l.get("level") == "SUCCESS"])
        error_steps = len([l for l in logs if l.get("level") == "ERROR"])
        
        success_rate = (success_steps / total_steps * 100) if total_steps > 0 else 0
        
        return {
            "total_steps_executed": total_steps,
            "successful_steps": success_steps,
            "failed_steps": error_steps,
            "success_rate": round(success_rate, 2),
            "execution_status": "SUCCESS" if error_steps == 0 else "PARTIAL" if error_steps < total_steps else "FAILED"
        }

    def _analyze_performance(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze workflow performance"""
        durations = []
        
        for log in logs:
            metadata = log.get("metadata", {})
            if "duration" in metadata:
                durations.append(metadata["duration"])
        
        if not durations:
            return {
                "avg_step_duration": 0,
                "fastest_step": 0,
                "slowest_step": 0,
                "bottleneck_identified": None
            }
        
        avg_duration = sum(durations) / len(durations)
        
        return {
            "avg_step_duration": round(avg_duration, 3),
            "fastest_step": round(min(durations), 3),
            "slowest_step": round(max(durations), 3),
            "bottleneck_identified": "Sentiment analysis" if max(durations) > 0.5 else "None"
        }

    def _detect_anomalies(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in execution"""
        anomalies = []
        
        # Check for repeated errors
        error_messages = {}
        for log in logs:
            if log.get("level") == "ERROR":
                message = log.get("message", "Unknown error")
                error_messages[message] = error_messages.get(message, 0) + 1
        
        for error, count in error_messages.items():
            if count > 1:
                anomalies.append({
                    "type": "repeated_error",
                    "message": error,
                    "occurrences": count,
                    "severity": "high" if count > 2 else "medium"
                })
        
        # Check for unusual execution patterns
        if len(logs) > 10:
            anomalies.append({
                "type": "high_step_count",
                "description": "Workflow executed more steps than expected",
                "step_count": len(logs),
                "severity": "low"
            })
        
        return anomalies

    def _generate_suggestions(self, workflow: Dict[str, Any], logs: List[Dict[str, Any]]) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        # Analyze workflow structure
        actions = workflow.get("actions", [])
        conditions = workflow.get("conditions", [])
        
        if len(actions) > 5:
            suggestions.append("Consider breaking complex workflow into sub-workflows")
        
        if not conditions:
            suggestions.append("Add conditional logic to optimize execution paths")
        
        # Analyze execution logs
        error_logs = [l for l in logs if l.get("level") == "ERROR"]
        if error_logs:
            suggestions.append("Implement error handling and retry mechanisms")
        
        # Performance optimization
        durations = [l.get("metadata", {}).get("duration", 0) for l in logs]
        if durations and max(durations) > 1:
            suggestions.append("Optimize slow-running actions using parallel execution")
        
        suggestions.append("Cache frequently accessed data to reduce API calls")
        suggestions.append("Implement circuit breaker pattern for external API calls")
        
        return suggestions

    def _predict_issues(self, workflow: Dict[str, Any], logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict potential future issues"""
        predictions = []
        
        # Look for warning signs
        error_count = len([l for l in logs if l.get("level") == "ERROR"])
        total_logs = len(logs)
        error_rate = (error_count / total_logs * 100) if total_logs > 0 else 0
        
        if error_rate > 10:
            predictions.append({
                "issue": "High error rate",
                "probability": "high",
                "recommended_action": "Review action configurations and error handling",
                "impact": "Workflow reliability compromised"
            })
        
        # Check for cascading failures
        actions = workflow.get("actions", [])
        if len(actions) > 3 and error_count > 0:
            predictions.append({
                "issue": "Potential cascading failures",
                "probability": "medium",
                "recommended_action": "Add failure isolation and recovery points",
                "impact": "Single failure could affect entire workflow"
            })
        
        # Scalability concerns
        if len(actions) > 8:
            predictions.append({
                "issue": "Scalability concerns",
                "probability": "medium",
                "recommended_action": "Refactor workflow into microservices",
                "impact": "Difficulty scaling to handle load"
            })
        
        return predictions

    def generate_escalation_report(self, incident_data: Dict[str, Any]) -> str:
        """Generate escalation report"""
        self.logger.log_action_start("escalation_report_generation", "reporting")
        
        start_time = time.time()
        
        report = f"""
═══════════════════════════════════════════════════════════════
                    ESCALATION REPORT
═══════════════════════════════════════════════════════════════

Incident ID: {incident_data.get('id', 'N/A')}
Timestamp: {incident_data.get('timestamp', 'N/A')}
Severity: {incident_data.get('severity', 'UNKNOWN')}

CUSTOMER INFORMATION
────────────────────
Name: {incident_data.get('customer_name', 'N/A')}
Customer ID: {incident_data.get('customer_id', 'N/A')}
Contact: {incident_data.get('contact', 'N/A')}

ISSUE DETAILS
─────────────
Type: {incident_data.get('issue_type', 'N/A')}
Description: {incident_data.get('description', 'N/A')}
Impact: {incident_data.get('impact', 'N/A')}

SENTIMENT ANALYSIS
──────────────────
Sentiment Score: {incident_data.get('sentiment_score', 'N/A')}
Sentiment: {incident_data.get('sentiment', 'N/A')}

RECOMMENDED ACTIONS
───────────────────
1. Immediate Review Required
2. Assign Senior Support Agent
3. Contact Customer within 1 hour
4. Document all interactions

═══════════════════════════════════════════════════════════════
        Report Generated by Nexora AI Recovery System
═══════════════════════════════════════════════════════════════
        """
        
        duration = time.time() - start_time
        self.logger.log_action_success("escalation_report_generation", "reporting", duration)
        
        return report

    def generate_performance_report(self, workflow_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance metrics report"""
        self.logger.log_action_start("performance_report", "reporting")
        
        start_time = time.time()
        
        report = {
            "report_type": "Performance Metrics",
            "workflow_name": workflow_stats.get("workflow_name", "Unknown"),
            "execution_date": time.time(),
            "metrics": {
                "total_executions": workflow_stats.get("execution_count", 0),
                "success_rate": workflow_stats.get("success_rate", 0),
                "avg_duration": workflow_stats.get("avg_duration", 0),
                "error_count": workflow_stats.get("error_count", 0),
                "recovery_rate": workflow_stats.get("recovery_rate", 0)
            },
            "trending": {
                "performance_trend": "stable",
                "error_trend": "decreasing",
                "efficiency_trend": "improving"
            }
        }
        
        duration = time.time() - start_time
        self.logger.log_action_success("performance_report", "reporting", duration)
        
        return report
