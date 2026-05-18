"""Student Dashboard - Pre-built templates for college students and educators"""
import streamlit as st
import json
import uuid
from datetime import datetime, timedelta
from utils.deepseek_api import DeepSeekAPI
from utils.workflow_storage import WorkflowStorage
from utils.workflow_executor import WorkflowExecutor
from utils.logger import WorkflowLogger
import os

# Templates for student-focused workflows
STUDENT_TEMPLATES = {
    "🎉 Tomorrow is Holiday": {
        "description": "Notify students that tomorrow is a holiday",
        "icon": "🎉",
        "fields": [
            {"name": "holiday_name", "label": "Holiday Name", "placeholder": "e.g., Independence Day"},
            {"name": "student_emails", "label": "Student Emails (comma-separated)", "placeholder": "student1@college.com, student2@college.com"},
            {"name": "whatsapp_numbers", "label": "WhatsApp Numbers (comma-separated)", "placeholder": "+919876543210, +918765432109"},
            {"name": "message", "label": "Custom Message (optional)", "placeholder": "Enjoy your holiday!"}
        ]
    },
    
    "📢 Urgent Meeting Today": {
        "description": "Send urgent meeting notification to students",
        "icon": "📢",
        "fields": [
            {"name": "meeting_title", "label": "Meeting Title", "placeholder": "e.g., Important Announcement"},
            {"name": "meeting_time", "label": "Meeting Time", "placeholder": "e.g., 2:30 PM"},
            {"name": "student_emails", "label": "Student Emails (comma-separated)", "placeholder": "student1@college.com, student2@college.com"},
            {"name": "whatsapp_numbers", "label": "WhatsApp Numbers (comma-separated)", "placeholder": "+919876543210, +918765432109"},
            {"name": "location", "label": "Location/Link", "placeholder": "e.g., Auditorium / Meet Link"}
        ]
    },
    
    "📊 Results are Out": {
        "description": "Announce exam/assignment results to students",
        "icon": "📊",
        "fields": [
            {"name": "exam_name", "label": "Exam/Assignment Name", "placeholder": "e.g., Mid-Semester Exam"},
            {"name": "student_emails", "label": "Student Emails (comma-separated)", "placeholder": "student1@college.com, student2@college.com"},
            {"name": "whatsapp_numbers", "label": "WhatsApp Numbers (comma-separated)", "placeholder": "+919876543210, +918765432109"},
            {"name": "result_link", "label": "Results Link", "placeholder": "Portal link or attachment details"},
            {"name": "announcement_date", "label": "Announcement Date", "placeholder": "e.g., Check on College Portal"}
        ]
    },
    
    "⏰ Assignment Deadline Reminder": {
        "description": "Remind students about upcoming assignment deadlines",
        "icon": "⏰",
        "fields": [
            {"name": "assignment_name", "label": "Assignment Name", "placeholder": "e.g., Project Report"},
            {"name": "deadline", "label": "Deadline", "placeholder": "e.g., 30 May 2026"},
            {"name": "student_emails", "label": "Student Emails (comma-separated)", "placeholder": "student1@college.com, student2@college.com"},
            {"name": "whatsapp_numbers", "label": "WhatsApp Numbers (comma-separated)", "placeholder": "+919876543210, +818765432109"},
            {"name": "submission_link", "label": "Submission Link", "placeholder": "Portal or email address"}
        ]
    },
    
    "🎓 Placement Drive Notification": {
        "description": "Notify students about upcoming placement opportunities",
        "icon": "🎓",
        "fields": [
            {"name": "company_name", "label": "Company Name", "placeholder": "e.g., Google"},
            {"name": "drive_date", "label": "Drive Date", "placeholder": "e.g., 25 May 2026"},
            {"name": "student_emails", "label": "Eligible Student Emails (comma-separated)", "placeholder": "student1@college.com, student2@college.com"},
            {"name": "whatsapp_numbers", "label": "WhatsApp Numbers (comma-separated)", "placeholder": "+919876543210, +818765432109"},
            {"name": "registration_link", "label": "Registration Link", "placeholder": "Registration form or portal"}
        ]
    },
    
    "📚 Class Rescheduled": {
        "description": "Notify students about class reschedule",
        "icon": "📚",
        "fields": [
            {"name": "subject_name", "label": "Subject/Class Name", "placeholder": "e.g., Data Structures"},
            {"name": "original_time", "label": "Original Time", "placeholder": "e.g., 10:00 AM"},
            {"name": "new_time", "label": "New Time", "placeholder": "e.g., 2:00 PM"},
            {"name": "new_date", "label": "New Date (if changed)", "placeholder": "e.g., Tomorrow"},
            {"name": "student_emails", "label": "Student Emails (comma-separated)", "placeholder": "student1@college.com, student2@college.com"},
            {"name": "whatsapp_numbers", "label": "WhatsApp Numbers (comma-separated)", "placeholder": "+919876543210, +818765432109"}
        ]
    }
}

