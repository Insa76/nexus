from __future__ import annotations
from actions.base import Action
from planner.execution_context import ExecutionContext
from planner.plan import PlanStep
from providers.provider_manager import ProviderManager

class OpenFileAction(Action):
    """Abre un archivo existente con la aplicación predeterminada."""
    name = "system.open_file"
    description = "Busca y abre un archivo en una carpeta personal autorizada."
    parameters = {
        "file_name": {"type": "string", "required": True, "description": "Nombre del archivo, sin ruta."},
        "location": {"type": "string", "required": True, "description": "desktop, documents o downloads."},
        "extension": {"type": "string", "required": False, "description": "Extensión opcional."},
    }

    def __init__(self, provider_manager: ProviderManager) -> None:
        self._provider_manager = provider_manager

    async def execute(self, context: ExecutionContext, step: PlanStep) -> None:
        file_name = step.metadata.get("file_name")
        location = step.metadata.get("location", "desktop")
        extension = step.metadata.get("extension")
        if not isinstance(file_name, str) or not file_name.strip():
            context.add_error("No se especificó el nombre del archivo.")
            return
        try:
            success = await self._provider_manager.execute(
                provider="local", tool="windows.open_file",
                parameters={"file_name": file_name, "location": location, "extension": extension},
            )
        except Exception as exc:
            context.add_error(f"No se pudo abrir el archivo '{file_name}': {exc}")
            return
        if not success:
            context.add_error(
                f"No se encontró una coincidencia única para '{file_name}' "
                f"en '{location}', o Windows no pudo abrirla."
            )
            return
        context.add_result("file_name", file_name)
        context.add_result("location", location)
        context.add_result("status", "opened")
