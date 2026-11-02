import { ACTIONS } from "../config/actions";
import { Handle, Position } from "reactflow";

export default function ActionNode({ data, id }) {

  const action = data.action || "create_folder";

  const config = ACTIONS[action];

  // 🔥 NODE STATE
  const state = data.nodeState || "idle";

  // =========================
  // UPDATE PARAM FIELD
  // =========================
  const updateField = (field, value) => {

    data.onChange(id, {

      ...data,

      params: {

        ...data.params,

        [field]: value
      }
    });
  };

  // =========================
  // CHANGE ACTION
  // =========================
  const changeAction = (newAction) => {

    data.onChange(id, {

      ...data,

      action: newAction,

      params: {}
    });
  };

  // =========================
  // VISUAL STATES
  // =========================
  const styles = {

    idle: {

      background: "#222",

      border: "1px solid #444",

      boxShadow: "none"
    },

    pending: {

      background: "#222",

      border: "1px solid #444",

      boxShadow: "none"
    },

    running: {

      background: "#16333a",

      border: "2px solid #4deeea",

      boxShadow:
        "0 0 20px rgba(77,238,234,0.8)"
    },

    success: {

      background: "#18361f",

      border: "2px solid #57ff89",

      boxShadow:
        "0 0 20px rgba(87,255,137,0.8)"
    },

    error: {

      background: "#3a1616",

      border: "2px solid #ff5c5c",

      boxShadow:
        "0 0 20px rgba(255,92,92,0.8)"
    }
  };

  const currentStyle =
    styles[state] || styles.idle;

  console.log("🧩 ACTION NODE:", data);

  return (

    <>

      {/* INPUT HANDLE */}
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: "#4deeea",
          width: 10,
          height: 10,
          border: "2px solid #fff"
        }}
      />

      <div
        style={{

          padding: 10,

          color: "#fff",

          borderRadius: 8,

          minWidth: 220,

          transform:

            state === "running"
              ? "scale(1.03)"
              : "scale(1)",

          transition: "all 0.25s ease",

          ...currentStyle
        }}
      >

        {/* HEADER */}
        <div
          style={{

            marginBottom: 10,

            fontWeight: "bold",

            color:

              state === "running"
                ? "#4deeea"

              : state === "success"
                ? "#57ff89"

              : state === "error"
                ? "#ff5c5c"

              : "#fff"
          }}
        >
          ⚙️ {config.label}
        </div>

        {/* SELECT ACTION */}
        <select
          value={action}
          onChange={(e) =>
            changeAction(e.target.value)
          }
          style={{

            width: "100%",

            marginBottom: 10,

            padding: 6,

            borderRadius: 6,

            background: "#111",

            color: "#fff",

            border: "1px solid #555"
          }}
        >
          {Object.entries(ACTIONS).map(
            ([key, a]) => (

              <option
                key={key}
                value={key}
              >
                {a.label}
              </option>
            )
          )}
        </select>

        {/* DYNAMIC INPUTS */}
        <div>

          {config.fields.map((f) => (

            <input
              key={f.name}

              placeholder={f.label}

              value={
                data.params?.[f.name] || ""
              }

              onChange={(e) =>
                updateField(
                  f.name,
                  e.target.value
                )
              }

              style={{

                display: "block",

                marginTop: 5,

                width: "100%",

                padding: 6,

                borderRadius: 5,

                border: "1px solid #555",

                background: "#111",

                color: "#fff"
              }}
            />

          ))}

        </div>

        {/* RETRY + TIMEOUT */}
        <div style={{ marginTop: 12 }}>

          <input
            type="number"

            placeholder="Retries"

            value={data.retry || 0}

            onChange={(e) =>

              data.onChange(id, {

                ...data,

                retry: Number(e.target.value)
              })
            }

            style={{

              width: "100%",

              marginBottom: 5,

              padding: 6,

              borderRadius: 5,

              border: "1px solid #555",

              background: "#111",

              color: "#fff"
            }}
          />

          <input
            type="number"

            placeholder="Timeout (sec)"

            value={data.timeout || 30}

            onChange={(e) =>

              data.onChange(id, {

                ...data,

                timeout: Number(e.target.value)
              })
            }

            style={{

              width: "100%",

              padding: 6,

              borderRadius: 5,

              border: "1px solid #555",

              background: "#111",

              color: "#fff"
            }}
          />

        </div>

      </div>

      {/* OUTPUT HANDLE */}
      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          background: "#57ff89",
          width: 10,
          height: 10,
          border: "2px solid #fff"
        }}
      />

    </>
  );
}