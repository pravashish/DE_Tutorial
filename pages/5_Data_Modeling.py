import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Data Modeling", page_icon="📐", layout="wide")

st.markdown("""
<style>
    .dm-header { font-size:1.6rem; font-weight:800; color:#c084fc; }
    .lesson-card { background:#1e1e2e; border-radius:10px; padding:1.2rem; border-left:3px solid #c084fc; }
    .schema-box { background:#0d0d1a; border-radius:8px; padding:1rem; font-family:monospace; font-size:0.85rem; border:1px solid #2a2a3e; }
</style>
""", unsafe_allow_html=True)

PROGRESS_FILE = Path("data/progress.json")

def award_xp(amount, reason):
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            p = json.load(f)
    else:
        p = {"xp": 0, "completed_modules": [], "badges": []}
    p["xp"] += amount
    PROGRESS_FILE.parent.mkdir(exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(p, f, indent=2)
    st.balloons()
    st.success(f"🎉 +{amount} XP — {reason}")

st.markdown("<div class='dm-header'>📐 Data Modeling</div>", unsafe_allow_html=True)
st.markdown("*Phase 2 · The foundation of every data warehouse · 300 XP available*")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Star Schema", "Normalization", "🎮 Design It"])

with tab1:
    st.markdown("## Star Schema — The Data Warehouse Standard")
    st.markdown("""
    <div class='lesson-card'>
    The star schema is how virtually every data warehouse is organized.
    One central <b>fact table</b> (what happened) surrounded by <b>dimension tables</b> (who/what/where/when).
    It looks like a star when drawn as a diagram.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ```
                        ┌─────────────────┐
                        │  dim_date       │
                        │  date_id  PK    │
                        │  date           │
                        │  month          │
                        │  quarter        │
                        │  year           │
                        └────────┬────────┘
                                 │
    ┌──────────────┐    ┌────────▼─────────┐    ┌──────────────────┐
    │ dim_customer │    │   fact_orders    │    │  dim_product     │
    │ customer_id  │◄───│  order_id   PK  │───▶│  product_id  PK  │
    │ name         │    │  customer_id FK │    │  name            │
    │ country      │    │  product_id  FK │    │  category        │
    │ tier         │    │  date_id     FK │    │  price           │
    └──────────────┘    │  amount         │    └──────────────────┘
                        │  quantity       │
                        │  discount       │
                        └─────────────────┘

    FACTS = measures (amount, quantity, discount)
    DIMENSIONS = context (who, what, when, where)
    ```
    """)

    st.markdown("### Fact Table vs Dimension Table")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Fact Table**
        - Records events / transactions
        - Has foreign keys to all dimensions
        - Contains numeric measures
        - Grows very large (billions of rows)
        - Examples: `fact_orders`, `fact_pageviews`, `fact_payments`
        """)
    with col2:
        st.markdown("""
        **Dimension Table**
        - Describes context
        - Has a primary key referenced by facts
        - Contains descriptive attributes
        - Relatively small (millions at most)
        - Examples: `dim_customer`, `dim_product`, `dim_date`
        """)

    st.markdown("### Why Star Schema Over Normalized?")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **3NF (Normalized) — for OLTP**
        ```sql
        -- To get order revenue by country:
        SELECT country, SUM(amount)
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN customers c ON o.customer_id = c.id
        JOIN addresses a ON c.address_id = a.id
        JOIN cities ci ON a.city_id = ci.id
        JOIN countries co ON ci.country_id = co.id
        GROUP BY country
        -- 6 joins — slow for analytics
        ```
        """)
    with col2:
        st.markdown("""
        **Star Schema — for OLAP**
        ```sql
        -- Same query with star schema:
        SELECT dc.country, SUM(fo.amount)
        FROM fact_orders fo
        JOIN dim_customer dc
          ON fo.customer_id = dc.customer_id
        GROUP BY dc.country
        -- 1 join — fast for analytics
        ```
        """)

    q = st.radio("Where does `revenue_usd` belong?", [
        "A) Dimension table — it describes a product",
        "B) Fact table — it's a numeric measure of an event",
        "C) Either works equally well",
        "D) A separate table by itself",
    ], index=None)
    if q:
        if "B)" in q:
            st.success("✅ Correct! Numeric measures (revenue, quantity, discount) always go in fact tables.")
        else:
            st.error("❌ Numeric measures that result from events belong in fact tables.")

    if st.button("Claim Star Schema XP ✨"):
        award_xp(60, "Star schema mastered")


