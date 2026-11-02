import { useEffect, useState } from "react"
import axios from "axios"
import { getAuthHeaders } from "../../services/auth"

const api = axios.create({
  baseURL: "http://127.0.0.1:8010",
  headers: { "x-api-key": "nexus-secret" }
})

api.interceptors.request.use((config) => {

  const token = localStorage.getItem("token")

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

export default function MissionControl(){

  const [goals,setGoals] = useState([])
  const [jobs,setJobs] = useState({})
  const [voice,setVoice] = useState([])

  /* =========================
     LOAD DATA
  ========================= */

  useEffect(()=>{

    const load = async ()=>{

      try{

        const g = await api.get("/goals")
        setGoals(g.data)

        const j = await api.get("/jobs")
        setJobs(j.data)

      }catch(e){
        console.error(e)
      }
    }

    load()

    const i=setInterval(load,2000)

    return ()=>clearInterval(i)

  },[])


  /* =========================
     REALTIME VOICE
  ========================= */

  useEffect(()=>{

    const ws = new WebSocket("ws://127.0.0.1:8010/ws")

    ws.onmessage = (e)=>{

      const msg = JSON.parse(e.data)

      if(msg.type === "nexus_voice"){

        setVoice(v => [
          msg.message,
          ...v.slice(0,8)
        ])

      }

    }

    return ()=>ws.close()

  },[])


  /* ========================= */

  const running = Object.values(jobs)
    .filter(j=>j.status==="running").length

  const done = Object.values(jobs)
    .filter(j=>j.status==="done").length


  /* ========================= */

  return(

    <div style={styles.page}>

      <h1 style={styles.title}>Nexus Mission Control</h1>

      <div style={styles.grid}>

        <Card title="Active Goals">

          {goals.map(g=>(
            <div key={g.id} style={styles.row}>
              {g.goal}
            </div>
          ))}

        </Card>


        <Card title="System Health">

          <div style={styles.metric}>
            Running jobs: {running}
          </div>

          <div style={styles.metric}>
            Completed jobs: {done}
          </div>

        </Card>


        <Card title="Nexus Voice">

          {voice.map((v,i)=>(
            <div key={i} style={styles.log}>
              {v}
            </div>
          ))}

        </Card>


      </div>

    </div>
  )
}


/* ========================= */

function Card({title,children}){

  return(

    <div style={styles.card}>

      <div style={styles.cardTitle}>
        {title}
      </div>

      {children}

    </div>

  )

}


/* ========================= */

const styles = {

  page:{
    padding:40,
    background:"#0f1115",
    height:"100vh",
    color:"white",
    fontFamily:"Inter"
  },

  title:{
    marginBottom:30
  },

  grid:{
    display:"grid",
    gridTemplateColumns:"repeat(3,1fr)",
    gap:20
  },

  card:{
    background:"rgba(255,255,255,.05)",
    borderRadius:16,
    padding:20,
    minHeight:200
  },

  cardTitle:{
    marginBottom:10,
    opacity:.6
  },

  metric:{
    fontSize:22,
    marginBottom:10
  },

  row:{
    marginBottom:6
  },

  log:{
    fontFamily:"monospace",
    fontSize:12,
    marginBottom:4
  }

}