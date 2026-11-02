from plugins.sdk.base import NexusPlugin


class Plugin(NexusPlugin):

    name = "hello"
    description = "plugin demo"

    def __init__(self, api):
        self.api = api

    def actions(self):

        return {
            "hello_world": self.hello
        }

    def hello(self, value):
        return "Hola desde plugin externo!"
