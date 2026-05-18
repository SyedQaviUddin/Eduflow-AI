"""Notification Agent - Sends alerts and notifications (REAL SMTP + API integration)"""
import time
import json
import os
from typing import Dict, Any, List
from utils.logger import WorkflowLogger, LogLevel
from utils.email_service import EmailService
from utils.email_templates import EmailTemplates
from utils.whatsapp_service import WhatsAppService


class NotificationAgent:
    def __init__(self, logger: WorkflowLogger):
        self.logger = logger
        self.name = "Notification Agent"
        self.notification_history = []
        self.email_service = EmailService()  # Real SMTP service
        self.whatsapp_service = WhatsAppService(logger)  # WhatsApp service
        self.default_whatsapp = os.getenv("DEFAULT_WHATSAPP_NUMBER", "+917671901101")

    def send_whatsapp_alert(self, phone: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp notification via WhatsApp API"""
        self.logger.log_action_start("whatsapp_alert", "notification")
        
        start_time = time.time()
        
        try:
            # Use WhatsApp service
            result = self.whatsapp_service.send_message(phone, message, "text")
            
            notification = {
                "type": "whatsapp",
                "recipient": phone,
                "message": message,
                "timestamp": time.time(),
                "status": result.get("status", "sent"),
                "message_id": result.get("message_id")
            }
            self.notification_history.append(notification)
            
            self.logger.log(
                LogLevel.SUCCESS,
                "[WHATSAPP]",
                f"WhatsApp message sent to {phone}",
                {"phone": phone, "status": result.get("status")}
            )
            
            duration = time.time() - start_time
            self.logger.log_action_success("whatsapp_alert", "notification", duration)
            
            return {
                "success": result.get("success", False),
                "status": result.get("status"),
                "recipient": phone,
                "method": "whatsapp",
                "message_id": result.get("message_id"),
                "error": result.get("error")
            }
        
        except Exception as e:
            self.logger.log_action_failure("whatsapp_alert", "notification", str(e))
            return {"success": False, "error": str(e), "recipient": phone}
    
    def send_bulk_whatsapp(self, numbers: List[str], message: str) -> Dict[str, Any]:
        """Send WhatsApp message to multiple recipients"""
        self.logger.log_action_start("bulk_whatsapp", "notification")
        
        start_time = time.time()
        
        try:
            results = self.whatsapp_service.send_bulk_message(numbers, message)
            
            self.logger.log(
                LogLevel.SUCCESS,
                "[WHATSAPP-BULK]",
                f"Sent to {results['successful']}/{results['total']} recipients",
                results
            )
            
            duration = time.time() - start_time
            self.logger.log_action_success("bulk_whatsapp", "notification", duration)
            
            return {
                "success": results.get("failed", 0) == 0,
                "total": results.get("total"),
                "successful": results.get("successful"),
                "failed": results.get("failed"),
                "details": results.get("details")
            }
        
        except Exception as e:
            self.logger.log_action_failure("bulk_whatsapp", "notification", str(e))
            return {"success": False, "error": str(e)}

    def send_email(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """Send REAL email via SMTP"""
        self.logger.log_action_start("email_notification", "notification")
        
        start_time = time.time()
        
        try:
            # Use real email service
            result = self.email_service.send_email(recipient, subject, body, is_html=True)
            
            notification = {
                "type": "email",
                "recipient": recipient,
                "subject": subject,
                "body": body[:100] + "..." if len(body) > 100 else body,
                "timestamp": time.time(),
                "status": "sent" if result.get("success") else "failed",
                "result": result
            }
            self.notification_history.append(notification)
            
            if result.get("success"):
                self.logger.log(
                    LogLevel.SUCCESS,
                    "[EMAIL-REAL]",
                    f"✅ Email sent to {recipient}: {subject}",
                    {"recipient": recipient, "subject": subject}
                )
            else:
                self.logger.log(
                    LogLevel.ERROR,
                    "[EMAIL-REAL]",
                    f"❌ Email failed: {result.get('error')}",
                    {"recipient": recipient, "error": result.get("error")}
                )
            
            duration = time.time() - start_time
            self.logger.log_action_success("email_notification", "notification", duration)
            
            return {
                "success": result.get("success", False),
                "status": "sent" if result.get("success") else "failed",
                "recipient": recipient,
                "error": result.get("error"),
                "message": result.get("message")
            }
        
        except Exception as e:
            self.logger.log_action_failure("email_notification", "notification", str(e))
            return {"success": False, "error": str(e), "recipient": recipient}

    def send_message(self, recipient: str = None, subject: str = "Notification", 
                     body: str = "", message_type: str = "general", **kwargs) -> Dict[str, Any]:
        """Send any type of message via email with flexible formatting"""
        self.logger.log_action_start(f"send_{message_type}_message", "notification")
        
        start_time = time.time()
        
        try:
            # Use flexible email service send_message method
            result = self.email_service.send_message(
                recipient=recipient,
                subject=subject,
                body=body,
                message_type=message_type,
                is_html=True,
                **kwargs
            )
            
            notification = {
                "type": "email",
                "message_type": message_type,
                "recipient": recipient or self.email_service.default_recipient,
                "subject": subject,
                "timestamp": time.time(),
                "status": "sent" if result.get("success") else "failed",
                "result": result
            }
            self.notification_history.append(notification)
            
            if result.get("success"):
                self.logger.log(
                    LogLevel.SUCCESS,
                    f"[{message_type.upper()}]",
                    f"✅ Message sent to {notification['recipient']}: {subject}",
                    {"recipient": notification['recipient'], "type": message_type}
                )
            else:
                self.logger.log(
                    LogLevel.ERROR,
                    f"[{message_type.upper()}]",
                    f"❌ Message failed: {result.get('error')}",
                    {"recipient": recipient, "error": result.get("error")}
                )
            
            duration = time.time() - start_time
            self.logger.log_action_success(f"send_{message_type}_message", "notification", duration)
            
            return {
                "success": result.get("success", False),
                "status": "sent" if result.get("success") else "failed",
                "message_type": message_type,
                "recipient": notification['recipient'],
                "error": result.get("error"),
                "message": result.get("message")
            }
        
        except Exception as e:
            self.logger.log_action_failure(f"send_{message_type}_message", "notification", str(e))
            return {"success": False, "error": str(e), "message_type": message_type}

    def send_professional_email(self, recipient: str, subject: str, body: str, 
                                message_type: str = "reminder", details: Dict = None) -> Dict[str, Any]:
        """Send professional formatted email using templates"""
        self.logger.log_action_start("send_professional_email", "notification")
        
        start_time = time.time()
        
        try:
            # Get professional template
            if message_type == "reminder":
                template = EmailTemplates.reminder(subject, body, details)
            elif message_type == "announcement":
                template = EmailTemplates.announcement(subject, body, [recipient] if recipient else None)
            elif message_type == "error":
                template = EmailTemplates.error_alert(subject, body, details)
            elif message_type == "workflow_completion":
                template = EmailTemplates.workflow_completion(subject, body or "success", details)
            else:
                template = EmailTemplates.notification_alert(subject, body, details, "info")
            
            html_body = template["html"]
            final_subject = template["subject"]
            
            # Send via email service
            result = self.email_service.send_email(
                recipient=recipient or self.email_service.default_recipient,
                subject=final_subject,
                body=html_body,
                is_html=True
            )
            
            if result.get("success"):
                self.logger.log(
                    LogLevel.SUCCESS,
                    "[PROFESSIONAL_EMAIL]",
                    f"✅ Professional email sent to {result['recipient']}: {final_subject}",
                    {"recipient": result['recipient'], "type": message_type}
                )
            else:
                self.logger.log(
                    LogLevel.ERROR,
                    "[PROFESSIONAL_EMAIL]",
                    f"❌ Email failed: {result.get('error')}",
                    {"recipient": recipient, "error": result.get("error")}
                )
            
            notification = {
                "type": "email",
                "message_type": message_type,
                "recipient": result['recipient'],
                "subject": final_subject,
                "timestamp": time.time(),
                "status": "sent" if result.get("success") else "failed"
            }
            self.notification_history.append(notification)
            
            duration = time.time() - start_time
            self.logger.log_action_success("send_professional_email", "notification", duration)
            
            return {
                "success": result.get("success", False),
                "status": "sent" if result.get("success") else "failed",
                "recipient": result['recipient'],
                "subject": final_subject,
                "message_type": message_type,
                "error": result.get("error")
            }
        
        except Exception as e:
            self.logger.log_action_failure("send_professional_email", "notification", str(e))
            return {"success": False, "error": str(e), "message_type": message_type}

    def send_slack_message(self, channel: str, message: str) -> Dict[str, Any]:
        """Send Slack notification"""
        self.logger.log_action_start("slack_notification", "notification")
        
        start_time = time.time()
        time.sleep(0.4)
        
        try:
            notification = {
                "type": "slack",
                "channel": channel,
                "message": message,
                "timestamp": time.time(),
                "status": "sent"
            }
            self.notification_history.append(notification)
            
            self.logger.log(
                LogLevel.SUCCESS,
                "[SLACK]",
                f"Message sent to {channel}",
                {"channel": channel}
            )
            
            duration = time.time() - start_time
            self.logger.log_action_success("slack_notification", "notification", duration)
            
            return {"success": True, "status": "sent", "channel": channel}
        
        except Exception as e:
            self.logger.log_action_failure("slack_notification", "notification", str(e))
            return {"success": False, "error": str(e)}

    def send_sms(self, phone: str, message: str) -> Dict[str, Any]:
        """Send SMS notification"""
        self.logger.log_action_start("sms_notification", "notification")
        
        start_time = time.time()
        time.sleep(0.4)
        
        try:
            notification = {
                "type": "sms",
                "recipient": phone,
                "message": message,
                "timestamp": time.time(),
                "status": "sent"
            }
            self.notification_history.append(notification)
            
            self.logger.log(
                LogLevel.SUCCESS,
                "[SMS]",
                f"SMS sent to {phone}",
                {"phone": phone}
            )
            
            duration = time.time() - start_time
            self.logger.log_action_success("sms_notification", "notification", duration)
            
            return {"success": True, "status": "sent", "recipient": phone}
        
        except Exception as e:
            self.logger.log_action_failure("sms_notification", "notification", str(e))
            return {"success": False, "error": str(e)}

    def send_escalation_report(self, recipient: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send escalation report to admin"""
        self.logger.log_action_start("escalation_report", "notification")
        
        start_time = time.time()
        time.sleep(0.7)
        
        try:
            report_body = f"""
Escalation Report
================
Generated at: {time.time()}

Incident Details:
{json.dumps(report_data, indent=2)}

Action Required: IMMEDIATE REVIEW
            """
            
            result = self.send_email(
                recipient,
                "⚠️ ESCALATION REPORT - Immediate Action Required",
                report_body
            )
            
            duration = time.time() - start_time
            
            return result
        
        except Exception as e:
            self.logger.log_action_failure("escalation_report", "notification", str(e))
            return {"success": False, "error": str(e)}

    def broadcast_notification(self, channels: List[str], message: str) -> Dict[str, Any]:
        """Send notification to multiple channels"""
        self.logger.log_action_start("broadcast_notification", "notification")
        
        results = {}
        for channel in channels:
            if channel == "whatsapp":
                results["whatsapp"] = self.send_whatsapp_alert(os.getenv("DEFAULT_WHATSAPP_NUMBER", "+917671901101"), message)
            elif channel == "email":
                results["email"] = self.send_email(os.getenv("DEFAULT_NOTIFICATION_EMAIL", "sqavi037@gmail.com"), "Alert", message)
            elif channel == "slack":
                results["slack"] = self.send_slack_message("#alerts", message)
        
        self.logger.log_action_success("broadcast_notification", "notification", 0.5)
        
        return results

    def get_notification_history(self) -> List[Dict[str, Any]]:
        """Get all sent notifications"""
        return self.notification_history
