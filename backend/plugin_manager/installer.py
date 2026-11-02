import shutil
from pathlib import Path

BASE = Path("plugins")
INSTALLED = BASE / "installed"
MARKET = BASE / "marketplace"

INSTALLED.mkdir(exist_ok=True)
MARKET.mkdir(exist_ok=True)


def install_plugin(filename):

    src = MARKET / filename
    dst = INSTALLED / filename

    shutil.copy(src, dst)

    return f"{filename} instalado"


def remove_plugin(filename):

    f = INSTALLED / filename

    if f.exists():
        f.unlink()

    return f"{filename} eliminado"
