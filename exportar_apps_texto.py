
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "NEXUS_APPS_TEXTO"

FOLDERS = [
    "apps",
    "backend",
    "dashboard",
    "desktop",
    "electron",
    "landing",
    "nexus-mobile",
]

EXCLUDED_DIRS = {
    ".git", "node_modules", "dist", "build", ".next",
    ".venv", "venv", "__pycache__", ".pytest_cache",
    "coverage", ".turbo", ".cache", "vendor",
}

EXCLUDED_FILES = {
    ".env", ".env.local", ".env.production",
    ".env.development", ".env.test",
}

EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".html", ".css", ".scss", ".sass",
    ".json", ".jsonc", ".md", ".txt",
    ".yml", ".yaml", ".toml", ".ini",
    ".cfg", ".conf", ".sql", ".sh",
    ".bat", ".ps1", ".xml", ".svg",
    ".prisma", ".graphql", ".gql",
    ".vue", ".svelte", ".mjs", ".cjs",
    ".properties", ".gitignore", ".editorconfig",
    ".dockerignore", ".example",
}

SPECIAL_FILES = {
    "Dockerfile", "Makefile", "Procfile",
    "LICENSE", "README", "CHANGELOG",
    "requirements", "Pipfile", "Justfile",
}

MAX_CHARS = 350_000
PART = 0
CURRENT = []
CURRENT_SIZE = 0
TOTAL_FILES = 0
SKIPPED = 0


def write_part():
    global PART, CURRENT, CURRENT_SIZE

    if not CURRENT:
        return

    PART += 1
    path = OUTPUT / f"NEXUS_APPS_TEXTO_{PART:03}.txt"

    content = "\n".join(CURRENT)
    path.write_text(content, encoding="utf-8")

    print(f"Creado: {path.name} ({len(content):,} caracteres)")

    CURRENT = []
    CURRENT_SIZE = 0


def add_text(text):
    global CURRENT_SIZE

    while text:
        available = MAX_CHARS - CURRENT_SIZE

        if available <= 0:
            write_part()
            available = MAX_CHARS

        piece = text[:available]
        CURRENT.append(piece)
        CURRENT_SIZE += len(piece)
        text = text[available:]

        if CURRENT_SIZE >= MAX_CHARS:
            write_part()


def read_file(path):
    data = path.read_bytes()

    if b"\x00" in data:
        return None

    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue

    return None


def main():
    global TOTAL_FILES, SKIPPED

    OUTPUT.mkdir(exist_ok=True)

    add_text(
        "NEXUS - EXPORTACION DE CODIGO FUENTE\n"
        "Formato: texto UTF-8\n"
        "Cada archivo conserva su ruta original.\n\n"
    )

    for folder in FOLDERS:
        base = ROOT / folder

        if not base.exists():
            print(f"No encontrada: {folder}")
            continue

        print(f"Procesando: {folder}")

        for current_root, dirs, files in os.walk(base):
            dirs[:] = sorted(
                d for d in dirs
                if d not in EXCLUDED_DIRS
            )

            for filename in sorted(files):
                path = Path(current_root) / filename

                if filename in EXCLUDED_FILES:
                    SKIPPED += 1
                    continue

                if filename.startswith(".env."):
                    SKIPPED += 1
                    continue

                if (
                    path.suffix.lower() not in EXTENSIONS
                    and filename not in SPECIAL_FILES
                ):
                    SKIPPED += 1
                    continue

                try:
                    content = read_file(path)

                    if content is None:
                        SKIPPED += 1
                        continue

                    relative = path.relative_to(ROOT).as_posix()

                    header = (
                        "\n\n"
                        + "=" * 75 + "\n"
                        + f"ARCHIVO: {relative}\n"
                        + "=" * 75 + "\n\n"
                    )

                    add_text(header)
                    add_text(content)
                    add_text(
                        f"\n\n"
                        f"--- FIN DEL ARCHIVO: {relative} ---\n"
                    )

                    TOTAL_FILES += 1

                except Exception as error:
                    print(f"Error leyendo {path}: {error}")
                    SKIPPED += 1

    write_part()

    summary = (
        f"Archivos exportados: {TOTAL_FILES}\n"
        f"Archivos excluidos o no legibles: {SKIPPED}\n"
        f"Partes generadas: {PART}\n"
    )

    (OUTPUT / "RESUMEN.txt").write_text(
        summary, encoding="utf-8"
    )

    print("\nEXPORTACION FINALIZADA")
    print(summary)
    print(f"Resultado: {OUTPUT}")


if __name__ == "__main__":
    main()
