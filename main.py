import sys
import re
import requests
import asyncio
import websockets
import json
import random
import logging



DISCORD_BASE_URL = "https://discordapp.com/api"
GATEWAY_URI = "wss://gateway.discord.gg/?v=6&encoding=json"



quotes = [
    'THE DOTHRAKI ON AN OPEN FIELD NED',
    'LETS GO KILL SOME BOAR',
    'ONE BALL AND NO BRAINS',
    'YOUR MOTHER WAS A DUMB WHORE WITH A FAT ARSE',
    'MOAR WINE',
    'THE WHORE IS PREGNANT',
    'START THE DAMN JOUST BEFORE I PISS MYSELF',
    'GODS I WAS STRONG THEN',
    'YOU HEARD THE HAND, THE KING\'S TOO FAT FOR HIS ARMOR! GO FIND THE BREASTPLATE STRETCHER! NOW!',
    'BESSIE. THANKS THE GODS FOR BESSIE... AND HER TITS',
    'BOW YA SHITS, BOW BEFORE YOUR KING',
    'YOU GOT FAT',
    'WHO NAMED YOU? SOME HALFWIT WITH A STUTTER??',
    'YOU LET THAT LITTLE GIRL DISARM YOU?',
    'ALL I WANTED TO DO WAS CRACK SKULLS AND FUCK GIRLS!',
    'YOU\'RE MY COUNCIL, COUNSEL! SPEAK SENSE TO THIS HONORABLE FOOL!',
    'SOON ENOUGH, THAT CHILD WILL SPREAD HER LEGS AND START BREEDING!',
    'DID YOU EVER MAKE THE EIGHT BARRY?',
    'I\'M NOT TRYING TO HONOR YOU, I\'M TRYING TO GET YOU TO RUN MY KINGDOM WHILE I EAT, DRINK AND WHORE MY WAY TO AN EARLY GRAVE!',
    'TAKE SHIP FOR THE FREE CITIES WITH MY HORSE AND MY HAMMER, SPEND MY TIME WARRING AND WHORING, THAT’S WHAT I WAS MADE FOR!',
    'SHE SHOULD BE ON A HILL SOMEWHERE WITH THE SUN AND THE CLOUDS ABOVE HER!',
    'DRINK AND STAY QUIET, THE KING IS TALKING!',
    'I WARNED YOU THIS WOULD HAPPEN! BACK IN THE NORTH, I WARNED YOU, BUT YOU DIDN\'T CARE TO HEAR! WELL, HEAR IT NOW!',
    'STOP THIS MADNESS, IN THE NAME OF YOUR KING!',
    'IS THAT WHAT EMPTY MEANS??',
    'IT\'S A GREAT CRIME TO LIE TO A KING!',
    'YOU EVER FUCK A RIVERLANDS GIRL?',
    'THERE\'S A WAR COMING, NED. I DON\'T KNOW WHEN, I DON\'T KNOW WHO WE\'LL BE FIGHTING...BUT IT\'S COMING!',
    'SURROUNDED BY LANNISTERS! EVERY TIME I CLOSE MY EYES I SEE THEIR BLONDE HAIR AND THEIR SMUG, SATISFIED FACES!',
    'SEVEN HELLS, NED, I WANT TO HIT SOMEONE!',
    'THEY NEVER TELL YOU HOW THEY ALL SHIT THEMSELVES! THEY DON\'T PUT THAT PART IN THE SONGS!',
    'THE SELLSWORD KING, HOW THE SINGERS WOULD LOVE ME!',
    'I ONLY KNOW SHE WAS THE ONE THING I EVER WANTED',
    'I WAS NEVER SO ALIVE AS WHEN I WAS WINNING THIS THRONE, OR SO DEAD AS NOW THAT I\'VE WON IT',
    'I\'M NOT TRYING TO HONOR YOU, I\'M TRYING TO GET YOU RUN MY KINGDOM WHILIE I EAT, DRINK, AND WHORE MY WAY TO AN EARLY GRAVE',
    'IT\'S A NEAT LITTLE TRICK YOU DO: YOU MOVE YOUR LIPS, AND YOUR FATHER\'S VOICE COMES OUT',
    'I WANT THE FUNERAL FEAST TO BE THE BIGGEST THE KINGDOM EVER SAW, AND I WANT EVERYONE TO TASTE THE BOAR THAT GOT ME',
    'I ASK YOU, NED, WHAT GOOD IS IT TO WEAR A CROWN',
    'THE GODS MOCK THE PRAYERS OF KINGS AND COWHERDS ALIKE',
    'BACKSTABBING DOESN\'T PREPARE YOU FOR A FIGHT, AND THAT\'S ALL THE REALM IS NOW',
    'A BIT OF WINE NOW AND AGAIN, A GIRL SQUEALING IN BED, THE FEEL OF A HORSE BETWEEN MY LEGS?',
    'I\'LL HAVE YER HEAD ON A SPIKE',
    'OUT. OUT! DAMN YOU, I\'M DONE WITH YOU',
    'GO! RUN BACK TO WINTERFELL!',
    'SO YOU DON\'T LIKE THE HAND\'S JOKE? IS THAT IT?',
    'WE WERE AT WAR! NONE OF US KNEW IF WE WERE GONNA GO BACK HOME AGAIN!',
    'IS THAT HOW YOU SPEAK TO YOUR KING?',
    'HE COULD HAVE LINGERED ON THE EDGE OF THE BATTLE WITH THE SMART BOYS, AND TODAY HIS WIFE WOULD BE MAKING HIM MISERABLE, HIS SONS WOULD BE INGRATES, AND HE WOULD BE WAKING THREE TIMES IN THE NIGHT TO PISS INTO A BOWL!',
    'YES, IT\'S BEEN A LONG TIME... BUT I STILL REMEMBER EVERY FACE!',
    'FORCED TO MIND THE DOOR WHILE YOUR KING EATS AND DRINKS AND SHITS AND FUCKS!',
    'STUPID BOY!',
    'TAKE ME TO YOUR CRYPT, I WANT TO PAY MY RESPECTS!',
    'GIVE ME SOMETHING FOR THE PAIN AND LET ME DIE!',
    'DID YOU HAVE TO BURY HER IN A PLACE LIKE THIS?',
    'CAREFUL, {0}! CAREFUL NOW!',
    ', GODS WHAT A STUPID NAME'
]



