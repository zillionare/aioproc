from aioproc import aioprocess

async def main():
    proc = await aioprocess("python", "-m", "http.server", detached=True)
    #await proc.wait()

import asyncio

asyncio.run(main())
