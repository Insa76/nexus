from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from contextlib import asynccontextmanager
import logging
import asyncio

from core.database import init_db, get_connection

from api.routes import router
from api.dashboard import router as dashboard_router
from auth.routes import router as auth_router
from api.marketplace import router as market_router
from sync.server import router as sync_router
from api.realtime import router as realtime_router
from api.jobs import router as jobs_router
from api.setup import router as setup_router
from workflows.routes import router as workflows_router
from monitor.routes import router as monitor_router
from scheduler.routes import router as scheduler_router
from audit.routes import router as audit_router
from events.webhook import router as webhook_router
from events.routes_dlq import router as dlq_router
from brain.routes import router as brain_router
from api.copilot import router as copilot_router
from api.system import router as system_router
from api.ai import router as ai_router
from api.goals import router as goals_router
from api.simulation import router as simulation_router
from api.schedules import router as schedules_router
from api.ai_builder import router as ai_builder_router
from api.workflows import router as workflows_router
from api.triggers import router as triggers_router
from api.executions import router as executions_router
from api.approvals import router as approvals_router


from automations.scheduler import add_job
from automations.watcher import watch

from core.metrics import metrics
from core.nexus_state import nexus_state
from core.governance import evaluate_mode_request
from core.explainer import explain_decision
from core.decision_engine import decision_engine

from realtime.ws import manager as ws

from core.self_model import self_model
from core.anomaly_detector import anomaly_detector
from learning.learning_engine import learning_engine

from workflows.repository import load_workflows
from sync.client import pull_memory
from brain.personal_memory.store import save_memory
from autonomy.autonomous_loop import autonomous_loop
from triggers.folder_trigger import start_folder_trigger

from api.missions import (
    router as missions_router
)
from core.persistent_agents import (
    DesktopWatcherAgent
)

from api.operator import (
    router as operator_router
)

from core.system_agent import (
    SystemAgent
)

from actions.plugins import load_plugins
from scheduler.engine import Scheduler

from jobs.manager import JobManager
import jobs.manager as manager_module

from auth.security import decode_token
from resilience.circuit import circuit

logging.basicConfig(level=logging.INFO)

# =====================================================
# DB WAIT
# =====================================================

def wait_for_db():
    import time

    for _ in range(10):
        try:
            conn = get_connection()
            conn.cursor().execute("SELECT 1")
            conn.close()
            print("✅ DB lista")
            return
        except Exception:
            print("⏳ Esperando DB...")
            time.sleep(2)

    raise Exception("DB no disponible")


# =====================================================
# LIFESPAN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    logging.info("🚀 Nexus iniciando...")

    wait_for_db()
    init_db()

    manager_module.manager = JobManager()
    await manager_module.manager.start()

    Scheduler()

    load_plugins()

    asyncio.create_task(autonomous_loop())

    start_folder_trigger()

    for m in pull_memory():
        save_memory(m)

    workflows = load_workflows()

    for w in workflows:
        trigger = w.get("trigger")
        if trigger and trigger.get("type") == "filesystem":
            from events.watcher import watcher
            watcher.watch(trigger.get("path"), w.get("name"))

    add_job(600, [
        {"action": "create_folder", "value": "PDF"}
    ])

    watch(".", ".pdf", [
        {"action": "create_folder", "value": "PDF"}
    ])

    yield

    logging.info("🛑 Nexus detenido")


# =====================================================
# APP
# =====================================================

app = FastAPI(title="Nexus IA", lifespan=lifespan)

# =====================================================
# 🔥 CORS (ANTES DE AUTH)
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# 🔐 AUTH MIDDLEWARE
# =====================================================

@app.middleware("http")
async def auth(request: Request, call_next):

    if request.method == "OPTIONS":
        return await call_next(request)

    path = request.url.path

    PUBLIC_PATHS = {
        "/",
        "/health",
        "/metrics",
        "/docs",
        "/openapi.json",
        "/auth/login",
        "/auth/register",
    }

    if path in PUBLIC_PATHS or path.startswith("/auth") or path.startswith("/ws"):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return JSONResponse(status_code=401, content={"error": "Missing token"})

    try:
        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":
            raise Exception("Invalid format")

        token = parts[1]

        user = decode_token(token)

        if not user:
            raise Exception("Invalid token")

        request.state.user = user

    except Exception as e:
        print("❌ AUTH ERROR:", str(e))
        return JSONResponse(status_code=401, content={"error": "Invalid token"})

    return await call_next(request)


# =====================================================
# ROUTERS
# =====================================================

app.include_router(router)
app.include_router(dashboard_router)
app.include_router(auth_router)
app.include_router(market_router)
app.include_router(sync_router)
app.include_router(realtime_router)
app.include_router(jobs_router)
app.include_router(setup_router)
app.include_router(workflows_router)
app.include_router(monitor_router)
app.include_router(scheduler_router)
app.include_router(audit_router)
app.include_router(webhook_router)
app.include_router(dlq_router)
app.include_router(brain_router)
app.include_router(copilot_router)
app.include_router(system_router)
app.include_router(ai_router)
app.include_router(goals_router)
app.include_router(simulation_router)
app.include_router(schedules_router)
app.include_router(ai_builder_router)
app.include_router(triggers_router)
app.include_router(executions_router)
app.include_router(approvals_router)
app.include_router(missions_router)
app.include_router(operator_router)


# =====================================================
# ROOT
# =====================================================

@app.get("/")
def root():
    return {"status": "Nexus running"}


@app.get("/health")
def health():

    try:
        jobs = len(manager_module.manager.list_jobs() or [])
        return {
            "status": "ok",
            "scheduler_running": True,
            "jobs_loaded": jobs
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}


# =====================================================
# METRICS
# =====================================================

@app.get("/metrics")
def get_metrics():
    return {
        "counters": metrics.counters,
        "histograms": metrics.histograms,
        "active_jobs": metrics.active_jobs,
        "circuit_state": circuit.state
    }


# =====================================================
# MODE
# =====================================================

@app.post("/nexus/mode")
async def set_mode(data: dict):

    requested = data.get("mode")

    approved, reason = evaluate_mode_request(requested)

    nexus_state.apply_mode(approved)

    await ws.broadcast({
        "type": "mode.changed",
        "mode": approved
    })

    return {
        "requested": requested,
        "applied": approved
    }


# =====================================================
# FAVICON
# =====================================================

@app.get("/favicon.ico")
def favicon():
    return FileResponse("static/favicon.ico")

