"""Workflow Execution Engine - Orchestrates workflow execution"""
import re
import uuid
import time
import random
import json
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime

from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.notification_agent import NotificationAgent
from agents.recovery_agent import RecoveryAgent
from agents.reporting_agent import ReportingAgent
from utils.logger import WorkflowLogger, LogLevel, HistoricalLogger
from utils.workflow_storage import WorkflowStorage
from utils.workflow_parser import WorkflowParser
from utils.monitoring import get_monitoring_manager, EventType


class WorkflowExecutor:
    def __init__(self):
        self.execution_id = str(uuid.uuid4())[:8]
        self.logger = WorkflowLogger()
        self.storage = WorkflowStorage()
        self.parser = WorkflowParser()
        self.historical_logger = HistoricalLogger()
        self.monitoring_manager = get_monitoring_manager()
        self.current_monitor = None
        
        # Initialize agents
        self.research_agent = ResearchAgent(self.logger)
        self.analysis_agent = AnalysisAgent(self.logger)
        self.notification_agent = NotificationAgent(self.logger)
        self.recovery_agent = RecoveryAgent(self.logger)
        self.reporting_agent = ReportingAgent(self.logger)
        
        self.execution_state = {
            "workflow_id": None,
            "status": "idle",
            "paused": False,
            "current_action": None,
            "context": {},
            "execution_count": 0,
            "start_time": None,
            "end_time": None
        }

    def _is_placeholder_value(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        return "{{" in value and "}}" in value

    def _is_valid_email(self, email: str) -> bool:
        if not isinstance(email, str) or self._is_placeholder_value(email):
            return False
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()))

    def _is_valid_phone(self, phone: str) -> bool:
        if not isinstance(phone, str) or self._is_placeholder_value(phone):
            return False
        cleaned = re.sub(r"[^\d]", "", phone)
        return 10 <= len(cleaned) <= 15

    def _normalize_recipient_list(self, raw_value: Any) -> List[str]:
        if raw_value is None:
            return []
        if isinstance(raw_value, str):
            return [item.strip() for item in raw_value.split(",") if item.strip()]
        if isinstance(raw_value, list):
            return [str(item).strip() for item in raw_value if str(item).strip()]
        return [str(raw_value).strip()]

    def _resolve_email_recipients(self, raw_recipients: Any, context: Dict[str, Any] = None) -> List[str]:
        recipients = self._normalize_recipient_list(raw_recipients)
        valid = [r for r in recipients if self._is_valid_email(r)]
        default_email = os.getenv("DEFAULT_NOTIFICATION_EMAIL", "sqavi037@gmail.com")

        actual_emails = [r for r in valid if r.lower() != default_email.lower()]
        if actual_emails:
            return actual_emails
        if valid and not context:
            return valid

        if context:
            if isinstance(context.get("bulk_emails"), list) and context.get("bulk_emails"):
                return [r for r in context.get("bulk_emails") if self._is_valid_email(r)]
            if isinstance(context.get("emails"), list) and context.get("emails"):
                return [r for r in context.get("emails") if self._is_valid_email(r)]
            if isinstance(context.get("email"), str) and self._is_valid_email(context.get("email")):
                return [context.get("email")]

        return [default_email]

    def _normalize_phone_number(self, raw_phone: str) -> str:
        if not isinstance(raw_phone, str):
            return ""
        cleaned = re.sub(r"[^\d+]", "", raw_phone)
        if cleaned.startswith("00"):
            cleaned = "+" + cleaned.lstrip("0")
        elif not cleaned.startswith("+"):
            cleaned = "+" + cleaned
        return cleaned

    def _resolve_phone_numbers(self, raw_numbers: Any, context: Dict[str, Any] = None) -> List[str]:
        phone_list = self._normalize_recipient_list(raw_numbers)
        normalized = [self._normalize_phone_number(p) for p in phone_list if p]
        default_whatsapp = self._normalize_phone_number(os.getenv("DEFAULT_WHATSAPP_NUMBER", "+917671901101"))

        actual_numbers = [p for p in normalized if self._is_valid_phone(p) and p != default_whatsapp]
        if actual_numbers:
            return actual_numbers

        if normalized and default_whatsapp in normalized and context:
            if isinstance(context.get("bulk_whatsapp_numbers"), list) and context.get("bulk_whatsapp_numbers"):
                bulk = [p for p in [self._normalize_phone_number(x) for x in context.get("bulk_whatsapp_numbers")] if self._is_valid_phone(p)]
                if bulk:
                    return bulk
            if isinstance(context.get("whatsapp_numbers"), list) and context.get("whatsapp_numbers"):
                bulk = [p for p in [self._normalize_phone_number(x) for x in context.get("whatsapp_numbers")] if self._is_valid_phone(p)]
                if bulk:
                    return bulk

        valid = [p for p in normalized if self._is_valid_phone(p)]
        if valid:
            return valid

        if context:
            if isinstance(context.get("bulk_whatsapp_numbers"), list) and context.get("bulk_whatsapp_numbers"):
                return [p for p in [self._normalize_phone_number(x) for x in context.get("bulk_whatsapp_numbers")] if self._is_valid_phone(p)]
            if isinstance(context.get("whatsapp_numbers"), list) and context.get("whatsapp_numbers"):
                return [p for p in [self._normalize_phone_number(x) for x in context.get("whatsapp_numbers")] if self._is_valid_phone(p)]
            if isinstance(context.get("phone"), str) and self._is_valid_phone(context.get("phone")):
                return [self._normalize_phone_number(context.get("phone"))]

        return [default_whatsapp]

    def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any], 
                        simulate_failure: bool = False, failure_action: str = None) -> Dict[str, Any]:
        """Execute a workflow with input data"""
        
        # Load workflow
        workflow_metadata = self.storage.load_workflow(workflow_id)
        if not workflow_metadata:
            return {"success": False, "error": "Workflow not found"}
        
        workflow_data = workflow_metadata.get("workflow", {})
        workflow_name = workflow_data.get("name", "Unknown Workflow")
        
        # Initialize execution
        self.execution_id = str(uuid.uuid4())[:8]
        self.logger.start_workflow(self.execution_id, workflow_name)
        
        # Create monitoring for this execution
        self.current_monitor = self.monitoring_manager.create_monitor(workflow_id)
        self.current_monitor.start_workflow(workflow_name)
        
        self.execution_state.update({
            "workflow_id": workflow_id,
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "context": input_data.copy()
        })
        
        self.logger.log(
            LogLevel.INFO,
            "System",
            f"🚀 Starting execution with ID: {self.execution_id}",
            {"workflow_id": workflow_id, "input_data": input_data}
        )
        
        try:
            # Execute workflow
            result = self._execute_workflow_actions(workflow_data, input_data, 
                                                   simulate_failure, failure_action)
            
            self.execution_state["status"] = "completed"
            self.execution_state["end_time"] = datetime.now().isoformat()
            self.current_monitor.end_workflow(success=result.get("success", False))
            
            return result
        
        except Exception as e:
            self.logger.log(
                LogLevel.ERROR,
                "System",
                f"Workflow execution failed: {str(e)}",
                {"error": str(e)}
            )
            
            self.execution_state["status"] = "failed"
            self.current_monitor.end_workflow(success=False)
            
            return {
                "success": False,
                "execution_id": self.execution_id,
                "error": str(e),
                "logs": self.logger.get_current_logs(),
                "execution_summary": self.logger.get_execution_summary()
            }
        
        finally:
            # Save execution logs
            log_file = self.logger.save_logs()
            self.storage.increment_execution_count(workflow_id)

    def _execute_workflow_actions(self, workflow: Dict[str, Any], input_data: Dict[str, Any],
                                  simulate_failure: bool = False, failure_action: str = None) -> Dict[str, Any]:
        """Execute workflow actions in sequence"""
        
        context = input_data.copy()
        action_results = {}
        skipped_actions = set()
        
        actions = workflow.get("actions", [])
        conditions = workflow.get("conditions", [])
        notifications = workflow.get("notifications", [])
        
        # Execute actions
        for action in actions:
            action_id = action.get("id", "unknown")
            action_type = action.get("type", "unknown")
            
            if action_id in skipped_actions:
                continue
            
            self.execution_state["current_action"] = action_id
            
            # Simulate failure if requested
            if simulate_failure and action_id == failure_action:
                error_msg = "Webhook API timeout"
                self.logger.log_action_failure(action_id, action_type, error_msg)
                
                # Activate recovery
                recovery_result = self.recovery_agent.handle_failure(
                    action_id,
                    error_msg,
                    action
                )
                
                if not recovery_result.get("recovered"):
                    self.logger.log(
                        LogLevel.ERROR,
                        "System",
                        "❌ Action failed and recovery unsuccessful",
                        {"action_id": action_id}
                    )
                    action_results[action_id] = {"success": False, "error": error_msg}
                    continue
                else:
                    self.logger.log(
                        LogLevel.SUCCESS,
                        "System",
                        f"✓ Recovered from failure using {recovery_result.get('strategy')}",
                        {}
                    )
                    action_results[action_id] = {"success": True, "recovered": True}
            else:
                # Normal action execution
                result = self._execute_action(action, context)
                action_results[action_id] = result
                
                if result.get("success"):
                    # Store result in context for subsequent actions
                    context[action_id] = result.get("data", {})

        # Evaluate conditions
        for condition in conditions:
            condition_id = condition.get("id", "unknown")
            condition_text = condition.get("condition", "")
            
            result = self.analysis_agent.evaluate_condition(condition_text, context)
            
            if result:
                then_action = condition.get("then_action", "")
                if then_action and then_action not in skipped_actions:
                    self.logger.log(
                        LogLevel.DEBUG,
                        "System",
                        f"Condition TRUE: executing {then_action}",
                        {}
                    )
            else:
                else_action = condition.get("else_action", "")
                if else_action:
                    skipped_actions.add(else_action)

        # Send notifications
        notification_results = self._send_notifications(notifications, context)

        # Generate insights
        insights = self.reporting_agent.generate_insights(workflow, self.logger.get_current_logs())

        # Compile results
        execution_summary = self.logger.get_execution_summary()
        
        return {
            "success": all(r.get("success", False) for r in action_results.values() if r),
            "execution_id": self.execution_id,
            "workflow_id": self.execution_state["workflow_id"],
            "action_results": action_results,
            "notification_results": notification_results,
            "context": context,
            "logs": self.logger.get_current_logs(),
            "execution_summary": execution_summary,
            "insights": insights,
            "recovery_stats": self.recovery_agent.get_recovery_statistics()
        }

    def _execute_action(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action"""
        action_type = action.get("type", "unknown")
        action_id = action.get("id", "unknown")
        
        # Start agent monitoring
        if self.current_monitor:
            self.current_monitor.start_agent(f"{action_type}_{action_id}")
        
        try:
            if action_type == "sentiment_analysis":
                text = context.get("text", "") or context.get("message", "")
                result = self.research_agent.analyze_sentiment(text)
                
                if self.current_monitor:
                    self.current_monitor.end_agent(f"{action_type}_{action_id}", 
                                                   success=True, output=result)
                
                return {"success": True, "data": result}
            
            elif action_type == "data_extraction":
                result = self.research_agent.extract_key_information(context)
                
                if self.current_monitor:
                    self.current_monitor.end_agent(f"{action_type}_{action_id}", 
                                                   success=True, output=result)
                
                return {"success": True, "data": result}
            
            elif action_type == "pattern_analysis":
                historical = context.get("historical_data", [])
                result = self.research_agent.analyze_patterns(historical)
                
                if self.current_monitor:
                    self.current_monitor.end_agent(f"{action_type}_{action_id}", 
                                                   success=True, output=result)
                
                return {"success": True, "data": result}
            
            elif action_type == "condition_check":
                condition = action.get("config", {}).get("condition", "")
                result = self.analysis_agent.evaluate_condition(condition, context)
                
                if self.current_monitor:
                    self.current_monitor.end_agent(f"{action_type}_{action_id}", 
                                                   success=True, output={"condition_result": result})
                
                return {"success": True, "data": {"condition_result": result}}
            
            elif action_type == "risk_assessment":
                result = self.analysis_agent.assess_risk(context)
                
                if self.current_monitor:
                    self.current_monitor.end_agent(f"{action_type}_{action_id}", 
                                                   success=True, output=result)
                
                return {"success": True, "data": result}
            
            elif action_type in ["whatsapp_alert", "whatsapp_notification", "whatsapp_message"]:
                raw_phone = action.get("config", {}).get("phone") or action.get("config", {}).get("recipient")
                phone_candidates = self._resolve_phone_numbers(raw_phone, context)
                message = action.get("config", {}).get("message", f"Alert: {context.get('issue', 'No details')}")

                if len(phone_candidates) > 1:
                    result = self.notification_agent.send_bulk_whatsapp(phone_candidates, message)
                    action_success = result.get("successful", 0) > 0
                else:
                    phone = phone_candidates[0] if phone_candidates else os.getenv("DEFAULT_WHATSAPP_NUMBER", "+917671901101")
                    result = self.notification_agent.send_whatsapp_alert(phone, message)
                    action_success = result.get("success", False)

                if self.current_monitor:
                    self.current_monitor.end_agent(f"{action_type}_{action_id}", 
                                                   success=action_success, output=result)

                return {"success": action_success, "data": result}
            
            elif action_type == "email_notification":
                raw_recipient = action.get("config", {}).get("to") or action.get("config", {}).get("recipient")
                recipient = self._resolve_email_recipients(raw_recipient, context)[0]
                subject = action.get("config", {}).get("subject", f"Alert: {context.get('issue', 'Notification')}")
                body = action.get("config", {}).get("body", json.dumps(context, indent=2))
                message_type = action.get("config", {}).get("message_type", "alert")
                
                result = self.notification_agent.send_message(
                    recipient=recipient,
                    subject=subject,
                    body=body,
                    message_type=message_type
                )
                
                if self.current_monitor:
                    self.current_monitor.record_event(
                        EventType.EMAIL_SENT,
                        f"📧 Email sent to {recipient}",
                        agent_name="email_notification",
                        data=result
                    )
                    self.current_monitor.end_agent(f"{action_type}_{action_id}", 
                                                   success=result.get("success", False), output=result)
                
                return {"success": result.get("success", False), "data": result}
            
            elif action_type == "slack_notification":
                channel = action.get("config", {}).get("channel", "#alerts")
                message = f"Workflow Alert: {context.get('issue', 'No details')}"
                result = self.notification_agent.send_slack_message(channel, message)
                
                if self.current_monitor:
                    self.current_monitor.end_agent(f"{action_type}_{action_id}", 
                                                   success=result.get("success", False), output=result)
                
                return {"success": result.get("success", False), "data": result}
            
            elif action_type == "sms_notification":
                phone = action.get("config", {}).get("phone", "+1234567890")
                message = f"Alert: {context.get('issue', 'No details')}"
                result = self.notification_agent.send_sms(phone, message)
                
                if self.current_monitor:
                    self.current_monitor.end_agent(f"{action_type}_{action_id}", 
                                                   success=result.get("success", False), output=result)
                
                return {"success": result.get("success", False), "data": result}
            
            elif action_type == "escalation_report":
                raw_recipient = action.get("config", {}).get("to")
                recipient = self._resolve_email_recipients(raw_recipient)[0]
                result = self.notification_agent.send_escalation_report(recipient, context)
                
                if self.current_monitor:
                    self.current_monitor.end_agent(f"{action_type}_{action_id}", 
                                                   success=result.get("success", False), output=result)
                
                return {"success": result.get("success", False), "data": result}
            
            else:
                # Generic action
                self.logger.log_action_start(action.get("id"), action_type)
                time.sleep(0.3)
                self.logger.log_action_success(action.get("id"), action_type, 0.3)
                
                if self.current_monitor:
                    self.current_monitor.end_agent(f"{action_type}_{action_id}", 
                                                   success=True, output={"status": "completed"})
                
                return {"success": True, "data": {"status": "completed"}}
        
        except Exception as e:
            self.logger.log_action_failure(action.get("id"), action_type, str(e))
            
            if self.current_monitor:
                self.current_monitor.end_agent(f"{action_type}_{action_id}", 
                                               success=False, error=str(e))
            
            return {"success": False, "error": str(e)}

    def _send_notifications(self, notifications: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Send notifications based on configuration"""
        results = {}
        
        for idx, notif in enumerate(notifications):
            notif_type = notif.get("type", "unknown").lower()
            if notif_type in ["notification", "whatsapp_notification", "whatsapp_message"]:
                notif_type = "whatsapp"
            elif notif_type in ["email_notification"]:
                notif_type = "email"
            trigger = notif.get("trigger", "on_completion")
            
            # Determine if notification should be sent based on trigger
            should_send = True
            
            if trigger == "on_success":
                should_send = context.get("success", False)
            elif trigger == "on_failure":
                should_send = not context.get("success", True)
            elif trigger == "on_negative_sentiment":
                should_send = context.get("sentiment") == "negative"
            
            if should_send:
                if notif_type == "email":
                    raw_recipients = notif.get("recipient") or notif.get("to") or notif.get("recipients")
                    recipients = self._resolve_email_recipients(raw_recipients, context)
                    
                    subject = notif.get("subject", "Workflow Notification")
                    body = notif.get("body", json.dumps(context, indent=2))
                    message_type = notif.get("message_type", "notification")
                    template_type = notif.get("template_type", message_type)
                    
                    # Send to all recipients
                    email_results = []
                    for recipient in recipients:
                        if template_type in ["reminder", "announcement", "error", "workflow_completion"]:
                            result = self.notification_agent.send_professional_email(
                                recipient=recipient,
                                subject=subject,
                                body=body,
                                message_type=template_type,
                                details=context.get("details", {})
                            )
                        else:
                            result = self.notification_agent.send_message(
                                recipient=recipient,
                                subject=subject,
                                body=body,
                                message_type=message_type,
                                title=notif.get("title", subject)
                            )
                        email_results.append(result)
                        
                        self.logger.log(
                            LogLevel.SUCCESS,
                            "Notification",
                            f"📧 Email sent to {recipient}",
                            {"recipient": recipient, "subject": subject}
                        )
                    
                    results[f"email_{idx}"] = {
                        "type": "email",
                        "total": len(recipients),
                        "results": email_results
                    }
                
                elif notif_type == "whatsapp":
                    # Handle WhatsApp notifications
                    raw_phone_numbers = notif.get("phone") or notif.get("recipient") or notif.get("recipients")
                    phone_numbers = self._resolve_phone_numbers(raw_phone_numbers, context)
                    message = notif.get("message", notif.get("body", json.dumps(context, indent=2)))
                    
                    if len(phone_numbers) == 1:
                        result = self.notification_agent.send_whatsapp_alert(phone_numbers[0], message)
                        results[f"whatsapp_{idx}"] = result
                    else:
                        result = self.notification_agent.send_bulk_whatsapp(phone_numbers, message)
                        results[f"whatsapp_bulk_{idx}"] = result
                    
                    self.logger.log(
                        LogLevel.SUCCESS,
                        "Notification",
                        f"💬 WhatsApp messages sent to {len(phone_numbers)} recipient(s)",
                        {"count": len(phone_numbers)}
                    )
                
                elif notif_type == "slack":
                    channel = notif.get("channel", "#alerts")
                    message = notif.get("message", f"Workflow: {context.get('issue', 'Alert')}")
                    result = self.notification_agent.send_slack_message(channel, message)
                    results[f"slack_{idx}"] = result
        
        return results

    def pause_execution(self) -> bool:
        """Pause current execution"""
        self.execution_state["paused"] = True
        self.logger.log(
            LogLevel.INFO,
            "System",
            "⏸️ Workflow execution paused",
            {}
        )
        return True

    def resume_execution(self) -> bool:
        """Resume paused execution"""
        self.execution_state["paused"] = False
        self.logger.log(
            LogLevel.INFO,
            "System",
            "▶️ Workflow execution resumed",
            {}
        )
        return True

    def get_execution_state(self) -> Dict[str, Any]:
        """Get current execution state"""
        return self.execution_state.copy()

    def get_historical_executions(self) -> List[Dict[str, Any]]:
        """Get historical execution data"""
        return self.historical_logger.get_all_workflow_executions()

    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics across all workflows"""
        return self.historical_logger.get_workflow_execution_stats()
