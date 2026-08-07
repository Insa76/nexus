from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ObjectiveStatus(str, Enum):
    """
    Estado de un objetivo.
    """

    CREATED = "created"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Objective(BaseModel):
    """
    Representa un objetivo que NEXUS debe cumplir.
    """

    id: str

    title: str

    status: ObjectiveStatus = ObjectiveStatus.CREATED

    priority: int = 100

    metadata: dict = Field(default_factory=dict)