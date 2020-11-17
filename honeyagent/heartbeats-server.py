"""
Author: Thein Than Zaw 
Date Started: 16/11/2020

The client program, running on any number of computers, periodically sends 
an UDP packet to the server program that runs on one central computer. 

In the server program, one thread dynamically builds and updates 
a dictionary that stores the IP numbers of the client computers 
and the timestamp of the last packet received from each. 

At the same time, the main thread of the server program periodically 
checks the dictionary, noting whether any of the timestamps is older 
than a defined timeout. 

The packets are sent from each client every 10 seconds, while the server 
checks the dictionary every 30 seconds, and its timeout defaults to the 
same interval.

These parameters, along with the server IP number and port used, can be 
adapted to one’s needs. 
"""

""" PyHeartBeat server: receives and tracks UDP packets from all clients.

While the BeatLog thread logs each UDP packet in a dictionary, the main
thread periodically scans the dictionary and prints the IP addresses of the
clients that sent at least one packet during the run, but have
not sent any packet since a time longer than the definition of the timeout.

Adjust the constant parameters as needed, or call as:
    PyHBServer.py [timeout [udpport]]
"""

"""
1)  When the server is started, it will call the http endpoint on the flask server to 
    retrive the honeynodes details
        def populate_heartbeat_dict():
            # Query the database for honey node info
            # GET REQUEST to endpoint on flask
            # populate the honeynode dictionary

            route("/get_honey_node"):
                return all_honey_nodes
            
            request.get("flaskip/get_honey_node")
            honeynode_dict = reponse.data
       
2)  Update the honeynodes of the active status after a period of time or if there is a slient honey node 
        def update_slient_honeynodes_database():
            # update the status of slient honeynodes to database (no more heartbeats signals)
            # POST or PUT REQUEST to endpoint on flask --> this will then update the database 

            route ("/update_honeynode?token=??")
            # this is to update the honeynode status to the database
            request.post("flaskip/update_honeynode?token=xxx")


3) Update the database every 10 min or so 
        def update_database():

"""


"""
    You'll often want your threads to be able to use or modify variables common between 
    threads but to do that you'll have to use something known as a lock.
    
     Whenever a function wants to modify a variable, it locks that variable. 
     
     When another function wants to use a variable, it must wait until that variable is unlocked.
"""
HBPORT = 43279
DEAD_INTERVAL = 30

from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM, SOCK_STREAM
from threading import Lock, Thread, Event
from time import time, ctime, sleep
import sys
import json
class HeartBeatDict:
    "Manage heartbeat dictionary"

    def __init__(self):
        self.heartbeat_dict = {}
        if __debug__:
            """
                heartbeat_dict should be reconfigure to be in this format
                heartbeat_dict = {}
                heatbeat_dict["token"] = {
                    "honeynode_name": "",
                    "ip_addr": "100.10.10.1",
                    "subnet_mask": "255.255.255.0",
                    "honeypot_type": "",
                    "nids_type": "",
                    "deployed_date": "",
                }

                token will be used to identify unique honey nodes

                
            """
            self.heartbeat_dict['127.0.0.1'] = time()
        self.heartbeat_dict_lock = Lock()

    def __repr__(self):
        list = ''
        self.heartbeat_dict_lock.acquire()
        for key in self.heartbeat_dict.keys():
            list = "%sIP address: %s - Last time: %s\n" % (
                list, key, ctime(self.heartbeat_dict[key]))
        self.heartbeat_dict_lock.release()
        return list

    def update(self, entry):
        "Create or update a dictionary entry"
        self.heartbeat_dict_lock.acquire()
        self.heartbeat_dict[entry] = time()
        self.heartbeat_dict_lock.release()

    def extract_slient_nodes(self, howPast):
        "Returns a list of entries older than howPast"
        silent = []
        when = time() - howPast
        self.heartbeat_dict_lock.acquire()
        for key in self.heartbeat_dict.keys():
            if self.heartbeat_dict[key] < when:
                silent.append(key)
        self.heartbeat_dict_lock.release()
        return silent

class BeatRec(Thread):
    "Receive UDP packets, log them in heartbeat dictionary"

    def __init__(self, goOnEvent, updateDictFunc, port):
        Thread.__init__(self)
        self.goOnEvent = goOnEvent
        self.updateDictFunc = updateDictFunc
        self.port = port
        self.recSocket = socket(AF_INET, SOCK_DGRAM)
        self.recSocket.bind(('', port))

    def __repr__(self):
        return "Heartbeat Server on port: %d\n" % self.port

    def run(self):
        while self.goOnEvent.isSet():
            if __debug__:
                print ("Waiting to receive...")
            data, addr = self.recSocket.recvfrom(1024)
            data = data.decode('utf-8')
            # json.loads() deserialises the json object and return it to python dictionary
            data = json.loads(data)
            print(data['token'])
            # print(type(data.decode('utf-8')))
            if __debug__:
                print (f"Received packet from {addr}") 
            self.updateDictFunc(addr[0])

def main():
    "Listen to the heartbeats and detect inactive clients"
    global HBPORT, DEAD_INTERVAL
    # if len(sys.argv)>1:
    #     HBPORT=sys.argv[1]
    # if len(sys.argv)>2:
    #     DEAD_INTERVAL=sys.argv[2]

    beatRecGoOnEvent = Event()
    beatRecGoOnEvent.set()
    heartbeat_dict_object = HeartBeatDict()
    beatRecThread = BeatRec(beatRecGoOnEvent, heartbeat_dict_object.update, HBPORT)
    if __debug__:
        print (beatRecThread)
    beatRecThread.start()
    print (f"HeartBeats server listening on port {HBPORT}") 
    print ("\n*** Press Ctrl-C to stop ***\n")


    
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect(('127.0.0.1', 30002))
        data = {
            "command" : "kill"
        }
        data_json = json.dumps(data)
        data_encoded = data_json.encode('utf-8')
        s.sendall(data_encoded)

    while 1:
        try:
            if __debug__:
                print ("HeartBeat Dictionary")
                print (f"{heartbeat_dict_object}")
            silent = heartbeat_dict_object.extract_slient_nodes(DEAD_INTERVAL)
            if silent:
                print ("Silent Nodes")
                print (f"{silent}")
            sleep(DEAD_INTERVAL)
        except KeyboardInterrupt:
            print ("Exiting.")
            beatRecGoOnEvent.clear()
            beatRecThread.join()
            sys.exit(0)

if __name__ == '__main__':
    main()


"""
needs two processes 
1) heartbeats process
2) command process
"""