import asyncio
from brain.patterns import analyze_patterns
from realtime.ws import manager as ws

INTERVAL_SECONDS = 1800  # 30 min


async def periodic_analysis():

    print("🧠 Proactive AI iniciada")

    while True:

        try:
            suggestions = analyze_patterns()

            if suggestions:

                await ws.broadcast({
                    "type": "ai_suggestion",
                    "data": suggestions
                })

                print("🧠 Nueva sugerencia enviada")

        except Exception as e:
            print("Proactive AI error:", e)

        await asyncio.sleep(INTERVAL_SECONDS)