# 📅 Scheduled Workflows - Complete Guide

## Overview

Nexora AI now supports **scheduled date-based notifications**! Generate workflows that automatically run at specific times with date conditions.

---

## What's New ✨

### **Scheduled Workflow Features**
- ✅ Daily scheduling at specific times (9 AM, 2 PM, etc.)
- ✅ Date-based conditions (after/before/on specific dates)
- ✅ Automatic notification triggering
- ✅ Holiday notifications, reminders, and alerts
- ✅ Multi-recipient support
- ✅ Professional email templates

---

## Example Prompt

Copy and paste this into the Workflow Generator:

```
After 18 May 2026,
every day at 9:00 AM,
check today's date.
If today's date is after 18 May,
send notification to default user saying:
"Today is a holiday 🎉"
```

## Generated Workflow Output

```json
{
  "name": "holiday_notification_after_may_18",
  "trigger": "daily_schedule_9am",
  "schedule": {
    "frequency": "daily",
    "time": "09:00",
    "enabled": true
  },
  "conditions": [
    {
      "type": "date_condition",
      "operator": "greater_than",
      "threshold_date": "2026-05-18",
      "expression": "current_date > 2026-05-18"
    }
  ],
  "actions": [
    {
      "type": "date_check",
      "description": "Check if today's date is after 18 May 2026"
    },
    {
      "type": "send_notification",
      "description": "Send holiday notification"
    }
  ],
  "notifications": [
    {
      "type": "notification",
      "recipient": "default_user",
      "subject": "Holiday Alert",
      "body": "Today is a holiday 🎉",
      "message_type": "announcement"
    }
  ]
}
```

---

## How It Works ⚡

```
⏰ Daily Scheduler (9 AM)
        ↓
📅 Check Current Date
        ↓
❓ Is Date > 18 May?
    /         \
  ✅ YES      ❌ NO
   ↓            ↓
📧 Send         ⏹️ Stop
Notification    Execution
   ↓
🎉 "Today is a holiday 🎉"
```

---

## Syntax Guide

### **Time Specification**
```
9 AM
9:00 AM
09:00
2:30 PM
14:30
```

### **Date Specification**
```
18 May 2026
May 18, 2026
after 18 May 2026
before 25 December 2026
```

### **Frequency**
```
daily
every day
daily at 9 AM
every morning at 9 AM
```

### **Conditions**
```
after [date]      → Trigger only after this date
before [date]     → Trigger only before this date
on [date]         → Trigger only on this date
if [condition]    → Custom conditional logic
```

---

## Example Workflows

### **Example 1: Holiday Reminder**
```
"After 18 May 2026, every day at 9:00 AM, check today's date.
If today's date is after 18 May, send notification saying: Today is a holiday 🎉"
```

**Output**: Daily 9 AM notification after May 18 with professional email

---

### **Example 2: Project Deadline Alert**
```
"Every day at 8:00 AM, if the date is after 31 May 2026,
send reminder to team@company.com about upcoming projects"
```

**Output**: 8 AM daily reminder after May 31

---

### **Example 3: System Maintenance Notice**
```
"Daily at 2:00 PM before 25 December 2026,
send notification about system maintenance window"
```

**Output**: 2 PM daily notification until Dec 25

---

### **Example 4: Team Meeting Reminder**
```
"Every day at 10:00 AM after 1 June 2026,
send reminder to dev-team@company.com about standup"
```

**Output**: 10 AM daily standup reminder

---

## Supported Actions

### **Notification Types**
- **Holiday Alert** 🎉 - Holiday notifications
- **Reminder** 🔔 - Reminders and alerts
- **Announcement** 📢 - Important announcements
- **Error Alert** ❌ - Error notifications
- **Info** ℹ️ - General information

### **Recipients**
- Default user (from .env)
- Specific email addresses
- Multiple recipients (comma-separated)

---

## How to Use

### **Step 1: Open Workflow Generator**
- Go to: http://localhost:8502
- Click: **⚙️ AI Workflow Generator**

### **Step 2: Type Scheduling Request**
Example:
```
After 18 May 2026, every day at 9:00 AM, 
check today's date. If today's date is after 18 May, 
send notification saying: "Today is a holiday 🎉"
```

### **Step 3: Generate Workflow**
- Click: **🚀 Generate Workflow**
- Review the generated workflow
- Check schedule, time, and conditions

### **Step 4: Save Workflow**
- Click: **💾 Save Workflow**
- Workflow saved in `data/workflows/`

### **Step 5: Execute**
- Go to: **🎮 Controls**
- Select your scheduled workflow
- Click: **Execute Workflow**

### **Step 6: View Execution**
- Go to: **📊 Live Monitoring**
- See real-time execution status
- Check email for professional notification

---

## Technical Details

### **Scheduler Agent** (`agents/scheduler_agent.py`)
- Parses natural language scheduling requests
- Extracts dates, times, and frequencies
- Creates schedule configurations
- Evaluates date conditions

### **Scheduling Service** (`utils/scheduling_service.py`)
- Manages scheduled workflow execution
- Tracks execution status
- Enforces date conditions
- Provides execution history

### **DeepSeek API Enhancement** (`utils/deepseek_api.py`)
- Detects scheduling requests
- Generates workflows with schedule metadata
- Smart fallback parsing for date/time extraction

