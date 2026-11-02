from __future__ import annotations
import re
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
        """Calcula relevancia mediante frases y términos compartidos."""

        subject = SemanticRetriever._normalize(fact.subject)
        predicate = SemanticRetriever._normalize(fact.predicate)
        value = SemanticRetriever._normalize(str(fact.value))

        # Conservar el comportamiento existente para coincidencias directas.
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

        # Solo aplicar coincidencia por términos si la búsqueda directa
        # no encontró nada.
        if score > 0:
            return score

        stopwords = {
            "que", "qué", "recordas", "recordás", "recuerdas",
            "sobre", "el", "la", "los", "las", "de", "del",
            "un", "una", "unos", "unas", "me", "lo", "por",
            "favor", "acerca", "contame", "decime",
        }

        query_tokens = {
            token
            for token in re.findall(r"[a-záéíóúüñ0-9]+", query)
            if token not in stopwords
        }

        if not query_tokens:
            return 0.0

        subject_tokens = set(
            re.findall(r"[a-záéíóúüñ0-9]+", subject)
        )
        predicate_tokens = set(
            re.findall(r"[a-záéíóúüñ0-9]+", predicate)
        )
        value_tokens = set(
            re.findall(r"[a-záéíóúüñ0-9]+", value)
        )

        matched_subject = query_tokens & subject_tokens
        matched_predicate = query_tokens & predicate_tokens
        matched_value = query_tokens & value_tokens

        matched_tokens = (
            matched_subject | matched_predicate | matched_value
        )

        if not matched_tokens:
            return 0.0

        coverage = len(matched_tokens) / len(query_tokens)

        return (
            0.4 * coverage
            + 0.2 * bool(matched_subject)
            + 0.2 * bool(matched_predicate)
            + 0.2 * bool(matched_value)
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(
            value.strip().lower().split()
        )

