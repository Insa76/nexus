import time
from datetime import datetime


class Metrics:

    def __init__(self):
        self.start_time = time.time()

        # contadores
        self.counters = {}

        # histogramas
        self.histograms = {}

        # gauges (estado actual)
        self.gauges = {}

        # métricas globales
        self.total_workflows = 0
        self.total_steps = 0
        self.total_jobs = 0
        self.total_errors = 0
        self.active_jobs = 0

    # =========================
    # COUNTERS
    # =========================

    def inc(self, name):
        self.counters[name] = self.counters.get(name, 0) + 1

    def inc_job(self):
        self.inc("jobs_created")
        self.total_jobs += 1

    def inc_error(self):
        self.inc("jobs_failed")
        self.total_errors += 1

    # =========================
    # HISTOGRAMS
    # =========================

    def observe(self, name, value):
        if name not in self.histograms:
            self.histograms[name] = []

        self.histograms[name].append(value)

    # =========================
    # GAUGES
    # =========================

    def set_active_jobs(self, value):
        self.active_jobs = value
        self.gauges["active_jobs"] = value

    def set_gauge(self, name, value):
        self.gauges[name] = value

    # =========================
    # WORKFLOW METRICS
    # =========================

    def inc_workflow(self):
        self.total_workflows += 1

    def inc_step(self):
        self.total_steps += 1

    # =========================
    # UPTIME
    # =========================

    def uptime(self):
        return round(time.time() - self.start_time)

    # =========================
    # SNAPSHOT
    # =========================

    def snapshot(self):

        return {
            "uptime_seconds": self.uptime(),
            "total_workflows_executed": self.total_workflows,
            "total_steps_executed": self.total_steps,
            "total_jobs_created": self.total_jobs,
            "total_errors": self.total_errors,
            "active_jobs": self.active_jobs,
            "timestamp": datetime.utcnow().isoformat()
        }

    # =========================
    # CONCURRENCY INFO
    # =========================

    def concurrency_info(self, queue_size, workers):

        return {
            "queue_size": queue_size,
            "max_workers": workers
        }


metrics = Metrics()