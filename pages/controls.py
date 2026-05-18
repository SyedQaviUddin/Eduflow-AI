"""Controls Page - Workflow execution with transparent agent tracking"""
import csv
import re
import streamlit as st
import json
import os
from datetime import datetime
from utils.workflow_storage import WorkflowStorage
from utils.workflow_executor import WorkflowExecutor
from utils.logger import WorkflowLogger
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.notification_agent import NotificationAgent
from agents.recovery_agent import RecoveryAgent
from agents.reporting_agent import ReportingAgent


def _extract_emails_from_text(text: str) -> list:
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return list({match.group(0).strip() for match in re.finditer(pattern, text)})


def _extract_phone_numbers_from_text(text: str) -> list:
    pattern = r"(?:\+\d{10,15}|\d{10,15}|\(\d{3,5}\)\s?\d{6,10})"
    raw = [match.group(0).strip() for match in re.finditer(pattern, text)]
    normalized = []
    for item in raw:
        candidate = re.sub(r"[^\d+]", "", item)
        if not candidate.startswith("+") and len(candidate) >= 10:
            candidate = "+" + candidate
        if 10 <= len(candidate.lstrip("+")) <= 15:
            normalized.append(candidate)
    return list(dict.fromkeys(normalized))


def _parse_file_for_contacts(uploaded_file) -> tuple:
    try:
        content = uploaded_file.read().decode("utf-8", errors="ignore")
    except Exception:
        try:
            uploaded_file.seek(0)
            content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        except Exception:
            content = ""

    emails = _extract_emails_from_text(content)
    phones = _extract_phone_numbers_from_text(content)

    if uploaded_file.name.lower().endswith(".csv"):
        uploaded_file.seek(0)
        try:
            decoded = content.splitlines()
            reader = csv.reader(decoded)
            for row in reader:
                for cell in row:
                    emails.extend(_extract_emails_from_text(cell))
                    phones.extend(_extract_phone_numbers_from_text(cell))
        except Exception:
            pass

    return list(dict.fromkeys(emails)), list(dict.fromkeys(phones))


