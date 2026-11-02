import { useEffect, useState, useMemo } from "react"
import axios from "axios"
import JobTimeline from "./JobTimeline"

const api = axios.create({
  baseURL: "http://127.0.0.1:8010"
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

export default function JobsPanel(){

  const [jobs,setJobs]=useState({})
  const [metrics,setMetrics]=useState({})
  const [expanded,setExpanded]=useState(null)
  const [selected,setSelected]=useState(null)

  /* =========================
     polling
  ========================= */

  useEffect(() => {

  const loadInitial = async () => {
    const [jobsRes, metricsRes] = await Promise.all([
      api.get("/jobs"),
      api.get("/metrics")
    ])
    setJobs(jobsRes.data)
    setMetrics(metricsRes.data)
  }

  loadInitial()

  const ws = new WebSocket("ws://127.0.0.1:8010/ws")

  ws.onmessage = (e) => {

    const msg = JSON.parse(e.data)

    if (msg.type === "job_update") {

      setJobs(prev => ({
        ...prev,
        [msg.job_id]: {
          ...prev[msg.job_id],
          status: msg.status,
          result: msg.result
        }
      }))
    }

    if (msg.type === "metrics_update") {
      setMetrics(msg.data)
    }

    if (msg.type === "circuit_update") {
      setMetrics(prev => ({
        ...prev,
        circuit_state: msg.state
      }))
    }
  }

  return () => ws.close()

}, [])

  /* =========================
     ordenar por fecha
  ========================= */

  const orderedEntries = useMemo(()=>{
    return Object.entries(jobs)
      .sort((a,b)=>{
        const da = new Date(a[1].updated_at || 0)
        const db = new Date(b[1].updated_at || 0)
        return db - da
      })
  },[jobs])

  const list = orderedEntries.map(e=>e[1])

  /* =========================
     métricas
  ========================= */

  const stats = useMemo(()=>( {
    total: list.length,
    running: list.filter(j=>j.status==="running").length,
    queued: list.filter(j=>j.status==="queued").length,
    done: list.filter(j=>j.status==="done").length,
    error: list.filter(j=>j.status==="error").length
  }),[jobs])

  /* ========================= */

  const color=(s)=>{
    if(s==="running") return "#f6c344"
    if(s==="done") return "#2ecc71"
    if(s==="queued") return "#3498db"
    if(s==="error") return "#e74c3c"
    return "#999"
  }

  const toggle = (id)=>{
    setExpanded(expanded===id ? null : id)
  }

  const formatResult = (r)=>{
    if(!r) return "Sin resultado"
    if(typeof r === "string") return r
    return JSON.stringify(r,null,2)
  }

  /* ========================= */

  return(
  <div style={styles.wrap}>

    <h3 style={{marginBottom:14,fontSize:18}}>Jobs</h3>

    <div style={styles.stats}>
      <Stat label="Total" value={stats.total}/>
      <Stat label="Running" value={stats.running}/>
      <Stat label="Queued" value={stats.queued}/>
      <Stat label="Done" value={stats.done}/>
      <Stat label="Error" value={stats.error}/>
    </div>

    <div style={styles.list}>

      {orderedEntries.map(([id,j])=>{

        const isExpanded = expanded===id

        return(
          <div key={id} style={styles.rowWrap}>

            <div 
              style={styles.row}
              onClick={()=>toggle(id)}
            >

              <div style={{display:"flex",alignItems:"center",gap:8}}>

                <span style={styles.arrow}>
                  {isExpanded ? "▾" : "▸"}
                </span>

                <span style={styles.version}>
                  v{j.version}
                </span>

                <span>{j.workflow}</span>

              </div>

              <div style={{display:"flex",alignItems:"center",gap:10}}>

                {j.updated_at && (
                  <span style={styles.time}>
                    {new Date(j.updated_at).toLocaleTimeString()}
                  </span>
                )}

                <span style={{
                  ...styles.badge,
                  background: color(j.status),
                  animation: j.status==="running"
                    ? "pulse 1.2s infinite"
                    : "none"
                }}>
                  {j.status}
                </span>

              </div>

            </div>

            {isExpanded && (
              <div style={styles.detail}>

                {/* RESULTADO DEL JOB */}

                <pre style={{
                  ...styles.pre,
                  color: j.status==="error"
                    ? "#ff6b6b"
                    : "#cfcfcf"
                }}>
                  {formatResult(j.result)}
                </pre>

                {/* 🔥 WORKFLOW TIMELINE */}

                <div style={{marginTop:10}}>
                  <JobTimeline jobId={id}/>
                </div>

              </div>
            )}

          </div>
        )

      })}

    </div>

  </div>
)
}

/* ========================= */

function Stat({label,value}){
  return(
    <div style={styles.card}>
      <div style={{opacity:.5,fontSize:12}}>{label}</div>
      <div style={{fontSize:22,fontWeight:600}}>{value}</div>
    </div>
  )
}

/* ========================= */

const styles={

  wrap:{
    background:"rgba(255,255,255,.05)",
    borderRadius:16,
    padding:18,
    color:"white",
    backdropFilter:"blur(6px)"
  },

  stats:{
    display:"grid",
    gridTemplateColumns:"repeat(5,1fr)",
    gap:10,
    marginBottom:14
  },

  card:{
    background:"rgba(255,255,255,.08)",
    borderRadius:12,
    padding:12,
    textAlign:"center"
  },

  list:{
    display:"flex",
    flexDirection:"column",
    gap:8,
    maxHeight:340,
    overflow:"auto",
    scrollbarWidth:"thin"
  },

  rowWrap:{
    display:"flex",
    flexDirection:"column"
  },

  row:{
    display:"flex",
    justifyContent:"space-between",
    alignItems:"center",
    background:"rgba(255,255,255,.04)",
    padding:"10px 12px",
    borderRadius:10,
    cursor:"pointer",
    transition:"all .2s ease"
  },

  arrow:{
    fontSize:12,
    opacity:.6
  },

  version:{
    fontSize:11,
    opacity:.5
  },

  badge:{
    padding:"4px 10px",
    borderRadius:10,
    fontSize:12,
    fontWeight:600
  },

  time:{
    fontSize:11,
    opacity:.5
  },

  detail:{
    marginTop:6,
    background:"rgba(0,0,0,.35)",
    padding:10,
    borderRadius:10
  },

  pre:{
    fontSize:11,
    whiteSpace:"pre-wrap",
    wordBreak:"break-word",
    lineHeight:"1.4"
  }
}