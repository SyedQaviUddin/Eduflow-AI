"""Live Execution Monitoring Page - Real-time workflow execution dashboard"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any
import time
import json

from utils.monitoring import get_monitoring_manager, EventType
from utils.workflow_executor import WorkflowExecutor


def show():
    st.title("⚡ Live Execution Monitoring")
    st.markdown("Real-time workflow execution tracking with performance metrics")
    
    monitoring_manager = get_monitoring_manager()
    
    # Get active executions
    active_monitors = monitoring_manager.get_active_monitors()
    all_monitors = monitoring_manager.get_all_monitors()
    
    # Top metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Active Workflows",
            len(active_monitors),
            f"{len(active_monitors)} running"
        )
    
    with col2:
        completed = sum(1 for m in all_monitors.values() if m.status == "completed")
        st.metric("Completed", completed, "workflows")
    
    with col3:
        failed = sum(1 for m in all_monitors.values() if m.status == "failed")
        st.metric("Failed", failed, "workflows")
    
    with col4:
        total_events = sum(len(m.events) for m in all_monitors.values())
        st.metric("Total Events", total_events, "logged")
    
    with col5:
        avg_duration = 0
        completed_monitors = [m for m in all_monitors.values() if m.status == "completed"]
        if completed_monitors:
            avg_duration = sum(m.total_duration for m in completed_monitors) / len(completed_monitors)
        st.metric("Avg Duration", f"{avg_duration:.2f}s", "per workflow")
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔴 Live Status",
        "📊 Agent Performance",
        "📈 Metrics Dashboard",
        "📋 Event Stream",
        "⏱️ Timeline"
    ])
    
    # Tab 1: Live Status
    with tab1:
        st.subheader("Active Workflow Executions")
        
        if active_monitors:
            for monitor in active_monitors:
                _display_execution_status(monitor)
        else:
            st.info("No active workflows running")
        
        if st.button("🔄 Refresh Status"):
            st.rerun()
    
    # Tab 2: Agent Performance
    with tab2:
        st.subheader("Agent Execution Performance")
        
        if all_monitors:
            # Collect all agent metrics
            agent_data = []
            for monitor in all_monitors.values():
                for agent_name, metrics in monitor.get_all_agent_metrics().items():
                    agent_data.append({
                        "Agent": agent_name,
                        "Workflow": monitor.workflow_name,
                        "Status": metrics.get("status", "unknown"),
                        "Duration (s)": metrics.get("duration", 0),
                        "Success": metrics.get("success_count", 0),
                        "Errors": metrics.get("error_count", 0),
                        "CPU %": metrics.get("cpu_usage", 0),
                        "Memory MB": metrics.get("memory_mb", 0)
                    })
            
            if agent_data:
                df = pd.DataFrame(agent_data)
                
                # Agent duration chart
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Agent Execution Time")
                    agent_duration = df.groupby("Agent")["Duration (s)"].mean()
                    fig = px.bar(
                        x=agent_duration.index,
                        y=agent_duration.values,
                        labels={"x": "Agent", "y": "Avg Duration (s)"},
                        color_discrete_sequence=["#00ff00"]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Success Rate by Agent")
                    agent_success = df.groupby("Agent").apply(
                        lambda x: (x["Success"].sum() / (x["Success"].sum() + x["Errors"].sum()) * 100) 
                        if (x["Success"].sum() + x["Errors"].sum()) > 0 else 0
                    )
                    fig = px.bar(
                        x=agent_success.index,
                        y=agent_success.values,
                        labels={"x": "Agent", "y": "Success Rate %"},
                        color_discrete_sequence=["#0099ff"]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                st.subheader("Detailed Agent Metrics")
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No agent metrics available yet")
        else:
            st.info("No workflows have been executed yet")
    
    # Tab 3: Metrics Dashboard
    with tab3:
        st.subheader("Performance Metrics")
        
        if all_monitors:
            metrics_data = []
            for monitor in all_monitors.values():
                summary = monitor.get_summary()
                metrics_data.append({
                    "Workflow": monitor.workflow_name,
                    "Status": monitor.status,
                    "Duration (s)": monitor.total_duration,
                    "Agents": summary.get("total_agents", 0),
                    "Success Rate %": round(summary.get("success_rate", 0), 2),
                    "Events": summary.get("event_count", 0),
                    "Total Success": summary.get("total_success", 0),
                    "Total Errors": summary.get("total_errors", 0)
                })
            
            df = pd.DataFrame(metrics_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Workflow Duration Distribution")
                fig = px.histogram(
                    df,
                    x="Duration (s)",
                    nbins=20,
                    color_discrete_sequence=["#00ff00"],
                    labels={"Duration (s)": "Execution Time (seconds)"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Success Rate Distribution")
                fig = px.box(
                    df,
                    y="Success Rate %",
                    color_discrete_sequence=["#0099ff"]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            st.subheader("All Workflows Summary")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No metrics available yet")
    
    # Tab 4: Event Stream
    with tab4:
        st.subheader("Real-time Event Stream")
        
        if all_monitors:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_workflow = st.selectbox(
                    "Select Workflow",
                    [m.workflow_name for m in all_monitors.values()],
                    key="workflow_select"
                )
            
            with col2:
                max_events = st.slider("Show Last N Events", 5, 100, 20)
            
            # Find the selected monitor
            selected_monitor = None
            for monitor in all_monitors.values():
                if monitor.workflow_name == selected_workflow:
                    selected_monitor = monitor
                    break
            
            if selected_monitor:
                events = selected_monitor.get_recent_events(max_events)
                
                if events:
                    # Create event display
                    for event in reversed(events):
                        _display_event(event)
                else:
                    st.info("No events recorded yet")
            else:
                st.warning("Workflow not found")
        else:
            st.info("No workflows available")
    
    # Tab 5: Timeline
    with tab5:
        st.subheader("Execution Timeline")
        
        if all_monitors:
            # Create timeline data
            timeline_data = []
            for monitor in all_monitors.values():
                if monitor.start_time:
                    for agent_name, metrics in monitor.get_all_agent_metrics().items():
                        if metrics.get("start_time"):
                            timeline_data.append({
                                "Task": agent_name,
                                "Workflow": monitor.workflow_name,
                                "Start": metrics.get("start_time"),
                                "End": metrics.get("end_time") or datetime.now().isoformat(),
                                "Status": metrics.get("status", "unknown")
                            })
            
            if timeline_data:
                df_timeline = pd.DataFrame(timeline_data)
                df_timeline["Start"] = pd.to_datetime(df_timeline["Start"])
                df_timeline["End"] = pd.to_datetime(df_timeline["End"])
                
                # Create Gantt chart
                fig = px.timeline(
                    df_timeline,
                    x_start="Start",
                    x_end="End",
                    y="Task",
                    color="Status",
                    hover_data=["Workflow"],
                    title="Execution Timeline",
                    color_discrete_map={
                        "running": "#FFD700",
                        "completed": "#00FF00",
                        "failed": "#FF0000",
                        "idle": "#808080"
                    }
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No timeline data available")
        else:
            st.info("No workflows available")


def _display_execution_status(monitor) -> None:
    """Display status of a single execution"""
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_emoji = "🟢" if monitor.status == "running" else "🟡" if monitor.status == "completed" else "🔴"
            st.write(f"{status_emoji} **{monitor.workflow_name}**")
        
        with col2:
            elapsed = (datetime.now() - monitor.start_time).total_seconds() if monitor.start_time else 0
            st.write(f"⏱️ {elapsed:.1f}s")
        
        with col3:
            agent_count = len(monitor.agents)
            st.write(f"🤖 {agent_count} agents")
        
        with col4:
            event_count = len(monitor.events)
            st.write(f"📊 {event_count} events")
        
        # Progress bar
        progress_data = monitor.get_progress()
        total_agents = len(monitor.agents)
        completed_agents = sum(1 for m in monitor.agents.values() if m.status.value == "completed")
        
        if total_agents > 0:
            progress = completed_agents / total_agents
            st.progress(progress, text=f"{completed_agents}/{total_agents} agents completed")
        
        # Agent status
        with st.expander("📋 Agent Details"):
            agent_statuses = progress_data.get("agent_statuses", {})
            for agent_name, status in agent_statuses.items():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                
                with col_a:
                    status_icon = "✅" if status["status"] == "completed" else "⏳" if status["status"] == "running" else "❌"
                    st.write(f"{status_icon} {agent_name}")
                
                with col_b:
                    st.write(f"{status['duration']:.2f}s")
                
                with col_c:
                    if status.get("error"):
                        st.error("Error", icon="⚠️")


def _display_event(event: Dict[str, Any]) -> None:
    """Display a single event"""
    timestamp = event.get("timestamp", "")
    event_type = event.get("event_type", "unknown")
    agent_name = event.get("agent_name", "System")
    message = event.get("message", "")
    
    # Color coding based on event type
    if event_type == "workflow_start":
        st.success(f"🚀 **Workflow Started** - {message}")
    elif event_type == "workflow_end":
        st.success(f"✅ **Workflow Completed** - {message}")
    elif event_type == "agent_start":
        st.info(f"▶️ **Agent Started** ({agent_name}) - {message}")
    elif event_type == "agent_end":
        st.success(f"✅ **Agent Completed** ({agent_name}) - {message}")
    elif event_type == "email_sent":
        st.success(f"📧 **Email Sent** - {message}")
    elif event_type == "recovery_triggered":
        st.warning(f"🔄 **Recovery Triggered** - {message}")
    elif event_type == "error_occurred":
        st.error(f"❌ **Error** - {message}")
    else:
        st.write(f"📌 {message}")
