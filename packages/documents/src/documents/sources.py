from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentSource:
    scheme: str
    location: str

    @classmethod
    def from_location(cls, location: str) -> "DocumentSource":
        value = location.strip()

        if not value:
            raise ValueError(
                "Document source location cannot be empty"
            )

        # Windows drive path:
        # C:/archivo.txt
        # C:\archivo.txt
        if (
            len(value) >= 2
            and value[0].isalpha()
            and value[1] == ":"
        ):
            return cls(
                scheme="local",
                location=value,
            )

        # Plain local path.
        if ":" not in value:
            return cls(
                scheme="local",
                location=value,
            )

        scheme, source_location = value.split(
            ":",
            1,
        )

        scheme = scheme.strip().lower()
        source_location = source_location.strip()

        if not scheme:
            raise ValueError(
                "Document source scheme cannot be empty"
            )

        if not source_location:
            raise ValueError(
                "Document source location cannot be empty"
            )

        return cls(
            scheme=scheme,
            location=source_location,
        )
