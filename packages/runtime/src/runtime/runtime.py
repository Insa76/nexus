from __future__ import annotations

from core.kernel import Kernel

from planner.execution_context import ExecutionContext

from runtime.dispatcher import Dispatcher
from runtime.executor import Executor
from runtime.registry import Registry
from runtime.scheduler import Scheduler
from runtime.service_container import ServiceContainer
from runtime.execution_result import ExecutionResult

from actions.registry import ActionRegistry
from actions.manager import ActionManager

from providers.tool_registry import ToolRegistry


class Runtime:
    """
    Runtime principal de NEXUS.

    Es el orquestador del sistema.

    Su responsabilidad es coordinar los distintos
    componentes sin conocer sus implementaciones.

    Nunca contiene lógica de negocio.
    """

    def __init__(
        self,
        kernel: Kernel,
    ) -> None:

        self.kernel = kernel

        self.registry = Registry()

        self.container = ServiceContainer()

        self.scheduler = Scheduler()

        self.dispatcher = Dispatcher()

        #
        # Se inicializan en Bootstrap
        #

        self.action_registry: ActionRegistry | None = None

        self.action_manager: ActionManager | None = None

        self.tool_registry: ToolRegistry | None = None

        self.executor: Executor | None = None

    def configure_actions(
        self,
        registry: ActionRegistry,
        manager: ActionManager,
    ) -> None:
        """
        Configura el sistema de Actions.
        """

        self.action_registry = registry

        self.action_manager = manager

    def configure_tools(
        self,
        registry: ToolRegistry,
    ) -> None:
        """
        Configura el registro de herramientas.
        """

        self.tool_registry = registry

    def configure_executor(
        self,
        executor: Executor,
    ) -> None:
        """
        Configura el Executor.
        """

        self.executor = executor

    async def execute(
        self,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Ejecuta un plan completo.
        """

        if self.executor is None:

            raise RuntimeError(
                "Runtime executor has not been configured."
            )

        return await self.executor.execute(
            context
        )

    def register_module(
        self,
        name: str,
        module,
    ) -> None:

        self.registry.register(
            name,
            module,
        )

    def register_service(
        self,
        name: str,
        service,
    ) -> None:

        self.container.register(
            name,
            service,
        )
