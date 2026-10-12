from __future__ import annotations

from actions.base import Action

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from providers.provider_manager import ProviderManager


class ScreenCaptureAction(Action):
    """
    Action para capturar la pantalla.

    Produce el artifact `image`.
    """

    name = "system.screen_capture"

    description = (
        "Captura la pantalla actual."
    )

    produces = [
        "image",
    ]

    def __init__(
        self,
        provider_manager: ProviderManager,
    ) -> None:

        self._provider_manager = provider_manager

    async def execute(
        self,
        context: ExecutionContext,
        step: PlanStep,
    ) -> None:

        try:

            image = await self._provider_manager.execute(
                provider="local",
                tool="windows.capture_screen",
                parameters={},
            )

        except Exception as exc:

            context.add_error(
                f"Failed to capture screen: {exc}"
            )

            return

        path = step.metadata.get(
            "path"
        )

        if path:

            image.save(path)

            context.add_result(
                "path",
                path,
            )

        #
        # La imagen es un artifact.
        #

        context.add_artifact(
            "image",
            image,
        )

        context.add_result(
            "status",
            "captured",
        )
