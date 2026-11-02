from fastapi import WebSocket

class WSManager:

    def __init__(self):
        self.clients: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.append(ws)
        print(f"🟢 WS conectado | Total: {len(self.clients)}")

    def disconnect(self, ws: WebSocket):
        if ws in self.clients:
            self.clients.remove(ws)
            print(f"🔌 WS desconectado | Total: {len(self.clients)}")

    async def broadcast(self, data):

        print(f"📡 Broadcasting: {data}")

        disconnected = []

        for c in self.clients:
            try:
                await c.send_json(data)
            except Exception as e:
                print("❌ Error WS:", e)
                disconnected.append(c)

        # limpiar conexiones muertas
        for d in disconnected:
            self.disconnect(d)


manager = WSManager()