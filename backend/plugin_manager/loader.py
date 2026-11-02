import importlib.util
from pathlib import Path
from plugins.sdk.base import NexusPlugin
from plugins.sdk.api import NexusAPI

PLUGINS = {}


def load_installed():

    folder = Path("plugins/installed")

    for file in folder.glob("*.py"):

        spec = importlib.util.spec_from_file_location(file.stem, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "Plugin"):

            plugin = module.Plugin(NexusAPI())

            plugin.on_load()

            for name, fn in plugin.actions().items():
                PLUGINS[name] = fn

    print("Plugins activos:", list(PLUGINS.keys()))
