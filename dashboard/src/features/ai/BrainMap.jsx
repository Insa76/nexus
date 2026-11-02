import ReactFlow, { Background, Controls } from "reactflow"
import "reactflow/dist/style.css"

import { useEffect, useState } from "react"
import axios from "axios"

const api = axios.create({
  baseURL: "http://127.0.0.1:8010",
  headers: { "x-api-key": "nexus-secret" }
})

export default function BrainMap(){

  const [nodes,setNodes] = useState([])
  const [edges,setEdges] = useState([])

  useEffect(()=>{

    const load = async ()=>{

      try{

        const goals = await api.get("/goals")
        const jobs = await api.get("/jobs")

        buildGraph(goals.data, jobs.data)

      }catch(e){
        console.error(e)
      }

    }

    load()

    const i = setInterval(load,2000)

    return ()=>clearInterval(i)

  },[])


  function buildGraph(goals,jobs){

    const n=[]
    const e=[]

    let id=1

    goals.forEach((g,i)=>{

      const goalId = "goal_"+id++

      n.push({
        id:goalId,
        position:{x:100,y:i*150},
        data:{label:"🎯 "+g.goal},
        style:{background:"#8e44ad",color:"white"}
      })

      Object.entries(jobs).forEach(([jid,j])=>{

        const jobNode="job_"+jid

        n.push({
          id:jobNode,
          position:{x:400,y:i*150+50},
          data:{label:"⚙ "+j.workflow},
          style:{background:"#2980b9",color:"white"}
        })

        e.push({
          id:"e_"+goalId+"_"+jid,
          source:goalId,
          target:jobNode
        })

      })

    })

    setNodes(n)
    setEdges(e)

  }


  return(

    <div style={{height:"600px",background:"#111"}}>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
      >

        <Background/>
        <Controls/>

      </ReactFlow>

    </div>

  )

}