""" PyHeartBeat client: sends an UDP packet to a given server every 10 seconds.

Adjust the constant parameters as needed, or call as:
    PyHBClient.py serverip [udpport]
"""

from socket import socket, AF_INET, SOCK_DGRAM
from time import time, ctime, sleep
import sys
import multiprocessing
import threading
import json
from configparser import ConfigParser

"""
heart beat signals will sent to the server (SERVIERIP) per time specified 
by HELLO_INTERVAL
"""
config = ConfigParser()
# check if it's possible to generate the conf bia bash script 

config.read('config.conf')

SERVER_IP = config['C2-SERVER']['SERVER_IP']                    # local host, just for testing
SERVER_HB_PORT = int(config['HEARTBEATS']['SERVER_HB_PORT'])            # an arbitrary UDP port
HELLO_INTERVAL = int(config['HEARTBEATS']['HELLO_INTERVAL'])               # number of seconds between heartbeats

# HONEYNODE INFO
TOKEN = config['HONEYNODE']['TOKEN']

# SERVER_IP = '127.0.0.1'    # local host, just for testing
# SERVER_HB_PORT = 43278            # an arbitrary UDP port
# HELLO_INTERVAL = 10             # number of seconds between heartbeats

heartbeat_data = {
    "token": TOKEN,
    "honeynode_name": "",
    "ip_addr": "100.10.10.1",
    "subnet_mask": "255.255.255.0",
    "honeypot_type": "",
    "nids_type": "",
    "deployed_date": "",
    "msg": "HEARTBEATS! HELLO!"
}

heartbeat_data_json = json.dumps(heartbeat_data)


if len(sys.argv)>1:
    SERVER_IP=sys.argv[1]
if len(sys.argv)>2:
    SERVER_HB_PORT=sys.argv[2]

hbsocket = socket(AF_INET, SOCK_DGRAM)
print (f"PyHeartBeat client sending to IP {SERVER_IP} , {SERVER_HB_PORT}")
print ("\n*** Press Ctrl-C to terminate ***\n")
def send_heartbeats():
    while 1:
        # hbsocket.sendto('FUCK FYP'.encode('utf-8'), (SERVER_IP, SERVER_HB_PORT))
        hbsocket.sendto(heartbeat_data_json.encode('utf-8'), (SERVER_IP, SERVER_HB_PORT))
        if __debug__:
            print (f"Time: {ctime(time(  ))}")
        sleep(HELLO_INTERVAL)

process_list=list()
if __name__ == '__main__':   
    for _ in range(2):
        p = multiprocessing.Process(target=send_heartbeats)
        p.start()
        process_list.append(p)

    for p in process_list:
        p.join()

