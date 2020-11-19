# from socket import socket, AF_INET, SOCK_DGRAM,SOCK_STREAM
import socket
import json
import time
def send_command():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', 30000))
        data = {
            "command" : "handshakee"
        }
        data_json = json.dumps(data)
        data_encoded = data_json.encode('utf-8')
        s.send(data_encoded)
            

send_command()