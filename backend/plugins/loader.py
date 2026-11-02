import importlib
import os

PLUGINS = {}


def load_plugins():

    folder = os.path.dirname(__file__)

    for f in os.listdir(folder):

        if f.endswith(".py") and f not in ["loader.py", "__init__.py"]:

            name = f[:-3]
            module = importlib.import_module(f"plugins.{name}")

            if hasattr(module, "register"):
                module.register(PLUGINS)

    print("Plugins cargados:", list(PLUGINS.keys()))


def run_plugin(action, value):

    if action in PLUGINS:
        return PLUGINS[action](value)

    return None
