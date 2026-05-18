# 📧 Nexora AI - Flexible Email Notification System

## ✅ Overview

The email notification system has been completely overhauled to be **flexible and support any type of message**. You can now send emails with custom subjects, bodies, and message types - all with automatic HTML formatting and professional styling.

---

## 🎯 Key Features

### 1. **Flexible Message Types**
Send different types of messages:
- Workflow notifications
- Error alerts
- System status updates
- Analytics reports
- Custom notifications
- Any custom message type

### 2. **Automatic HTML Formatting**
- Messages are automatically converted to professional HTML
- Built-in styling with Nexora AI theme (dark mode, neon green accents)
- Support for custom titles and details sections
- Timestamps and source attribution included

### 3. **Multiple Recipient Support**
- Send to default recipient from `.env`
- Send to specific recipients
- Override recipient per message
- Support for multiple recipients

### 4. **Retry Logic**
- Automatic retry with exponential backoff
- 3 retry attempts by default
- 2s → 4s → 8s delays between retries
- Detailed error logging

---

## 📝 Usage Examples

### Example 1: Simple Text Message
```python
from utils.email_service import EmailService

service = EmailService()
result = service.send_email(
    recipient="admin@company.com",
    subject="Test Email",
    body="This is a test message",
    is_html=False
)
```

### Example 2: Flexible Message with Auto HTML
```python
from utils.email_service import EmailService

service = EmailService()
result = service.send_message(
    recipient="admin@company.com",
    subject="System Alert",
    body="All systems operational",
    message_type="system_status",
    title="System Status Update",
    details={"status": "online", "agents": 5}
)
```

### Example 3: Using NotificationAgent
```python
from agents.notification_agent import NotificationAgent
from utils.logger import WorkflowLogger

logger = WorkflowLogger()
agent = NotificationAgent(logger)

result = agent.send_message(
    recipient="admin@company.com",
    subject="Workflow Complete",
    body="Workflow execution completed successfully",
    message_type="workflow_completion"
)
```

### Example 4: In Workflow Configuration
```json
{
  "notifications": [
    {
      "type": "email",
      "trigger": "on_completion",
      "recipient": "admin@company.com",
      "subject": "Workflow Execution Report",
      "body": "Your workflow has been executed",
      "message_type": "workflow_report",
      "title": "Execution Report"
    }
  ]
}
```

### Example 5: Custom HTML Content
```python
from utils.email_service import EmailService

service = EmailService()
html_body = """
<h3>Workflow Report</h3>
<p>Status: <strong style="color: green;">SUCCESS</strong></p>
<ul>
  <li>Execution Time: 45s</li>
  <li>Agents Used: 5</li>
  <li>Success Rate: 100%</li>
</ul>
"""

result = service.send_message(
    recipient="admin@company.com",
    subject="Workflow Report",
    body=html_body,
    message_type="workflow_report",
    is_html=True
)
```

---

## 🔧 Configuration

### Environment Variables (.env)
```env
# Gmail SMTP Configuration
GMAIL_EMAIL=sqavi037@gmail.com
GMAIL_APP_PASSWORD=your-app-password

# Default notification recipient
DEFAULT_NOTIFICATION_EMAIL=admin@company.com

# Enable/disable features
ENABLE_EMAIL_NOTIFICATIONS=true
```

### Email Service Methods

#### `send_email(recipient, subject, body, is_html=True)`
Send a direct email without automatic formatting.

**Parameters:**
- `recipient` (str): Email address to send to
- `subject` (str): Email subject line
- `body` (str): Email body content
- `is_html` (bool): Whether body is HTML format

**Returns:** Dict with `success`, `recipient`, `subject`, `attempt`, `message`

---

#### `send_message(recipient=None, subject="Notification", body="", message_type="general", is_html=True, **kwargs)`
Send a flexible message with automatic HTML formatting.

