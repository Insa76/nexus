from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SemanticFact:
    """
    Representa una unidad de conocimiento semántico.

    Un hecho semántico no representa una ejecución concreta.
    Representa conocimiento que puede reutilizarse posteriormente.
    """

    subject: str
    predicate: str
    value: Any

    confidence: float = 1.0

    source: str = "system"

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class SemanticMemory:
    """
    Memoria semántica de NEXUS.

    Responsabilidades:

    - almacenar conocimiento estructurado
    - recuperar conocimiento por sujeto
    - recuperar conocimiento por sujeto y predicado
    - actualizar hechos existentes
    - eliminar conocimiento
    - consultar todos los hechos

    Esta capa NO:

    - interpreta lenguaje natural
    - consulta WorkingMemory
    - ejecuta acciones
    - decide si un hecho debe aprenderse
    - modifica el estado real del sistema
    """

    def __init__(self) -> None:
        self._facts: dict[
            tuple[str, str],
            SemanticFact,
        ] = {}

    #
    # ---------------------------------------------------------
    # WRITE
    # ---------------------------------------------------------
    #

    def learn(
        self,
        subject: str,
        predicate: str,
        value: Any,
        *,
        confidence: float = 1.0,
        source: str = "system",
        metadata: dict[str, Any] | None = None,
    ) -> SemanticFact:
        """
        Aprende un hecho semántico.

        Si ya existe un hecho para el mismo
        subject + predicate, se actualiza su valor.
        """

        subject = self._normalize(subject)
        predicate = self._normalize(predicate)

        if not subject:
            raise ValueError(
                "SemanticFact subject cannot be empty."
            )

        if not predicate:
            raise ValueError(
                "SemanticFact predicate cannot be empty."
            )

        confidence = self._normalize_confidence(
            confidence
        )

        key = (
            subject,
            predicate,
        )

        now = datetime.now(timezone.utc)

        existing = self._facts.get(key)

        if existing is not None:
            existing.value = value
            existing.confidence = confidence
            existing.source = source

            if metadata is not None:
                existing.metadata = dict(metadata)

            existing.updated_at = now

            return existing

        fact = SemanticFact(
            subject=subject,
            predicate=predicate,
            value=value,
            confidence=confidence,
            source=source,
            created_at=now,
            updated_at=now,
            metadata=dict(metadata or {}),
        )

        self._facts[key] = fact

        return fact

    #
    # ---------------------------------------------------------
    # READ
    # ---------------------------------------------------------
    #

    def get(
        self,
        subject: str,
        predicate: str,
    ) -> SemanticFact | None:
        """
        Recupera un hecho específico.
        """

        key = (
            self._normalize(subject),
            self._normalize(predicate),
        )

        return self._facts.get(key)

    def get_value(
        self,
        subject: str,
        predicate: str,
        default: Any = None,
    ) -> Any:
        """
        Recupera directamente el valor de un hecho.
        """

        fact = self.get(
            subject,
            predicate,
        )

        if fact is None:
            return default

        return fact.value

    def find_by_subject(
        self,
        subject: str,
    ) -> list[SemanticFact]:
        """
        Recupera todos los hechos asociados a un sujeto.
        """

        normalized_subject = self._normalize(
            subject
        )

        return [
            fact
            for fact in self._facts.values()
            if fact.subject == normalized_subject
        ]

    def find_by_predicate(
        self,
        predicate: str,
    ) -> list[SemanticFact]:
        """
        Recupera todos los hechos que utilizan
        un determinado predicado.
        """

        normalized_predicate = self._normalize(
            predicate
        )

        return [
            fact
            for fact in self._facts.values()
            if fact.predicate == normalized_predicate
        ]

    def all(self) -> list[SemanticFact]:
        """
        Devuelve todos los hechos conocidos.
        """

        return list(
            self._facts.values()
        )

    def count(self) -> int:
        """
        Devuelve la cantidad de hechos almacenados.
        """

        return len(self._facts)

    #
    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------
    #

    def forget(
        self,
        subject: str,
        predicate: str,
    ) -> bool:
        """
        Elimina un hecho específico.

        Devuelve True si existía.
        """

        key = (
            self._normalize(subject),
            self._normalize(predicate),
        )

        if key not in self._facts:
            return False

        del self._facts[key]

        return True

    def clear(self) -> None:
        """
        Elimina todo el conocimiento semántico.
        """

        self._facts.clear()

    #
    # ---------------------------------------------------------
    # INTERNAL
    # ---------------------------------------------------------
    #

    @staticmethod
    def _normalize(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError(
                "SemanticMemory values must be strings."
            )

        return " ".join(
            value.strip().lower().split()
        )

    @staticmethod
    def _normalize_confidence(
        confidence: float,
    ) -> float:
        try:
            confidence = float(
                confidence
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "SemanticFact confidence must be numeric."
            ) from exc

        return max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )
