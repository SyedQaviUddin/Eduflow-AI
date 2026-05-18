"""Visualization Page - Workflow graph and execution flow (Mermaid)"""
import html
import json

import streamlit as st
from utils.workflow_storage import WorkflowStorage
from utils.workflow_parser import WorkflowParser
import streamlit.components.v1 as components


def _render_mermaid(diagram: str, height: int = 480):
    """Render a Mermaid diagram via an embedded HTML component."""
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
                flowchart: {{ useMaxWidth: true, curve: 'basis', nodeSpacing: 70, rankSpacing: 90 }}
            }});
        </script>
    <style>
            .diagram-shell {{
                background: #ffffff;
                border: 1px solid rgba(148, 163, 184, 0.35);
                border-radius: 16px;
                padding: 18px;
                box-shadow: 0 14px 40px rgba(15, 23, 42, 0.08);
                overflow-x: auto;
            }}

            .mermaid {{
                background: transparent;
                color: #1b2430;
            }}

            .mermaid svg {{
                width: 100% !important;
                height: auto !important;
            }}

            .mermaid .edgePath path,
            .mermaid .flowchart-link {{
                filter: drop-shadow(0 0 5px rgba(148, 163, 184, 0.35));
            }}

            @keyframes nodeGlow {{
                0%, 100% {{ filter: drop-shadow(0 0 2px rgba(59, 130, 246, 0.25)); }}
                50% {{ filter: drop-shadow(0 0 12px rgba(59, 130, 246, 0.20)); }}
            }}

            .mermaid .node.triggerNode rect,
            .mermaid .node.triggerNode circle,
            .mermaid .node.triggerNode polygon,
            .mermaid .node.triggerNode path {{
                animation: nodeGlow 2.4s ease-in-out infinite;
            }}

            .mermaid .node.actionNode rect,
            .mermaid .node.actionNode circle,
            .mermaid .node.actionNode polygon,
            .mermaid .node.actionNode path {{
                animation: nodeGlow 3.2s ease-in-out infinite;
            }}

            .mermaid .node.conditionNode rect,
            .mermaid .node.conditionNode circle,
            .mermaid .node.conditionNode polygon,
            .mermaid .node.conditionNode path {{
                animation: nodeGlow 2.9s ease-in-out infinite;
            }}

            .mermaid .node.notificationNode rect,
            .mermaid .node.notificationNode circle,
            .mermaid .node.notificationNode polygon,
            .mermaid .node.notificationNode path {{
                animation: nodeGlow 3.6s ease-in-out infinite;
            }}

                .mermaid .node.triggerNode rect, .mermaid .node.triggerNode polygon, .mermaid .node.triggerNode path {{ fill: #dbeafe; stroke: #1d4ed8; stroke-width: 2.5px; rx: 16px; ry: 16px; }}
                .mermaid .node.actionNode rect, .mermaid .node.actionNode polygon, .mermaid .node.actionNode path {{ fill: #dbeafe; stroke: #2563eb; stroke-width: 2px; rx: 16px; ry: 16px; }}
                .mermaid .node.conditionNode rect, .mermaid .node.conditionNode polygon, .mermaid .node.conditionNode path {{ fill: #fef3c7; stroke: #d97706; stroke-width: 2.5px; rx: 12px; ry: 12px; }}
                .mermaid .node.notificationNode rect, .mermaid .node.notificationNode polygon, .mermaid .node.notificationNode path {{ fill: #ede9fe; stroke: #7c3aed; stroke-width: 2px; rx: 16px; ry: 16px; }}
    </style>
    """
    components.html(html_doc, height=height)


def show():
    st.title("🎨 Workflow Visualization")
    st.markdown("Streamlined workflow graph (Mermaid) — interactive and readable")

    storage = WorkflowStorage()
    parser = WorkflowParser()

    workflows = storage.list_workflows()
    if not workflows:
        st.warning("No workflows available. Create one in the Workflow Generator page.")
        return

    # Select workflow and show simplified controls
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_idx = st.selectbox("Select workflow to visualize", range(len(workflows)), format_func=lambda i: workflows[i]["name"], key="viz_select_workflow")
        selected = workflows[selected_idx]

    with col2:
        # Enable/disable quick toggle
        enabled = st.button("Toggle Enable/Disable", key=f"viz_toggle_{selected['id']}")
        # small refresh
        if st.button("Refresh", key=f"viz_refresh_{selected['id']}"):
            st.rerun()

    # Load workflow details
    wf_meta = storage.load_workflow(selected["id"])
    wf = wf_meta.get("workflow", {})

    # Build mermaid flow (flowchart LR with labels)
    nodes, edges = parser.parse_workflow_json(wf)

    # Create simple mermaid flow from nodes/edges
    mermaid_lines = ["flowchart LR"]
    node_aliases = {}

    # add nodes with shapes and style classes
    for index, node in enumerate(nodes):
        node_id = node.get("id") or node.get("name", f"n{index}")
        alias = f"node_{index}"
        node_aliases[node_id] = alias

        label = node.get("label") or node.get("name", node_id)
        safe_label = html.escape(label.replace('"', ""))
        node_type = node.get("type", "action")

        if node_type == "trigger":
            mermaid_lines.append(f'    {alias}("{safe_label}")')
            mermaid_lines.append(f"    class {alias} triggerNode")
        elif node_type == "condition":
            mermaid_lines.append(f'    {alias}{{"{safe_label}"}}')
            mermaid_lines.append(f"    class {alias} conditionNode")
        elif node_type == "notification":
            mermaid_lines.append(f'    {alias}[["{safe_label}"]]')
            mermaid_lines.append(f"    class {alias} notificationNode")
        else:
            mermaid_lines.append(f'    {alias}(["{safe_label}"])')
            mermaid_lines.append(f"    class {alias} actionNode")

    mermaid_lines.append("    classDef triggerNode fill:#122b63,stroke:#00d4ff,color:#ffffff,stroke-width:2.5px;")
    mermaid_lines.append("    classDef actionNode fill:#0f5f8d,stroke:#36d0ff,color:#ffffff,stroke-width:2px;")
    mermaid_lines.append("    classDef conditionNode fill:#7d4b00,stroke:#ffb347,color:#ffffff,stroke-width:2.5px;")
    mermaid_lines.append("    classDef notificationNode fill:#6d1f6f,stroke:#ff73ff,color:#ffffff,stroke-width:2px;")

    link_styles = []
    for idx, e in enumerate(edges):
        src = node_aliases.get(e.get("from"), e.get("from"))
        dst = node_aliases.get(e.get("to"), e.get("to"))
        lbl = e.get("label", "")
        arrow = f"    {src} -->|{lbl}| {dst}" if lbl else f"    {src} --> {dst}"
        mermaid_lines.append(arrow)

        color = e.get("color", "#36d0ff")
        width = e.get("width", 2)
        link_styles.append(f"    linkStyle {idx} stroke:{color},stroke-width:{width}px,opacity:0.95;")

    mermaid_lines.extend(link_styles)

    mermaid = "\n".join(mermaid_lines)

    st.divider()
    # Display metrics
    stats = parser.get_workflow_statistics(wf)
    c1, c2, c3 = st.columns(3)
    c1.metric("Nodes", len(nodes))
    c2.metric("Connections", len(edges))
    c3.metric("Complexity", f"{stats.get('complexity_score', 0):.0f}/100")

    st.subheader("📊 Visualization")
    st.caption("Horizontal flow with soft gradients, curved connections, and animated nodes.")
    _render_mermaid(mermaid, height=520)

    st.markdown("---")
    with st.expander("Raw JSON", expanded=False):
        st.json(wf)
    
