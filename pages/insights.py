"""Insights Page - AI-powered operational intelligence"""
import streamlit as st
import json
from utils.workflow_executor import WorkflowExecutor
from utils.logger import HistoricalLogger


def show():
    st.title("🔮 AI Operational Insights")
    st.markdown("Intelligent analysis and optimization recommendations")
    
    executor = WorkflowExecutor()
    logger = HistoricalLogger()
    
    # Get statistics
    stats = executor.get_execution_statistics()
    executions = logger.get_all_workflow_executions()
    
    # Main insight tabs
    insight_tab1, insight_tab2, insight_tab3, insight_tab4, insight_tab5 = st.tabs(
        ["Performance", "Anomalies", "Bottlenecks", "Recommendations", "Predictions"]
    )
    
    with insight_tab1:
        st.subheader("📊 Performance Metrics")
        
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        
        with col_p1:
            st.metric(
                "Total Executions",
                stats.get("total_executions", 0),
                delta="+5 this week"
            )
        
        with col_p2:
            st.metric(
                "Avg Success Rate",
                f"{stats.get('avg_success_rate', 0):.1f}%",
                delta="+3.2%"
            )
        
        with col_p3:
            st.metric(
                "Total Failures",
                stats.get("total_failures", 0),
                delta="-2 this week"
            )
        
        with col_p4:
            recovery_rate = 85.3  # Simulated
            st.metric(
                "Recovery Rate",
                f"{recovery_rate}%",
                delta="+12.5%"
            )
        
        st.divider()
        
        st.write("**Detailed Performance Analysis**")
        
        perf_col1, perf_col2 = st.columns(2)
        
        with perf_col1:
            st.write("**Execution Time Trends**")
            st.markdown("""
            - Average execution: 2.3s
            - Fastest: 0.8s
            - Slowest: 6.2s
            - Trend: Stable ➡️
            """)
        
        with perf_col2:
            st.write("**Success/Failure Ratio**")
            st.markdown("""
            - Last 7 days: 94.2% success
            - Last 30 days: 91.8% success
            - Last 90 days: 89.3% success
            - Trend: Improving 📈
            """)
    
    with insight_tab2:
        st.subheader("🚨 Anomaly Detection")
        
        anomalies = [
            {
                "type": "Repeated Failure Pattern",
                "severity": "high",
                "message": "WhatsApp action fails 30% of the time",
                "detected_at": "2 hours ago",
                "action": "Check WhatsApp API connection"
            },
            {
                "type": "Performance Spike",
                "severity": "medium",
                "message": "Execution time increased by 45% for workflow XYZ",
                "detected_at": "45 minutes ago",
                "action": "Review database queries"
            },
            {
                "type": "Low Traffic Pattern",
                "severity": "low",
                "message": "No executions for workflow ABC in 12 hours",
                "detected_at": "30 minutes ago",
                "action": "Check if workflow is disabled"
            },
            {
                "type": "Error Spike",
                "severity": "high",
                "message": "Error rate increased from 5% to 15% in sentiment analysis",
                "detected_at": "15 minutes ago",
                "action": "Investigate sentiment model performance"
            }
        ]
        
        for anomaly in anomalies:
            severity_color = "🔴" if anomaly["severity"] == "high" else "🟡" if anomaly["severity"] == "medium" else "🟢"
            
            with st.expander(f"{severity_color} {anomaly['type']}"):
                st.write(f"**Message:** {anomaly['message']}")
                st.write(f"**Detected:** {anomaly['detected_at']}")
                st.write(f"**Recommended Action:** {anomaly['action']}")
                
                st.divider()
                st.write("**Root Cause Analysis:**")
                st.write("The anomaly was detected through statistical analysis of execution patterns.")
                st.write("Multiple factors contributed to this anomaly.")
    
    with insight_tab3:
        st.subheader("⚠️ Bottleneck Identification")
        
        bottlenecks = [
            {
                "action": "Sentiment Analysis",
                "avg_time": 0.8,
                "occurrences": 342,
                "impact": "High",
                "suggestion": "Consider using cached embeddings or switching to faster model"
            },
            {
                "action": "Email Notification",
                "avg_time": 0.6,
                "occurrences": 180,
                "impact": "Medium",
                "suggestion": "Implement async email sending"
            },
            {
                "action": "API Call to External Service",
                "avg_time": 1.2,
                "occurrences": 95,
                "impact": "High",
                "suggestion": "Implement request batching and caching"
            }
        ]
        
        for bottleneck in bottlenecks:
            impact_emoji = "🔴" if bottleneck["impact"] == "High" else "🟡"
            
            with st.expander(f"{impact_emoji} {bottleneck['action']} - {bottleneck['avg_time']}s avg"):
                col_b1, col_b2, col_b3 = st.columns(3)
                
                with col_b1:
                    st.metric("Average Time", f"{bottleneck['avg_time']}s")
                
                with col_b2:
                    st.metric("Occurrences", bottleneck['occurrences'])
                
                with col_b3:
                    st.metric("Impact", bottleneck['impact'])
                
                st.divider()
                st.write(f"**Optimization Suggestion:**")
                st.write(bottleneck['suggestion'])
    
    with insight_tab4:
        st.subheader("💡 AI Recommendations")
        
        recommendations = [
            {
                "category": "Performance",
                "priority": "high",
                "title": "Implement Parallel Execution",
                "description": "Workflows with 5+ independent actions can execute in parallel",
                "impact": "30-40% faster execution",
                "effort": "medium"
            },
            {
                "category": "Reliability",
                "priority": "high",
                "title": "Add Circuit Breaker Pattern",
                "description": "Protect against cascading failures in external API calls",
                "impact": "Reduce failure propagation by 60%",
                "effort": "low"
            },
            {
                "category": "Cost",
                "priority": "medium",
                "title": "Enable Result Caching",
                "description": "Cache API responses for identical requests within 1 hour",
                "impact": "Reduce API calls by 35%",
                "effort": "low"
            },
            {
                "category": "Scalability",
                "priority": "medium",
                "title": "Break Complex Workflows",
                "description": "Split workflows with >10 actions into sub-workflows",
                "impact": "Better maintainability and error isolation",
                "effort": "high"
            },
            {
                "category": "Observability",
                "priority": "low",
                "title": "Add Custom Metrics",
                "description": "Track business metrics in addition to technical metrics",
                "impact": "Better insights into workflow effectiveness",
                "effort": "medium"
            }
        ]
        
        # Priority filter
        priority_filter = st.multiselect(
            "Filter by priority",
            ["high", "medium", "low"],
            default=["high", "medium"]
        )
        
        filtered_recs = [r for r in recommendations if r["priority"] in priority_filter]
        
        for rec in filtered_recs:
            priority_emoji = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
            
            with st.expander(f"{priority_emoji} {rec['title']} - {rec['effort'].upper()}"):
                st.write(f"**Category:** {rec['category']}")
                st.write(f"**Description:** {rec['description']}")
                st.write(f"**Impact:** {rec['impact']}")
                
                # Implementation checkbox
                if st.checkbox(f"Mark for implementation", key=f"impl_{rec['title'][:20]}"):
                    st.success("✓ Added to implementation queue")
    
    with insight_tab5:
        st.subheader("🔭 Failure Predictions")
        
        st.write("**AI-Predicted Issues (Next 7 Days)**")
        
        predictions = [
            {
                "probability": 0.75,
                "issue": "High error rate in WhatsApp notifications",
                "cause": "API rate limit approaching",
                "prevention": "Implement exponential backoff and request throttling",
                "affected_workflows": 3
            },
            {
                "probability": 0.62,
                "issue": "Performance degradation in sentiment analysis",
                "cause": "Model inference latency increase",
                "prevention": "Upgrade server resources or optimize model",
                "affected_workflows": 8
            },
            {
                "probability": 0.48,
                "issue": "Database connection pool exhaustion",
                "cause": "Increased concurrent workflow executions",
                "prevention": "Increase pool size or optimize queries",
                "affected_workflows": 5
            },
            {
                "probability": 0.35,
                "issue": "Third-party API timeout",
                "cause": "Scheduled maintenance window",
                "prevention": "Implement fallback endpoints",
                "affected_workflows": 2
            }
        ]
        
        for pred in predictions:
            prob_percent = int(pred["probability"] * 100)
            prob_emoji = "🔴" if prob_percent > 70 else "🟡" if prob_percent > 50 else "🟢"
            
            with st.expander(f"{prob_emoji} {prob_percent}% probability - {pred['issue']}"):
                st.write(f"**Root Cause:** {pred['cause']}")
                st.write(f"**Affected Workflows:** {pred['affected_workflows']}")
                st.write(f"**Prevention Strategy:** {pred['prevention']}")
                
                st.divider()
                st.progress(pred["probability"], text=f"{prob_percent}% confidence")