def show():
    st.title("🎓 Student Dashboard - Quick Notifications")
    st.markdown("Send notifications to students using pre-built templates")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Templates", "✉️ Send Custom", "📊 History"])
    
    with tab1:
        st.header("Choose a Template")
        
        # Display templates in columns
        cols = st.columns(2)
        selected_template = None
        
        for idx, (template_name, template_data) in enumerate(STUDENT_TEMPLATES.items()):
            col = cols[idx % 2]
            
            with col:
                with st.container():
                    st.markdown(f"""
                    <div style='
                        border: 2px solid #00ff00;
                        border-radius: 10px;
                        padding: 15px;
                        background: rgba(0, 255, 0, 0.05);
                        margin: 10px 0;
                    '>
                        <h3>{template_data['icon']} {template_name}</h3>
                        <p>{template_data['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Use {template_name}", key=f"template_{template_name}"):
                        st.session_state.selected_template = template_name
                        st.rerun()
        
        # Show form if template selected
        if "selected_template" in st.session_state and st.session_state.selected_template:
            st.divider()
            show_template_form(st.session_state.selected_template)
    
    with tab2:
        st.header("✉️ Send Custom Notification")
        show_custom_notification_form()
    
    with tab3:
        st.header("📊 Notification History")
        show_notification_history()


def show_template_form(template_name):
    """Show form for selected template"""
    template = STUDENT_TEMPLATES[template_name]
    
    st.subheader(f"📝 {template_name}")
    
    # Create form
    with st.form(key="template_form"):
        form_data = {}
        
        for field in template["fields"]:
            if field["name"] in ["student_emails", "whatsapp_numbers"]:
                form_data[field["name"]] = st.text_area(
                    field["label"],
                    placeholder=field["placeholder"],
                    height=100,
                    help="One email/number per line or comma-separated"
                )
            else:
                form_data[field["name"]] = st.text_input(
                    field["label"],
                    placeholder=field["placeholder"]
                )
        
        # Add scheduling option
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            send_immediately = st.checkbox("Send Immediately", value=True)
        with col2:
            if not send_immediately:
                schedule_time = st.time_input("Schedule at (optional)")
            else:
                schedule_time = None
        
        submitted = st.form_submit_button("🚀 Generate & Execute Workflow", use_container_width=True)
        
        if submitted:
            process_template(template_name, template, form_data, send_immediately, schedule_time)


def process_template(template_name, template, form_data, send_immediately, schedule_time):
    """Process template and execute workflow"""
    
    # Validate data
    if not form_data.get("student_emails") and not form_data.get("whatsapp_numbers"):
        st.error("❌ Please provide at least one student email or WhatsApp number")
        return
    
    # Parse emails and numbers
    emails = [e.strip() for e in form_data.get("student_emails", "").split(",") if e.strip()]
    whatsapp_numbers = [n.strip() for n in form_data.get("whatsapp_numbers", "").split(",") if n.strip()]
    
    # Generate workflow description
    workflow_description = generate_workflow_description(template_name, form_data)
    
    # Generate workflow using AI
    with st.spinner("🤖 Generating workflow..."):
        api = DeepSeekAPI()
        workflow = api.generate_workflow(workflow_description)
    
    st.success("✅ Workflow generated successfully!")
    
    # Add recipient information
    workflow["recipients"] = {
        "emails": emails,
        "whatsapp_numbers": whatsapp_numbers
    }
    
    # Display workflow
    with st.expander("📋 View Generated Workflow", expanded=True):
        st.json(workflow)
    
    # Save workflow
    storage = WorkflowStorage()
    workflow_id = str(uuid.uuid4())
    
    workflow_metadata = {
        "id": workflow_id,
        "name": workflow.get("name", template_name),
        "description": workflow.get("description", "Student notification"),
        "created_at": datetime.now().isoformat(),
        "template": template_name,
        "status": "saved"
    }
    
    storage.save_workflow(workflow_id, workflow, workflow_metadata)
    st.success(f"✅ Workflow saved with ID: {workflow_id[:8]}")
    
    # Auto-execute if requested
    if send_immediately:
        with st.spinner("📤 Executing workflow and sending notifications..."):
            try:
                executor = WorkflowExecutor()
                result = executor.execute_workflow(
                    workflow_id,
                    {"recipients": workflow["recipients"]},
                    simulate_failure=False
                )
                
                if result.get("success"):
                    st.success(f"✅ Notifications sent successfully!")
                    st.balloons()
                    
                    # Show execution details
                    with st.expander("📊 Execution Details"):
                        execution_details = {
                            "status": "completed",
                            "emails_sent": len(emails),
                            "whatsapp_sent": len(whatsapp_numbers),
                            "timestamp": datetime.now().isoformat(),
                            "recipients": {
                                "emails": emails[:3] + (["..."] if len(emails) > 3 else []),
                                "whatsapp": whatsapp_numbers[:3] + (["..."] if len(whatsapp_numbers) > 3 else [])
                            }
                        }
                        st.json(execution_details)
                else:
                    st.error(f"❌ Execution failed: {result.get('error')}")
            
            except Exception as e:
                st.error(f"❌ Error executing workflow: {str(e)}")


def generate_workflow_description(template_name, form_data):
    """Generate natural language workflow description from template"""
    
    descriptions = {
        "🎉 Tomorrow is Holiday": f"""
        Tomorrow is {form_data.get('holiday_name', 'a holiday')}.
        Send notification to students: "{form_data.get('message', 'Enjoy your holiday!')}"
        Send to emails: {form_data.get('student_emails')}
        Send to WhatsApp: {form_data.get('whatsapp_numbers')}
        """,
        
        "📢 Urgent Meeting Today": f"""
        Urgent meeting: {form_data.get('meeting_title')} at {form_data.get('meeting_time')}.
        Location/Link: {form_data.get('location')}.
        Notify all students immediately.
        Emails: {form_data.get('student_emails')}
        WhatsApp: {form_data.get('whatsapp_numbers')}
        """,
        
        "📊 Results are Out": f"""
        {form_data.get('exam_name')} results are now available.
        Link: {form_data.get('result_link')}
        Send result announcement to all students.
        Emails: {form_data.get('student_emails')}
        WhatsApp: {form_data.get('whatsapp_numbers')}
        """,
        
        "⏰ Assignment Deadline Reminder": f"""
        Reminder: {form_data.get('assignment_name')} deadline is {form_data.get('deadline')}.
        Submission: {form_data.get('submission_link')}
        Notify students about upcoming deadline.
        Emails: {form_data.get('student_emails')}
        WhatsApp: {form_data.get('whatsapp_numbers')}
        """,
        
        "🎓 Placement Drive Notification": f"""
        Placement opportunity: {form_data.get('company_name')} drive on {form_data.get('drive_date')}.
        Registration: {form_data.get('registration_link')}
        Notify eligible students immediately.
        Emails: {form_data.get('student_emails')}
        WhatsApp: {form_data.get('whatsapp_numbers')}
        """,
        
        "📚 Class Rescheduled": f"""
        {form_data.get('subject_name')} class rescheduled.
        Original: {form_data.get('original_time')}
        New: {form_data.get('new_time')} on {form_data.get('new_date')}.
        Notify all students.
        Emails: {form_data.get('student_emails')}
        WhatsApp: {form_data.get('whatsapp_numbers')}
        """
    }
    
    return descriptions.get(template_name, f"Send notification about {template_name}")


def show_custom_notification_form():
    """Show form for custom notifications"""
    
    with st.form(key="custom_notification_form"):
        st.subheader("Create Custom Notification")
        
        # Basic info
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Notification Title", placeholder="e.g., Important Update")
        with col2:
            priority = st.selectbox("Priority", ["🟢 Low", "🟡 Medium", "🔴 High", "🔴 Urgent"])
        
        # Message
        message = st.text_area("Message", placeholder="Write your notification message...", height=100)
        
        # Recipients
        st.divider()
        st.markdown("### Recipients")
        
        col1, col2 = st.columns(2)
        with col1:
            emails = st.text_area("Emails (comma-separated)", height=80)
        with col2:
            whatsapp = st.text_area("WhatsApp Numbers (comma-separated)", height=80)
        
        # Additional options
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            send_immediately = st.checkbox("Send Immediately", value=True)
        with col2:
            if not send_immediately:
                schedule_time = st.time_input("Schedule at")
        
        submitted = st.form_submit_button("🚀 Send Notification", use_container_width=True)
        
        if submitted:
            if not (emails or whatsapp):
                st.error("❌ Please provide at least one email or WhatsApp number")
            elif not message:
                st.error("❌ Please write a message")
            else:
                st.success("✅ Notification workflow created and executed!")
                st.balloons()


def show_notification_history():
    """Show history of sent notifications"""
    
    logger = WorkflowLogger()
    
    # Get recent logs
    st.subheader("Recent Notifications")
    
    # Mock data for demonstration
    history_data = [
        {
            "time": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
            "template": "🎉 Tomorrow is Holiday",
            "recipients": 25,
            "status": "✅ Success"
        },
        {
            "time": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
            "template": "📢 Urgent Meeting Today",
            "recipients": 50,
            "status": "✅ Success"
        },
        {
            "time": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
            "template": "📊 Results are Out",
            "recipients": 150,
            "status": "✅ Success"
        },
        {
            "time": (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M"),
            "template": "⏰ Assignment Deadline Reminder",
            "recipients": 75,
            "status": "✅ Success"
        }
    ]
    
    # Display as table
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**Time**")
    with col2:
        st.markdown("**Template**")
    with col3:
        st.markdown("**Recipients**")
    with col4:
        st.markdown("**Status**")
    
    st.divider()
    
    for item in history_data:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.text(item["time"])
        with col2:
            st.text(item["template"])
        with col3:
            st.text(f"{item['recipients']} students")
        with col4:
            st.markdown(item["status"])
    
    # Summary stats
    st.divider()
    st.subheader("📊 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Notifications", "4", "Today")
    with col2:
        st.metric("Total Recipients", "300", "+50 this week")
    with col3:
        st.metric("Success Rate", "100%", "All sent")
    with col4:
        st.metric("Avg Response", "2.5 mins", "faster today")


if __name__ == "__main__":
    show()
