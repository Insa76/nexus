import asyncio
import os
import json
import re

from core.ai_agent import ask_agent

from jobs.actions import execute_action


class DesktopWatcherAgent:

    def __init__(self):

        self.running = True

        self.previous_files = set()

    async def loop(self):

        print("👁 DesktopWatcher started")

        while self.running:

            try:

                files = set(
                    os.listdir(
                        "C:/Users/cdi40/Desktop"
                    )
                )

                new_files = (
                    files
                    - self.previous_files
                )

                if new_files:

                    print(
                        f"📄 NEW FILES: {new_files}"
                    )

                    await self.handle_new_files(
                        list(new_files)
                    )

                self.previous_files = files

                await asyncio.sleep(5)

            except Exception as e:

                print(
                    f"Watcher error: {e}"
                )

                await asyncio.sleep(10)

    async def handle_new_files(
        self,
        files
    ):

        prompt = f"""
You are a desktop automation AI.

New files:

{files}

Decide what to do.

Respond ONLY valid JSON.

{{
  "action": "...",
  "params": {{}}
}}
"""

        response = ask_agent(
            prompt
        )

        print(f"🧠 WATCHER: {response}")

        match = re.search(
           r"\{.*\}",
           response,
           re.DOTALL
        )

        if not match:
          return

        parsed = json.loads(
           match.group(0)
        )

        action = parsed.get(
          "action"
        )

        params = parsed.get(
          "params",
          {}
        )

        await execute_action(
          action,
          params
        )