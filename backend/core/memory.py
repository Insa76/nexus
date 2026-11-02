from datetime import datetime

class NexusMemory:

    def __init__(self):
        self.events = []

    def remember(self, event):

        self.events.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event
        })

        if len(self.events) > 100:
            self.events.pop(0)

    def last_events(self):
        return self.events[-10:]


memory = NexusMemory()