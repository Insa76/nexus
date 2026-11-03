from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from documents.cognitive import (
    DocumentCognitiveAccess,
    DocumentCognitiveResult,
)
from processes.cognitive import (
    ProcessCognitiveAccess,
    ProcessCognitiveResult,
)
from processes.models import Process
from rules.cognitive import (
    RuleCognitiveAccess,
    RuleCognitiveResult,
)
from rules.models import Rule
from tasks.cognitive import TaskCognitiveAccess, TaskCognitiveResult
from tasks.models import Task, TaskStatus


@dataclass(frozen=True, slots=True)
class CognitiveCapabilityContext:
    """
    Contexto disponible para una operación cognitiva.

    Mantiene la información de entrada separada de las
    implementaciones concretas de las capabilities.
    """

    context: object
    parameters: dict[str, Any]


@dataclass(frozen=True, slots=True)
class CognitiveCapabilityInvocation:
    """
    Representa una capability cognitiva seleccionada,
    pero todavía no ejecutada.
    """

    capability: str
    operation: str
    parameters: dict[str, Any]


@dataclass(frozen=True, slots=True)
class CognitiveCapabilityDescriptor:
    """
    Describe una capability cognitiva disponible.

    El descriptor permite separar:

    - qué capability existe
    - qué operación expone
    - qué acción puede seleccionarla

    No contiene implementación ni ejecuta nada.
    """

    capability: str
    operation: str
    action: str


@dataclass(frozen=True, slots=True)
class CognitiveCapabilityOperation:
    """
    Describe una operación cognitiva disponible.

    Representa la capacidad concreta que el Cognitive Core
    puede utilizar.
    """

    capability: str
    operation: str
    action: str