def doPostOfQuote(channelID, author):
    endpoint = """{0}/channels/{1}/messages""".format(DISCORD_BASE_URL, channelID)
    
    index = random.randint(0, len(quotes) - 1)
    message = '{0}{1}'
    if index == len(quotes) - 1:
        message = message.format(author, quotes[index])
    elif index == len(quotes) - 2:
        message = quotes[index].format(author)
    else:
        message = message.format('', quotes[index])
    # As required by the API
    content = {
        'content': message
    }
    # As required by the API
    headers = { 
        'Authorization': """Bot {0}""".format(sys.argv[1])
    }
    #print (endpoint, content, headers)
    r = requests.post(endpoint, data=content, headers=headers)
    #print(r.text)



async def consumer(message, queue, heartbeatqueue):
    """
    Consumes the message received from the websocket, then evaluates
    what is in it
    """
    r = json.loads(message)
    print ('Received from gateway: ', r)
    opcode = r["op"]
    message_type = r["t"]
    sequence_number = r["s"]
    if opcode == 0: # Dispatch message from gateway
        print('Dispatch received from gateway')
        if message_type == 'MESSAGE_CREATE':
            author = r["d"]["author"]["username"]
            print ('Message created by ', author) # TODO: ignore own messages, maybe not needed, as it just scans for bobby b in the content
            print ('Content: ', r["d"]["content"])

            channel_id = r["d"]["channel_id"]
            # Currently, the bot will scan any message for any variation of bobby b (case insensitive)
            if re.search("bobby b", r["d"]["content"], re.IGNORECASE):
                # Note: this should be moved out of the consumer code, but the message is received on the rest endpoint
                doPostOfQuote(channel_id, author)

            # Or if it gets mentioned
            mentions = r["d"]["mentions"]
            if mentions:
                for mention in mentions:
                    if mention["username"] == "BobbyBBot":
                        doPostOfQuote(channel_id, author)

        if message_type == 'READY':
            print ('Bot is logged in')
            # TODO: need to cache the sessionID somewhere, in order to be able to resume
            # Another asyncio.queue? :^)

        await heartbeatqueue.put(sequence_number)
    if opcode == 1: # Heartbeat
        print('Heartbeat')
    if opcode == 9: # Invalid session, either resume or disconnect
        print ('Invalid session!')
    if opcode == 10 : # Hello
        heartbeat_interval = r["d"]["heartbeat_interval"]
        print('Hello received with heartbeat interval', heartbeat_interval)

        await heartbeatqueue.put(heartbeat_interval)
        await queue.put("HELLO")
    if opcode == 11: # ACK
        print('ACK from server')



async def producer(queue):
    """
    Evaluates what is currently on the main queue and produces a
    message 
    """
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



async def consumer_handler(websocket, queue, heartbeatqueue):
    """
    Waits for a message from the websocket, then forwards this to the consumer
    """
    while True:
        await consumer(await websocket.recv(), queue, heartbeatqueue)



async def producer_handler(websocket, queue):
    """
    Waits for a message from the producer, then sends it through the websocket
    """
    while True:
        message = await producer(queue)
        print('Produced message: ', message)
        await websocket.send(message)
        print('Sent!')



async def heartbeat_handler(websocket, heartbeatqueue):
    """
    Sends a heartbeat payload to the gateway based on an interval received
    from the first message received from it. The first element added to the
    queue should be that interval, any subsequent elements are sequence numbers
    """  
    interval = await heartbeatqueue.get()
    print ('Received interval: ', interval)
    
    while True:
        await asyncio.sleep(interval / 1000)
        print('Done sleeping, sending heartbeat')
        last_sequence_number = await heartbeatqueue.get()
        await websocket.send(""" 
            {{
                "op": 1,
                "d": {0}
            }} """.format(last_sequence_number))
        print('Heartbeat sent!')



async def handler(websocket, queue, heartbeatqueue):
    """
    Starts the tasks to consume and produce messages to the Discord gateway, as well
    as a task for sending heartbeats on an interval based from the first message received
    from the gateway. This continues until the script is killed
    """
    consumer_task = asyncio.ensure_future(consumer_handler(websocket, queue, heartbeatqueue))
    producer_task = asyncio.ensure_future(producer_handler(websocket, queue))
    heartbeat_task = asyncio.ensure_future(heartbeat_handler(websocket, heartbeatqueue))
    done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED,)
    for task in pending:
        task.cancel()



async def main():
    assert len(sys.argv) > 1 # Supply the token to the bot as an argument to the script
    async with websockets.connect(GATEWAY_URI) as websocket:
        queue = asyncio.Queue() # Used to let the producer know what kind of message 
        heartbeatqueue = asyncio.LifoQueue() # Used for heartbeat messages, the first element that is added to this queue 
        await handler(websocket, queue, heartbeatqueue)



random.seed()
asyncio.run(main())