import { useEffect, useState } from "react";
import { connectWS } from "../../services/ws";

export default function RealtimePanel({ jobId }) {

  const [logs, setLogs] = useState([]);

  useEffect(() => {
    connectWS((msg) => {

      // filtrar por job
      if (jobId && msg.job_id !== jobId) return;

      setLogs(prev => [msg, ...prev].slice(0, 50));
    });
  }, [jobId]);

  return (
    <div style={{
      background: "#000",
      color: "#0f0",
      padding: 10,
      borderRadius: 8,
      marginTop: 20
    }}>
      <h3>Realtime Logs</h3>

      {logs.map((l, i) => (
        <div key={i}>
          [{l.type}] {l.message || ""}
        </div>
      ))}
    </div>
  );
}