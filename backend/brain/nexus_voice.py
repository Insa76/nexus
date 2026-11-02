from realtime.ws import manager as ws


async def speak(message, level="info"):

    text = f"Nexus: {message}"

    print(text)

    try:
        await ws.broadcast({
            "type": "nexus_voice",
            "message": text,
            "level": level
        })
    except:
        pass