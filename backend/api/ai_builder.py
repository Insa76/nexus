import json
import re
from core.llm import generate_steps
from fastapi import APIRouter, Depends
from auth.deps import get_current_user

router = APIRouter(prefix="/ai-builder")


@router.post("/generate")
async def generate(data: dict, user=Depends(get_current_user)):

    prompt = data.get("prompt")

    raw = generate_steps(prompt)

    print("🧠 RAW LLM:", raw)

    try:
        # =========================
        # 🔥 EXTRAER SOLO JSON
        # =========================
        match = re.search(r"\{.*\}", raw, re.DOTALL)

        if not match:
            raise Exception("No se encontró JSON")

        clean_json = match.group(0)

        parsed = json.loads(clean_json)

        steps = validate_steps(parsed.get("steps", []))

        return {"steps": steps}

    except Exception as e:

        print("❌ AI BUILDER ERROR:", str(e))

        return {
            "error": "LLM devolvió JSON inválido",
            "raw": raw
        }



# =========================
# FIX JSON (🔥 CLAVE)
# =========================

def fix_json(text: str):

    # cerrar llaves faltantes
    open_braces = text.count("{")
    close_braces = text.count("}")

    if open_braces > close_braces:
        text += "}" * (open_braces - close_braces)

    # cerrar corchetes faltantes
    open_brackets = text.count("[")
    close_brackets = text.count("]")

    if open_brackets > close_brackets:
        text += "]" * (open_brackets - close_brackets)

    return text


# =========================
# EXTRACT JSON
# =========================

def extract_json(text):

    match = re.search(r"\{.*", text, re.DOTALL)

    if match:
        return match.group(0)

    return text


# =========================
# VALIDATE
# =========================

VALID_ACTIONS = {
    "create_folder",
    "move_files",
    "open_url"
}


def validate_steps(steps):

    safe = []

    for s in steps:

        if s.get("action") not in VALID_ACTIONS:
            continue

        safe.append(s)

    return safe