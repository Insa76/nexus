import { getAuthHeaders } from "./auth";

export async function runWorkflow(steps) {

  const res = await fetch("http://localhost:8010/jobs/run", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders()
    },
    body: JSON.stringify({
      name: "builder-workflow",
      steps
    })
  });

  return res.json();
}