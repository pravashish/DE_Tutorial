import streamlit as st
import pandas as pd
import sqlite3
import json
from pathlib import Path

st.set_page_config(page_title="SQL Playground", page_icon="🗄️", layout="wide")

st.markdown("""
<style>
    .sql-header { font-size:1.6rem; font-weight:800; color:#ffd93d; }
    .lesson-card { background:#1e1e2e; border-radius:10px; padding:1.2rem; border-left:3px solid #ffd93d; margin:0.5rem 0; }
    .result-table { border-radius:8px; overflow:hidden; }
    .hint-box { background:#1a1a2e; border-radius:8px; padding:0.8rem; border:1px solid #7b2ff7; font-size:0.88rem; }
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

# ── In-memory SQLite database with sample data ────────────────────────────────
@st.cache_resource
def get_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.executescript("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        country TEXT,
        signup_date TEXT,
        tier TEXT  -- 'free', 'pro', 'enterprise'
    );

    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(id),
        product TEXT,
        amount REAL,
        status TEXT,  -- 'completed', 'pending', 'cancelled'
        order_date TEXT
    );

    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL,
        stock INTEGER
    );

    INSERT INTO customers VALUES
        (1,  'Alice Johnson',  'alice@example.com',  'US',  '2023-01-15', 'pro'),
        (2,  'Bob Smith',      'bob@example.com',    'UK',  '2023-02-20', 'free'),
        (3,  'Carol White',    'carol@example.com',  'US',  '2023-03-10', 'enterprise'),
        (4,  'Dave Brown',     'dave@example.com',   'DE',  '2023-04-05', 'pro'),
        (5,  'Eve Davis',      'eve@example.com',    'US',  '2023-05-12', 'free'),
        (6,  'Frank Miller',   'frank@example.com',  'FR',  '2023-06-18', 'enterprise'),
        (7,  'Grace Wilson',   'grace@example.com',  'US',  '2023-07-22', 'pro'),
        (8,  'Henry Moore',    'henry@example.com',  'AU',  '2023-08-30', 'free'),
        (9,  'Iris Taylor',    'iris@example.com',   'US',  '2023-09-14', 'pro'),
        (10, 'Jack Anderson',  'jack@example.com',   'CA',  '2023-10-01', 'enterprise');

    INSERT INTO orders VALUES
        (1,  1, 'Analytics Pro',   299.00, 'completed', '2024-01-10'),
        (2,  1, 'Data Export',     49.00,  'completed', '2024-02-15'),
        (3,  2, 'Starter Pack',    9.99,   'completed', '2024-01-20'),
        (4,  3, 'Enterprise Suite',999.00, 'completed', '2024-01-05'),
        (5,  3, 'API Access',      199.00, 'completed', '2024-02-01'),
        (6,  3, 'Support Plan',    299.00, 'pending',   '2024-03-10'),
        (7,  4, 'Analytics Pro',   299.00, 'completed', '2024-01-25'),
        (8,  5, 'Starter Pack',    9.99,   'cancelled', '2024-02-10'),
        (9,  6, 'Enterprise Suite',999.00, 'completed', '2024-01-15'),
        (10, 7, 'Analytics Pro',   299.00, 'completed', '2024-02-20'),
        (11, 8, 'Starter Pack',    9.99,   'pending',   '2024-03-01'),
        (12, 9, 'Analytics Pro',   299.00, 'completed', '2024-02-28'),
        (13, 10,'Enterprise Suite',999.00, 'completed', '2024-01-30'),
        (14, 1, 'Support Plan',    299.00, 'completed', '2024-03-05'),
        (15, 4, 'Data Export',     49.00,  'completed', '2024-03-12');

    INSERT INTO products VALUES
        (1, 'Starter Pack',    'subscription', 9.99,  999),
        (2, 'Analytics Pro',   'subscription', 299.00, 500),
        (3, 'Enterprise Suite','subscription', 999.00, 100),
        (4, 'Data Export',     'addon',        49.00,  750),
        (5, 'API Access',      'addon',        199.00, 300),
        (6, 'Support Plan',    'service',      299.00, 200);
    """)
    return conn

conn = get_db()

def run_query(sql: str):
    try:
        df = pd.read_sql_query(sql, conn)
        return df, None
    except Exception as e:
        return None, str(e)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("<div class='sql-header'>🗄️ SQL Playground</div>", unsafe_allow_html=True)
