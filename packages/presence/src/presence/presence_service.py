from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any


class PresenceService:
    """
    Capa de observación de NEXUS.

    Convierte el estado observable de WorkingMemory
    en un modelo de presencia apto para consumidores
    externos como Console o JARVIS.

    IMPORTANTE:
    - No ejecuta acciones.
    - No modifica el Engine.
    - No contiene lógica cognitiva.
    - No expone chain-of-thought.
    """

    def __init__(self, memory) -> None:
        self._memory = memory

    def snapshot(self) -> dict[str, Any]:
        """
        Devuelve el estado observable actual de NEXUS.
        """

        entries = self._memory.all()

        request = self._latest_data(
            entries,
            "user_request",
        )

        context = self._latest_data(
            entries,
            "cognitive_context",
        )

        intent = self._latest_data(
            entries,
            "intent",
        )

        decision = self._latest_data(
            entries,
            "decision",
        )

        objective = self._latest_data(
            entries,
            "objective",
        )

        plan = self._latest_data(
            entries,
            "plan_final",
        )

        if plan is None:
            plan = self._latest_data(
                entries,
                "plan",
            )

        execution_result = self._latest_data(
            entries,
            "execution_result",
        )

        verification = self._latest_data(
            entries,
            "verification",
        )

        state = self._resolve_state(
            intent=intent,
            decision=decision,
            execution_result=execution_result,
            verification=verification,
        )

        return {
            "state": state,
            "request": self._build_request(request),
            "context": self._safe_value(context),
            "intent": self._build_intent(intent),
            "decision": self._build_decision(decision),
            "objective": self._build_objective(objective),
            "plan": self._build_plan(plan),
            "execution": self._build_execution(
                execution_result,
                intent,
            ),
            "verification": self._build_verification(
                verification,
            ),
            "memory": self._build_memory(
                entries,
            ),
            "learning": self._build_learning(
                entries,
            ),
            "events": self._build_events(
                entries,
            ),
        }

    # ---------------------------------------------------------
    # STATE
    # ---------------------------------------------------------

    def _resolve_state(
        self,
        *,
        intent: dict[str, Any] | None,
        decision: dict[str, Any] | None,
        execution_result: dict[str, Any] | None,
        verification: dict[str, Any] | None,
    ) -> str:

        if not intent:
            return "idle"

        if not decision:
            return "understanding"

        if not decision.get(
            "requires_execution",
            False,
        ):
            return "needs_confirmation"

        if not execution_result:
            return "executing"

        if not execution_result.get(
            "success",
            False,
        ):
            return "failed"

        if not verification:
            return "verifying"

        if not verification.get(
            "verified",
            False,
        ):
            return "failed"

        return "completed"

    # ---------------------------------------------------------
    # REQUEST
    # ---------------------------------------------------------

    def _build_request(
        self,
        data: dict[str, Any] | None,
    ) -> dict[str, Any] | None:

        if data is None:
            return None

        return {
            "text": data.get(
                "text",
                "",
            ),
        }

    # ---------------------------------------------------------
    # INTENT
    # ---------------------------------------------------------

    def _build_intent(
        self,
        data: dict[str, Any] | None,
    ) -> dict[str, Any] | None:

        if data is None:
            return None

        return {
            "name": data.get(
                "action",
                "unknown",
            ),
            "confidence": data.get(
                "confidence",
                0.0,
            ),
        }

    # ---------------------------------------------------------
    # DECISION
    # ---------------------------------------------------------

    def _build_decision(
        self,
        data: dict[str, Any] | None,
    ) -> dict[str, Any] | None:

        if data is None:
            return None

        requires_execution = data.get(
            "requires_execution",
            False,
        )

        if requires_execution:
            decision_type = "execute"
        else:
            decision_type = "none"

        return {
            "type": decision_type,
            "reason": data.get(
                "reason",
            ),
        }

    # ---------------------------------------------------------
    # OBJECTIVE
    # ---------------------------------------------------------

    def _build_objective(
        self,
        data: dict[str, Any] | None,
    ) -> dict[str, Any] | None:

        if data is None:
            return None

        description = (
            data.get("description")
            or data.get("title")
            or data.get("action")
            or data.get("name")
        )

        if description is None:
            metadata = data.get(
                "metadata",
            )

            if isinstance(
                metadata,
                dict,
            ):
                application = metadata.get(
                    "application",
                )

                original_text = metadata.get(
                    "original_text",
                )

                if original_text:
                    description = original_text
                elif application:
                    description = (
                        f"Execute action for "
                        f"{application}"
                    )

        if description is None:
            description = str(data)

        return {
            "description": str(
                description
            ),
        }

    # ---------------------------------------------------------
    # PLAN
    # ---------------------------------------------------------

    def _build_plan(
        self,
        data: dict[str, Any] | None,
    ) -> dict[str, Any] | None:

        if data is None:
            return None

        steps = data.get(
            "steps",
            [],
        )

        normalized_steps = []

        for index, step in enumerate(
            steps
        ):

            if not isinstance(
                step,
                dict,
            ):
                continue

            status = step.get(
                "status",
                "pending",
            )

            status = self._enum_value(
                status,
                "pending",
            )

            action = step.get(
                "action"
            )

            if action is None:
                action = step.get(
                    "name",
                    "unknown",
                )

            normalized_steps.append(
                {
                    "id": step.get(
                        "id",
                        f"step-{index + 1}",
                    ),
                    "action": str(
                        action
                    ),
                    "status": status,
                    "description": (
                        str(
                            step["description"]
                        )
                        if step.get(
                            "description"
                        ) is not None
                        else None
                    ),
                }
            )

        return {
            "steps": normalized_steps,
        }

    # ---------------------------------------------------------
    # EXECUTION
    # ---------------------------------------------------------

    def _build_execution(
        self,
        data: dict[str, Any] | None,
        intent: dict[str, Any] | None,
    ) -> dict[str, Any] | None:

        if data is None:
            return None

        return {
            "status": (
                "completed"
                if data.get("success")
                else "failed"
            ),
            "action": (
                intent.get("action")
                if intent
                else None
            ),
            "result": self._safe_value(
                data.get("output")
            ),
            "error": (
                data.get("message")
                if not data.get("success")
                else None
            ),
        }

    # ---------------------------------------------------------
    # VERIFICATION
    # ---------------------------------------------------------

    def _build_verification(
        self,
        data: dict[str, Any] | None,
    ) -> dict[str, Any] | None:

        if data is None:
            return None

        verified = data.get(
            "verified",
            False,
        )

        confidence = data.get(
            "confidence",
        )

        if verified:
            if (
                isinstance(
                    confidence,
                    (int, float),
                )
                and confidence < 1.0
            ):
                status = (
                    "verified_with_limited_evidence"
                )
            else:
                status = "verified"
        else:
            status = "failed"

        return {
            "status": status,
            "confidence": confidence,
            "message": data.get(
                "reason",
            ),
        }

    # ---------------------------------------------------------
    # MEMORY
    # ---------------------------------------------------------

    def _build_memory(
        self,
        entries: list,
    ) -> dict[str, Any]:

        has_episode = any(
            entry.type == "episode"
            for entry in entries
        )

        return {
            "status": (
                "stored"
                if has_episode
                else "pending"
            ),
            "entries": len(entries),
        }

    # ---------------------------------------------------------
    # LEARNING
    # ---------------------------------------------------------

    def _build_learning(
        self,
        entries: list,
    ) -> dict[str, Any]:

        has_episode = any(
            entry.type == "episode"
            for entry in entries
        )

        return {
            "status": (
                "learned"
                if has_episode
                else "pending"
            ),
            "message": (
                "Execution experience available "
                "for future reuse."
                if has_episode
                else None
            ),
        }

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------

    def _build_events(
        self,
        entries: list,
    ) -> list[dict[str, Any]]:

        events = []

        for entry in entries:

            timestamp = getattr(
                entry,
                "timestamp",
                None,
            )

            if isinstance(
                timestamp,
                datetime,
            ):
                timestamp_value = (
                    timestamp.isoformat()
                )
            else:
                timestamp_value = str(
                    timestamp
                )

            events.append(
                {
                    "id": str(
                        entry.id
                    ),
                    "type": entry.type,
                    "timestamp": timestamp_value,
                    "message": self._event_message(
                        entry.type,
                        entry.data,
                    ),
                    "data": self._safe_value(
                        entry.data
                    ),
                }
            )

        return events

    def _event_message(
        self,
        event_type: str,
        data: Any,
    ) -> str:

        messages = {
            "user_request": "Request received.",
            "cognitive_context": "Context recovered.",
            "intent": "Intent resolved.",
            "decision": "Decision generated.",
            "objective": "Objective created.",
            "plan": "Plan generated.",
            "plan_final": "Final plan state recorded.",
            "verification": "Execution verified.",
            "execution_result": "Execution result recorded.",
            "episode": "Episode stored.",
            "error": "Execution error recorded.",
            "verification_failure": "Verification failed.",
        }

        return messages.get(
            event_type,
            event_type.replace(
                "_",
                " ",
            ).capitalize()
            + ".",
        )

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _latest_data(
        entries: list,
        entry_type: str,
    ) -> dict[str, Any] | None:

        for entry in reversed(entries):

            if entry.type == entry_type:
                return entry.data

        return None

    @staticmethod
    def _enum_value(
        value: Any,
        default: str,
    ) -> str:

        if isinstance(
            value,
            Enum,
        ):
            return str(
                value.value
            )

        if value is None:
            return default

        return str(value)

    @classmethod
    def _safe_value(
        cls,
        value: Any,
    ) -> Any:

        if value is None:
            return None

        if isinstance(
            value,
            Enum,
        ):
            return value.value

        if isinstance(
            value,
            (str, int, float, bool),
        ):
            return value

        if isinstance(
            value,
            datetime,
        ):
            return value.isoformat()

        if isinstance(
            value,
            dict,
        ):
            return {
                str(key): cls._safe_value(
                    item
                )
                for key, item in value.items()
            }

        if isinstance(
            value,
            (list, tuple, set),
        ):
            return [
                cls._safe_value(item)
                for item in value
            ]

        model_dump = getattr(
            value,
            "model_dump",
            None,
        )

        if callable(model_dump):
            try:
                return cls._safe_value(
                    model_dump()
                )
            except Exception:
                pass

        return str(value)
