"""Gmail API Email Service - Alternative to SMTP"""
import google.auth.oauthlib.flow
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from typing import Dict, Any, List
import os
import json
import time

class GmailAPIService:
    """Gmail API service - No app password needed!"""
    
    def __init__(self):
        self.service = None
        self.sender_email = os.getenv("GMAIL_EMAIL", "ibrahim70.work@gmail.com")
        self.max_retries = 3
        self._initialize_gmail_api()
    
    def _initialize_gmail_api(self):
        """Initialize Gmail API with your Google account"""
        try:
            # Try to use service account if available
            if os.path.exists('gmail_credentials.json'):
                self.service = self._use_service_account()
            else:
                # Use OAuth2 flow
                self.service = self._use_oauth2()
        except Exception as e:
            print(f"Gmail API initialization: {str(e)}")
            # Will try SMTP fallback
    
    def _use_oauth2(self):
        """Use OAuth2 for Gmail API"""
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            import pickle
            
            SCOPES = ['https://www.googleapis.com/auth/gmail.send']
            
            # Try to load existing token
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
                    if creds and creds.valid:
                        if creds.expired and creds.refresh_token:
                            creds.refresh(Request())
                        return build('gmail', 'v1', credentials=creds)
            
            # Create new flow
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save token for future use
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
            
            return build('gmail', 'v1', credentials=creds)
        
        except Exception as e:
            print(f"OAuth2 setup required: {str(e)}")
            return None
    
    def _use_service_account(self):
        """Use service account credentials"""
        try:
            creds = Credentials.from_service_account_file(
                'gmail_credentials.json',
                scopes=['https://www.googleapis.com/auth/gmail.send']
            )
            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            print(f"Service account error: {str(e)}")
            return None
    
    def send_email(self, recipient: str, subject: str, body: str, is_html: bool = True) -> Dict[str, Any]:
        """Send email via Gmail API"""
        
        if not self.service:
            return {
                "success": False,
                "error": "Gmail API not initialized. Using SMTP fallback."
            }
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Create message
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
                
                # Send via Gmail API
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                send_message = {'raw': raw_message}
                
                result = self.service.users().messages().send(
                    userId='me',
                    body=send_message
                ).execute()
                
                return {
                    "success": True,
                    "recipient": recipient,
                    "message_id": result.get('id'),
                    "message": f"Email sent successfully via Gmail API",
                    "method": "gmail_api"
                }
            
            except Exception as e:
                error_msg = str(e)
                print(f"[ATTEMPT {attempt}] Gmail API send failed: {error_msg[:100]}")
                
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    return {
                        "success": False,
                        "recipient": recipient,
                        "error": error_msg,
                        "attempts": self.max_retries,
                        "message": f"Failed to send email after {self.max_retries} attempts",
                        "method": "gmail_api"
                    }
        
        return {"success": False, "error": "Unknown error", "attempts": self.max_retries}


# Setup instructions
GMAIL_API_SETUP = """
Gmail API Setup (No App Password Needed!)

Option 1: Automatic Setup (Recommended)
===================================
1. Run: python setup_gmail_api.py
2. This will guide you through authentication
3. You'll authorize once in your browser
4. Token saves for future use

Option 2: Manual Setup
====================
1. Go to: https://console.cloud.google.com/
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download as JSON → save as 'credentials.json'
6. Run: python setup_gmail_api.py

Option 3: Service Account (For Automated Systems)
================================================
1. Create service account in Cloud Console
2. Share your Gmail with service account
3. Download credentials → save as 'gmail_credentials.json'
4. Restart app

For now: Regular Gmail password will be used with SMTP fallback
This setup takes 3 minutes and gives permanent access!
"""

if __name__ == "__main__":
    print(GMAIL_API_SETUP)
