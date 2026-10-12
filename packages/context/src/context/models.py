from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class UserProfile:
    id: str
    name: str
    role: str | None = None
    organization_id: str | None = None
    preferences: dict[str, object] = field(default_factory=dict)
    responsibilities: tuple[str, ...] = ()
    priorities: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(
        cls,
        name: str,
        *,
        role: str | None = None,
        organization_id: str | None = None,
        preferences: dict[str, object] | None = None,
        responsibilities: tuple[str, ...] = (),
        priorities: tuple[str, ...] = (),
    ) -> "UserProfile":
        return cls(
            id=str(uuid4()),
            name=name,
            role=role,
            organization_id=organization_id,
            preferences=dict(preferences or {}),
            responsibilities=responsibilities,
            priorities=priorities,
        )


@dataclass(frozen=True)
class OrganizationProfile:
    id: str
    name: str
    industry: str | None = None
    description: str | None = None
    areas: tuple[str, ...] = ()
    rules: tuple[str, ...] = ()
    priorities: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(
        cls,
        name: str,
        *,
        industry: str | None = None,
        description: str | None = None,
        areas: tuple[str, ...] = (),
        rules: tuple[str, ...] = (),
        priorities: tuple[str, ...] = (),
        metadata: dict[str, object] | None = None,
    ) -> "OrganizationProfile":
        return cls(
            id=str(uuid4()),
            name=name,
            industry=industry,
            description=description,
            areas=areas,
            rules=rules,
            priorities=priorities,
            metadata=dict(metadata or {}),
        )


@dataclass(frozen=True)
class ProjectContext:
    id: str
    name: str
    organization_id: str
    description: str | None = None
    status: str = "active"
    responsible_user_ids: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(
        cls,
        name: str,
        organization_id: str,
        *,
        description: str | None = None,
        status: str = "active",
        responsible_user_ids: tuple[str, ...] = (),
        metadata: dict[str, object] | None = None,
    ) -> "ProjectContext":
        return cls(
            id=str(uuid4()),
            name=name,
            organization_id=organization_id,
            description=description,
            status=status,
            responsible_user_ids=responsible_user_ids,
            metadata=dict(metadata or {}),
        )


@dataclass(frozen=True)
class AssistantContext:
    user: UserProfile | None = None
    organization: OrganizationProfile | None = None
    projects: tuple[ProjectContext, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)

    def project(self, project_id: str) -> ProjectContext | None:
        for project in self.projects:
            if project.id == project_id:
                return project

        return None

    def to_dict(self) -> dict[str, object]:
        return {
            "user": (
                {
                    "id": self.user.id,
                    "name": self.user.name,
                    "role": self.user.role,
                    "organization_id": self.user.organization_id,
                    "preferences": dict(self.user.preferences),
                    "responsibilities": list(self.user.responsibilities),
                    "priorities": list(self.user.priorities),
                    "created_at": self.user.created_at.isoformat(),
                }
                if self.user is not None
                else None
            ),
            "organization": (
                {
                    "id": self.organization.id,
                    "name": self.organization.name,
                    "industry": self.organization.industry,
                    "description": self.organization.description,
                    "areas": list(self.organization.areas),
                    "rules": list(self.organization.rules),
                    "priorities": list(self.organization.priorities),
                    "metadata": dict(self.organization.metadata),
                    "created_at": self.organization.created_at.isoformat(),
                }
                if self.organization is not None
                else None
            ),
            "projects": [
                {
                    "id": project.id,
                    "name": project.name,
                    "organization_id": project.organization_id,
                    "description": project.description,
                    "status": project.status,
                    "responsible_user_ids": list(
                        project.responsible_user_ids
                    ),
                    "metadata": dict(project.metadata),
                    "created_at": project.created_at.isoformat(),
                }
                for project in self.projects
            ],
            "metadata": dict(self.metadata),
        }
