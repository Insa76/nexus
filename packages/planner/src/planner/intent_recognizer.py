from __future__ import annotations

import re

from packages.planner.src.planner.intent import Intent


class IntentRecognizer:
    """
    Convierte una frase del usuario
    en un Intent estructurado.

    Primera implementación basada
    en reglas.
    """

    def recognize(
        self,
        text: str,
    ) -> Intent:

        normalized = text.lower().strip()

        #
        # Abrir aplicación
        #

        match = re.match(
            r"^(abrí|abre|abrir)\s+(.+)$",
            normalized,
        )

        if match:

            application = match.group(2).strip()

            return Intent(
                action="system.open_app",
                original_text=text,
                parameters={
                    "application": application
                },
            )

        #
        # Capturar pantalla
        #

        match = re.match(
            r"^(capturá|captura|capturar)\s+(la\s+)?pantalla$",
            normalized,
        )

        if match:

            return Intent(
                action="system.screen_capture",
                original_text=text,
                parameters={},
            )

        #
        # Listar procesos
        #

        match = re.match(
            r"^(mostrame|mostrar|lista|listar)\s+(los\s+)?procesos$",
            normalized,
        )

        if match:

            return Intent(
                action="system.process_list",
                original_text=text,
                parameters={},
            )

        #
        # Intent por defecto
        #

        return Intent(
            action="echo",
            original_text=text,
            parameters={},
        )