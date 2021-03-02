based on code from u/shinevision

to start just put your nano address in the Data.json file and run the main file.

u/shinevision's README:

NanoPython

Python to NANO network API using websockets.
Usage

Put in a address you want to monitor in the nanoAddress field. The program will listen for RECEIVE payments. You can set it to listen to RECIEVE, SEND or even BOTH! Just change the logic after the websocket receive command after the while loop!
What do i need?

    Download the main.py file and the nodes.json file.
    Change address inside.
    Make sure you pip install the requirements.txt (or manually)
    ...
    Profit!

Requirements

    Python libs:
        asyncio
        ssl
        websockets
        json

For full info. Look at the requirements.txt!
Nodes?

In the nodes.json file you will find some websocket nodes. You can add as many as you would like. It will automatically assign a random node on start.
Can i donate?

Of course! just use the default NANO address! nano_3ij45i1uzaqwe8bdkbg4bfehdn4duzewao8m3z5grhda33hzzuzfo8a9zsws QR Code

You can also use this to test if everything works :)
Questions?

Feel free to ask for help!