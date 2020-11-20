# from socket import socket, AF_INET, SOCK_DGRAM,SOCK_STREAM
import socket
import json
import time

handshake_data = {
    "token": TOKEN,
    "honeynode_name": HONEYNODE_NAME,
    "ip_addr": HONEYNODE_IP,
    "subnet_mask": HONEYNODE_SUBNET_MASK,
    "honeypot_type": HONEYNODE_HONEYPOT_TYPE,
    "nids_type": HONEYNODE_NIDS_TYPE,
    "deployed_date": HONEYNODE_DEPLOYED_DATE,
    "msg": "HANDSHAKE"
}

def send_command():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', 30000))
        data = {
            "command" : "handshake"
        }
        data_json = json.dumps(data)
        data_encoded = data_json.encode('utf-8')
        s.send(data_encoded)
            

send_command()