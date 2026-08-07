from __future__ import annotations

import asyncio

from core.kernel import Kernel

from engine.engine import Engine

from runtime.runtime import Runtime
from runtime.executor import Executor

from actions.registry import ActionRegistry
from actions.manager import ActionManager


async def _bootstrap() -> None:

    print()

    print("=" * 50)
    print("          NEXUS Cognitive OS")
    print("=" * 50)
    print()

    #
    # Kernel
    #

    kernel = Kernel()

    print("✓ Kernel")

    #
    # Runtime
    #

    runtime = Runtime(
        kernel=kernel,
    )

    print("✓ Runtime")

    #
    # Actions
    #

    action_registry = ActionRegistry()

    action_manager = ActionManager(
        action_registry,
    )

    runtime.configure_actions(
        action_registry,
        action_manager,
    )

    print("✓ Actions")

    #
    # Executor
    #

    executor = Executor(
        runtime,
    )

    runtime.configure_executor(
        executor,
    )

    print("✓ Executor")

    #
    # Engine
    #

    engine = Engine(
        runtime,
    )

    print("✓ Engine")

    print()
    print("=" * 50)
    print("NEXUS READY")
    print("=" * 50)
    print()

    #
    # Próximamente:
    #
    # await engine.execute(...)
    #

    _ = engine


def main() -> None:

    asyncio.run(
        _bootstrap()
    )