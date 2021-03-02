import asyncio
import ssl
import websockets
import json
import random

ssl_context = ssl.create_default_context() #Create SSL default cert. (websocket is TLS)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

nanoAddress = "nano_3ij45i1uzaqwe8bdkbg4bfehdn4duzewao8m3z5grhda33hzzuzfo8a9zsws" #Address to track

nodes = [] #In the future i want the ability to switch node. In case of an offline node. Thats why this is global.

activeNode = "" #a node (websocket) will be randomly assigned to this string and used.

def raw_to_nano(raw): #This is NOT the correct way to do this (floating point error) but for now it will do for testing.
    return (int(raw) / 1000000000000000000000000000000)
def nano_to_raw(raw): #Read comment above:
    return (int(raw) * 1000000000000000000000000000000)

def load_nodes(): #Load nodes.json file with all nodes (websocket addresses)
    global nodes
    print("Loading list of nodes from file...")
    with open("nodes.json", "r") as file:
        nodes = json.load(file)
        print("Nodes loaded.")

def assign_random_node(): #Assign node randomly.
    global activeNode
    print("Assigning random node...")
    load_nodes()
    activeNode = nodes["nodes"][random.randint(0, len(nodes))]
    print(f"Node assigned! ({activeNode})")

async def main(): #Connect to websocket. Subscribe and listen for transactions.
    async with websockets.connect(activeNode, ssl=ssl_context) as websocket:
        print(f"Connected to websocket: {activeNode}\nSending subscription to websocket.")
        await websocket.send('{"action": "subscribe","topic": "confirmation","options":{"accounts": ["' + nanoAddress + '"]}}') #F strings don't work :(
        print(await websocket.recv())
        print("Subscribed!\nNow waiting for donations...\n\n")

        while 1: #Infinite listen loop. Listen for transactions
            rec = json.loads(await websocket.recv()) #Get JSON transaction payload

            #PUT YOUR LOGIC HERE!!!!

            if "receive" in rec["message"]["block"]["subtype"]: #If its a donation (if type is receive). Print. usefull for Twitch bot integration.
            
                confirmation = rec.get("topic", None) #Check if topic key exists. If not, make None.
                if confirmation: #check if None.
                    if confirmation == "confirmation": #Send NANO is legit and confirmed.
                        print(f"GOT DONATION FROM {rec['message']['account']}\nAmount RAW: {rec['message']['amount']}\nAmount NANO: {raw_to_nano(rec['message']['amount'])}")

try:
    assign_random_node() # Assign random socket node from file.
    asyncio.get_event_loop().run_until_complete(main()) #Run async websocket loop
except KeyboardInterrupt: #if you CTRL + C it quits.
    pass
except ConnectionRefusedError: #If websocket is offline it will error. Put fallback logic here. For example remove node form nodes list and re-assign new node.
    print("ERROR connecting to websocket. websocket offline?")
