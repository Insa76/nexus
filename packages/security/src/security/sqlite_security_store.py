
from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path

from security.assignments import ActorRoleAssignment
from security.models import Actor, ActorType
from security.permissions import Permission, PermissionAction
from security.roles import Role


class SQLiteSecurityStore:
    """Persistencia local de roles y asignaciones de Security."""

    def __init__(self, database_path: str | Path) -> None:
        requested_path = str(database_path)
        self._uri = requested_path == ":memory:"
        self._anchor: sqlite3.Connection | None = None

        if self._uri:
            self._database_path = (
                f"file:nexus_security_{uuid.uuid4().hex}"
                "?mode=memory&cache=shared"
            )
            # Mantiene viva la base compartida mientras exista el store.
            self._anchor = sqlite3.connect(
                self._database_path,
                uri=True,
            )
        else:
            self._database_path = requested_path
            Path(self._database_path).parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self._database_path,
            uri=self._uri,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS security_roles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS security_role_permissions (
                    role_id TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    action TEXT NOT NULL,
                    PRIMARY KEY (role_id, resource, action),
                    FOREIGN KEY (role_id)
                        REFERENCES security_roles(id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS security_assignments (
                    actor_id TEXT NOT NULL,
                    actor_type TEXT NOT NULL,
                    actor_name TEXT,
                    role_id TEXT NOT NULL,
                    PRIMARY KEY (actor_id, actor_type, role_id),
                    FOREIGN KEY (role_id)
                        REFERENCES security_roles(id)
                        ON DELETE CASCADE
                );
                """
            )

    def save_role(self, role: Role) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO security_roles (id, name)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET name = excluded.name
                """,
                (role.id, role.name),
            )

            connection.execute(
                """
                DELETE FROM security_role_permissions
                WHERE role_id = ?
                """,
                (role.id,),
            )

            connection.executemany(
                """
                INSERT INTO security_role_permissions
                    (role_id, resource, action)
                VALUES (?, ?, ?)
                """,
                [
                    (role.id, permission.resource, permission.action.value)
                    for permission in sorted(
                        role.permissions,
                        key=lambda item: (
                            item.resource,
                            item.action.value,
                        ),
                    )
                ],
            )

    def get_role(self, role_id: str) -> Role | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, name FROM security_roles WHERE id = ?",
                (role_id,),
            ).fetchone()

            if row is None:
                return None

            permission_rows = connection.execute(
                """
                SELECT resource, action
                FROM security_role_permissions
                WHERE role_id = ?
                ORDER BY resource, action
                """,
                (role_id,),
            ).fetchall()

        permissions = frozenset(
            Permission(
                resource=item["resource"],
                action=PermissionAction(item["action"]),
            )
            for item in permission_rows
        )

        return Role(
            id=row["id"],
            name=row["name"],
            permissions=permissions,
        )

    def list_roles(self) -> tuple[Role, ...]:
        with self._connect() as connection:
            role_ids = connection.execute(
                "SELECT id FROM security_roles ORDER BY rowid"
            ).fetchall()

        roles = (self.get_role(row["id"]) for row in role_ids)
        return tuple(role for role in roles if role is not None)

    def delete_role(self, role_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM security_roles WHERE id = ?",
                (role_id,),
            )
            return cursor.rowcount > 0

    def save_assignment(
        self,
        assignment: ActorRoleAssignment,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO security_assignments
                    (actor_id, actor_type, actor_name, role_id)
                VALUES (?, ?, ?, ?)
                """,
                (
                    assignment.actor.id,
                    assignment.actor.actor_type.value,
                    assignment.actor.name,
                    assignment.role.id,
                ),
            )

    def list_assignments(self) -> tuple[ActorRoleAssignment, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT actor_id, actor_type, actor_name, role_id
                FROM security_assignments
                ORDER BY rowid
                """
            ).fetchall()

        assignments: list[ActorRoleAssignment] = []

        for row in rows:
            role = self.get_role(row["role_id"])
            if role is None:
                continue

            assignments.append(
                ActorRoleAssignment(
                    actor=Actor(
                        id=row["actor_id"],
                        actor_type=ActorType(row["actor_type"]),
                        name=row["actor_name"],
                    ),
                    role=role,
                )
            )

        return tuple(assignments)

    def delete_assignment(
        self,
        assignment: ActorRoleAssignment,
    ) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM security_assignments
                WHERE actor_id = ?
                  AND actor_type = ?
                  AND role_id = ?
                """,
                (
                    assignment.actor.id,
                    assignment.actor.actor_type.value,
                    assignment.role.id,
                ),
            )
            return cursor.rowcount > 0
