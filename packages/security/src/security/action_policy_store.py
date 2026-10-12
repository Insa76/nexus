from __future__ import annotations

from dataclasses import dataclass, field

from security.action_policy import ActionPolicy


@dataclass(slots=True)
class ActionPolicyStore:
    """Registro de políticas de autorización por acción."""

    _policies: dict[str, ActionPolicy] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def register(self, policy: ActionPolicy) -> None:
        if policy.action_name in self._policies:
            raise ValueError(
                f"Action policy already registered: {policy.action_name}"
            )

        self._policies[policy.action_name] = policy

    def get(self, action_name: str) -> ActionPolicy | None:
        return self._policies.get(action_name)

    def list(self) -> tuple[ActionPolicy, ...]:
        return tuple(self._policies.values())

    def remove(self, action_name: str) -> bool:
        return self._policies.pop(action_name, None) is not None
