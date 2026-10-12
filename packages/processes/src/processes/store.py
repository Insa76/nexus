from __future__ import annotations

from processes.models import Process


class ProcessStore:
    """In-memory store for assistant processes."""

    def __init__(self) -> None:
        self._processes: dict[str, Process] = {}

    def add(self, process: Process) -> Process:
        self._processes[process.id] = process
        return process

    def get(self, process_id: str) -> Process | None:
        return self._processes.get(process_id)

    def list(self) -> list[Process]:
        return list(self._processes.values())

    def update(self, process: Process) -> Process:
        if process.id not in self._processes:
            raise KeyError(
                f"Process not found: {process.id}"
            )

        self._processes[process.id] = process
        return process

    def remove(self, process_id: str) -> Process | None:
        return self._processes.pop(process_id, None)

    def clear(self) -> None:
        self._processes.clear()

    def count(self) -> int:
        return len(self._processes)
