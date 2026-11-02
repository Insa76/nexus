from __future__ import annotations

import re
from typing import Any

from planner.intent import Intent
from planner.intent_provider import IntentProvider
from planner.ollama_intent_provider import OllamaIntentProvider
from planner.rule_intent_provider import RuleIntentProvider


class HybridIntentProvider(IntentProvider):
    """
    Provider híbrido de interpretación.

    Primero intenta resolver la intención mediante
    reglas deterministas.

    Si las reglas no reconocen la solicitud,
    utiliza Ollama como fallback.

    También permite interpretar solicitudes compuestas
    como:

        "Capturá la pantalla y después inspeccionala"

    generando una Intent principal con una secuencia
    de sub-intenciones.
    """

    def __init__(
        self,
        rule_provider: RuleIntentProvider,
        ollama_provider: OllamaIntentProvider,
    ) -> None:

        self._rule_provider = rule_provider

        self._ollama_provider = ollama_provider

    async def recognize(
        self,
        text: str,
        capabilities: list[dict[str, Any]] | None = None,
        context: dict[str, Any] | None = None,
    ) -> Intent:

                #
        # Saludos simples: no deben activar herramientas.
        #

        normalized = re.sub(
            r"[¿?¡!.,;:]+",
            "",
            text.lower().strip(),
        )

        greetings = {
            "hola",
            "hola nexus",
            "buenas",
            "buen día",
            "buen dia",
            "buenos días",
            "buenos dias",
            "buenas tardes",
            "buenas noches",
            "hey",
            "qué tal",
            "que tal",
        }

        if normalized in greetings:
            return Intent(
                action="system.unknown",
                confidence=0.0,
                parameters={},
                original_text=text,
            )

        #
        # Primero comprobamos si la solicitud contiene
        # una secuencia explícita de acciones.
        #

        parts = self._split_compound_request(
            text
        )

        # Antes de separar por la conjunción "y", damos prioridad a una
        # intención determinista reconocida sobre la solicitud completa.
        # Así, expresiones como "fecha y hora actual" no se dividen en dos
        # fragmentos incompletos y no terminan innecesariamente en Ollama.
        if len(parts) > 1:
            whole_intent = await self._rule_provider.recognize(
                text,
                capabilities,
                context,
            )
            if whole_intent.action != "system.unknown":
                return whole_intent

        #
        # Solicitud simple.
        #

        if len(parts) == 1:

            return await self._recognize_single(
                parts[0],
                capabilities,
                context,
            )

        #
        # Solicitud compuesta.
        #

        sub_intents: list[Intent] = []

        for part in parts:

            intent = await self._recognize_single(
                part,
                capabilities,
                context,
            )

            #
            # Si una parte no pudo resolverse,
            # no construimos una secuencia parcial.
            #

            if intent.action == "system.unknown":

                #
                # Intentamos interpretar la solicitud
                # completa mediante Ollama.
                #

                return await self._ollama_provider.recognize(
                    text,
                    capabilities,
                    context,
                )

            sub_intents.append(
                intent
            )

        #
        # La Intent principal conserva el texto original
        # y contiene la secuencia que deberá convertir
        # el Planner en pasos.
        #

        first = sub_intents[0]

        return Intent(
            action=first.action,
            confidence=min(
                intent.confidence
                for intent in sub_intents
            ),
            parameters=first.parameters.copy(),
            original_text=text,
            sub_intents=sub_intents,
        )

    async def _recognize_single(
        self,
        text: str,
        capabilities: list[dict[str, Any]] | None,
        context: dict[str, Any] | None,
    ) -> Intent:
        """
        Resuelve una única parte de una solicitud.
        """

        intent = await self._rule_provider.recognize(
            text,
            capabilities,
            context,
        )

        if intent.action != "system.unknown":

            return intent

        return await self._ollama_provider.recognize(
            text,
            capabilities,
            context,
        )

    @staticmethod
    def _split_compound_request(
        text: str,
    ) -> list[str]:
        """
        Divide solicitudes que expresan una secuencia
        explícita de acciones.

        Ejemplos:

            "capturá la pantalla y después inspeccionala"

        se convierte en:

            [
                "capturá la pantalla",
                "inspeccionala",
            ]

        También reconoce conectores como:

            "y luego"
            "y después"
            "y a continuación"
            "y"

        El split solamente se realiza cuando el conector
        aparece entre fragmentos con contenido.
        """

        normalized = text.strip()

        if not normalized:

            return [normalized]

        parts = re.split(
            r"\s+\b(?:y\s+(?:después|luego|a\s+continuación)|y)\b\s+",
            normalized,
            flags=re.IGNORECASE,
        )

        return [
            part.strip()
            for part in parts
            if part.strip()
        ]
