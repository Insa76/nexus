from __future__ import annotations
import asyncio
import json
import re
from typing import Any

import httpx
from ollama import AsyncClient, RequestError

from planner.intent import Intent
from planner.intent_provider import IntentProvider


class OllamaIntentProvider(IntentProvider):
    """Interpreta lenguaje natural usando Ollama y valida la intención resultante."""

    MIN_CONFIDENCE = 0.50
    REQUEST_TIMEOUT_SECONDS = 10.0

    def __init__(
        self,
        model: str = "llama3:latest",
        host: str = "http://localhost:11434",
    ) -> None:
        self._model = model
        self._host = host

    async def recognize(
        self,
        text: str,
        capabilities: list[dict[str, Any]] | None = None,
        context: dict[str, Any] | None = None,
    ) -> Intent:
        capabilities = capabilities or []
        context = context or {}

        # Índices para resolver la respuesta del modelo contra el catálogo real.
        by_name = {
            capability["name"]: capability
            for capability in capabilities
            if isinstance(capability, dict)
            and isinstance(capability.get("name"), str)
        }
        by_action = {
            capability["action"]: capability
            for capability in capabilities
            if isinstance(capability, dict)
            and isinstance(capability.get("action"), str)
        }

        normalized = text.lower().strip()

        # Consultas deterministas de volumen actual.
        volume_read_patterns = (
            r"\ba cuánto está\b",
            r"\ba cuanto está\b",
            r"\ba cuánto quedó\b",
            r"\ba cuanto quedó\b",
            r"\bcuánto está\b",
            r"\bcuanto está\b",
            r"\bcuánto quedó\b",
            r"\bcuanto quedó\b",
            r"\bqué volumen\b",
            r"\bque volumen\b",
            r"\bcuál es el volumen\b",
            r"\bcual es el volumen\b",
            r"\bvolumen actual\b",
            r"\bqué nivel de volumen\b",
            r"\bque nivel de volumen\b",
        )

        if any(re.search(pattern, normalized) for pattern in volume_read_patterns):
            if by_action.get("system.get_volume") is not None:
                return Intent(
                    action="system.get_volume",
                    confidence=1.0,
                    parameters={},
                    original_text=text,
                )

        capabilities_json = json.dumps(
            capabilities,
            ensure_ascii=False,
            indent=2,
        )
        context_json = json.dumps(
            context,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        system_prompt = f"""
Sos el módulo de interpretación de NEXUS.

Tu tarea es convertir la solicitud del usuario
 en UNA intención estructurada.

CAPACIDADES DISPONIBLES:

{capabilities_json}

CONTEXTO RECIENTE DE NEXUS:

{context_json}

IMPORTANTE SOBRE EL CONTEXTO:

El contexto sirve únicamente para ayudar a
comprender solicitudes que dependan de una
interacción anterior.

El contexto NO crea capacidades nuevas.

Nunca ejecutes una acción solamente porque
aparece en el contexto.

La acción seleccionada debe existir actualmente
en CAPACIDADES DISPONIBLES.

El estado real del sistema tiene prioridad sobre
cualquier dato almacenado en memoria.

El contexto contiene diferentes tipos de información
y cada uno tiene un propósito distinto:

- last_request:
  última solicitud textual del usuario.

- last_intent:
  última intención interpretada.

- last_result:
  resultado de la última ejecución.

- recent_episodes:
  registro de acciones que NEXUS ejecutó realmente,
  incluyendo la acción, los parámetros, el texto
  original y el resultado.

IMPORTANTE SOBRE recent_episodes:

recent_episodes representa MEMORIA EPISÓDICA.

Si el usuario pregunta qué hizo, cuál fue su última
acción, qué hizo recién o qué acción realizó antes,
está preguntando por un EPISODIO de interacción,
no por el estado actual del sistema.

Ejemplos:

- "¿Qué hice recién?"
- "¿Cuál fue mi última acción?"
- "¿Qué hice antes?"
- "¿Qué cambié antes?"
- "¿Qué hice antes de subir el volumen?"

Estas preguntas deben resolverse utilizando
recent_episodes cuando exista una capacidad disponible
para consultar memoria episódica.

No deben interpretarse automáticamente como una
consulta sobre el estado actual del sistema.

Diferencias importantes:

- "¿A cuánto está el volumen?"
  → consulta el estado actual.

- "¿Qué volumen tenía antes?"
  → consulta el historial del estado del volumen.

- "¿Qué hice recién?"
  → consulta memoria episódica.

- "¿Cuál fue mi última acción?"
  → consulta memoria episódica.

El estado actual del sistema tiene prioridad cuando
el usuario pregunta por el estado actual.

La memoria episódica tiene prioridad cuando el usuario
pregunta explícitamente por acciones realizadas
anteriormente.

REGLAS ESTRICTAS:

1. Solo podés seleccionar una acción que exista
   en las capacidades disponibles.

2. Si la solicitud no corresponde claramente
   a una capacidad, devolvé system.unknown.

3. NO intentes adivinar la intención del usuario.

4. NO confundas verbos de conversación con
   acciones del sistema. Un saludo como "hola"
   debe devolver system.unknown.

5. Podés utilizar el contexto reciente para
   interpretar referencias como:

   - "dejalo como estaba"
   - "dejala en 30%"
   - "eso"
   - "lo mismo"
   - "el volumen"
   - "esa aplicación"

   siempre que exista suficiente información
   en el contexto.

6. Para system.open_app, el usuario debe estar
   pidiendo explícitamente abrir, ejecutar o
   iniciar una aplicación.

7. Para system.set_volume, el usuario puede
   referirse al volumen, música, sonido, audio
   o utilizar expresiones como subir, bajar,
   fuerte o bajo cuando el contexto indique
   claramente que habla del sonido.

8. Para system.get_volume, el usuario está
   consultando el volumen actual.

   Ejemplos:
   - "¿A cuánto está el volumen?"
   - "¿Cuál es el volumen?"
   - "¿Qué volumen tengo?"
   - "¿A cuánto está?"
   - "Decime el volumen actual"

   Si la solicitud es una pregunta sobre el
   estado actual del volumen, utilizá
   system.get_volume.

9. Una consulta sobre el volumen NUNCA debe
   convertirse en system.set_volume.

10. Si la solicitud contiene un valor numérico
    acompañado de una instrucción para cambiar
    el volumen, utilizá system.set_volume.

11. Si la solicitud solamente pregunta por el
    volumen actual y no solicita modificarlo,
    utilizá system.get_volume.

12. Para system.mute, el usuario debe pedir
    silenciar.

13. Para system.unmute, el usuario debe pedir
    quitar el silencio.

14. Para system.close_app, el usuario debe pedir
    explícitamente cerrar una aplicación.

15. Si la solicitud es enviar mensajes, hablar
    con una persona, realizar una tarea que no
    aparezca en las capacidades, o cualquier
    otra tarea no disponible, devolvé:

    system.unknown

16. Nunca uses una capacidad solamente porque
    una palabra del usuario parece coincidir
    con su nombre.

17. El campo action debe utilizar exactamente
    el campo action de la capacidad.

18. Si no existe suficiente información para
    completar los parámetros obligatorios,
    devolvé system.unknown.

19. Respondé únicamente JSON válido.

EJEMPLOS:

Usuario:
"Poné el volumen al 40%"

Respuesta:
{{
    "action": "system.set_volume",
    "confidence": 1.0,
    "parameters": {{
        "level": 40
    }}
}}

Usuario:
"La música está demasiado fuerte, dejala en 30%"

Respuesta:
{{
    "action": "system.set_volume",
    "confidence": 1.0,
    "parameters": {{
        "level": 30
    }}
}}

Usuario:
"Está muy fuerte el audio, bajalo al 25%"

Respuesta:
{{
    "action": "system.set_volume",
    "confidence": 1.0,
    "parameters": {{
        "level": 25
    }}
}}

Usuario:
"Mandale un mensaje a Juan"

Respuesta:
{{
    "action": "system.unknown",
    "confidence": 0.0,
    "parameters": {{}}
}}

Usuario:
"Abrí Spotify"

Respuesta:
{{
    "action": "system.open_app",
    "confidence": 1.0,
    "parameters": {{
        "application": "Spotify"
    }}
}}

Usuario:
"hola"

Respuesta:
{{
    "action": "system.unknown",
    "confidence": 0.0,
    "parameters": {{}}
}}

FORMATO:

{{
    "action": "system.unknown",
    "confidence": 0.0,
    "parameters": {{}}
}}

SOLICITUD DEL USUARIO:

{text}
"""

        try:
            async with asyncio.timeout(self.REQUEST_TIMEOUT_SECONDS):
                async with AsyncClient(
                    host=self._host,
                    timeout=self.REQUEST_TIMEOUT_SECONDS,
                ) as client:
                    response = await client.chat(
                        model=self._model,
                        messages=[{"role": "system", "content": system_prompt}],
                        format="json",
                        options={"temperature": 0},
                    )
        except (
            TimeoutError,
            httpx.TimeoutException,
            httpx.RequestError,
            RequestError,
        ):
            return self._unknown(text)

        try:
            data = json.loads(response.message.content)
        except (json.JSONDecodeError, TypeError):
            return self._unknown(text)

        if not isinstance(data, dict):
            return self._unknown(text)

        requested_action = str(data.get("action", "system.unknown"))
        try:
            confidence = float(data.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0

        parameters = data.get("parameters", {})
        if not isinstance(parameters, dict):
            parameters = {}

        if confidence < self.MIN_CONFIDENCE:
            return self._unknown(text, confidence)

        capability = by_action.get(requested_action)
        if capability is None:
            capability = by_name.get(requested_action)
        if capability is None:
            return self._unknown(text, confidence)

        if not self._validate_parameters(capability, parameters):
            return self._unknown(text, confidence)

        if not self._validate_semantics(
            text,
            capability["action"],
            parameters,
            context,
        ):
            return self._unknown(text, confidence)

        return Intent(
            action=capability["action"],
            confidence=confidence,
            parameters=parameters,
            original_text=text,
        )

    def _validate_semantics(
        self,
        text: str,
        action: str,
        parameters: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Comprueba que la acción propuesta sea compatible con la solicitud."""
        context = context or {}
        normalized = text.lower().strip()

        if action == "system.open_app":
            open_pattern = r"\b(abr[ií]r?|ejecut[aá]r?|inici[aá]r?|lanzar?)\b"
            if not re.search(open_pattern, normalized):
                return False
            application = parameters.get("application")
            return isinstance(application, str) and bool(application.strip())

        if action == "system.get_volume":
            read_patterns = (
                r"\ba cuánto está\b",
                r"\ba cuanto está\b",
                r"\bcuánto está\b",
                r"\bcuanto está\b",
                r"\bqué volumen\b",
                r"\bque volumen\b",
                r"\bcuál es el volumen\b",
                r"\bcual es el volumen\b",
                r"\bvolumen actual\b",
                r"\bqué nivel de volumen\b",
                r"\bque nivel de volumen\b",
                r"\bdecime el volumen actual\b",
                r"\bdecime el volumen\b",
            )
            return any(re.search(pattern, normalized) for pattern in read_patterns)

        if action == "system.set_volume":
            read_patterns = (
                r"\ba cuánto está\b",
                r"\ba cuanto está\b",
                r"\bcuánto está\b",
                r"\bcuanto está\b",
                r"\bqué volumen\b",
                r"\bque volumen\b",
                r"\bcuál es el volumen\b",
                r"\bcual es el volumen\b",
                r"\bvolumen actual\b",
                r"\bqué nivel de volumen\b",
                r"\bque nivel de volumen\b",
            )
            if any(re.search(pattern, normalized) for pattern in read_patterns):
                return False

            level = parameters.get("level")
            if not isinstance(level, (int, float)) or isinstance(level, bool):
                return False
            if not 0 <= float(level) <= 100:
                return False

            audio_cues = (
                "volumen", "música", "musica", "sonido", "audio", "parlante",
                "altavoz", "auricular", "auriculares", "micrófono", "microfono",
            )
            volume_cues = (
                "fuerte", "bajo", "baja", "bajá", "subí", "subi", "subir",
                "subirlo", "bajarlo", "bajala", "bajalo", "subilo", "subila",
                "más fuerte", "mas fuerte", "más bajo", "mas bajo", "dejala",
                "dejalo", "dejarlo",
            )
            has_audio_context = any(cue in normalized for cue in audio_cues)
            has_volume_context = any(cue in normalized for cue in volume_cues)

            previous_intent = context.get("last_intent")
            previous_result = context.get("last_result")
            previous_action = None
            if isinstance(previous_intent, dict):
                previous_action = previous_intent.get("action")

            previous_volume = None
            if isinstance(previous_result, dict):
                output = previous_result.get("output")
                if isinstance(output, dict):
                    previous_volume = output.get("volume")

            has_previous_volume_context = previous_action in {
                "system.set_volume",
                "system.get_volume",
            }
            if isinstance(previous_volume, (int, float)) and not isinstance(previous_volume, bool):
                has_previous_volume_context = True

            return has_audio_context or has_volume_context or has_previous_volume_context

        if action == "system.mute":
            return bool(re.search(r"\b(silenci[aá]r?|mute|sin sonido)\b", normalized))

        if action == "system.unmute":
            return bool(
                re.search(
                    r"\b(quit[aá]r?.*silencio|desmut|activar.*sonido)\b",
                    normalized,
                )
            )

        if action == "system.close_app":
            close_pattern = r"\b(cerr[aá]r?|termin[aá]r?|finaliz[aá]r?)\b"
            if not re.search(close_pattern, normalized):
                return False
            application = parameters.get("application")
            return isinstance(application, str) and bool(application.strip())

        if action == "system.get_last_episode":
            episode_patterns = (
                r"\búltima acción\b",
                r"\bultima accion\b",
                r"\búltimo episodio\b",
                r"\bultimo episodio\b",
                r"\bqué hice\b",
                r"\bque hice\b",
                r"\bqué hiciste\b",
                r"\bque hiciste\b",
                r"\bqué pasó\b",
                r"\bque paso\b",
                r"\bqué acción hice\b",
                r"\bque accion hice\b",
                r"\búltima vez\b",
                r"\bultima vez\b",
                r"\brecién\b",
                r"\brecien\b",
                r"\bqué hice antes\b",
                r"\bque hice antes\b",
                r"\bqué cambié antes\b",
                r"\bque cambie antes\b",
                r"\bqué hizo nexus antes\b",
                r"\bque hizo nexus antes\b",
            )
            return any(re.search(pattern, normalized) for pattern in episode_patterns)

        # Las demás acciones conservan la política de validación existente.
        return True

    def _validate_parameters(
        self,
        capability: dict[str, Any],
        parameters: dict[str, Any],
    ) -> bool:
        """Valida parámetros contra el esquema de la capacidad seleccionada."""
        schema = capability.get("parameters", {})
        if not isinstance(schema, dict):
            return True

        # Parámetros obligatorios.
        for name, definition in schema.items():
            if not isinstance(definition, dict):
                continue
            if definition.get("required", False) and name not in parameters:
                return False

        # No aceptar parámetros que no estén definidos en el esquema.
        for name in parameters:
            if name not in schema:
                return False

        # Comprobar los tipos de los parámetros recibidos.
        for name, value in parameters.items():
            definition = schema.get(name, {})
            parameter_type = definition.get("type")

            if parameter_type == "string":
                if not isinstance(value, str):
                    return False
            elif parameter_type == "number":
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    return False
            elif parameter_type == "integer":
                if isinstance(value, bool) or not isinstance(value, int):
                    return False

        return True

    def _unknown(
        self,
        text: str,
        confidence: float = 0.0,
    ) -> Intent:
        return Intent(
            action="system.unknown",
            confidence=confidence,
            parameters={},
            original_text=text,
        )
