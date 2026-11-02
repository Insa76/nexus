import ReactFlow, {
  addEdge,
  Background,
  Controls
} from "reactflow"
import "reactflow/dist/style.css"

import { useState, useEffect, useRef } from "react"
import toast from "react-hot-toast"

import Presence from "../presence/Presence"
import ConditionNode from "../../nodes/ConditionNode"
import Copilot from "../ai/Copilot"

import axios from "axios"

const api = axios.create({
  baseURL: "http://127.0.0.1:8010",
  headers: { "x-api-key": "nexus-secret" }
})

export default function Workflow() {

  const [logs, setLogs] = useState([])
  const [activeAction, setActiveAction] = useState(null)
  const [finishedActions, setFinishedActions] = useState([])
  const [errorAction, setErrorAction] = useState(null)
  const [aiPrompt,setAiPrompt] = useState("")

  const idRef = useRef(2)

  const [nodes, setNodes] = useState([
    {
      id: "1",
      position: { x: 100, y: 100 },
      data: { label: "▶ Trigger" },
      type: "default"
    }
  ])

  const [edges, setEdges] = useState([])

  const nodeTypes = { condition: ConditionNode }

  /* ==================================================
     WEBSOCKET LIVE EVENTS
  ================================================== */

  useEffect(() => {

    const ws = new WebSocket("ws://127.0.0.1:8010/ws")

    ws.onmessage = (e) => {

      const msg = JSON.parse(e.data)

      setLogs(l => [...l.slice(-120), msg])

      if (msg.type === "workflow_step") {
        setActiveAction(msg.action)
        setErrorAction(null)
      }

      if (msg.type === "workflow_result") {
        setFinishedActions(prev => [...prev, msg.action])
        setActiveAction(null)
      }

      if (msg.type === "workflow_error") {
        setErrorAction(msg.action)
        setActiveAction(null)
      }

    }

    return () => ws.close()

  }, [])

  /* ==================================================
     VISUAL NODE COLORING
  ================================================== */

  const styledNodes = nodes.map(n => {

    if (!n.data?.action) return n

    let style = {
      border: "1px solid #444",
      borderRadius: 8,
      padding: 6
    }

    if (n.data.action === activeAction) {
      style = {
        ...style,
        border: "2px solid #f6c344",
        boxShadow: "0 0 12px #f6c344"
      }
    }

    if (finishedActions.includes(n.data.action)) {
      style = {
        ...style,
        border: "2px solid #2ecc71",
        boxShadow: "0 0 12px #2ecc71"
      }
    }

    if (errorAction === n.data.action) {
      style = {
        ...style,
        border: "2px solid #e74c3c",
        boxShadow: "0 0 12px #e74c3c"
      }
    }

    return {
      ...n,
      style
    }

  })

  /* ==================================================
     AI WORKFLOW GENERATION
  ================================================== */

  const generateWithAI = async () => {

    if(!aiPrompt) return

    try{

      const res = await api.post("/ai/generate-workflow",{
        prompt: aiPrompt
      })

      const wf = res.data.workflow

      buildGraphFromWorkflow(wf)

      toast.success("Workflow generado por IA")

    }catch(err){

      toast.error("Error generando workflow")

    }

  }

  /* ==================================================
     BUILD GRAPH FROM WORKFLOW JSON
  ================================================== */

  function buildGraphFromWorkflow(workflow){

    const newNodes=[
      {
        id:"1",
        position:{x:100,y:100},
        data:{label:"▶ Trigger"}
      }
    ]

    const newEdges=[]

    let lastId="1"

    workflow.steps.forEach((step,i)=>{

      const id=String(i+2)

      newNodes.push({
        id,
        position:{x:300,y:100+i*120},
        data:{
          label:step.action,
          action:step.action
        }
      })

      newEdges.push({
        id:lastId+"-"+id,
        source:lastId,
        target:id
      })

      lastId=id

    })

    setNodes(newNodes)
    setEdges(newEdges)

  }

  /* ==================================================
     ADD NODE
  ================================================== */

  const addNode = (action) => {

    const newNode = {
      id: String(idRef.current++),
      position: { x: 260, y: 150 + idRef.current * 70 },
      data: { label: action, action },
      type: "default"
    }

    setNodes(n => [...n, newNode])

  }

  /* ==================================================
     SAVE WORKFLOW
  ================================================== */

  const saveWorkflow = async () => {

    const nodeMap = {}
    nodes.forEach(n => nodeMap[n.id] = n)

    const edgeMap = {}
    edges.forEach(e => {
      if (!edgeMap[e.source]) edgeMap[e.source] = []
      edgeMap[e.source].push(e)
    })

    function buildTree(nodeId) {

      const node = nodeMap[nodeId]
      if (!node) return null

      if (node.data?.action) {

        const children = (edgeMap[nodeId] || [])
          .map(e => buildTree(e.target))
          .filter(Boolean)

        return {
          type: "action",
          action: node.data.action,
          value: null,
          next: children
        }

      }

      return null

    }

    const targets = edges.map(e => e.target)
    const rootNode = nodes.find(n => !targets.includes(n.id))

    if (!rootNode) {
      toast.error("No se detecta nodo raíz")
      return
    }

    const tree = buildTree(rootNode.id)

    if (!tree) {
      toast.error("Workflow vacío o mal conectado")
      return
    }

    await api.post("/workflows/save", [
      {
        name: "workflow-1",
        trigger: "manual",
        steps: [tree]
      }
    ])

    toast.success("Workflow guardado ✓")

  }

  /* ==================================================
     RUN WORKFLOW
  ================================================== */

  const runAsync = async () => {

    setFinishedActions([])
    setErrorAction(null)

    const res = await api.post("/jobs/run", { name: "workflow-1" })

    toast("Job creado: " + res.data.job_id)

  }

  /* ==================================================
     LOAD WORKFLOW FROM COPILOT
  ================================================== */

  const loadGeneratedWorkflow = (workflow) => {

    buildGraphFromWorkflow(workflow)

  }

  /* ==================================================
     UI
  ================================================== */

  return (
    <div style={{ position: "relative" }}>

      <div style={{
        position: "absolute",
        right: 20,
        top: 20,
        width: 140,
        height: 140,
        pointerEvents: "none",
        zIndex: 50
      }}>
        <Presence />
      </div>

      {/* ================= AI PROMPT ================= */}

      <div style={{display:"flex",gap:6,marginBottom:8}}>

        <input
          value={aiPrompt}
          onChange={e=>setAiPrompt(e.target.value)}
          placeholder="Describe el workflow..."
          style={{flex:1,padding:6}}
        />

        <button onClick={generateWithAI}>
          Generate AI
        </button>

      </div>

      {/* ================= ACTION BUTTONS ================= */}

      <div style={{ display: "flex", gap: 6, marginBottom: 8 }}>
        <button onClick={() => addNode("list_dir")}>List Dir</button>
        <button onClick={() => addNode("move_files")}>Move Files</button>
        <button onClick={() => addNode("create_folder")}>Create Folder</button>
        <button onClick={saveWorkflow}>Save</button>
        <button onClick={runAsync}>Run Async 🚀</button>
      </div>

      {/* ================= WORKFLOW CANVAS ================= */}

      <div style={{
        height: 600,
        background: "#111",
        borderRadius: 12,
        overflow: "hidden"
      }}>

        <ReactFlow
          nodes={styledNodes}
          edges={edges}
          onConnect={(p) => setEdges(e => addEdge(p, e))}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>

        <Copilot onWorkflow={loadGeneratedWorkflow}/>

      </div>

      {/* ================= LOG PANEL ================= */}

      <div style={{
        marginTop: 10,
        height: 120,
        overflow: "auto",
        background: "#000",
        color: "#0f0",
        fontSize: 12,
        padding: 8,
        borderRadius: 8
      }}>
        {logs.map((l, i) => (
          <div key={i}>{JSON.stringify(l)}</div>
        ))}
      </div>

    </div>
  )
}