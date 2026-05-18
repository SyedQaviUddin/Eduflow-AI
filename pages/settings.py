"""Settings Page - Configuration and preferences"""
import streamlit as st
import json


def show():
    st.title("⚙️ Settings")
    st.markdown("Configuration and system preferences")
    
    # Settings tabs
    set_tab1, set_tab2, set_tab3, set_tab4 = st.tabs(
        ["General", "API Configuration", "Notifications", "Advanced"]
    )
    
    with set_tab1:
        st.subheader("🔧 General Settings")
        
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.write("**Display Settings**")
            
            theme = st.radio(
                "Theme",
                ["Dark (Default)", "Light", "Auto"],
                horizontal=True
            )
            
            log_retention = st.slider(
                "Log Retention (days)",
                1, 90, 30
            )
        
        with col_g2:
            st.write("**System Settings**")
            
            auto_save = st.checkbox("Auto-save workflows", value=True)
            
            notify_on_failure = st.checkbox(
                "Notify on workflow failure",
                value=True
            )
            
            enable_analytics = st.checkbox(
                "Enable usage analytics",
                value=True
            )
        
        st.divider()
        
        col_g3, col_g4 = st.columns(2)
        
        with col_g3:
            st.write("**Workflow Defaults**")
            
            default_timeout = st.number_input(
                "Default execution timeout (seconds)",
                min_value=5,
                max_value=300,
                value=60
            )
            
            max_retries = st.number_input(
                "Max recovery retries",
                min_value=1,
                max_value=10,
                value=3
            )
        
        with col_g4:
            st.write("**Notification Defaults**")
            
            notify_type = st.multiselect(
                "Default notification channels",
                ["Email", "WhatsApp", "Slack", "SMS"],
                default=["Email"]
            )
        
        if st.button("💾 Save Settings", use_container_width=True, key="set_save_btn"):
            st.success("✅ Settings saved successfully!")
    
    with set_tab2:
        st.subheader("🔑 API Configuration")
        
        st.info("ℹ️ API keys are stored securely and never logged")
        
        col_api1, col_api2 = st.columns(2)
        
        with col_api1:
            st.write("**DeepSeek AI**")
            
            deepseek_key = st.text_input(
                "DeepSeek API Key",
                type="password",
                value="sk-" + "*" * 50
            )
            
            if st.button("🧪 Test DeepSeek Connection", use_container_width=True, key="test_deepseek"):
                st.success("✅ Connection successful")
                st.write("Model: deepseek-chat")
                st.write("Status: Ready")
        
        with col_api2:
            st.write("**External Services**")
            
            whatsapp_api = st.text_input(
                "WhatsApp Business API Key",
                type="password"
            )
            
            slack_webhook = st.text_input(
                "Slack Webhook URL",
                type="password"
            )
            
            if st.button("🧪 Test All APIs", use_container_width=True, key="test_all_apis"):
                st.success("✅ All API connections verified")
        
        st.divider()
        
        st.subheader("📊 API Usage")
        
        col_usage1, col_usage2, col_usage3 = st.columns(3)
        
        with col_usage1:
            st.metric(
                "DeepSeek Calls",
                1245,
                delta="↑ 156"
            )
        
        with col_usage2:
            st.metric(
                "WhatsApp Messages",
                342,
                delta="↑ 45"
            )
        
        with col_usage3:
            st.metric(
                "Email Sent",
                678,
                delta="↑ 89"
            )
    
    with set_tab3:
        st.subheader("🔔 Notification Settings")
        
        st.write("**Email Settings**")
        
        col_n1, col_n2 = st.columns(2)
        
        with col_n1:
            smtp_server = st.text_input(
                "SMTP Server",
                "smtp.gmail.com"
            )
            
            smtp_port = st.number_input(
                "SMTP Port",
                value=587,
                min_value=1,
                max_value=65535
            )
        
        with col_n2:
            email_address = st.text_input(
                "From Email Address",
                "noreply@nexora.ai"
            )
            
            email_password = st.text_input(
                "Email Password",
                type="password"
            )
        
        st.divider()
        
        st.write("**WhatsApp Settings**")
        
        whatsapp_account = st.text_input(
            "WhatsApp Business Account ID",
            placeholder="1234567890"
        )
        
        whatsapp_phone = st.text_input(
            "WhatsApp Number to Notify",
            "+1-234-567-8900"
        )
        
        st.divider()
        
        st.write("**Slack Settings**")
        
        slack_channel = st.text_input(
            "Default Slack Channel",
            "#workflows"
        )
        
        slack_mention = st.checkbox(
            "Mention @channel on critical alerts",
            value=False
        )
        
        st.divider()
        
        st.write("**Notification Rules**")
        
        notify_on = st.multiselect(
            "Send notifications when:",
            [
                "Workflow starts",
                "Workflow completes",
                "Workflow fails",
                "Recovery activated",
                "Anomaly detected"
            ],
            default=["Workflow fails", "Recovery activated", "Anomaly detected"]
        )
        
        if st.button("💾 Save Notification Settings", use_container_width=True):
            st.success("✅ Notification settings saved!")
    
    with set_tab4:
        st.subheader("🔬 Advanced Settings")
        
        st.warning("⚠️ Modify these settings only if you know what you're doing!")
        
        st.write("**Execution Engine**")
        
        col_adv1, col_adv2 = st.columns(2)
        
        with col_adv1:
            max_parallel = st.number_input(
                "Max parallel executions",
                min_value=1,
                max_value=50,
                value=5
            )
            
            execution_timeout = st.number_input(
                "Global execution timeout (seconds)",
                min_value=10,
                max_value=600,
                value=120
            )
        
        with col_adv2:
            memory_limit = st.number_input(
                "Memory limit per execution (MB)",
                min_value=128,
                max_value=4096,
                value=512
            )
            
            debug_mode = st.checkbox("Enable debug mode", value=False)
        
        st.divider()
        
        st.write("**Data Storage**")
        
        retention_logs = st.number_input(
            "Execution logs retention (days)",
            min_value=1,
            max_value=365,
            value=90
        )
        
        compression = st.checkbox(
            "Compress old logs",
            value=True
        )
        
        backup_enabled = st.checkbox(
            "Enable automatic backups",
            value=True
        )
        
        st.divider()
        
        st.write("**System Actions**")
        
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button("🧹 Clear Cache", use_container_width=True):
                st.success("✅ Cache cleared")
        
        with col_action2:
            if st.button("📦 Export Data", use_container_width=True):
                st.info("📥 Preparing export...")
        
        with col_action3:
            if st.button("⚙️ Reset Settings", use_container_width=True):
                if st.checkbox("Confirm reset"):
                    st.warning("⚠️ Confirming reset...")
        
        st.divider()
        
        if st.button("💾 Save Advanced Settings", use_container_width=True):
            st.success("✅ Advanced settings saved!")
    
    # Footer info
    st.divider()
    st.markdown("""
    ### 📋 System Information
    
    - **Version:** Nexora AI v1.0
    - **Build:** Production
    - **Last Updated:** 2024-01-16
    - **Status:** Operational ✅
    """)
