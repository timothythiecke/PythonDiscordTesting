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
        # Open websocket to gateway and wait for the hello message from the server
        r = await websocket.recv()
        heartbeat_interval = 0
        if json.loads(r)["op"] == 10 : # Note: should probably do something if response is not opcode 10
            heartbeat_interval = json.loads(r)["d"]["heartbeat_interval"]
            print('Hello received', heartbeat_interval)
            return [heartbeat_interval, websocket]

        #asyncio.get_event_loop().run_until_complete(sendIdentity())

async def connectToGatewayTryCatch():
    websocket = websockets.connect(GATEWAY_URI)
    await websocket.ensure_open()

async def sendIdentity():
    async with websockets.connect(GATEWAY_URI) as websocket:
        # TODO: Need to take another look as to why the json methods did not work
        # Send identity
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
        print(result)
        #print(result["t"] == "READY")
        #print(result["d"]["session_id"]) # Need to cache this for resume
        
        
        '''while True:
            try:
                r = await websocket.recv()
                print(json.loads(r), "\n")    
            except websockets.ConnectionClosed:
                print('Terminated')
                break'''

        '''print(result)
        print(result["d"]["guilds"], "\n")
        r = await websocket.recv()
        print(json.loads(r), "\n") # Should be create
        r = await websocket.recv()
        print(json.loads(r), "\n")
        r = await websocket.recv()
        print(json.loads(r), "\n")
        r = await websocket.recv()
        print(json.loads(r), "\n")'''
        
        #r = await websocket.recv()
        #print(json.loads(r))
        #r = await websocket.recv()
        #print(json.loads(r))

async def consumer(message, queue):
    r = json.loads(message)
    print ('Received from gateway: ', r)
    opcode = r["op"]
    message_type = r["t"]
    if opcode == 0: # Dispatch
        print('dispatch from gateway')
        if message_type == 'MESSAGE_CREATE':
            print ('message created by ', r["d"]["author"]) # TODO: ignore own messages
        if message_type == 'READY':
            print ('bot is logged in')

    if opcode == 1: # Heartbeat
        print('heartbeat')
    if opcode == 9: # Invalid session, either resume or disconnect
        print ('invalid session')
    if opcode == 10 : # Hello
        heartbeat_interval = json.loads(message)["d"]["heartbeat_interval"]
        print('Hello received', heartbeat_interval)
            
            #return [heartbeat_interval, websocket]
            # asyncio.ensure_future?
            #print(message)
        await queue.put("HELLO")

async def producer(queue):
    message_type = await queue.get()
    print(message_type)
    if message_type == 'HELLO':
        return """ 
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
        }} """.format(sys.argv[1])
    else:
        return ''

async def consumer_handler(websocket, queue):
    print('consumer handler')
    '''async for message in websocket:
        await consumer(message)'''
    while True:
        await consumer(await websocket.recv(), queue)


async def producer_handler(websocket, queue):
    print('producer handler')
    while True:
        message = await producer(queue)
        print('Got message ', message)
        await websocket.send(message)
        print('Done sending')

async def handler(websocket, queue):
    print('handling')
    consumer_task = asyncio.ensure_future(consumer_handler(websocket, queue))
    producer_task = asyncio.ensure_future(producer_handler(websocket, queue))
    done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED,)
    for task in pending:
        task.cancel()

async def main():
    assert len(sys.argv) > 1 # Supply the token to the bot as an argument to the script
    #asyncio.get_event_loop().run_until_complete(connectToGateway())
    async with websockets.connect(GATEWAY_URI) as websocket:
        queue = asyncio.Queue()
        await handler(websocket, queue)
    
asyncio.run(main())