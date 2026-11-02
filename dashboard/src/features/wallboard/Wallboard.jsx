import { useEffect, useState, useMemo } from "react"
import axios from "axios"
import Presence from "../presence/Presence"
import SystemHealth from "../system/SystemHealth"
import ErrorPanel from "../../components/ErrorPanel"

const API = "http://127.0.0.1:8010"

export default function Wallboard(){

  const [jobs,setJobs]=useState({})
  const [time,setTime]=useState(new Date())
  const [events,setEvents]=useState([])
  const [health,setHealth]=useState("healthy")

  /* reloj */
  useEffect(()=>{
    const i = setInterval(()=>setTime(new Date()),1000)
    return ()=>clearInterval(i)
  },[])

  /* bootstrap inicial */
  useEffect(()=>{
    axios.get(`${API}/jobs`,{
      headers:{ "x-api-key":"nexus-secret" }
    }).then(r=>setJobs(r.data))
  },[])

  /* websocket realtime */
  useEffect(()=>{

  const ws = new WebSocket("ws://127.0.0.1:8010/ws")

  ws.onmessage = (e)=>{

    const msg = JSON.parse(e.data)

    if(msg.type==="job_done"){
      pushActivity("He completado una automatización sin incidentes.")
      setCognitiveState("ÓPTIMO")
    }

    if(msg.type==="job_error"){
      pushActivity("He detectado una anomalía operativa. Estoy evaluando el impacto.")
      setCognitiveState("ANALIZANDO")
    }

    if(msg.type==="circuit.opened"){
      pushActivity("He activado un protocolo de protección preventiva.")
      setProtection("PROTECCIÓN ELEVADA")
      setCognitiveState("DEFENSIVO")
    }

    if(msg.type==="circuit.closed"){
      pushActivity("He restablecido condiciones estables.")
      setProtection("ACTIVA")
      setCognitiveState("ÓPTIMO")
    }

    if(msg.type === "nexus_decision"){
      console.log("Nexus decision:", msg)
    }

    if(msg.type === "nexus_voice"){
    setEvents(ev => [
    msg.message,
    ...ev.slice(0,10)
    ])
}

  }

  return ()=>ws.close()

},[])

  const pushEvent = (text)=>{
    setEvents(ev=>[
      {
        time: new Date().toLocaleTimeString(),
        text
      },
      ...ev.slice(0,8)
    ])
  }

  /* métricas derivadas */

  const list = Object.values(jobs)

  const stats = useMemo(()=>({

    total: list.length,
    running: list.filter(j=>j.status==="running").length,
    queued: list.filter(j=>j.status==="queued").length,
    done: list.filter(j=>j.status==="done").length,
    error: list.filter(j=>j.status==="error").length

  }),[jobs])

  const healthText = {
    healthy:"🟢 Sistema saludable",
    warning:"🟡 Atención requerida",
    critical:"🔴 Acción necesaria"
  }

  return(
    <div style={styles.page}>

      <Presence />
      <SystemHealth/>
      <ErrorPanel/>

      <div style={styles.header}>
        <div style={styles.brand}>NEXUS CLOUD</div>
        <div style={styles.clock}>{time.toLocaleTimeString()}</div>
      </div>

      <div style={styles.systemHealth}>
        {healthText[health]}
      </div>

      <div style={styles.metrics}>

        <Metric title="Automatizaciones" value={stats.total}/>
        <Metric title="En ejecución" value={stats.running} color="#c7a73b"/>
        <Metric title="En espera" value={stats.queued} color="#3b82f6"/>
        <Metric title="Completadas" value={stats.done} color="#3ba776"/>
        <Metric title="Errores" value={stats.error} color="#c75c5c"/>

      </div>

      <div style={styles.activity}>

        <div style={styles.activityTitle}>Actividad reciente</div>

        {events.map((e,i)=>(
          <div key={i} style={styles.logRow}>
            <span style={styles.logTime}>{e.time}</span>
            <span style={styles.logText}>{e.text}</span>
          </div>
        ))}

      </div>

    </div>
  )
}

/* ========================= */

function Metric({title,value,color}){

  return(
    <div style={styles.metric}>
      <div style={styles.metricTitle}>{title}</div>
      <div style={{
        ...styles.metricValue,
        color: color || "#f5f5f7"
      }}>
        {value}
      </div>
    </div>
  )
}

/* ========================= */

const styles = {

  page:{
    height:"100vh",
    background:"#0b0d10",
    color:"#f5f5f7",
    fontFamily:"Inter, sans-serif",
    padding:"48px 80px",
    display:"flex",
    flexDirection:"column"
  },

  header:{
    display:"flex",
    justifyContent:"space-between",
    alignItems:"center",
    marginBottom:40
  },

  brand:{
    fontSize:14,
    letterSpacing:4,
    color:"#8b8f98"
  },

  clock:{
    fontSize:28,
    fontWeight:500
  },

  systemHealth:{
    marginBottom:30,
    fontSize:16,
    opacity:.85
  },

  metrics:{
    display:"grid",
    gridTemplateColumns:"repeat(5, 1fr)",
    gap:40,
    marginBottom:60
  },

  metric:{
    borderBottom:"1px solid #1c1f26",
    paddingBottom:16
  },

  metricTitle:{
    fontSize:13,
    color:"#8b8f98",
    marginBottom:6,
    letterSpacing:1
  },

  metricValue:{
    fontSize:42,
    fontWeight:600
  },

  activity:{
    flex:1,
    borderTop:"1px solid #1c1f26",
    paddingTop:30
  },

  activityTitle:{
    fontSize:13,
    color:"#8b8f98",
    marginBottom:16,
    letterSpacing:1
  },

  logRow:{
    display:"flex",
    gap:20,
    fontSize:14,
    marginBottom:8,
    opacity:.9
  },

  logTime:{
    width:90,
    color:"#8b8f98"
  },

  logText:{
    color:"#f5f5f7"
  }

}