**Parameters:**
- `recipient` (str): Email address (uses default if None)
- `subject` (str): Email subject line
- `body` (str, dict, list): Message content (auto-converted to JSON if dict/list)
- `message_type` (str): Type of message (used for styling/title)
- `is_html` (bool): Convert to HTML if True
- `title` (str): Custom title for HTML body
- `details` (dict): Additional details to display in HTML

**Returns:** Dict with `success`, `recipient`, `subject`, `message_type`, `message`

---

## 🎨 HTML Email Styling

Emails are automatically formatted with:
- **Dark theme**: `#0a0e27` background
- **Accent colors**: 
  - Neon green: `#00ff00` (headers, success)
  - Cyan: `#0099ff` (secondary info)
  - Red: `#ff0000` (errors/alerts)
- **Professional layout**: Centered content, proper spacing
- **Mobile responsive**: Clean formatting on all devices

---

## 🚀 Workflow Integration

### Auto-Send on Workflow Completion
Workflows can now trigger email notifications with flexible configuration:

```json
{
  "id": "wf-001",
  "name": "Data Processing",
  "actions": [...],
  "notifications": [
    {
      "type": "email",
      "trigger": "on_completion",
      "recipient": "team@company.com",
      "subject": "Data Processing Complete",
      "body": "Processing has finished successfully",
      "message_type": "completion"
    },
    {
      "type": "email",
      "trigger": "on_failure",
      "recipient": "admin@company.com",
      "subject": "Processing Failed",
      "body": "An error occurred during processing",
      "message_type": "error"
    }
  ]
}
```

### Trigger Types
- `on_completion`: Send when workflow finishes (success or failure)
- `on_success`: Send only if workflow succeeds
- `on_failure`: Send only if workflow fails
- `on_negative_sentiment`: Send if analysis detects negative sentiment

---

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "recipient": "admin@company.com",
  "subject": "Notification",
  "message": "Email sent successfully on attempt 1",
  "attempt": 1
}
```

### Failure Response
```json
{
  "success": false,
  "recipient": "admin@company.com",
  "subject": "Notification",
  "error": "SMTP connection error",
  "attempts": 3,
  "message": "Failed to send email after 3 attempts"
}
```

---

## 🔍 Debugging

### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Email Configuration
```python
from utils.email_service import EmailService

service = EmailService()
print(f"Sender: {service.sender_email}")
print(f"Default Recipient: {service.default_recipient}")
print(f"SMTP Server: {service.smtp_server}:{service.smtp_port}")
```

### Test Email Delivery
Run the test script:
```bash
python test_email_fix.py
```

---

## ✨ New in This Update

1. ✅ **Fixed hardcoded recipient** - Now reads from workflow config or `.env`
2. ✅ **Flexible message types** - Send any type of message
3. ✅ **Automatic HTML formatting** - Professional styling included
4. ✅ **Custom details support** - Add key-value pairs to emails
5. ✅ **Better error handling** - Detailed error messages with sender/recipient info
6. ✅ **Console logging** - Visual feedback (✅/❌) for email sending
7. ✅ **Workflow integration** - Full support in workflow executor
8. ✅ **Retry logic** - Automatic exponential backoff

---

## 🆘 Troubleshooting

### Emails Not Sending
1. Check `.env` file has correct Gmail credentials
2. Verify Gmail account has "App Passwords" enabled
3. Check internet connection
4. Run `test_email_fix.py` to test directly

### Authentication Failed
- Generate new App Password from Gmail Account Settings
- Update `.env` file with new password
- Restart the application

### SMTP Connection Error
- Verify SMTP server is `smtp.gmail.com` and port is `587`
- Check firewall is not blocking port 587
- Ensure `STARTTLS` is enabled (it is by default)

---

## 📞 Support

For issues or questions about the email system:
1. Check logs in `data/logs/`
2. Run `test_email_fix.py` to diagnose
3. Verify `.env` configuration
4. Check Firebase/Gmail account settings

---

**Last Updated**: May 17, 2026  
**Version**: 2.0 (Flexible Message System)
