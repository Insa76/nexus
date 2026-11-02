import asyncio
import inspect
from collections import defaultdict


class EventBus:

    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, event_type: str, handler):
        self.listeners[event_type].append(handler)

    async def publish(self, event_type: str, payload: dict):

        if event_type not in self.listeners:
            return

        for handler in self.listeners[event_type]:

            asyncio.create_task(
                self._safe_execute(handler, event_type, payload)
            )

    async def _safe_execute(self, handler, event_type, payload):

        try:
            sig = inspect.signature(handler)

            # Handler(event_type, payload)
            if len(sig.parameters) == 2:
                await handler(event_type, payload)

            # Handler(payload)
            else:
                await handler(payload)

        except Exception as e:
            print(f"⚠ Event handler error [{event_type}]:", e)


bus = EventBus()