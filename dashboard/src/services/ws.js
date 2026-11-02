let socket;

export function connectWS(onMessage) {
  socket = new WebSocket("ws://localhost:8010/ws");

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
}