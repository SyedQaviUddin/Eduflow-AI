"""Professional Email Templates for Nexora AI Workflows"""
import json
from datetime import datetime
from typing import Dict, Any, Optional


class EmailTemplates:
    """Professional email templates for different workflow scenarios"""
    
    @staticmethod
    def get_professional_header(title: str = "Nexora AI Notification") -> str:
        """Get HTML header for professional emails"""
        return f"""
        <!DOCTYPE html>
        <html style="margin: 0; padding: 0;">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
        </head>
        <body style="margin: 0; padding: 0; background: #0a0e27; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;">
        """
    
    @staticmethod
    def get_professional_footer() -> str:
        """Get HTML footer for professional emails"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"""
                    <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #2a3f5f; text-align: center; color: #888; font-size: 12px;">
                        This is an automated notification from Nexora AI<br>
                        Timestamp: {timestamp}<br>
                        <a href="http://localhost:8502" style="color: #00ff00; text-decoration: none;">View Dashboard</a>
                    </p>
                </div>
            </body>
        </html>
        """
    
    @staticmethod
    def notification_alert(subject: str, message: str, details: Dict = None, alert_type: str = "info") -> Dict[str, str]:
        """Generate professional notification alert email"""
        
        # Alert styling
        alert_colors = {
            "success": {"border": "#00ff00", "bg": "rgba(0, 255, 0, 0.1)", "icon": "✅"},
            "error": {"border": "#ff0000", "bg": "rgba(255, 0, 0, 0.1)", "icon": "❌"},
            "warning": {"border": "#ffaa00", "bg": "rgba(255, 170, 0, 0.1)", "icon": "⚠️"},
            "info": {"border": "#0099ff", "bg": "rgba(0, 153, 255, 0.1)", "icon": "ℹ️"}
        }
        
        colors = alert_colors.get(alert_type, alert_colors["info"])
        
        html = EmailTemplates.get_professional_header(f"Nexora AI - {subject}")
        html += f"""
            <div style="background: #0a0e27; color: #eaf7ff; padding: 20px; max-width: 600px; margin: 20px auto;">
                <div style="background: #122b63; border-left: 4px solid {colors['border']}; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 10px 0; color: {colors['border']}; font-size: 20px;">
                        {colors['icon']} {subject}
                    </h2>
                    <p style="margin: 0; color: #eaf7ff; line-height: 1.6; white-space: pre-wrap;">{message}</p>
        """
        
        if details:
            html += """
                    <div style="margin-top: 20px; padding: 15px; background: #0a0e27; border-radius: 5px;">
                        <h3 style="margin: 0 0 10px 0; color: #0099ff; font-size: 14px;">DETAILS:</h3>
                        <ul style="margin: 0; padding-left: 20px;">
            """
            for key, value in details.items():
                html += f"<li style=\"margin: 5px 0; color: #eaf7ff;\"><strong>{key}:</strong> {value}</li>\n"
            html += """
                        </ul>
                    </div>
            """
        
        html += """
                </div>
        """
        html += EmailTemplates.get_professional_footer()
        
        return {
            "html": html,
            "subject": subject,
            "message_type": alert_type
        }
    
    @staticmethod
    def workflow_completion(workflow_name: str, status: str, execution_data: Dict = None) -> Dict[str, str]:
        """Generate workflow completion email"""
        
        status_color = "#00ff00" if status == "success" else "#ff0000"
        status_icon = "✅" if status == "success" else "❌"
        
        message = f"Workflow '{workflow_name}' has completed execution with status: {status.upper()}"
        
        html = EmailTemplates.get_professional_header(f"Workflow Complete - {workflow_name}")
        html += f"""
            <div style="background: #0a0e27; color: #eaf7ff; padding: 20px; max-width: 600px; margin: 20px auto;">
                <div style="background: #122b63; border-left: 4px solid {status_color}; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 10px 0; color: {status_color}; font-size: 20px;">
                        {status_icon} Workflow Execution Complete
                    </h2>
                    <p style="margin: 0 0 15px 0; color: #eaf7ff; font-size: 16px; font-weight: bold;">
                        Workflow: {workflow_name}
                    </p>
                    <p style="margin: 0; color: #eaf7ff; line-height: 1.6;">{message}</p>
        """
        
        if execution_data:
            html += """
                    <div style="margin-top: 20px; padding: 15px; background: #0a0e27; border-radius: 5px;">
                        <h3 style="margin: 0 0 10px 0; color: #0099ff; font-size: 14px;">EXECUTION DETAILS:</h3>
                        <table style="width: 100%; border-collapse: collapse; color: #eaf7ff;">
            """
            for key, value in execution_data.items():
                html += f"""
                            <tr style="border-bottom: 1px solid #2a3f5f;">
                                <td style="padding: 8px; font-weight: bold; color: #00ff00;">{key}</td>
                                <td style="padding: 8px;">{value}</td>
                            </tr>
                """
            html += """
                        </table>
                    </div>
            """
        
        html += """
                </div>
        """
        html += EmailTemplates.get_professional_footer()
        
        return {
            "html": html,
            "subject": f"✅ {workflow_name} - Workflow Complete",
            "message_type": "workflow_completion"
        }
    
    @staticmethod
    def announcement(title: str, content: str, recipients: list = None) -> Dict[str, str]:
        """Generate professional announcement email"""
        
        recipient_text = ", ".join(recipients) if recipients else "Team"
        
        html = EmailTemplates.get_professional_header(f"Announcement - {title}")
        html += f"""
            <div style="background: #0a0e27; color: #eaf7ff; padding: 20px; max-width: 600px; margin: 20px auto;">
                <div style="background: #122b63; border-left: 4px solid #00ff00; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h1 style="margin: 0 0 15px 0; color: #00ff00; font-size: 24px;">
                        📢 {title}
                    </h1>
                    <p style="margin: 0 0 20px 0; color: #eaf7ff; line-height: 1.8; white-space: pre-wrap;">{content}</p>
                    <div style="margin-top: 20px; padding: 15px; background: #0a0e27; border-left: 3px solid #0099ff; border-radius: 5px;">
                        <p style="margin: 0; color: #0099ff; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">
                            Sent to: {recipient_text}
                        </p>
                    </div>
                </div>
        """
        html += EmailTemplates.get_professional_footer()
        
        return {
            "html": html,
            "subject": f"📢 {title}",
            "message_type": "announcement"
        }
    
    @staticmethod
    def error_alert(error_title: str, error_message: str, error_details: Dict = None) -> Dict[str, str]:
        """Generate professional error alert email"""
        
        html = EmailTemplates.get_professional_header(f"Error Alert - {error_title}")
        html += f"""
            <div style="background: #0a0e27; color: #eaf7ff; padding: 20px; max-width: 600px; margin: 20px auto;">
                <div style="background: #122b63; border-left: 4px solid #ff0000; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 10px 0; color: #ff0000; font-size: 20px;">
                        ❌ ERROR: {error_title}
                    </h2>
                    <p style="margin: 0 0 15px 0; color: #ff6666; line-height: 1.6; font-family: monospace;">{error_message}</p>
        """
        
        if error_details:
            html += """
                    <div style="margin-top: 20px; padding: 15px; background: #0a0e27; border-radius: 5px; border: 1px solid #ff0000;">
                        <h3 style="margin: 0 0 10px 0; color: #ff0000; font-size: 14px;">ERROR DETAILS:</h3>
                        <pre style="margin: 0; color: #ff9999; font-size: 12px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word;">
            """
            html += json.dumps(error_details, indent=2)
            html += """
                        </pre>
                    </div>
            """
        
        html += """
                    <div style="margin-top: 20px; padding: 15px; background: rgba(255, 100, 100, 0.1); border-radius: 5px; border-left: 3px solid #ff0000;">
                        <p style="margin: 0; color: #ffaa00; font-size: 12px;">
                            ⚠️ Immediate action may be required. Check your dashboard for more information.
                        </p>
                    </div>
                </div>
        """
        html += EmailTemplates.get_professional_footer()
        
        return {
            "html": html,
            "subject": f"🚨 ERROR: {error_title}",
            "message_type": "error"
        }
    
    @staticmethod
    def reminder(title: str, message: str, details: Dict = None) -> Dict[str, str]:
        """Generate professional reminder email"""
        
        html = EmailTemplates.get_professional_header(f"Reminder - {title}")
        html += f"""
            <div style="background: #0a0e27; color: #eaf7ff; padding: 20px; max-width: 600px; margin: 20px auto;">
                <div style="background: #122b63; border-left: 4px solid #ffaa00; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 10px 0; color: #ffaa00; font-size: 20px;">
                        🔔 Reminder: {title}
                    </h2>
                    <p style="margin: 0 0 15px 0; color: #eaf7ff; line-height: 1.8; white-space: pre-wrap;">{message}</p>
        """
        
        if details:
            html += """
                    <div style="margin-top: 20px; padding: 15px; background: #0a0e27; border-radius: 5px;">
                        <h3 style="margin: 0 0 10px 0; color: #ffaa00; font-size: 14px;">DETAILS:</h3>
                        <ul style="margin: 0; padding-left: 20px;">
            """
            for key, value in details.items():
                html += f"<li style=\"margin: 5px 0; color: #eaf7ff;\"><strong>{key}:</strong> {value}</li>\n"
            html += """
                        </ul>
                    </div>
            """
        
        html += """
                </div>
        """
        html += EmailTemplates.get_professional_footer()
        
        return {
            "html": html,
            "subject": f"🔔 {title}",
            "message_type": "reminder"
        }