### **Workflow Structure**
```python
{
    "name": str,              # Workflow name
    "trigger": str,           # daily_schedule_9am
    "schedule": {
        "frequency": str,     # daily, weekly, monthly
        "time": str,          # 09:00, 14:30
        "enabled": bool       # true/false
    },
    "conditions": [{
        "type": "date_condition",
        "operator": "greater_than",  # >, >=, ==, <, <=
        "threshold_date": str,       # 2026-05-18
        "expression": str           # current_date > 2026-05-18
    }],
    "actions": [...],
    "notifications": [...]
}
```

---

## Date Condition Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `greater_than` | After date | After 18 May 2026 |
| `greater_than_or_equal` | On or after date | From 18 May 2026 |
| `equal` | On specific date | On 18 May 2026 |
| `less_than` | Before date | Before 25 Dec 2026 |
| `less_than_or_equal` | Up to and including date | Until 25 Dec 2026 |

---

## Email Templates

Notifications automatically use professional HTML templates:

### **Color Coding**
- 🟢 **Green** - Success, holidays, announcements
- 🔴 **Red** - Errors, alerts
- 🟡 **Yellow** - Reminders, warnings
- 🔵 **Blue** - Info, general notifications

### **Features**
- Dark theme (professional styling)
- Color-coded left border
- Clear messaging
- Timestamps
- Mobile responsive
- Company branding

---

## Timezone Handling

- **Current**: Uses system timezone
- **Default**: Assumes local machine time
- **Future**: Multi-timezone support planned

---

## Execution Examples

### **Scheduled Execution Log**

```
[Scheduler Agent]
Workflow triggered at 9:00 AM

[Condition Engine]
Checking date condition: current_date > 2026-05-18
Today: 2026-05-20 ✓ CONDITION MET

[Decision Agent]
Date threshold passed, proceeding with actions

[Action: date_check]
Current date: 2026-05-20
Status: After 18 May 2026 ✓

[Action: send_notification]
Recipient: default_user
Subject: Holiday Alert
Body: Today is a holiday 🎉

[Notification Agent]
Sending notification to default_user
Email template: announcement
Status: SUCCESS

[Workflow]
Completed successfully
Execution time: 2.3s
Notifications sent: 1
```

---

## Limitations & Notes

⚠️ **Important**:
- Scheduling runs based on system time
- Must be actively running to execute
- Currently no persistent background daemon
- Testing: Schedule 9 AM and 2 PM easily to verify
- Dates use ISO format internally (2026-05-18)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflow not executing at scheduled time | Check system time, ensure app is running |
| Date condition not working | Use format "18 May 2026", verify date comparison |
| No notification received | Check email address in .env, check spam folder |
| Time parsing failed | Use "9 AM", "09:00", or "9:00 AM" format |
| Condition always false | Make sure threshold_date is set correctly |

---

## Example: Complete Holiday Workflow

**User Input**:
```
After 18 May 2026, every day at 9:00 AM, 
check today's date. If today's date is after 18 May, 
send notification to default user saying: "Today is a holiday 🎉"
```

**Generated Workflow**:
```json
{
  "name": "holiday_notification_after_may_18",
  "trigger": "daily_schedule_9am",
  "description": "After 18 May 2026, check daily at 9 AM if today is after that date and send a holiday notification",
  "schedule": {
    "frequency": "daily",
    "time": "09:00",
    "enabled": true
  },
  "actions": [
    {
      "id": "action_1",
      "type": "date_check",
      "description": "Check if today's date is after 18 May 2026"
    },
    {
      "id": "action_2",
      "type": "send_notification",
      "description": "Send holiday notification to default user"
    }
  ],
  "conditions": [
    {
      "id": "condition_1",
      "type": "date_condition",
      "operator": "greater_than",
      "threshold_date": "2026-05-18",
      "expression": "current_date > 2026-05-18"
    }
  ],
  "notifications": [
    {
      "type": "notification",
      "trigger": "scheduled",
      "recipient": "default_user",
      "subject": "Holiday Alert",
      "body": "Today is a holiday 🎉",
      "message_type": "announcement"
    }
  ]
}
```

**Execution**:
- 9:00 AM every day after May 18, 2026
- Checks: Is today > May 18? Yes → Send notification
- Result: Professional email with "Today is a holiday 🎉"

---

## Next Steps

1. ✅ **Try It**: Generate your first scheduled workflow
2. ✅ **Customize**: Adjust times, dates, and messages
3. ✅ **Monitor**: Watch execution in Live Monitoring
4. ✅ **Verify**: Check email inbox for professional notification
5. ✅ **Automate**: Build complex scheduling workflows

---

## Files Modified

- ✅ `agents/scheduler_agent.py` - NEW scheduler with date/time parsing
- ✅ `utils/scheduling_service.py` - NEW scheduling service
- ✅ `utils/deepseek_api.py` - Enhanced with schedule detection
- ✅ `test_scheduled_workflows.py` - Comprehensive tests

---

## Support

- Read: `QUICK_REFERENCE.md` for quick start
- Check: `USER_GUIDE.md` for complete documentation
- Run: `python test_scheduled_workflows.py` to verify
- View: Execution logs in `data/logs/`

---

**That's it! You can now create scheduled date-based notifications!** 🚀
