import sys
import requests
import asyncio
import websockets
import json
from time import sleep

DISCORD_BASE_URL = "https://discordapp.com/api"
GATEWAY_URI = "wss://gateway.discord.gg/?v=6&encoding=json"

async def connectToGateway():
    async with websockets.connect(GATEWAY_URI) as websocket:
        print('Waiting for hello')
        r = await websocket.recv()
        heartbeat_interval = 0
        if json.loads(r)["op"] == 10 : # Note: should probably do something if response is not opcode 10
            heartbeat_interval = json.loads(r)["d"]["heartbeat_interval"]
            print('Hello received', heartbeat_interval)

        # TODO: Need to take another look as to why the json methods did not work
        await websocket.send(""" 
        {{
            "op": 2,
            "d": {{
                "token": "{0}", 
                "properties": {{	
                    "$os": "windows",
                    "$browser": "disco",
                    "$device": "disco"
                }},
                "compress": false,
                "large_threshold": 250,
                "guild_subscriptions": false,
                "shard": [0, 1]
            }}
        }} """.format(sys.argv[1]))

        r = await websocket.recv()
        result = json.loads(r)
        print(result["t"] == "READY")
        print(result["d"]["session_id"]) # Need to cache this for resume
        '''while True:
            try:
                r = await websocket.recv()
                #print(r)    
            except websockets.ConnectionClosed:
                print('Terminated')
                break'''

        print(result)
        print(result["d"]["guilds"], "\n")
        r = await websocket.recv()
        print(json.loads(r), "\n")
        r = await websocket.recv()
        print(json.loads(r), "\n")
        r = await websocket.recv()
        print(json.loads(r), "\n")
        r = await websocket.recv()
        print(json.loads(r), "\n")
        
        #r = await websocket.recv()
        #print(json.loads(r))
        #r = await websocket.recv()
        #print(json.loads(r))

print("done")

assert len(sys.argv) > 1 # Supply the token to the bot as an argument to the script
asyncio.get_event_loop().run_until_complete(connectToGateway())



