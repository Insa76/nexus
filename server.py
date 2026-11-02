
from __future__ import annotations

import asyncio
import json
import queue
import threading
from datetime import date, datetime, timezone
from urllib.parse import unquote, urlsplit
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from bootstrap.bootstrap import build_assistant_runtime
from tasks import Reminder, ReminderStatus
from tasks.reminder_lifecycle import InvalidReminderTransition
from presence.presence_service import PresenceService
from presence.presence_event import PresenceEvent
from nexus_http_security import (
    cors_origin_for,
    is_allowed_browser_origin,
    is_allowed_host,
    MAX_REQUEST_BODY_BYTES,
)


HOST = "127.0.0.1"
PORT = 8765

BASE_DIR = Path(__file__).resolve().parent

# El Engine mantiene WorkingMemory en memoria.
# Serializamos las ejecuciones para evitar que
# dos solicitudes modifiquen la memoria simultáneamente.
engine_lock = threading.Lock()


print()
print("=" * 60)
print("                 NEXUS DEV CONSOLE")
print("=" * 60)

engine, assistant_services, assistant_lifecycle = (
    build_assistant_runtime()
)
presence = PresenceService(engine.memory)

print("✓ NEXUS Engine iniciado")
print("✓ WorkingMemory activa")
print("✓ PresenceService activo")
print(f"✓ Servidor: http://{HOST}:{PORT}")
print("=" * 60)
print()


