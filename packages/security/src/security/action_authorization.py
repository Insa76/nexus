from __future__ import annotations

from dataclasses import dataclass

from security.action_policy_store import ActionPolicyStore
from security.authorization import AuthorizationService
from security.models import Actor


@dataclass(slots=True)
class ActionAuthorization:
    """Evalúa si un actor puede ejecutar una acción registrada."""

    policy_store: ActionPolicyStore
    authorization: AuthorizationService

    def is_allowed(
        self,
        actor: Actor,
        action_name: str,
    ) -> bool:
        policy = self.policy_store.get(action_name)

        if policy is None:
            return False

        return self.authorization.is_allowed(
            actor,
            policy.permission,
        )
