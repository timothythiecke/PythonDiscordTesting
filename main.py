import requests
import asyncio
import websockets
import json

#print('hello world')

#URL = "http://maps.googleapis.com/maps/api/geocode/json"
#location = "delhi technological universtiy"
#PARAMS = { 'address': location }

#URL = "http://youtube.com"
#URL = "https://timbo.free.beeceptor.com/"
#PARAMS = {}
#print(PARAMS)
#r = requests.get(URL, PARAMS)
#print(r)

#print (r.json())
#data = r.json()
#print(data)

DISCORD_BASE_URL = "https://discordapp.com/api"
#AUTH_URL = "https://discordapp.com/api/oauth2/authorize?client_id=157730590492196864&scope=bot&permissions=1"

# Gebruik deze link in je webbrowser om je bot toe te voegen
#
# https://discordapp.com/api/oauth2/authorize?client_id=624939999649071104&scope=bot&permissions=72704 #permissions moet je ergens berekenen

#heartbeat_interval = "global"

async def connectToGateway():
    URI = "wss://gateway.discord.gg/?v=6&encoding=json"
    async with websockets.connect(URI) as websocket:
        r = await websocket.recv()
        if json.loads(r)["op"] == 10 :
            return json.loads(r)["d"]["heartbeat_interval"]
            #print (heartbeat_interval)
        #else:
        #    throw

async def sendHeartBeatToGateway():
    async with websockets.connect(URI) as websocket:

heartbeat_interval = asyncio.get_event_loop().run_until_complete(connectToGateway())

asyncio.get_event_loop().run_forever


print (heartbeat_interval)
print("done")