st.markdown("*Phase 2 · Real SQLite Database · Write and run actual SQL · 400 XP available*")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Explore Data",
    "🎯 Guided Challenges",
    "🪟 Window Functions",
    "🔗 CTEs",
    "⚔️ Boss Challenge"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Explore Data
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Database Schema")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **customers**
        ```
        id           INTEGER  PK
        name         TEXT
        email        TEXT
        country      TEXT
        signup_date  TEXT
        tier         TEXT (free/pro/enterprise)
        ```
        """)
    with col2:
        st.markdown("""
        **orders**
        ```
        id           INTEGER  PK
        customer_id  INTEGER  FK → customers
        product      TEXT
        amount       REAL
        status       TEXT (completed/pending/cancelled)
        order_date   TEXT
        ```
        """)
    with col3:
        st.markdown("""
        **products**
        ```
        id           INTEGER  PK
        name         TEXT
        category     TEXT
        price        REAL
        stock        INTEGER
        ```
        """)

    st.markdown("### Free Query Editor")
    st.markdown("Write any SQL and see results instantly:")

    free_sql = st.text_area(
        "SQL:",
        value="SELECT * FROM customers LIMIT 5;",
        height=100,
        key="free_sql"
    )

    if st.button("▶ Run Query", type="primary", key="run_free"):
        df, err = run_query(free_sql)
        if err:
            st.error(f"❌ SQL Error: {err}")
        else:
            st.success(f"✅ {len(df)} rows returned")
            st.dataframe(df, use_container_width=True)

    st.markdown("### Quick Previews")
    preview_choice = st.selectbox("Preview table:", ["customers", "orders", "products"])
    df_preview, _ = run_query(f"SELECT * FROM {preview_choice}")
    st.dataframe(df_preview, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Guided Challenges
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    challenges = [
        {
            "title": "Basic: Count customers by country",
            "description": "Write a query that shows how many customers are from each country, ordered by count descending.",
            "hint": "Use GROUP BY country and COUNT(*), then ORDER BY",
            "solution": "SELECT country, COUNT(*) as customer_count FROM customers GROUP BY country ORDER BY customer_count DESC",
            "expected_cols": ["country", "customer_count"],
            "xp": 30,
        },
        {
            "title": "JOIN: Get customer names with their total spend",
            "description": "Show each customer's name and their total amount spent on COMPLETED orders only.",
            "hint": "JOIN customers to orders, filter WHERE status = 'completed', GROUP BY customer",
            "solution": "SELECT c.name, SUM(o.amount) as total_spent FROM customers c JOIN orders o ON c.id = o.customer_id WHERE o.status = 'completed' GROUP BY c.id, c.name ORDER BY total_spent DESC",
            "expected_cols": ["name", "total_spent"],
            "xp": 40,
        },
        {
            "title": "Filter: Customers who have never ordered",
            "description": "Find customers who have NO orders at all. (Hint: there's a technique for this.)",
            "hint": "Use LEFT JOIN ... WHERE orders.id IS NULL, or use NOT IN with a subquery",
            "solution": "SELECT c.name, c.email FROM customers c LEFT JOIN orders o ON c.id = o.customer_id WHERE o.id IS NULL",
            "expected_cols": ["name", "email"],
            "xp": 40,
        },
        {
            "title": "Aggregation: Revenue by product category",
            "description": "Join orders to products and show total revenue per product category (completed orders only).",
            "hint": "JOIN orders to products on product name, filter status, GROUP BY category",
            "solution": "SELECT p.category, SUM(o.amount) as revenue, COUNT(*) as order_count FROM orders o JOIN products p ON o.product = p.name WHERE o.status = 'completed' GROUP BY p.category ORDER BY revenue DESC",
            "expected_cols": ["category", "revenue"],
            "xp": 50,
        },
    ]

    for i, challenge in enumerate(challenges):
        with st.expander(f"Challenge {i+1}: {challenge['title']} — {challenge['xp']} XP"):
            st.markdown(f"**Task:** {challenge['description']}")

            with st.expander("💡 Hint"):
                st.markdown(f"<div class='hint-box'>{challenge['hint']}</div>", unsafe_allow_html=True)

            user_sql = st.text_area("Your SQL:", height=80, key=f"challenge_sql_{i}",
                                    placeholder="SELECT ...")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶ Run My Query", key=f"run_challenge_{i}"):
                    if user_sql.strip():
                        df, err = run_query(user_sql)
                        if err:
                            st.error(f"❌ {err}")
                        else:
                            st.success(f"✅ {len(df)} rows")
                            st.dataframe(df, use_container_width=True)
                            expected = challenge["expected_cols"]
                            actual = [c.lower() for c in df.columns]
                            if all(e.lower() in actual for e in expected):
                                st.success(f"🎉 Looks correct! Claim your {challenge['xp']} XP below.")
            with col2:
                if st.button("Show Solution", key=f"sol_{i}"):
                    st.code(challenge["solution"], language="sql")
                    df_sol, _ = run_query(challenge["solution"])
                    st.dataframe(df_sol, use_container_width=True)

            if st.button(f"Claim {challenge['xp']} XP ✨", key=f"xp_ch_{i}"):
                award_xp(challenge["xp"], f"SQL Challenge {i+1} completed")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Window Functions
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## Window Functions — The Most Powerful SQL Feature")
    st.markdown("""
    <div class='lesson-card'>
    Window functions let you compute aggregates <b>without collapsing rows</b>.
    A regular GROUP BY gives you one row per group. A window function gives you
    the aggregate AND keeps all original rows.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**GROUP BY — collapses rows**")
        st.code("""
SELECT customer_id, SUM(amount) as total
FROM orders
GROUP BY customer_id;
-- Returns 1 row per customer
        """, language="sql")

    with col2:
        st.markdown("**Window Function — keeps all rows**")
        st.code("""
SELECT
  customer_id,
  amount,
  SUM(amount) OVER (PARTITION BY customer_id)
    as customer_total
FROM orders;
-- Returns ALL order rows, each showing the customer's total
        """, language="sql")

    st.markdown("### Anatomy of a Window Function")
    st.markdown("""
    ```
    FUNCTION_NAME() OVER (
        PARTITION BY column    ← like GROUP BY — defines the window
        ORDER BY column        ← order within the window
        ROWS BETWEEN ...       ← optional: frame specification
    )
    ```
    """)

    st.markdown("### Try These — Run and Observe")

    window_examples = {
        "Row Number per customer": """
SELECT
    c.name,
    o.product,
    o.amount,
    ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.amount DESC) as rank_by_amount
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'completed'
ORDER BY c.name, rank_by_amount""",

        "Running total of revenue": """
SELECT
    order_date,
    amount,
    SUM(amount) OVER (ORDER BY order_date) as running_total
FROM orders
WHERE status = 'completed'
ORDER BY order_date""",

        "Each order vs customer average": """
SELECT
    c.name,
    o.product,
    o.amount,
    ROUND(AVG(o.amount) OVER (PARTITION BY o.customer_id), 2) as customer_avg,
    ROUND(o.amount - AVG(o.amount) OVER (PARTITION BY o.customer_id), 2) as vs_avg
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'completed'
ORDER BY c.name""",

        "Rank customers by total spend": """
SELECT
    c.name,
    c.tier,
    SUM(o.amount) as total_spent,
    RANK() OVER (ORDER BY SUM(o.amount) DESC) as spend_rank
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.status = 'completed'
GROUP BY c.id, c.name, c.tier
ORDER BY spend_rank""",
    }

    selected = st.selectbox("Choose an example:", list(window_examples.keys()))
    st.code(window_examples[selected].strip(), language="sql")

    if st.button("▶ Run Example", key="run_window"):
        df, err = run_query(window_examples[selected])
        if err:
            st.error(f"❌ {err}")
        else:
            st.dataframe(df, use_container_width=True)

    st.markdown("### Window Function Reference")
    funcs = [
        ("ROW_NUMBER()", "Unique sequential number within partition (1, 2, 3, 4...)"),
        ("RANK()", "Rank with gaps for ties (1, 1, 3, 4...)"),
        ("DENSE_RANK()", "Rank without gaps for ties (1, 1, 2, 3...)"),
        ("SUM() OVER", "Running or partitioned sum"),
        ("AVG() OVER", "Running or partitioned average"),
        ("LAG(col, n)", "Value from n rows before current row"),
        ("LEAD(col, n)", "Value from n rows after current row"),
        ("FIRST_VALUE(col)", "First value in the window frame"),
        ("LAST_VALUE(col)", "Last value in the window frame"),
        ("NTILE(n)", "Divide rows into n equal buckets (quartiles, deciles)"),
    ]
    for func, desc in funcs:
        st.markdown(f"- `{func}` — {desc}")

    if st.button("Claim XP for Window Functions ✨", key="xp_window"):
        award_xp(60, "Window functions mastered")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CTEs
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## Common Table Expressions (CTEs)")
    st.markdown("""
    <div class='lesson-card'>
    CTEs let you break complex queries into named, readable steps.
    Instead of one giant nested query, you write a series of named subqueries.
    Think of them as <b>temporary named views</b> that exist only for one query.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ❌ Without CTEs (hard to read)")
        st.code("""
SELECT name, total_spent, tier
FROM (
    SELECT c.name, c.tier,
           SUM(o.amount) as total_spent
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    WHERE o.status = 'completed'
    GROUP BY c.id, c.name, c.tier
) customer_totals
WHERE total_spent > 200
ORDER BY total_spent DESC
        """, language="sql")

    with col2:
        st.markdown("### ✅ With CTEs (readable)")
        st.code("""
WITH customer_totals AS (
    SELECT
        c.name,
        c.tier,
        SUM(o.amount) as total_spent
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    WHERE o.status = 'completed'
    GROUP BY c.id, c.name, c.tier
)
SELECT name, total_spent, tier
FROM customer_totals
WHERE total_spent > 200
ORDER BY total_spent DESC
        """, language="sql")

    st.markdown("### Multi-Step CTE Example")
    multi_cte = """
WITH
-- Step 1: Get completed orders only
completed_orders AS (
    SELECT * FROM orders WHERE status = 'completed'
),
-- Step 2: Aggregate by customer
customer_revenue AS (
    SELECT
        customer_id,
        COUNT(*) as order_count,
        SUM(amount) as total_revenue,
        MAX(amount) as largest_order
    FROM completed_orders
    GROUP BY customer_id
),
-- Step 3: Join with customer details
final AS (
    SELECT
        c.name,
        c.tier,
        c.country,
        cr.order_count,
        cr.total_revenue,
        cr.largest_order
    FROM customers c
    JOIN customer_revenue cr ON c.id = cr.customer_id
)
SELECT *
FROM final
ORDER BY total_revenue DESC
    """

    st.code(multi_cte.strip(), language="sql")
    if st.button("▶ Run Multi-Step CTE"):
        df, err = run_query(multi_cte)
        if err:
            st.error(f"❌ {err}")
        else:
            st.dataframe(df, use_container_width=True)
            st.info("Notice how each CTE is a named step. You can read the query like a story: first get completed orders, then aggregate, then join with customers.")

    if st.button("Claim XP for CTEs ✨", key="xp_cte"):
        award_xp(50, "CTEs mastered")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Boss Challenge
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("## ⚔️ Boss Challenge: Full Analytics Query")
    st.markdown("""
    <div style='background:#1a1a2e; border-radius:10px; padding:1.2rem; border:1px solid #ff6b6b'>
    <b>Mission:</b> Write ONE query using CTEs + Window Functions that produces this report:<br><br>
    For each customer show:<br>
    • Their name and tier<br>
    • Total revenue from completed orders<br>
    • Their rank by revenue (1 = highest spender)<br>
    • Revenue as % of total all-customer revenue<br>
    • Whether they are above or below average spend ("above avg" / "below avg")<br><br>
    <b>⭐ 100 XP if you get it right</b>
    </div>
    """, unsafe_allow_html=True)

    boss_sql = st.text_area("Write your query:", height=200, key="boss_sql",
                            placeholder="WITH customer_revenue AS (\n    ...\n)\nSELECT ...\n")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Run My Query", key="run_boss"):
            if boss_sql.strip():
                df, err = run_query(boss_sql)
                if err:
                    st.error(f"❌ {err}")
                else:
                    st.dataframe(df, use_container_width=True)
                    cols = [c.lower() for c in df.columns]
                    has_rank = any("rank" in c for c in cols)
                    has_pct = any("pct" in c or "percent" in c or "%" in c for c in cols)
                    if has_rank:
                        st.success("✅ Has ranking column!")
                    if has_pct:
                        st.success("✅ Has percentage column!")

    with col2:
        if st.button("Show Model Solution", key="boss_sol"):
            model = """
WITH customer_revenue AS (
    SELECT
        c.id,
        c.name,
        c.tier,
        SUM(o.amount) as total_revenue
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    WHERE o.status = 'completed'
    GROUP BY c.id, c.name, c.tier
),
with_stats AS (
    SELECT *,
        RANK() OVER (ORDER BY total_revenue DESC) as revenue_rank,
        ROUND(total_revenue * 100.0 / SUM(total_revenue) OVER (), 1) as pct_of_total,
        AVG(total_revenue) OVER () as avg_revenue
    FROM customer_revenue
)
SELECT
    name,
    tier,
    total_revenue,
    revenue_rank,
    pct_of_total || '%' as share_of_revenue,
    CASE WHEN total_revenue >= avg_revenue THEN 'above avg' ELSE 'below avg' END as vs_avg
FROM with_stats
ORDER BY revenue_rank
            """
            st.code(model.strip(), language="sql")
            df_sol, _ = run_query(model)
            st.dataframe(df_sol, use_container_width=True)

    if st.button("Claim 100 XP + SQL Badge ✨", key="xp_boss"):
        p = load_progress()
        p["xp"] += 100
        if "sql_playground" not in p["completed_modules"]:
            p["completed_modules"].append("sql_playground")
        if "🗄️ SQL Wizard" not in p["badges"]:
            p["badges"].append("🗄️ SQL Wizard")
        save_progress(p)
        st.session_state.progress = p
        st.balloons()
        st.success("🏅 Badge earned: 🗄️ SQL Wizard!")
