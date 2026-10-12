from __future__ import annotations

from dataclasses import dataclass

from memory.semantic_memory import SemanticFact, SemanticMemory


@dataclass(frozen=True)
class SemanticMatch:
    """
    Resultado de una recuperación semántica.

    score:
        Relevancia calculada para la consulta.
    """

    fact: SemanticFact
    score: float


class SemanticRetriever:
    """
    Recupera conocimiento desde SemanticMemory.

    Esta capa NO:
    - modifica memoria
    - aprende hechos
    - ejecuta acciones
    - consulta el sistema
    - interpreta lenguaje natural complejo

    Solamente recupera y ordena conocimiento existente.
    """

    def __init__(
        self,
        semantic_memory: SemanticMemory,
    ) -> None:
        self._semantic_memory = semantic_memory

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> list[SemanticMatch]:
        """
        Busca hechos relacionados con una consulta.

        La recuperación utiliza coincidencias simples
        sobre subject, predicate y value textual.
        """

        query = self._normalize(query)

        if not query:
            return []

        if limit <= 0:
            return []

        matches: list[SemanticMatch] = []

        for fact in self._semantic_memory.all():
            score = self._score(
                fact,
                query,
            )

            if score <= 0:
                continue

            matches.append(
                SemanticMatch(
                    fact=fact,
                    score=score,
                )
            )

        matches.sort(
            key=lambda match: (
                -match.score,
                -match.fact.confidence,
                match.fact.subject,
                match.fact.predicate,
            )
        )

        return matches[:limit]

    def search_by_subject(
        self,
        subject: str,
        *,
        limit: int = 10,
    ) -> list[SemanticMatch]:
        """
        Recupera conocimiento asociado a un sujeto.
        """

        subject = self._normalize(subject)

        if not subject or limit <= 0:
            return []

        facts = self._semantic_memory.find_by_subject(
            subject
        )

        matches = [
            SemanticMatch(
                fact=fact,
                score=1.0,
            )
            for fact in facts
        ]

        matches.sort(
            key=lambda match: (
                -match.fact.confidence,
                match.fact.predicate,
            )
        )

        return matches[:limit]

    def search_by_predicate(
        self,
        predicate: str,
        *,
        limit: int = 10,
    ) -> list[SemanticMatch]:
        """
        Recupera conocimiento asociado a un predicado.
        """

        predicate = self._normalize(predicate)

        if not predicate or limit <= 0:
            return []

        facts = self._semantic_memory.find_by_predicate(
            predicate
        )

        matches = [
            SemanticMatch(
                fact=fact,
                score=1.0,
            )
            for fact in facts
        ]

        matches.sort(
            key=lambda match: (
                -match.fact.confidence,
                match.fact.subject,
            )
        )

        return matches[:limit]

    @staticmethod
    def _score(
        fact: SemanticFact,
        query: str,
    ) -> float:
        """
        Calcula relevancia básica.

        Prioridad:
        - coincidencia exacta de subject
        - coincidencia exacta de predicate
        - coincidencia exacta del valor textual
        - coincidencias parciales
        """

        subject = SemanticRetriever._normalize(
            fact.subject
        )

        predicate = SemanticRetriever._normalize(
            fact.predicate
        )

        value = SemanticRetriever._normalize(
            str(fact.value)
        )

        score = 0.0

        if query == subject:
            score += 1.0

        if query == predicate:
            score += 0.9

        if query == value:
            score += 0.8

        if query in subject:
            score += 0.6

        if query in predicate:
            score += 0.5

        if query in value:
            score += 0.4

        return score

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(
            value.strip().lower().split()
        )
