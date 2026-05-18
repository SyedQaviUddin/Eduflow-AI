"""Dashboard Page - Teacher/Admin overview, workflow templates, prompt builder, and visualization"""
import html
import json
import streamlit as st
import streamlit.components.v1 as components
from utils.deepseek_api import DeepSeekAPI
from utils.workflow_parser import WorkflowParser
from utils.workflow_storage import WorkflowStorage


def _render_mermaid(diagram: str, height: int = 520):
    html_doc = f"""
        <div class="diagram-shell">
            <div class="mermaid">{diagram}</div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'neutral',
                securityLevel: 'loose',
                flowchart: {{ useMaxWidth: true, curve: 'basis', nodeSpacing: 70, rankSpacing: 80 }}
            }});
        </script>
        <style>
            .diagram-shell {{
                background: #ffffff;
                border: 1px solid #e1e5ed;
                border-radius: 16px;
                padding: 14px;
                overflow-x: auto;
                box-shadow: 0 12px 24px rgba(32, 64, 112, 0.06);
            }}
            .mermaid {{
                background: transparent;
                color: #1b2430;
                font-family: Inter, sans-serif;
            }}
            .mermaid svg {{
                width: 100% !important;
                height: auto !important;
            }}
        </style>
    """
    components.html(html_doc, height=height)


def _build_mermaid(workflow_json: dict) -> str:
    parser = WorkflowParser()
    nodes, edges = parser.parse_workflow_json(workflow_json)
    mermaid_lines = ["flowchart LR"]
    node_aliases = {}

    for index, node in enumerate(nodes):
        alias = f"n{index}"
        node_aliases[node["id"]] = alias
        label = html.escape(node.get("label", node["id"]).replace('"', ''))
        node_type = node.get("type", "action")

        if node_type == "trigger":
            mermaid_lines.append(f'{alias}("{label}")')
            mermaid_lines.append(f"class {alias} triggerNode")
        elif node_type == "condition":
            mermaid_lines.append(f'{alias}{{"{label}"}}')
            mermaid_lines.append(f"class {alias} conditionNode")
        elif node_type == "notification":
            mermaid_lines.append(f'{alias}[["{label}"]]')
            mermaid_lines.append(f"class {alias} notificationNode")
        else:
            mermaid_lines.append(f'{alias}(["{label}"])')
            mermaid_lines.append(f"class {alias} actionNode")

    mermaid_lines.append("classDef triggerNode fill:#dbeafe,stroke:#1d4ed8,color:#1d4ed8,stroke-width:2px;")
    mermaid_lines.append("classDef actionNode fill:#e0f2fe,stroke:#2563eb,color:#1d4ed8,stroke-width:2px;")
    mermaid_lines.append("classDef conditionNode fill:#fef3c7,stroke:#d97706,color:#92400e,stroke-width:2px;")
    mermaid_lines.append("classDef notificationNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,stroke-width:2px;")

    for idx, edge in enumerate(edges):
        src = node_aliases.get(edge.get("from"), edge.get("from"))
        dst = node_aliases.get(edge.get("to"), edge.get("to"))
        label = edge.get("label", "")
        if label:
            mermaid_lines.append(f"    {src} -->|{label}| {dst}")
        else:
            mermaid_lines.append(f"    {src} --> {dst}")
        mermaid_lines.append(f"    linkStyle {idx} stroke:{edge.get('color', '#2563eb')},stroke-width:{edge.get('width', 2)}px;")

    return "\n".join(mermaid_lines)


