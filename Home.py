import streamlit as st
import json
import os
from pathlib import Path

st.set_page_config(
    page_title="DE/AI Learning Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d2ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .phase-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        border-left: 4px solid;
        margin-bottom: 0.8rem;
    }
    .xp-bar-outer {
        background: #2a2a3e;
        border-radius: 20px;
        height: 22px;
        width: 100%;
        margin-top: 6px;
    }
    .xp-bar-inner {
        background: linear-gradient(90deg, #00d2ff, #7b2ff7);
        border-radius: 20px;
        height: 22px;
        transition: width 0.4s ease;
    }
    .stat-box {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #2a2a3e;
    }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ── Progress State ────────────────────────────────────────────────────────────
PROGRESS_FILE = Path("data/progress.json")

def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {
        "xp": 0,
        "level": 1,
        "completed_modules": [],
        "badges": [],
        "streak": 0,
        "last_activity": None,
    }

def save_progress(data):
    PROGRESS_FILE.parent.mkdir(exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)

if "progress" not in st.session_state:
    st.session_state.progress = load_progress()

progress = st.session_state.progress

# ── XP / Level Logic ──────────────────────────────────────────────────────────
XP_PER_LEVEL = 500
level = max(1, progress["xp"] // XP_PER_LEVEL + 1)
xp_in_level = progress["xp"] % XP_PER_LEVEL
xp_pct = int((xp_in_level / XP_PER_LEVEL) * 100)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 👤 Your Profile")
    st.markdown(f"**Level {level} Engineer**")
    st.markdown(f"""
    <div class='xp-bar-outer'>
        <div class='xp-bar-inner' style='width:{xp_pct}%'></div>
    </div>
    <small>{xp_in_level} / {XP_PER_LEVEL} XP to Level {level+1}</small>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='stat-box'>🔥<br><b>{progress['streak']}</b><br><small>Day Streak</small></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-box'>✅<br><b>{len(progress['completed_modules'])}</b><br><small>Modules Done</small></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏅 Badges")
    if progress["badges"]:
        st.markdown(" ".join([f"`{b}`" for b in progress["badges"]]))
    else:
        st.markdown("<small>Complete modules to earn badges!</small>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🗺️ Navigation")
    st.page_link("Home.py", label="🏠 Home", icon=None)
    st.page_link("pages/1_Python_Foundations.py", label="🐍 Python Foundations")
    st.page_link("pages/2_Docker_Explorer.py", label="🐳 Docker Explorer")
    st.page_link("pages/3_SQL_Playground.py", label="🗄️ SQL Playground")
    st.page_link("pages/4_ETL_Pipeline_Builder.py", label="🔧 ETL Pipeline Builder")
    st.page_link("pages/5_Data_Modeling.py", label="📐 Data Modeling")
    st.page_link("pages/6_Quiz_Arena.py", label="⚔️ Quiz Arena")

# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown("<div class='main-title'>DE/AI Engineering Learning Hub 🚀</div>", unsafe_allow_html=True)
st.markdown("**Your 6-month journey from Data Engineer to AI Data Engineer — interactive, visual, project-based.**")
st.markdown("---")

# ── Roadmap ───────────────────────────────────────────────────────────────────
st.markdown("## 🗺️ Your Learning Roadmap")

PHASES = [
    {
        "phase": "Phase 1",
        "title": "Foundations Hardened",
        "weeks": "Weeks 1–3",
        "color": "#00d2ff",
        "topics": ["Production Python", "Docker", "Git Workflows", "Linux"],
        "modules": ["python_foundations", "docker_explorer"],
        "status": "active",
    },
    {
        "phase": "Phase 2",
        "title": "Data Engineering Core",
        "weeks": "Weeks 4–10",
        "color": "#7b2ff7",
        "topics": ["PostgreSQL Deep Dive", "Data Modeling", "ETL/ELT", "Airflow", "dbt", "Snowflake"],
        "modules": ["sql_playground", "etl_pipeline", "data_modeling"],
        "status": "locked",
    },
    {
        "phase": "Phase 3",
        "title": "Distributed Systems",
        "weeks": "Weeks 11–14",
        "color": "#ff6b6b",
        "topics": ["Kafka", "Spark", "Lakehouse", "Streaming Pipelines"],
        "modules": [],
        "status": "locked",
    },
    {
        "phase": "Phase 4",
        "title": "Cloud & Infrastructure",
        "weeks": "Weeks 15–17",
        "color": "#ffd93d",
        "topics": ["AWS Core", "Terraform", "CI/CD", "Kubernetes Basics"],
        "modules": [],
        "status": "locked",
    },
    {
        "phase": "Phase 5",
        "title": "AI Data Engineering",
        "weeks": "Weeks 18–24",
        "color": "#6bcb77",
        "topics": ["Embeddings", "RAG Pipelines", "Vector DBs", "LangChain", "AI Agents", "LLMOps"],
        "modules": [],
        "status": "locked",
    },
]

for phase in PHASES:
    completed = sum(1 for m in phase["modules"] if m in progress["completed_modules"])
    total = len(phase["modules"]) if phase["modules"] else "?"
    pct = int((completed / len(phase["modules"])) * 100) if phase["modules"] else 0

    lock = "🔓" if phase["status"] == "active" else "🔒"
    status_color = phase["color"] if phase["status"] == "active" else "#555"

    with st.container():
        st.markdown(f"""
        <div class='phase-card' style='border-color:{status_color}'>
            <div style='display:flex; justify-content:space-between; align-items:center'>
                <div>
                    <span style='color:{status_color}; font-weight:700'>{lock} {phase['phase']}: {phase['title']}</span>
                    <span style='color:#888; font-size:0.85rem; margin-left:10px'>{phase['weeks']}</span>
                </div>
                <span style='color:#aaa; font-size:0.85rem'>{completed}/{total} modules</span>
            </div>
            <div style='margin-top:6px'>
                {'  '.join([f"<span style='background:#2a2a3e; padding:2px 8px; border-radius:4px; font-size:0.78rem; margin-right:4px'>{t}</span>" for t in phase['topics']])}
            </div>
            <div class='xp-bar-outer' style='margin-top:8px; height:6px'>
                <div class='xp-bar-inner' style='width:{pct}%; background:{status_color}; height:6px'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Current Module ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 🎯 Start Here — Current Module")

col1, col2, col3 = st.columns(3)

with col1:
    completed = "python_foundations" in progress["completed_modules"]
    st.markdown(f"""
    <div style='background:#1e1e2e; border-radius:12px; padding:1.2rem; border:1px solid {"#00d2ff" if not completed else "#6bcb77"}'>
        <div style='font-size:1.5rem'>🐍</div>
        <div style='font-weight:700; margin-top:4px'>Python Foundations</div>
        <div style='color:#aaa; font-size:0.85rem; margin-top:4px'>Production patterns, config, logging, error handling</div>
        <div style='margin-top:8px'>
            <span style='background:{"#6bcb77" if completed else "#00d2ff"}22; color:{"#6bcb77" if completed else "#00d2ff"}; padding:3px 10px; border-radius:20px; font-size:0.78rem'>
                {"✅ Completed" if completed else "▶ In Progress"}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    completed = "docker_explorer" in progress["completed_modules"]
    st.markdown(f"""
    <div style='background:#1e1e2e; border-radius:12px; padding:1.2rem; border:1px solid {"#7b2ff7" if not completed else "#6bcb77"}'>
        <div style='font-size:1.5rem'>🐳</div>
        <div style='font-weight:700; margin-top:4px'>Docker Explorer</div>
        <div style='color:#aaa; font-size:0.85rem; margin-top:4px'>Visual container builder, layer explorer, compose simulator</div>
        <div style='margin-top:8px'>
            <span style='background:{"#6bcb77" if completed else "#7b2ff722"}; color:{"#6bcb77" if completed else "#7b2ff7"}; padding:3px 10px; border-radius:20px; font-size:0.78rem'>
                {"✅ Completed" if completed else "▶ Start Now"}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    completed = "sql_playground" in progress["completed_modules"]
    st.markdown(f"""
    <div style='background:#1e1e2e; border-radius:12px; padding:1.2rem; border:1px solid {"#ff6b6b" if not completed else "#6bcb77"}'>
        <div style='font-size:1.5rem'>🗄️</div>
        <div style='font-weight:700; margin-top:4px'>SQL Playground</div>
        <div style='color:#aaa; font-size:0.85rem; margin-top:4px'>Run real SQL, visualize query plans, learn window functions</div>
        <div style='margin-top:8px'>
            <span style='background:{"#6bcb77" if completed else "#ff6b6b22"}; color:{"#6bcb77" if completed else "#ff6b6b"}; padding:3px 10px; border-radius:20px; font-size:0.78rem'>
                {"✅ Completed" if completed else "🔒 Phase 2"}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Quick Stats ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 📈 Journey Stats")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total XP", f"{progress['xp']} XP", delta=None)
c2.metric("Current Level", f"Level {level}")
c3.metric("Modules Completed", len(progress["completed_modules"]))
c4.metric("Day Streak", f"{progress['streak']} 🔥")

st.markdown("---")
st.markdown("<center><small>Built with ❤️ as part of your DE/AI Engineering journey · Update daily to keep your streak</small></center>", unsafe_allow_html=True)
