from __future__ import annotations

from typing import Any

from runtime.execution_result import ExecutionResult


class ResponseFormatter:
    """
    Convierte resultados técnicos de NEXUS
    en respuestas legibles para el usuario.

    No interpreta intenciones.
    No consulta memoria.
    No ejecuta acciones.

    Solamente transforma un ExecutionResult
    en lenguaje humano.
    """

    def format(
        self,
        result: ExecutionResult,
    ) -> str:
        """
        Convierte un ExecutionResult en una
        respuesta textual para el usuario.
        """

        if not result.success:
            if result.message:
                return result.message

            return "No pude completar la operación."

        output = result.output

        if not isinstance(output, dict):
            if output:
                return str(output)

            return "Listo."

        #
        # Consulta de memoria episódica
        #
        if "episode_query_result" in output:
            query_result = output.get(
                "episode_query_result",
                {},
            )

            if query_result.get("status") != "found":
                return (
                    "No encontré la información "
                    "que buscabas en la memoria."
                )

            action = query_result.get("action")
            value = query_result.get("value")

            if action == "system.open_app":
                if value:
                    return (
                        f"La última aplicación que abriste "
                        f"fue {value}."
                    )

                return (
                    "Encontré la acción, "
                    "pero no pude identificar "
                    "la aplicación."
                )

            if action == "system.close_app":
                if value:
                    return (
                        f"La última aplicación que cerraste "
                        f"fue {value}."
                    )

                return (
                    "Encontré la acción, "
                    "pero no pude identificar "
                    "la aplicación."
                )

            if action == "system.set_volume":
                if value is not None:
                    return (
                        f"El último volumen que pusiste "
                        f"fue {self._format_number(value)}%."
                    )

                return (
                    "Encontré el cambio de volumen, "
                    "pero no pude recuperar el valor."
                )

            if action == "system.screen_capture":
                if value == "captured":
                    return "La última acción fue una captura de pantalla."

                return (
                    "Encontré la última captura, "
                    "pero no pude determinar su estado."
                )

            return (
                "Encontré la información en la memoria, "
                "pero todavía no puedo expresarla "
                "de forma natural."
            )

                # Búsqueda cognitiva de documentos
        if output.get("operation") == "documents.find_relevant":
            documents = output.get("documents", [])

            if not documents:
                return "No encontré documentos que coincidan con tu búsqueda."

            names = [
                document.get("name")
                for document in documents
                if isinstance(document, dict) and document.get("name")
            ]

            if not names:
                return f"Encontré {len(documents)} documento(s) relevante(s)."

            if len(names) == 1:
                return f"Encontré un documento relevante: {names[0]}."

            return (
                f"Encontré {len(names)} documentos relevantes: "
                + ", ".join(names)
                + "."
            )

        # Búsqueda cognitiva de reglas y procesos
        operation = output.get("operation")

        cognitive_collections = {
            "rules.find_relevant": ("rules", "reglas"),
            "processes.find_relevant": ("processes", "procesos"),
        }

        if operation in cognitive_collections:
            collection_name, label = cognitive_collections[operation]
            items = output.get(collection_name, [])

            if not items:
                return f"No encontré {label} relevantes para tu búsqueda."

            names = [
                item.get("name")
                for item in items
                if isinstance(item, dict) and item.get("name")
            ]

            if not names:
                return (
                    f"Encontré {len(items)} {label} relevantes, "
                    "pero no tienen nombres disponibles."
                )

            if len(names) == 1:
                response = f"Encontré una {label[:-1]} relevante: {names[0]}."
            else:
                response = (
                    f"Encontré {len(names)} {label} relevantes: "
                    + ", ".join(names)
                    + "."
                )

            details = []
            for item in items:
                if not isinstance(item, dict):
                    continue

                name = item.get("name")
                description = item.get("description")
                status = item.get("status")

                detail = name or "Sin nombre"
                if description:
                    detail += f" — {description}"
                if status:
                    detail += f" (estado: {status})"

                details.append(detail)

            if details:
                response += "\n\n" + "\n".join(
                    f"- {detail}" for detail in details
                )

            return response


        if not output:
            return "Listo."

        #
        # Captura + inspección
        #
        # La inspección utiliza el resultado producido
        # por system.inspect_capture.
        #
        if "capture_inspection" in output:
            inspection = output.get("capture_inspection")

            if isinstance(inspection, dict):
                width = inspection.get("width")
                height = inspection.get("height")

                if width is not None and height is not None:
                    return (
                        "Inspeccioné la pantalla. "
                        f"La captura tiene "
                        f"{self._format_number(width)} × "
                        f"{self._format_number(height)} píxeles."
                    )

            width = output.get("width")
            height = output.get("height")

            if width is not None and height is not None:
                return (
                    "Inspeccioné la pantalla. "
                    f"La captura tiene "
                    f"{self._format_number(width)} × "
                    f"{self._format_number(height)} píxeles."
                )

            return "Inspeccioné la pantalla."

        #
        # Captura de pantalla
        #
        if output.get("status") == "captured":
            return "Capturé la pantalla."

        #
        # Episodios recientes
        #
        if (
            output.get("status") == "read"
            and "episodes" in output
        ):
            return self._format_recent_episodes(
                output.get("episodes", [])
            )

        #
        # Episodio individual
        #
        if (
            output.get("status") == "read"
            and "episode" in output
        ):
            episode = output.get("episode")

            if not episode:
                if output.get("mode") == "previous":
                    return "No registré una acción anterior."

                return "No registré ninguna acción recientemente."

            action = episode.get("action")
            parameters = episode.get(
                "parameters",
                {},
            )

            if output.get("mode") == "previous":
                description = self._describe_episode_noun(
                    action,
                    parameters,
                )

                if not description:
                    return (
                        "Registré una acción anterior, "
                        "pero no pude describirla."
                    )

                return (
                    "La acción anterior fue "
                    f"{description}."
                )

            if output.get("mode") == "last":
                description = self._describe_episode(
                    action,
                    parameters,
                )

                if not description:
                    return (
                        "Registré una última acción, "
                        "pero no pude describirla."
                    )

                return (
                    "Tu última acción fue "
                    f"{description}."
                )

        #
        # Último episodio
        #
        if (
            output.get("status") == "read"
            and "episode" in output
        ):
            episode = output.get("episode")

            if not episode:
                return (
                    "No registré ninguna acción "
                    "recientemente."
                )

            if not episode.get(
                "success",
                True,
            ):
                return (
                    "La última acción registrada "
                    "no se completó correctamente."
                )

            description = (
                self._describe_episode_infinitive(
                    episode.get("action"),
                    episode.get(
                        "parameters",
                        {},
                    ),
                )
            )

            if description:
                return (
                    "Tu última acción fue "
                    f"{description}."
                )

            original_text = episode.get(
                "original_text"
            )

            if original_text:
                return (
                    "Tu última acción fue: "
                    f"{original_text}."
                )

            return (
                "Encontré la última acción, "
                "pero no puedo describirla."
            )

        #
        # Volumen actual
        #
        if (
            output.get("status") == "read"
            and "volume" in output
        ):
            volume = output["volume"]

            return (
                f"El volumen está al "
                f"{self._format_number(volume)}%."
            )

        #
        # Historial del volumen
        #
        if (
            "found" in output
            and "mode" in output
        ):
            found = output.get("found")
            value = output.get("value")
            mode = output.get("mode")

            if not found:
                return self._format_history_not_found(
                    mode
                )

            if mode == "previous":
                return (
                    "El volumen anterior era "
                    f"{self._format_number(value)}%."
                )

            if mode == "find":
                return (
                    "Sí. El volumen estuvo en "
                    f"{self._format_number(value)}%."
                )

        #
        # Volumen establecido
        #
        if (
            output.get("status") == "set"
            and "volume" in output
        ):
            volume = output["volume"]

            return (
                f"Volumen establecido al "
                f"{self._format_number(volume)}%."
            )

        #
        # Volumen restaurado
        #
        if (
            output.get("status") == "restored"
            and "volume" in output
        ):
            volume = output["volume"]

            return (
                f"Volumen restaurado al "
                f"{self._format_number(volume)}%."
            )

        #
        # Aplicación abierta
        #
        if (
            output.get("status") == "opened"
            and "application" in output
        ):
            application = output["application"]

            return (
                f"Abrí {application}."
            )

        #
        # Aplicación cerrada
        #
        if (
            output.get("status") == "closed"
            and "application" in output
        ):
            application = output["application"]

            return (
                f"Cerré {application}."
            )

        #
        # Mute / Unmute / Restore
        #
        if (
            output.get("status") == "muted"
            and output.get("muted") is True
        ):
            return "Silencié el sistema."

        if (
            output.get("status") == "unmuted"
            and output.get("muted") is False
        ):
            return "Activé el sonido."

        if (
            output.get("status") == "restored"
            and "muted" in output
        ):
            muted = output["muted"]

            if muted is True:
                return "Restauré el silencio."

            if muted is False:
                return "Restauré el sonido."

        #
        # Estado actual de mute
        #
        if (
            output.get("status") == "read"
            and "muted" in output
        ):
            if output["muted"] is True:
                return "El sistema está silenciado."

            if output["muted"] is False:
                return "El sonido está activado."

        #
        # Hora actual
        #
        if output.get("status") == "read" and "time" in output:
            if "date" in output:
                return f"Hoy es {output['date']} y son las {output['time']}."
            return f"Son las {output['time']}."

        #
        # Fallback
        #
        return str(output)

    @staticmethod
    def _format_number(value: Any) -> str:
        """
        Formatea números evitando .0 innecesarios.
        """

        if isinstance(value, float) and value.is_integer():
            return str(int(value))

        return str(value)

    @staticmethod
    def _format_recent_episodes(
        episodes: list[dict[str, Any]],
    ) -> str:
        """
        Formatea una lista de episodios recientes.
        """

        if not episodes:
            return "No registré acciones recientemente."

        descriptions: list[str] = []

        for episode in episodes:
            description = ResponseFormatter._describe_episode(
                episode.get("action"),
                episode.get("parameters", {}),
            )

            if description:
                descriptions.append(description)
                continue

            original_text = episode.get("original_text")

            if original_text:
                descriptions.append(original_text)

        if not descriptions:
            return "Encontré acciones recientes, pero no pude describirlas."

        if len(descriptions) == 1:
            return (
                "La acción reciente fue "
                f"{descriptions[0]}."
            )

        return (
            "Las acciones recientes fueron: "
            + "; ".join(descriptions)
            + "."
        )

    @staticmethod
    def _describe_episode(
        action: str | None,
        parameters: dict[str, Any],
    ) -> str | None:
        """
        Describe un episodio en lenguaje natural.
        """

        if action == "system.open_app":
            application = parameters.get("application")

            if application:
                return f"abrir {application}"

        if action == "system.close_app":
            application = parameters.get("application")

            if application:
                return f"cerrar {application}"

        if action == "system.screen_capture":
            return "capturar la pantalla"

        if action == "system.set_volume":
            level = parameters.get("level")

            if level is not None:
                return (
                    "establecer el volumen al "
                    f"{ResponseFormatter._format_number(level)}%"
                )

        if action == "system.mute":
            return "silenciar el sistema"

        if action == "system.unmute":
            return "activar el sonido"

        if action == "system.process_list":
            return "consultar los procesos activos"

        return None

    @staticmethod
    def _describe_episode_noun(
        action: str | None,
        parameters: dict[str, Any],
    ) -> str | None:
        """
        Describe un episodio como sustantivo.
        """

        if action == "system.open_app":
            application = parameters.get("application")

            if application:
                return f"abrir {application}"

        if action == "system.close_app":
            application = parameters.get("application")

            if application:
                return f"cerrar {application}"

        if action == "system.screen_capture":
            return "capturar la pantalla"

        if action == "system.set_volume":
            level = parameters.get("level")

            if level is not None:
                return (
                    "establecer el volumen al "
                    f"{ResponseFormatter._format_number(level)}%"
                )

        if action == "system.mute":
            return "silenciar el sistema"

        if action == "system.unmute":
            return "activar el sonido"

        if action == "system.process_list":
            return "consultar los procesos activos"

        return None

    @staticmethod
    def _describe_episode_infinitive(
        action: str | None,
        parameters: dict[str, Any],
    ) -> str | None:
        """
        Describe un episodio usando infinitivo.
        """

        return ResponseFormatter._describe_episode(
            action,
            parameters,
        )

    @staticmethod
    def _format_history_not_found(
        mode: str | None,
    ) -> str:
        if mode == "previous":
            return "No encontré un volumen anterior registrado."

        if mode == "find":
            return "No encontré ese valor en el historial del volumen."

        return "No encontré información en el historial del volumen."
