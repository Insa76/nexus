import asyncio
from bootstrap.bootstrap import build_engine

async def main():
    engine = build_engine()

    first = await engine.execute("abrí Chrome")
    print("1:", first.success, first.metadata.get("response"))

    second = await engine.execute("¿qué aplicación abrí?")
    print("2:", second.success, second.metadata.get("response"))

asyncio.run(main())
