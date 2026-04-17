import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import sys
import os
from datetime import datetime

# Ensure backend imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agent import AutonomousAgent
from backend.data_generator import get_sensor_data, get_historical_data, get_all_machines

# ─────────────────────────────────────────────────────────────────────────────
# App Config & Premium UI Setup
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ecoSential AI-Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS Styling (Glassmorphism, Animations, Fonts)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Space+Grotesk:wght@500;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, .stMarkdown {
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* Background and global elements */
    .stApp {
        background: radial-gradient(circle at top left, #0f172a, #020617);
        color: #f8fafc;
    }

    /* Glassmorphism Metric Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 20px;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }

    /* Status Indicators with Glowing animations */
    @keyframes pulse-critical {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    @keyframes pulse-warning {
        0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(245, 158, 11, 0); }
        100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
    }
    @keyframes pulse-normal {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    .status-badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        letter-spacing: 1px;
        display: inline-block;
        font-size: 0.9em;
    }
    .status-CRITICAL {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid #ef4444;
        animation: pulse-critical 2s infinite;
    }
    .status-WARNING {
        background: rgba(245, 158, 11, 0.2);
        color: #fcd34d;
        border: 1px solid #f59e0b;
        animation: pulse-warning 2s infinite;
    }
    .status-NORMAL {
        background: rgba(16, 185, 129, 0.1);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.4);
        animation: pulse-normal 3s infinite;
    }

    /* Customizing Streamlit Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }

    /* Custom Action Buttons */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #0ea5e9, #3b82f6) !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────────────────────────────────

if 'agent' not in st.session_state:
    st.session_state.agent = AutonomousAgent()
if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_action' not in st.session_state:
    st.session_state.last_action = None

machines = get_all_machines()

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar / Navigation
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h1 style='background: -webkit-linear-gradient(45deg, #0ea5e9, #2dd4bf); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>ecoSential AI-Pro</h1>
            <p style='color: #94a3b8; font-size: 14px;'>Groq Powered Industrial Engine</p>
        </div>
    """, unsafe_allow_html=True)
    
    selected_machine = st.selectbox(
        "🎯 Target Machine",
        options=[m['id'] for m in machines],
        format_func=lambda x: f"{next(m['icon'] for m in machines if m['id'] == x)} {x} - {next(m['name'] for m in machines if m['id'] == x)}"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚡ Control Center")
    inject_anomaly = st.toggle("🔥 Simulate Critical Failure", value=False)
    auto_run = st.toggle("🔄 Auto-Run (Continuous)", value=False)
    
    col1, col2 = st.columns(2)
    with col1:
        step_clicked = st.button("▶ Trigger Cycle", use_container_width=True, type="primary")
    with col2:
        if st.button("🗑️ Reset Brain", use_container_width=True):
            st.session_state.agent = AutonomousAgent()
            st.session_state.history = []
            st.rerun()

    if step_clicked or auto_run:
        with st.spinner("🤖 Groq LLaMA-3 Reasoning..."):
            sensor_data = get_sensor_data(selected_machine, cycle_count=st.session_state.agent.total_cycles, inject_anomaly=inject_anomaly)
            result = st.session_state.agent.run_cycle(selected_machine, sensor_data)
            st.session_state.history.append(result)
            st.session_state.last_action = result

    st.markdown("<br><hr style='border-color: #334155;'>", unsafe_allow_html=True)
    st.markdown("### 🧠 Vector Memory DB")
    mem_stats = st.session_state.agent.memory.get_stats()
    st.metric("Stored Experiences", mem_stats["total_memories"])
    st.metric("RL Reward Average", f"{mem_stats['avg_reward']:.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# Main Dashboard UI
# ─────────────────────────────────────────────────────────────────────────────

latest = st.session_state.history[-1] if st.session_state.history else None

if not latest:
    st.markdown("""
        <div style='text-align: center; margin-top: 100px;'>
            <h2 style='color: #cbd5e1;'>System Idle</h2>
            <p style='color: #64748b; font-size: 18px;'>Select a machine and click <b>Trigger Cycle</b> in the sidebar to begin autonomous monitoring.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    # Top Overview Row
    data = latest["sensor_data"]
    status_str = data['status']
    
    col_hdr1, col_hdr2 = st.columns([2, 1])
    with col_hdr1:
        st.markdown(f"""
            <h2>Operating Status: {selected_machine}</h2>
            <div class='status-badge status-{status_str}'>{status_str}</div>
            <span style='color: #94a3b8; margin-left: 15px;'>Last Sync: {datetime.now().strftime('%H:%M:%S')}</span>
        """, unsafe_allow_html=True)
    with col_hdr2:
        # Mini AI insight bubble
        decision = latest["decision"]
        st.markdown(f"""
            <div class='glass-card' style='padding: 10px 15px; margin-bottom: 0;'>
                <span style='color:#38bdf8; font-weight:bold;'>🧠 Agent Risk Assesment:</span><br>
                <span style='font-size: 14px;'>{decision.get('risk_assessment', 'Evaluating...')}</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Telemetry Metric Cards Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.metric("Temperature", f"{data['temperature']:.1f} °C", delta=f"{data['temperature'] - 75:.1f}", delta_color="inverse")
        st.markdown("</div>", unsafe_allow_html=True)
    with m2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.metric("Vibration", f"{data['vibration']:.2f} mm/s", delta=f"{data['vibration'] - 2.5:.2f}", delta_color="inverse")
        st.markdown("</div>", unsafe_allow_html=True)
    with m3:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.metric("Power Draw", f"{data['energy_consumption']:.0f} kW")
        st.markdown("</div>", unsafe_allow_html=True)
    with m4:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.metric("Health Integrity", f"{data['health_score']:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Layout Tabs
    tab_dash, tab_agent, tab_mem, tab_chat = st.tabs([
        "📈 Telemetry & KPIs", 
        "🤖 Agent Reasoning", 
        "🧬 Memory Store",
        "💬 Ask AI Assistant"
    ])

    # ── TAB 1: TELEMETRY ──────────────────────────────────────────────────
    with tab_dash:
        col_c1, col_c2 = st.columns([3, 2])
        
        with col_c1:
            st.markdown("### Sensor Telemetry Trend")
            hist_df = get_historical_data(selected_machine)
            # Premium Plotly Chart
            fig = px.line(hist_df, x="timestamp", y=["temperature", "vibration"], template="plotly_dark")
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=0, r=0, t=30, b=0),
                hovermode="x unified"
            )
            # Add gradients to lines
            fig.data[0].line.color = "#0ea5e9"
            fig.data[1].line.color = "#f43f5e"
            st.plotly_chart(fig, use_container_width=True)
            
        with col_c2:
            st.markdown("### Efficiency Index")
            eng = latest.get("energy_report", {})
            fig2 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=eng.get("efficiency_index", 50),
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#2dd4bf"},
                    'bgcolor': "rgba(255,255,255,0.1)",
                    'steps': [
                        {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.3)"},
                        {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.3)"},
                        {'range': [70, 100], 'color': "rgba(16, 185, 129, 0.3)"}],
                }
            ))
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, margin=dict(l=20, r=20, t=20, b=20), height=300)
            st.plotly_chart(fig2, use_container_width=True)

    # ── TAB 2: AGENT REASONING ─────────────────────────────────────────────
    with tab_agent:
        st.markdown("### Explainable AI (XAI) Output")
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            st.markdown("""<div class='glass-card' style='height: 100%;'>
                <h4 style='color: #c084fc;'>1. LLM Chain of Thought</h4>
            """, unsafe_allow_html=True)
            st.write(decision.get("chain_of_thought", "N/A"))
            st.markdown(f"**Confidence:** <span style='color:#10b981;'>{decision.get('confidence', 0)*100}%</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_a2:
            st.markdown("""<div class='glass-card' style='height: 100%;'>
                <h4 style='color: #fb923c;'>2. Decision & Actions</h4>
            """, unsafe_allow_html=True)
            
            action_type = decision.get('action_type', 'monitor')
            icon = "🚨" if action_type == 'alert' else "🔧" if action_type == 'adjust_params' else "✅"
            color = "#ef4444" if action_type == 'alert' else "#f59e0b" if action_type == 'adjust_params' else "#10b981"
            
            st.markdown(f"**Primary Action:** <span style='color:{color}; font-size: 18px; font-weight: bold;'>{icon} {action_type.upper()}</span>", unsafe_allow_html=True)
            st.markdown(f"*{decision.get('explanation', '')}*")
            
            st.markdown("---")
            for res in latest["tool_results"]:
                if res.get("success"):
                    st.success(f"Tool `{res.get('tool')}`: {res.get('message')}")
                else:
                    st.error(f"Tool `{res.get('tool')}` Failed: {res.get('message')}")
            st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 3: MEMORY ──────────────────────────────────────────────────────
    with tab_mem:
        col_m1, col_m2 = st.columns([1, 2])
        
        with col_m1:
            reward = latest["reward"]
            r_color = "#10b981" if reward > 0 else "#ef4444"
            st.markdown(f"""<div class='glass-card' style='text-align: center;'>
                <h3 style='color: #94a3b8;'>Cycle Reward Score</h3>
                <h1 style='color: {r_color}; font-size: 4rem; margin: 0;'>{reward:+.1f}</h1>
                <p style='color: #cbd5e1; font-size: 14px;'>{latest['reward_rationale']}</p>
            </div>""", unsafe_allow_html=True)
            
            st.markdown("### 🧬 Insights")
            for insight in latest["learning_insights"]:
                st.info(insight)
                
        with col_m2:
            st.markdown("### 🗄️ FAISS Vector Replay")
            memories = st.session_state.agent.memory.long_term_meta
            if memories:
                df = pd.DataFrame(memories)
                disp_df = df[['timestamp', 'event_type', 'decision', 'reward']].copy()
                disp_df['timestamp'] = pd.to_datetime(disp_df['timestamp']).dt.strftime('%H:%M:%S')
                
                # Style the dataframe natively in Streamlit
                st.dataframe(
                    disp_df.sort_values(by='timestamp', ascending=False),
                    use_container_width=True,
                    height=300
                )
            else:
                st.write("Memory store is empty.")

    # ── TAB 4: CHAT INTERFACE ──────────────────────────────────────────────
    with tab_chat:
        st.markdown("### 💬 Chat with ecoSential AI-Pro")
        st.markdown("<p style='color: #94a3b8;'>Ask the agent to explain its decisions, summarize the factory health, or give maintenance advice based on its memory.</p>", unsafe_allow_html=True)
        
        user_q = st.text_input("Enter your question here...", placeholder="e.g., Why did you lower the power on M-101 earlier?")
        
        if st.button("Send Message", type="primary"):
            if user_q:
                with st.spinner("🤖 Groq LLaMA-3 is typing..."):
                    reply = st.session_state.agent.chat(user_q, selected_machine)
                    st.markdown(f"""
                        <div class='glass-card' style='border-left: 4px solid #10b981; margin-top: 15px;'>
                            <strong style='color: #38bdf8;'>ecoSential AI:</strong><br>
                            <span style='font-size: 16px;'>{reply}</span>
                        </div>
                    """, unsafe_allow_html=True)

# ── HANDLE AUTO RUN ────────────────────────────────────────────────────
if auto_run:
    time.sleep(3)
    st.rerun()
