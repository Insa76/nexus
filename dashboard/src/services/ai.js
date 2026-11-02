import { getAuthHeaders } from "./auth";

export async function generateWorkflow(prompt) {

  try {

    const res = await fetch("http://localhost:8010/ai-builder/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders()
      },
      body: JSON.stringify({ prompt })
    });

    const text = await res.text(); // 🔥 clave

    console.log("🧠 RAW RESPONSE:", text);

    if (!res.ok) {
      throw new Error(text);
    }

    const data = JSON.parse(text);

    return data;

  } catch (err) {

    console.error("🔥 ERROR IA:", err);

    alert("ERROR IA:\n" + err.message);

    throw err;
  }
}