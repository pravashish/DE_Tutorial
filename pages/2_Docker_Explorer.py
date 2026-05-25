import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Docker Explorer", page_icon="🐳", layout="wide")

st.markdown("""
<style>
    .docker-header { font-size:1.6rem; font-weight:800; color:#2496ed; }
    .layer-box {
        border-radius: 8px; padding: 0.7rem 1rem; margin: 3px 0;
        border-left: 4px solid; font-family: monospace; font-size:0.88rem;
        transition: all 0.2s;
    }
    .cached { border-color: #6bcb77; background: #0d2818; }
    .rebuilt { border-color: #ff6b6b; background: #2d0f0f; }
    .lesson-card { background:#1e1e2e; border-radius:10px; padding:1.2rem; border-left:3px solid #2496ed; margin:0.5rem 0; }
    .cmd-box { background:#0d1117; border-radius:8px; padding:1rem; font-family:monospace; font-size:0.88rem; border:1px solid #2a2a3e; }
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

if "docker_section" not in st.session_state:
    st.session_state.docker_section = 0

st.markdown("<div class='docker-header'>🐳 Docker Visual Explorer</div>", unsafe_allow_html=True)
st.markdown("*Phase 1 · Week 1 · Visual + Interactive · 250 XP available*")
st.markdown("---")

# ── Section nav ───────────────────────────────────────────────────────────────
sections = ["The Problem", "Core Concepts", "Layer Simulator", "Dockerfile Builder", "Compose Explorer", "Commands Game", "Challenge"]
cols = st.columns(len(sections))
for i, (col, name) in enumerate(zip(cols, sections)):
    with col:
        active = i == st.session_state.docker_section
        done = i < st.session_state.docker_section
        label = f"{'✅' if done else ('▶' if active else '○')} {i+1}"
        if st.button(label, key=f"ds_{i}", use_container_width=True, type="primary" if active else "secondary"):
            st.session_state.docker_section = i
            st.rerun()

st.markdown("---")
sec = st.session_state.docker_section


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 0 — The Problem Docker Solves
# ══════════════════════════════════════════════════════════════════════════════
if sec == 0:
    st.markdown("## The Problem Docker Solves")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='lesson-card'>
        <b>Without Docker:</b><br><br>
        "It works on my machine" is the most hated phrase in engineering.
        Your laptop has Python 3.11. The server has Python 3.8.
        You have pandas 2.0. The server has pandas 1.3.
        You're on Mac. The server is Linux.<br><br>
        Result: code works locally, fails in production. Every time.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background:#0d2818; border-radius:10px; padding:1.2rem; border-left:3px solid #6bcb77'>
        <b>With Docker:</b><br><br>
        You package your code + Python version + all libraries + OS dependencies
        into a single <b>container image</b>. That image runs identically on your
        laptop, your teammate's laptop, staging, and production.<br><br>
        "Ship the environment, not just the code."
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Visual: What Docker Actually Is")
    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────┐
    │                  YOUR LAPTOP                        │
    │                                                     │
    │  ┌──────────────────────────────────────────────┐  │
    │  │           Docker Container                    │  │
    │  │                                               │  │
    │  │  ┌──────────────┐  ┌──────────────────────┐  │  │
    │  │  │  Your Code   │  │  Python 3.11         │  │  │
    │  │  │  pipeline.py │  │  pandas 2.0          │  │  │
    │  │  │  config.py   │  │  psycopg2            │  │  │
    │  │  └──────────────┘  │  All dependencies    │  │  │
    │  │                    └──────────────────────┘  │  │
    │  │  Isolated filesystem · Network · Processes   │  │
    │  └──────────────────────────────────────────────┘  │
    │                                                     │
    └─────────────────────────────────────────────────────┘

    This exact container runs the same on ANY machine with Docker.
    ```
    """)

    st.markdown("### Docker vs Virtual Machines")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Virtual Machine (heavy)**
        ```
        ┌─────────────────┐
        │   Your App      │
        ├─────────────────┤
        │  Guest OS       │  ← Full OS copy (GBs)
        ├─────────────────┤
        │  Hypervisor     │
        ├─────────────────┤
        │  Host OS        │
        └─────────────────┘
        Startup: minutes
        Size: gigabytes
        ```
        """)
    with col2:
        st.markdown("""
        **Docker Container (light)**
        ```
        ┌─────────────────┐
        │   Your App      │
        ├─────────────────┤
        │  Dependencies   │  ← Just what you need (MBs)
        ├─────────────────┤
        │  Docker Engine  │
        ├─────────────────┤
        │  Host OS        │  ← Shared kernel
        └─────────────────┘
        Startup: milliseconds
        Size: megabytes
        ```
        """)

    st.markdown("### Quick Check")
    a = st.radio("Which best describes a Docker container?", [
        "A) A full copy of an operating system",
        "B) An isolated environment with your app + dependencies that runs the same everywhere",
        "C) A virtual machine that emulates hardware",
        "D) A cloud service that runs your code",
    ], index=None)
    if a:
        if "B)" in a:
            st.success("✅ Exactly right!")
            if st.button("Claim XP ✨", key="xp_d0"):
                award_xp(25, "Understood what Docker is")
        else:
            st.error("Not quite — containers share the host OS kernel, they don't copy it.")

    st.markdown("---")
    col1, col2 = st.columns([6,1])
    with col2:
        if st.button("Next →", type="primary"):
            st.session_state.docker_section = 1
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Core Concepts
# ══════════════════════════════════════════════════════════════════════════════
elif sec == 1:
    st.markdown("## Core Docker Concepts")

    concepts = [
        ("📄", "Dockerfile", "Recipe", "A text file with step-by-step instructions to build an image. Like a recipe for a cake."),
        ("🖼️", "Image", "Baked Cake", "A read-only snapshot built from a Dockerfile. Can be stored and shared. Like a baked cake ready to serve."),
        ("📦", "Container", "Slice on a plate", "A running instance of an image. You can have many containers from one image."),
        ("🏪", "Registry", "Bakery / Store", "A place to store and share images. Docker Hub is public. Your company has a private one (ECR, GCR, ACR)."),
        ("🎼", "docker-compose", "Catering order", "A tool to define and run multi-container apps. One file, multiple services all connected."),
        ("📚", "Layer", "Recipe step", "Each instruction in a Dockerfile creates a layer. Layers are cached and reused for speed."),
        ("💾", "Volume", "External hard drive", "Persistent storage that survives container restarts. Your database data lives here."),
        ("🌐", "Network", "Private WiFi", "How containers talk to each other. Services in the same compose file share a network."),
    ]

    cols = st.columns(2)
    for i, (icon, term, analogy, desc) in enumerate(concepts):
        with cols[i % 2]:
            st.markdown(f"""
            <div style='background:#1e1e2e; border-radius:10px; padding:1rem; margin-bottom:0.7rem; display:flex; gap:12px'>
                <div style='font-size:1.8rem'>{icon}</div>
                <div>
                    <div style='font-weight:700; color:#2496ed'>{term}</div>
                    <div style='color:#ffd93d; font-size:0.82rem'>Analogy: {analogy}</div>
                    <div style='color:#ccc; font-size:0.85rem; margin-top:4px'>{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### Match the Analogy")
    q = {
        "The instructions to build your environment": ("Dockerfile", ["Dockerfile", "Image", "Container", "Registry"]),
        "A running instance of your app": ("Container", ["Dockerfile", "Image", "Container", "Volume"]),
        "Where you push/pull images from": ("Registry", ["Network", "Volume", "Registry", "Layer"]),
        "Persistent storage that survives restarts": ("Volume", ["Volume", "Container", "Network", "Image"]),
    }
    correct_all = True
    for question, (correct, options) in q.items():
        ans = st.selectbox(question, options, index=None, key=f"docker_q_{question}")
        if ans is not None and ans != correct:
            correct_all = False

    if st.button("Claim XP ✨", key="xp_d1"):
        award_xp(30, "Docker concepts mastered")

    st.markdown("---")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.docker_section = 0
            st.rerun()
    with col2:
        if st.button("Next: Layer Simulator →", type="primary"):
            st.session_state.docker_section = 2
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Layer Cache Simulator
# ══════════════════════════════════════════════════════════════════════════════
elif sec == 2:
    st.markdown("## 🎮 Layer Cache Simulator")
    st.markdown("""
    <div class='lesson-card'>
    Docker builds images in <b>layers</b>. Each instruction in your Dockerfile = one layer.
    Layers are <b>cached</b> — if a layer hasn't changed, Docker reuses it instead of rebuilding.
    This makes rebuilds fast. <b>The order of instructions matters enormously.</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Simulate a Docker Build")
    st.markdown("Choose what changed between builds, and see which layers get cached vs rebuilt:")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**What changed since last build?**")
        change_code = st.checkbox("I changed my Python source code", value=True)
        change_reqs = st.checkbox("I added a new library to requirements.txt")
        change_base = st.checkbox("I upgraded the base Python version")

    LAYERS = [
        ("FROM python:3.11-slim", "Base image pull", "base"),
        ("WORKDIR /app", "Set working directory", "workdir"),
        ("ENV PYTHONDONTWRITEBYTECODE=1", "Set environment variables", "env"),
        ("COPY requirements.txt .", "Copy requirements file", "reqs_copy"),
        ("RUN pip install -r requirements.txt", "Install Python libraries (~2 min)", "pip"),
        ("COPY src/ ./src/", "Copy source code", "src"),
        ("RUN useradd appuser", "Create non-root user", "user"),
        ("CMD [\"python\", \"-m\", \"pipeline\"]", "Set startup command", "cmd"),
    ]

    # Determine which layers rebuild
    rebuild_from = None
    if change_base:
        rebuild_from = "base"
    elif change_reqs:
        rebuild_from = "reqs_copy"
    elif change_code:
        rebuild_from = "src"

    rebuilding = False
    with col2:
        st.markdown("**Build output:**")
        total_time = 0
        for instruction, description, key in LAYERS:
            if rebuild_from and key == rebuild_from:
                rebuilding = True
            if rebuilding:
                status = "rebuilt"
                time_est = "2min" if key == "pip" else "2s"
                total_time += 120 if key == "pip" else 2
                st.markdown(f"""
                <div class='layer-box rebuilt'>
                    🔨 REBUILDING &nbsp; <b>{instruction[:45]}</b><br>
                    <span style='color:#888; font-size:0.8rem'>{description} · {time_est}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='layer-box cached'>
                    ⚡ CACHED &nbsp;&nbsp;&nbsp;&nbsp; <b>{instruction[:45]}</b><br>
                    <span style='color:#888; font-size:0.8rem'>{description} · &lt;1s</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    if change_code and not change_reqs and not change_base:
        st.success("""
        ✅ **Good Dockerfile order!** Only layers after `COPY src/` rebuild.
        The slow `pip install` layer is cached → **build takes ~4 seconds**.
        This is why we copy requirements.txt BEFORE source code.
        """)
    elif change_reqs and not change_base:
        st.warning("""
        ⚠️ Requirements changed → pip install must rerun (~2 minutes).
        But base image layers are still cached. This is expected and unavoidable.
        """)
    elif change_base:
        st.error("""
        🐢 Base image changed → **everything rebuilds** (~3-4 minutes).
        Only change the base image when absolutely necessary.
        """)

    st.markdown("### The Golden Rule")
    st.markdown("""
    ```
    ✅ CORRECT ORDER (fast rebuilds):
    ─────────────────────────────────
    FROM python:3.11-slim        ← changes rarely
    COPY requirements.txt .      ← changes occasionally
    RUN pip install ...          ← expensive, cache it
    COPY src/ .                  ← changes often
    CMD [...]

    ❌ WRONG ORDER (slow rebuilds):
    ─────────────────────────────────
    FROM python:3.11-slim
    COPY src/ .                  ← any code change busts the cache here
    COPY requirements.txt .
    RUN pip install ...          ← reinstalls EVERY TIME code changes
    CMD [...]
    ```
    """)

    if st.button("Claim XP ✨", key="xp_d2"):
        award_xp(40, "Docker layer caching understood")

    st.markdown("---")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.docker_section = 1
            st.rerun()
    with col2:
        if st.button("Next: Dockerfile Builder →", type="primary"):
            st.session_state.docker_section = 3
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Dockerfile Builder
# ══════════════════════════════════════════════════════════════════════════════
elif sec == 3:
    st.markdown("## 🔧 Dockerfile Builder")
    st.markdown("Build a Dockerfile by selecting options. See the result update in real time.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Configuration")
        python_ver = st.selectbox("Python version", ["3.11-slim", "3.11", "3.10-slim", "3.9-slim"])
        workdir = st.text_input("Working directory", "/app")
        has_reqs = st.checkbox("Has requirements.txt", True)
        src_dir = st.text_input("Source directory to copy", "src/")
        run_as_root = st.checkbox("Run as root (bad practice)", False)
        entrypoint = st.text_input("Startup command", "python -m pipeline.main")
        port = st.number_input("Expose port (0 = none)", 0, 65535, 0)

    with col2:
        st.markdown("### Generated Dockerfile")
        cmd_parts = entrypoint.split()
        cmd_json = json.dumps(cmd_parts)
        expose_line = f"\nEXPOSE {port}" if port else ""
        user_lines = "\nRUN useradd --create-home appuser\nUSER appuser" if not run_as_root else ""
        reqs_lines = f"\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt" if has_reqs else ""
        warning = "" if not run_as_root else "\n# ⚠️  WARNING: Running as root is a security risk in production"

        dockerfile = f"""FROM python:{python_ver}

WORKDIR {workdir}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1{warning}{reqs_lines}

COPY {src_dir} ./{src_dir}{expose_line}{user_lines}

CMD {cmd_json}"""

        st.code(dockerfile, language="dockerfile")

        if run_as_root:
            st.warning("⚠️ Running as root is a security risk. A container breakout gives full host access.")
        else:
            st.success("✅ Running as non-root user — production best practice.")

        if python_ver in ["3.11", "3.10"]:
            st.info("💡 Use `-slim` variant to reduce image size significantly (~900MB → ~130MB).")

    st.markdown("### Image Size Comparison")
    sizes = {
        "python:3.11 (full)": 900,
        "python:3.11-slim": 130,
        "python:3.11-alpine": 50,
    }
    for variant, size_mb in sizes.items():
        bar_width = int((size_mb / 900) * 100)
        color = "#6bcb77" if size_mb < 200 else ("#ffd93d" if size_mb < 500 else "#ff6b6b")
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:12px; margin:4px 0'>
            <span style='min-width:200px; font-family:monospace; font-size:0.85rem'>{variant}</span>
            <div style='background:#2a2a3e; border-radius:4px; height:20px; flex:1'>
                <div style='background:{color}; width:{bar_width}%; height:20px; border-radius:4px'></div>
            </div>
            <span style='color:{color}; min-width:60px'>{size_mb}MB</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    > **Alpine** is smallest but can cause issues with C-extension libraries (like pandas/numpy).
    > **slim** is the production sweet spot — small and compatible.
    """)

    if st.button("Claim XP ✨", key="xp_d3"):
        award_xp(35, "Dockerfile building skills earned")

    st.markdown("---")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.docker_section = 2
            st.rerun()
    with col2:
        if st.button("Next: Compose Explorer →", type="primary"):
            st.session_state.docker_section = 4
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Compose Explorer
# ══════════════════════════════════════════════════════════════════════════════
elif sec == 4:
    st.markdown("## 🎼 docker-compose Explorer")
    st.markdown("""
    <div class='lesson-card'>
    In data engineering, you never run just one service. You run your app + a database +
    maybe a message queue + a dashboard. <b>docker-compose</b> defines all of them together,
    their connections, and their dependencies.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Architecture: What We're Building")
    st.markdown("""
    ```
    ┌──────────────────────────────────────────────────────────┐
    │                  docker-compose network                  │
    │                                                          │
    │   ┌────────────┐        ┌──────────────────────────┐    │
    │   │  pipeline  │──────▶│       postgres            │    │
    │   │  (Python)  │       │  port: 5432               │    │
    │   │            │       │  data: postgres_volume    │    │
    │   └────────────┘       └──────────────────────────┘    │
    │         │                                               │
    │         │              ┌──────────────────────────┐    │
    │         └─────────────▶│       pgadmin            │    │
    │                        │  port: 8080 (browser)    │    │
    │                        └──────────────────────────┘    │
    └──────────────────────────────────────────────────────────┘

    Containers talk via service name: pipeline → postgres:5432
    NOT localhost — each container has its own network namespace
    ```
    """)

    st.markdown("### Annotated docker-compose.yml")

    tab1, tab2, tab3 = st.tabs(["Full File", "Key Concepts", "🎮 Interactive"])

    with tab1:
        st.code("""
version: "3.9"

services:

  # ── Database ─────────────────────────────────────────────────
  postgres:
    image: postgres:15              # Use official image, pin version
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret123
      POSTGRES_DB: pipeline_db
    ports:
      - "5432:5432"                 # host_port:container_port
    volumes:
      - postgres_data:/var/lib/postgresql/data   # persist data!
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 5s
      timeout: 5s
      retries: 5                    # pipeline waits until this passes

  # ── Application ───────────────────────────────────────────────
  pipeline:
    build: .                        # build from local Dockerfile
    environment:
      DB_HOST: postgres             # ← service name, NOT localhost
      DB_PORT: 5432
      DB_NAME: pipeline_db
      DB_USER: admin
      DB_PASSWORD: secret123
      APP_ENV: development
    depends_on:
      postgres:
        condition: service_healthy  # don't start until DB is ready
    volumes:
      - ./src:/app/src              # hot reload in development

  # ── DB Admin UI ───────────────────────────────────────────────
  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "8080:80"                   # access at http://localhost:8080
    depends_on:
      - postgres

volumes:
  postgres_data:                    # docker manages this volume
        """, language="yaml")

    with tab2:
        concepts = [
            ("service name as hostname", "Inside compose, containers find each other by service name. `pipeline` connects to `postgres:5432`, not `localhost:5432`. Each container is its own network host."),
            ("depends_on + healthcheck", "Without healthcheck, `depends_on` just waits for the container to start — not for it to be ready. Postgres takes a few seconds to accept connections. healthcheck solves this."),
            ("named volumes", "`postgres_data` is a named volume managed by Docker. It persists when you run `docker compose down`. Only `docker compose down -v` removes it. This is where your DB data lives."),
            ("bind mounts in dev", "`./src:/app/src` maps your local src folder into the container. Changes to local files appear instantly — no rebuild needed. Remove this in production."),
            ("ports mapping", "`5432:5432` means: expose container port 5432 on host port 5432. The left is host, right is container. If you have a local Postgres, use `5433:5432` to avoid conflict."),
        ]
        for concept, explanation in concepts:
            with st.expander(f"📌 {concept}"):
                st.markdown(explanation)

    with tab3:
        st.markdown("### What happens when you run `docker compose up`?")
        if st.button("▶ Simulate `docker compose up`"):
            steps = [
                ("📦", "Reading docker-compose.yml...", "#2496ed"),
                ("🔨", "Building `pipeline` image from Dockerfile...", "#ffd93d"),
                ("⬇️", "Pulling `postgres:15` image...", "#ffd93d"),
                ("⬇️", "Pulling `dpage/pgadmin4` image...", "#ffd93d"),
                ("🚀", "Starting `postgres` container...", "#2496ed"),
                ("❤️", "Waiting for postgres healthcheck... (attempt 1/5)", "#888"),
                ("❤️", "Waiting for postgres healthcheck... (attempt 2/5)", "#888"),
                ("✅", "postgres is healthy!", "#6bcb77"),
                ("🚀", "Starting `pipeline` container (depends_on satisfied)...", "#2496ed"),
                ("🚀", "Starting `pgadmin` container...", "#2496ed"),
                ("✅", "All services running!", "#6bcb77"),
                ("🌐", "pipeline → postgres:5432 (connected)", "#6bcb77"),
                ("🌐", "pgadmin available at http://localhost:8080", "#6bcb77"),
            ]

            progress_bar = st.empty()
            log_area = st.empty()
            logs = []
            import time
            for i, (icon, msg, color) in enumerate(steps):
                logs.append(f'<div style="color:{color}; font-family:monospace; font-size:0.85rem; padding:2px 0">{icon} {msg}</div>')
                log_area.markdown("".join(logs), unsafe_allow_html=True)
                time.sleep(0.3)

        if st.button("Claim XP ✨", key="xp_d4"):
            award_xp(35, "docker-compose mastered")

    st.markdown("---")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.docker_section = 3
            st.rerun()
    with col2:
        if st.button("Next: Commands Game →", type="primary"):
            st.session_state.docker_section = 5
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Commands Game
# ══════════════════════════════════════════════════════════════════════════════
elif sec == 5:
    st.markdown("## ⚔️ Docker Commands Game")
    st.markdown("Match the command to what it does. Score 10 XP per correct answer.")

    if "cmd_score" not in st.session_state:
        st.session_state.cmd_score = 0

    questions = [
        {
            "command": "docker compose up -d",
            "correct": "Start all services in the background (detached mode)",
            "options": [
                "Start all services in the background (detached mode)",
                "Start all services and show logs",
                "Delete all containers",
                "Download all images",
            ]
        },
        {
            "command": "docker compose down -v",
            "correct": "Stop containers AND delete volumes (wipes database data)",
            "options": [
                "Stop containers and keep volumes",
                "Stop containers AND delete volumes (wipes database data)",
                "Delete all images",
                "Stop only the main service",
            ]
        },
        {
            "command": "docker compose logs -f pipeline",
            "correct": "Stream live logs from the pipeline service",
            "options": [
                "Show all logs from all services",
                "Show the last log file",
                "Stream live logs from the pipeline service",
                "Show pipeline configuration",
            ]
        },
        {
            "command": "docker compose exec postgres psql -U admin",
            "correct": "Open a psql shell inside the running postgres container",
            "options": [
                "Restart the postgres service",
                "Open a psql shell inside the running postgres container",
                "Show postgres logs",
                "Connect from outside Docker",
            ]
        },
        {
            "command": "docker compose up --build",
            "correct": "Rebuild images before starting (picks up code changes)",
            "options": [
                "Start without rebuilding",
                "Rebuild images before starting (picks up code changes)",
                "Build only, don't start",
                "Download latest images",
            ]
        },
    ]

    score = 0
    for q in questions:
        st.markdown(f"**What does this command do?**")
        st.code(q["command"], language="bash")
        ans = st.radio("", q["options"], index=None, key=f"cmd_{q['command']}")
        if ans:
            if ans == q["correct"]:
                st.success("✅ +10 XP")
                score += 10
            else:
                st.error(f"❌ Correct: {q['correct']}")
        st.markdown("---")

    if score > 0 and st.button(f"Claim {score} XP ✨", key="xp_d5"):
        award_xp(score, "Docker commands quiz")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.docker_section = 4
            st.rerun()
    with col2:
        if st.button("Next: Final Challenge →", type="primary"):
            st.session_state.docker_section = 6
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Final Challenge
# ══════════════════════════════════════════════════════════════════════════════
elif sec == 6:
    st.markdown("## ⚔️ Final Challenge: Build the Stack")
    st.markdown("""
    <div style='background:#1a1a2e; border-radius:10px; padding:1.2rem; border:1px solid #7b2ff7'>
    <b>Mission:</b> You need to set up a local development stack with:<br>
    • A Python pipeline service<br>
    • A PostgreSQL database (persisted)<br>
    • The pipeline should wait for Postgres to be healthy<br>
    • Source code should hot-reload (no rebuild for code changes)<br><br>
    Answer the questions below to prove you can build it.
    </div>
    """, unsafe_allow_html=True)

    q1 = st.radio(
        "1. Your pipeline can't connect to Postgres. The error is: `could not connect to host 'localhost'`. What's wrong?",
        [
            "A) PostgreSQL isn't installed",
            "B) The pipeline is using `localhost` instead of the service name `postgres`",
            "C) The port number is wrong",
            "D) Docker isn't running",
        ], index=None, key="fc1"
    )
    if q1 and "B)" in q1:
        st.success("✅ Correct! In docker-compose, containers talk via service name. `localhost` refers to the container itself, not the postgres service.")
    elif q1:
        st.error("❌ In docker-compose, each container is its own network host. Use the service name `postgres` as the hostname.")

    q2 = st.radio(
        "2. You restart your stack with `docker compose down && docker compose up`. Your database data is gone. Why?",
        [
            "A) docker compose down always deletes data",
            "B) You didn't define a named volume — data was in an anonymous container layer",
            "C) PostgreSQL has a bug",
            "D) You need to use `--persist` flag",
        ], index=None, key="fc2"
    )
    if q2 and "B)" in q2:
        st.success("✅ Correct! Without a named volume, data lives in the container's writable layer. When the container is removed, data is gone. Always define `volumes: postgres_data:/var/lib/postgresql/data`.")
    elif q2:
        st.error("❌ The issue is missing volume configuration. Without a named volume, data doesn't persist beyond the container's lifetime.")

    q3 = st.radio(
        "3. Your pipeline starts before Postgres is ready and crashes. How do you fix this in docker-compose.yml?",
        [
            "A) Add `sleep 5` at the start of your pipeline script",
            "B) Add `depends_on: postgres` with `condition: service_healthy` and a healthcheck on postgres",
            "C) Start postgres manually before running compose",
            "D) Use `restart: always` on the pipeline service",
        ], index=None, key="fc3"
    )
    if q3 and "B)" in q3:
        st.success("✅ Correct! `depends_on` with `condition: service_healthy` makes compose wait until postgres passes its healthcheck before starting the pipeline.")
    elif q3:
        st.error("❌ `sleep` is fragile (what if Postgres takes longer?), and `restart: always` just keeps crashing. The proper solution is `depends_on` + `healthcheck`.")

    q4 = st.radio(
        "4. You want code changes to appear instantly without rebuilding the image. What do you add?",
        [
            "A) Use `--no-cache` when building",
            "B) Add a bind mount: `./src:/app/src` in the pipeline volumes section",
            "C) Run `docker compose up --build` after every change",
            "D) Install your code with `pip install -e .`",
        ], index=None, key="fc4"
    )
    if q4 and "B)" in q4:
        st.success("✅ Correct! A bind mount maps your local folder into the container in real time. Any file change is immediately visible inside the container.")
    elif q4:
        st.error("❌ Rebuilding on every change takes minutes. A bind mount `./src:/app/src` makes local files visible inside the container instantly.")

    answers_correct = all([
        q1 and "B)" in q1,
        q2 and "B)" in q2,
        q3 and "B)" in q3,
        q4 and "B)" in q4,
    ])

    if answers_correct:
        st.balloons()
        st.success("🎉 All correct! You understand Docker for data engineering.")
        if st.button("Claim 80 XP + Docker Badge 🐳"):
            p = load_progress()
            p["xp"] += 80
            if "docker_explorer" not in p["completed_modules"]:
                p["completed_modules"].append("docker_explorer")
            if "🐳 Docker Captain" not in p["badges"]:
                p["badges"].append("🐳 Docker Captain")
            save_progress(p)
            st.session_state.progress = p
            st.balloons()
            st.success("🏅 Badge earned: 🐳 Docker Captain! Head to Home to see your progress.")

    col1, _ = st.columns([1,1])
    with col1:
        if st.button("← Previous"):
            st.session_state.docker_section = 5
            st.rerun()