class NexusHandler(BaseHTTPRequestHandler):

    # =========================================================
    # JSON SAFE
    # =========================================================

    def _json_safe(
        self,
        value: Any,
    ) -> Any:
        """
        Convierte estructuras internas de NEXUS
        en valores compatibles con JSON.

        Esta conversión ocurre únicamente
        en la frontera HTTP.
        """

        if value is None:
            return None

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ):
            return value

        if isinstance(
            value,
            (datetime, date),
        ):
            return value.isoformat()

        if isinstance(value, bytes):
            return {
                "type": "bytes",
                "size": len(value),
            }

        # PIL.Image.Image
        if (
            hasattr(value, "size")
            and hasattr(value, "mode")
            and value.__class__.__module__.startswith(
                "PIL"
            )
        ):
            width, height = value.size

            return {
                "type": "image",
                "width": width,
                "height": height,
                "mode": value.mode,
            }

        if isinstance(value, dict):
            return {
                str(key): self._json_safe(item)
                for key, item in value.items()
            }

        if isinstance(
            value,
            (list, tuple, set),
        ):
            return [
                self._json_safe(item)
                for item in value
            ]

        # Objetos Pydantic u otros objetos
        # con model_dump().
        model_dump = getattr(
            value,
            "model_dump",
            None,
        )

        if callable(model_dump):
            try:
                return self._json_safe(
                    model_dump()
                )
            except Exception:
                pass

        # Último recurso.
        return {
            "type": "object",
            "class": value.__class__.__name__,
            "repr": repr(value),
        }

    def _reminder_to_dict(
        self,
        reminder: Reminder,
    ) -> dict[str, Any]:
        return {
            "id": reminder.id,
            "message": reminder.message,
            "trigger_at": reminder.trigger_at.isoformat(),
            "status": reminder.status.value,
            "task_id": reminder.task_id,
            "user_id": reminder.user_id,
            "organization_id": reminder.organization_id,
            "project_id": reminder.project_id,
            "created_at": reminder.created_at.isoformat(),
        }

    # =========================================================
    # HTTP HELPERS
    # =========================================================

    def _write_cors_headers(self) -> None:
        origin = cors_origin_for(self.headers.get("Origin"))
        if origin is None:
            return
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, DELETE, OPTIONS",
        )

    def _reject_untrusted_request(self) -> bool:
        """Reject untrusted browser origins and non-loopback Host headers."""
        if not is_allowed_host(self.headers.get("Host")):
            self._send_json(
                {"success": False, "message": "Host no permitido."},
                status=403,
            )
            return True

        origin = self.headers.get("Origin")
        if not is_allowed_browser_origin(origin):
            self._send_json(
                {"success": False, "message": "Origen web no permitido."},
                status=403,
            )
            return True
        return False

    def _send_json(
        self,
        data: dict,
        status: int = 200,
    ) -> None:

        safe_data = self._json_safe(data)

        payload = json.dumps(
            safe_data,
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(len(payload)),
        )

        self._write_cors_headers()

        self.end_headers()

        self.wfile.write(payload)

    def _send_html(
        self,
        content: bytes,
    ) -> None:

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(len(content)),
        )

        self.end_headers()

        self.wfile.write(content)

    # =========================================================
    # MEMORY / TRACE HELPERS
    # =========================================================

    def _entry_to_dict(
        self,
        entry,
    ) -> dict:

        return {
            "id": entry.id,
            "timestamp": entry.timestamp.isoformat(),
            "type": entry.type,
            "data": entry.data,
        }

    def _build_trace(
        self,
        entries: list,
    ) -> dict:
        """
        Construye un Execution Trace a partir
        de las entradas generadas por una ejecución.
        """

        trace = {
            "request": None,
            "intent": None,
            "objective": None,
            "plan": None,
            "result": None,
            "error": None,
        }

        for entry in entries:

            if entry.type == "user_request":
                trace["request"] = entry.data

            elif entry.type == "intent":
                trace["intent"] = entry.data

            elif entry.type == "objective":
                trace["objective"] = entry.data

            elif entry.type == "plan":
                trace["plan"] = entry.data

            elif entry.type == "execution_result":
                trace["result"] = entry.data

            elif entry.type == "error":
                trace["error"] = entry.data

        return trace

    # =========================================================
    # PRESENCE EVENT STREAM (SSE)
    # =========================================================

    def _send_sse_headers(self) -> None:
        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/event-stream; charset=utf-8",
        )

        self.send_header(
            "Cache-Control",
            "no-cache",
        )

        self.send_header(
            "Connection",
            "keep-alive",
        )

        self._write_cors_headers()

        self.end_headers()

    def _write_sse(
        self,
        event: str,
        data: Any,
    ) -> None:
        payload = json.dumps(
            self._json_safe(data),
            ensure_ascii=False,
        )

        message = (
            f"event: {event}\\n"
            f"data: {payload}\\n\\n"
        ).encode("utf-8")

        self.wfile.write(message)
        self.wfile.flush()

    def _handle_presence_events(self) -> None:
        event_queue: queue.Queue[PresenceEvent] = queue.Queue()
        closed = threading.Event()

        def listener(event: PresenceEvent) -> None:
            if not closed.is_set():
                event_queue.put(event)

        unsubscribe = engine.presence_events.subscribe(listener)

        try:
            self._send_sse_headers()

            # Confirma que el canal está conectado.
            self._write_sse(
                "connected",
                {
                    "state": "connected",
                    "message": "Presence Event Stream conectado.",
                },
            )

            while True:
                try:
                    event = event_queue.get(
                        timeout=15.0,
                    )

                    self._write_sse(
                        "presence",
                        event.to_dict(),
                    )

                except queue.Empty:
                    # Keep-alive para mantener abierta
                    # la conexión SSE.
                    self.wfile.write(
                        b": keep-alive\\n\\n"
                    )
                    self.wfile.flush()

        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            closed.set()
            unsubscribe()

    # =========================================================
    # OPTIONS
    # =========================================================

    def do_OPTIONS(self) -> None:
        if self._reject_untrusted_request():
            return

        self.send_response(204)
        self._write_cors_headers()
        self.end_headers()

    # =========================================================
    # GET
    # =========================================================

    def do_GET(self) -> None:

        if self._reject_untrusted_request():
            return

        # -----------------------------------------------------
        # REMINDERS
        # -----------------------------------------------------

        if urlsplit(self.path).path == "/api/reminders":
            reminders = assistant_services.reminder_store.list()

            self._send_json({
                "success": True,
                "reminders": [
                    self._reminder_to_dict(reminder)
                    for reminder in reminders
                ],
            })
            return

        # -----------------------------------------------------
        # PRESENCE EVENT STREAM
        # -----------------------------------------------------

        if self.path == "/api/presence/events":
            self._handle_presence_events()
            return

        # -----------------------------------------------------
        # Console HTML legacy
        # -----------------------------------------------------

        if self.path in (
            "/",
            "/index.html",
        ):

            index_file = (
                BASE_DIR / "index.html"
            )

            content = index_file.read_bytes()

            self._send_html(content)

            return

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        if self.path == "/api/status":

            self._send_json(
                {
                    "status": "online",
                    "memory": engine.memory.count(),
                }
            )

            return

        # -----------------------------------------------------
        # PRESENCE
        # -----------------------------------------------------

        if self.path == "/api/presence":

            snapshot = presence.snapshot()

            self._send_json(
                snapshot
            )

            return

        # -----------------------------------------------------
        # MEMORY
        # -----------------------------------------------------

        if self.path == "/api/memory":

            entries = [
                self._entry_to_dict(entry)
                for entry in engine.memory.all()
            ]

            self._send_json(
                {
                    "entries": entries,
                    "count": len(entries),
                }
            )

            return

        self.send_error(404)

    # =========================================================
    # LEARNING CANDIDATE PROMOTION
    # =========================================================

    def _handle_learning_candidate_promote(self) -> None:
        try:
            content_length = int(
                self.headers.get("Content-Length", "0")
            )
            if content_length <= 0:
                self._send_json(
                    {"success": False, "message": "El cuerpo JSON es obligatorio."},
                    status=400,
                )
                return
            if content_length > MAX_REQUEST_BODY_BYTES:
                self._send_json(
                    {"success": False, "message": "El cuerpo supera el límite de 1 MiB."},
                    status=413,
                )
                return

            body = self.rfile.read(content_length)
            candidate = json.loads(body.decode("utf-8"))

            if not isinstance(candidate, dict):
                self._send_json(
                    {"success": False, "message": "Learning candidate must be an object."},
                    status=400,
                )
                return

            candidate_id = candidate.get("id")
            knowledge = candidate.get("knowledge")
            insight_id = candidate.get("insightId")
            source_cycle_ids = candidate.get("sourceCycleIds")
            evidence_keys = candidate.get("evidenceKeys")

            if not isinstance(candidate_id, str) or not candidate_id.strip():
                self._send_json(
                    {"success": False, "message": "Candidate id is required."},
                    status=400,
                )
                return

            if not isinstance(knowledge, str) or not knowledge.strip():
                self._send_json(
                    {"success": False, "message": "Candidate knowledge is required."},
                    status=400,
                )
                return

            if not isinstance(insight_id, str) or not insight_id.strip():
                self._send_json(
                    {"success": False, "message": "Insight id is required."},
                    status=400,
                )
                return

            if not isinstance(source_cycle_ids, list):
                source_cycle_ids = []

            if not isinstance(evidence_keys, list):
                evidence_keys = []

            memory_key = f"insight:{candidate_id}"

            with engine_lock:
                fact = engine.semantic_memory.learn(
                    memory_key,
                    "cognitive_pattern",
                    knowledge.strip(),
                    confidence=0.85,
                    source="cognitive_insight",
                    metadata={
                        "candidate_id": candidate_id,
                        "insight_id": insight_id,
                        "source_cycle_ids": [str(item) for item in source_cycle_ids],
                        "evidence_keys": [str(item) for item in evidence_keys],
                        "promoted_from": "console_learning_candidate",
                    },
                )

            self._send_json(
                {
                    "success": True,
                    "memory_key": memory_key,
                    "promoted_at": datetime.now().astimezone().isoformat(),
                    "fact": fact,
                }
            )

        except json.JSONDecodeError:
            self._send_json(
                {"success": False, "message": "Invalid JSON."},
                status=400,
            )
        except Exception as exc:
            self._send_json(
                {"success": False, "message": str(exc)},
                status=500,
            )

    # =========================================================
    # REMINDER CREATION
    # =========================================================

    def _handle_reminder_create(self) -> None:
        try:
            content_length = int(
                self.headers.get("Content-Length", "0")
            )
            if content_length <= 0:
                self._send_json({
                    "success": False,
                    "message": "El cuerpo JSON es obligatorio.",
                }, status=400)
                return
            if content_length > MAX_REQUEST_BODY_BYTES:
                self._send_json({
                    "success": False,
                    "message": "El cuerpo supera el límite de 1 MiB.",
                }, status=413)
                return

            body = self.rfile.read(content_length)
            payload = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            self._send_json({
                "success": False,
                "message": "El cuerpo debe contener JSON válido.",
            }, status=400)
            return

        if not isinstance(payload, dict):
            self._send_json({
                "success": False,
                "message": "El cuerpo debe ser un objeto JSON.",
            }, status=400)
            return

        message = payload.get("message")
        trigger_raw = payload.get("trigger_at")

        if not isinstance(message, str) or not message.strip():
            self._send_json({
                "success": False,
                "message": "El campo 'message' es obligatorio.",
            }, status=400)
            return

        if not isinstance(trigger_raw, str):
            self._send_json({
                "success": False,
                "message": "El campo 'trigger_at' es obligatorio.",
            }, status=400)
            return

        try:
            trigger_at = datetime.fromisoformat(
                trigger_raw.replace("Z", "+00:00")
            )
        except ValueError:
            self._send_json({
                "success": False,
                "message": "La fecha debe tener formato ISO 8601.",
            }, status=400)
            return

        if trigger_at.tzinfo is None or trigger_at.utcoffset() is None:
            self._send_json({
                "success": False,
                "message": "La fecha debe incluir zona horaria.",
            }, status=400)
            return

        trigger_at = trigger_at.astimezone(timezone.utc)

        if trigger_at <= datetime.now(timezone.utc):
            self._send_json({
                "success": False,
                "message": "La fecha debe ser futura.",
            }, status=400)
            return

        reminder = Reminder.create(
            message=message.strip(),
            trigger_at=trigger_at,
        )

        store = assistant_services.reminder_store
        scheduler = assistant_services.reminder_scheduler

        try:
            store.add(reminder)
            scheduler.schedule(reminder)
        except Exception:
            try:
                scheduler.cancel(reminder.id)
            except Exception:
                pass

            store.remove(reminder.id)

            self._send_json({
                "success": False,
                "message": "No se pudo programar el recordatorio.",
            }, status=500)
            return

        self._send_json({
            "success": True,
            "reminder": self._reminder_to_dict(reminder),
        }, status=201)

    # =========================================================
    # POST
    # =========================================================

    def do_POST(self) -> None:

        if self._reject_untrusted_request():
            return

        if urlsplit(self.path).path == "/api/reminders":
            self._handle_reminder_create()
            return

        if self.path == "/api/learning/candidates/promote":
            self._handle_learning_candidate_promote()
            return

        if self.path != "/api/execute":

            self.send_error(404)

            return

        try:

            # -------------------------------------------------
            # BODY
            # -------------------------------------------------

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )
            if content_length <= 0:
                self._send_json(
                    {"success": False, "message": "El cuerpo JSON es obligatorio."},
                    status=400,
                )
                return
            if content_length > MAX_REQUEST_BODY_BYTES:
                self._send_json(
                    {"success": False, "message": "El cuerpo supera el límite de 1 MiB."},
                    status=413,
                )
                return

            body = self.rfile.read(
                content_length
            )

            payload = json.loads(
                body.decode("utf-8")
            )

            text = payload.get("text")

            # -------------------------------------------------
            # VALIDATION
            # -------------------------------------------------

            if not isinstance(
                text,
                str,
            ):

                self._send_json(
                    {
                        "success": False,
                        "message": (
                            "El campo 'text' "
                            "es obligatorio."
                        ),
                    },
                    400,
                )

                return

            text = text.strip()

            if not text:

                self._send_json(
                    {
                        "success": False,
                        "message": (
                            "La instrucción "
                            "no puede estar vacía."
                        ),
                    },
                    400,
                )

                return

            # -------------------------------------------------
            # EXECUTION
            # -------------------------------------------------

            with engine_lock:

                # Memoria antes
                memory_before = (
                    engine.memory.count()
                )

                # Ejecutar NEXUS
                result = asyncio.run(
                    engine.execute(text)
                )

                # Memoria después
                memory_after = (
                    engine.memory.count()
                )

                # Entradas generadas
                all_entries = (
                    engine.memory.all()
                )

                execution_entries = (
                    all_entries[
                        memory_before:
                        memory_after
                    ]
                )

                # Trace
                trace = self._build_trace(
                    execution_entries
                )

            # -------------------------------------------------
            # PUBLIC RESPONSE
            # -------------------------------------------------

            response_text = (
                result.metadata.get(
                    "response"
                )
                if isinstance(
                    result.metadata,
                    dict,
                )
                else None
            )

            if not isinstance(
                response_text,
                str,
            ) or not response_text.strip():

                response_text = result.message

            self._send_json(
                {
                    "success": result.success,
                    "message": response_text,
                    "output": result.output,
                    "artifacts": result.artifacts,
                    "metadata": result.metadata,
                    "execution_time": result.execution_time,
                    "memory_count": (
                        engine.memory.count()
                    ),
                    "trace": trace,
                }
            )

        except Exception as exc:

            self._send_json(
                {
                    "success": False,
                    "message": (
                        f"Error interno: {exc}"
                    ),
                },
                500,
            )

    # =========================================================
    # REMINDER CANCELLATION
    # =========================================================

    def do_DELETE(self) -> None:

        if self._reject_untrusted_request():
            return
        path = unquote(urlsplit(self.path).path)
        prefix = "/api/reminders/"

        if not path.startswith(prefix):
            self.send_error(404)
            return

        reminder_id = path[len(prefix):].strip()

        if not reminder_id or "/" in reminder_id:
            self._send_json({
                "success": False,
                "message": "ID de recordatorio inválido.",
            }, status=400)
            return

        store = assistant_services.reminder_store
        scheduler = assistant_services.reminder_scheduler
        reminder = store.get(reminder_id)

        if reminder is None:
            self._send_json({
                "success": False,
                "message": "Recordatorio no encontrado.",
            }, status=404)
            return

        if reminder.status is not ReminderStatus.PENDING:
            self._send_json({
                "success": False,
                "message": "Solo se pueden cancelar recordatorios pendientes.",
                "status": reminder.status.value,
            }, status=409)
            return

        try:
            scheduler.cancel(reminder_id)
        except InvalidReminderTransition:
            self._send_json({
                "success": False,
                "message": "El estado del recordatorio cambió y no puede cancelarse.",
            }, status=409)
            return
        except Exception:
            self._send_json({
                "success": False,
                "message": "No se pudo cancelar el recordatorio.",
            }, status=500)
            return

        updated = store.get(reminder_id)

        if updated is None or updated.status is not ReminderStatus.CANCELLED:
            self._send_json({
                "success": False,
                "message": "No se pudo confirmar la cancelación.",
            }, status=500)
            return

        self._send_json({
            "success": True,
            "reminder": self._reminder_to_dict(updated),
        })

    # =========================================================
    # LOG
    # =========================================================

    def log_message(
        self,
        format,
        *args,
    ) -> None:

        print(
            f"[NEXUS] {format % args}"
        )


