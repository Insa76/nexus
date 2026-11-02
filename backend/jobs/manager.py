import asyncio
import uuid
import json
import re

from datetime import datetime, timezone

from workflows.engine import run_workflow
from realtime.ws import manager as ws
from core.database import get_connection
from core.logger import logger
from workflows.repository import get_workflow_by_name
from jobs.actions import execute_action

from core.agents import (
    HealingAgent
)

from core.learning import (
    save_pattern,
    load_patterns
)

MAX_WORKERS = 4
MAX_QUEUE = 50


# ==========================================================
# JOB MANAGER
# ==========================================================
class JobManager:

    def __init__(self):

        self.queue = asyncio.Queue(
            maxsize=MAX_QUEUE
        )

        self.max_workers = MAX_WORKERS

        self.semaphore = asyncio.Semaphore(
            self.max_workers
        )

        self.started = False

        self.workers = []

        self.join_tracker = {}

        self.paused_jobs = {}

        self.runtime_logs = []

        self.paused = False

    def add_runtime_log(
        self,
        message
    ):

        self.runtime_logs.append(message)

        if len(self.runtime_logs) > 100:
          self.runtime_logs.pop(0)

    # ======================================================
    # START
    # ======================================================
    async def start(self):

        if self.started:
            return

        logger.info("JobManager started")

        self.started = True

        self.recover_jobs()

        for i in range(self.max_workers):

            worker = asyncio.create_task(
                self.worker()
            )

            self.workers.append(worker)

        # 🔥 RUNTIME SUPERVISOR
        asyncio.create_task(
            self.runtime_supervisor_loop()
        )        

    # ======================================================
    # RECOVER
    # ======================================================
    def recover_jobs(self):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, workflow, tenant_id
            FROM jobs
            WHERE status IN ('queued','running')
        """)

        rows = cur.fetchall()

        conn.close()

        for row in rows:

            try:

                self.queue.put_nowait({

                    "job_id": row["id"],

                    "workflow": row["workflow"],

                    "tenant_id": row["tenant_id"]
                })

            except:
                pass

    # ======================================================
    # WORKER
    # ======================================================
    async def worker(self):

        logger.info("Worker initialized")

        while True:

            if getattr(self, "paused", False):

                print("🛑 SYSTEM PAUSED")

                await asyncio.sleep(5)

                continue

            job = await self.queue.get()

            job_id = job["job_id"]

            workflow_input = job["workflow"]

            tenant_id = job["tenant_id"]

            print(f"\n🚀 NUEVO JOB: {job_id}")

            print(f"📦 INPUT: {workflow_input}")

            try:

                # ==========================================
                # NORMALIZAR
                # ==========================================
                if isinstance(workflow_input, str):

                    try:

                        workflow = json.loads(
                            workflow_input
                        )

                    except:

                        workflow = get_workflow_by_name(
                            workflow_input,
                            tenant_id
                        )

                else:

                    workflow = workflow_input

                print(
                    f"🔥 WORKFLOW FINAL: {workflow}"
                )

                async with self.semaphore:

                    self.update_status(
                        job_id,
                        "running"
                    )

                    steps = None
                    nodes = None
                    edges = None

                    # ======================================
                    # LINEAR
                    # ======================================
                    if isinstance(workflow, list):

                        steps = workflow

                    # ======================================
                    # STEPS
                    # ======================================
                    elif (
                        isinstance(workflow, dict)
                        and isinstance(
                            workflow.get("steps"),
                            list
                        )
                    ):

                        steps = workflow.get(
                            "steps",
                            []
                        )

                    # ======================================
                    # GRAPH MODE
                    # ======================================
                    elif (
                        isinstance(workflow, dict)
                        and workflow.get("nodes")
                    ):

                        nodes = workflow["nodes"]

                        edges = workflow.get(
                            "edges",
                            []
                        )

                    # ======================================
                    # START
                    # ======================================
                    await ws.broadcast({

                        "type": "job_log",

                        "job_id": job_id,

                        "message": "🚀 Job iniciado"
                    })

                    # ======================================
                    # LINEAR EXECUTION
                    # ======================================
                    if steps:

                        total_steps = len(steps)

                        completed_steps = 0

                        for step in steps:

                            action = step.get(
                                "action"
                            )

                            value = step.get(
                                "value",
                                {}
                            )

                            await ws.broadcast({

                                "type": "job_log",

                                "job_id": job_id,

                                "message":
                                    f"⚙️ Ejecutando {action}",

                                "action": action,

                                "status": "running"
                            })

                            try:

                                result = await execute_action(
                                    action,
                                    value
                                )

                                # ==========================
                                # CONDITION FAIL
                                # ==========================
                                if isinstance(result, dict):

                                    if (
                                        result.get("success")
                                        is False
                                    ):

                                        await ws.broadcast({

                                            "type": "job_log",

                                            "job_id": job_id,

                                            "message":
                                                f"⛔ Condición falló: {action}",

                                            "action": action,

                                            "status": "error"
                                        })

                                        break

                                completed_steps += 1

                                progress = int(
                                    (
                                        completed_steps
                                        / total_steps
                                    ) * 100
                                )

                                # ==========================
                                # MOVE FILES LOG
                                # ==========================
                                if action == "move_files":

                                    moved = result.get(
                                        "moved",
                                        0
                                    )

                                    if moved == 0:

                                        message = (
                                            "⚠️ No se encontraron archivos"
                                        )

                                    else:

                                        message = (
                                            f"📦 {moved} archivos movidos"
                                        )

                                    await ws.broadcast({

                                        "type": "job_log",

                                        "job_id": job_id,

                                        "message": message
                                    })

                                # ==========================
                                # SUCCESS
                                # ==========================
                                await ws.broadcast({

                                    "type": "job_log",

                                    "job_id": job_id,

                                    "message":
                                        f"✅ {action} completado",

                                    "action": action,

                                    "status": "success",

                                    "progress": progress,

                                    "completed_steps":
                                        completed_steps,

                                    "total_steps":
                                        total_steps
                                })

                            except Exception as step_error:

                                await ws.broadcast({

                                    "type": "job_log",

                                    "job_id": job_id,

                                    "message":
                                        f"❌ Error en {action}: {str(step_error)}",

                                    "action": action,

                                    "status": "error"
                                })

                                raise step_error

                    # ======================================
                    # GRAPH EXECUTION
                    # ======================================
                    elif nodes:

                        start = nodes[0]

                        await self.execute_node(
                            start,
                            nodes,
                            edges,
                            job_id
                        )

                    # ======================================
                    # END
                    # ======================================
                    await ws.broadcast({

                        "type": "job_log",

                        "job_id": job_id,

                        "message": "🎉 Job finalizado"
                    })

                    self.update_status(

                        job_id,

                        "done",

                        {
                            "status": "ok"
                        }
                    )

            except Exception as e:

                logger.error(
                    f"Job error: {e}"
                )

                await ws.broadcast({

                    "type": "job_log",

                    "job_id": job_id,

                    "message":
                        f"💥 Job falló: {str(e)}"
                })

                self.update_status(

                    job_id,

                    "error",

                    {
                        "error": str(e)
                    }
                )

            finally:

                self.queue.task_done()

    # ======================================================
    # CREATE JOB
    # ======================================================
    async def create_job(
        self,
        workflow,
        tenant_id
    ):

        job_id = str(uuid.uuid4())

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO jobs
            (
                id,
                workflow,
                tenant_id,
                status,
                updated_at
            )
            VALUES (%s,%s,%s,%s,%s)
        """, (

            job_id,

            json.dumps(workflow),

            tenant_id,

            "queued",

            datetime.now(timezone.utc)
        ))

        conn.commit()

        conn.close()

        job = {

            "job_id": job_id,

            "workflow": workflow,

            "tenant_id": tenant_id
        }

        await self.queue.put(job)

        print(f"📥 JOB ENQUEUED: {job_id}")

        return job_id

    # ======================================================
    # UPDATE STATUS
    # ======================================================
    def update_status(
        self,
        job_id,
        status,
        result=None
    ):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE jobs
            SET
                status = %s,
                result = %s,
                updated_at = %s
            WHERE id = %s
        """, (

            status,

            json.dumps(result)
            if result
            else None,

            datetime.now(timezone.utc),

            job_id
        ))

        conn.commit()

        conn.close()

    # ======================================================
    # EXECUTE NODE
    # ======================================================
    async def execute_node(
        self,
        node,
        nodes,
        edges,
        job_id
    ):

        healer = HealingAgent()

        action = node["data"]["action"]

        value = node["data"]["params"]

        self.save_execution(

            job_id,

            node["id"],

            action,

            "running"
        )

        print(f"⚙️ EXEC NODE: {action}")

        # ==================================================
        # JOIN NODE
        # ==================================================
        if action == "join":

            join_id = node["id"]

            incoming = len([
                e for e in edges
                if e["target"] == join_id
            ])

            if join_id not in self.join_tracker:

                self.join_tracker[join_id] = 0

            self.join_tracker[join_id] += 1

            print(
                f"🔗 JOIN {join_id}: "
                f"{self.join_tracker[join_id]}/{incoming}"
            )

            # esperar ramas
            if self.join_tracker[join_id] < incoming:
                return

            # reset
            self.join_tracker[join_id] = 0

        # ==================================================
        # WS RUNNING
        # ==================================================
        await ws.broadcast({

            "type": "job_log",

            "job_id": job_id,

            "node_id": node["id"],

            "message":
                f"⚙️ Ejecutando {action}",

            "action": action,

            "status": "running"
        })

        # ==================================================
        # RETRIES
        # ==================================================
        retry_count = node["data"].get(
            "retry",
            0
        )

        timeout = node["data"].get(
            "timeout",
            30
        )

        attempt = 0

        while True:

            try:

                result = await asyncio.wait_for(

                    execute_action(
                        action,
                        value
                    ),

                    timeout=timeout
                )

                print(f"✅ RESULT: {result}")

                # ==========================================
                # GENERATED DAG
                # ==========================================
                if isinstance(result, dict):

                    if result.get("workflow"):

                        generated = result["workflow"]

                        print(
                            "🧠 EXECUTING GENERATED DAG"
                        )

                        await self.execute_node(

                            generated["nodes"][0],

                            generated["nodes"],

                            generated["edges"],

                            job_id
                        )

                        return

                # ==========================================
                # APPROVAL
                # ==========================================
                if isinstance(result, dict):

                    if result.get(
                        "waiting_approval"
                    ):

                        print(
                            "🛑 WORKFLOW PAUSED"
                        )

                        self.paused_jobs[job_id] = {

                            "node": node,

                            "nodes": nodes,

                            "edges": edges
                        }

                        self.update_status(

                            job_id,

                            "waiting_approval",

                            {
                                "node_id":
                                    node["id"]
                            }
                        )

                        await ws.broadcast({

                            "type":
                                "approval_required",

                            "job_id": job_id,

                            "node_id":
                                node["id"],

                            "message":
                                value.get(
                                    "message",
                                    "Approval required"
                                )
                        })

                        return

                self.save_execution(

                    job_id,

                    node["id"],

                    action,

                    "success",

                    result
                )

                break

            except Exception as e:

                print(
                    f"❌ RETRY {attempt+1}/{retry_count}"
                )

                # ==========================================
                # SAVE ERROR
                # ==========================================
                self.save_execution(

                    job_id,

                    node["id"],

                    action,

                    "error",

                    {
                        "error": str(e)
                    }
                )

                # ==========================================
                # SELF HEALING
                # ==========================================
                try:

                    print(
                        "🧠 HEALING ATTEMPT"
                    )

                    healing = healer.heal(

                        str(e),

                        node
                    )

                    print(
                        f"🧠 HEAL RAW: {healing}"
                    )

                    match = re.search(

                        r"\{.*\}",

                        healing,

                        re.DOTALL
                    )

                    if match:

                        repair = json.loads(
                            match.group(0)
                        )

                        repair_action = repair.get(
                            "action"
                        )

                        repair_params = repair.get(
                            "params",
                            {}
                        )

                        print(
                            f"🛠 REPAIR: {repair_action}"
                        )

                        await execute_action(

                            repair_action,

                            repair_params
                        )

                        print(
                            "✅ REPAIR EXECUTED"
                        )

                        save_pattern(

                           pattern=str(e),

                           solution=str(healing),

                           confidence=0.7
                        )

                except Exception as heal_error:

                    print(
                        f"❌ HEAL ERROR: {heal_error}"
                    )

                attempt += 1

                if attempt > retry_count:
                    raise e

                await asyncio.sleep(1)

        # ==================================================
        # WS SUCCESS
        # ==================================================
        await ws.broadcast({

            "type": "job_log",

            "job_id": job_id,

            "node_id": node["id"],

            "message":
                f"✅ {action} completado",

            "action": action,

            "status": "success"
        })

        # ==================================================
        # ROUTING
        # ==================================================
        expected = "true"

        if isinstance(result, dict):

            if "decision" in result:

                expected = result["decision"]

            else:

                success = result.get(
                    "success",
                    True
                )

                expected = (
                    "true"
                    if success
                    else "false"
                )

        # ==================================================
        # MATCH EDGES
        # ==================================================
        matching_edges = []

        for e in edges:

            if (
                e["source"] == node["id"]
                and e.get("label") == expected
            ):

                matching_edges.append(e)

        # ==================================================
        # NEXT NODES
        # ==================================================
        next_nodes = []

        for edge in matching_edges:

            target = next(
                (
                    n for n in nodes
                    if n["id"] == edge["target"]
                ),
                None
            )

            if target:
                next_nodes.append(target)

        # ==================================================
        # PARALLEL EXECUTION
        # ==================================================
        if next_nodes:

            await asyncio.gather(*[

                self.execute_node(
                    n,
                    nodes,
                    edges,
                    job_id
                )

                for n in next_nodes
            ])

    # ======================================================
    # SAVE EXECUTION
    # ======================================================
    def save_execution(
        self,
        job_id,
        node_id,
        action,
        status,
        result=None
    ):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO workflow_executions
            (
                id,
                job_id,
                node_id,
                action,
                status,
                result
            )
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (

            str(uuid.uuid4()),

            job_id,

            node_id,

            action,

            status,

            json.dumps(result)
            if result
            else None
        ))

        conn.commit()

        conn.close()

    # ======================================================
    # RESUME JOB
    # ======================================================
    async def resume_job(
        self,
        job_id
    ):

        paused = self.paused_jobs.get(
            job_id
        )

        if not paused:
            return

        node = paused["node"]

        nodes = paused["nodes"]

        edges = paused["edges"]

        matching_edges = []

        for e in edges:

            if (
                e["source"] == node["id"]
                and e.get("label") == "true"
            ):

                matching_edges.append(e)

        next_nodes = []

        for edge in matching_edges:

            target = next(
                (
                    n for n in nodes
                    if n["id"] == edge["target"]
                ),
                None
            )

            if target:
                next_nodes.append(target)

        await asyncio.gather(*[

            self.execute_node(
                n,
                nodes,
                edges,
                job_id
            )

            for n in next_nodes
        ])

        self.update_status(
            job_id,
            "running"
        )

        del self.paused_jobs[job_id]

     # ======================================================
    # RUNTIME SUPERVISOR
    # ======================================================
    async def runtime_supervisor_loop(self):

        from core.agents import (
            RuntimeSupervisorAgent
        )

        supervisor = RuntimeSupervisorAgent()

        while True:

            try:

                jobs = {

                    "queue_size":
                        self.queue.qsize(),

                    "workers":
                        self.max_workers
                }

                metrics = {

                    "active_jobs":
                        self.queue.qsize()
                }

                logs = "\n".join(
                    self.runtime_logs[-20:]
                )

                analysis = supervisor.analyze(

                    jobs,

                    metrics,

                    logs
                )

                print(
                    f"🧠 RUNTIME SUPERVISOR: {analysis}"
                )

                match = re.search(

                    r"\{.*\}",

                    analysis,

                    re.DOTALL
                )

                if match:

                    parsed = json.loads(
                        match.group(0)
                    )

                    action = parsed.get(
                        "action",
                        "none"
                    )

                    # ==========================
                    # SCALE UP
                    # ==========================
                    if action == "scale_up":

                        self.update_workers(
                            self.max_workers + 1
                        )

                    # ==========================
                    # PAUSE
                    # ==========================
                    elif action == "pause_jobs":

                        print(
                            "🛑 SUPERVISOR PAUSED JOBS"
                        )

                await asyncio.sleep(30)

            except Exception as e:

                print(
                    f"Supervisor error: {e}"
                )

                await asyncio.sleep(10)    

    # ======================================================
    # UPDATE WORKERS
    # ======================================================
    def update_workers(self, count):

        print(
            f"🔧 Updating workers: "
            f"{self.max_workers} → {count}"
        )

        self.max_workers = count

        print(
            f"✅ Workers activos: "
            f"{self.max_workers}"
        )


# ==========================================================
# GLOBAL INSTANCE
# ==========================================================
manager = JobManager()