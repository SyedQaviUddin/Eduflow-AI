# 🎉 NEW FEATURE: Scheduled Date-Based Notifications!

## What's New ✨

Your Nexora AI now supports **scheduled workflows with date conditions**!

Generate workflows that automatically trigger at specific times with date-based conditions.

---

## Quick Example

**Type this:**
```
After 18 May 2026, every day at 9:00 AM, check today's date.
If today's date is after 18 May, send notification saying: "Today is a holiday 🎉"
```

**System generates:**
```
✓ Workflow Name: holiday_notification_after_may_18
✓ Trigger: daily_schedule_9am
✓ Condition: current_date > 2026-05-18
✓ Action: Send professional email notification
```

**Result:** 📧 Daily 9 AM email sent after May 18!

---

## Try These Examples

### **Example 1: Holiday Reminder** 🎉
```
After 18 May 2026, every day at 9:00 AM, 
check today's date. If today's date is after 18 May, 
send notification saying: "Today is a holiday 🎉"
```

### **Example 2: Team Standup** 🤝
```
Every day at 10:00 AM after 1 June 2026, 
send reminder to dev-team@company.com about standUp meeting
```

### **Example 3: System Maintenance** 🔧
```
Daily at 2:00 PM before 25 December 2026, 
send notification about system maintenance window
```

### **Example 4: Project Deadline** 📅
```
Every day at 8:00 AM after 31 May 2026, 
send reminder to team@company.com: "Project deadline approaching"
```

---

## Supported Syntax

### **Time Formats** ⏰
- `9 AM`
- `9:00 AM`
- `09:00`
- `2:30 PM`
- `14:30`

### **Date Formats** 📅
- `18 May 2026`
- `after 18 May 2026`
- `before 25 December 2026`
- `on 1 June 2026`

### **Frequency** 🔄
- `daily`
- `every day`
- `every morning`
- `every afternoon`

### **Conditions** ❓
- `if date > 18 May` (after this date)
- `if date < 25 Dec` (before this date)
- `if date == 1 June` (on this date)

---

## How to Use

### **Step 1:** Open Nexora
```bash
streamlit run app.py
```

### **Step 2:** Go to Workflow Generator
- Click: **⚙️ AI Workflow Generator**

### **Step 3:** Type Your Scheduling Request
```
After 18 May 2026, every day at 9:00 AM, 
check today's date. If today's date is after 18 May, 
send notification saying: "Today is a holiday 🎉"
```

### **Step 4:** Generate
- Click: **🚀 Generate Workflow**

### **Step 5:** Review & Save
- Check the generated schedule
- Click: **💾 Save Workflow**

### **Step 6:** Execute
- Go to: **🎮 Controls**
- Select workflow
- Click: **Execute Workflow**

### **Step 7:** Verify
- Check **📊 Live Monitoring**
- Check email inbox
- See professional notification ✅

---

## Workflow Features

### **Automatic Features**
✅ Date parsing (18 May 2026 → May 18, 2026)
✅ Time parsing (9 AM → 09:00 in 24-hour format)
✅ Condition evaluation (after/before/on dates)
✅ Email extraction (any mentioned email address)
✅ Professional formatting (HTML emails with styling)
✅ Multi-recipient support
✅ Color-coded alerts
✅ Automatic timestamps

### **Generated Workflow Structure**
```json
{
  "name": "workflow_name",
  "trigger": "daily_schedule_9am",
  "schedule": {
    "frequency": "daily",
    "time": "09:00",
    "enabled": true
  },
  "conditions": [{
    "type": "date_condition",
    "operator": "greater_than",
    "threshold_date": "2026-05-18"
  }],
  "actions": [...],
  "notifications": [...]
}
```

---

## Email Examples

### **Holiday Notification**
```
Subject: Holiday Alert
Body: Today is a holiday 🎉

🟢 Green border (success/holiday)
Professional dark theme
Automatic timestamp
Company branding
```

### **Reminder Notification**
```
Subject: Team Standup Reminder
Body: Remember your 10 AM standup meeting

🟡 Yellow border (reminder)
Professional formatting
Clear action items
```

### **System Alert**
```
Subject: System Maintenance Window
Body: System maintenance scheduled for today

🔴 Red/🟠 Orange border (alert)
Important notice styling
Contact information
```

---