# =============================================================
# SERVER
# =============================================================




def main() -> None:
    server = ThreadingHTTPServer(
        (HOST, PORT),
        NexusHandler,
    )

    # Bucle asyncio persistente para los servicios del asistente.
    assistant_loop = asyncio.new_event_loop()

    def run_assistant_loop() -> None:
        asyncio.set_event_loop(assistant_loop)
        assistant_loop.run_forever()

    assistant_thread = threading.Thread(
        target=run_assistant_loop,
        name="nexus-assistant-services",
        daemon=True,
    )

    assistant_thread.start()

    try:
        # Iniciar los servicios dentro del bucle persistente.
        asyncio.run_coroutine_threadsafe(
            assistant_lifecycle.start(),
            assistant_loop,
        ).result()

        print("✓ Reminder Store")
        print("✓ Reminder Scheduler")
        print(f"✓ Servidor HTTP activo en http://{HOST}:{PORT}")

        server.serve_forever()

    except KeyboardInterrupt:
        print()
        print("NEXUS detenido.")

    finally:
        server.server_close()

        try:
            if assistant_loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    assistant_lifecycle.stop(),
                    assistant_loop,
                ).result(timeout=10)

        finally:
            if assistant_loop.is_running():
                assistant_loop.call_soon_threadsafe(
                    assistant_loop.stop
                )

            assistant_thread.join(timeout=10)

            if not assistant_thread.is_alive():
                assistant_loop.close()

            close_semantic_memory = getattr(
                engine.semantic_memory,
                "close",
                None,
            )

            if callable(close_semantic_memory):
                close_semantic_memory()


if __name__ == "__main__":
    main()
