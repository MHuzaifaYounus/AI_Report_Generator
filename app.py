import streamlit as st
import pandas as pd
import io
import os
import json
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

# --- CSS STYLING (DARK MODE COMPATIBLE & COMPACT) ---
st.markdown("""
<style>
    /* 1. MOVE EVERYTHING UP */
    .block-container {
        padding-top: 6rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* 2. HEADER TYPOGRAPHY (Theme Aware) */
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

    /* 3. TABS STYLING (Separated & Bordered) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px; /* Separation between tabs */
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        border-radius: 8px;
        padding-top: 8px;
        padding-bottom: 8px;
        padding-left: 20px;
        padding-right: 20px;
        border: 1px solid #475569; /* Add Border */
        background-color: rgba(255,255,255,0.02);
        transition: all 0.3s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        border-color: #4ade80;
        background-color: rgba(255,255,255,0.05);
    }
    .stTabs [aria-selected="true"] {
        border-color: #3b82f6 !important; /* Active Tab Highlight */
        background-color: rgba(59, 130, 246, 0.1) !important;
    }
    
    /* 4. OUTPUT BOX (Dark Mode Friendly & Spacious) */
    .insight-box {
        padding: 25px;
        border-radius: 8px;
        border: 1px solid #475569; /* Subtle border */
        border: 1px solid #475569; /* Subtle border */
        background-color: rgba(255, 255, 255, 0.03); /* Tiny bit of lightness */
        min-height: 450px; /* Adjusted height */
        margin-bottom: 15px;
        border-left: 5px solid #3b82f6; /* Default Blue for Trends */
        font-size: 1.1rem;
        line-height: 1.6;
    }
    .insight-anomalies {
        border-left: 5px solid #ef4444 !important; /* Red for Anomalies */
    }
    .insight-actions {
        border-left: 5px solid #22c55e !important; /* Green for Actions */
    }

    /* 5. BUTTONS (Compact & High Vis) */
    .stButton button {
        height: 50px;
        font-weight: 700;
        border-radius: 8px;
        border: 1px solid #475569;
        transition: all 0.2s;
    }
    .stButton button:hover {
        border-color: #4ade80;
        color: #4ade80;
    }

    /* 6. CONVERT RADIO TO TABS (Custom CSS) */
    div[role="radiogroup"] {
        display: flex;
        gap: 10px;
        width: 100%;
    }
    div[role="radiogroup"] > label {
        flex: 1; /* Make tabs equal width */
        background: rgba(255,255,255,0.03);
        padding: 12px 10px; /* Reduced side padding slightly */
        border-radius: 8px;
        border: 1px solid #475569;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
        display: flex; /* Critical for centering and justify-content */
        justify-content: center;
        align-items: center;
        font-weight: 600;
        white-space: nowrap; /* Prevent wrapping */
    }
    div[role="radiogroup"] > label:hover {
        border-color: #4ade80;
        background: rgba(255,255,255,0.05);
    }
    /* Highlight Selected Tab */
    div[role="radiogroup"] > label[data-checked="true"] {
        background: rgba(59, 130, 246, 0.15) !important;
        border-color: #3b82f6 !important;
        color: #ffff !important;
    }
    /* Hide the default radio circle safely */
    div[role="radiogroup"] label > div:first-child {
        width: 0px !important;
        height: 0px !important;
        opacity: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Ensure text is visible and centered */
    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] {
        color: #cbd5e1 !important; /* Light text */
        display: block;
    }
    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        margin: 0;
        font-weight: 600;
    }
    /* Active Tab Text Color */
    div[role="radiogroup"] > label[data-checked="true"] div[data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    
    /* Hide the default Streamlit footer/menu for cleanliness */
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
        # Compact Metrics
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
                get_cached_insight.clear()
            except Exception as e:
                st.error(f"Error: {e}")

# --- DASHBOARD LAYOUT ---

# 1. COMPACT HEADER
st.markdown('<div class="main-header">AI Workflow & Report Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Strategic Intelligence in <b>< 2 Seconds</b></div>', unsafe_allow_html=True)

if st.session_state['stats_dict']:
    # File Badge (Compact)
    st.caption(f"✅ Active File: **{uploaded_file.name}**")

    # 2. MIDDLE SECTION: CUSTOM TABS (Radio)
    # Using radio allows us to detect the "Click" and run logic *only* for the active tab
    selected_tab = st.radio(
        "Navigation", 
        ["📈 Trends Analyst", "🛡️ Anomaly Hunter", "♟️ The Strategist"], 
        horizontal=True, 
        label_visibility="collapsed"
    )
    
    # 3. CONTENT LOGIC (Triggered by selection)
    st.markdown("---") # Visual separator

    if selected_tab == "📈 Trends Analyst":
        # Check if we need to generate
        if not st.session_state['trend_result']:
             with st.spinner("🤖 Analyzing Trends..."):
                st.session_state['trend_result'] = get_cached_insight(st.session_state['stats_dict'], "Trends")
                st.rerun() # Rerun to show content
        
        # Show Content
        content = st.session_state['trend_result']
        st.markdown(f'<div class="insight-box">{content}</div>', unsafe_allow_html=True)

    elif selected_tab == "🛡️ Anomaly Hunter":
        # Check if we need to generate
        if not st.session_state['anomaly_result']:
             with st.spinner("🛡️ Hunting Anomalies..."):
                st.session_state['anomaly_result'] = get_cached_insight(st.session_state['stats_dict'], "Anomalies")
                st.rerun()
        
        # Show Content
        content = st.session_state['anomaly_result']
        st.markdown(f'<div class="insight-box insight-anomalies">{content}</div>', unsafe_allow_html=True)

    elif selected_tab == "♟️ The Strategist":
        # Check if we need to generate
        if not st.session_state['action_result']:
             with st.spinner("♟️ Generating Strategy..."):
                st.session_state['action_result'] = get_cached_insight(st.session_state['stats_dict'], "Actions")
                st.rerun()
        
        # Show Content
        content = st.session_state['action_result']
        st.markdown(f'<div class="insight-box insight-actions">{content}</div>', unsafe_allow_html=True)

else:
    # Empty State
    st.info("👈 Upload CSV to start.")