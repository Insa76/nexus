from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EpisodeQuery:
    action: str
    field: str
    source: str = "episode_query"


class EpisodeQueryResolver:
    """
    Detecta consultas explícitas sobre acciones registradas
    en memoria episódica.

    No consulta memoria.
    No ejecuta acciones.
    Solamente determina qué episodio debe consultarse
    y qué campo interesa recuperar.
    """

    def resolve(
        self,
        text: str,
    ) -> EpisodeQuery | None:

        normalized = self._normalize(text)

        #
        # Última aplicación abierta
        #
        if normalized in {
            "qué aplicación abrí",
            "que aplicación abrí",
            "qué aplicacion abrí",
            "que aplicacion abrí",
            "qué app abrí",
            "que app abrí",
        }:
            return EpisodeQuery(
                action="system.open_app",
                field="application",
            )

        #
        # Última aplicación cerrada
        #
        if normalized in {
            "qué aplicación cerré",
            "que aplicación cerré",
            "qué aplicacion cerré",
            "que aplicacion cerré",
            "qué app cerré",
            "que app cerré",
        }:
            return EpisodeQuery(
                action="system.close_app",
                field="application",
            )

        #
        # Último volumen establecido
        #
        if normalized in {
            "qué volumen puse",
            "que volumen puse",
            "qué volumen dejé",
            "que volumen dejé",
            "qué volumen configure",
            "que volumen configure",
        }:
            return EpisodeQuery(
                action="system.set_volume",
                field="level",
            )

        #
        # Última captura
        #
        if normalized in {
            "qué capturé",
            "que capturé",
            "qué capture",
            "que capture",
        }:
            return EpisodeQuery(
                action="system.screen_capture",
                field="status",
            )

        return None

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:
        """
        Normaliza espacios y puntuación exterior para que
        una consulta pueda llegar con signos de interrogación,
        exclamación u otra puntuación natural.

        Ejemplos:

            ¿Qué aplicación abrí?
            Qué aplicación abrí
            ¿Qué aplicación abrí

        producen el mismo texto normalizado.
        """

        normalized = text.lower().strip()

        normalized = normalized.strip(
            "¿?¡!.,;: "
        )

        normalized = " ".join(
            normalized.split()
        )

        return normalized
