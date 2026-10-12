from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Tool(BaseModel):
    """
    Describe una herramienta ejecutable por NEXUS.

    Una herramienta puede declarar los artifacts que
    produce y consume para permitir que el Planner
    construya relaciones entre pasos sin conocer
    la implementación concreta.
    """

    name: str

    description: str

    provider: str

    action: str | None = None

    parameters: dict[str, Any] = Field(
        default_factory=dict
    )

    produces: list[str] = Field(
        default_factory=list
    )

    consumes: list[str] = Field(
        default_factory=list
    )
