from __future__ import annotations
import os
import re
from pathlib import Path

class WindowsFileOpener:
    """Abre archivos únicamente desde Escritorio, Documentos o Descargas."""
    def __init__(self, home: Path | None = None) -> None:
        self._home = (home or Path.home()).resolve()

    def open(self, file_name: str, location: str = "desktop", extension: str | None = None) -> bool:
        if not isinstance(file_name, str) or not file_name.strip():
            return False
        roots = {
            "desktop": self._home / "Desktop",
            "documents": self._home / "Documents",
            "downloads": self._home / "Downloads",
        }
        root = roots.get(str(location).lower())
        if root is None or not root.is_dir():
            return False
        root = root.resolve()
        requested = file_name.strip()
        if any(c in requested for c in '<>:"/\\\\|?*'):
            return False
        ext = "." + extension.lower().lstrip(".") if extension else None
        matches = []
        for current, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if not (Path(current) / d).is_symlink()]
            for name in names:
                candidate = Path(current) / name
                if ext and candidate.suffix.lower() != ext:
                    continue
                if candidate.stem.casefold() == requested.casefold() or candidate.name.casefold() == requested.casefold():
                    try:
                        resolved = candidate.resolve()
                        resolved.relative_to(root)
                    except (OSError, ValueError):
                        continue
                    matches.append(resolved)
                    if len(matches) > 1:
                        return False
        if len(matches) != 1 or not matches[0].is_file():
            return False
        try:
            os.startfile(str(matches[0]))  # type: ignore[attr-defined]
            return True
        except (OSError, AttributeError):
            return False
