# Nexora AI - Complete User Guide

## 🚀 Quick Start

### 1. **Start the Application**
```bash
cd c:\Users\sqavi\Nexora-ai
streamlit run app.py
```

Then open: **http://localhost:8502**

---

## 📧 Sending Emails via Workflow Generation

### How to Send Email Notifications

#### **Step 1: Go to Workflow Generator**
- Click on **⚙️ AI Workflow Generator** in the left sidebar
- This page lets you describe workflows in plain English

#### **Step 2: Describe What You Want**
Type natural language descriptions like:

```
Send email to syeduddin827@gmail.com that tomorrow is holiday
```

Or:

```
Email admin@company.com and syeduddin827@gmail.com about system maintenance scheduled for tomorrow
```

Or:

```
Send reminder email to syeduddin827@gmail.com about the team meeting
```

#### **Step 3: Generate the Workflow**
1. Click **"🚀 Generate Workflow"** button
2. AI will automatically:
   - Extract email addresses from your text
   - Determine the type of notification (reminder, announcement, alert, etc.)
   - Create a professional workflow
   - Add proper email subjects and bodies

#### **Step 4: Review the Generated Workflow**
- View the JSON structure
- Check email recipients and subjects
- Review the triggers and conditions

#### **Step 5: Save the Workflow**
1. Give your workflow a name (e.g., "Holiday Notification")
2. Click **"💾 SAVE WORKFLOW"**
3. Your workflow is now stored in `data/workflows/`

#### **Step 6: Execute the Workflow**
1. Go to **🎮 Controls** page
2. Select your saved workflow from the dropdown
3. Click **"Execute Workflow"**
4. Monitor execution in real-time

---

## 📬 Email System Features

### **Professional Email Templates**

The system automatically formats emails with:
- ✅ Professional HTML styling
- ✅ Dark theme matching the app
- ✅ Color-coded alerts (green for success, red for errors)
- ✅ Automatic timestamps
- ✅ Clean, readable layout

### **Supported Email Types**

1. **Reminder**: For reminders and notifications
   ```
   "message_type": "reminder"
   ```

2. **Announcement**: For important announcements
   ```
   "message_type": "announcement"
   ```

3. **Error Alert**: For error notifications
   ```
   "message_type": "error"
   ```

4. **Workflow Completion**: When workflows finish
   ```
   "message_type": "workflow_completion"
   ```

5. **Custom Notification**: Any other message
   ```
   "message_type": "notification"
   ```

---

## 🔧 Configuration

### **Email Settings (.env file)**
```
GMAIL_EMAIL=sqavi037@gmail.com
GMAIL_APP_PASSWORD=uhtt iylw hiow wbcc
DEFAULT_NOTIFICATION_EMAIL=sqavi037@gmail.com,syeduddin827@gmail.com
ENABLE_EMAIL_NOTIFICATIONS=true
```

### **Adding Multiple Recipients**
Separate emails with commas in `.env`:
```
DEFAULT_NOTIFICATION_EMAIL=email1@gmail.com,email2@gmail.com,email3@gmail.com
```

---

## 💡 Example Workflows

### **Example 1: Holiday Reminder**
```
"Send email to syeduddin827@gmail.com that tomorrow is holiday"
```
**Result:**
- Workflow Name: "Holiday Notification"
- Recipients: syeduddin827@gmail.com
- Subject: "Tomorrow is Holiday"
- Type: Reminder with professional formatting

### **Example 2: System Maintenance**
```
"Email admin@company.com and syeduddin827@gmail.com about system maintenance tomorrow at 2 PM"
```
**Result:**
- Multiple emails with same information
- Professional announcement format
- Both recipients notified

### **Example 3: Error Alert**
```
"Send alert email to syeduddin827@gmail.com if API connection fails"
```
**Result:**
- Triggered on error
- Red alert styling
- Error details included

---

## 📊 Workflow Execution

### **Real-Time Monitoring**
1. Go to **📊 Live Monitoring** page
2. Watch real-time status of:
   - Workflow execution progress
   - Agent activity
   - Email sending status
   - Error logs

