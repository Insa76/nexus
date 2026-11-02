import ollama
import json

from memory.search import search_memory
from context.system_context import get_context
from history.store import load_history, save_history

from brain.personal_memory.store import save_memory
from brain.personal_memory.recall import recall
from brain.personal_memory.extractor import should_remember

from brain.autonomous.runner import run_autonomous

from brain.semantic.recall import recall_semantic
from brain.semantic.learner import learn_from_interaction
from brain.semantic.vector_store import save_vector_memory
from brain.semantic.ranking import search_similar


SYSTEM_PROMPT = """
Sos Nexus, un asistente de sistema local inteligente.

REGLAS ESTRICTAS:

SIEMPRE devolver SOLO uno de estos formatos:

Acción simple:
{ "action": "open_app", "value": "chrome" }

Texto:
{ "response": "texto" }

NUNCA usar:
- type
- data
- launch_app
- formatos inventados

Sé breve, directo y práctico.
"""


# =========================================================
# 🔥 Parser tolerante (corrige formatos raros del LLM)
# =========================================================
def normalize_result(result):

    if not isinstance(result, dict):
        return {"response": str(result)}

    # formato correcto
    if "action" in result or "response" in result:
        return result

    # formato inventado tipo:
    # { type: "LAUNCH_APP", data: { app_name: "Chrome" } }
    if "type" in result:
        t = str(result["type"]).lower()

        if "launch" in t or "open" in t:
            app = result.get("data", {}).get("app_name", "")
            return {"action": "open_app", "value": app}

    return {"response": str(result)}


# =========================================================
# 🧠 Cerebro principal
# =========================================================
def ask_nexus(message: str, user=None):

    if user is None:
        user = {"id": "default"}

    user_id = user.get("id", "default")

    lower = message.lower()

    # =====================================================
    # 1️⃣ Tareas complejas → agente autónomo
    # =====================================================
    if any(x in lower for x in [
        "prepará", "analizá", "organiza todo",
        "hacé todo", "completo", "automáticamente"
    ]):
        result = run_autonomous(message, user)
        return {"response": result}

    # =====================================================
    # 2️⃣ Contextos inteligentes
    # =====================================================
    memory_context = search_memory(message)
    system_ctx = get_context()
    personal_memories = recall(message)
    semantic_mem = recall_semantic(user_id)

    # =====================================================
    # 3️⃣ Historial conversacional
    # =====================================================
    history = load_history()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Contexto del sistema:\n{system_ctx}"}
    ]

    if memory_context:
        messages.append({
            "role": "system",
            "content": f"Contexto de archivos:\n{memory_context}"
        })

    if personal_memories:
        messages.append({
            "role": "system",
            "content": f"Memoria personal relevante:\n{personal_memories}"
        })

    if semantic_mem:
        messages.append({
            "role": "system",
            "content": f"Memoria semántica del usuario:\n{semantic_mem}"
        })

    # últimos intercambios
    for h in history[-6:]:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["assistant"]})

    messages.append({"role": "user", "content": message})

    similar = search_similar(user.get("id","default"), message)

    if similar:
       memory_context = "\n".join([x[1] for x in similar])
       messages.append({
        "role": "system",
        "content": f"Memoria relevante:\n{memory_context}"
    })

    # =====================================================
    # 4️⃣ LLM
    # =====================================================
    try:
        res = ollama.chat(
            model="llama3",
            messages=messages
        )

        content = res["message"]["content"]

    except Exception as e:
        return {"response": f"Error LLM: {str(e)}"}
    
    save_vector_memory(user.get("id","default"), message)

    # =====================================================
    # 5️⃣ Parseo robusto
    # =====================================================
    try:
        parsed = json.loads(content)
        result = normalize_result(parsed)
    except Exception:
        result = {"response": content}

    # =====================================================
    # 6️⃣ Guardar historial
    # =====================================================
    history.append({
        "user": message,
        "assistant": result.get("response") or str(result)
    })

    save_history(history)

    # =====================================================
    # 7️⃣ Memoria personal
    # =====================================================
    if should_remember(message):
        save_memory(message)

    # =====================================================
    # 8️⃣ Aprendizaje semántico automático
    # =====================================================
    learn_from_interaction(
        user_id,
        message,
        result.get("response", "")
    )

    return result