class CognitiveCapabilityRouter:
    """
    Punto de entrada para que el Cognitive Core utilice capabilities.

    No conoce stores ni detalles internos de Documents, Processes o Rules.
    """

    def __init__(
        self,
        *,
        document_access: DocumentCognitiveAccess | None = None,
        process_access: ProcessCognitiveAccess | None = None,
        rule_access: RuleCognitiveAccess | None = None,
        task_access: TaskCognitiveAccess | None = None,
    ) -> None:
        self._document_access = document_access
        self._process_access = process_access
        self._rule_access = rule_access
        self._task_access = task_access

    @property
    def document_access(self) -> DocumentCognitiveAccess | None:
        return self._document_access

    @property
    def process_access(self) -> ProcessCognitiveAccess | None:
        return self._process_access

    @property
    def rule_access(self) -> RuleCognitiveAccess | None:
        return self._rule_access

    @property
    def descriptors(self) -> tuple[CognitiveCapabilityDescriptor, ...]:
        """
        Devuelve las capabilities cognitivas actualmente disponibles.
        """

        descriptors: list[CognitiveCapabilityDescriptor] = []

        if self._document_access is not None:
            descriptors.append(
                CognitiveCapabilityDescriptor(
                    capability="documents",
                    operation="find_relevant",
                    action="documents.find_relevant",
                )
            )

        if self._process_access is not None:
            descriptors.extend(
                (
                    CognitiveCapabilityDescriptor(
                        capability="processes",
                        operation="find_relevant",
                        action="processes.find_relevant",
                    ),
                    CognitiveCapabilityDescriptor(
                        capability="processes",
                        operation="get",
                        action="processes.get",
                    ),
                    CognitiveCapabilityDescriptor(
                        capability="processes",
                        operation="list",
                        action="processes.list",
                    ),
                )
            )

        if self._rule_access is not None:
            descriptors.extend(
                (
                    CognitiveCapabilityDescriptor(
                        capability="rules",
                        operation="find_relevant",
                        action="rules.find_relevant",
                    ),
                    CognitiveCapabilityDescriptor(
                        capability="rules",
                        operation="get",
                        action="rules.get",
                    ),
                    CognitiveCapabilityDescriptor(
                        capability="rules",
                        operation="list",
                        action="rules.list",
                    ),
                )
            )

        if self._task_access is not None:
            descriptors.extend(
                (
                    CognitiveCapabilityDescriptor(
                        capability="tasks",
                        operation="find_relevant",
                        action="tasks.find_relevant",
                    ),
                    CognitiveCapabilityDescriptor(
                        capability="tasks",
                        operation="get",
                        action="tasks.get",
                    ),
                    CognitiveCapabilityDescriptor(
                        capability="tasks",
                        operation="list",
                        action="tasks.list",
                    ),
                    CognitiveCapabilityDescriptor(
                        capability="tasks",
                        operation="create",
                        action="tasks.create",
                    ),
                    CognitiveCapabilityDescriptor(
                        capability="tasks",
                        operation="update",
                        action="tasks.update",
                    ),
                    CognitiveCapabilityDescriptor(
                        capability="tasks",
                        operation="transition",
                        action="tasks.transition",
                    ),
                )
            )

        return tuple(descriptors)

    def available_capabilities(self) -> tuple[str, ...]:
        """
        Devuelve los identificadores de las capabilities cognitivas
        actualmente disponibles para el Cognitive Core.
        """

        return tuple(
            descriptor.capability
            for descriptor in self.descriptors
        )

    def available_operations(
        self,
    ) -> tuple[CognitiveCapabilityOperation, ...]:
        """
        Devuelve las operaciones cognitivas actualmente disponibles.
        """

        return tuple(
            CognitiveCapabilityOperation(
                capability=descriptor.capability,
                operation=descriptor.operation,
                action=descriptor.action,
            )
            for descriptor in self.descriptors
        )

    def find_operation(
        self,
        *,
        action: str,
    ) -> CognitiveCapabilityOperation | None:
        """
        Busca la operación cognitiva asociada a una acción.
        """

        for operation in self.available_operations():
            if operation.action == action:
                return operation

        return None

    @staticmethod
    def summarize_operation_result(
        result: (
            DocumentCognitiveResult
            | ProcessCognitiveResult
            | RuleCognitiveResult
            | TaskCognitiveResult
            | Task
            | tuple[Task, ...]
            | Process
            | tuple[Process, ...]
            | Rule
            | tuple[Rule, ...]
            | None
        ),
        *,
        operation: str,
    ) -> dict[str, Any]:
        if isinstance(result, DocumentCognitiveResult):
            count = len(result.documents)

            return {
                "operation": "documents.find_relevant",
                "result_count": count,
                "document_count": count,
                "query_count": len(result.query.documents),
                "has_results": count > 0,
                "status": "found" if count > 0 else "empty",
            }

        if isinstance(result, TaskCognitiveResult):
            count = len(result.tasks)
            return {
                "operation": "tasks.find_relevant",
                "result_count": count,
                "has_results": count > 0,
                "status": "found" if count > 0 else "empty",
            }

        if isinstance(result, ProcessCognitiveResult):
            count = len(result.processes)

            return {
                "operation": "processes.find_relevant",
                "result_count": count,
                "has_results": count > 0,
                "status": "found" if count > 0 else "empty",
            }

        if isinstance(result, RuleCognitiveResult):
            count = len(result.rules)

            return {
                "operation": "rules.find_relevant",
                "result_count": count,
                "has_results": count > 0,
                "status": "found" if count > 0 else "empty",
            }

        if operation == "tasks.get":
            count = 1 if isinstance(result, Task) else 0
            return {
                "operation": operation,
                "result_count": count,
                "has_results": count > 0,
                "status": "found" if count > 0 else "empty",
            }

        if operation == "tasks.list":
            if not isinstance(result, tuple) or (
                result and not all(isinstance(item, Task) for item in result)
            ):
                raise TypeError(f"Expected tuple[Task, ...] result for {operation}")
            count = len(result)
            return {
                "operation": operation,
                "result_count": count,
                "has_results": count > 0,
                "status": "found" if count > 0 else "empty",
            }

        if operation in {"tasks.create", "tasks.update", "tasks.transition"}:
            if not isinstance(result, Task):
                raise TypeError(f"Expected Task result for {operation}")
            return {
                "operation": operation,
                "result_count": 1,
                "has_results": True,
                "status": "completed",
                "task_id": result.id,
            }

        if operation == "processes.get":
            count = 1 if isinstance(result, Process) else 0

            return {
                "operation": operation,
                "result_count": count,
                "has_results": count > 0,
                "status": "found" if count > 0 else "empty",
            }

        if operation == "processes.list":
            if not isinstance(result, tuple):
                raise TypeError(
                    f"Expected tuple result for {operation}, "
                    f"got {type(result)!r}"
                )

            if result and not all(
                isinstance(item, Process)
                for item in result
            ):
                raise TypeError(
                    f"Expected tuple[Process, ...] result for {operation}, "
                    f"got {type(result)!r}"
                )

            count = len(result)

            return {
                "operation": operation,
                "result_count": count,
                "has_results": count > 0,
                "status": "found" if count > 0 else "empty",
            }

        if operation == "rules.get":
            count = 1 if isinstance(result, Rule) else 0

            return {
                "operation": operation,
                "result_count": count,
                "has_results": count > 0,
                "status": "found" if count > 0 else "empty",
            }

        if operation == "rules.list":
            if not isinstance(result, tuple):
                raise TypeError(
                    f"Expected tuple result for {operation}, "
                    f"got {type(result)!r}"
                )

            if result and not all(
                isinstance(item, Rule)
                for item in result
            ):
                raise TypeError(
                    f"Expected tuple[Rule, ...] result for {operation}, "
                    f"got {type(result)!r}"
                )

            count = len(result)

            return {
                "operation": operation,
                "result_count": count,
                "has_results": count > 0,
                "status": "found" if count > 0 else "empty",
            }

        raise TypeError(
            f"Unsupported cognitive capability result type: {type(result)!r}"
        )

    def find_relevant_documents(
        self,
        *,
        context: object,
        name: str | None = None,
        mime_type: str | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> DocumentCognitiveResult:
        if self._document_access is None:
            raise RuntimeError(
                "Document cognitive capability is not available."
            )

        return self._document_access.find_relevant(
            context=context,
            name=name,
            mime_type=mime_type,
            offset=offset,
            limit=limit,
        )

    def find_relevant_tasks(
        self,
        *,
        context: object,
    ) -> TaskCognitiveResult:
        if self._task_access is None:
            raise RuntimeError("Task cognitive capability is not available.")
        return self._task_access.find_relevant(context=context)

    def get_task(
        self,
        *,
        task_id: str,
        context: object,
    ) -> Task | None:
        if self._task_access is None:
            raise RuntimeError("Task cognitive capability is not available.")
        return self._task_access.get(task_id, context=context)

    def list_tasks(
        self,
        *,
        context: object,
    ) -> tuple[Task, ...]:
        if self._task_access is None:
            raise RuntimeError("Task cognitive capability is not available.")
        return self._task_access.list(context=context)

    def find_relevant_processes(
        self,
        *,
        context: object,
    ) -> ProcessCognitiveResult:
        if self._process_access is None:
            raise RuntimeError(
                "Process cognitive capability is not available."
            )

        return self._process_access.find_relevant(
            context=context,
        )

    def get_process(
        self,
        *,
        process_id: str,
    ) -> Process | None:
        if self._process_access is None:
            raise RuntimeError(
                "Process cognitive capability is not available."
            )

        return self._process_access.get(process_id)

    def list_processes(self) -> tuple[Process, ...]:
        if self._process_access is None:
            raise RuntimeError(
                "Process cognitive capability is not available."
            )

        return self._process_access.list()

    def find_relevant_rules(
        self,
        *,
        context: object,
    ) -> RuleCognitiveResult:
        if self._rule_access is None:
            raise RuntimeError(
                "Rule cognitive capability is not available."
            )

        return self._rule_access.find_relevant(
            context=context,
        )

    def get_rule(
        self,
        *,
        rule_id: str,
    ) -> Rule | None:
        if self._rule_access is None:
            raise RuntimeError(
                "Rule cognitive capability is not available."
            )

        return self._rule_access.get(rule_id)

    def list_rules(self) -> tuple[Rule, ...]:
        if self._rule_access is None:
            raise RuntimeError(
                "Rule cognitive capability is not available."
            )

        return self._rule_access.list()

    def select(
        self,
        *,
        action: str,
        parameters: dict[str, Any] | None = None,
    ) -> CognitiveCapabilityInvocation | None:
        """
        Determina si una intención corresponde a una
        capability cognitiva disponible.

        La selección no ejecuta ninguna operación.
        """

        parameters = parameters or {}

        for descriptor in self.descriptors:
            if descriptor.action != action:
                continue

            return CognitiveCapabilityInvocation(
                capability=descriptor.capability,
                operation=descriptor.operation,
                parameters=dict(parameters),
            )

        return None

    def invoke(
        self,
        invocation: CognitiveCapabilityInvocation,
        *,
        context: object,
        assistant_context: object | None = None,
    ) -> (
        DocumentCognitiveResult
        | ProcessCognitiveResult
        | RuleCognitiveResult
        | TaskCognitiveResult
        | Task
        | tuple[Task, ...]
        | Process
        | tuple[Process, ...]
        | Rule
        | tuple[Rule, ...]
        | None
    ):
        """
        Ejecuta la operación cognitiva previamente seleccionada.

        La invocación ocurre sobre el acceso cognitivo de la capability.
        No ejecuta acciones del Runtime.
        """

        if invocation.capability == "documents":
            if invocation.operation != "find_relevant":
                raise ValueError(
                    f"Unsupported documents operation: "
                    f"{invocation.operation}"
                )

            if self._document_access is None:
                raise RuntimeError(
                    "Document cognitive capability is not available."
                )


            return self._document_access.find_relevant(
    context=(
        assistant_context
        if assistant_context is not None
        else context
    ),
    name=invocation.parameters.get("name"),
    mime_type=invocation.parameters.get("mime_type"),
    offset=invocation.parameters.get("offset", 0),
    limit=invocation.parameters.get("limit"),
)

        if invocation.capability == "tasks":
            if self._task_access is None:
                raise RuntimeError("Task cognitive capability is not available.")

            if assistant_context is None:
                raise ValueError("tasks operations require 'assistant_context'.")

            if invocation.operation == "find_relevant":
                return self._task_access.find_relevant(context=assistant_context)

            if invocation.operation == "get":
                task_id = invocation.parameters.get("task_id")
                if not task_id:
                    raise ValueError("tasks.get requires 'task_id'.")
                return self._task_access.get(task_id, context=assistant_context)

            if invocation.operation == "list":
                return self._task_access.list(context=assistant_context)

            if invocation.operation == "create":
                title = invocation.parameters.get("title")
                if not isinstance(title, str) or not title.strip():
                    raise ValueError("tasks.create requires a non-empty 'title'.")
                return self._task_access.create(
                    context=assistant_context,
                    title=title,
                    description=invocation.parameters.get("description"),
                    priority=invocation.parameters.get("priority", "normal"),
                )

            if invocation.operation == "update":
                task_id = (
                    invocation.parameters.get("task_id")
                    or invocation.parameters.get("task_reference")
                )
                if not isinstance(task_id, str) or not task_id.strip():
                    raise ValueError("tasks.update requires 'task_id' or 'task_reference'.")
                return self._task_access.update(
                    task_id,
                    context=assistant_context,
                    title=invocation.parameters.get("title"),
                    description=invocation.parameters.get("description"),
                    priority=invocation.parameters.get("priority"),
                )

            if invocation.operation == "transition":
                task_id = (
                    invocation.parameters.get("task_id")
                    or invocation.parameters.get("task_reference")
                )
                target = invocation.parameters.get("target_status")
                if not isinstance(task_id, str) or not task_id.strip():
                    raise ValueError("tasks.transition requires 'task_id'.")
                try:
                    target_status = TaskStatus(target)
                except (ValueError, TypeError) as exc:
                    raise ValueError(
                        "target_status must be pending, in_progress, completed or cancelled."
                    ) from exc
                updated = self._task_access.transition(
                    task_id, target_status, context=assistant_context,
                )
                if updated is None:
                    raise ValueError("La tarea no existe en el proyecto activo.")
                return updated

            raise ValueError(f"Unsupported tasks operation: {invocation.operation}")

        if invocation.capability == "processes":
            if self._process_access is None:
                raise RuntimeError(
                    "Process cognitive capability is not available."
                )

            if invocation.operation == "find_relevant":
                if assistant_context is None:
                    raise ValueError(
                        "processes.find_relevant requires 'assistant_context'."
                    )

                return self._process_access.find_relevant(
                    context=assistant_context,
                )

            if invocation.operation == "get":
                process_id = invocation.parameters.get("process_id")

                if not process_id:
                    raise ValueError(
                        "processes.get requires 'process_id'."
                    )

                if assistant_context is None:
                    raise ValueError(
                        "processes.get requires 'assistant_context'."
                    )

                return self._process_access.get(
                    process_id,
                    context=assistant_context,
                )

            if invocation.operation == "list":
                if assistant_context is None:
                    raise ValueError(
                        "processes.list requires 'assistant_context'."
                    )

                return self._process_access.list(
                    context=assistant_context,
                )

            raise ValueError(
                f"Unsupported processes operation: "
                f"{invocation.operation}"
            )


        if invocation.capability == "rules":
            if self._rule_access is None:
                raise RuntimeError(
                    "Rule cognitive capability is not available."
                )

            if invocation.operation == "find_relevant":
                if assistant_context is None:
                    raise ValueError(
                        "rules.find_relevant requires 'assistant_context'."
                    )

                return self._rule_access.find_relevant(
                    context=assistant_context,
                )

            if invocation.operation == "get":
                rule_id = invocation.parameters.get("rule_id")

                if not rule_id:
                    raise ValueError(
                        "rules.get requires 'rule_id'."
                    )

                if assistant_context is None:
                    raise ValueError(
                        "rules.get requires 'assistant_context'."
                    )

                return self._rule_access.get(
                    rule_id,
                    context=assistant_context,
                )

            if invocation.operation == "list":
                if assistant_context is None:
                    raise ValueError(
                        "rules.list requires 'assistant_context'."
                    )

                return self._rule_access.list(
                    context=assistant_context,
                )

        raise ValueError(
            f"Unsupported cognitive capability: "
            f"{invocation.capability}"
        )
