import { useEffect, useState } from "react";
import { authFetch } from "../services/auth";

export default function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = async () => {
    try {
      const res = await authFetch("http://localhost:8010/auth/users");
      const data = await res.json();
      setUsers(data);
    } catch (err) {
      console.error("Error cargando usuarios:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const deleteUser = async (username) => {
    try {
      await authFetch(`http://localhost:8010/auth/users/${username}`, {
        method: "DELETE",
      });

      // refrescar lista
      fetchUsers();

    } catch (err) {
      console.error("Error eliminando usuario:", err);
    }
  };

  if (loading) {
    return <div style={{ padding: 20 }}>Cargando usuarios...</div>;
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>Usuarios</h2>

      {users.length === 0 && (
        <div>No hay usuarios</div>
      )}

      {users.map((u) => (
        <div
          key={u.username}
          style={{
            marginBottom: 10,
            padding: 10,
            background: "#1a1a1a",
            borderRadius: 8,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}
        >
          <div>
            <b>{u.username}</b> ({u.role})
          </div>

          <button onClick={() => deleteUser(u.username)}>
            Eliminar
          </button>
        </div>
      ))}
    </div>
  );
}