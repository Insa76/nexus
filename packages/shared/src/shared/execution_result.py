from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ExecutionResult:

    success: bool = True

    data: dict = field(default_factory=dict)

    errors: list[str] = field(default_factory=list)

    def add(

        self,

        key: str,

        value,

    ):

        self.data[key] = value

    def fail(

        self,

        message: str,

    ):

        self.success = False

        self.errors.append(message)