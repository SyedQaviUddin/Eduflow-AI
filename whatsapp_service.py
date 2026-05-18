"""WhatsApp Notification Service - Send messages via WhatsApp"""
import re
import requests
from typing import Dict, Any, List, Optional
from utils.logger import WorkflowLogger, LogLevel
import os

class WhatsAppService:
    """Send notifications via WhatsApp using Twilio or similar service"""
    
    def __init__(self, logger: WorkflowLogger = None):
        self.logger = logger or WorkflowLogger()
        
        # WhatsApp configuration
        self.account_sid = os.getenv("WHATSAPP_ACCOUNT_SID", "").strip()
        self.auth_token = os.getenv("WHATSAPP_AUTH_TOKEN", "").strip()
        self.whatsapp_api_key = os.getenv("WHATSAPP_API_KEY", "").strip()
        self.whatsapp_api_url = os.getenv("WHATSAPP_API_URL", "").strip()
        self.from_number = self._normalize_phone_number(os.getenv("WHATSAPP_FROM_NUMBER", "").strip())
        self.default_from_number = self._normalize_phone_number(os.getenv("DEFAULT_WHATSAPP_NUMBER", "+917671901101").strip())
        self.api_url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(self.account_sid)

        if self.whatsapp_api_url and not self.whatsapp_api_url.lower().startswith(("http://", "https://")) and not self.whatsapp_api_key:
            # If WHATSAPP_API_URL contains only a key by mistake, treat it as the key.
            self.whatsapp_api_key = self.whatsapp_api_url
            self.whatsapp_api_url = ""
            self.logger.log(LogLevel.WARNING, "WhatsApp", "Interpreted WHATSAPP_API_URL as a provider key because no WHATSAPP_API_KEY was set.")

        self.logger.log(LogLevel.INFO, "WhatsApp", "WhatsApp Service initialized")

    def _normalize_phone_number(self, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            return ""
        normalized = re.sub(r"[^\d+]", "", value.strip())
        if normalized.startswith("00"):
            normalized = "+" + normalized.lstrip("0")
        elif not normalized.startswith("+"):
            normalized = "+" + normalized
        return normalized

    def send_message(self, recipient: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Send WhatsApp message
        
        Args:
            recipient: Phone number in E.164 format (+919876543210)
            message: Message content
            message_type: Type of message (text, template, etc.)
        
        Returns:
            Dict with status, recipient, message_id, error (if any)
        """
        
        # Validate phone number format
        recipient = self._normalize_phone_number(recipient)
        if self.whatsapp_api_key and self.whatsapp_api_url:
            return self._send_generic_api_whatsapp(recipient, message, message_type)
        
        # If no Twilio configured, return local notification
        if not self.account_sid or not self.auth_token:
            return self._send_local_whatsapp(recipient, message, message_type)

        if not self.from_number:
            error = "Missing WHATSAPP_FROM_NUMBER for Twilio WhatsApp sending. Set WHATSAPP_FROM_NUMBER in .env to your Twilio WhatsApp sender number."
            self.logger.log(LogLevel.ERROR, "WhatsApp", error, {"recipient": recipient})
            return {
                "success": False,
                "recipient": recipient,
                "error": error,
                "status": "failed"
            }
        
        try:
            # Send via Twilio WhatsApp
            payload = {
                "From": f"whatsapp:{self.from_number}",
                "To": f"whatsapp:{recipient}",
                "Body": message
            }
            
            response = requests.post(
                self.api_url,
                data=payload,
                auth=(self.account_sid, self.auth_token),
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                self.logger.log(
                    LogLevel.SUCCESS,
                    "WhatsApp",
                    f"WhatsApp message sent to {recipient}",
                    {"message_sid": result.get("sid")}
                )
                return {
                    "success": True,
                    "recipient": recipient,
                    "message_id": result.get("sid"),
                    "status": "sent"
                }
            else:
                error = response.json().get("message", "Unknown error")
                hint = ""
                if "From address" in error or "Channel with the specified From address" in error:
                    hint = " Ensure WHATSAPP_FROM_NUMBER is a valid Twilio WhatsApp sender and your Twilio account has that number provisioned."
                self.logger.log(
                    LogLevel.ERROR,
                    "WhatsApp",
                    f"Failed to send WhatsApp message: {error}",
                    {"recipient": recipient, "hint": hint}
                )
                return {
                    "success": False,
                    "recipient": recipient,
                    "error": f"{error}{hint}",
                    "status": "failed"
                }
        
        except Exception as e:
            self.logger.log(
                LogLevel.ERROR,
                "WhatsApp",
                f"WhatsApp service error: {str(e)}",
                {"recipient": recipient}
            )
            return {
                "success": False,
                "recipient": recipient,
                "error": str(e),
                "status": "error"
            }

    def _send_generic_api_whatsapp(self, recipient: str, message: str, message_type: str) -> Dict[str, Any]:
        """
        Send WhatsApp message via a generic API provider using WHATSAPP_API_URL and WHATSAPP_API_KEY.
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.whatsapp_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "recipient": recipient,
                "message": message,
                "type": message_type
            }
            response = requests.post(
                self.whatsapp_api_url,
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code in [200, 201]:
                result = response.json() if response.headers.get("Content-Type", "").startswith("application/json") else {}
                self.logger.log(
                    LogLevel.SUCCESS,
                    "WhatsApp",
                    f"WhatsApp message sent via generic API to {recipient}",
                    {"status_code": response.status_code, "response": result}
                )
                return {
                    "success": True,
                    "recipient": recipient,
                    "message_id": result.get("message_id") or result.get("id"),
                    "status": "sent",
                    "provider": "generic"
                }
            else:
                error = None
                try:
                    error = response.json().get("error")
                except Exception:
                    error = response.text
                self.logger.log(
                    LogLevel.ERROR,
                    "WhatsApp",
                    f"Generic WhatsApp API failed: {error}",
                    {"status_code": response.status_code, "response_text": response.text}
                )
                return {
                    "success": False,
                    "recipient": recipient,
                    "error": error or "Generic WhatsApp API failure",
                    "status": "failed",
                    "status_code": response.status_code
                }
        except Exception as e:
            self.logger.log(
                LogLevel.ERROR,
                "WhatsApp",
                f"Generic WhatsApp service error: {str(e)}",
                {"recipient": recipient}
            )
            return {
                "success": False,
                "recipient": recipient,
                "error": str(e),
                "status": "error"
            }

    def _send_local_whatsapp(self, recipient: str, message: str, message_type: str) -> Dict[str, Any]:
        """
        Local WhatsApp notification (when Twilio not configured)
        Logs the message locally instead of sending via API
        """
        
        local_message = f"""
        ✅ WhatsApp Message Would Be Sent:
        
        To: {recipient}
        From: {self.from_number}
        Type: {message_type}
        Time: {self._get_timestamp()}
        
        Message:
        {message}
        
        Note: Configure WHATSAPP_ACCOUNT_SID and WHATSAPP_AUTH_TOKEN in .env to enable live sending
        """
        
        self.logger.log(
            LogLevel.INFO,
            "WhatsApp",
            f"Local WhatsApp notification to {recipient}",
            {"message": message}
        )
        
        return {
            "success": True,
            "recipient": recipient,
            "message_id": f"local_{self._get_timestamp()}",
            "status": "local_notification",
            "note": "Configured for local testing"
        }
    
    def send_bulk_message(self, recipients: List[str], message: str) -> Dict[str, Any]:
        """
        Send message to multiple recipients
        """
        results = {
            "total": len(recipients),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for recipient in recipients:
            result = self.send_message(recipient, message)
            results["details"].append(result)
            
            if result.get("success"):
                results["successful"] += 1
            else:
                results["failed"] += 1
        
        self.logger.log(
            LogLevel.INFO,
            "WhatsApp",
            f"Bulk message sent to {results['successful']}/{results['total']} recipients",
            results
        )
        
        return results
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Global WhatsApp service instance
_whatsapp_service = None

def get_whatsapp_service(logger: WorkflowLogger = None) -> WhatsAppService:
    """Lazy singleton pattern for WhatsApp service"""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = WhatsAppService(logger)
    return _whatsapp_service