with tab2:
    st.markdown("## Normalization — Eliminating Redundancy")
    st.markdown("""
    <div class='lesson-card'>
    Normalization is the process of structuring a database to reduce redundancy and improve integrity.
    It comes in "normal forms" (1NF, 2NF, 3NF). Most production OLTP databases target 3NF.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### The Problem: Unnormalized Data")
    st.markdown("""
    ```
    orders (unnormalized)
    ┌────┬──────────────┬─────────────┬─────────┬──────────┬────────────┬──────────┐
    │ id │ customer_name│customer_email│ country │ product  │ category   │ amount   │
    ├────┼──────────────┼─────────────┼─────────┼──────────┼────────────┼──────────┤
    │  1 │ Alice Johnson│alice@x.com  │ US      │ Pro Plan │subscription│ 299.00   │
    │  2 │ Alice Johnson│alice@x.com  │ US      │ Export   │addon       │  49.00   │
    │  3 │ Bob Smith    │bob@x.com    │ UK      │ Pro Plan │subscription│ 299.00   │
    └────┴──────────────┴─────────────┴─────────┴──────────┴────────────┴──────────┘

    Problems:
    • Alice's email stored twice — update one, forget the other → inconsistency
    • "subscription" stored for every Pro Plan order → waste
    • Changing Alice's country requires updating multiple rows
    ```
    """)

    st.markdown("### After Normalization (3NF)")
    st.markdown("""
    ```
    customers               products                orders
    ┌────┬───────┬───────┐  ┌────┬──────────┬────┐  ┌────┬─────┬─────┬────────┐
    │ id │ name  │ email │  │ id │ name     │cat │  │ id │cust │prod │amount  │
    ├────┼───────┼───────┤  ├────┼──────────┼────┤  ├────┼─────┼─────┼────────┤
    │  1 │ Alice │alice@ │  │  1 │ Pro Plan │sub │  │  1 │  1  │  1  │ 299.00 │
    │  2 │ Bob   │bob@   │  │  2 │ Export   │add │  │  2 │  1  │  2  │  49.00 │
    └────┴───────┴───────┘  └────┴──────────┴────┘  │  3 │  2  │  1  │ 299.00 │
                                                     └────┴─────┴─────┴────────┘
    ✅ Alice's email stored once
    ✅ "subscription" stored once per product
    ✅ Change Alice's data in one place
    ```
    """)

    if st.button("Claim Normalization XP ✨"):
        award_xp(50, "Normalization understood")


with tab3:
    st.markdown("## 🎮 Design It: E-commerce Schema")
    st.markdown("""
    <div style='background:#1a1a2e; border-radius:10px; padding:1.2rem; border:1px solid #c084fc'>
    <b>Challenge:</b> You're building a data warehouse for an e-commerce company.
    Answer the design questions below.<br><br>
    <span style='background:#7b2ff722; color:#c084fc; padding:3px 10px; border-radius:20px; font-size:0.82rem'>⭐ 100 XP</span>
    </div>
    """, unsafe_allow_html=True)

    q1 = st.radio(
        "1. You need to track 'number of items in each order'. Where does this go?",
        ["dim_product", "dim_customer", "fact_orders", "dim_date"],
        index=None, key="dm_q1"
    )
    if q1 == "fact_orders":
        st.success("✅ Correct! `quantity` is a measure of an event — it goes in the fact table.")
    elif q1:
        st.error("❌ Numeric measures of events belong in fact tables.")

    q2 = st.radio(
        "2. Product names change sometimes. If you use the current product name in fact_orders, what happens to historical data?",
        [
            "A) Nothing, it's fine",
            "B) Historical orders will show the new product name, not what was ordered at the time (Slowly Changing Dimension problem)",
            "C) The database prevents name changes",
            "D) You need to delete old records",
        ], index=None, key="dm_q2"
    )
    if q2 and "B)" in q2:
        st.success("✅ Correct! This is called a Slowly Changing Dimension (SCD). Solutions: store product_id (not name) in fact table, or use SCD Type 2 to version dimension records.")
    elif q2:
        st.error("❌ Storing mutable attributes in fact tables is a classic mistake. The product name can change but the historical order shouldn't change with it.")

    q3 = st.radio(
        "3. Your fact_orders table has 10 billion rows. A query GROUP BY customer_country is slow. What's the fix?",
        [
            "A) Add an index on customer_country in fact_orders",
            "B) customer_country should be in dim_customer, not fact_orders — join it at query time",
            "C) Partition fact_orders by customer_country",
            "D) Create a separate fact table for each country",
        ], index=None, key="dm_q3"
    )
    if q3 and "B)" in q3:
        st.success("✅ Correct! Country is a customer attribute — it belongs in dim_customer. The fact table only stores the customer_id foreign key. This is exactly why we have dimensions.")
    elif q3:
        st.error("❌ Denormalizing country into the fact table makes it hard to update and bloats the table. Join to dim_customer instead.")

    if all([q1 == "fact_orders", q2 and "B)" in q2, q3 and "B)" in q3]):
        st.balloons()
        st.success("🎉 All correct! You think like a data architect.")
        if st.button("Claim 100 XP + Data Modeling Badge ✨"):
            if PROGRESS_FILE.exists():
                with open(PROGRESS_FILE) as f:
                    p = json.load(f)
            else:
                p = {"xp": 0, "completed_modules": [], "badges": []}
            p["xp"] += 100
            if "data_modeling" not in p["completed_modules"]:
                p["completed_modules"].append("data_modeling")
            if "📐 Schema Architect" not in p["badges"]:
                p["badges"].append("📐 Schema Architect")
            PROGRESS_FILE.parent.mkdir(exist_ok=True)
            with open(PROGRESS_FILE, "w") as f:
                json.dump(p, f, indent=2)
            st.balloons()
            st.success("🏅 Badge: 📐 Schema Architect")
