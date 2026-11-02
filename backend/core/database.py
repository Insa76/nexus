import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")


def get_connection():
    conn = psycopg.connect(DB_URL, row_factory=dict_row)
    return conn


def init_db():

    conn = get_connection()
    cur = conn.cursor()

    print("INIT_DB EJECUTADO")

    # =========================
    # WORKFLOWS
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS workflows (
        id TEXT,
        version INTEGER,
        name TEXT,
        tenant_id TEXT,
        workspace_id TEXT,
        trigger TEXT,
        data TEXT,
        definition JSONB,
        active INTEGER,
        created_at TIMESTAMP,
        PRIMARY KEY (id, version, workspace_id)
    )
    """)

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_workflow_active
    ON workflows (id, active)
    """)

    # =========================
    # JOBS
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        workflow TEXT,
        version INTEGER,
        tenant_id TEXT,
        workspace_id TEXT,
        status TEXT,
        payload JSONB,
        result JSONB,
        error TEXT,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    """)

    # =========================
    # SCHEDULES
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id TEXT PRIMARY KEY,
        workflow TEXT,
        type TEXT,
        expression TEXT,
        enabled BOOLEAN,
        last_run TIMESTAMP
    )
    """)

    # =========================
    # TENANTS
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
        id TEXT PRIMARY KEY,
        name TEXT,
        created_at TIMESTAMP
    )
    """)

    # =========================
    # WORKSPACES
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS workspaces (
        id TEXT PRIMARY KEY,
        tenant_id TEXT,
        name TEXT,
        created_at TIMESTAMP
    )
    """)

    # =========================
    # USERS
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT,
        tenant_id TEXT,
        workspace_id TEXT,
        created_at TIMESTAMP
    )
    """)

    # =========================
    # AUDIT LOGS
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        tenant_id TEXT,
        workspace_id TEXT,
        action TEXT,
        entity TEXT,
        entity_id TEXT,
        metadata JSONB,
        created_at TIMESTAMP
    )
    """)

    # =========================
    # DEAD JOBS
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS dead_jobs (
        id TEXT PRIMARY KEY,
        job_id TEXT,
        workflow TEXT,
        tenant_id TEXT,
        workspace_id TEXT,
        error TEXT,
        payload JSONB,
        created_at TIMESTAMP
    )
    """)

    # =========================
    # STEP EXECUTIONS
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS step_executions (
        id TEXT PRIMARY KEY,
        job_id TEXT,
        workflow TEXT,
        step_name TEXT,
        status TEXT,
        input JSONB,
        output JSONB,
        error TEXT,
        started_at TIMESTAMP,
        finished_at TIMESTAMP
    )
    """)

    # =========================
    # CIRCUIT BREAKERS
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS circuit_breakers (
        workflow TEXT PRIMARY KEY,
        state TEXT,
        failure_count INTEGER,
        last_failure TIMESTAMP,
        opened_at TIMESTAMP
    )
    """)

    # =========================
    # JOB STEPS
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS job_steps (
        id SERIAL PRIMARY KEY,
        job_id TEXT,
        step TEXT,
        status TEXT,
        result JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    )
    """)

    # =========================
    # NEXUS LEARNING
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS nexus_learning (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP,
        type TEXT,
        message TEXT,
        workflow TEXT,
        data JSONB
    )
    """)

    # =========================
    # DECISIONS LOG
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS decisions_log (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP,
        action TEXT,
        reason TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    goal TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()