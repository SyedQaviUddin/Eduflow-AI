"""Quick Start Guide - Nexora AI"""

# ⚡ NEXORA AI - QUICK START GUIDE

## 🚀 Launch Application

### 1. Open Terminal
```bash
cd c:\Users\sqavi\Nexora-ai
```

### 2. Run Streamlit App
```bash
streamlit run app.py
```

### 3. Access Dashboard
Open browser to: `http://localhost:8501`

---

## 📖 STEP-BY-STEP WALKTHROUGH

### Step 1: Dashboard Overview
- Click "📊 Dashboard" in sidebar
- See key metrics and system health
- Review recent workflow statistics

### Step 2: Create Your First Workflow
1. Click "⚙️ Workflow Generator" 
2. Enter a natural language prompt:
   ```
   When customer submits complaint form,
   analyze sentiment, if negative send WhatsApp alert
   and email admin with escalation report.
   ```
3. Click "🚀 Generate Workflow"
4. Review the generated workflow
5. Click "💾 Save Workflow"
6. Note the workflow ID

### Step 3: Execute Workflow
1. Go to "🎮 Controls"
2. Select your saved workflow
3. Enter test data:
   - Customer Name: John Doe
   - Message: "This product is terrible!"
4. Check "🔴 Simulate Failure" (optional, to test recovery)
5. Click "▶️ Run Workflow"
6. Watch execution in real-time

### Step 4: View Results
- See execution summary
- Review action results
- Check logs for detailed steps
- View AI-generated insights

### Step 5: Visualize Workflow
1. Go to "🎨 Visualization"
2. Select your workflow
3. See ASCII workflow diagram
4. Review component details

### Step 6: Monitor Execution
1. Go to "📋 Execution Logs"
2. View live execution logs
3. Check execution history
4. Analyze log statistics

### Step 7: Get AI Insights
1. Go to "🔮 AI Insights"
2. View performance metrics
3. Check anomaly detection
4. See bottleneck analysis
5. Review recommendations
6. Check failure predictions

---

## 💡 EXAMPLE WORKFLOWS

### Example 1: Customer Complaint Escalation
**Prompt:**
```
When customer submits a complaint,
analyze the sentiment of their message.
If the sentiment is negative, 
send a WhatsApp alert to the admin
and send an email with an escalation report.
```

**Generated Workflow Actions:**
- Sentiment Analysis
- Conditional Check (is sentiment negative?)
- WhatsApp Alert
- Email Notification
- Escalation Report

---

### Example 2: Data Validation & Notification
**Prompt:**
```
Validate incoming JSON data,
if invalid format detected,
send error alert to Slack channel,
if valid, proceed with processing
and send success notification.
```

**Generated Workflow Actions:**
- Data Validation
- Conditional Check (is data valid?)
- Slack Notification (on error)
- Processing Action (on success)

---

### Example 3: Alert Management
**Prompt:**
```
Monitor system metrics,
if CPU usage exceeds 80% or memory exceeds 90%,
trigger immediate email alert to ops team
and create escalation ticket.
```

**Generated Workflow Actions:**
- Metric Collection
- Threshold Evaluation
- Email Alert
- Ticket Creation
- Reporting

---

## 🎮 CONTROL FEATURES

### Workflow Execution Controls
- **▶️ Run**: Execute workflow with input data
- **⏸️ Pause**: Pause running execution
- **▶️ Resume**: Resume paused execution
- **🧪 Test**: Run workflow in dry-run mode
- **⏰ Schedule**: Schedule workflow execution (coming soon)

### Workflow Management
- **✏️ Edit**: Modify workflow configuration
- **⏸️ Enable/Disable**: Toggle workflow status
- **📋 Duplicate**: Create copy of workflow
- **🗑️ Delete**: Remove workflow permanently

---

## 📊 KEY METRICS TO MONITOR

### Performance Metrics
- **Success Rate**: Percentage of successful executions
- **Execution Time**: Average time per execution
- **Error Rate**: Percentage of failures
- **Recovery Rate**: Successful recoveries from failures

### System Health
- **Total Workflows**: Number of saved workflows
- **Active Workflows**: Currently enabled workflows
- **Total Executions**: Lifetime execution count
- **Average Success Rate**: Overall success percentage

---

## 🔮 AI INSIGHTS FEATURES

### Performance Analysis
- Execution time trends
- Success/failure ratio
- Resource utilization
- Performance improvements

### Anomaly Detection
- Repeated failure patterns
- Performance spikes
- Low traffic anomalies
- Error rate anomalies

### Bottleneck Identification
- Slow-running actions
- High-latency operations
- Resource constraints
- Optimization suggestions

