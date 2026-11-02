import { useState } from "react";

export default function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const register = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:8010/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          password,
          tenant_id: "default", // 🔥 importante para tu sistema multi-tenant
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Error al registrarse");
        return;
      }

      // ✔ opcional: autologin después de registrar
      if (data.token) {
        localStorage.setItem("token", data.token);
        window.location.href = "/";
      } else {
        window.location.href = "/login";
      }

    } catch (err) {
      setError("Error de conexión con el servidor");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 40, maxWidth: 300 }}>

      <h2>Crear cuenta</h2>

      <input
        placeholder="Usuario"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />

      <input
        placeholder="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button onClick={register} disabled={loading}>
        {loading ? "Creando..." : "Registrarse"}
      </button>

      {error && (
        <div style={{ color: "red", marginTop: 10 }}>
          {error}
        </div>
      )}

    </div>
  );
}