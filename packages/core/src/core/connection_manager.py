from __future__ import annotations

from fastapi import WebSocket
from fastapi import WebSocketDisconnect


class ConnectionManager:
    """
    Administra las conexiones WebSocket activas del Kernel.

    Responsabilidades:
    - aceptar conexiones
    - cerrar conexiones
    - enviar mensajes a todos los clientes

    No conoce lógica de negocio.
    No conoce IA.
    No conoce eventos.
    """

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    @property
    def count(self) -> int:
        """Cantidad de clientes conectados."""
        return len(self._connections)

    async def connect(self, websocket: WebSocket) -> None:
        """
        Acepta una nueva conexión.
        """

        await websocket.accept()

        self._connections.append(websocket)

        print(f"[Kernel] Client connected ({self.count})")

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Elimina una conexión.
        """

        if websocket in self._connections:
            self._connections.remove(websocket)

        print(f"[Kernel] Client disconnected ({self.count})")

    async def broadcast(self, message: dict) -> None:
        """
        Envía un mensaje a todos los clientes conectados.

        Las conexiones inválidas son eliminadas automáticamente.
        """

        disconnected: list[WebSocket] = []

        for websocket in self._connections:

            try:
                await websocket.send_json(message)

            except WebSocketDisconnect:
                disconnected.append(websocket)

            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)