def show():
    st.title("📊 Eduflow Teacher & Admin Dashboard")
    st.markdown("Empower teachers and administrators with workflow automation, notification templates, and visual process previews.")

    storage = WorkflowStorage()
    api = DeepSeekAPI()
    parser = WorkflowParser()

    templates = [
        {
            "name": "Exam Reminder Workflow",
            "subtitle": "Notify students and teachers before exams",
            "prompt": "When an exam schedule is published, send an email reminder to students and a WhatsApp update to teachers.",
            "workflow": {
                "name": "Exam Reminder",
                "trigger": "schedule_published",
                "actions": [
                    {"id": "a1", "type": "email_notification", "description": "Send exam reminder email", "config": {"subject": "Exam reminder"}},
                    {"id": "a2", "type": "whatsapp_alert", "description": "Notify teachers on WhatsApp", "config": {"phone": "+917671901101"}}
                ],
                "conditions": [],
                "notifications": [
                    {"type": "email", "trigger": "on_completion", "recipient": "students@example.com", "subject": "Exam Reminder", "body": "Please prepare for the upcoming exam.", "message_type": "reminder"},
                    {"type": "whatsapp", "trigger": "on_completion", "phone": "+917671901101", "message": "Exam schedule is published. Please review."}
                ]
            }
        },
        {
            "name": "Parent Update Workflow",
            "subtitle": "Send polished email and WhatsApp summaries",
            "prompt": "When attendance drops below threshold, email parents and send a WhatsApp update to counselors.",
            "workflow": {
                "name": "Attendance Alert",
                "trigger": "attendance_low",
                "actions": [
                    {"id": "a1", "type": "email_notification", "description": "Email parents and admin", "config": {"subject": "Attendance alert"}},
                    {"id": "a2", "type": "whatsapp_alert", "description": "Notify counselor", "config": {"phone": "+917671901101"}}
                ],
                "conditions": [],
                "notifications": [
                    {"type": "email", "trigger": "on_completion", "recipient": "parents@example.com", "subject": "Attendance Alert", "body": "Your student attendance is below the expected level.", "message_type": "announcement"},
                    {"type": "whatsapp", "trigger": "on_completion", "phone": "+917671901101", "message": "Attendance alert sent to parents."}
                ]
            }
        }
    ]

    if "dashboard_prompt" not in st.session_state:
        st.session_state.dashboard_prompt = ""
    if "dashboard_workflow" not in st.session_state:
        st.session_state.dashboard_workflow = None
    if "dashboard_template" not in st.session_state:
        st.session_state.dashboard_template = None

    section_col1, section_col2, section_col3 = st.columns(3)
    section_col1.metric("Workflows Saved", len(storage.list_workflows()))
    section_col2.metric("Active Workflows", sum(1 for w in storage.list_workflows() if w.get("enabled")))
    section_col3.metric("Notifications Ready", "Email + WhatsApp")

    st.divider()

    with st.expander("🎓 Teacher & Admin Templates", expanded=True):
        for idx, template in enumerate(templates):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"**{template['name']}**  \n{template['subtitle']}")
                st.caption(template['prompt'])
            with cols[1]:
                if st.button("Use Template", key=f"template_use_{idx}"):
                    st.session_state.dashboard_prompt = template["prompt"]
                    st.session_state.dashboard_workflow = template["workflow"]
                    st.session_state.dashboard_template = template["name"]
                    st.rerun()

    st.markdown("---")

    with st.container():
        st.subheader("✍️ Build a workflow with a simple prompt")
        prompt = st.text_area(
            "Describe what you want to automate:",
            value=st.session_state.dashboard_prompt,
            height=130,
            placeholder="Example: When a new complaint arrives, analyze sentiment, then email the admin and send WhatsApp alert if urgent."
        )
        st.session_state.dashboard_prompt = prompt

        gen_col1, gen_col2 = st.columns([2, 1])
        with gen_col1:
            if st.button("Generate Workflow Visualization", key="dashboard_generate"):
                if not prompt.strip():
                    st.warning("Please provide a prompt to generate the workflow.")
                else:
                    with st.spinner("Creating workflow structure..."):
                        try:
                            workflow_json = api.generate_workflow(prompt)
                            st.session_state.dashboard_workflow = workflow_json
                            st.session_state.dashboard_template = None
                        except Exception as exc:
                            st.error(f"Workflow generation failed: {exc}")
        with gen_col2:
            if st.button("Clear Preview", key="dashboard_clear"):
                st.session_state.dashboard_workflow = None
                st.session_state.dashboard_template = None
                st.rerun()

    if st.session_state.dashboard_workflow:
        workflow = st.session_state.dashboard_workflow
        st.markdown("---")
        st.subheader("📈 Workflow Preview")

        summary_col1, summary_col2, summary_col3 = st.columns(3)
        stats = parser.get_workflow_statistics(workflow)
        summary_col1.metric("Actions", stats.get("total_actions", 0))
        summary_col2.metric("Conditions", stats.get("total_conditions", 0))
        summary_col3.metric("Notifications", stats.get("total_notifications", 0))

        st.markdown(f"**Name:** {workflow.get('name', 'Generated Workflow')}  \n**Trigger:** {workflow.get('trigger', 'event')}\n**Source:** {st.session_state.dashboard_template or 'AI prompt'}")
        st.divider()
        mermaid_code = _build_mermaid(workflow)
        _render_mermaid(mermaid_code)

        with st.expander("💾 Workflow JSON", expanded=False):
            st.json(workflow)

    st.markdown("---")

    st.subheader("🧭 Dashboard Actions")
    action_col1, action_col2, action_col3 = st.columns(3)
    with action_col1:
        if st.button("🎮 Go to Controls", key="dash_action_controls"):
            st.session_state.page = "🎮 Controls"
            st.rerun()
    with action_col2:
        if st.button("📋 View Logs", key="dash_action_logs"):
            st.session_state.page = "📋 Execution Logs"
            st.rerun()
    with action_col3:
        if st.button("🔮 View Insights", key="dash_action_insights"):
            st.session_state.page = "🔮 AI Insights"
            st.rerun()

    st.markdown("---")
    st.subheader("📌 Operational Intelligence")
    st.write("Designed for teachers and admins: clear status, ready workflows, and notification control.")
    op_col1, op_col2 = st.columns(2)
    with op_col1:
        st.markdown(
            "- ✅ Teacher-friendly templates for attendance, exams, and parent notifications.\n"
            "- ✅ Email and WhatsApp alerts ready for instant launch.\n"
            "- ✅ Simplified workflow preview with diagram visualization."
        )
    with op_col2:
        st.markdown(
            "- ✅ Control workflows from the Controls page.\n"
            "- ✅ Review execution history in Execution Logs.\n"
            "- ✅ Inspect AI insights and operational health anytime."
        )

    st.divider()
    st.markdown("**Need editing?** Create workflows here and then use the Controls page to review and execute them.")
