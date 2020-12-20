import hpfeeds
import sys
import json
import requests


# run broker :
# If the aionotify package is installed and the host os is Linux then the broker will automatically reload the JSON file whenever it changes.
# pip3 install aionotify
# hpfeeds-broker -e tcp:port=10000 --auth=auth.json --name=mybroker

HOST = 'localhost'
PORT = 10000

CHANNELS = [
    "cowrie.sessions",
    "snort.alerts",
    "agave.events",     # for drupot
    "wordpot.events",
    "elastichoney.events",
    "shockpot.events",
    "sticky_elephant.connections", 
    "sticky_elephant.queries",
    "dionaea.connections", 
    "dionaea.capture",
    "mwbinary.dionaea.sensorunique", 
    "dionaea.capture.anon", 
    "dionaea.caputres"
]

IDENT = 'collector'
SECRET = 'collector'



def main():
    hpc = hpfeeds.new(HOST, PORT, IDENT, SECRET)
    print("connected to " + hpc.brokername)


    def on_message(identifier, channel, payload):

        print(f"Identifier : {identifier}")
        print(f"Channel: {channel}")
        print("Payload:")
 
        payload_converted = json.loads(payload.decode())
        print(payload_converted)
        print("\n")

        # call api endpoint to store the log/alert in database and display on the webpage
        

    def on_error(payload):
        hpc.stop()


    hpc.subscribe(CHANNELS)
    hpc.run(on_message, on_error)
    print("error occured, aborting...")
    hpc.close()
    return 0


main()