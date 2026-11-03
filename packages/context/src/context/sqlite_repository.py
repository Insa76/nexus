from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from context.models import (
    AssistantContext,
    OrganizationProfile,
    ProjectContext,
    UserProfile,
)


class ContextValidationError(ValueError):
    """Error de validación de un cambio de contexto."""


class SQLiteContextRepository:
    """
    Persistencia local del contexto operativo de NEXUS.

    La base vive fuera del repositorio y del directorio de ejecución:
    ~/.nexus/context.sqlite3 (o la ruta indicada por NEXUS_CONTEXT_DB_PATH).

    El repositorio conserva un perfil local, una organización activa y
    todos sus proyectos. Los identificadores son generados por el servidor;
    los IDs recibidos solo pueden seleccionar proyectos ya existentes.
    """

    _DEFAULT_STATE: dict[str, Any] = {
        "user": None,
        "organization": None,
        "projects": [],
        "active_project_id": None,
        "updated_at": None,
    }

    def __init__(self, db_path: str | Path | None = None) -> None:
        configured_path = (
            db_path
            or os.environ.get("NEXUS_CONTEXT_DB_PATH")
            or (Path.home() / ".nexus" / "context.sqlite3")
        )
        self._db_path = Path(configured_path).expanduser()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @property
    def db_path(self) -> Path:
        return self._db_path

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            str(self._db_path),
            timeout=10,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 10000")
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS nexus_context_state (
                    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO nexus_context_state
                    (singleton_id, payload, updated_at)
                VALUES (1, ?, ?)
                """,
                (
                    json.dumps(self._DEFAULT_STATE, ensure_ascii=False),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    @staticmethod
    def _clean_text(
        value: Any,
        field: str,
        *,
        required: bool = False,
        maximum: int = 2000,
    ) -> str | None:
        if value is None:
            if required:
                raise ContextValidationError(
                    f"El campo '{field}' es obligatorio."
                )
            return None
        if not isinstance(value, str):
            raise ContextValidationError(
                f"El campo '{field}' debe ser texto."
            )
        cleaned = value.strip()
        if required and not cleaned:
            raise ContextValidationError(
                f"El campo '{field}' no puede estar vacío."
            )
        if len(cleaned) > maximum:
            raise ContextValidationError(
                f"El campo '{field}' supera {maximum} caracteres."
            )
        return cleaned or None

    @classmethod
    def _clean_list(
        cls,
        value: Any,
        field: str,
    ) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ContextValidationError(
                f"El campo '{field}' debe ser una lista de textos."
            )
        if len(value) > 100:
            raise ContextValidationError(
                f"El campo '{field}' admite hasta 100 elementos."
            )
        result: list[str] = []
        for item in value:
            cleaned = cls._clean_text(
                item,
                field,
                required=True,
                maximum=500,
            )
            if cleaned:
                result.append(cleaned)
        return result

    @staticmethod
    def _clean_object(value: Any, field: str) -> dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ContextValidationError(
                f"El campo '{field}' debe ser un objeto."
            )
        try:
            encoded = json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise ContextValidationError(
                f"El campo '{field}' contiene datos no serializables."
            ) from exc
        if len(encoded.encode("utf-8")) > 32_000:
            raise ContextValidationError(
                f"El campo '{field}' supera el límite de 32 KiB."
            )
        return value

    def _read_state(self, connection: sqlite3.Connection) -> dict[str, Any]:
        row = connection.execute(
            """
            SELECT payload
            FROM nexus_context_state
            WHERE singleton_id = 1
            """
        ).fetchone()
        if row is None:
            return dict(self._DEFAULT_STATE)
        try:
            state = json.loads(row["payload"])
        except (TypeError, json.JSONDecodeError):
            state = dict(self._DEFAULT_STATE)
        if not isinstance(state, dict):
            state = dict(self._DEFAULT_STATE)
        for key, default in self._DEFAULT_STATE.items():
            state.setdefault(key, default)
        return state

    def get_state(self) -> dict[str, Any]:
        """Devuelve una copia JSON del contexto persistido."""
        with self._connect() as connection:
            state = self._read_state(connection)
        return json.loads(json.dumps(state, ensure_ascii=False))

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Actualiza el perfil y la selección activa.

        Formato admitido:
          {
            "user": {"name": "...", "role": "..."},
            "organization": {"name": "...", "industry": "..."},
            "project": {"id": opcional, "name": "...", "description": "..."},
            "active_project_id": "id-existente" | null
          }

        Los bloques omitidos conservan su valor. Enviar project sin ID crea
        un proyecto nuevo. Enviar project con ID solo modifica uno existente.
        """
        if not isinstance(payload, dict):
            raise ContextValidationError(
                "El cuerpo debe ser un objeto JSON."
            )

        allowed = {
            "user",
            "organization",
            "project",
            "active_project_id",
        }
        unknown = set(payload) - allowed
        if unknown:
            raise ContextValidationError(
                "Campos no permitidos: " + ", ".join(sorted(unknown))
            )

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            state = self._read_state(connection)

            user = state.get("user")
            organization = state.get("organization")
            projects = state.get("projects") or []
            active_project_id = state.get("active_project_id")

            if "organization" in payload:
                incoming = payload["organization"]
                if incoming is None:
                    organization = None
                    active_project_id = None
                else:
                    if not isinstance(incoming, dict):
                        raise ContextValidationError(
                            "El campo 'organization' debe ser un objeto."
                        )
                    organization = dict(organization or {})
                    organization["id"] = (
                        organization.get("id") or str(uuid4())
                    )
                    organization["name"] = self._clean_text(
                        incoming.get("name", organization.get("name")),
                        "organization.name",
                        required=True,
                        maximum=160,
                    )
                    for field in ("industry", "description"):
                        if field in incoming:
                            organization[field] = self._clean_text(
                                incoming[field],
                                f"organization.{field}",
                                maximum=2000,
                            )
                    for field in ("areas", "rules", "priorities"):
                        if field in incoming:
                            organization[field] = self._clean_list(
                                incoming[field],
                                f"organization.{field}",
                            )
                    organization.setdefault("industry", None)
                    organization.setdefault("description", None)
                    organization.setdefault("areas", [])
                    organization.setdefault("rules", [])
                    organization.setdefault("priorities", [])
                    organization.setdefault("metadata", {})

                    if (
                        active_project_id
                        and not any(
                            p.get("id") == active_project_id
                            and p.get("organization_id") == organization["id"]
                            for p in projects
                        )
                    ):
                        active_project_id = None

            if "user" in payload:
                incoming = payload["user"]
                if not isinstance(incoming, dict):
                    raise ContextValidationError(
                        "El campo 'user' debe ser un objeto."
                    )
                user = dict(user or {})
                user["id"] = user.get("id") or str(uuid4())
                user["name"] = self._clean_text(
                    incoming.get("name", user.get("name")),
                    "user.name",
                    required=True,
                    maximum=160,
                )
                if "role" in incoming:
                    user["role"] = self._clean_text(
                        incoming["role"],
                        "user.role",
                        maximum=160,
                    )
                if "preferences" in incoming:
                    user["preferences"] = self._clean_object(
                        incoming["preferences"],
                        "user.preferences",
                    )
                if "responsibilities" in incoming:
                    user["responsibilities"] = self._clean_list(
                        incoming["responsibilities"],
                        "user.responsibilities",
                    )
                if "priorities" in incoming:
                    user["priorities"] = self._clean_list(
                        incoming["priorities"],
                        "user.priorities",
                    )
                user.setdefault("role", None)
                user.setdefault("preferences", {})
                user.setdefault("responsibilities", [])
                user.setdefault("priorities", [])
                user.setdefault(
                    "created_at",
                    datetime.now(timezone.utc).isoformat(),
                )

            if user is not None:
                user["organization_id"] = (
                    organization.get("id")
                    if organization is not None
                    else None
                )

            if "project" in payload:
                incoming = payload["project"]
                if incoming is None:
                    active_project_id = None
                else:
                    if not isinstance(incoming, dict):
                        raise ContextValidationError(
                            "El campo 'project' debe ser un objeto."
                        )
                    if organization is None:
                        raise ContextValidationError(
                            "Primero debe configurarse una organización."
                        )
                    project_id = incoming.get("id")
                    existing = None
                    if project_id is not None:
                        existing = next(
                            (
                                item for item in projects
                                if item.get("id") == project_id
                                and item.get("organization_id") == organization["id"]
                            ),
                            None,
                        )
                        if existing is None:
                            raise ContextValidationError(
                                "El proyecto indicado no existe en la organización activa."
                            )
                    project = dict(existing or {})
                    project["id"] = (
                        existing.get("id")
                        if existing is not None
                        else str(uuid4())
                    )
                    project["organization_id"] = organization["id"]
                    project["name"] = self._clean_text(
                        incoming.get("name", project.get("name")),
                        "project.name",
                        required=True,
                        maximum=160,
                    )
                    for field in ("description", "status"):
                        if field in incoming:
                            project[field] = self._clean_text(
                                incoming[field],
                                f"project.{field}",
                                maximum=2000 if field == "description" else 80,
                            )
                    project.setdefault("description", None)
                    project.setdefault("status", "active")
                    project.setdefault("responsible_user_ids", [])
                    project.setdefault("metadata", {})
                    project.setdefault(
                        "created_at",
                        datetime.now(timezone.utc).isoformat(),
                    )
                    if existing is None:
                        projects.append(project)
                    else:
                        projects = [
                            project if item.get("id") == project["id"] else item
                            for item in projects
                        ]
                    active_project_id = project["id"]

            if "active_project_id" in payload:
                requested_id = payload["active_project_id"]
                if requested_id is None:
                    active_project_id = None
                elif not isinstance(requested_id, str):
                    raise ContextValidationError(
                        "active_project_id debe ser texto o null."
                    )
                elif organization is None or not any(
                    item.get("id") == requested_id
                    and item.get("organization_id") == organization["id"]
                    for item in projects
                ):
                    raise ContextValidationError(
                        "El proyecto activo no pertenece a la organización seleccionada."
                    )
                else:
                    active_project_id = requested_id

            state = {
                "user": user,
                "organization": organization,
                "projects": projects,
                "active_project_id": active_project_id,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            encoded = json.dumps(
                state,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            connection.execute(
                """
                UPDATE nexus_context_state
                SET payload = ?, updated_at = ?
                WHERE singleton_id = 1
                """,
                (encoded, state["updated_at"]),
            )
            connection.commit()

        return self.get_state()

    @staticmethod
    def _datetime(value: str | None) -> datetime:
        if not value:
            return datetime.now(timezone.utc)
        try:
            parsed = datetime.fromisoformat(value)
        except (TypeError, ValueError):
            return datetime.now(timezone.utc)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed

    def load_context(self) -> AssistantContext:
        """Reconstruye los modelos de dominio desde SQLite."""
        state = self.get_state()
        raw_user = state.get("user")
        raw_organization = state.get("organization")

        user = None
        if isinstance(raw_user, dict):
            user = UserProfile(
                id=raw_user["id"],
                name=raw_user["name"],
                role=raw_user.get("role"),
                organization_id=raw_user.get("organization_id"),
                preferences=dict(raw_user.get("preferences") or {}),
                responsibilities=tuple(raw_user.get("responsibilities") or []),
                priorities=tuple(raw_user.get("priorities") or []),
                created_at=self._datetime(raw_user.get("created_at")),
            )

        organization = None
        if isinstance(raw_organization, dict):
            organization = OrganizationProfile(
                id=raw_organization["id"],
                name=raw_organization["name"],
                industry=raw_organization.get("industry"),
                description=raw_organization.get("description"),
                areas=tuple(raw_organization.get("areas") or []),
                rules=tuple(raw_organization.get("rules") or []),
                priorities=tuple(raw_organization.get("priorities") or []),
                metadata=dict(raw_organization.get("metadata") or {}),
                created_at=self._datetime(raw_organization.get("created_at")),
            )

        projects: list[ProjectContext] = []
        if organization is not None:
            for raw_project in state.get("projects") or []:
                if (
                    not isinstance(raw_project, dict)
                    or raw_project.get("organization_id") != organization.id
                ):
                    continue
                projects.append(
                    ProjectContext(
                        id=raw_project["id"],
                        name=raw_project["name"],
                        organization_id=raw_project["organization_id"],
                        description=raw_project.get("description"),
                        status=raw_project.get("status", "active"),
                        responsible_user_ids=tuple(
                            raw_project.get("responsible_user_ids") or []
                        ),
                        metadata=dict(raw_project.get("metadata") or {}),
                        created_at=self._datetime(
                            raw_project.get("created_at")
                        ),
                    )
                )

        active_project_id = state.get("active_project_id")
        if not any(p.id == active_project_id for p in projects):
            active_project_id = None

        return AssistantContext(
            user=user,
            organization=organization,
            projects=tuple(projects),
            metadata={
                "active_project_id": active_project_id,
            },
        )
