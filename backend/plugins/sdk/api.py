from actions.system_actions import execute_action


class NexusAPI:

    def run(self, action, value, user=None):
        return execute_action(action, value, user)

    def log(self, text):
        print("[PLUGIN]", text)
