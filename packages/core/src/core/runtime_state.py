from pydantic import BaseModel, Field


class RuntimeState(BaseModel):
    """
    Estado global del Kernel.

    Este objeto representa únicamente el estado operativo
    del Runtime. No contiene lógica.
    """

    online: bool = True

    connected_clients: int = 0

    active_agents: list[str] = Field(default_factory=list)

    current_model: str = "NEXUS Core"

    kernel_version: str = "0.1.0"