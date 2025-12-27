import streamlit as st
import pandas as pd
import io
import os
import time
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# 2. Imports
from src.data_processor import process_csv
from src.agent_engine import get_ai_insight

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Decision Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TURBO MODE CACHING ---
@st.cache_data(show_spinner=False)
def get_cached_insight(stats, insight_type):
    return get_ai_insight(stats, insight_type)

# --- CSS STYLING (FIXED PADDING & LAYOUT) ---
st.markdown("""
<style>
    /* 1. MOVE EVERYTHING UP */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* 2. HEADER TYPOGRAPHY */
    .main-header {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0px;
        background: linear-gradient(90deg, #4ade80, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 15px;
    }

    /* 3. OUTPUT BOX (Dark Mode Friendly) */
    .insight-box {
        padding: 25px;
        border-radius: 8px;
        border: 1px solid #475569;
        background-color: rgba(255, 255, 255, 0.03); 
        min-height: 200px;
        margin-bottom: 15px;
        border-left: 5px solid #3b82f6;
        font-size: 1.1rem;
        line-height: 1.6;
        animation: fadeIn 0.5s ease-in-out;
    }
    .insight-anomalies {
        border-left: 5px solid #ef4444 !important;
    }
    .insight-actions {
        border-left: 5px solid #22c55e !important;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* 4. CUSTOM TABS (RADIO BUTTONS) - FIXED PADDING */
    div[role="radiogroup"] {
        display: flex;
        gap: 10px;
        width: 100%;
        margin-bottom: 15px;
    }
    div[role="radiogroup"] > label {
        flex: 1; 
        background: rgba(255,255,255,0.03);
        padding: 15px 10px;  /* Reduced side padding to 0, relies on Flex center */
        border-radius: 8px;
        border: 1px solid #475569;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
        display: flex; 
        justify-content: center;
        align-items: center;
        font-weight: 600;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        white-space: nowrap !important; /* <--- FIX: FORCE SINGLE LINE */
    }
    div[role="radiogroup"] > label:hover {
        border-color: #4ade80;
        background: rgba(255,255,255,0.05);
        transform: translateY(-2px);
    }
    /* Highlight Selected Tab */
    div[role="radiogroup"] > label[data-checked="true"] {
        background: rgba(59, 130, 246, 0.15) !important;
        border-color: #3b82f6 !important;
        color: #ffff !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
    }
    /* Hide radio circle */
    div[role="radiogroup"] label > div:first-child {
        display: none;
    }
    /* Text Styling */
    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        font-size: 1rem; /* Slightly smaller text to fit better */
        margin: 0;
        font-weight: 600;
    }

    /* Hide Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE SETUP ---
if 'stats_dict' not in st.session_state:
    st.session_state['stats_dict'] = None
if 'trend_result' not in st.session_state:
    st.session_state['trend_result'] = None
if 'anomaly_result' not in st.session_state:
    st.session_state['anomaly_result'] = None
if 'action_result' not in st.session_state:
    st.session_state['action_result'] = None

# --- SIDEBAR: DATA INSPECTOR ---
with st.sidebar:
    st.title("🎛️ Data Control")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    
    st.divider()
    
    if st.session_state['stats_dict']:
        stats = st.session_state['stats_dict']
        st.caption("DATA DNA")
        c1, c2 = st.columns(2)
        c1.metric("Rows", stats['overall_summary']['row_count'])
        c2.metric("Cols", stats['overall_summary']['column_count'])
        
        missing = sum(stats['overall_summary']['missing_values_summary'].values())
        st.metric("Missing Values", missing, delta="Clean" if missing==0 else "Issues", delta_color="inverse")
            
        with st.expander("🔍 Raw JSON"):
            st.json(stats)
            
        if st.button("🗑️ Reset", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    else:
        st.info("Upload a file to begin.")

# --- MAIN LOGIC ---
if uploaded_file is not None:
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state['stats_dict'] is None or file_id != st.session_state.get('uploaded_file_id'):
        with st.spinner("⚡ processing..."):
            try:
                st.session_state['stats_dict'] = process_csv(io.BytesIO(uploaded_file.getvalue()))
                st.session_state['uploaded_file_id'] = file_id 
                # Reset results
                st.session_state['trend_result'] = None
                st.session_state['anomaly_result'] = None
                st.session_state['action_result'] = None
                get_cached_insight.clear()
            except Exception as e:
                st.error(f"Error: {e}")

# --- DASHBOARD LAYOUT ---

# 1. HEADER
st.markdown('<div class="main-header">AI Workflow & Report Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Strategic Intelligence in <b>< 2 Seconds</b></div>', unsafe_allow_html=True)

if st.session_state['stats_dict']:
    # File Badge
    st.caption(f"✅ Active File: **{uploaded_file.name}**")

    # 2. MIDDLE SECTION: AGENT SELECTOR
    selected_tab = st.radio(
        "Select Agent:", 
        ["📈 Trends Analyst", "🛡️ Anomaly Hunter", "♟️ The Strategist"], 
        horizontal=True, 
        index=None, 
        label_visibility="collapsed"
    )
    
    st.markdown("---") 

    # 3. CONTENT LOGIC
    
    # State 1: Nothing Selected
    if selected_tab is None:
        st.markdown(
            """
            <div style="text-align: center; padding: 40px; opacity: 0.7; border: 2px dashed #475569; border-radius: 10px;">
                <h3>🤖 Multi-Agent Swarm Ready</h3>
                <p>Select an Agent above to activate intelligence.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # State 2: Trends Selected
    elif selected_tab == "📈 Trends Analyst":
        if not st.session_state['trend_result']:
             with st.spinner("📈 Analyst is identifying growth patterns..."):
                result = get_cached_insight(st.session_state['stats_dict'], "Trends")
                # Handle 429 Error Gracefully
                if "429" in result or "quota" in result.lower():
                    st.warning("⚠️ **Demo Quota Exceeded:** Please wait 60 seconds or restart the app.")
                else:
                    st.session_state['trend_result'] = result
                    st.rerun()
        
        if st.session_state['trend_result']:
            st.markdown(f'<div class="insight-box">{st.session_state["trend_result"]}</div>', unsafe_allow_html=True)

    # State 3: Anomalies Selected
    elif selected_tab == "🛡️ Anomaly Hunter":
        if not st.session_state['anomaly_result']:
             with st.spinner("🛡️ Hunter is scanning for z-score outliers..."):
                result = get_cached_insight(st.session_state['stats_dict'], "Anomalies")
                if "429" in result or "quota" in result.lower():
                    st.warning("⚠️ **Demo Quota Exceeded:** Please wait 60 seconds or restart the app.")
                else:
                    st.session_state['anomaly_result'] = result
                    st.rerun()
        
        if st.session_state['anomaly_result']:
            st.markdown(f'<div class="insight-box insight-anomalies">{st.session_state["anomaly_result"]}</div>', unsafe_allow_html=True)

    # State 4: Actions Selected
    elif selected_tab == "♟️ The Strategist":
        if not st.session_state['action_result']:
             with st.spinner("♟️ CEO is formulating strategy..."):
                result = get_cached_insight(st.session_state['stats_dict'], "Actions")
                if "429" in result or "quota" in result.lower():
                    st.warning("⚠️ **Demo Quota Exceeded:** Please wait 60 seconds or restart the app.")
                else:
                    st.session_state['action_result'] = result
                    st.rerun()
        
        if st.session_state['action_result']:
            st.markdown(f'<div class="insight-box insight-actions">{st.session_state["action_result"]}</div>', unsafe_allow_html=True)

else:
    # Empty State
    st.info("👈 Upload CSV to start.")