### **Execution History**
1. Go to **📜 Execution History**
2. View all past workflow executions
3. Check:
   - Execution time
   - Success/failure status
   - Email delivery status
   - Error messages

---

## ✅ Verification Checklist

- [x] Email system working
- [x] Professional templates applied
- [x] Workflow generation parses emails
- [x] Multiple recipients supported
- [x] Real-time monitoring
- [x] Execution history saved
- [x] All agents integrated
- [x] Professional styling

---

## 🆘 Troubleshooting

### **Emails Not Sending?**
1. Check `.env` file has correct credentials
2. Verify `ENABLE_EMAIL_NOTIFICATIONS=true`
3. Check Gmail Account Settings for App Passwords
4. Run test: `python test_workflow_gen.py`

### **Workflow Not Generating?**
1. Check internet connection (for DeepSeek API)
2. Verify API key in `.env`
3. Check syntax of prompt
4. See `data/logs/` for detailed errors

### **Emails Not Professional?**
1. Check email template settings
2. Verify `message_type` is set correctly
3. Look at email headers in `data/logs/`

---

## 📁 File Structure

```
Nexora-ai/
├── app.py                          # Main app entry
├── pages/
│   ├── workflow_generator.py       # Generate workflows
│   ├── controls.py                 # Execute workflows
│   ├── live_monitoring.py          # Real-time dashboard
│   └── ...                         # Other pages
├── agents/
│   ├── notification_agent.py       # Handles emails
│   ├── research_agent.py
│   ├── analysis_agent.py
│   └── ...
├── utils/
│   ├── email_service.py            # SMTP client
│   ├── email_templates.py          # Professional templates
│   ├── deepseek_api.py            # Workflow generation
│   ├── workflow_executor.py        # Execution engine
│   └── ...
├── data/
│   ├── workflows/                  # Saved workflows (JSON)
│   ├── logs/                       # Execution logs
│   └── ...
└── .env                            # Configuration
```

---

## 🚀 Next Steps

1. **Start the app**: `streamlit run app.py`
2. **Go to Workflow Generator**: Type a natural language request
3. **Generate workflow**: Click "Generate Workflow"
4. **Save workflow**: Give it a name and save
5. **Execute**: Go to Controls and run the workflow
6. **Monitor**: Watch execution on Live Monitoring page
7. **Verify emails**: Check your inbox for professional formatted emails

---

## 📧 Sample Prompts

Copy and paste these into the workflow generator:

```
1. Send email to syeduddin827@gmail.com that tomorrow is holiday

2. Notify admin@company.com and syeduddin827@gmail.com about system maintenance

3. Send reminder email to syeduddin827@gmail.com about the team meeting at 3 PM

4. Alert syeduddin827@gmail.com if database connection fails

5. Email team@company.com with daily status report

6. Send confirmation email to syeduddin827@gmail.com after task completion

7. Notify managers about the quarterly review process
```

---

## ✨ Features Included

✅ **AI Workflow Generation** - Natural language to workflows
✅ **Professional Email Templates** - Beautiful formatted emails
✅ **Multi-Recipient Support** - Send to multiple emails
✅ **Real-Time Monitoring** - Watch executions live
✅ **Execution History** - Track all workflow runs
✅ **Auto Email Parsing** - Extract emails from text
✅ **Smart Templates** - Different formats for different types
✅ **Error Handling** - Retry logic with exponential backoff
✅ **Activity Logging** - Complete execution logs
✅ **Dark Theme** - Professional UI matching email style

---

## 🎯 System Architecture

```
User Input (Workflow Generator)
    ↓
DeepSeek AI API (generates workflow structure)
    ↓
Workflow JSON (with email notifications)
    ↓
Workflow Executor (runs actions and notifications)
    ↓
Notification Agent (handles emails)
    ↓
Email Service (SMTP client)
    ↓
Gmail SMTP Server
    ↓
Recipients Inbox
```

---

## 📞 Support

For issues or questions:
1. Check `data/logs/` for detailed error messages
2. Verify `.env` configuration
3. Run test script: `python test_workflow_gen.py`
4. Check Streamlit console output for errors

---

**Last Updated**: May 17, 2026  
**Version**: 2.0 (Professional Email System)  
**Status**: ✅ Production Ready

