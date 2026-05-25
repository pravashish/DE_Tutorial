import streamlit as st
import pandas as pd
import json
import io
from pathlib import Path

st.set_page_config(page_title="ETL Pipeline Builder", page_icon="🔧", layout="wide")

st.markdown("""
<style>
    .etl-header { font-size:1.6rem; font-weight:800; color:#ff6b6b; }
    .stage-box { background:#1e1e2e; border-radius:10px; padding:1rem; border-top:3px solid; margin:0.4rem 0; }
    .lesson-card { background:#1e1e2e; border-radius:10px; padding:1.2rem; border-left:3px solid #ff6b6b; }
    .flow-arrow { text-align:center; font-size:1.5rem; color:#555; padding:2px 0; }
</style>
""", unsafe_allow_html=True)

PROGRESS_FILE = Path("data/progress.json")

def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"xp": 0, "level": 1, "completed_modules": [], "badges": [], "streak": 0}

def save_progress(data):
    PROGRESS_FILE.parent.mkdir(exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def award_xp(amount, reason):
    p = load_progress()
    p["xp"] += amount
    save_progress(p)
    st.balloons()
    st.success(f"🎉 +{amount} XP — {reason}")

# ── Sample dirty data ─────────────────────────────────────────────────────────
SAMPLE_DATA = pd.DataFrame({
    "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "name": ["  Alice Johnson  ", "BOB SMITH", "carol white", "Dave Brown", "", "Frank Miller", "  Grace", "Henry Moore", "Iris Taylor", "Jack Anderson"],
    "email": ["alice@example.com", "not-an-email", "carol@example.com", "dave@example.com", "eve@example.com", "", "grace@example.com", "henry@example.com", None, "jack@example.com"],
    "age": [28, 999, 29, -5, 31, 45, 27, 33, 29, 41],
    "salary": ["$75,000", "$82,500", "$68,000", "$91,000", "$55,000", "$110,000", "$72,000", "$88,000", "$65,000", "$95,000"],
    "join_date": ["2023-01-15", "2023-02-20", "not-a-date", "2023-04-05", "2023-05-12", "2023-06-18", "2023-07-22", "2023-08-30", "2023-09-14", "2023-10-01"],
    "department": ["Engineering", "Marketing", "Engineering", "Sales", "Engineering", "MANAGEMENT", "engineering", "Marketing", "Sales", None],
})

st.markdown("<div class='etl-header'>🔧 ETL Pipeline Builder</div>", unsafe_allow_html=True)
st.markdown("*Phase 2 · Week 3 · Build a real pipeline step by step · 300 XP available*")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📖 ETL Theory", "🎮 Interactive Pipeline", "💻 Generate Code", "⚔️ Challenge"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ETL Theory
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## What is ETL?")
    st.markdown("""
    <div class='lesson-card'>
    ETL = <b>Extract, Transform, Load</b>. The fundamental pattern of data engineering.
    Every data pipeline you build for the next decade will follow some version of this pattern.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────────────────┐
    │                        ETL PIPELINE                             │
    │                                                                 │
    │  ┌──────────┐     ┌───────────────┐     ┌──────────────────┐  │
    │  │ EXTRACT  │────▶│  TRANSFORM    │────▶│      LOAD        │  │
    │  │          │     │               │     │                  │  │
    │  │ Read raw │     │ • Clean       │     │ Write to:        │  │
    │  │ data from│     │ • Validate    │     │ • Data warehouse │  │
    │  │ sources: │     │ • Reshape     │     │ • Database       │  │
    │  │ • APIs   │     │ • Enrich      │     │ • Data lake      │  │
    │  │ • DBs    │     │ • Aggregate   │     │ • S3 / GCS       │  │
    │  │ • Files  │     │ • Standardize │     │ • Snowflake      │  │
    │  │ • Streams│     │               │     │ • BigQuery       │  │
    │  └──────────┘     └───────────────┘     └──────────────────┘  │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
    ```
    """)

    st.markdown("### ETL vs ELT — The Modern Shift")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Traditional ETL**
        ```
        Source → Transform → Load → Warehouse
        ```
        - Transform BEFORE loading
        - Transformations in Python/Java/Spark
        - Common with older warehouses
        - Good for: complex logic, reducing data volume
        """)
    with col2:
        st.markdown("""
        **Modern ELT** (dbt era)
        ```
        Source → Load → Transform → Warehouse
        ```
        - Load raw data FIRST
        - Transform IN the warehouse using SQL
        - Common with Snowflake, BigQuery, Redshift
        - Good for: flexibility, auditability, SQL teams
        """)

    st.markdown("""
    > **Industry trend:** Most modern data teams use ELT with dbt.
    > Raw data lands in S3/GCS, gets loaded to Snowflake, then dbt transforms it.
    > But you still need to know ETL — Kafka consumers, streaming pipelines,
    > and real-time systems still transform before loading.
    """)

    if st.button("Claim Theory XP ✨", key="xp_etl_theory"):
        award_xp(40, "ETL theory learned")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Interactive Pipeline
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 🎮 Build Your Pipeline Step by Step")
    st.markdown("You have dirty data. Apply transformations one at a time and see what changes.")

    if "pipeline_steps" not in st.session_state:
        st.session_state.pipeline_steps = []

    if "current_df" not in st.session_state:
        st.session_state.current_df = SAMPLE_DATA.copy()

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 🔧 Add a Transformation Step")

        step_type = st.selectbox("Choose step:", [
            "Remove rows with null email",
            "Remove rows with invalid age (< 0 or > 120)",
            "Strip whitespace from name column",
            "Normalize name to Title Case",
            "Normalize department to lowercase",
            "Clean salary (remove $ and commas, convert to float)",
            "Parse join_date to proper date format",
            "Validate email format (must contain @)",
            "Reset index",
        ])

        if st.button("➕ Apply Step", type="primary"):
            df = st.session_state.current_df.copy()
            before_rows = len(df)
            step_applied = True
            error = None

            try:
                if step_type == "Remove rows with null email":
                    df = df.dropna(subset=["email"])
                    df = df[df["email"] != ""]
                elif step_type == "Remove rows with invalid age (< 0 or > 120)":
                    df = df[(df["age"] >= 0) & (df["age"] <= 120)]
                elif step_type == "Strip whitespace from name column":
                    df["name"] = df["name"].str.strip()
                elif step_type == "Normalize name to Title Case":
                    df["name"] = df["name"].str.title()
                elif step_type == "Normalize department to lowercase":
                    df["department"] = df["department"].str.lower()
                elif step_type == "Clean salary (remove $ and commas, convert to float)":
                    df["salary"] = df["salary"].str.replace("[$,]", "", regex=True).astype(float)
                elif step_type == "Parse join_date to proper date format":
                    df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")
                    df = df.dropna(subset=["join_date"])
                elif step_type == "Validate email format (must contain @)":
                    df = df[df["email"].str.contains("@", na=False)]
                elif step_type == "Reset index":
                    df = df.reset_index(drop=True)

                after_rows = len(df)
                st.session_state.current_df = df
                st.session_state.pipeline_steps.append({
                    "step": step_type,
                    "rows_before": before_rows,
                    "rows_after": after_rows,
                    "dropped": before_rows - after_rows,
                })
            except Exception as e:
                st.error(f"❌ Step failed: {e}")

        if st.button("🔄 Reset to Original Data"):
            st.session_state.current_df = SAMPLE_DATA.copy()
            st.session_state.pipeline_steps = []
            st.rerun()

        st.markdown("### 📋 Pipeline Steps Applied")
        if st.session_state.pipeline_steps:
            for i, step in enumerate(st.session_state.pipeline_steps):
                dropped = step["dropped"]
                color = "#ff6b6b" if dropped > 0 else "#6bcb77"
                st.markdown(f"""
                <div style='background:#1e1e2e; border-radius:6px; padding:0.5rem 0.8rem; margin:3px 0; font-size:0.82rem'>
                    <span style='color:#888'>{i+1}.</span> {step['step'][:45]}<br>
                    <span style='color:{color}'>
                        {step['rows_before']} → {step['rows_after']} rows
                        {f"(-{dropped} dropped)" if dropped else " (no rows dropped)"}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<small style='color:#888'>No steps applied yet</small>", unsafe_allow_html=True)

    with col2:
        st.markdown("### 📊 Current Data State")
        df_display = st.session_state.current_df

        m1, m2, m3 = st.columns(3)
        m1.metric("Rows", len(df_display))
        m2.metric("Columns", len(df_display.columns))
        m3.metric("Null values", int(df_display.isnull().sum().sum()))

        st.dataframe(df_display, use_container_width=True, height=350)

        if len(st.session_state.pipeline_steps) >= 5:
            st.success("✅ You've built a real transformation pipeline!")
            if st.button("Claim XP for Pipeline ✨", key="xp_pipeline"):
                award_xp(80, "Built an ETL pipeline")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Generate Code
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 💻 Generate Production Python Code")
    st.markdown("Your pipeline steps → real Python code you can run.")

    steps_applied = st.session_state.get("pipeline_steps", [])

    if not steps_applied:
        st.info("Go to 'Interactive Pipeline' tab and apply some steps first. Then come back here to see the generated code.")
    else:
        code_lines = [
            "import pandas as pd",
            "import logging",
            "",
            "logger = logging.getLogger(__name__)",
            "",
            "",
            "def transform(df: pd.DataFrame) -> pd.DataFrame:",
            '    """Apply all transformation steps to the DataFrame."""',
            f"    logger.info('Starting transform with %d rows', len(df))",
            "    initial_rows = len(df)",
            "",
        ]

        step_map = {
            "Remove rows with null email": '    df = df.dropna(subset=["email"])\n    df = df[df["email"] != ""]',
            "Remove rows with invalid age (< 0 or > 120)": '    df = df[(df["age"] >= 0) & (df["age"] <= 120)]',
            "Strip whitespace from name column": '    df["name"] = df["name"].str.strip()',
            "Normalize name to Title Case": '    df["name"] = df["name"].str.title()',
            "Normalize department to lowercase": '    df["department"] = df["department"].str.lower()',
            "Clean salary (remove $ and commas, convert to float)": '    df["salary"] = df["salary"].str.replace("[$,]", "", regex=True).astype(float)',
            "Parse join_date to proper date format": '    df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")\n    df = df.dropna(subset=["join_date"])',
            "Validate email format (must contain @)": '    df = df[df["email"].str.contains("@", na=False)]',
            "Reset index": '    df = df.reset_index(drop=True)',
        }

        for step in steps_applied:
            name = step["step"]
            code_lines.append(f"    # {name}")
            if name in step_map:
                code_lines.append(step_map[name])
            code_lines.append(f'    logger.info("After step \'{name[:30]}\': %d rows", len(df))')
            code_lines.append("")

        code_lines.extend([
            "    dropped = initial_rows - len(df)",
            "    logger.info('Transform complete: %d rows (dropped %d)', len(df), dropped)",
            "    return df",
        ])

        full_code = "\n".join(code_lines)
        st.code(full_code, language="python")

        st.download_button(
            "⬇️ Download transform.py",
            data=full_code,
            file_name="transform.py",
            mime="text/plain",
        )

        st.markdown("""
        > **Notice what good generated code does:**
        > - Logs at each step with row counts
        > - Tracks total rows dropped
        > - Clear function signature with type hint
        > - Each step has a comment explaining what it does
        """)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Challenge
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## ⚔️ ETL Challenge: Debug the Pipeline")
    st.markdown("""
    <div style='background:#1a1a2e; border-radius:10px; padding:1.2rem; border:1px solid #ff6b6b'>
    <b>Scenario:</b> Your pipeline ran successfully (no errors), but the business team is complaining
    that the revenue report shows wrong numbers. You need to find the bug.<br><br>
    <b>⭐ 100 XP</b>
    </div>
    """, unsafe_allow_html=True)

    st.code("""
def calculate_monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    # Convert order_date to datetime
    df['order_date'] = pd.to_datetime(df['order_date'])

    # Extract month
    df['month'] = df['order_date'].dt.month

    # Calculate monthly revenue
    monthly = df.groupby('month')['amount'].sum().reset_index()
    monthly.columns = ['month', 'revenue']

    return monthly

# Input data sample:
# order_date    amount    status
# 2024-01-10    299.00    completed
# 2024-01-20    9.99      completed
# 2024-02-01    199.00    cancelled   ← notice this
# 2024-02-15    49.00     completed
    """, language="python")

    q1 = st.radio(
        "What's wrong with this pipeline?",
        [
            "A) pd.to_datetime will fail on some dates",
            "B) It includes ALL orders including cancelled ones, inflating revenue",
            "C) The groupby is incorrect",
            "D) .dt.month returns wrong values",
        ], index=None, key="etl_q1"
    )

    if q1 and "B)" in q1:
        st.success("✅ Correct! Missing `WHERE status = 'completed'` filter. The `cancelled` order worth $199 is being counted as revenue.")

        st.markdown("**Write the fix:**")
        fix = st.text_area("Fixed line:", placeholder="df = df[...]", height=60, key="etl_fix")
        if fix and "completed" in fix and "status" in fix:
            st.success("✅ Perfect fix! `df = df[df['status'] == 'completed']` before the groupby.")

    elif q1:
        st.error("❌ The code runs fine technically. The bug is a business logic error — look at what data is being included.")

    st.markdown("---")
    st.markdown("**Interview question:** What type of bug is this? What process would prevent it?")
    answer = st.text_area("Your answer:", height=80, key="etl_interview",
                          placeholder="This is a... The way to prevent it is...")

    if answer and len(answer) > 50:
        st.info("""
        **Model answer:** This is a **business logic bug** — the code is technically correct Python,
        but implements the wrong logic. Prevention strategies:
        1. **Data tests** — assert that `revenue` never includes cancelled orders
        2. **dbt tests** — test that source data matches expected distributions
        3. **Code review** — a domain expert reviews pipeline logic
        4. **Reconciliation** — compare pipeline output against known-good source numbers
        """)
        if st.button("Claim 100 XP ✨", key="xp_etl_challenge"):
            award_xp(100, "ETL debugging challenge completed")
