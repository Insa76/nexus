import importlib
import pkgutil


def load_plugins():

    for loader, name, is_pkg in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{name}")