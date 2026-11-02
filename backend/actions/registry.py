ACTIONS = {}


def register_action(name, fn):
    ACTIONS[name] = fn


def get_action(name):
    return ACTIONS.get(name)