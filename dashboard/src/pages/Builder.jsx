import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges
} from "reactflow";

import "reactflow/dist/style.css";

import {
  useState,
  useCallback,
  useEffect
} from "react";

import ActionNode from "../nodes/ActionNode";

import { getAuthHeaders } from "../services/auth";

const nodeTypes = {
  action: ActionNode
};

export default function Builder() {

  // =========================================================
  // STATE
  // =========================================================
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const [prompt, setPrompt] = useState("");
  const [missionGoal, setMissionGoal] = useState("");

  const [logs, setLogs] = useState([]);

  const [currentJobId, setCurrentJobId] =
    useState(null);

  const [generatedSteps, setGeneratedSteps] =
    useState([]);

  const [savedWorkflows, setSavedWorkflows] =
    useState([]);

  const [workflowName, setWorkflowName] =
    useState("");

  const [reactFlowInstance, setReactFlowInstance] =
    useState(null);

  const [executions, setExecutions] =
    useState([]);

  const [operatorGoal, setOperatorGoal] =
  useState("");  

  // =========================================================
  // LIVE STATE
  // =========================================================
  const [nodeStates, setNodeStates] =
    useState({});

  const [activeAction, setActiveAction] =
    useState(null);

  const [progress, setProgress] =
    useState(0);

  const [stepInfo, setStepInfo] =
    useState({
      completed: 0,
      total: 0
    });

  // =========================================================
  // LOAD WORKFLOWS
  // =========================================================
  useEffect(() => {

    loadWorkflows();

  }, []);

  // =========================================================
  // WEBSOCKET
  // =========================================================
  useEffect(() => {

    const ws = new WebSocket(
      "ws://127.0.0.1:8010/ws"
    );

    ws.onopen = () => {

      console.log("🟢 WS conectado");
    };

    ws.onmessage = (event) => {

      const msg = JSON.parse(event.data);

      console.log("📡 WS EVENT:", msg);

      // =====================================================
      // JOB LOGS
      // =====================================================
      if (
        msg.type === "job_log" &&
        msg.job_id === currentJobId
      ) {

        setLogs(prev => [
          ...prev,
          msg.message
        ]);

        // ===================================================
        // NODE STATES
        // ===================================================
        if (
          msg.node_id &&
          msg.status
        ) {

          setNodeStates(prev => ({

            ...prev,

            [msg.node_id]: msg.status
          }));
        }

        // ===================================================
        // ACTIVE ACTION
        // ===================================================
        if (
          msg.action &&
          msg.status === "running"
        ) {

          setActiveAction(msg.action);
        }

        // ===================================================
        // PROGRESS
        // ===================================================
        if (
          typeof msg.progress === "number"
        ) {

          setProgress(msg.progress);

          setStepInfo({
            completed:
              msg.completed_steps || 0,

            total:
              msg.total_steps || 0
          });
        }
      }

      // =====================================================
      // APPROVAL
      // =====================================================
      if (
        msg.type === "approval_required"
      ) {

        const ok = window.confirm(
          msg.message
        );

        if (ok) {

          fetch(
            `http://localhost:8010/approvals/${msg.job_id}`,
            {
              method: "POST",

              headers: {
                ...getAuthHeaders()
              }
            }
          );
        }
      }
    };

    ws.onerror = (err) => {

      console.log(
        "⚠️ WS error",
        err
      );
    };

    ws.onclose = () => {

      console.log("⚪ WS cerrado");
    };

    return () => {

      ws.close();
    };

  }, [currentJobId]);

  // =========================================================
  // UPDATE NODE
  // =========================================================
  const updateNodeData = (
    id,
    newData
  ) => {

    setNodes((nds) =>
      nds.map((n) =>
        n.id === id
          ? {
              ...n,

              data: {
                ...newData,
                onChange: updateNodeData
              }
            }
          : n
      )
    );
  };

  // =========================================================
  // ADD NODE
  // =========================================================
  const addNode = () => {

    const id = String(Date.now());

    const newNode = {

      id,

      type: "action",

      position: {
        x: 250,
        y: 250
      },

      data: {

        action: "create_folder",

        params: {},

        onChange: updateNodeData,

        nodeState: "pending"
      }
    };

    setNodes(prev => [
      ...prev,
      newNode
    ]);

    setTimeout(() => {

      reactFlowInstance?.fitView();

    }, 100);
  };

  // =========================================================
  // FLOW EVENTS
  // =========================================================
  const onNodesChange = useCallback(

    (changes) => {

      setNodes((nds) =>
        applyNodeChanges(
          changes,
          nds
        )
      );
    },

    []
  );

  const onEdgesChange = useCallback(

    (changes) => {

      setEdges((eds) =>
        applyEdgeChanges(
          changes,
          eds
        )
      );
    },

    []
  );

  const onConnect = (params) => {

    const label = window.prompt(
      "Tipo conexión: true / false",
      "true"
    );

    setEdges((eds) =>
      addEdge(
        {
          ...params,

          label:
            label || "true"
        },
        eds
      )
    );
  };

  // =========================================================
  // RUN WORKFLOW
  // =========================================================
  const runWorkflow = async () => {

    if (
      !nodes ||
      nodes.length === 0
    ) {

      alert(
        "No hay nodos para ejecutar"
      );

      return;
    }

    setLogs([]);
    setNodeStates({});
    setProgress(0);

    setStepInfo({
      completed: 0,
      total: nodes.length
    });

    try {

      const res = await fetch(
        "http://localhost:8010/jobs/run",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            ...getAuthHeaders()
          },

          body: JSON.stringify({
            nodes,
            edges
          })
        }
      );

      const data =
        await res.json();

      console.log(
        "🔥 JOB RESPONSE:",
        data
      );

      if (!data.job_id) {

        alert(
          "Error ejecutando workflow"
        );

        return;
      }

      setCurrentJobId(
        data.job_id
      );

      setTimeout(() => {

        loadExecutions(
          data.job_id
        );

      }, 1000);

    } catch (err) {

      console.error(err);
    }
  };

  // =========================================================
  // RUN AI
  // =========================================================
  const runAI = async () => {

    try {

      const res = await fetch(
        "http://localhost:8010/ai-builder/generate",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            ...getAuthHeaders()
          },

          body: JSON.stringify({
            prompt
          })
        }
      );

      const data =
        await res.json();

      console.log(
        "🧠 IA RESPONSE:",
        data
      );

      if (
        !data.steps ||
        data.steps.length === 0
      ) {

        alert(
          "IA no generó pasos"
        );

        return;
      }

      setGeneratedSteps(
        data.steps
      );

      const newNodes =
        data.steps.map(
          (step, i) => ({

            id:
              `${Date.now()}-${i}`,

            type: "action",

            position: {
              x: 250,
              y: i * 160
            },

            data: {

              action:
                step.action,

              params:
                step.value || {},

              nodeState:
                "pending",

              onChange:
                updateNodeData
            }
          })
        );

      setNodes(newNodes);

    } catch (err) {

      console.error(err);
    }
  };

  // =========================================================
  // SAVE WORKFLOW
  // =========================================================
  const saveWorkflow = async () => {

    if (!workflowName) {

      alert(
        "Nombre requerido"
      );

      return;
    }

    try {

      await fetch(
        "http://localhost:8010/workflows/save",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            ...getAuthHeaders()
          },

          body: JSON.stringify({

            name:
              workflowName,

            nodes,

            edges
          })
        }
      );

      alert(
        "Workflow guardado 🚀"
      );

      loadWorkflows();

    } catch (err) {

      console.error(err);
    }
  };

  // =========================================================
  // LOAD WORKFLOWS
  // =========================================================
  const loadWorkflows = async () => {

    try {

      const res = await fetch(
        "http://localhost:8010/workflows",
        {
          headers: {
            ...getAuthHeaders()
          }
        }
      );

      const data =
        await res.json();

      setSavedWorkflows(data);

    } catch (err) {

      console.error(err);
    }
  };

  // =========================================================
  // LOAD WORKFLOW
  // =========================================================
  const loadWorkflow = async (
    workflowId
  ) => {

    try {

      const res = await fetch(
        `http://localhost:8010/workflows/${workflowId}`,
        {
          headers: {
            ...getAuthHeaders()
          }
        }
      );

      const data =
        await res.json();

      const hydratedNodes =
        data.nodes.map(n => ({

          ...n,

          data: {

            ...n.data,

            onChange:
              updateNodeData,

            nodeState:
              nodeStates[n.id]
              || "idle"
          }
        }));

      setNodes(
        hydratedNodes
      );

      setEdges(
        data.edges || []
      );

    } catch (err) {

      console.error(err);
    }
  };

  // =========================================================
  // LOAD EXECUTIONS
  // =========================================================
  const loadExecutions = async (
    jobId
  ) => {

    try {

      const res = await fetch(
        `http://localhost:8010/executions/${jobId}`,
        {
          headers: {
            ...getAuthHeaders()
          }
        }
      );

      const data =
        await res.json();

      setExecutions(data);

    } catch (err) {

      console.error(err);
    }
  };

  // =========================================================
  // RUN MISSION
  // =========================================================
  const runMission = async () => {

    try {

      const res = await fetch(
        "http://localhost:8010/missions/run",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            ...getAuthHeaders()
          },

          body: JSON.stringify({
            goal: missionGoal
          })
        }
      );

      const data =
        await res.json();

      console.log(
        "🚀 MISSION:",
        data
      );

    } catch (err) {

      console.error(err);
    }
  };

  // =========================================================
  // NODES STATE
  // =========================================================
  const nodesWithState =
    nodes.map((n) => ({

      ...n,

      data: {

        ...n.data,

        nodeState:
          nodeStates[n.id]
          || "pending"
      }
    }));

  // =========================================================
  // EDGES STATE
  // =========================================================
  const edgesWithState =
    edges.map((e) => {

      const sourceNode =
        nodes.find(
          n => n.id === e.source
        );

      const isActive =
        sourceNode?.data?.action
        === activeAction;

      return {

        ...e,

        animated: isActive,

        style: {

          stroke:
            isActive
              ? "#4deeea"
              : "#555",

          strokeWidth:
            isActive
              ? 3
              : 1.5
        }
      };
    });

  const runOperator = async () => {

  const res = await fetch(

    "http://localhost:8000/operator/run",

    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders()
      },

      body: JSON.stringify({
        goal: operatorGoal
      })
    }
  );

  const data = await res.json();

  console.log(
    "🧠 OPERATOR:",
    data
  );
};  

  // =========================================================
  // UI
  // =========================================================
  return (

  <div
    style={{
      width: "100vw",
      height: "100vh",
      background: "#0d1117",
      overflow: "hidden"
    }}
  >

    {/* ================================================= */}
    {/* TOP BAR */}
    {/* ================================================= */}
    <div
      style={{
        position: "fixed",

        top: 0,
        left: 0,
        right: 0,

        height: 72,

        zIndex: 100,

        display: "flex",

        alignItems: "center",

        gap: 10,

        padding: "0 16px",

        background: "rgba(10,10,10,0.96)",

        borderBottom: "1px solid #222",

        backdropFilter: "blur(10px)"
      }}
    >

      <button onClick={addNode}>
        + Nodo
      </button>

      <button onClick={runWorkflow}>
        ▶ Ejecutar
      </button>

      <input
        placeholder="Nombre workflow"
        value={workflowName}
        onChange={(e) =>
          setWorkflowName(e.target.value)
        }
        style={{
          width: 180
        }}
      />

      <button onClick={saveWorkflow}>
        💾 Guardar
      </button>

      <input
        placeholder="Ej: ordenar PDFs"
        value={prompt}
        onChange={(e) =>
          setPrompt(e.target.value)
        }
        style={{
          width: 220
        }}
      />

      <button onClick={runAI}>
        ✨ AI
      </button>

      <input
        placeholder="Mission Goal"
        value={missionGoal}
        onChange={(e) =>
          setMissionGoal(e.target.value)
        }
        style={{
          width: 260
        }}
      />

      <button onClick={runMission}>
        🚀 Run Mission
      </button>

    </div>

    <div
  style={{
    position: "absolute",
    top: 70,
    left: 10,
    zIndex: 20
  }}
>

  <input
    placeholder="Operator Goal"
    value={operatorGoal}
    onChange={(e) =>
      setOperatorGoal(
        e.target.value
      )
    }
  />

  <button
    onClick={runOperator}
  >
    🧠 Run Operator
  </button>

</div>

    {/* ================================================= */}
    {/* LEFT SIDEBAR */}
    {/* ================================================= */}
    <div
      style={{
        position: "fixed",

        top: 82,
        left: 10,

        bottom: 10,

        width: 280,

        zIndex: 50,

        background: "#111",

        border: "1px solid #222",

        borderRadius: 12,

        overflow: "hidden",

        display: "flex",

        flexDirection: "column"
      }}
    >

      <div
        style={{
          padding: 14,

          borderBottom: "1px solid #222",

          fontWeight: "bold",

          color: "#fff"
        }}
      >
        📂 Workflows
      </div>

      <div
        style={{
          flex: 1,

          overflowY: "auto",

          padding: 12
        }}
      >

        {savedWorkflows.length === 0 && (

          <div
            style={{
              color: "#888"
            }}
          >
            No hay workflows
          </div>
        )}

        {savedWorkflows.map((wf) => (

          <div
            key={wf.id}
            style={{
              background: "#1a1a1a",

              borderRadius: 10,

              padding: 10,

              marginBottom: 10
            }}
          >

            <div
              style={{
                color: "#fff",

                marginBottom: 8
              }}
            >
              {wf.name}
            </div>

            <button
              onClick={() =>
                loadWorkflow(wf.id)
              }
            >
              ▶ Load
            </button>

          </div>
        ))}

      </div>

    </div>

    {/* ================================================= */}
    {/* RIGHT SIDEBAR */}
    {/* ================================================= */}
    <div
      style={{
        position: "fixed",

        top: 82,
        right: 10,

        bottom: 10,

        width: 340,

        zIndex: 50,

        display: "flex",

        flexDirection: "column",

        gap: 12
      }}
    >

      {/* ============================================= */}
      {/* EXECUTION PANEL */}
      {/* ============================================= */}
      <div
        style={{
          background: "#111",

          border: "1px solid #222",

          borderRadius: 12,

          overflow: "hidden",

          minHeight: 250,

          maxHeight: 320,

          display: "flex",

          flexDirection: "column"
        }}
      >

        <div
          style={{
            padding: 14,

            borderBottom: "1px solid #222",

            fontWeight: "bold",

            color: "#fff"
          }}
        >
          📜 Execution Timeline
        </div>

        <div
          style={{
            flex: 1,

            overflowY: "auto",

            padding: 12
          }}
        >

          {executions.map((e, i) => (

            <div
              key={i}
              style={{
                padding: 10,

                marginBottom: 10,

                borderRadius: 8,

                background:
                  e.status === "success"
                    ? "#13361b"
                    : e.status === "error"
                    ? "#3a1616"
                    : "#222"
              }}
            >

              <div
                style={{
                  color: "#fff"
                }}
              >
                ⚙️ {e.action}
              </div>

              <div
                style={{
                  color: "#aaa",

                  marginTop: 4
                }}
              >
                Status: {e.status}
              </div>

              <div
                style={{
                  fontSize: 12,

                  opacity: 0.7,

                  marginTop: 6,

                  color: "#777"
                }}
              >
                {e.created_at}
              </div>

            </div>
          ))}

        </div>

      </div>

      {/* ============================================= */}
      {/* PROGRESS */}
      {/* ============================================= */}
      <div
        style={{
          background: "#0b0f14",

          border: "1px solid #188686",

          borderRadius: 12,

          padding: 14
        }}
      >

        <div
          style={{
            color: "#4deeea",

            marginBottom: 10
          }}
        >
          🚀 Progreso:
          {" "}
          {stepInfo.completed}
          /
          {stepInfo.total}
        </div>

        <div
          style={{
            width: "100%",

            height: 10,

            background: "#222",

            borderRadius: 999
          }}
        >

          <div
            style={{
              width: `${progress}%`,

              height: "100%",

              background: "#4deeea",

              borderRadius: 999,

              transition: "width 0.3s ease"
            }}
          />

        </div>

      </div>

      {/* ============================================= */}
      {/* LOGS */}
      {/* ============================================= */}
      <div
        style={{
          flex: 1,

          background: "#0b0f14",

          border: "1px solid #188686",

          borderRadius: 12,

          overflow: "hidden",

          display: "flex",

          flexDirection: "column"
        }}
      >

        <div
          style={{
            padding: 14,

            borderBottom: "1px solid #133",

            color: "#4deeea",

            fontWeight: "bold"
          }}
        >
          🧠 Runtime Logs
        </div>

        <div
          style={{
            flex: 1,

            overflowY: "auto",

            padding: 14,

            color: "#4deeea"
          }}
        >

          {logs.length === 0 && (

            <div>
              Esperando ejecución...
            </div>
          )}

          {logs.map((log, i) => (

            <div
              key={i}
              style={{
                marginBottom: 8
              }}
            >
              • {log}
            </div>

          ))}

        </div>

      </div>

    </div>

    {/* ================================================= */}
    {/* FLOW */}
    {/* ================================================= */}
    <div
      style={{
        position: "absolute",

        top: 72,
        left: 0,
        right: 0,
        bottom: 0
      }}
    >

      <ReactFlow
        nodeTypes={nodeTypes}
        nodes={nodesWithState}
        edges={edgesWithState}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onInit={setReactFlowInstance}
        deleteKeyCode={["Backspace", "Delete"]}
        fitView
      >
        <MiniMap />
        <Controls />
        <Background />
      </ReactFlow>

    </div>

  </div>
);
}