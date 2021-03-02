import asyncio
import ssl
import websockets
import json
import random
from converter import Nanos

ssl_context = ssl.create_default_context()  # Create SSL default cert. (websocket is TLS)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class Interpreter:

    def __init__(self, message, myaccount):
        self.message = message
        self.myaccount = myaccount
        self.transferred_value = None
        self.strange_account = str
        self.subtype = str
        self.balance = None

        self.__on_message()

    def __onreceive(self):  # interprets the message if type = receive
        self.transferred_value = Nanos(raw=self.message['message']['amount'])
        self.strange_account = self.message['message']['account']
        self.balance = Nanos(raw=self.message['message']['block']['balance'])
        print(
            f"Received Nanos from {self.strange_account}\nAmount RAW: {self.transferred_value.raw}\nAmount NANO: {self.transferred_value.nano}\n")
        print(f"Your currently own {self.balance.nano} Nanos\n\n")

    def __onsend(self):  # Interprets the message if type = send
        self.strange_account = self.message['message']['block']['link_as_account']
        self.transferred_value = Nanos(raw=self.message['message']['amount'])
        self.balance = Nanos(raw=self.message['message']['block']['balance'])
        print(
            f"Sent Nanos to {self.strange_account}\nAmount RAW: {self.transferred_value.raw}\nAmount NANO: {self.transferred_value.nano}\n")
        print(f"Your currently own {self.balance.nano} Nanos\n\n")

    def __on_message(self):
        confirmation = self.message.get("topic", None)
        if confirmation == "confirmation":  # checks for confirmation from node
            self.subtype = self.message["message"]["block"]["subtype"]
        # checks for type of transaction
        if self.subtype == "send":
            # sometimes there is also a send message when your account receives nanos with your account as the linked one, like this it only lists transfers from strange accounts
            if self.message['message']['block']['link_as_account'] != self.myaccount:
                self.__onsend()
        elif self.subtype == "receive":
            self.__onreceive()


class Connector:
    def __init__(self, myaccount, sslcontext):
        self.myaccount = myaccount
        self.ssl_context = sslcontext
        self.nodes = self.__load_nodes()
        self.activeNode = self.__assign_random_node()  # Assign random socket node from file.

        asyncio.get_event_loop().run_until_complete(self.subscribe_and_listen())  # Run async websocket loop

    def __load_nodes(self):  # Load nodes.json file with all nodes (websocket addresses)
        print("Loading list of nodes from file...")
        with open("Data.json", "r") as file:
            nodes = json.load(file)
            print("Nodes loaded.")
            return nodes["nodes"]

    def __assign_random_node(self):  # Assign node randomly.
        print("Assigning random node...")
        activeNode = self.nodes[random.randint(0, len(self.nodes) - 1)]
        print(f"Node assigned! ({activeNode})")
        return activeNode

    async def subscribe_and_listen(self):  # Connect to websocket. Subscribe and listen for transactions.
        async with websockets.connect(self.activeNode, ssl=self.ssl_context) as websocket:
            print(f"Connected to websocket: {self.activeNode}\nSending subscription to websocket.")
            await websocket.send(
                '{"action": "subscribe","topic": "confirmation","options":{"accounts": ["' + self.myaccount + '"]}}')  # F strings don't work :(
            print(await websocket.recv())
            print(f"Subscribed!\nAccount: {self.myaccount}\nNow waiting for Transfer...\n\n")

            while 1:  # Infinite listen loop. Listen for transactions
                Interpreter(json.loads(await websocket.recv()),
                            self.myaccount)  # Get JSON transaction payload and loads everything into the Interpreter class


def main(nanoAddress, ssl_context):  # function is needed for recursion
    try:
        connection = Connector(nanoAddress, ssl_context)  # connection to node gets established
    except KeyboardInterrupt:  # if you CT
        pass
    except ConnectionRefusedError:  # If websocket is offline it will error. Put fallback logic here. For example remove node form nodes list and re-assign new node.
        with open("Data.json", "r") as file:  # opening the Nodes.json
            data = json.load(file)
        with open("Data_savefile" + str(random.randint(0, 1000)) + ".json",
                  "w") as savefile:  # There is probably a better way to do this than with randint() (eg incrementing numbers) , but I am lazy and it works for me like this
            json.dump(data,
                      savefile)  # making a savefile if what I did here doesnt work properly, this file should probably be stored seperately (manually) bc technically it could be overwritten by the next safefile
        i = 0
        for node in data["nodes"]:
            if node == connection.activeNode:  # checking if selected Node, that is offline is in list and deleting it from list
                data["nodes"].pop(i)
            i += 1
        with open("Data.json", "w") as newfile:  # overwriting Nodes.json with corrected list
            json.dump(data, newfile)

        print(f"ERROR connecting to websocket {connection.activeNode}. Websocket offline?")
        main(nanoAddress,
             ssl_context)  # theres probably also a better way to do this since you could technically end in recursion depth error, but you would need a lot of unavailable nodes in your Nodes.json for this to happen.


with open("Data.json", "r") as file:
    data = json.load(file)

main(data["nanoAddress"], ssl_context)
