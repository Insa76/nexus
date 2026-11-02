from pathlib import Path
import zipfile
import subprocess

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "NEXUS_ENTREGA"

OUTPUT.mkdir(exist_ok=True)

EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "node_modules",
    "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".next", ".turbo", ".cache",
    "coverage", "htmlcov"
}

EXCLUDED_SUFFIXES = {
    ".pyc", ".pyo", ".zip", ".7z", ".rar",
    ".tar", ".gz"
}

GROUPS = {
    "01_CORE": ["packages", "tests", "docs"],
    "02_APPS": [
        "apps", "backend", "dashboard",
        "desktop", "electron", "landing", "nexus-mobile"
    ],
}

def include_file(path):
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False

    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False

    if path.name == ".env":
        return False

    if path.name.startswith(".env.") and path.name != ".env.example":
        return False

    return True

def add_path(archive, path):
    if not path.exists():
        return

    if path.is_file():
        if include_file(path.relative_to(ROOT)):
            archive.write(path, path.relative_to(ROOT))
        return

    for item in path.rglob("*"):
        if item.is_file() and include_file(item.relative_to(ROOT)):
            archive.write(item, item.relative_to(ROOT))

def create_archive(name, paths):
    destination = OUTPUT / f"NEXUS_{name}.zip"

    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED,
        compresslevel=6
    ) as archive:
        for relative in paths:
            add_path(archive, ROOT / relative)

    print(f"CREADO: {destination} ({destination.stat().st_size / 1024 / 1024:.1f} MB)")

# Paquete 1: motor, arquitectura y pruebas
create_archive("01_CORE", GROUPS["01_CORE"])

# Paquete 2: aplicaciones e interfaces
create_archive("02_APPS", GROUPS["02_APPS"])

# Paquete 3: todo el resto del proyecto y estado Git
excluded = set(GROUPS["01_CORE"] + GROUPS["02_APPS"])

remaining = [
    item.name for item in ROOT.iterdir()
    if item.name not in excluded
    and item.name != "exportar_nexus.py"
]

create_archive("03_RESTO", remaining)

# Estado Git para preservar los cambios locales
try:
    commands = [
        ["git", "status", "--short", "--branch"],
        ["git", "log", "-5", "--oneline"],
        ["git", "diff", "--stat"]
    ]

    report = []

    for command in commands:
        result = subprocess.run(
            command, cwd=ROOT, capture_output=True,
            text=True, encoding="utf-8", errors="replace"
        )
        report.append("$ " + " ".join(command))
        report.append(result.stdout)
        report.append(result.stderr)

    (OUTPUT / "NEXUS_GIT_STATE.txt").write_text(
        "\n".join(report), encoding="utf-8"
    )

except Exception as error:
    print("No se pudo obtener el estado Git:", error)

print("\nEXPORTACIÓN TERMINADA.")
print("Carpeta:", OUTPUT)