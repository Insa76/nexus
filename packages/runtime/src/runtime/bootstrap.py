from __future__ import annotations

from packages.core.src.core.kernel import Kernel

from packages.runtime.src.runtime.runtime import Runtime

from packages.actions.src.actions.registry import CapabilityRegistry
from packages.actions.src.actions.manager import CapabilityManager

from packages.actions.src.actions.echo import EchoCapability
from packages.actions.src.actions.open_app import OpenAppCapability
from packages.runtime.src.runtime.executor import Executor


class Bootstrap:
    """
    Inicializa todos los componentes principales
    del Runtime.
    """

    def build(self) -> Runtime:

        kernel = Kernel()

        runtime = Runtime(
            kernel=kernel,
        )

        #
        # Capability Registry
        #

        registry = CapabilityRegistry()

        registry.register(
            EchoCapability()
        )

        registry.register(
            OpenAppCapability()
        )

        manager = CapabilityManager(
            registry
        )

        executor = Executor(
          manager
        )

        runtime.configure_executor(
          executor
        )

        runtime.capability_registry = registry

        runtime.capability_manager = manager

        return runtime