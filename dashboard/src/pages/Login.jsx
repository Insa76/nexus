import { useState } from "react";

const API = "http://127.0.0.1:8010";

export default function Login() {

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const login = async () => {

    if (!username || !password) {
      setError("Completá usuario y contraseña");
      return;
    }

    setLoading(true);
    setError(null);

    try {

      const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error en login");
      }

      const data = await res.json();

      // guardar sesión
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));

      // redirigir
      window.location.href = "/";

    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      gap: 10,
      maxWidth: 300,
      margin: "100px auto"
    }}>

      <h2>Login Nexus</h2>

      <input
        placeholder="Usuario"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />

      <input
        placeholder="Contraseña"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button onClick={login} disabled={loading}>
        {loading ? "Ingresando..." : "Login"}
      </button>

      {error && (
        <div style={{ color: "red", fontSize: 14 }}>
          {error}
        </div>
      )}

    </div>
  );
}