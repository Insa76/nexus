import { useState, useEffect } from "react"
import axios from "axios"

const API = "http://192.168.0.15:8000" // ← poné tu IP real

export default function App() {

  const [msg, setMsg] = useState("")
  const [chat, setChat] = useState([])
  const [stats, setStats] = useState({})

  const send = async (text) => {

    const t = text || msg
    if (!t) return

    setChat(c => [...c, { role: "user", text: t }])
    setMsg("")

    const res = await axios.post(API + "/ask", { message: t }, {
      headers: { "x-api-key": "nexus-secret" }
    })

    setChat(c => [...c, { role: "assistant", text: res.data.result }])
  }

  const loadStats = async () => {
    const s = await axios.get(API + "/dashboard/stats", {
      headers: { "x-api-key": "nexus-secret" }
    })
    setStats(s.data)
  }

  useEffect(() => {
    loadStats()
    const i = setInterval(loadStats, 3000)
    return () => clearInterval(i)
  }, [])

  return (
    <div style={styles.page}>

      <h2>Nexus Mobile</h2>

      {/* Stats */}
      <div style={styles.stats}>
        <Card label="CPU" value={stats.cpu + "%"} />
        <Card label="RAM" value={stats.ram + "%"} />
      </div>

      {/* Chat */}
      <div style={styles.chat}>
        {chat.map((m,i)=>(
          <div key={i} style={{
            ...styles.bubble,
            alignSelf: m.role === "user" ? "flex-end" : "flex-start",
            background: m.role === "user" ? "#6c5ce7" : "#2d3436"
          }}>
            {m.text}
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div style={styles.quick}>
        <button onClick={()=>send("ordená descargas")}>Ordenar</button>
        <button onClick={()=>send("abrí chrome")}>Chrome</button>
        <button onClick={()=>send("cerrá esta app")}>Cerrar app</button>
      </div>

      {/* Input */}
      <div style={styles.row}>
        <input
          value={msg}
          onChange={e=>setMsg(e.target.value)}
          placeholder="Decile algo a Nexus..."
          style={styles.input}
        />
        <button onClick={()=>send()}>Enviar</button>
      </div>

    </div>
  )
}

function Card({label,value}){
  return (
    <div style={styles.card}>
      <div>{label}</div>
      <strong>{value}</strong>
    </div>
  )
}

const styles = {
  page:{
    background:"#121212",
    color:"white",
    height:"100vh",
    padding:16,
    display:"flex",
    flexDirection:"column",
    gap:12,
    fontFamily:"sans-serif"
  },
  stats:{ display:"flex", gap:10 },
  card:{ background:"#1e1e1e", padding:10, borderRadius:8 },
  chat:{
    flex:1,
    overflowY:"auto",
    display:"flex",
    flexDirection:"column",
    gap:6
  },
  bubble:{
    padding:8,
    borderRadius:10,
    maxWidth:"80%"
  },
  quick:{
    display:"flex",
    gap:6
  },
  row:{ display:"flex", gap:6 },
  input:{ flex:1, padding:8, borderRadius:8 }
}