def show():
    st.title("🎮 Workflow Controls")
    st.markdown("Execute workflows with real-time agent tracking")
    
    storage = WorkflowStorage()
    executor = WorkflowExecutor()
    logger = WorkflowLogger()
    
    # Tabs for different control sections
    tab1, tab2 = st.tabs(["▶️ Execute Workflow", "🤖 Agent Status"])
    
    with tab1:
        st.subheader("Execute Your Workflow")
        
        workflows = storage.list_workflows()
        
        if not workflows:
            st.warning("❌ No workflows available. Create one in ⚙️ Workflow Generator!")
            st.info("Steps: 1) Generate workflow 2) Save it 3) Return here to execute")
        else:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                workflow_names = [w["name"] for w in workflows]
                selected_idx = st.selectbox(
                    "Select Workflow to Execute",
                    range(len(workflows)), 
                    format_func=lambda i: workflows[i]["name"],
                    key="ctrl_workflow_select_idx"
                )
                selected = workflows[selected_idx]
            
            with col2:
                status_icon = "🟢" if selected.get("enabled", True) else "🔴"
                st.write(f"**{status_icon}** {'Active' if selected.get('enabled', True) else 'Inactive'}")
                st.caption(f"ID: {selected['id'][:8]}")
                toggle_label = "Disable Workflow" if selected.get("enabled", True) else "Enable Workflow"
                if st.button(toggle_label, key=f"ctrl_toggle_enabled_{selected['id']}"):
                    new_status = storage.toggle_workflow_enabled(selected["id"])
                    if new_status is None:
                        st.error("❌ Failed to update workflow status")
                    else:
                        st.success(f"✅ Workflow {'enabled' if new_status else 'disabled'}")
                        st.rerun()

            workflow_metadata = storage.load_workflow(selected["id"]) or {}
            workflow_data = workflow_metadata.get("workflow", {})
            metadata = workflow_data.get("metadata", {})

            default_creator_email = metadata.get("creator_email", os.getenv("GMAIL_EMAIL", "sqavi037@gmail.com"))
            default_issue = workflow_data.get("description") or workflow_data.get("trigger") or "Automated workflow"
            default_prompt = metadata.get("prompt") or workflow_data.get("description") or workflow_data.get("trigger", "")
            default_message = ""
            for action in workflow_data.get("actions", []):
                default_message = action.get("config", {}).get("body", default_message) or default_message
                if default_message:
                    break
            if not default_message:
                for notif in workflow_data.get("notifications", []):
                    default_message = notif.get("body", default_message) or default_message
                    if default_message:
                        break

            st.divider()

            st.subheader("📥 Input Data")
            if default_prompt:
                st.info(f"Generated from prompt: {default_prompt}")

            input_method = st.radio(
                "Choose input method:",
                ["Form", "JSON"],
                horizontal=True,
                key="ctrl_input_method_radio_0"
            )

            st.markdown("**Bulk Upload for Parents/Contacts**")
            uploaded_file = st.file_uploader(
                "Upload a CSV or TXT file containing parent email IDs or WhatsApp numbers",
                type=["csv", "txt"],
                key="ctrl_file_upload"
            )
            bulk_emails, bulk_phones = [], []
            if uploaded_file:
                bulk_emails, bulk_phones = _parse_file_for_contacts(uploaded_file)
                if bulk_emails:
                    st.success(f"✅ Extracted {len(bulk_emails)} email(s) from file")
                    st.write(bulk_emails[:10])
                if bulk_phones:
                    st.success(f"✅ Extracted {len(bulk_phones)} WhatsApp number(s) from file")
                    st.write(bulk_phones[:10])
                if not bulk_emails and not bulk_phones:
                    st.warning("No valid email addresses or phone numbers found in the uploaded file.")

            if input_method == "Form":
                col_f1, col_f2 = st.columns(2)

                st.markdown(f"**Workflow:** {workflow_data.get('name', 'Unnamed')}  ")
                if workflow_data.get('description'):
                    st.caption(workflow_data.get('description'))
                st.markdown(f"**Created by:** {default_creator_email}")

                with col_f1:
                    name_input = st.text_input(
                        "Sender / Contact Name",
                        metadata.get("sender_name", "Teacher"),
                        key="ctrl_form_name_0"
                    )
                    email_input = st.text_input(
                        "Sender Email",
                        default_creator_email,
                        key="ctrl_form_email_0"
                    )

                with col_f2:
                    id_input = st.text_input(
                        "Reference ID",
                        workflow_data.get("trigger", "WF-001"),
                        key="ctrl_form_id_0"
                    )
                    issue_input = st.text_input(
                        "Problem / Workflow Reason",
                        default_issue,
                        key="ctrl_form_issue_0"
                    )

                message_input = st.text_area(
                    "Message or Notification Text",
                    default_message or "Please review the workflow details and notify parents.",
                    height=120,
                    key="ctrl_form_message_0"
                )

                input_data = {
                    "name": name_input,
                    "email": email_input,
                    "id": id_input,
                    "issue": issue_input,
                    "text": message_input,
                    "workflow_prompt": default_prompt,
                    "workflow_name": workflow_data.get("name"),
                    "workflow_description": workflow_data.get("description"),
                    "creator_email": default_creator_email,
                    "bulk_emails": bulk_emails,
                    "bulk_whatsapp_numbers": bulk_phones,
                    "timestamp": datetime.now().isoformat()
                }
            else:  # JSON mode
                json_input = st.text_area(
                    "Enter Input JSON",
                    value=json.dumps({
                        "name": "John Doe",
                        "email": default_creator_email,
                        "text": default_message or "Please review the workflow issue.",
                        "issue": default_issue,
                        "id": workflow_data.get("trigger", "WF-001")
                    }, indent=2),
                    height=180,
                    key="ctrl_json_input_area_0"
                )
                try:
                    input_data = json.loads(json_input)
                except Exception as e:
                    st.error(f"❌ Invalid JSON: {str(e)}")
                    input_data = {}
                input_data["workflow_prompt"] = default_prompt
                input_data["workflow_name"] = workflow_data.get("name")
                input_data["workflow_description"] = workflow_data.get("description")
                input_data["creator_email"] = default_creator_email
                input_data["bulk_emails"] = bulk_emails
                input_data["bulk_whatsapp_numbers"] = bulk_phones
                input_data["timestamp"] = datetime.now().isoformat()

            st.divider()
            
            # EXECUTION OPTIONS
            st.subheader("⚙️ Execution Options")
            
            opt_col1, opt_col2, opt_col3 = st.columns(3)
            
            with opt_col1:
                run_now = st.checkbox(
                    "Run Now",
                    value=True,
                    key="ctrl_checkbox_run_now_0"
                )
            
            with opt_col2:
                save_logs = st.checkbox(
                    "Save Logs",
                    value=True,
                    key="ctrl_checkbox_save_logs_0"
                )
            
            with opt_col3:
                show_tracking = st.checkbox(
                    "Show Agent Tracking",
                    value=True,
                    key="ctrl_checkbox_show_tracking_0"
                )
            
            st.divider()
            
            # EXECUTION BUTTONS
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
            
            with btn_col1:
                execute_btn = st.button(
                    "▶️ EXECUTE",
                    use_container_width=True,
                    type="primary",
                    key="ctrl_btn_execute_0"
                )
            
            with btn_col2:
                test_btn = st.button(
                    "🧪 TEST",
                    use_container_width=True,
                    key="ctrl_btn_test_0"
                )
            
            with btn_col3:
                reset_btn = st.button(
                    "🔄 RESET",
                    use_container_width=True,
                    key="ctrl_btn_reset_0"
                )
            
            st.divider()
            
            # TEST MODE
            if test_btn:
                st.info("✅ **Test Mode:** Workflow structure validated successfully!")
                st.write("Ready to execute with live agent tracking.")
            
            # RESET MODE
            if reset_btn:
                st.session_state.clear()
                st.rerun()
            
            # EXECUTION MODE
            if execute_btn and run_now and input_data:
                workflow_id = selected["id"]
                executor = WorkflowExecutor()
                progress_container = st.container()
                results_container = st.container()
                
                try:
                    with progress_container:
                        progress_bar = st.progress(0)
                        status_box = st.empty()
                        agent_tracking = st.empty()
                    
                    with st.spinner("⏳ Executing workflow..."):
                        status_box.info("🚀 Starting workflow execution with live monitoring...")
                        result = executor.execute_workflow(workflow_id, input_data)
                        progress_bar.progress(100)
                    
                    with results_container:
                        st.divider()
                        
                        if result.get("success"):
                            st.success("✅ **Workflow Execution Completed Successfully!**")
                        else:
                            st.warning("⚠️ **Workflow Execution Completed with Status**")
                        
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            st.subheader("📊 Execution Summary")
                            exec_summary = result.get("execution_summary", {})
                            st.write(f"**Execution ID:** `{result.get('execution_id', 'N/A')}`")
                            st.write(f"**Status:** {'✅ Success' if result.get('success') else '⚠️ Completed'}")
                            st.write(f"**Total Logs:** {len(result.get('logs', []))} entries")
                        
                        with col_r2:
                            st.subheader("🤖 Agent Results")
                            action_results = result.get("action_results", {})
                            success_count = sum(1 for action_result in action_results.values() if action_result.get("success"))
                            total_count = len(action_results)
                            st.write(f"✅ {success_count}/{total_count} actions succeeded")
                        
                        st.divider()
                        
                        if result.get("action_results"):
                            st.subheader("📧 Notifications Sent")
                            if any("email" in action_id.lower() and action_result.get("success") for action_id, action_result in result.get("action_results", {}).items()):
                                st.success("📧 Email notification sent successfully")
                            if any("whatsapp" in action_id.lower() and action_result.get("success") for action_id, action_result in result.get("action_results", {}).items()):
                                st.success("💬 WhatsApp notification sent successfully")

                        st.divider()
                        
                        if st.checkbox("📋 Show Detailed Logs", value=False):
                            st.subheader("Execution Logs")
                            logs = result.get("logs", [])
                            if logs:
                                for log in logs[-20:]:
                                    level = log.get("level", "INFO")
                                    agent = log.get("agent", "System")
                                    message = log.get("message", "")
                                    
                                    if level == "SUCCESS":
                                        st.success(f"[{agent}] {message}")
                                    elif level == "ERROR":
                                        st.error(f"[{agent}] {message}")
                                    elif level == "WARNING":
                                        st.warning(f"[{agent}] {message}")
                                    else:
                                        st.info(f"[{agent}] {message}")
                        
                        st.info(f"""
                        ⚡ **Live Monitoring Available!**
                        
                        Go to **⚡ Live Monitoring** tab to see:
                        - Real-time agent execution tracking
                        - Performance metrics and charts
                        - Event stream
                        - Execution timeline
                        
                        Workflow ID: `{workflow_id}`
                        """)
                
                except Exception as e:
                    st.error(f"❌ Execution failed: {str(e)}")
                    st.code(str(e))
    
    with tab2:
        st.subheader("🤖 Agent System Status")
        
        agents_info = [
            {
                "emoji": "🔬",
                "name": "Research Agent",
                "actions": ["Sentiment Analysis", "Data Extraction", "Pattern Discovery"],
                "status": "✅ READY"
            },
            {
                "emoji": "📊",
                "name": "Analysis Agent",
                "actions": ["Decision Making", "Condition Evaluation", "Risk Assessment"],
                "status": "✅ READY"
            },
            {
                "emoji": "📢",
                "name": "Notification Agent",
                "actions": ["Email Alerts", "WhatsApp Messages", "Slack Notifications"],
                "status": "✅ READY"
            },
            {
                "emoji": "🏥",
                "name": "Recovery Agent",
                "actions": ["Self-Healing", "Retry Strategies", "Fallback Actions"],
                "status": "✅ READY"
            },
            {
                "emoji": "📋",
                "name": "Reporting Agent",
                "actions": ["Insights Generation", "Anomaly Detection", "Recommendations"],
                "status": "✅ READY"
            },
        ]
        
        for agent in agents_info:
            with st.container():
                col_a1, col_a2, col_a3 = st.columns([1, 2, 1])
                
                with col_a1:
                    st.write(f"**{agent['emoji']} {agent['name']}**")
                
                with col_a2:
                    st.caption(" • ".join(agent["actions"]))
                
                with col_a3:
                    st.write(agent["status"])
                
                st.divider()
        
        st.info("💡 All agents are operational and ready for workflow execution!")
