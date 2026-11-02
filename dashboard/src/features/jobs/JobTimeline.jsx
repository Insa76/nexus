import { useEffect, useState } from "react"
import axios from "axios"

const api = axios.create({
  baseURL: "http://127.0.0.1:8010",
  headers: {
    "x-api-key": "nexus-secret"
  }
})

export default function JobTimeline({jobId}){

  const [steps,setSteps]=useState([])

  useEffect(()=>{

    if(!jobId) return

    api.get(`/jobs/${jobId}/steps`)
      .then(r=>setSteps(r.data))

  },[jobId])

  return(
    <div style={styles.wrap}>

      <h3>Workflow Timeline</h3>

      {steps.map((s,i)=>(
        <div key={i} style={styles.step}>

          <div style={{
            ...styles.dot,
            background:s.status==="success"
              ? "#2ecc71"
              : "#e74c3c"
          }}/>

          <div style={styles.info}>
            <div>{s.step}</div>
            <div style={styles.time}>{s.timestamp}</div>
          </div>

        </div>
      ))}

    </div>
  )
}

const styles={

  wrap:{
    background:"rgba(255,255,255,.05)",
    padding:16,
    borderRadius:12,
    color:"white"
  },

  step:{
    display:"flex",
    gap:10,
    marginBottom:8
  },

  dot:{
    width:10,
    height:10,
    borderRadius:"50%"
  },

  info:{
    display:"flex",
    justifyContent:"space-between",
    width:"100%"
  },

  time:{
    opacity:.5,
    fontSize:12
  }
}