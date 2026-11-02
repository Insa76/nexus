import os
import shutil
import webbrowser
import json
import re
import pyautogui
import asyncio

from core.ai_agent import ask_agent

from core.agent_memory import (
    save_memory,
    load_memory
)

from core.agents import (
    PlannerAgent,
    SupervisorAgent
)

from core.vector_memory import (
    save_vector_memory,
    search_memory
)

from core.workflow_generator import (
    generate_workflow
)

from core.security import (
    validate_action
)

from core.vision import (
    extract_text
)

from core.vision import (
    detect_ui_elements
)

from core.object_detection import (
    detect_objects
)

from core.accessibility import (
    list_ui_elements
)

from core.accessibility import (
    click_ui_element
)

from core.multimodal_memory import (
    save_multimodal_memory,
    load_recent_memories
)



BASE_PATH = r"C:\Users\cdi40\Desktop"


async def execute_action(action, value):

    print(f"📂 BASE PATH: {BASE_PATH}")
    print(f"📄 EXISTS: {os.path.exists(BASE_PATH)}")
    print(f"🔥 STEP: {action} → {value}")

    safe, reason = validate_action(
    action,
    value
  )

    if not safe:

       print(
          f"🛑 BLOCKED: {reason}"
       )

       return {
          "success": False,
          "blocked": True,
          "reason": reason
        }

    # ==========================================================
    # CREATE FOLDER
    # ==========================================================
    if action == "create_folder":

        folder_path = os.path.join(
            BASE_PATH,
            value["path"].strip()
        )

        os.makedirs(folder_path, exist_ok=True)

        print(f"📁 Carpeta creada: {folder_path}")

        return {
            "success": True
        }

    # ==========================================================
    # MOVE FILES
    # ==========================================================
    elif action == "move_files":

        files = os.listdir(BASE_PATH)

        print(f"📄 ARCHIVOS: {files}")

        moved = 0

        destination = os.path.join(
            BASE_PATH,
            value["to"].strip()
        )

        os.makedirs(destination, exist_ok=True)

        for f in files:

            if f.endswith(value["ext"]):

                source = os.path.join(
                    BASE_PATH,
                    f
                )

                target = os.path.join(
                    destination,
                    f
                )

                shutil.move(source, target)

                moved += 1

                print(f"📦 Movido: {f}")

        print(f"✅ Total movidos: {moved}")

        return {
            "success": True,
            "moved": moved
        }

    # ==========================================================
    # OPEN URL
    # ==========================================================
    elif action == "open_url":

        webbrowser.open(value["url"])

        print(f"🌐 URL abierta: {value['url']}")

        return {
            "success": True
        }

    # ==========================================================
    # JOIN
    # ==========================================================
    elif action == "join":

        print("🔗 JOIN NODE")

        return {
            "success": True
        }

    # ==========================================================
    # APPROVAL
    # ==========================================================
    elif action == "approval":

        print("🛑 WAITING APPROVAL")

        return {
            "waiting_approval": True
        }

    # ==========================================================
    # IF EXTENSION
    # ==========================================================
    elif action == "if_extension":

        ext = value["ext"]

        files = os.listdir(BASE_PATH)

        found = any(
            f.endswith(ext)
            for f in files
        )

        print(f"🔍 IF EXTENSION {ext}: {found}")

        return {
            "success": found
        }

    # ==========================================================
    # AI CLASSIFY FILE
    # ==========================================================
    elif action == "ai_classify_file":

        files = os.listdir(BASE_PATH)

        pdfs = [
            f for f in files
            if f.endswith(".pdf")
        ]

        if not pdfs:

            return {
                "decision": "none"
            }

        filename = pdfs[0]

        print(f"🧠 AI ANALYZING: {filename}")

        lower = filename.lower()

        if "factura" in lower:

            decision = "invoice"

        elif "contrato" in lower:

            decision = "contract"

        else:

            decision = "unknown"

        print(f"🧠 AI DECISION: {decision}")

        return {
            "success": True,
            "decision": decision
        }

    # ==========================================================
    # AI AGENT
    # ==========================================================
    elif action == "ai_agent":

        files = os.listdir(BASE_PATH)

        context = "\n".join(files)

        prompt = value.get(
            "prompt",
            ""
        )

        model = value.get(
            "model",
            "llama3"
        )

        full_prompt = f"""
Archivos actuales:

{context}

{prompt}
"""

        print("🧠 ASKING AGENT")

        response = ask_agent(
            full_prompt,
            model
        )

        print(f"🧠 AGENT RESPONSE: {response}")

        return {
            "success": True,
            "decision": response.strip()
        }

    # ==========================================================
    # AI TOOL AGENT
    # ==========================================================
    elif action == "ai_tool_agent":

        goal = value.get(
            "goal",
            ""
        )

        model = value.get(
            "model",
            "llama3"
        )

        tools = """

AVAILABLE TOOLS:

1. create_folder
params:
{
  "path": "string"
}

2. move_files
params:
{
  "ext": ".pdf",
  "to": "folder"
}

3. open_url
params:
{
  "url": "https://..."
}

"""

        prompt = f"""
You are an automation AI.

Goal:
{goal}

{tools}

Respond ONLY valid JSON:

{{
  "tool": "...",
  "params": {{}}
}}
"""

        print("🧠 ASKING TOOL AGENT")

        response = ask_agent(
            prompt,
            model
        )

        print(f"🧠 TOOL AGENT RAW: {response}")

        # ======================================================
        # EXTRACT JSON
        # ======================================================
        match = re.search(
            r"\{.*\}",
            response,
            re.DOTALL
        )

        if not match:

            print("❌ NO JSON RETURNED")

            return {
                "success": False
            }

        parsed = json.loads(
            match.group(0)
        )

        tool = parsed.get("tool")

        params = parsed.get(
            "params",
            {}
        )

        print(f"🛠 TOOL: {tool}")
        print(f"🛠 PARAMS: {params}")

        # ======================================================
        # EXECUTE TOOL
        # ======================================================
        tool_result = await execute_action(
            tool,
            params
        )

        return {
            "success": True,
            "tool": tool,
            "tool_result": tool_result
        }

    # ==========================================================
    # AI AUTONOMOUS AGENT
    # ==========================================================
    elif action == "ai_autonomous_agent":

        goal = value.get(
            "goal",
            ""
        )

        model = value.get(
            "model",
            "llama3"
        )

        max_steps = int(
            value.get(
                "max_steps",
                5
            )
        )

        # ======================================================
        # AGENTS
        # ======================================================
        planner = PlannerAgent()

        supervisor = SupervisorAgent()

        print(f"🧠 AUTONOMOUS GOAL: {goal}")

        # ======================================================
        # TOOLS
        # ======================================================
        tools = """

AVAILABLE TOOLS:

1. create_folder
params:
{
  "path": "string"
}

2. move_files
params:
{
  "ext": ".pdf",
  "to": "folder"
}

3. open_url
params:
{
  "url": "https://..."
}

4. if_extension
params:
{
  "ext": ".pdf"
}

"""

        # ======================================================
        # MEMORY
        # ======================================================
        memory = load_memory(
            "main_agent",
            limit=10
        )

        memory_text = "\n".join([

            f"""
Role: {m['role']}
Content: {m['content']}
"""

            for m in memory
        ])

        # ======================================================
        # VECTOR MEMORY
        # ======================================================
        similar_memories = search_memory(
            "main_agent",
            goal
        )

        memory_context = "\n".join([

            m["memory"]["content"]

            for m in similar_memories
        ])

        # ======================================================
        # AGENT HISTORY
        # ======================================================
        history = []

        from core.security import (
         MAX_AUTONOMOUS_STEPS
        )

        max_steps = min(
          max_steps,
          MAX_AUTONOMOUS_STEPS
        )

        # ======================================================
        # AGENT LOOP
        # ======================================================
        for step_index in range(max_steps):

            print(f"\n🧠 AGENT STEP {step_index + 1}")

            # ==================================================
            # FILE CONTEXT
            # ==================================================
            try:

                files = os.listdir(BASE_PATH)

            except Exception:

                files = []

            context = "\n".join(files)

            # ==================================================
            # HISTORY
            # ==================================================
            history_text = "\n".join(history)

            # ==================================================
            # PROMPT
            # ==================================================
            prompt = f"""
You are an autonomous automation AI.

Your job is to achieve the user's goal using tools.

GOAL:
{goal}

FILES:
{context}

PREVIOUS MEMORY:
{memory_text}

RELEVANT MEMORIES:
{memory_context}

TOOLS:
{tools}

PREVIOUS STEPS:
{history_text}

RULES:
- Respond ONLY valid JSON
- Never explain
- Never use markdown
- One tool at a time

If the goal is complete:

{{
  "done": true
}}

Otherwise:

{{
  "tool": "tool_name",
  "params": {{}}
}}
"""

            # ==================================================
            # PLANNER
            # ==================================================
            response = planner.plan(
                goal,
                tools,
                history_text + "\n" + memory_context
            )

            print(f"🧠 RAW RESPONSE: {response}")

            # ==================================================
            # PARSE JSON
            # ==================================================
            try:

                match = re.search(
                    r"\{.*\}",
                    response,
                    re.DOTALL
                )

                if not match:

                    history.append(
                        "Invalid JSON response"
                    )

                    continue

                parsed = json.loads(
                    match.group(0)
                )

            except Exception as e:

                history.append(
                    f"JSON parse error: {str(e)}"
                )

                save_memory(
                    "main_agent",
                    "error",
                    str(e)
                )

                continue

            # ==================================================
            # DONE
            # ==================================================
            if parsed.get("done"):

                print("✅ AGENT COMPLETE")

                save_memory(
                    "main_agent",
                    "goal_completed",
                    goal
                )

                save_vector_memory(
                    "main_agent",
                    f"Completed goal: {goal}"
                )

                return {
                    "success": True,
                    "history": history
                }

            # ==================================================
            # TOOL
            # ==================================================
            tool = parsed.get("tool")

            params = parsed.get(
                "params",
                {}
            )

            print(f"🛠 TOOL: {tool}")
            print(f"📦 PARAMS: {params}")

            # ==================================================
            # TOOL EXECUTION
            # ==================================================
            try:

                tool_result = await execute_action(
                    tool,
                    params
                )

                print(f"✅ TOOL RESULT: {tool_result}")

                # ==============================================
                # SUPERVISOR
                # ==============================================
                review = supervisor.review(
                    history
                )

                print(f"🛡 SUPERVISOR: {review}")

                if "stop" in review.lower():

                    print("🛑 SUPERVISOR STOPPED AGENT")

                    save_memory(
                        "main_agent",
                        "supervisor_stop",
                        review
                    )

                    return {
                        "success": False,
                        "error": "Supervisor stopped execution"
                    }

            except Exception as tool_error:

                print(f"❌ TOOL ERROR: {tool_error}")

                save_memory(
                    "main_agent",
                    "tool_error",
                    str(tool_error)
                )

                save_vector_memory(
                    "main_agent",
                    f"Tool error: {tool_error}"
                )

                history.append(f"""
Tool:
{tool}

Params:
{params}

Error:
{str(tool_error)}
""")

                continue

            # ==================================================
            # SAVE MEMORY
            # ==================================================
            save_memory(

                "main_agent",

                "tool_execution",

                f"""
Tool: {tool}

Params:
{params}

Result:
{tool_result}
""",

                {
                    "tool": tool
                }
            )

            # ==================================================
            # SAVE VECTOR MEMORY
            # ==================================================
            save_vector_memory(

                "main_agent",

                f"""
Tool: {tool}

Params:
{params}

Result:
{tool_result}
"""
            )

            # ==================================================
            # OBSERVATION HISTORY
            # ==================================================
            history.append(f"""
Tool:
{tool}

Params:
{params}

Result:
{tool_result}
""")

        # ======================================================
        # MAX STEPS REACHED
        # ======================================================
        print("❌ MAX STEPS REACHED")

        save_memory(
            "main_agent",
            "max_steps",
            goal
        )

        save_vector_memory(
            "main_agent",
            f"Max steps reached for goal: {goal}"
        )

        return {
            "success": False,
            "error": "Max steps reached",
            "history": history
        }
    
    elif action == "ai_generate_workflow":

       goal = value.get(
           "goal",
           ""
        )

       model = value.get(
           "model",
           "llama3"
        )

       workflow = generate_workflow(
           goal,
           model
        )

       print(f"🧠 GENERATED DAG: {workflow}")

       return {
          "success": True,
          "workflow": workflow
        }
    
    elif action == "click":

       x = int(value.get("x", 0))
       y = int(value.get("y", 0))

       pyautogui.click(x, y)

       print(f"🖱 CLICK: {x},{y}")

       return {
          "success": True
        }
    
    elif action == "type_text":

       text = value.get(
          "text",
          ""
        )

       pyautogui.write(
          text,
          interval=0.02
        )

       print(f"⌨️ TEXT: {text}")

       return {
          "success": True
        }
    
    elif action == "screenshot":

       image = pyautogui.screenshot()

       path = "latest_screen.png"

       image.save(path)

       print(f"📸 SCREENSHOT: {path}")

       return {
          "success": True,
          "path": path
        }
    
    elif action == "vision_read":

       image = pyautogui.screenshot()

       path = "vision.png"

       image.save(path)

       text = extract_text(path)

       print(f"👁 VISION:\n{text}")

       return {
          "success": True,
          "text": text
        }
    
    elif action == "ai_vision_agent":

       image = pyautogui.screenshot()

       path = "vision_agent.png"

       image.save(path)

       text = extract_text(path)

       goal = value.get(
          "goal",
          ""
        )

       prompt = f"""
You are a visual AI assistant.

Screen content:

{text}

Goal:
{goal}

What should the user click or do next?

Respond briefly.
"""

       response = ask_agent(prompt)

       print(f"👁🧠 VISION AI: {response}")

       return {
         "success": True,
         "response": response
        }
    
    elif action == "vision_click":

       target = value.get(
          "target",
          ""
        ).lower()

       image = pyautogui.screenshot()

       path = "vision_click.png"

       image.save(path)

       elements = detect_ui_elements(
          path
        )

       print(f"👁 ELEMENTS: {elements}")

       for el in elements:

          text = el["text"].lower()

          if target in text:

            x = el["x"] + el["w"] // 2
            y = el["y"] + el["h"] // 2

            pyautogui.click(x, y)

            print(
                f"🖱 CLICKED: {target}"
            )

            return {
                "success": True,

                "clicked": target,

                "x": x,

                "y": y
            }

       return {
          "success": False,
          "error": "Target not found"
        }
    
    elif action == "visual_autonomous_agent":

       goal = value.get(
          "goal",
          ""
        )

       # ====================================
       # LOAD VISUAL MEMORIES
       # ====================================
       memories = load_recent_memories(
           "vision_agent",
           limit=5
        )

       memory_context = "\n".join([

           f"""
OCR:
{m["ocr_text"]}

Objects:
{m["objects"]}
"""

           for m in memories
       ])

       # ====================================
       # VISUAL LOOP
       # ====================================
       for step in range(10):

           print(f"👁 STEP {step+1}")

           image = pyautogui.screenshot()

           path = "visual_loop.png"

           image.save(path)

           # ====================================
           # OCR UI
           # ====================================
           elements = detect_ui_elements(
               path
            )

           ui_text = "\n".join([

               el["text"]

               for el in elements
           ])

           # ====================================
           # OBJECT DETECTION
           # ====================================
           objects = detect_objects(
               path
            )

           # ====================================
           # SAVE MULTIMODAL MEMORY
           # ====================================
           save_multimodal_memory(

              "vision_agent",

              path,

              ui_text,

              objects,

              {
                  "goal": goal,
                  "step": step + 1
            }
          )

          # ====================================
          # AI PROMPT
          # ====================================
           prompt = f"""
You are a visual AI operator.

Goal:
{goal}

Previous Visual Memories:

{memory_context}

Visible UI:

{ui_text}

Detected Objects:

{objects}

Decide the next action.

Respond ONLY valid JSON.

Click:

{{
  "action": "click",
  "target": "Search"
}}

Type:

{{
  "action": "type",
  "text": "Hello"
}}

Done:

{{
  "action": "done"
}}
"""

        # ====================================
        # ASK AGENT
        # ====================================
           response = ask_agent(
              prompt
            )

           print(f"👁🧠 {response}")

          # ====================================
          # PARSE JSON
          # ====================================
           match = re.search(
              r"\{.*\}",
              response,
              re.DOTALL
            )

           if not match:

               print("⚠️ INVALID AI RESPONSE")

               continue

           parsed = json.loads(
               match.group(0)
            )

           # ====================================
           # ROUTING
           # ====================================
           action_type = parsed.get(
               "action"
            )

           # ====================================
           # DONE
           # ====================================
           if action_type == "done":

              print("✅ VISUAL GOAL COMPLETED")

              return {
                  "success": True
              }

           # ====================================
           # CLICK
           # ====================================
           elif action_type == "click":

              target = parsed.get(
                  "target",
                  ""
                )

              print(f"🖱 TARGET: {target}")

              await execute_action(

                  "vision_click",

                  {
                    "target": target
                  }
              )

           # ====================================
           # TYPE
           # ====================================
           elif action_type == "type":

              text = parsed.get(
                 "text",
                 ""
                )

              print(f"⌨️ TYPE: {text}")

              await execute_action(

                 "type_text",

                 {
                    "text": text
                 }
              )

           # ====================================
           # WAIT UI UPDATE
           # ====================================
           await asyncio.sleep(1)

    # ====================================
    # MAX STEPS
    # ====================================
       return {

          "success": False,

          "error": "Max visual steps reached"
        }
    
    elif action == "detect_objects":

       image = pyautogui.screenshot()

       path = "objects.png"

       image.save(path)

       detections = detect_objects(
          path
        )

       print(f"🎯 OBJECTS: {detections}")

       return {
          "success": True,
          "objects": detections
        }
    
    elif action == "ai_visual_reasoning":

       image = pyautogui.screenshot()

       path = "visual_reasoning.png"

       image.save(path)

       text = extract_text(path)

       objects = detect_objects(
          path
        )

       goal = value.get(
          "goal",
          ""
        )

       prompt = f"""
You are a visual AI system.

Goal:
{goal}

OCR Text:
{text}

Detected Objects:
{objects}

Analyze the screen.

Explain what is happening.
"""

    # =========================
    # PASO 7
    # ASK AGENT
    # =========================
       response = ask_agent(
          prompt
        )

       print(
          f"🧠👁 VISUAL REASONING: {response}"
        )

    # =========================
    # PASO 8
    # RETURN
    # =========================
       return {
          "success": True,
          "response": response
        }
    
    elif action == "list_ui":

       elements = list_ui_elements()

       print(f"🪟 UI: {elements}")

       return {
         "success": True,
         "elements": elements
       }
    
    elif action == "focus_window":

       title = value.get(
          "title",
          ""
        )

       ok = click_ui_element(
          title
        )

       return {
          "success": ok
       }

    # ==========================================================
    # UNKNOWN ACTION
    # ==========================================================
    else:

        raise Exception(
            f"Acción no soportada: {action}"
        )