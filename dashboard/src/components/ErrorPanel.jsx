import { useEffect, useState } from "react"
import axios from "axios"

const api = axios.create({
  baseURL: "http://127.0.0.1:8010",
  headers: {
    "x-api-key": "nexus-secret"
  }
})

export default function ErrorPanel(){

  const [errors,setErrors]=useState([])

  useEffect(()=>{

    const load = async ()=>{
      const r = await api.get("/system/errors")
      setErrors(r.data)
    }

    load()

    const i = setInterval(load,3000)

    return ()=>clearInterval(i)

  },[])

  return(
    <div style={styles.wrap}>

      <h3>Top Errors</h3>

      {errors.length===0 && (
        <div style={styles.ok}>
          No errors detected
        </div>
      )}

      {errors.map((e,i)=>(
        <div key={i} style={styles.row}>
          <span>{e.error}</span>
          <span style={styles.count}>{e.count}</span>
        </div>
      ))}

    </div>
  )
}

const styles={

  wrap:{
    background:"rgba(255,255,255,.05)",
    borderRadius:14,
    padding:14,
    color:"white"
  },

  ok:{
    opacity:.6
  },

  row:{
    display:"flex",
    justifyContent:"space-between",
    marginBottom:6,
    fontSize:13
  },

  count:{
    background:"#e74c3c",
    padding:"2px 8px",
    borderRadius:8,
    fontSize:11
  }

}