### Recommendations
- Performance optimizations
- Reliability improvements
- Cost reduction strategies
- Scalability enhancements

### Failure Predictions
- Predicted issues (next 7 days)
- Risk probabilities
- Affected workflows
- Prevention strategies

---

## 🛠️ RECOVERY & SELF-HEALING

When a workflow fails:

1. **Failure Detection**: System detects the failure
2. **Recovery Activation**: Recovery Agent activates
3. **Strategy Selection**: Multiple recovery strategies attempted:
   - Retry with exponential backoff
   - Use cached data
   - Fallback endpoints
   - Alternative authentication
   - Skip and continue

4. **Recovery Success**: If recovery succeeds:
   - Continue workflow execution
   - Log recovery strategy used
   - Update recovery statistics

5. **Failed Recovery**: If all strategies fail:
   - Log detailed error
   - Generate alert
   - Create incident report
   - Suggest manual fixes

---

## 📋 EXECUTION LOGS

### Log Levels
- 🟢 **SUCCESS**: Action completed successfully
- 🔴 **ERROR**: Action failed
- 🟡 **WARNING**: Potential issue
- 🔵 **INFO**: General information
- 🟣 **DEBUG**: Detailed debug information

### Log View Modes
1. **Live Logs**: Real-time execution monitoring
2. **History**: Past execution records
3. **Analytics**: Aggregate statistics and trends

---

## ⚙️ CONFIGURATION

### Default Settings
- **Execution Timeout**: 120 seconds
- **Max Retries**: 3 attempts
- **Log Retention**: 90 days
- **Parallel Executions**: 5 concurrent

### API Configuration
- DeepSeek API (required for AI features)
- WhatsApp API (optional)
- Slack Webhook (optional)
- Custom API endpoints (optional)

---

## 🚨 TROUBLESHOOTING

### Issue: Workflow Generation Fails
**Solution**: 
- Check DeepSeek API key is set
- Ensure prompt is clear and detailed
- Try with simpler workflow description

### Issue: Actions Not Executing
**Solution**:
- Check workflow is enabled
- Verify input data format
- Check execution logs for errors
- Review recovery statistics

### Issue: Notifications Not Sending
**Solution**:
- Verify API credentials are correct
- Check network connectivity
- Review notification settings
- Check spam/junk folder for emails

### Issue: Performance Issues
**Solution**:
- Check system resources
- Review bottleneck analysis in Insights
- Consider breaking workflow into sub-workflows
- Optimize slow-running actions

---

## 💾 DATA & STORAGE

### Saved Locations
- **Workflows**: `data/workflows/`
- **Execution Logs**: `data/logs/`
- **System Config**: `.env` file

### Backup & Recovery
- Automatic backup (if enabled)
- Manual export via Settings
- JSON format for easy portability

---

## 📞 SUPPORT & HELP

### Built-in Help
- Click "📖 Docs" in sidebar for documentation
- Click "💬 Support" for contact info
- Check logs for detailed error messages

### Common Questions
**Q: Can I modify workflows after saving?**
A: Currently view-only. Edit feature coming soon.

**Q: How long are logs retained?**
A: Default 90 days, configurable in settings.

**Q: What if a workflow fails?**
A: Recovery Agent automatically attempts recovery using multiple strategies.

**Q: Can I schedule workflows?**
A: Scheduling feature coming soon. Currently manual execution only.

---

## 🎯 NEXT STEPS

1. ✅ Read this guide
2. ✅ Create your first workflow
3. ✅ Execute it and see results
4. ✅ Check logs and insights
5. ✅ Review recovery mechanisms
6. ✅ Customize settings as needed
7. ✅ Explore all features

---

## 📊 DASHBOARD TOUR

### Main Dashboard
- 4 key metrics at top
- Recent workflows list
- System health status
- Quick action buttons
- AI insights preview

### System Status
- API Health
- Processing Engine
- Recovery System
- Analytics Engine
- Cache Status

---

## 🔐 SECURITY NOTES

- API keys stored in `.env` file
- Never commit `.env` to version control
- Credentials not logged to output
- Secure storage of workflow data
- Clean logs retention

---

## 🎓 LEARNING PATH

**Beginner:**
1. Create simple workflow
2. Execute it
3. View results
4. Check logs

**Intermediate:**
1. Create conditional workflows
2. Add multiple notifications
3. Test failure recovery
4. Review insights

**Advanced:**
1. Optimize workflows
2. Implement custom actions
3. Monitor performance
4. Fine-tune recovery strategies

---

**Happy Automating! 🚀**

For more help: support@nexora.ai
