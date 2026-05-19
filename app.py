"""Nexora AI - Main Application Entry Point"""
import streamlit as st
import os
from pathlib import Path


st.markdown("""
<script>
    // Force Streamlit light theme
    const root = window.parent.document.documentElement;
    root.setAttribute('data-theme', 'light');

    // Remove dark mode classes
    document.body.classList.remove('dark');

    // Force white background
    document.body.style.backgroundColor = 'white';
</script>

<style>
    html, body, .stApp {
        background-color: white !important;
        color: black !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #f5f7fa !important;
    }

    * {
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

# st.markdown("""
# <script>
#     const html = window.parent.document.querySelector('html');
#     html.setAttribute('data-theme', 'light');
# </script>
# """, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Eduflow AI - Workflow Automation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
# st.markdown("""
# <style>

# /* Force Light Theme */
# html, body, [class*="css"]  {
#     background-color: #ffffff !important;
#     color: #000000 !important;
# }

# /* Main app background */
# .stApp {
#     background-color: #ffffff !important;
# }

# /* Sidebar */
# section[data-testid="stSidebar"] {
#     background-color: #f8f9fa !important;
# }

# /* Text visibility */
# h1, h2, h3, h4, h5, h6, p, span, div, label {
#     color: #ffffff !important;
# }

# </style>
# """, unsafe_allow_html=True)
# Custom CSS for clean white theme
# st.markdown("""
# <style>
#     :root {
#         --primary-color: #0f4b8a;
#         --secondary-color: #4a97d9;
#         --accent-color: #f9af3a;
#         --bg-light: #f7f9fc;
#         --card-bg: #ffffff;
#         --border-gray: #e1e5ed;
#         --text-dark: #1b2430;
#     }

#     body {
#         background-color: var(--bg-light);
#         color: var(--text-dark);
#     }

#     .main {
#         background-color: var(--bg-light);
#     }

#     .stSidebar {
#         background-color: #ffffff;
#         color: var(--text-dark);
#         border-right: 1px solid var(--border-gray);
#     }

#     .stButton > button {
#         background-color: var(--primary-color);
#         color: #ffffff;
#         border: 1px solid var(--primary-color);
#         font-weight: 600;
#         border-radius: 8px;
#     }

#     .stButton > button:hover {
#         background-color: #0c3a6a;
#         border-color: #0c3a6a;
#     }

#     h1, h2, h3, h4, h5 {
#         color: var(--text-dark);
#     }

#     .stTabs [data-baseweb="tab-list"] {
#         border-bottom: 1px solid var(--border-gray);
#     }

#     .stTabs [aria-selected="true"] {
#         color: var(--primary-color);
#         border-bottom: 3px solid var(--primary-color);
#     }

#     .card {
#         background: var(--card-bg);
#         border: 1px solid var(--border-gray);
#         border-radius: 16px;
#         padding: 18px;
#         box-shadow: 0 12px 30px rgba(43, 72, 112, 0.06);
#     }

#     .card--highlight {
#         border-color: var(--primary-color);
#     }
# </style>
# """, unsafe_allow_html=True)
st.markdown("""
<style>

:root {
    --primary-color: #0f4b8a;
    --secondary-color: #4a97d9;
    --accent-color: #f9af3a;
    --bg-light: #f7f9fc;
    --card-bg: #ffffff;
    --border-gray: #e1e5ed;
    --text-dark: #1b2430;
}

/* Main App */
body {
    # background-color: var(--bg-light);
    color: var(--text-dark);
    background-color: #2563EB;
}

.main {
    
    background-color: var(--bg-light);
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 2px solid var(--border-gray);
    width: 340px !important;
}

/* Sidebar Header */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--text-dark);
    font-weight: 700;
}

/* RADIO BUTTON LABELS */
div[role="radiogroup"] label {
    background: #ffffff;
    border: 1px solid var(--border-gray);
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 12px;
    transition: all 0.3s ease;
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #1b2430 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}

/* Hover Effect */
div[role="radiogroup"] label:hover {
    background: linear-gradient(90deg, #eef5ff, #f8fbff);
    border: 1px solid #4a97d9;
    transform: translateX(4px);
    box-shadow: 0 8px 20px rgba(74,151,217,0.15);
}

/* Selected Navigation */
div[role="radiogroup"] label[data-selected="true"] {
    background: linear-gradient(90deg, #0f4b8a, #4a97d9);
    color: white !important;
    border: none;
    box-shadow: 0 10px 25px rgba(15,75,138,0.35);
}

/* Radio circle hide */
div[role="radiogroup"] input[type="radio"] {
    display: none;
}

/* Buttons */
.stButton > button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    font-weight: 700;
    border-radius: 12px;
    padding: 12px 20px;
    transition: 0.3s;
}

.stButton > button:hover {
    background-color: #0c3a6a;
    transform: scale(1.02);
}

/* Cards */
.card {
    background: var(--card-bg);
    border: 1px solid var(--border-gray);
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 12px 30px rgba(43,72,112,0.08);
}

.card--highlight {
    border-color: var(--primary-color);
}

/* Metrics */
[data-testid="metric-container"] {
    background: white;
    border-radius: 16px;
    padding: 14px;
    border: 1px solid var(--border-gray);
    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}

.stTabs [data-baseweb="tab"] {
    font-size: 18px;
    font-weight: 600;
    border-radius: 10px;
    padding: 10px 18px;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #0f4b8a, #4a97d9);
    color: white;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>

/* Hide Streamlit default multipage sidebar navigation */
[data-testid="stSidebarNav"] {
    display: none;
}

/* Hide top app navigation */
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0rem;
}

</style>
""", unsafe_allow_html=True)


# Initialize session state
if "workflow_created" not in st.session_state:
    st.session_state.workflow_created = False
if "execution_result" not in st.session_state:
    st.session_state.execution_result = None
if "current_workflow" not in st.session_state:
    st.session_state.current_workflow = None
if "workflow_id" not in st.session_state:
    st.session_state.workflow_id = None

# Initialize monitoring manager in session state (persists across reruns)
if "monitoring_manager" not in st.session_state:
    from utils.monitoring import get_monitoring_manager
    st.session_state.monitoring_manager = get_monitoring_manager()

# Sidebar navigation
if "page" not in st.session_state:
    st.session_state.page = "📊 Dashboard"

st.sidebar.markdown("## 🤖 Eduflow AI")
st.sidebar.markdown("### Intelligent Workflow Automation")
st.sidebar.divider()

pages = {
    "📊 Dashboard": "pages/dashboard",
    "⚙️ Workflow Generator": "pages/workflow_generator",
    "🎨 Visualization": "pages/visualization",
    "📋 Execution Logs": "pages/execution_logs",
    "🎮 Controls": "pages/controls",
    "🔮 AI Insights": "pages/insights"
}

page = st.sidebar.radio("Navigation", list(pages.keys()), index=list(pages.keys()).index(st.session_state.page), key="sidebar_page", label_visibility="collapsed")
st.session_state.page = page

st.sidebar.divider()
st.sidebar.markdown("### 📈 Workflow Summary")
from utils.workflow_storage import WorkflowStorage
storage = WorkflowStorage()
workflows = storage.list_workflows()
st.sidebar.metric("Total Workflows", len(workflows))
st.sidebar.metric("Active Workflows", sum(1 for w in workflows if w.get("enabled")))
st.sidebar.metric("Saved Workflows", len(workflows))

# Load selected page
if page == "📊 Dashboard":
    import pages.dashboard as dashboard_page
    dashboard_page.show()
elif page == "⚙️ Workflow Generator":
    import pages.workflow_generator as gen_page
    gen_page.show()
elif page == "⚡ Live Monitoring":
    import pages.live_monitoring as live_page
    live_page.show()
elif page == "🎨 Visualization":
    import pages.visualization as viz_page
    viz_page.show()
elif page == "📋 Execution Logs":
    import pages.execution_logs as logs_page
    logs_page.show()
elif page == "🎮 Controls":
    import pages.controls as controls_page
    controls_page.show()
elif page == "🔮 AI Insights":
    import pages.insights as insights_page
    insights_page.show()
elif page == "⚙️ Settings":
    import pages.settings as settings_page
    settings_page.show()

# Footer
st.sidebar.divider()
st.sidebar.markdown("""
---
**Nexora AI v1.0**  
*Powered by DeepSeek & StreamLit*  
*Built for intelligent workflow automation*
""")
