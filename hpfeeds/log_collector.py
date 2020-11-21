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
    "conpot.events",
    "elastichoney.events",
    "shockpot.events"
]

IDENT = 'collector'
SECRET = 'collector'



def main():
    hpc = hpfeeds.new(HOST, PORT, IDENT, SECRET)
    print("connected to " + hpc.brokername)


    def on_message(identifier, channel, payload):

        # Dump the log to a json file to collect the log format
        # THis is a testing feature, it will not be in the final version
        # with open("logdump.json") as f:
        #     log_data_dict = json.load(f)

        print(f"Identifier : {identifier}")
        print(f"Channel: {channel}")
        print("Payload:")
 
        payload_converted = json.loads(payload.decode())
        print(payload_converted)
        print("\n")

        # if identifier not in log_data_dict.keys():
        #    log_data_dict[identifier] = {"payloads":[payload_converted]}

        # data = {identifier: {"payloads":[payload_converted]}}
        # log_data_dict[identifier]["payloads"].append(payload_converted)

        # with open("logdump.json", 'w') as f:
        #     json.dump(log_data_dict, f, indent=4)

        # call api endpoint to store the log/alert in database and display on the webpage
        

    def on_error(payload):
        hpc.stop()


    hpc.subscribe(CHANNELS)
    hpc.run(on_message, on_error)
    print("error occured, aborting...")
    hpc.close()
    return 0


main()