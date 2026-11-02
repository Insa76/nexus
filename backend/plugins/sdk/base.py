class NexusPlugin:

    name = "base"
    description = "plugin"

    def actions(self):
        """
        devolver dict:
        {
            "action_name": function
        }
        """
        return {}

    def on_load(self):
        pass

    def on_unload(self):
        pass
