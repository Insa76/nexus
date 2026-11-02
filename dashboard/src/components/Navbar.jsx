export default function Navbar() {

  const user = JSON.parse(localStorage.getItem("user") || "{}");

  return (
    <div style={{
      display: "flex",
      justifyContent: "space-between",
      padding: 15,
      background: "#111",
      borderBottom: "1px solid #222"
    }}>

      <div>
        <b>Nexus</b>
      </div>

      <div>
        <a href="/" style={{ marginRight: 15 }}>Dashboard</a>
        <a href="/users" style={{ marginRight: 15 }}>Usuarios</a>
        <a href="/builder" style={{ marginRight: 15 }}>Builder</a>
        <span style={{ marginRight: 15 }}>{user.username}</span>
        <button onClick={()=>{
          localStorage.clear()
          window.location.href = "/login"
        }}>
          Logout
        </button>
      </div>

    </div>
  );
}