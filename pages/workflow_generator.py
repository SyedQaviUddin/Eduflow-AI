"""Workflow Generator Page - Simple prompt-to-workflow creation for teachers and admins"""
import json
import os
import uuid
from datetime import datetime
import streamlit as st
from utils.deepseek_api import DeepSeekAPI
from utils.workflow_parser import WorkflowParser
from utils.workflow_storage import WorkflowStorage


def show():
    st.title("⚙️ AI Workflow Generator")
    st.markdown("Quickly create and save workflows from teacher/admin prompts. Then use Controls to execute.")

    storage = WorkflowStorage()
    api = DeepSeekAPI()
    parser = WorkflowParser()

    if "workflow_prompt" not in st.session_state:
        st.session_state.workflow_prompt = ""
    if "generated_workflow" not in st.session_state:
        st.session_state.generated_workflow = None
    if "workflow_name" not in st.session_state:
        st.session_state.workflow_name = ""

    templates = [
        {
            "name": "Student Attendance Alert",
            "prompt": "When student attendance falls below 75%, email parents and notify the counselor on WhatsApp.",
        },
        {
            "name": "Exam Reminder",
            "prompt": "When exam dates are published, send a reminder email to all students and a WhatsApp notice to teachers.",
        },
        {
            "name": "Parent Update",
            "prompt": "When a student receives a warning, notify parents by email and send a summary message to the class teacher via WhatsApp.",
        }
    ]

    with st.expander("🎓 Workflow Templates", expanded=True):
        cols = st.columns(len(templates))
        for idx, template in enumerate(templates):
            with cols[idx]:
                st.markdown(f"**{template['name']}**")
                st.caption(template['prompt'])
                if st.button("Use", key=f"template_{idx}"):
                    st.session_state.workflow_prompt = template["prompt"]
                    st.session_state.generated_workflow = None
                    st.rerun()

    st.text_area(
        "Describe the workflow you need:",
        value=st.session_state.workflow_prompt,
        key="workflow_prompt_input",
        height=140,
        placeholder="Example: When a new complaint arrives, analyze sentiment, then email the admin and send WhatsApp alert if urgent."
    )

    st.text_input(
        "Workflow name",
        value=st.session_state.workflow_name,
        key="workflow_name_input",
        placeholder="Example: Attendance Alert"
    )

    if st.button("Generate Workflow", key="generate_workflow"):
        prompt = st.session_state.workflow_prompt.strip()
        if not prompt:
            st.warning("Please enter a workflow prompt before generating.")
        else:
            with st.spinner("Generating workflow structure..."):
                try:
                    workflow_json = api.generate_workflow(prompt)
                    st.session_state.generated_workflow = workflow_json
                    st.session_state.workflow_name = workflow_json.get("name", st.session_state.workflow_name)
                except Exception as exc:
                    st.error(f"Failed to generate workflow: {exc}")

    if st.session_state.generated_workflow:
        st.markdown("---")
        workflow = st.session_state.generated_workflow
        st.subheader("Generated Workflow Preview")

        st.write(f"**Name:** {workflow.get('name', st.session_state.workflow_name)}")
        st.write(f"**Trigger:** {workflow.get('trigger', 'event')} ")

        st.write("**Actions:**")
        for action in workflow.get("actions", []):
            st.write(f"- {action.get('type', 'action')}: {action.get('description', '')}")

        st.write("**Notifications:**")
        for notif in workflow.get("notifications", []):
            st.write(f"- {notif.get('type', 'notification')} to {notif.get('recipient', notif.get('phone', 'N/A'))}")

        st.divider()
        st.subheader("Save Workflow")

        if st.button("Save Workflow", key="save_workflow"):
            workflow_id = str(uuid.uuid4())[:12]
            workflow_name = st.session_state.workflow_name.strip() or workflow.get("name", f"Workflow-{workflow_id}")
            workflow["name"] = workflow_name
            workflow["metadata"] = {
                "prompt": st.session_state.workflow_prompt,
                "creator_email": os.getenv("GMAIL_EMAIL", "sqavi037@gmail.com"),
                "generated_at": datetime.now().isoformat()
            }
            success = storage.save_workflow(workflow_id, workflow, name=workflow_name)
            if success:
                st.success("✅ Workflow saved successfully.")
                st.info("Go to the Controls page to review and execute the saved workflow.")
                st.session_state.generated_workflow = None
                st.session_state.workflow_prompt = ""
                st.session_state.workflow_name = ""
            else:
                st.error("❌ Unable to save the workflow. Please try again.")

    st.markdown("---")
    st.subheader("Saved Workflows")
    saved = storage.list_workflows()

    if saved:
        for idx, wf in enumerate(saved[:6]):
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.write(f"**{wf['name']}**")
                st.caption(f"ID: {wf['id']} | Executions: {wf['execution_count']}")
            with cols[1]:
                if st.button("View", key=f"view_saved_{idx}"):
                    st.write(wf)
            with cols[2]:
                if st.button("Delete", key=f"delete_saved_{idx}"):
                    if storage.delete_workflow(wf['id']):
                        st.success("Deleted workflow")
                        st.rerun()
                    else:
                        st.error("Could not delete workflow")
    else:
        st.info("No workflows saved yet. Generate one to get started.")
