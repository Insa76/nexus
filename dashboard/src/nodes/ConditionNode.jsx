import { Handle, Position } from "reactflow"

export default function ConditionNode({ data }) {

  return (
    <div style={{
      background:"#222",
      color:"#fff",
      padding:12,
      borderRadius:10,
      minWidth:180,
      border:"2px solid #ffaa00"
    }}>
      <strong>IF</strong>
      <div style={{fontSize:12, marginTop:6}}>
        {data.if_action} {data.operator} {data.compare}
      </div>

      {/* entrada */}
      <Handle type="target" position={Position.Top} />

      {/* salida THEN */}
      <Handle
        type="source"
        position={Position.Left}
        id="then"
        style={{ background:"#00cc66" }}
      />

      {/* salida ELSE */}
      <Handle
        type="source"
        position={Position.Right}
        id="else"
        style={{ background:"#ff4444" }}
      />
    </div>
  )
}