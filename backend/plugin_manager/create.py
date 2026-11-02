TEMPLATE = """
from plugins.sdk.base import NexusPlugin

class Plugin(NexusPlugin):

    name = "{name}"
    description = "custom plugin"

    def __init__(self, api):
        self.api = api

    def actions(self):
        return {{}}
"""

def create(name):

    with open(f"plugins/installed/{name}.py","w") as f:
        f.write(TEMPLATE.format(name=name))