## Date Condition Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `>` (greater_than) | After date | After 18 May 2026 |
| `>=` | On or after | From 18 May 2026 |
| `==` | On exact date | On 18 May 2026 only |
| `<` | Before date | Before 25 Dec 2026 |
| `<=` | Up to date | Until 25 Dec 2026 |

---

## Scheduling Examples

### **After Specific Date**
```
After 18 May 2026, every day at 9 AM
→ Triggers daily from May 18 onwards
```

### **Before Specific Date**
```
Every day at 2 PM before 25 December 2026
→ Triggers daily until Dec 24
```

### **Between Two Dates**
```
Daily at 10 AM after 1 June and before 1 July
→ Triggers daily in June only
```

### **Specific Time**
```
Every morning at 9:30 AM
→ Triggers at 9:30 AM every day
```

---

## Notification Recipients

### **Default User**
```
"send notification to default user"
→ Uses email from .env (DEFAULT_NOTIFICATION_EMAIL)
```

### **Specific Email**
```
"send notification to syeduddin827@gmail.com"
→ Sends to that email
```

### **Multiple Recipients**
```
"send to admin@company.com and team@company.com"
→ Sends to both emails
```

---

## Tips & Tricks

💡 **Tip 1**: Use natural language - system will parse it!
```
"Every day at 9 AM after May 18, notify about holiday"
→ Automatically detected as scheduled workflow
```

💡 **Tip 2**: Dates in any reasonable format work
```
"18 May 2026" = "May 18, 2026" = "2026-05-18"
→ All work the same
```

💡 **Tip 3**: Times are flexible
```
"9 AM" = "09:00" = "9:00 AM"
→ All recognized
```

💡 **Tip 4**: Mix natural language with structure
```
"Every day at 9 AM starting from 18 May..."
→ Perfect for generating scheduled workflows
```

---

## Common Use Cases

### **Holiday Announcements**
When: Every day at 9 AM
Check: If today is a holiday date
Send: Professional notification

### **Team Reminders**
When: Every day at specific time
Recipients: Team email
Message: Meeting reminder, deadline, etc.

### **System Notifications**
When: Based on date conditions
Alert: Maintenance, downtime, updates

### **Project Status**
When: Daily at scheduled time
Content: Project milestone, deadline approaching

### **Birthday Reminders**
When: Every day checking date
Trigger: On specific date
Send: Birthday greeting notification

---

## Execution Flow

```
📅 Every Day at Scheduled Time
        ↓
⏱️ Check if Time Matches
        ↓
❓ Check Date Condition
    /         \
  ✅ YES      ❌ NO
   ↓            ↓
📧 Send         ⏹️ Stop
Notification   Execution
   ↓
📬 Professional Email Delivered
```

---

## Verification

Run test to verify scheduling works:

```bash
python test_scheduled_workflows.py
```

Expected output:
```
✅ Schedule parsing from natural language: WORKING
✅ Date extraction (18 May 2026): WORKING
✅ Time extraction (9:00 AM): WORKING
✅ Frequency detection (daily): WORKING
✅ Condition evaluation (date > threshold): WORKING
✅ Workflow generation with schedule: WORKING
✅ Scheduling service registration: WORKING
```

---

## Documentation

- **Quick Start**: This file
- **Full Guide**: `SCHEDULED_WORKFLOWS_GUIDE.md`
- **Previous Features**: `QUICK_REFERENCE.md`
- **Complete**: `COMPLETE_SUMMARY.md`
- **All Docs**: `USER_GUIDE.md`

---

## What's Different?

### **Before** ❌
```
You: "Send email tomorrow"
System: Sends immediately
```

### **After** ✅
```
You: "After 18 May 2026, every day at 9 AM, send notification"
System: 
  - Generates scheduled workflow
  - Waits until May 18
  - Triggers every 9 AM
  - Sends professional notification
```

---

## Get Started Now!

1. ✅ Run: `streamlit run app.py`
2. ✅ Go to: Workflow Generator
3. ✅ Copy: `After 18 May 2026, every day at 9:00 AM, check today's date. If today's date is after 18 May, send notification saying: "Today is a holiday 🎉"`
4. ✅ Click: Generate
5. ✅ Save: Your workflow
6. ✅ Execute: From Controls
7. ✅ Verify: Check email and monitoring dashboard

---

**🎉 You now have professional scheduled notifications!**

Questions? Check `SCHEDULED_WORKFLOWS_GUIDE.md` for detailed documentation.
