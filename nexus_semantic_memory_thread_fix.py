from pathlib import Path
from datetime import datetime
import re

root = Path.cwd()
target = root / 'packages' / 'memory' / 'src' / 'memory' / 'semantic_memory.py'
if not target.is_file():
    raise SystemExit(f'No se encontró el archivo: {target}')
text = target.read_text(encoding='utf-8')
if 'NEXUS_SEMANTIC_MEMORY_THREAD_FIX_V1' in text:
    raise SystemExit('La corrección de concurrencia ya parece aplicada; no se modificó ningún archivo.')
if 'sqlite3.connect(resolved_path, timeout=10.0, check_same_thread=False)' in text:
    raise SystemExit('La conexión ya tiene check_same_thread=False. No se modificó ningún archivo.')

# Add synchronization support.
text = text.replace('import json\nimport sqlite3\n', 'import json\nimport sqlite3\nimport threading\nfrom functools import wraps\n', 1)
anchor = '\n\n@dataclass\nclass SemanticFact:'
decorator = '''\n\ndef _thread_safe(method):\n    """Serializa el acceso a la conexión SQLite compartida."""\n    @wraps(method)\n    def wrapper(self, *args, **kwargs):\n        with self._lock:\n            return method(self, *args, **kwargs)\n    return wrapper\n'''
if anchor not in text:
    raise SystemExit('No se encontró el punto de inserción para el decorador; no se modificó ningún archivo.')
text = text.replace(anchor, decorator + anchor, 1)

old = '    def __init__(self, db_path: str | Path | None = None) -> None:\n        if db_path is None or str(db_path) == ":memory:":'
new = '    def __init__(self, db_path: str | Path | None = None) -> None:\n        # NEXUS_SEMANTIC_MEMORY_THREAD_FIX_V1\n        self._lock = threading.RLock()\n        if db_path is None or str(db_path) == ":memory:":'
if text.count(old) != 1:
    raise SystemExit('No se encontró la inicialización de SemanticMemory esperada; no se modificó ningún archivo.')
text = text.replace(old, new, 1)
text = text.replace('sqlite3.connect(resolved_path, timeout=10.0)', 'sqlite3.connect(resolved_path, timeout=10.0, check_same_thread=False)', 1)

methods = [
    '    def _initialize_schema(self) -> None:',
    '    def learn(\n',
    '    def get(self, subject: str, predicate: str) -> SemanticFact | None:',
    '    def find_by_subject(self, subject: str) -> list[SemanticFact]:',
    '    def find_by_predicate(self, predicate: str) -> list[SemanticFact]:',
    '    def all(self) -> list[SemanticFact]:',
    '    def count(self) -> int:',
    '    def forget(self, subject: str, predicate: str) -> bool:',
    '    def clear(self) -> None:',
    '    def close(self) -> None:',
]
for marker in methods:
    if text.count(marker) != 1:
        raise SystemExit(f'No se encontró un método único para sincronizar: {marker!r}. No se modificó ningún archivo.')
    text = text.replace(marker, '    @_thread_safe\n' + marker, 1)

# Syntax sanity check before writing.
compile(text, str(target), 'exec')
backup = target.with_name(target.name + '.bak-thread-fix-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.write_text(target.read_text(encoding='utf-8'), encoding='utf-8')
target.write_text(text, encoding='utf-8')
print('Corrección de concurrencia aplicada correctamente.')
print(f'Archivo modificado: {target}')
print(f'Copia de seguridad: {backup}')
print('La conexión permite uso entre hilos y las operaciones se serializan con RLock.')
