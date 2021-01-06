import hpfeeds
import sys
import json
import requests
from datetime import datetime


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
    "dionaea.connections"
]

IDENT = 'collector'
SECRET = 'collector'


def parse_cowrie_logs(identifier, payload):
    general_log_data_dict = dict()

    general_log_data_dict['capture_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    general_log_data_dict['honeynode_name'] = ""
    general_log_data_dict['source_ip'] = payload["peerIP"]
    general_log_data_dict['source_port'] = payload["peerPort"]
    general_log_data_dict['destination_ip'] = payload["hostIP"]
    general_log_data_dict['destination_port'] = payload["hostPort"]
    general_log_data_dict['protocol'] = "TCP"
    general_log_data_dict['token'] = identifier
    general_log_data_dict['raw_log'] = json.dumps(payload)

    return general_log_data_dict


def parse_elastichoney_logs(identifier, payload):
    general_log_data_dict = dict()

    general_log_data_dict['capture_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    general_log_data_dict['honeynode_name'] = ""
    general_log_data_dict['source_ip'] = payload["source"]
    general_log_data_dict['source_port'] = 0
    general_log_data_dict['destination_ip'] = payload["honeypot"]
    general_log_data_dict['destination_port'] = payload["headers"]['host'].split(':')[1]
    general_log_data_dict['protocol'] = "TCP"
    general_log_data_dict['token'] = identifier
    general_log_data_dict['raw_log'] = json.dumps(payload)

    return general_log_data_dict


def parse_wordpot_logs(identifier, payload):
    general_log_data_dict = dict()

    general_log_data_dict['capture_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    general_log_data_dict['honeynode_name'] = ""
    general_log_data_dict['source_ip'] = payload["source_ip"]
    general_log_data_dict['source_port'] = payload["source_port"]
    general_log_data_dict['destination_ip'] = payload["dest_ip"]
    general_log_data_dict['destination_port'] = payload["dest_port"]
    general_log_data_dict['protocol'] = "TCP"
    general_log_data_dict['token'] = identifier
    general_log_data_dict['raw_log'] = json.dumps(payload)

    return general_log_data_dict


def parse_drupot_logs(identifier, payload):
    general_log_data_dict = dict()

    general_log_data_dict['capture_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    general_log_data_dict['honeynode_name'] = ""
    general_log_data_dict['source_ip'] = payload["src_ip"]
    general_log_data_dict['source_port'] = payload["src_port"]
    general_log_data_dict['destination_ip'] = payload["dest_ip"]
    general_log_data_dict['destination_port'] = payload["dest_port"]
    general_log_data_dict['protocol'] = "TCP"
    general_log_data_dict['token'] = identifier
    general_log_data_dict['raw_log'] = json.dumps(payload)

    return general_log_data_dict


def parse_shockpot_logs(identifier, payload):
    general_log_data_dict = dict()

    general_log_data_dict['capture_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    general_log_data_dict['honeynode_name'] = ""
    general_log_data_dict['source_ip'] = payload["source_ip"]
    general_log_data_dict['source_port'] = 0
    general_log_data_dict['destination_ip'] = payload["dest_host"]
    general_log_data_dict['destination_port'] = payload["dest_port"]
    general_log_data_dict['protocol'] = "TCP"
    general_log_data_dict['token'] = identifier
    general_log_data_dict['raw_log'] = json.dumps(payload)

    return general_log_data_dict


def parse_sticky_elephant_logs(identifier, payload):
    general_log_data_dict = dict()

    general_log_data_dict['capture_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    general_log_data_dict['honeynode_name'] = ""
    general_log_data_dict['source_ip'] = payload["source_ip"]
    general_log_data_dict['source_port'] = payload["source_port"]
    general_log_data_dict['destination_ip'] = payload["dest_ip"]
    general_log_data_dict['destination_port'] = payload["dest_port"]
    general_log_data_dict['protocol'] = "TCP"
    general_log_data_dict['token'] = identifier
    general_log_data_dict['raw_log'] = json.dumps(payload)

    return general_log_data_dict


def parse_snort_nids_logs(identifier, payload):
    nids_log_dict = dict()

    nids_log_dict['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    nids_log_dict['honeynode_name'] = ""
    nids_log_dict['source_ip'] = payload['source_ip']
    nids_log_dict['source_port'] = payload['source_port']
    nids_log_dict['destination_ip'] = payload['destination_ip']
    nids_log_dict['destination_port'] = payload['destination_port']
    nids_log_dict['priority'] = payload['priority']
    nids_log_dict['classification'] = payload['classification']
    nids_log_dict['signature'] = payload['signature']

    return nids_log_dict
    

def parse_dionaea_connection_logs(identifier, payload):
    general_log_data_dict = dict()

    general_log_data_dict['capture_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    general_log_data_dict['honeynode_name'] = ""
    general_log_data_dict['source_ip'] = payload["remote_host"]
    general_log_data_dict['source_port'] = payload["remote_port"]
    general_log_data_dict['destination_ip'] = payload["local_host"]
    general_log_data_dict['destination_port'] = payload["local_port"]
    general_log_data_dict['protocol'] = "TCP"
    general_log_data_dict['token'] = identifier
    general_log_data_dict['raw_log'] = json.dumps(payload)

    return general_log_data_dict


def create_general_log_entry(identifier, channel, payload):
    general_log_entry = dict()

    if channel == "cowrie.sessions":
        general_log_entry = parse_cowrie_logs(identifier, payload)
    elif channel == "agave.events":
        general_log_entry = parse_drupot_logs(identifier, payload)
    elif channel == "wordpot.events":
        general_log_entry = parse_wordpot_logs(identifier, payload)
    elif channel == "elastichoney.events":
        general_log_entry = parse_elastichoney_logs(identifier, payload)
    elif channel == "shockpot.events":
        general_log_entry = parse_shockpot_logs(identifier, payload)
    elif channel == "sticky_elephant.connections" or channel == "sticky_elephant.queries":
        general_log_entry = parse_sticky_elephant_logs(identifier, payload)
    elif channel == "dionaea.connections":
        general_log_entry = parse_dionaea_connection_logs(identifier, payload)

    return general_log_entry


def insert_general_logs_to_database(general_log_entry):
    pass







def main():
    hpc = hpfeeds.new(HOST, PORT, IDENT, SECRET)
    print("connected to " + hpc.brokername)


    def on_message(identifier, channel, payload):

        print(f"Identifier : {identifier}")
        print(f"Channel: {channel}")
        print("Payload:")
 
        payload_converted = json.loads(payload.decode())
        print(type(payload_converted))
        general_log_entry = create_general_log_entry(identifier, channel, payload_converted)
        print(general_log_entry)
        print("\n")

        # call api endpoint to store the log/alert in database and display on the webpage
        

    def on_error(payload):
        hpc.stop()


    hpc.subscribe(CHANNELS)
    hpc.run(on_message, on_error)
    print("error occured, aborting...")
    hpc.close()
    return 0


if __name__ == "__main__":
    main()
