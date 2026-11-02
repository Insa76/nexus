import asyncio

from core.ai_agent import ask_agent

from core.system_monitor import (
    get_running_processes
)

from core.accessibility import (
    get_active_window
)


class SystemAgent:

    def __init__(self):

        self.running = True

    async def loop(self):

        print("🧠 SYSTEM AGENT STARTED")

        while self.running:

            try:

                processes = (
                    get_running_processes()
                )

                active = (
                    get_active_window()
                )

                prompt = f"""
You are an AI operating system supervisor.

Active Window:
{active}

Processes:
{processes[:30]}

Analyze user context.

Explain:
- what the user is doing
- what applications are active
- possible automations
- possible assistance

Respond briefly.
"""

                response = ask_agent(
                    prompt
                )

                print(
                    f"🧠 SYSTEM ANALYSIS:\n{response}"
                )

                await asyncio.sleep(30)

            except Exception as e:

                print(
                    f"System agent error: {e}"
                )

                await asyncio.sleep(10)