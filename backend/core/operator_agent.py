import asyncio
import json
import re

import pyautogui

from core.ai_agent import ask_agent

from jobs.actions import execute_action

from core.vision import (
    detect_ui_elements
)

from core.object_detection import (
    detect_objects
)

from core.multimodal_memory import (
    save_multimodal_memory,
    load_recent_memories
)

from core.vector_memory import (
    save_vector_memory,
    search_memory
)

from core.learning import (
    load_patterns
)

from core.security import (
    MAX_AUTONOMOUS_STEPS
)


class OperatorAgent:

    def __init__(self):

        self.running = False

    async def execute_goal(

        self,

        goal,

        max_steps=20
    ):

        # =========================
        # SECURITY LIMIT
        # =========================
        max_steps = min(
            max_steps,
            MAX_AUTONOMOUS_STEPS
        )

        self.running = True

        print(f"🧠 OPERATOR GOAL: {goal}")

        # =========================
        # LOAD MEMORIES
        # =========================
        visual_memories = load_recent_memories(
            "operator_agent",
            limit=5
        )

        semantic_memories = search_memory(
            "main_agent",
            goal
        )

        learned_patterns = load_patterns()

        # =========================
        # BUILD MEMORY CONTEXT
        # =========================
        visual_context = "\n".join([

            f"""
OCR:
{m["ocr_text"]}

Objects:
{m["objects"]}
"""

            for m in visual_memories
        ])

        semantic_context = "\n".join([

            m["memory"]["content"]

            for m in semantic_memories
        ])

        patterns_context = "\n".join([

            f"""
Pattern:
{p["pattern"]}

Solution:
{p["solution"]}
"""

            for p in learned_patterns
        ])

        # =========================
        # EXECUTION LOOP
        # =========================
        for step in range(max_steps):

            print(f"\n👁 OPERATOR STEP {step+1}")

            try:

                # =========================
                # SCREENSHOT
                # =========================
                image = pyautogui.screenshot()

                path = "operator_screen.png"

                image.save(path)

                # =========================
                # OCR UI
                # =========================
                ui = detect_ui_elements(
                    path
                )

                # =========================
                # OBJECT DETECTION
                # =========================
                objects = detect_objects(
                    path
                )

                # =========================
                # BUILD UI TEXT
                # =========================
                ui_text = "\n".join([

                    el["text"]

                    for el in ui
                ])

                # =========================
                # SAVE MULTIMODAL MEMORY
                # =========================
                save_multimodal_memory(

                    "operator_agent",

                    path,

                    ui_text,

                    objects,

                    {
                        "goal": goal,
                        "step": step + 1
                    }
                )

                # =========================
                # PROMPT
                # =========================
                prompt = f"""
You are an autonomous AI operator.

Goal:
{goal}

Current Step:
{step+1}

Visible UI:
{ui_text}

Detected Objects:
{objects}

Previous Visual Memories:
{visual_context}

Semantic Memories:
{semantic_context}

Learned Repair Patterns:
{patterns_context}

You can use these actions:

- open_url
- vision_click
- type_text
- screenshot
- focus_window
- detect_objects
- vision_read

Rules:
- Think step by step
- Avoid loops
- Be efficient
- Complete the goal safely

Respond ONLY valid JSON.

Open URL:

{{
  "action": "open_url",
  "params": {{
    "url": "https://google.com"
  }}
}}

Click:

{{
  "action": "vision_click",
  "params": {{
    "target": "Search"
  }}
}}

Type:

{{
  "action": "type_text",
  "params": {{
    "text": "Hello"
  }}
}}

Focus Window:

{{
  "action": "focus_window",
  "params": {{
    "title": "Chrome"
  }}
}}

Done:

{{
  "action": "done"
}}
"""

                # =========================
                # ASK AGENT
                # =========================
                response = ask_agent(
                    prompt
                )

                print(f"🧠 OPERATOR RESPONSE:\n{response}")

                # =========================
                # EXTRACT JSON
                # =========================
                match = re.search(
                    r"\{.*\}",
                    response,
                    re.DOTALL
                )

                if not match:

                    print("⚠️ INVALID JSON RESPONSE")

                    continue

                parsed = json.loads(
                    match.group(0)
                )

                action = parsed.get(
                    "action"
                )

                # =========================
                # DONE
                # =========================
                if action == "done":

                    print("✅ GOAL COMPLETE")

                    save_vector_memory(

                        "main_agent",

                        f"""
Goal completed:

{goal}
"""
                    )

                    return {
                        "success": True,
                        "goal": goal
                    }

                # =========================
                # PARAMS
                # =========================
                params = parsed.get(
                    "params",
                    {}
                )

                print(
                    f"⚙️ EXECUTING: {action}"
                )

                print(
                    f"📦 PARAMS: {params}"
                )

                # =========================
                # EXECUTE ACTION
                # =========================
                result = await execute_action(
                    action,
                    params
                )

                print(
                    f"✅ RESULT: {result}"
                )

                # =========================
                # SAVE EXPERIENCE
                # =========================
                save_vector_memory(

                    "main_agent",

                    f"""
Goal:
{goal}

Action:
{action}

Params:
{params}

Result:
{result}
"""
                )

                # =========================
                # SMALL DELAY
                # =========================
                await asyncio.sleep(2)

            except Exception as e:

                print(
                    f"💥 OPERATOR ERROR: {e}"
                )

                save_vector_memory(

                    "main_agent",

                    f"""
Operator error:

{str(e)}
"""
                )

                await asyncio.sleep(2)

        # =========================
        # MAX STEPS REACHED
        # =========================
        print("⚠️ MAX STEPS REACHED")

        return {
            "success": False,
            "error": "Max steps reached"
        }