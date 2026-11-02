from core.ai_agent import ask_agent

from core.agent_bus import (
    send_message,
    get_messages
)

# 🔥 LEARNING IMPORT
from core.learning import (
    load_patterns
)


# ==========================================================
# PLANNER AGENT
# ==========================================================
class PlannerAgent:

    def plan(
        self,
        goal,
        tools,
        memory=""
    ):

        # =========================
        # SEND MESSAGE
        # =========================
        send_message(
            "planner",
            "supervisor",
            f"Planning action for goal: {goal}"
        )

        # =========================
        # LOAD MESSAGES
        # =========================
        messages = get_messages(
            "planner"
        )

        message_context = "\n".join([

            f"""
FROM: {m['sender']}

MESSAGE:
{m['message']}
"""

            for m in messages
        ])

        # =========================
        # PROMPT
        # =========================
        prompt = f"""
You are a planning agent.

Goal:
{goal}

Available tools:
{tools}

Memory:
{memory}

Agent Messages:
{message_context}

Create the next best action.

Respond ONLY valid JSON:

{{
  "tool": "...",
  "params": {{}}
}}
"""

        # =========================
        # ASK AGENT
        # =========================
        return ask_agent(prompt)


# ==========================================================
# SUPERVISOR AGENT
# ==========================================================
class SupervisorAgent:

    def review(
        self,
        history
    ):

        # =========================
        # LOAD MESSAGES
        # =========================
        messages = get_messages(
            "supervisor"
        )

        message_context = "\n".join([

            f"""
FROM: {m['sender']}

MESSAGE:
{m['message']}
"""

            for m in messages
        ])

        # =========================
        # PROMPT
        # =========================
        prompt = f"""
You are a supervisor AI.

Review this execution history:

{history}

Agent Messages:

{message_context}

Detect:
- loops
- repeated failures
- dangerous behavior

Respond ONLY:
safe
or
stop
"""

        # =========================
        # ASK AGENT
        # =========================
        return ask_agent(prompt)


# ==========================================================
# HEALING AGENT
# ==========================================================
class HealingAgent:

    def heal(

        self,

        error,

        node,

        history=""
    ):

        # =========================
        # LOAD LEARNED PATTERNS
        # =========================
        patterns = load_patterns()

        # =========================
        # BUILD PATTERN CONTEXT
        # =========================
        pattern_context = "\n".join([

            f"""
Pattern:
{p["pattern"]}

Solution:
{p["solution"]}
"""

            for p in patterns
        ])

        # =========================
        # PROMPT
        # =========================
        prompt = f"""
You are a workflow healing AI.

Node:
{node}

Error:
{error}

History:
{history}

Known Successful Repairs:

{pattern_context}

Suggest a repair.

Respond ONLY valid JSON.

{{
  "action": "...",
  "params": {{}}
}}
"""

        # =========================
        # ASK AGENT
        # =========================
        return ask_agent(prompt)


# ==========================================================
# RUNTIME SUPERVISOR AGENT
# ==========================================================
class RuntimeSupervisorAgent:

    def analyze(

        self,

        jobs,
        metrics,
        logs
    ):

        prompt = f"""
You are an AI runtime supervisor.

Jobs:
{jobs}

Metrics:
{metrics}

Logs:
{logs}

Analyze:
- failures
- loops
- overload
- dangerous workflows
- instability

Detect:
- dangerous tools
- suspicious behavior
- recursive loops
- uncontrolled scaling

Respond ONLY valid JSON.

{{
  "status": "healthy|warning|critical",

  "recommendation": "...",

  "action": "none|scale_up|pause_jobs"
}}
"""

        return ask_agent(prompt)