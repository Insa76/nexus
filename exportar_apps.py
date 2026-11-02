from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "NEXUS_APPS_PARTES"
OUTPUT.mkdir(exist_ok=True)

EXCLUDED = {
    "node_modules", "dist", "build", ".git",
    ".next", ".venv", "venv", "__pycache__",
    ".pytest_cache", "coverage", ".turbo"
}

EXCLUDED_EXT = {
    ".pyc", ".zip", ".7z", ".rar", ".gz"
}

MAX_BYTES = 35 * 1024 * 1024

APP_DIRS = [
    "apps", "backend", "dashboard", "desktop",
    "electron", "landing", "nexus-mobile"
]

files = []

for folder in APP_DIRS:
    base = ROOT / folder
    if not base.exists():
        continue

    for p in base.rglob("*"):
        if not p.is_file():
            continue

        rel = p.relative_to(ROOT)

        if any(part in EXCLUDED for part in rel.parts):
            continue

        if p.suffix.lower() in EXCLUDED_EXT:
            continue

        if p.name == ".env":
            continue

        if p.name.startswith(".env.") and p.name != ".env.example":
            continue

        files.append((p, rel, p.stat().st_size))

parts = []
current = []
current_size = 0

for item in files:
    path, rel, size = item

    if current and current_size + size > MAX_BYTES:
        parts.append(current)
        current = []
        current_size = 0

    current.append(item)
    current_size += size

if current:
    parts.append(current)

for index, group in enumerate(parts, 1):
    destination = OUTPUT / f"NEXUS_APPS_PARTE_{index:02}.zip"

    with zipfile.ZipFile(
        destination, "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6
    ) as z:
        for path, rel, size in group:
            z.write(path, rel)

    print(
        f"{destination.name} | "
        f"{destination.stat().st_size / 1024 / 1024:.1f} MB | "
        f"{len(group)} archivos"
    )

print(f"\nTotal de partes: {len(parts)}")
print(f"Carpeta: {OUTPUT}")
