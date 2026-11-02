from core.metrics import metrics
from core.self_model import self_model
import jobs.manager as manager_module


async def adjust_workers():

    snapshot = self_model.snapshot()
    health = self_model.health_score(snapshot)

    queue_size = snapshot["queue_size"]

    manager = manager_module.manager

    if not manager:
        return

    current = manager.max_workers

    # ======================
    # Escalar hacia arriba
    # ======================

    if queue_size > 5 and health > 70:

        new_workers = min(current + 1, 8)

        if new_workers != current:
            await manager.update_workers(new_workers)
            print(f"🚀 Workers aumentados a {new_workers}")

    # ======================
    # Escalar hacia abajo
    # ======================

    if queue_size == 0 and current > 2:

        new_workers = current - 1

        await manager.update_workers(new_workers)
        print(f"📉 Workers reducidos a {new_workers}")