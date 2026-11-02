import { useEffect, useState } from "react"
import Presence from "../presence/Presence"

export default function AssistantMode(){

  const [expanded,setExpanded]=useState(false)
  const [mood,setMood]=useState("idle")

  /* ===============================
     HOTKEY
  =============================== */

  useEffect(()=>{

    const handler=(e)=>{
      if(e.ctrlKey && e.code==="Space"){
        setExpanded(v=>!v)
      }
    }

    window.addEventListener("keydown",handler)
    return ()=>window.removeEventListener("keydown",handler)

  },[])


  /* ===============================
     WEBSOCKET SISTEMA
  =============================== */

  useEffect(()=>{

    const ws = new WebSocket("ws://127.0.0.1:8000/ws")

    ws.onmessage = (e)=>{

      const msg = JSON.parse(e.data)

      if(msg.type==="job_failed"){
        setMood("error")
      }

      if(msg.type==="job_done"){
        setMood("happy")
      }

      if(msg.type==="job_start"){
        setMood("thinking")
      }

      // volver a idle después de 2s
      setTimeout(()=>setMood("idle"),2000)
    }

    ws.onerror = ()=>console.warn("WS Assistant desconectado")

    return ()=>ws.close()

  },[])


  return(
    <div style={styles.wrapper}>

      <Presence mood={mood}/>

      {expanded && (
        <div style={styles.panel}>
          <h3>Nexus</h3>
          <p>Modo asistente activo</p>
        </div>
      )}

    </div>
  )
}

const styles={
  wrapper:{
    width:"100vw",
    height:"100vh",
    display:"flex",
    alignItems:"center",
    justifyContent:"center",
    background:"transparent"
  },
  panel:{
    position:"absolute",
    bottom:10,
    width:280,
    background:"rgba(20,20,25,.95)",
    padding:16,
    borderRadius:16,
    color:"white"
  }
}