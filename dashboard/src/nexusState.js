export const NexusState = {
  mode: "idle" // idle | listening | thinking | speaking
}

export const setMode = (m)=>{
  NexusState.mode = m
}
