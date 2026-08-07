from enum import Enum


class ObjectiveStatus(str, Enum):

    CREATED = "created"

    PLANNING = "planning"

    READY = "ready"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"