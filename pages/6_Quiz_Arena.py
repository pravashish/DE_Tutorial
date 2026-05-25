import streamlit as st
import json
import random
from pathlib import Path

st.set_page_config(page_title="Quiz Arena", page_icon="⚔️", layout="wide")

st.markdown("""
<style>
    .quiz-header { font-size:1.6rem; font-weight:800; color:#ff6b6b; }
    .question-card { background:#1e1e2e; border-radius:12px; padding:1.5rem; border-top:3px solid #ff6b6b; margin:1rem 0; }
    .score-big { font-size:3rem; font-weight:900; text-align:center; }
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

ALL_QUESTIONS = [
    # Python
    {
        "topic": "Python",
        "difficulty": "easy",
        "q": "What's the problem with `except:` (bare except with no exception type)?",
        "options": ["It's slower", "It catches everything including KeyboardInterrupt, hiding root causes", "It doesn't work in Python 3", "Nothing, it's fine"],
        "answer": "It catches everything including KeyboardInterrupt, hiding root causes",
        "explanation": "Bare except catches SystemExit, KeyboardInterrupt, and all exceptions, making it impossible to Ctrl+C a program and hiding what actually went wrong."
    },
    {
        "topic": "Python",
        "difficulty": "medium",
        "q": "Why use `os.environ['KEY']` instead of `os.environ.get('KEY')` for required config?",
        "options": ["It's faster", "It crashes at startup if the variable is missing — fail loudly", "get() doesn't work on Windows", "No difference"],
        "answer": "It crashes at startup if the variable is missing — fail loudly",
        "explanation": "Failing at startup with a clear KeyError is much better than silently running with a missing value and getting a confusing error 30 minutes into processing."
    },
    # Docker
    {
        "topic": "Docker",
        "difficulty": "easy",
        "q": "Why do we COPY requirements.txt before COPY src/ in a Dockerfile?",
        "options": ["Alphabetical order", "Docker requires it", "So pip install gets cached — only reruns when requirements change, not on every code change", "Doesn't matter"],
        "answer": "So pip install gets cached — only reruns when requirements change, not on every code change",
        "explanation": "Docker caches each layer. Copying requirements first means pip install (which takes minutes) is only re-run when requirements.txt changes, not on every code edit."
    },
    {
        "topic": "Docker",
        "difficulty": "medium",
        "q": "In docker-compose, your app service can't connect to postgres. The error says 'unknown host localhost'. Why?",
        "options": ["Postgres isn't running", "Wrong port number", "Should use service name 'postgres' not 'localhost' — each container has its own network", "Firewall issue"],
        "answer": "Should use service name 'postgres' not 'localhost' — each container has its own network",
        "explanation": "In docker-compose, localhost refers to the container itself. Services talk to each other via service name: postgres:5432, not localhost:5432."
    },
    {
        "topic": "Docker",
        "difficulty": "hard",
        "q": "What's the difference between `docker compose down` and `docker compose down -v`?",
        "options": ["No difference", "down stops containers; down -v also deletes named volumes (your database data)", "-v means verbose output", "-v means force delete"],
        "answer": "down stops containers; down -v also deletes named volumes (your database data)",
        "explanation": "Named volumes persist by default when you stop a compose stack. The -v flag also removes them, which deletes your database data permanently."
    },
    # SQL
    {
        "topic": "SQL",
        "difficulty": "medium",
        "q": "What does `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY amount DESC)` do?",
        "options": [
            "Returns the total number of rows",
            "Numbers each row sequentially within each customer's orders, 1 being their highest amount",
            "Groups rows by customer",
            "Deletes duplicate rows"
        ],
        "answer": "Numbers each row sequentially within each customer's orders, 1 being their highest amount",
        "explanation": "PARTITION BY resets the counter per customer. ORDER BY amount DESC means rank 1 = highest amount per customer. This keeps all rows unlike GROUP BY."
    },
    {
        "topic": "SQL",
        "difficulty": "easy",
        "q": "What is the main advantage of a CTE over a nested subquery?",
        "options": ["CTEs are faster", "CTEs are named and readable — you can reference them multiple times and read the query like a story", "CTEs use less memory", "Subqueries don't work in PostgreSQL"],
        "answer": "CTEs are named and readable — you can reference them multiple times and read the query like a story",
        "explanation": "Both execute similarly in most databases. The main benefit is readability — CTEs let you name intermediate results and build complex queries in clear steps."
    },
    # Data Modeling
    {
        "topic": "Data Modeling",
        "difficulty": "medium",
        "q": "In a star schema, what goes in a fact table vs a dimension table?",
        "options": [
            "Facts = text descriptions, Dimensions = numbers",
            "Facts = events/measures (revenue, quantity), Dimensions = context (who, what, where, when)",
            "Facts = recent data, Dimensions = historical data",
            "No difference, it's just naming convention"
        ],
        "answer": "Facts = events/measures (revenue, quantity), Dimensions = context (who, what, where, when)",
        "explanation": "Fact tables record what happened (with numeric measures). Dimension tables provide context. This separation enables fast analytical queries with simple JOINs."
    },
    # ETL
    {
        "topic": "ETL",
        "difficulty": "easy",
        "q": "What is the key difference between ETL and ELT?",
        "options": [
            "ETL uses Python, ELT uses SQL",
            "ETL transforms before loading; ELT loads raw data first then transforms in the warehouse",
            "ETL is faster, ELT is slower",
            "ELT is only for cloud databases"
        ],
        "answer": "ETL transforms before loading; ELT loads raw data first then transforms in the warehouse",
        "explanation": "Modern data stacks (dbt + Snowflake/BigQuery) favor ELT: raw data lands in the warehouse, and SQL-based transformations (dbt models) run inside the warehouse."
    },
    {
        "topic": "ETL",
        "difficulty": "hard",
        "q": "Your pipeline ran without errors but revenue numbers are wrong. What type of bug is this and how do you find it?",
        "options": [
            "Syntax error — run a linter",
            "Business logic bug — review the logic against business requirements, add data quality tests",
            "Infrastructure bug — check server logs",
            "This can't happen if unit tests pass"
        ],
        "answer": "Business logic bug — review the logic against business requirements, add data quality tests",
        "explanation": "Silent correctness bugs are the hardest. Unit tests verify code works; they don't verify business logic is right. Data quality tests (e.g., assert revenue > 0, assert no cancelled orders in revenue) catch this."
    },
    # Distributed Systems
    {
        "topic": "Distributed Systems",
        "difficulty": "hard",
        "q": "The CAP theorem says a distributed system can guarantee at most 2 of 3 properties. What are they?",
        "options": [
            "Cost, Availability, Performance",
            "Consistency, Availability, Partition Tolerance",
            "Caching, Atomicity, Persistence",
            "Concurrency, Accuracy, Performance"
        ],
        "answer": "Consistency, Availability, Partition Tolerance",
        "explanation": "CAP: Consistency (every read gets the latest write), Availability (every request gets a response), Partition Tolerance (works despite network failures). You can only guarantee 2."
    },
    # General DE
    {
        "topic": "Data Engineering",
        "difficulty": "medium",
        "q": "What is idempotency in the context of data pipelines?",
        "options": [
            "The pipeline runs fast",
            "Running the pipeline multiple times produces the same result as running it once",
            "The pipeline handles errors automatically",
            "Data is encrypted at rest"
        ],
        "answer": "Running the pipeline multiple times produces the same result as running it once",
        "explanation": "Idempotent pipelines are critical. If your pipeline fails halfway and reruns, you shouldn't get double-counted rows or duplicate records. Design pipelines with UPSERT or truncate-reload patterns."
    },
]

st.markdown("<div class='quiz-header'>⚔️ Quiz Arena</div>", unsafe_allow_html=True)
st.markdown("*Test your knowledge across all topics · 10 XP per correct answer*")
st.markdown("---")

tab1, tab2 = st.tabs(["🎮 Quiz Mode", "📊 Topic Practice"])

with tab1:
    topics = ["All Topics"] + sorted(set(q["topic"] for q in ALL_QUESTIONS))
    difficulties = ["All", "easy", "medium", "hard"]

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_topic = st.selectbox("Topic", topics)
    with col2:
        selected_diff = st.selectbox("Difficulty", difficulties)
    with col3:
        num_q = st.slider("Number of questions", 3, len(ALL_QUESTIONS), 5)

    if st.button("🎮 Start New Quiz", type="primary"):
        pool = ALL_QUESTIONS.copy()
        if selected_topic != "All Topics":
            pool = [q for q in pool if q["topic"] == selected_topic]
        if selected_diff != "All":
            pool = [q for q in pool if q["difficulty"] == selected_diff]

        if len(pool) < num_q:
            st.warning(f"Only {len(pool)} questions available for this filter. Showing all.")
            num_q = len(pool)

        st.session_state.quiz_questions = random.sample(pool, num_q)
        st.session_state.quiz_answers = {}
        st.session_state.quiz_submitted = False
        st.rerun()

    if "quiz_questions" in st.session_state and st.session_state.quiz_questions:
        questions = st.session_state.quiz_questions

        if not st.session_state.get("quiz_submitted"):
            for i, q in enumerate(questions):
                diff_color = {"easy": "#6bcb77", "medium": "#ffd93d", "hard": "#ff6b6b"}[q["difficulty"]]
                st.markdown(f"""
                <div class='question-card'>
                    <div style='display:flex; justify-content:space-between; margin-bottom:8px'>
                        <span style='color:#888; font-size:0.82rem'>{q["topic"]}</span>
                        <span style='background:{diff_color}22; color:{diff_color}; padding:2px 8px; border-radius:10px; font-size:0.78rem'>{q["difficulty"]}</span>
                    </div>
                    <div style='font-weight:600; margin-bottom:12px'>Q{i+1}. {q["q"]}</div>
                </div>
                """, unsafe_allow_html=True)

                ans = st.radio("", q["options"], index=None, key=f"qa_{i}", label_visibility="collapsed")
                if ans:
                    st.session_state.quiz_answers[i] = ans
                st.markdown("")

            if len(st.session_state.quiz_answers) == len(questions):
                if st.button("✅ Submit Quiz", type="primary"):
                    st.session_state.quiz_submitted = True
                    st.rerun()
            else:
                remaining = len(questions) - len(st.session_state.quiz_answers)
                st.info(f"Answer {remaining} more question(s) to submit.")

        else:
            score = 0
            for i, q in enumerate(questions):
                user_ans = st.session_state.quiz_answers.get(i)
                correct = user_ans == q["answer"]
                if correct:
                    score += 1
                icon = "✅" if correct else "❌"
                color = "#6bcb77" if correct else "#ff6b6b"
                st.markdown(f"""
                <div style='background:#1e1e2e; border-radius:10px; padding:1rem; margin:0.5rem 0; border-left:4px solid {color}'>
                    <div style='font-weight:600'>{icon} Q{i+1}. {q["q"]}</div>
                    <div style='color:{color}; margin-top:4px'>Your answer: {user_ans or "Not answered"}</div>
                    {"" if correct else f'<div style="color:#888; margin-top:4px">Correct: {q["answer"]}</div>'}
                    <div style='color:#888; font-size:0.82rem; margin-top:6px'>💡 {q["explanation"]}</div>
                </div>
                """, unsafe_allow_html=True)

            xp_earned = score * 10
            pct = int(score / len(questions) * 100)
            grade_color = "#6bcb77" if pct >= 80 else ("#ffd93d" if pct >= 60 else "#ff6b6b")

            st.markdown(f"""
            <div style='background:#1e1e2e; border-radius:12px; padding:2rem; text-align:center; margin-top:1rem; border:2px solid {grade_color}'>
                <div class='score-big' style='color:{grade_color}'>{score}/{len(questions)}</div>
                <div style='font-size:1.2rem; color:#ccc; margin-top:8px'>{pct}% · {xp_earned} XP earned</div>
                <div style='color:#888; margin-top:4px'>
                    {"🏆 Outstanding!" if pct == 100 else "🎉 Great work!" if pct >= 80 else "📚 Keep studying!" if pct >= 60 else "💪 Review the material and try again"}
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Claim {xp_earned} XP ✨"):
                    p = load_progress()
                    p["xp"] += xp_earned
                    save_progress(p)
                    st.balloons()
                    st.success(f"🎉 +{xp_earned} XP added!")
            with col2:
                if st.button("🔄 New Quiz"):
                    del st.session_state.quiz_questions
                    del st.session_state.quiz_answers
                    st.session_state.quiz_submitted = False
                    st.rerun()

with tab2:
    st.markdown("## Practice by Topic")
    topic_counts = {}
    for q in ALL_QUESTIONS:
        topic_counts[q["topic"]] = topic_counts.get(q["topic"], 0) + 1

    for topic, count in sorted(topic_counts.items()):
        st.markdown(f"""
        <div style='background:#1e1e2e; border-radius:8px; padding:0.8rem 1rem; margin:0.3rem 0; display:flex; justify-content:space-between; align-items:center'>
            <span style='font-weight:600'>{topic}</span>
            <span style='color:#888'>{count} questions</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Interview Cheat Sheet")
    with st.expander("🐍 Python Production Patterns"):
        st.markdown("""
        - Always use `logging` not `print()`
        - Use `os.environ['KEY']` for required vars (fail loudly)
        - Use custom exception classes per domain
        - Never use bare `except:` — always catch specific exceptions
        - Use `@dataclass` for config objects
        - Type hints on every public function
        """)
    with st.expander("🐳 Docker Key Facts"):
        st.markdown("""
        - Layer order matters: put rarely-changing things first
        - Copy `requirements.txt` before source code for caching
        - Use `-slim` base images for smaller size
        - Never run as root in production
        - Services talk via service name, not localhost
        - `down -v` deletes volumes (your data!)
        """)
    with st.expander("🗄️ SQL Key Facts"):
        st.markdown("""
        - Window functions don't collapse rows (unlike GROUP BY)
        - CTEs are for readability, not necessarily performance
        - `ROW_NUMBER()` = unique, `RANK()` = gaps on ties, `DENSE_RANK()` = no gaps
        - `LAG()` / `LEAD()` for comparing rows to previous/next
        - Indexes speed up WHERE and JOIN columns
        - `EXPLAIN ANALYZE` shows query execution plan
        """)
    with st.expander("📐 Data Modeling Key Facts"):
        st.markdown("""
        - Star schema: one fact table, multiple dimension tables
        - Fact tables: numeric measures of events (revenue, quantity)
        - Dimension tables: context (customer, product, date, location)
        - 3NF for OLTP (transactional), star schema for OLAP (analytical)
        - Slowly Changing Dimensions (SCD) handle attribute changes over time
        - Never store derived metrics in the database — compute them at query time
        """)
