import time
from collections import defaultdict

from events.bus import bus
from brain.nexus_voice import speak


class CircuitBreaker:

    def __init__(self):
        self.failures = defaultdict(int)
        self.state = {}
        self.opened_at = {}

        self.threshold = 5
        self.cooldown_seconds = 30

    # --------------------------------------------------
    # INTERNAL KEY BUILDER
    # --------------------------------------------------

    def _key(self, workflow, tenant, workspace):
        return f"{workflow}:{tenant}:{workspace}"

    # --------------------------------------------------
    # CHECK STATE
    # --------------------------------------------------

    def is_open(self, workflow, tenant, workspace):

        key = self._key(workflow, tenant, workspace)
        state = self.state.get(key, "CLOSED")

        if state == "OPEN":

            opened = self.opened_at.get(key, 0)

            # cooldown para probar recuperación
            if time.time() - opened > self.cooldown_seconds:

                print(f"🟡 Circuit HALF_OPEN para {key}")

                self.state[key] = "HALF_OPEN"
                return False

            return True

        return False

    # --------------------------------------------------
    # FAILURE
    # --------------------------------------------------

    async def handle_failure(self, payload):

        workflow = payload["workflow"]
        tenant = payload.get("tenant_id", "default")
        workspace = payload.get("workspace_id", "main")

        key = self._key(workflow, tenant, workspace)

        self.failures[key] += 1

        if self.failures[key] >= self.threshold:

            self.state[key] = "OPEN"
            self.opened_at[key] = time.time()

            print(f"🔥 Circuit OPEN para {key}")

            await speak(
                f"He bloqueado temporalmente el workflow {workflow} por fallos repetidos.",
                "warning"
            )

            await bus.publish("circuit.opened", {
                "workflow": workflow,
                "tenant_id": tenant,
                "workspace_id": workspace
            })

    # --------------------------------------------------
    # SUCCESS
    # --------------------------------------------------

    async def handle_success(self, payload):

        workflow = payload["workflow"]
        tenant = payload.get("tenant_id", "default")
        workspace = payload.get("workspace_id", "main")

        key = self._key(workflow, tenant, workspace)

        if self.state.get(key) == "HALF_OPEN":

            self.state[key] = "CLOSED"
            self.failures[key] = 0

            print(f"🟢 Circuit CLOSED para {key}")

            await speak(
                f"He restaurado el funcionamiento normal del workflow {workflow}.",
                "info"
            )

            await bus.publish("circuit.closed", {
                "workflow": workflow,
                "tenant_id": tenant,
                "workspace_id": workspace
            })


circuit = CircuitBreaker()


def register_circuit():
    bus.subscribe("job.failed", circuit.handle_failure)
    bus.subscribe("job.done", circuit.handle_success)