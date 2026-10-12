from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from planner.intent import Intent


@dataclass(frozen=True)
class Decision:
    """
    Resultado de la evaluación cognitiva de una intención.

    Decision no ejecuta acciones ni crea planes.
    Su responsabilidad es determinar qué debería hacerse
    a partir de la intención y el contexto disponible.
    """

    decision_id: str
    intent: Intent
    selected_action: str | None
    confidence: float
    reason: str
    requires_execution: bool
    alternatives: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_executable(self) -> bool:
        return self.requires_execution and self.selected_action is not None


class DecisionEngine:
    """
    Capa determinista de decisión cognitiva de V1.

    Responsabilidades:
    - evaluar una intención
    - determinar si puede ejecutarse
    - seleccionar la acción correspondiente
    - producir una justificación
    - conservar trazabilidad

    No ejecuta acciones.
    No crea planes.
    No modifica memoria.
    No consulta servicios externos.
    """

    UNKNOWN_ACTION = "system.unknown"

    def decide(
        self,
        intent: Intent,
        context: dict[str, Any] | None = None,
        capabilities: list[dict[str, Any]] | None = None,
    ) -> Decision:
        context = context or {}
        capabilities = capabilities or []

        if intent.action == self.UNKNOWN_ACTION:
            return self._unknown_decision(intent)

        if intent.is_compound:
            return self._compound_decision(
                intent=intent,
                context=context,
                capabilities=capabilities,
            )

        if not self._action_is_available(intent.action, capabilities):
            return Decision(
                decision_id=self._decision_id(intent),
                intent=intent,
                selected_action=None,
                confidence=0.0,
                reason=(
                    f"La intención {intent.action} fue reconocida, "
                    "pero no existe una capacidad disponible para ejecutarla."
                ),
                requires_execution=False,
                metadata={
                    "status": "unavailable",
                    "action": intent.action,
                },
            )

        return Decision(
            decision_id=self._decision_id(intent),
            intent=intent,
            selected_action=intent.action,
            confidence=max(0.0, min(1.0, intent.confidence)),
            reason=(
                f"La intención reconocida es {intent.action} "
                "y existe una capacidad disponible para ejecutarla."
            ),
            requires_execution=True,
            metadata={
                "status": "selected",
                "action": intent.action,
                "context_available": bool(context),
            },
        )

    def _unknown_decision(self, intent: Intent) -> Decision:
        return Decision(
            decision_id=self._decision_id(intent),
            intent=intent,
            selected_action=None,
            confidence=0.0,
            reason="No se pudo determinar una acción ejecutable.",
            requires_execution=False,
            metadata={
                "status": "unknown",
                "action": self.UNKNOWN_ACTION,
            },
        )

    def _compound_decision(
        self,
        intent: Intent,
        context: dict[str, Any],
        capabilities: list[dict[str, Any]],
    ) -> Decision:
        executable_actions: list[str] = []

        for sub_intent in intent.sub_intents:
            if (
                sub_intent.action != self.UNKNOWN_ACTION
                and self._action_is_available(
                    sub_intent.action,
                    capabilities,
                )
            ):
                executable_actions.append(sub_intent.action)

        if not executable_actions:
            return Decision(
                decision_id=self._decision_id(intent),
                intent=intent,
                selected_action=None,
                confidence=0.0,
                reason=(
                    "La intención compuesta fue reconocida, "
                    "pero ninguna de sus acciones tiene una capacidad disponible."
                ),
                requires_execution=False,
                alternatives=[],
                metadata={
                    "status": "unavailable",
                    "compound": True,
                    "actions": [
                        sub_intent.action
                        for sub_intent in intent.sub_intents
                    ],
                    "context_available": bool(context),
                },
            )

        return Decision(
            decision_id=self._decision_id(intent),
            intent=intent,
            selected_action=executable_actions[0],
            confidence=max(0.0, min(1.0, intent.confidence)),
            reason=(
                "La intención compuesta contiene acciones ejecutables; "
                "la primera acción disponible fue seleccionada como punto de entrada."
            ),
            requires_execution=True,
            alternatives=executable_actions[1:],
            metadata={
                "status": "selected",
                "compound": True,
                "actions": executable_actions,
                "context_available": bool(context),
            },
        )

    @staticmethod
    def _action_is_available(
        action: str,
        capabilities: list[dict[str, Any]],
    ) -> bool:
        if not capabilities:
            return True

        for capability in capabilities:
            if not isinstance(capability, dict):
                continue

            if capability.get("action") == action:
                return True

        return False

    @staticmethod
    def _decision_id(intent: Intent) -> str:
        source = intent.original_text or intent.action
        return f"decision-{abs(hash(source))}"
