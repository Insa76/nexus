from __future__ import annotations

from core.kernel import Kernel

from runtime.runtime import Runtime
from runtime.executor import Executor

from actions.registry import CapabilityRegistry
from actions.manager import CapabilityManager

from actions.echo import EchoCapability
from actions.open_app import OpenAppCapability

from providers.tool_registry import ToolRegistry


class Bootstrap:
    """
    Inicializa todos los componentes principales
    de NEXUS.
    """

    def build(self) -> Runtime:

        #
        # Kernel
        #

        kernel = Kernel()

        #
        # Runtime
        #

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

        #
        # Capability Manager
        #

        manager = CapabilityManager(
            registry
        )

        #
        # Configure Runtime
        #

        runtime.configure_capabilities(
            registry,
            manager,
        )

        #
        # Executor
        #

        executor = Executor(
            manager
        )

        runtime.configure_executor(
            executor
        )

        return runtime
