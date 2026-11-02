export default function App() {

  return (
    <div style={styles.page}>

      <section style={styles.hero}>
        <h1>Nexus AI</h1>
        <p>Tu asistente inteligente local, privado y autónomo.</p>

        <div style={{display:"flex", gap:10}}>
          <a href="http://localhost:5173">
            <button style={styles.primary}>Abrir Nexus</button>
          </a>

          <a href="http://localhost:5174">
            <button style={styles.secondary}>Dashboard</button>
          </a>
        </div>
      </section>

      <section style={styles.grid}>
        <Card title="IA local" text="Sin nube. Privado. Rápido."/>
        <Card title="Automatización" text="Trabaja solo por vos"/>
        <Card title="Voz + Chat" text="Interacción natural"/>
        <Card title="Plugins" text="Extensible y modular"/>
        <Card title="Multiusuario" text="Roles y permisos"/>
        <Card title="Móvil + LAN" text="Control remoto total"/>
      </section>

      <footer style={{opacity:.5, marginTop:40}}>
        Nexus © 2026
      </footer>

    </div>
  )
}

function Card({title,text}){
  return (
    <div style={styles.card}>
      <h3>{title}</h3>
      <p>{text}</p>
    </div>
  )
}

const styles = {
  page:{
    background:"#0f1115",
    color:"white",
    minHeight:"100vh",
    fontFamily:"sans-serif",
    padding:40
  },
  hero:{
    textAlign:"center",
    marginTop:80
  },
  grid:{
    display:"grid",
    gridTemplateColumns:"repeat(auto-fit,minmax(200px,1fr))",
    gap:20,
    marginTop:80
  },
  card:{
    background:"#1b1d24",
    padding:20,
    borderRadius:14
  },
  primary:{
    background:"#7c5cff",
    color:"white",
    border:"none",
    padding:"10px 20px",
    borderRadius:10
  },
  secondary:{
    background:"#2a2d38",
    color:"white",
    border:"none",
    padding:"10px 20px",
    borderRadius:10
  }
}
