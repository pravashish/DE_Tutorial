import streamlit as st
import json
import ast
import traceback
from pathlib import Path

st.set_page_config(page_title="Python Foundations", page_icon="🐍", layout="wide")

# ── Shared styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .concept-header { font-size:1.6rem; font-weight:800; color:#00d2ff; }
    .lesson-card { background:#1e1e2e; border-radius:10px; padding:1.2rem; border-left:3px solid #00d2ff; margin:0.5rem 0; }
    .good-code { background:#0d2818; border-radius:8px; padding:1rem; border-left:3px solid #6bcb77; }
    .bad-code  { background:#2d0f0f; border-radius:8px; padding:1rem; border-left:3px solid #ff6b6b; }
    .challenge-box { background:#1a1a2e; border-radius:10px; padding:1.2rem; border:1px solid #7b2ff7; }
    .xp-reward { background:#7b2ff722; color:#c084fc; padding:4px 12px; border-radius:20px; font-size:0.82rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Progress helpers ──────────────────────────────────────────────────────────
PROGRESS_FILE = Path("data/progress.json")

def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"xp": 0, "level": 1, "completed_modules": [], "badges": [], "streak": 0, "last_activity": None}

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

if "progress" not in st.session_state:
    st.session_state.progress = load_progress()

# ── Lesson state ──────────────────────────────────────────────────────────────
if "py_lesson" not in st.session_state:
    st.session_state.py_lesson = 0

LESSONS = [
    "Why Production Python?",
    "Project Structure",
    "Configuration Management",
    "Logging",
    "Error Handling",
    "Type Hints",
    "Challenge: Fix the Code",
    "Challenge: Build a Config",
]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("<div class='concept-header'>🐍 Python Foundations</div>", unsafe_allow_html=True)
st.markdown("*Phase 1 · Week 1 · ~2 hours · 300 XP available*")
st.markdown("---")

# ── Lesson selector ───────────────────────────────────────────────────────────
cols = st.columns(len(LESSONS))
for i, (col, name) in enumerate(zip(cols, LESSONS)):
    with col:
        active = i == st.session_state.py_lesson
        done = i < st.session_state.py_lesson
        color = "#00d2ff" if active else ("#6bcb77" if done else "#555")
        label = f"{'✅' if done else ('▶' if active else '○')} {i+1}"
        if st.button(label, key=f"lesson_{i}", use_container_width=True,
                     type="primary" if active else "secondary"):
            st.session_state.py_lesson = i
            st.rerun()

st.markdown("---")
lesson = st.session_state.py_lesson

# ══════════════════════════════════════════════════════════════════════════════
# LESSON 0 — Why Production Python?
# ══════════════════════════════════════════════════════════════════════════════
if lesson == 0:
    st.markdown("## Lesson 1: Why Production Python?")
    st.markdown("""
    <div class='lesson-card'>
    Most developers write code for themselves. <b>Production engineers write code for systems.</b><br><br>
    The difference: your code will run <b>unattended</b>, at <b>3am</b>, handling <b>millions of records</b>,
    modified by <b>people you've never met</b>. That changes everything about how you write it.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### The 6 Properties of Production Code")

    props = [
        ("🤖", "Unattended", "Runs without a human watching. Must handle failures by itself."),
        ("💥", "Fail Loudly", "Crashes with a clear error rather than silently producing wrong output."),
        ("👥", "Readable", "Your teammates will modify this at 2am. Make it obvious."),
        ("🧪", "Testable", "Every function can be tested in isolation."),
        ("⚙️", "Configurable", "No hardcoded values. Everything via environment variables."),
        ("👁️", "Observable", "Structured logs that tell you exactly what happened and when."),
    ]

    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(props):
        with cols[i % 3]:
            st.markdown(f"""
            <div style='background:#1e1e2e; border-radius:10px; padding:1rem; margin-bottom:0.8rem; text-align:center'>
                <div style='font-size:1.8rem'>{icon}</div>
                <div style='font-weight:700; color:#00d2ff; margin:4px 0'>{title}</div>
                <div style='color:#aaa; font-size:0.85rem'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### Quick Check: Spot the Problem")
    st.markdown("Look at this code. What's wrong with it?")

    st.code("""
def process_payment(amount):
    try:
        result = charge_card("4532015112830366", amount)
        print("Payment done!")
        return result
    except:
        return False
    """, language="python")

    answer = st.radio("What are the problems?", [
        "A) Nothing, it looks fine",
        "B) Hardcoded credit card number + bare except hides errors + print instead of logging",
        "C) The function name is wrong",
        "D) It should use async/await",
    ], index=None)

    if answer:
        if "B)" in answer:
            st.success("✅ Correct! Three problems: (1) hardcoded sensitive data, (2) bare `except:` swallows all errors silently, (3) `print` gives you no timestamp, no log level, no context.")
            if st.button("Award XP for this lesson ✨"):
                award_xp(30, "Spotted production code problems")
        else:
            st.error("Not quite. Look carefully at the credit card number, the except clause, and the print statement.")

    st.markdown("---")
    col1, col2 = st.columns([6,1])
    with col2:
        if st.button("Next Lesson →", type="primary"):
            st.session_state.py_lesson = 1
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# LESSON 1 — Project Structure
# ══════════════════════════════════════════════════════════════════════════════
elif lesson == 1:
    st.markdown("## Lesson 2: Project Structure")

    st.markdown("""
    <div class='lesson-card'>
    A production Python project is not a single file. It's a <b>package</b> — a structured collection
    of modules with clear responsibilities. Getting this right from the start saves weeks of pain later.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ❌ How beginners structure projects")
        st.code("""
my_project/
├── script.py          # everything in one file
├── script2.py         # overflow goes here
├── script_final.py    # "final" version
├── script_FINAL2.py   # actual final
└── test.py            # tests? maybe
        """)
        st.markdown("""
        <div class='bad-code'>
        Problems:<br>
        • No separation of concerns<br>
        • Can't test individual pieces<br>
        • Impossible to reuse code<br>
        • No one knows what's "current"
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### ✅ Production structure")
        st.code("""
my_pipeline/
├── src/
│   └── my_pipeline/
│       ├── __init__.py
│       ├── config.py      ← all settings
│       ├── extract.py     ← data extraction
│       ├── transform.py   ← data cleaning
│       ├── load.py        ← data loading
│       └── utils.py       ← shared helpers
├── tests/
│   └── test_transform.py
├── .env                   ← secrets (never commit)
├── .env.example           ← template (commit this)
├── requirements.txt
├── Dockerfile
└── README.md
        """)
        st.markdown("""
        <div class='good-code'>
        Benefits:<br>
        • Each file has ONE job<br>
        • Easy to find anything<br>
        • Tests mirror source structure<br>
        • Anyone can onboard instantly
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🗺️ Architecture Flow")
    st.markdown("""
    ```
    [Raw Data Source]
          │
          ▼
    extract.py  ──── reads raw data, returns DataFrame
          │
          ▼
    transform.py ─── cleans, validates, reshapes data
          │
          ▼
    load.py ───────── writes to database/warehouse
          │
          ▼
    [Destination: PostgreSQL / Snowflake / S3]

    config.py ──── feeds settings into ALL of the above
    utils.py  ──── shared helpers used by ALL of the above
    ```
    """)

    st.markdown("### Interactive: Match the File to Its Job")
    q = {
        "Where do database credentials live?": ("config.py", ["extract.py", "config.py", "load.py", "__init__.py"]),
        "Where does the logic to remove null rows live?": ("transform.py", ["extract.py", "transform.py", "load.py", "utils.py"]),
        "Where does the code to read a CSV file live?": ("extract.py", ["extract.py", "transform.py", "config.py", "load.py"]),
    }
    all_correct = True
    for question, (correct, options) in q.items():
        ans = st.selectbox(question, options, index=None, key=question)
        if ans is not None:
            if ans == correct:
                st.success(f"✅ Correct — `{correct}` is the right place")
            else:
                st.error(f"❌ Not quite. This belongs in `{correct}`")
                all_correct = False

    if all_correct and st.button("Claim XP for this lesson ✨"):
        award_xp(30, "Mastered project structure")

    st.markdown("---")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.py_lesson = 0
            st.rerun()
    with col2:
        if st.button("Next Lesson →", type="primary"):
            st.session_state.py_lesson = 2
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# LESSON 2 — Configuration Management
# ══════════════════════════════════════════════════════════════════════════════
elif lesson == 2:
    st.markdown("## Lesson 3: Configuration Management")

    st.markdown("""
    <div class='lesson-card'>
    <b>Rule #1 of production engineering:</b> Never hardcode anything that changes between environments.
    Passwords, hostnames, ports, feature flags — all go in environment variables.
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["❌ The Problem", "✅ The Solution", "🧪 Try It"])

    with tab1:
        st.markdown("### Why hardcoding kills you")
        st.code("""
# This is in your git repo. Forever. Even if you delete it later.
# Anyone with repo access has your production password.
# You need a different file for dev vs staging vs prod.

DB_URL = "postgresql://admin:SuperSecret123@prod-db.company.com/users"
API_KEY = "sk-abc123def456..."
SLACK_WEBHOOK = "https://hooks.slack.com/services/T00/B00/xxx"

def run():
    conn = connect(DB_URL)
    ...
        """, language="python")

        st.markdown("""
        <div class='bad-code'>
        <b>Real incidents caused by this pattern:</b><br>
        • Uber (2016): AWS keys hardcoded → exposed on GitHub → $100k AWS bill in 2 days<br>
        • Twitch (2021): credentials in codebase → source code leaked<br>
        • Happens at companies every week — this is not theoretical
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### The right pattern")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**`.env` file (never commit)**")
            st.code("""
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=admin
DB_PASSWORD=secret
API_KEY=sk-abc123
            """)
            st.markdown("**`.env.example` (commit this)**")
            st.code("""
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
API_KEY=
            """)
        with col2:
            st.markdown("**`config.py`**")
            st.code("""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DBConfig:
    host: str
    port: int
    name: str
    user: str
    password: str

    @property
    def url(self):
        return (
            f"postgresql://{self.user}:"
            f"{self.password}@"
            f"{self.host}:{self.port}/"
            f"{self.name}"
        )

def load_config():
    return DBConfig(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        name=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
            """, language="python")

        st.markdown("""
        <div class='good-code'>
        <b>Notice:</b> We use <code>os.environ["KEY"]</code> not <code>os.environ.get("KEY")</code> for required vars.
        If DB_HOST is missing, the app <b>crashes at startup</b> with a clear error —
        not 10 minutes later with a confusing connection error.
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### Simulate a config loader")
        st.markdown("Set these 'environment variables' and see what the config produces:")

        c1, c2 = st.columns(2)
        with c1:
            db_host = st.text_input("DB_HOST", "localhost")
            db_port = st.text_input("DB_PORT", "5432")
            db_name = st.text_input("DB_NAME", "mydb")
        with c2:
            db_user = st.text_input("DB_USER", "admin")
            db_pass = st.text_input("DB_PASSWORD", type="password")
            app_env = st.selectbox("APP_ENV", ["development", "staging", "production"])

        if st.button("Build Config Object"):
            if not db_host or not db_port or not db_name or not db_user:
                st.error("❌ Missing required environment variables! App would crash at startup.")
            else:
                try:
                    port = int(db_port)
                    url = f"postgresql://{db_user}:{'*' * len(db_pass)}@{db_host}:{port}/{db_name}"
                    st.success("✅ Config loaded successfully!")
                    st.json({
                        "env": app_env,
                        "db": {
                            "host": db_host,
                            "port": port,
                            "name": db_name,
                            "user": db_user,
                            "password": "***hidden***",
                            "url": url,
                        }
                    })
                    st.info("💡 Password is never logged or displayed in production. Only the URL structure is shown.")
                except ValueError:
                    st.error("❌ DB_PORT must be an integer. App would crash at startup.")

        if st.button("Claim XP ✨", key="xp_config"):
            award_xp(50, "Configuration management mastered")

    st.markdown("---")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.py_lesson = 1
            st.rerun()
    with col2:
        if st.button("Next Lesson →", type="primary"):
            st.session_state.py_lesson = 3
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# LESSON 3 — Logging
# ══════════════════════════════════════════════════════════════════════════════
elif lesson == 3:
    st.markdown("## Lesson 4: Structured Logging")

    st.markdown("""
    <div class='lesson-card'>
    <code>print()</code> is for scripts. <b>Logging</b> is for systems. In production, logs are your only
    window into what happened. Every log line should answer: <i>What happened? When? How bad is it?</i>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ❌ Using print()")
        st.code("""
print("Starting...")
print("Got 500 rows")
print("ERROR: failed")
print("Done")
        """, language="python")
        st.markdown("""
        <div class='bad-code'>
        Problems:<br>
        • No timestamps<br>
        • No severity levels<br>
        • No context (which module?)<br>
        • Can't filter by severity<br>
        • Can't route to log systems
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### ✅ Using logging")
        st.code("""
import logging
logger = logging.getLogger(__name__)

logger.info("Pipeline started")
logger.info("Extracted %d rows", 500)
logger.error("Load failed: %s", err, exc_info=True)
logger.info("Pipeline completed in %.2fs", elapsed)
        """, language="python")
        st.markdown("""
        <div class='good-code'>
        Benefits:<br>
        • Automatic timestamps<br>
        • Levels: DEBUG INFO WARNING ERROR<br>
        • Module name from __name__<br>
        • exc_info=True adds stack trace<br>
        • Routes to Datadog, CloudWatch
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Log Level Guide")
    levels = [
        ("DEBUG",   "#888",    "Detailed diagnostics — only in development"),
        ("INFO",    "#00d2ff", "Normal operations — pipeline started, rows processed"),
        ("WARNING", "#ffd93d", "Unexpected but handled — retry attempt, missing optional field"),
        ("ERROR",   "#ff6b6b", "Failure that needs attention — connection failed, data invalid"),
        ("CRITICAL","#ff0000", "System is down — database unreachable, disk full"),
    ]
    for level_name, color, desc in levels:
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:12px; padding:6px 0; border-bottom:1px solid #2a2a3e'>
            <span style='background:{color}22; color:{color}; padding:3px 12px; border-radius:4px;
                         font-family:monospace; font-weight:700; min-width:80px; text-align:center'>{level_name}</span>
            <span style='color:#ccc'>{desc}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🎮 Log Line Builder")
    st.markdown("Build a real log line:")

    lc1, lc2, lc3 = st.columns(3)
    with lc1:
        log_level = st.selectbox("Level", ["DEBUG", "INFO", "WARNING", "ERROR"])
    with lc2:
        module = st.text_input("Module name", "pipeline.extract")
    with lc3:
        message = st.text_input("Message", "Extracted 1000 rows from users table")

    if st.button("Generate Log Line"):
        import datetime
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        colors = {"DEBUG": "#888", "INFO": "#00d2ff", "WARNING": "#ffd93d", "ERROR": "#ff6b6b"}
        color = colors[log_level]
        st.markdown(f"""
        <div style='background:#0d0d1a; border-radius:8px; padding:1rem; font-family:monospace; font-size:0.9rem'>
            <span style='color:#888'>{ts}</span>
            <span style='color:{color}; font-weight:700'> | {log_level:<8}</span>
            <span style='color:#c084fc'> | {module}</span>
            <span style='color:#e2e2e2'> | {message}</span>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Claim XP ✨", key="xp_log"):
        award_xp(40, "Logging patterns learned")

    st.markdown("---")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.py_lesson = 2
            st.rerun()
    with col2:
        if st.button("Next Lesson →", type="primary"):
            st.session_state.py_lesson = 4
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# LESSON 4 — Error Handling
# ══════════════════════════════════════════════════════════════════════════════
elif lesson == 4:
    st.markdown("## Lesson 5: Error Handling")

    st.markdown("""
    <div class='lesson-card'>
    <b>Golden rule:</b> Fail loudly and specifically. A system that silently produces wrong results
    is infinitely more dangerous than one that crashes with a clear error message.
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["The Patterns", "Error Hierarchy", "🎮 Debug Simulator"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ❌ Common mistakes")
            st.code("""
# Mistake 1: Bare except
try:
    result = process(data)
except:           # catches EVERYTHING
    return None   # silent failure

# Mistake 2: Too broad
try:
    result = process(data)
except Exception:
    print("something went wrong")
    # no context, no re-raise

# Mistake 3: Swallowing errors
def get_user(id):
    try:
        return db.find(id)
    except:
        return {}  # caller thinks it worked!
            """, language="python")

        with col2:
            st.markdown("### ✅ Production patterns")
            st.code("""
# Pattern 1: Custom exceptions
class ExtractionError(Exception):
    pass

class ValidationError(Exception):
    pass

# Pattern 2: Specific catching
def extract(url: str) -> dict:
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.Timeout:
        raise ExtractionError(
            f"Timeout after 30s: {url}"
        )
    except requests.HTTPError as e:
        raise ExtractionError(
            f"HTTP {e.response.status_code}: {url}"
        )

# Pattern 3: Let it propagate
# If you can't handle it, don't catch it
# The caller should decide what to do
            """, language="python")

    with tab2:
        st.markdown("### Exception Hierarchy in Data Pipelines")
        st.code("""
PipelineError (base)
├── ExtractionError
│   ├── SourceUnavailableError    (API/DB is down)
│   ├── AuthenticationError       (bad credentials)
│   └── RateLimitError            (too many requests)
├── TransformationError
│   ├── SchemaValidationError     (wrong columns/types)
│   ├── DataQualityError          (nulls, duplicates)
│   └── EncodingError             (bad characters)
└── LoadError
    ├── ConnectionError           (can't reach destination)
    ├── DuplicateKeyError         (row already exists)
    └── PermissionError           (no write access)
        """)
        st.markdown("""
        <div class='good-code'>
        Why this matters: when your pipeline fails at 3am, the on-call engineer sees
        <code>SchemaValidationError: column 'user_id' missing from source</code> and knows
        exactly what to check. Not just "something went wrong."
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### Debug Simulator")
        st.markdown("Here are broken functions. Fix them:")

        st.markdown("**Bug #1: What happens when `age` is `'N/A'`?**")
        st.code("""
def parse_user(row: dict) -> dict:
    return {
        "id": row["id"],
        "name": row["name"].strip(),
        "age": int(row["age"]),   # ← problem here
        "email": row["email"].lower(),
    }

# Input: {"id": 1, "name": "Alice", "age": "N/A", "email": "alice@x.com"}
        """, language="python")

        fix1 = st.text_area("Write a fixed version of the age line:", height=80,
                            placeholder='e.g.  "age": int(row["age"]) if row["age"].isdigit() else None,')
        if fix1 and ("None" in fix1 or "try" in fix1 or "isdigit" in fix1 or "except" in fix1):
            st.success("✅ Good approach! Handle the bad value, don't let it crash the whole pipeline.")
        elif fix1:
            st.warning("Think about what happens when `int()` gets a non-numeric string. How can you catch or avoid that?")

        st.markdown("**Bug #2: What's wrong with this retry logic?**")
        st.code("""
def fetch_with_retry(url):
    for i in range(3):
        try:
            return requests.get(url).json()
        except:
            pass
    return None   # ← what's wrong here?
        """, language="python")

        fix2 = st.radio("What should happen after 3 failed attempts?", [
            "A) Return None — let the caller handle it",
            "B) Raise an exception — the caller needs to know it failed",
            "C) Return an empty dict",
            "D) Print an error and return None",
        ], index=None, key="fix2")

        if fix2:
            if "B)" in fix2:
                st.success("✅ Correct! Raise `ExtractionError('Failed after 3 attempts: {url}')`. Never silently return None from a function that should return data.")
            else:
                st.error("❌ Returning None or an empty dict hides the failure. The caller will try to process empty data and you'll get confusing bugs downstream.")

        if st.button("Claim XP ✨", key="xp_errors"):
            award_xp(50, "Error handling patterns mastered")

    st.markdown("---")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.py_lesson = 3
            st.rerun()
    with col2:
        if st.button("Next Lesson →", type="primary"):
            st.session_state.py_lesson = 5
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# LESSON 5 — Type Hints
# ══════════════════════════════════════════════════════════════════════════════
elif lesson == 5:
    st.markdown("## Lesson 6: Type Hints")
    st.markdown("""
    <div class='lesson-card'>
    Type hints are <b>documentation that the computer can check</b>. They make your code
    self-explanatory and let tools like mypy catch bugs before you run anything.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Without type hints")
        st.code("""
# What does this accept? What does it return?
# What's records? What's config?
# You have to read the whole function to know.

def process(records, config, batch_size=100):
    results = []
    for batch in chunk(records, batch_size):
        results.extend(transform(batch, config))
    return results
        """, language="python")

    with col2:
        st.markdown("### With type hints")
        st.code("""
from typing import List, Dict, Optional
from datetime import datetime
from .config import AppConfig

def process_records(
    records: List[Dict[str, any]],
    config: AppConfig,
    batch_size: int = 100,
    since: Optional[datetime] = None,
) -> List[Dict[str, any]]:
    # Crystal clear: List of dicts in, list of dicts out
    # AppConfig tells you exactly what config looks like
    # since is optional (can be None)
    ...
        """, language="python")

    st.markdown("### Type Hint Cheat Sheet")
    hints = [
        ("str", "A string", '"hello"'),
        ("int", "An integer", "42"),
        ("float", "A float", "3.14"),
        ("bool", "True or False", "True"),
        ("List[str]", "A list of strings", '["a", "b", "c"]'),
        ("Dict[str, int]", "Dict mapping strings to ints", '{"age": 25}'),
        ("Optional[str]", "A string or None", '"hello" or None'),
        ("Tuple[str, int]", "Fixed-length tuple", '("alice", 25)'),
        ("Union[str, int]", "Either a string or int", '"hello" or 42'),
    ]
    col1, col2, col3 = st.columns(3)
    for i, (hint, desc, example) in enumerate(hints):
        with [col1, col2, col3][i % 3]:
            st.markdown(f"""
            <div style='background:#1e1e2e; border-radius:8px; padding:0.7rem; margin-bottom:0.5rem'>
                <code style='color:#c084fc'>{hint}</code><br>
                <small style='color:#aaa'>{desc}</small><br>
                <small style='color:#6bcb77'>{example}</small>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 🎮 Add Type Hints")
    st.markdown("Add type hints to this function signature:")
    st.code("""
# Add type hints to parameters and return value
def load_users(db_url, limit, active_only):
    ...
    # Returns a list of user dicts like:
    # [{"id": 1, "name": "Alice", "email": "alice@x.com"}]
    """, language="python")

    answer = st.text_area("Your answer:", height=80,
                          placeholder="def load_users(db_url: str, limit: int, active_only: bool) -> List[Dict]:")
    if answer and "str" in answer and "int" in answer and "bool" in answer and "List" in answer:
        st.success("✅ Excellent! That's the correct signature. In production you'd often use a TypedDict or Pydantic model instead of bare Dict.")
    elif answer:
        st.info("Getting there. Make sure you hint all three parameters AND the return type.")

    if st.button("Claim XP ✨", key="xp_types"):
        award_xp(40, "Type hints learned")

    st.markdown("---")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.py_lesson = 4
            st.rerun()
    with col2:
        if st.button("Next: Challenge →", type="primary"):
            st.session_state.py_lesson = 6
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# LESSON 6 — Challenge: Fix the Code
# ══════════════════════════════════════════════════════════════════════════════
elif lesson == 6:
    st.markdown("## ⚔️ Challenge 1: Fix the Code")
    st.markdown("""
    <div class='challenge-box'>
    <b>Mission:</b> The code below has 5 production problems. Find and explain all 5.
    Each correct answer = 20 XP. Max 100 XP.<br><br>
    <span class='xp-reward'>⭐ 100 XP available</span>
    </div>
    """, unsafe_allow_html=True)

    st.code("""
import requests

DB_PASSWORD = "admin123"
API_URL = "https://api.company.com/data"

def get_sales_data(start_date, end_date):
    try:
        response = requests.get(API_URL + "?start=" + start_date + "&end=" + end_date)
        data = response.json()
        print("Got data: " + str(len(data)) + " records")
        return data
    except:
        return []

def process_all():
    sales = get_sales_data("2024-01-01", "2024-12-31")
    results = []
    for record in sales:
        result = {
            "id": record["id"],
            "amount": float(record["amount"]),
            "region": record["region"]
        }
        results.append(result)
    print("Done processing")
    return results
    """, language="python")

    bugs = {
        "Bug 1": {
            "question": "What's wrong with `DB_PASSWORD = 'admin123'`?",
            "correct": "hardcoded",
            "options": [
                "Nothing, passwords are fine in code",
                "It's hardcoded — credentials must come from environment variables",
                "The variable name should be lowercase",
                "It should be encrypted",
            ]
        },
        "Bug 2": {
            "question": "What's wrong with the `except:` clause?",
            "correct": "bare",
            "options": [
                "Nothing, it catches all errors which is good",
                "It's a bare except — catches everything including KeyboardInterrupt, hides root cause",
                "It should use except Exception as e",
                "It's fine for a simple function",
            ]
        },
        "Bug 3": {
            "question": "What's wrong with `return []` in the except block?",
            "correct": "silent",
            "options": [
                "Should return None instead",
                "Should return an empty dict",
                "Silent failure — caller gets empty list and thinks nothing is wrong. Should raise.",
                "Nothing wrong, empty list is a safe default",
            ]
        },
        "Bug 4": {
            "question": "What's wrong with `print('Got data: ...')`?",
            "correct": "print",
            "options": [
                "The string formatting is wrong",
                "print() should be replaced with logging — no timestamps, no levels, can't route to log systems",
                "Nothing, print is fine for debugging",
                "It should use f-strings",
            ]
        },
        "Bug 5": {
            "question": "What happens if `record['amount']` is `'N/A'` or `record['region']` is missing?",
            "correct": "no validation",
            "options": [
                "Python handles it automatically",
                "float('N/A') raises ValueError, missing key raises KeyError — no validation or error handling",
                "It returns None for those fields",
                "The loop skips bad records automatically",
            ]
        },
    }

    score = 0
    for bug_name, bug in bugs.items():
        st.markdown(f"**{bug_name}:** {bug['question']}")
        ans = st.radio("", bug["options"], index=None, key=bug_name)
        if ans:
            if bug["correct"] in ans.lower():
                st.success("✅ +20 XP")
                score += 20
            else:
                correct_ans = [o for o in bug["options"] if bug["correct"] in o.lower()]
                st.error(f"❌ Correct answer: {correct_ans[0] if correct_ans else 'See explanation'}")

    if score > 0:
        st.markdown(f"### Your score: {score}/100 XP")
        if st.button(f"Claim {score} XP ✨", key="xp_challenge1"):
            award_xp(score, "Completed Fix the Code challenge")

    st.markdown("---")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.py_lesson = 5
            st.rerun()
    with col2:
        if st.button("Next: Build a Config →", type="primary"):
            st.session_state.py_lesson = 7
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# LESSON 7 — Challenge: Build a Config
# ══════════════════════════════════════════════════════════════════════════════
elif lesson == 7:
    st.markdown("## ⚔️ Challenge 2: Build a Config Module")
    st.markdown("""
    <div class='challenge-box'>
    <b>Mission:</b> Write a complete <code>config.py</code> that loads from environment variables.
    Requirements below.<br><br>
    <span class='xp-reward'>⭐ 100 XP — Module Complete Badge on finish</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Requirements:**
    - Load `DB_HOST`, `DB_PORT` (int), `DB_NAME`, `DB_USER`, `DB_PASSWORD` from env
    - Load `APP_ENV` with default `"development"`
    - Load `LOG_LEVEL` with default `"INFO"`
    - Use `@dataclass` for the config structure
    - Add a `db_url` property that builds the connection string
    - Missing required variables should raise `KeyError` immediately
    """)

    user_code = st.text_area("Write your config.py here:", height=300, placeholder="""import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    # your code here...
    pass

@dataclass
class AppConfig:
    # your code here...
    pass

def load_config() -> AppConfig:
    # your code here...
    pass
""")

    if st.button("Check My Code"):
        checks = {
            "Uses @dataclass": "@dataclass" in user_code,
            "Loads DB_HOST from env": "DB_HOST" in user_code and "environ" in user_code,
            "Converts DB_PORT to int": "int(" in user_code and "DB_PORT" in user_code,
            "Has APP_ENV with default": "APP_ENV" in user_code and (".get" in user_code or "development" in user_code),
            "Has db_url property": "@property" in user_code or "db_url" in user_code or "url" in user_code,
            "Has load_config function": "def load_config" in user_code,
        }
        all_pass = all(checks.values())
        for check, passed in checks.items():
            if passed:
                st.success(f"✅ {check}")
            else:
                st.error(f"❌ {check}")

        if all_pass:
            st.balloons()
            st.success("🎉 All checks passed! Excellent work.")
            if st.button("Claim 100 XP + Badge ✨"):
                p = load_progress()
                p["xp"] += 100
                if "python_foundations" not in p["completed_modules"]:
                    p["completed_modules"].append("python_foundations")
                if "🐍 Python Pro" not in p["badges"]:
                    p["badges"].append("🐍 Python Pro")
                save_progress(p)
                st.session_state.progress = p
                st.balloons()
                st.success("🏅 Badge earned: 🐍 Python Pro! Module complete — go to Home to see your progress.")

    st.markdown("---")
    st.markdown("### Model Solution (reveal after attempting)")
    with st.expander("👁️ Show solution"):
        st.code("""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

@dataclass
class AppConfig:
    env: str
    log_level: str
    db: DatabaseConfig

def load_config() -> AppConfig:
    return AppConfig(
        env=os.environ.get("APP_ENV", "development"),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
        db=DatabaseConfig(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            name=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
        ),
    )
        """, language="python")

    col1, _ = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.py_lesson = 6
            st.rerun()
