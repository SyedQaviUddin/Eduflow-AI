"""Execution Logs Page - Real-time workflow monitoring"""
import streamlit as st
import json
from datetime import datetime
from utils.workflow_executor import WorkflowExecutor
from utils.logger import HistoricalLogger, LogLevel


def show():
    st.title("📋 Execution Logs")
    st.markdown("Real-time workflow execution monitoring and history")
    
    logger = HistoricalLogger()
    executor = WorkflowExecutor()
    
    # Tabs for different log views
    tab1, tab2, tab3 = st.tabs(["Live Logs", "Execution History", "Log Analytics"])
    
    with tab1:
        st.subheader("🔴 Live Execution Monitoring")
        
        # Live execution state
        exec_state = executor.get_execution_state()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_color = "🟢" if exec_state.get("status") == "running" else "🔴"
            st.metric("Status", exec_state.get("status", "idle"), status_color)
        
        with col2:
            st.metric("Current Action", exec_state.get("current_action", "None"))
        
        with col3:
            st.metric("Paused", "Yes" if exec_state.get("paused") else "No")
        
        with col4:
            st.metric("Execution ID", exec_state.get("workflow_id", "None")[:8] if exec_state.get("workflow_id") else "None")
        
        st.divider()
        
        st.write("**Current Execution Logs:**")
        
        # Display sample logs
        sample_logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "agent": "System",
                "message": "🚀 Workflow execution started",
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "agent": "[RESEARCH_ANALYSIS]",
                "message": "Analyzing sentiment...",
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "SUCCESS",
                "agent": "[RESEARCH_ANALYSIS]",
                "message": "✓ Sentiment analysis completed (0.4s)",
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "DEBUG",
                "agent": "[CONDITION]",
                "message": "Evaluated: sentiment == 'negative' → TRUE",
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "agent": "[WHATSAPP]",
                "message": "Sending WhatsApp alert to admin...",
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "SUCCESS",
                "agent": "[WHATSAPP]",
                "message": "✓ Alert sent to +1234567890",
            }
        ]
        
        # Display logs with color coding
        for log in sample_logs:
            level = log.get("level", "INFO")
            if level == "SUCCESS":
                st.success(f"**{log['agent']}** {log['message']}")
            elif level == "ERROR":
                st.error(f"**{log['agent']}** {log['message']}")
            elif level == "WARNING":
                st.warning(f"**{log['agent']}** {log['message']}")
            else:
                st.info(f"**{log['agent']}** {log['message']}")
    
    with tab2:
        st.subheader("📚 Execution History")
        
        executions = logger.get_all_workflow_executions()
        
        if executions:
            # Filter options
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            
            with col_filter1:
                filter_status = st.selectbox(
                    "Filter by Status",
                    ["All", "SUCCESS", "PARTIAL", "FAILED"]
                )
            
            with col_filter2:
                filter_level = st.selectbox(
                    "Filter by Level",
                    ["All", "ERROR", "WARNING", "SUCCESS", "INFO"]
                )
            
            with col_filter3:
                limit = st.slider("Show Last N Executions", 1, 20, 10)
            
            st.divider()
            
            # Display execution history
            for idx, execution in enumerate(executions[:limit]):
                with st.expander(f"📊 Execution {idx + 1} - {execution.get('workflow_id', 'Unknown')}"):
                    col_h1, col_h2, col_h3 = st.columns(3)
                    
                    with col_h1:
                        st.write(f"**Timestamp:** {execution.get('timestamp', 'N/A')}")
                    
                    with col_h2:
                        total_logs = execution.get('total_logs', 0)
                        st.write(f"**Total Steps:** {total_logs}")
                    
                    with col_h3:
                        success_count = execution.get('success_count', 0)
                        error_count = execution.get('error_count', 0)
                        st.write(f"**Success/Errors:** {success_count}/{error_count}")
                    
                    st.json(execution.get('logs', [])[:5])
        else:
            st.info("No execution history available yet")
    
    with tab3:
        st.subheader("📈 Log Analytics")
        
        executions = logger.get_all_workflow_executions()
        
        if executions:
            # Calculate analytics
            total_execs = len(executions)
            total_steps = sum(e.get('total_logs', 0) for e in executions)
            total_errors = sum(e.get('error_count', 0) for e in executions)
            total_success = sum(e.get('success_count', 0) for e in executions)
            
            col_a1, col_a2, col_a3, col_a4 = st.columns(4)
            
            with col_a1:
                st.metric("Total Executions", total_execs)
            
            with col_a2:
                st.metric("Total Steps Executed", total_steps)
            
            with col_a3:
                success_rate = (total_success / total_steps * 100) if total_steps > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%")
            
            with col_a4:
                error_rate = (total_errors / total_steps * 100) if total_steps > 0 else 0
                st.metric("Error Rate", f"{error_rate:.1f}%")
            
            st.divider()
            
            # Log level distribution
            st.write("**Log Level Distribution**")
            
            level_dist = {
                "SUCCESS": 0,
                "ERROR": 0,
                "WARNING": 0,
                "INFO": 0
            }
            
            for execution in executions:
                for log in execution.get('logs', []):
                    level = log.get('level', 'INFO')
                    if level in level_dist:
                        level_dist[level] += 1
            
            st.bar_chart(level_dist)
            
            st.divider()
            
            # Top agents
            st.write("**Top Active Agents**")
            agent_dist = {}
            
            for execution in executions:
                for log in execution.get('logs', []):
                    agent = log.get('agent', 'Unknown')
                    agent_dist[agent] = agent_dist.get(agent, 0) + 1
            
            top_agents = sorted(agent_dist.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for agent, count in top_agents:
                st.write(f"- {agent}: {count} entries")
        else:
            st.info("No analytics data available yet")
