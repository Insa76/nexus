from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from uuid import uuid4


@dataclass(slots=True)
class Event:

    type: str

    source: str

    payload: dict

    priority: int = 100

    id: str = field(

        default_factory=lambda: str(uuid4())

    )

    timestamp: datetime = field(

        default_factory=datetime.utcnow

    )