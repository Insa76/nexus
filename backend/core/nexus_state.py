from resilience.circuit import circuit
from jobs import manager as manager_module

class NexusState:

    def __init__(self):
        self.mode = "efficient"

    def apply_mode(self, mode):

        self.mode = mode

        if mode == "stable":
            circuit.threshold = 3
            circuit.cooldown_seconds = 45
            manager_module.manager.semaphore = manager_module.asyncio.Semaphore(2)

        elif mode == "efficient":
            circuit.threshold = 5
            circuit.cooldown_seconds = 30
            manager_module.manager.semaphore = manager_module.asyncio.Semaphore(4)

        elif mode == "aggressive":
            circuit.threshold = 8
            circuit.cooldown_seconds = 15
            manager_module.manager.semaphore = manager_module.asyncio.Semaphore(8)

nexus_state = NexusState()