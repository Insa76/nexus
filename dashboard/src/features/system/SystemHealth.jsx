import { useEffect, useState } from "react"
import axios from "axios"

const api = axios.create({
  baseURL: "http://127.0.0.1:8010",
  headers: {
    "x-api-key": "nexus-secret"
  }
})

export default function SystemHealth(){

  const [health,setHealth]=useState(null)

  useEffect(()=>{

    const load = async ()=>{
      const r = await api.get("/system/health")
      setHealth(r.data)
    }

    load()

    const i = setInterval(load,2000)

    return ()=>clearInterval(i)

  },[])

  if(!health) return null

  return(
    <div style={styles.wrap}>

      <h3>System Health</h3>

      <div style={styles.score}>
        {health.health_score}%
      </div>

      <div style={styles.grid}>
        <Stat label="Errors" value={(health.error_rate*100).toFixed(1)+"%"}/>
        <Stat label="Queue" value={health.queue_size}/>
        <Stat label="Circuits" value={health.open_circuits.length}/>
        <Stat label="Jobs" value={health.total_jobs}/>
      </div>

    </div>
  )
}

function Stat({label,value}){
  return(
    <div style={styles.card}>
      <div style={styles.label}>{label}</div>
      <div style={styles.value}>{value}</div>
    </div>
  )
}

const styles={

  wrap:{
    background:"rgba(255,255,255,.05)",
    borderRadius:14,
    padding:16,
    color:"white"
  },

  score:{
    fontSize:48,
    fontWeight:700,
    textAlign:"center",
    marginBottom:12
  },

  grid:{
    display:"grid",
    gridTemplateColumns:"repeat(4,1fr)",
    gap:8
  },

  card:{
    background:"rgba(255,255,255,.08)",
    borderRadius:10,
    padding:8,
    textAlign:"center"
  },

  label:{
    fontSize:11,
    opacity:.6
  },

  value:{
    fontSize:18,
    fontWeight:600
  }

}