""" PyHeartBeat client: sends an UDP packet to a given server every 10 seconds.

Adjust the constant parameters as needed, or call as:
    PyHBClient.py serverip [udpport]
"""

from socket import socket, AF_INET, SOCK_DGRAM
from time import time, ctime, sleep
import sys
import multiprocessing
import threading

"""
heartbeat_data = {
    token: "xdfsdafsd",
    honeynode_name: "",
    ip_addr: "100.10.10.1",
    subnet_mask: "255.255.255.0",
    honeypot_type: "",
    nids_type: "",
    deployed_date: "",
    msg: "HEART-BEAT"
}

"""

SERVERIP = '127.0.0.1'    # local host, just for testing
HBPORT = 43278            # an arbitrary UDP port
BEATWAIT = 10             # number of seconds between heartbeats

if len(sys.argv)>1:
    SERVERIP=sys.argv[1]
if len(sys.argv)>2:
    HBPORT=sys.argv[2]

hbsocket = socket(AF_INET, SOCK_DGRAM)
print (f"PyHeartBeat client sending to IP {SERVERIP} , {HBPORT} %d")
print ("\n*** Press Ctrl-C to terminate ***\n")
def send_heartbeats():
    while 1:
        hbsocket.sendto('FUCK FYP'.encode('utf-8'), (SERVERIP, HBPORT))
        print('FUCK FYP'.encode('utf-8'))
        if __debug__:
            print (f"Time: {ctime(time(  ))}")
        sleep(BEATWAIT)

process_list=list()
if __name__ == '__main__':   
    for _ in range(10):
        p = multiprocessing.Process(target=send_heartbeats)
        p.start()
        process_list.append(p)

    for p in process_list:
        p.join()

print("test")