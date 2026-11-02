import { useEffect, useState } from "react";
import { authFetch } from "../services/auth";
import Navbar from "../components/Navbar";

import JobsPanel from "../features/jobs/JobsPanel";
import MissionControl from "../features/system/MissionControl";
import RealtimePanel from "../features/jobs/RealtimePanel";

export default function Dashboard() {

  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    authFetch("http://localhost:8010/metrics")
      .then(res => res.json())
      .then(setMetrics);
  }, []);

  if (!metrics) return <div style={{ padding: 20 }}>Cargando sistema...</div>;

  return (
    <div>

      {/* 🔥 NAVBAR */}
      <Navbar />

      <div style={{ padding: 20 }}>

        {/* 🔥 NEXUS CONTROL (RECUPERADO) */}
        <h1 style={{ marginBottom: 20 }}>🧠 Nexus Control</h1>

        <div style={{ display: "flex", gap: 20 }}>
          <Card title="Jobs activos" value={metrics.active_jobs} />
          <Card title="Errores" value={metrics.counters?.errors || 0} />
          <Card
            title="Circuit"
            value={metrics.circuit_state?.state || "unknown"}
          />
        </div>

        {/* 🔥 SYSTEM CONTROL */}
        <div style={{ marginTop: 30 }}>
          <MissionControl />
        </div>

        {/* 🔥 JOBS */}
        <div style={{ marginTop: 30 }}>
          <JobsPanel />
        </div>

        <RealtimePanel />

        {/* 🔥 DEBUG / LOG */}
        <h2 style={{ marginTop: 30 }}>Actividad</h2>

        <pre style={{
          background: "#111",
          color: "#0f0",
          padding: 10,
          borderRadius: 8
        }}>
          {JSON.stringify(metrics, null, 2)}
        </pre>

      </div>
    </div>
  );
}

function Card({ title, value }) {

  const display =
    typeof value === "object"
      ? JSON.stringify(value)
      : value;

  return (
    <div style={{
      background: "#1a1a1a",
      padding: 20,
      borderRadius: 10,
      minWidth: 150
    }}>
      <div style={{ fontSize: 12, color: "#aaa" }}>{title}</div>
      <div style={{ fontSize: 22 }}>{display}</div>
    </div>
  );
}