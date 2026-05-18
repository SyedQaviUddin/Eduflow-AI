"""Email Service - Real SMTP email sending with retry logic"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
import time
import os
import json
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """Real SMTP email service with Gmail support"""
    
    def __init__(self):
        # Gmail SMTP settings
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_EMAIL", "sqavi037@gmail.com")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD", "uhtt iylw hiow wbcc")
        self.default_recipient = os.getenv("DEFAULT_NOTIFICATION_EMAIL", "sqavi037@gmail.com")
        self.max_retries = 3
        self.retry_delay = 2
        
    def send_message(self, recipient: str = None, subject: str = "Notification", 
                      body: str = "", message_type: str = "general", 
                      is_html: bool = True, **kwargs) -> Dict[str, Any]:
        """Send any type of message via email with flexible templating"""
        recipient = recipient or self.default_recipient
        
        # Auto-format body if dict/list provided
        if isinstance(body, (dict, list)):
            body = json.dumps(body, indent=2)
        
        # Convert to HTML if not already
        if is_html and not body.startswith('<'):
            body = self._create_html_body(body, message_type, **kwargs)
        
        return self.send_email(recipient, subject, body, is_html)
    
    def _create_html_body(self, content: str, message_type: str = "general", 
                         title: str = None, details: Dict = None, **kwargs) -> str:
        """Create HTML formatted email body for any message type"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        title = title or message_type.upper().replace('_', ' ')
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #0a0e27; color: #eaf7ff; padding: 20px;">
                <div style="background: #122b63; border-left: 4px solid #00ff00; padding: 20px; border-radius: 8px; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #00ff00; margin-top: 0;">📧 {title}</h2>
                    <p style="background: #0a0e27; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap;">{content}</p>
        """
        
        if details:
            html += "<h3 style='color: #0099ff; margin-top: 20px;'>Details:</h3>"
            html += "<ul style='background: #0a0e27; padding: 15px; border-radius: 5px;'>"
            for key, value in details.items():
                html += f"<li><strong>{key}:</strong> {value}</li>"
            html += "</ul>"
        
        html += f"""
                    <p style="margin-top: 20px; font-size: 12px; color: #888;">Timestamp: {timestamp}</p>
                    <p style="margin-top: 10px; font-size: 12px; color: #666;">This is an automated notification from Nexora AI.</p>
                </div>
            </body>
        </html>
        """
        return html
    
    def send_email(self, recipient: str, subject: str, body: str, is_html: bool = True) -> Dict[str, Any]:
        """Send real email via SMTP with retry logic"""
        for attempt in range(1, self.max_retries + 1):
            try:
                # Create email message
                message = MIMEMultipart("alternative")
                message["Subject"] = subject
                message["From"] = self.sender_email
                message["To"] = recipient
                
                # Attach body
                if is_html:
                    part = MIMEText(body, "html")
                else:
                    part = MIMEText(body, "plain")
                message.attach(part)
                
                # Connect and send
                context = ssl.create_default_context()
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls(context=context)
                    server.login(self.sender_email, self.sender_password)
                    server.sendmail(self.sender_email, recipient, message.as_string())
                
                print(f"✅ [EMAIL SENT] To: {recipient} | Subject: {subject} | Attempt: {attempt}")
                
                return {
                    "success": True,
                    "recipient": recipient,
                    "subject": subject,
                    "attempt": attempt,
                    "message": f"Email sent successfully on attempt {attempt}"
                }
            
            except Exception as e:
                error_msg = str(e)
                print(f"❌ [ATTEMPT {attempt}] Email send failed: {error_msg}")
                print(f"   Sender: {self.sender_email}")
                print(f"   Recipient: {recipient}")
                
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** (attempt - 1))
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    return {
                        "success": False,
                        "recipient": recipient,
                        "subject": subject,
                        "error": error_msg,
                        "attempts": self.max_retries,
                        "message": f"Failed to send email after {self.max_retries} attempts"
                    }
        
        return {
            "success": False,
            "error": "Unknown error",
            "attempts": self.max_retries
        }
    
    def send_workflow_alert(self, recipient: str, workflow_name: str, 
                           sentiment: str, execution_id: str, 
                           alert_type: str = "negative_sentiment") -> Dict[str, Any]:
        """Send formatted workflow alert email"""
        
        if alert_type == "negative_sentiment":
            subject = f"⚠️ NEXORA AI ALERT: Negative Sentiment Detected - {workflow_name}"
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background: #0a0e27; color: #eaf7ff; padding: 20px;">
                    <div style="background: #122b63; border-left: 4px solid #ff0000; padding: 20px; border-radius: 8px;">
                        <h2 style="color: #ff0000; margin-top: 0;">⚠️ WORKFLOW EXECUTION ALERT</h2>
                        <p><strong>Workflow:</strong> {workflow_name}</p>
                        <p><strong>Execution ID:</strong> {execution_id}</p>
                        <p><strong>Alert Type:</strong> Negative Sentiment Detected</p>
                        <p><strong>Sentiment:</strong> {sentiment.upper()}</p>
                        <p><strong>Timestamp:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p style="margin-top: 20px; color: #ffaa00;">
                            <strong>Action Required:</strong> Review the workflow execution and take appropriate action.
                        </p>
                    </div>
                    <hr style="border: none; border-top: 1px solid #36d0ff; margin: 20px 0;">
                    <p style="font-size: 0.9em; color: #36d0ff;">
                        This is an automated alert from Nexora AI Workflow Automation Platform
                    </p>
                </body>
            </html>
            """
        
        elif alert_type == "workflow_completed":
            subject = f"✅ NEXORA AI: Workflow Completed - {workflow_name}"
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background: #0a0e27; color: #eaf7ff; padding: 20px;">
                    <div style="background: #0f5f2d; border-left: 4px solid #00ff00; padding: 20px; border-radius: 8px;">
                        <h2 style="color: #00ff00; margin-top: 0;">✅ WORKFLOW EXECUTION COMPLETED</h2>
                        <p><strong>Workflow:</strong> {workflow_name}</p>
                        <p><strong>Execution ID:</strong> {execution_id}</p>
                        <p><strong>Status:</strong> SUCCESS</p>
                        <p><strong>Timestamp:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    <hr style="border: none; border-top: 1px solid #36d0ff; margin: 20px 0;">
                    <p style="font-size: 0.9em; color: #36d0ff;">
                        This is an automated notification from Nexora AI Workflow Automation Platform
                    </p>
                </body>
            </html>
            """
        
        else:  # recovery_activated
            subject = f"🔄 NEXORA AI: Recovery Activated - {workflow_name}"
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background: #0a0e27; color: #eaf7ff; padding: 20px;">
                    <div style="background: #6d1f6f; border-left: 4px solid #ff73ff; padding: 20px; border-radius: 8px;">
                        <h2 style="color: #ff73ff; margin-top: 0;">🔄 RECOVERY ACTIVATED</h2>
                        <p><strong>Workflow:</strong> {workflow_name}</p>
                        <p><strong>Execution ID:</strong> {execution_id}</p>
                        <p><strong>Status:</strong> Self-healing in progress</p>
                        <p><strong>Timestamp:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    <hr style="border: none; border-top: 1px solid #36d0ff; margin: 20px 0;">
                    <p style="font-size: 0.9em; color: #36d0ff;">
                        This is an automated notification from Nexora AI Workflow Automation Platform
                    </p>
                </body>
            </html>
            """
        
        return self.send_email(recipient, subject, html_body, is_html=True)
    
    def send_batch_emails(self, recipients: List[str], subject: str, body: str) -> Dict[str, Any]:
        """Send email to multiple recipients"""
        results = {
            "successful": [],
            "failed": [],
            "total": len(recipients)
        }
        
        for recipient in recipients:
            result = self.send_email(recipient, subject, body)
            if result.get("success"):
                results["successful"].append(recipient)
            else:
                results["failed"].append({"recipient": recipient, "error": result.get("error")})
        
        return results
