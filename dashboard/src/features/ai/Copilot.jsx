import { useState } from "react"
import axios from "axios"

const api = axios.create({
  baseURL: "http://127.0.0.1:8010",
  headers: {
    "x-api-key": "nexus-secret"
  }
})

export default function Copilot({ onWorkflow }) {

  const [prompt,setPrompt] = useState("")
  const [loading,setLoading] = useState(false)

  const generate = async () => {

    setLoading(true)

    try {

      const r = await api.post("/copilot/generate",{
        prompt
      })

      if(r.data.ok){

        onWorkflow(r.data.workflow)

      }

    } catch(e){
      console.error(e)
    }

    setLoading(false)
  }

  return(

    <div style={styles.box}>

      <h3>Nexus Copilot</h3>

      <input
        placeholder="Describe una automatización..."
        value={prompt}
        onChange={e=>setPrompt(e.target.value)}
        style={styles.input}
      />

      <button onClick={generate} style={styles.btn}>
        {loading ? "Generando..." : "Generar Workflow"}
      </button>

    </div>
  )
}

const styles = {

 box:{
  background:"rgba(255,255,255,.05)",
  padding:14,
  borderRadius:12
 },

 input:{
  width:"100%",
  padding:8,
  marginBottom:8
 },

 btn:{
  width:"100%",
  padding:8
 }

}