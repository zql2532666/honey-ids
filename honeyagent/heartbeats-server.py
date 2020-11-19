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
1)  wWhen the server is started, it will call the http endpoint on the flask server to 
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
HBPORT = 40000
DEAD_INTERVAL = 30

# from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM, SOCK_STREAM
import socket
from threading import Lock, Thread, Event
from time import time, ctime, sleep
import sys
import json
import requests
class HeartBeatDict:
    "Manage heartbeat dictionaryda f"

    def __init__(self):
        self.heartbeat_dict = {}
        # if __debug__:
        #     # self.heartbeat_dict['127.0.0.1'] = time()
        #     self.heartbeat_dict[5] = time()
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
        print(f"updated : {self.heartbeat_dict}")
        self.heartbeat_dict_lock.release()

    def extract_slient_nodes(self, time_limit):
        "Returns a list of entries older than time_limit"
        silent = []
        print(f"time --> {time()}")
        when = time() - time_limit
        print(f"time_limit --> {time_limit}")
        print(f"when --> {when}")
        self.heartbeat_dict_lock.acquire()
        for key in self.heartbeat_dict.keys():
            if self.heartbeat_dict[key] < when:
                print(f"{key} : {self.heartbeat_dict[key]}")
                silent.append(key)
        self.heartbeat_dict_lock.release()
        return silent
    
    def populate_heartbeat_dict(self):
        # print("populating hearbeat dict")
        # API_ENDPOINT = ""
        # r = requests.get(API_ENDPOINT)
        # if r.status_code == 200:
        #     print("API call successful")
        #     data = r.json()
        #     data = json.loads(data)
        #     self.heartbeat_dict_lock.acquire()
        #     self.heartbeat_dict = data
        #     self.heartbeat_dict_lock.release()
        self.heartbeat_dict_lock.acquire()
        self.heartbeat_dict['test'] = time()
        self.heartbeat_dict_lock.release()

class HeartBeatReceiver(Thread):
    "Receive UDP packets, log them in heartbeat dictionary"

    def __init__(self, go_on_event, update_dict_func, port):
        Thread.__init__(self)
        self.go_on_event = go_on_event
        self.update_dict_func = update_dict_func
        self.port = port
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receive_socket.bind(('', port))

    def __repr__(self):
        return "Heartbeat Server on port: %d\n" % self.port

    def run(self):
        while self.go_on_event.isSet():
            if __debug__:
                print ("Waiting to receive...")
            data, addr = self.receive_socket.recvfrom(1024)
            data = data.decode('utf-8')
            # json.loads() deserialises the json object and return it to python dictionary
            data = json.loads(data)
            print(data['token'])
            # print(type(data.decode('utf-8')))
            if __debug__:
                print (f"Received packet from {addr}") 
            # updates the heartbeat dictionary, addr[0] contains the ip address of the sender
            # self.update_dict_func(addr[0])
            self.update_dict_func(int(data['token']))


"""
populate_heartbeat_dict() populates the heartbeat_dict with all the active nodes
    1) at the start of the program
    2) when a new handshake process with the a honeynode is successful (new honeynode added or old honeynode becoming active again)
        (flask should open a socket connection with a command, and this command should prompt in
        running of this method)
"""

    # 
    # call the http endpoint on Flask to populate

    # this method should be called 


"""
update_honeynode_status() will update to the flask endpoint when a honeynode has gone slient 
    Task 1: call the flask endpoint to update the database of the honeynode status --> becomes inactive

    Question: what should i do when a honeynode becomes active again for some reason? How can I update this new status
        2 scenrios:
            1)  A new handshake
                    client clicks on handshake button--> flask 
                    flask -- sockets --> honeynode 
                    honeynode -- api --> flask 
                        flask updates database (client becomes active again)
                    flask -- sockets --> c2 
                        c2 runs populate_heartbeat_dict (the old honeynode will now be now be inside the heartbeat_dict)
            2)  All of a sudden starts getting heartbeats

                thought --> update slient nodes + active nodes to the database? this way we can account for different nodes going silent
                each time . this is impossbile to do when you only want to access the data base if len(silent) == 0 
"""
def update_honeynode_status():
    print("update_honeynode_status")


def main():
    "Listen to the heartbeats and detect inactive clients"
    global HBPORT, DEAD_INTERVAL
    # if len(sys.argv)>1:
    #     HBPORT=sys.argv[1]
    # if len(sys.argv)>2:
    #     DEAD_INTERVAL=sys.argv[2]

    """
        Event Objects are used for communication between threads: 
            one thread signals an event and one or more other threads are waiting for it 

            An event object manages an internal flag that can be 
                i.  set to true with the set() method and 
                ii. reset to false with the clear() method.

            The wait() method blocks until the flag is true.


    """
    # Event() --> The internal flag is initially false
    heat_beat_rec_go_on_event = Event()

    # Set the internal flag to true. All threads waiting for it to become true are awakened. Threads that call wait() once the flag is true will not block at all. 
    heat_beat_rec_go_on_event.set()
    heartbeat_dict_object = HeartBeatDict()
    heartbeat_dict_object.populate_heartbeat_dict()
    heat_beat_rec_thread = HeartBeatReceiver(heat_beat_rec_go_on_event, heartbeat_dict_object.update, HBPORT)
    if __debug__:
        print (heat_beat_rec_thread)
    heat_beat_rec_thread.start()
    print (f"HeartBeats server listening on port {HBPORT}") 
    print ("\n*** Press Ctrl-C to stop ***\n")

    while 1:
        try:
            if __debug__:
                print ("HeartBeat Dictionary")
                print (f"{heartbeat_dict_object}")
            silent = heartbeat_dict_object.extract_slient_nodes(DEAD_INTERVAL)
            if silent:
                print ("Silent Nodes")
                print (f"{silent}")
                # Update the database of honeynode status 
            sleep(DEAD_INTERVAL)
        except KeyboardInterrupt:
            print ("Exiting.")

            # Reset the internal flag to false. Subsequently, threads calling wait() will block until set() is called to set the internal flag to true again. 
            heat_beat_rec_go_on_event.clear()
            heat_beat_rec_thread.join()
            sys.exit(0)

if __name__ == '__main__':
    main()


"""
needs two processes 
1) heartbeats process
2) command process
"""