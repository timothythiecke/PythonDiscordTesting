import requests
import asyncio
import websockets
import json

DISCORD_BASE_URL = "https://discordapp.com/api"
GATEWAY_URI = "wss://gateway.discord.gg/?v=6&encoding=json"

async def connectToGateway():
    async with websockets.connect(GATEWAY_URI) as websocket:
        r = await websocket.recv()
        if json.loads(r)["op"] == 10 : # Note: should probably do something if response is not opcode 10
            return json.loads(r)["d"]["heartbeat_interval"]

heartbeat_interval = asyncio.get_event_loop().run_until_complete(connectToGateway())

#asyncio.get_event_loop().run_forever

print (heartbeat_interval)
print("done")


