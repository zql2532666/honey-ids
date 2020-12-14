"""
Author: Thein Than Zaw 
Date Started: 16/11/2020

The client program, running on any number of computers, periodically sends 
an UDP packet to the server program that runs on one central computer. 

In the server program, one thread dynamically builds and updates 
a dictionary that stores the token number of the honeynodes  to the
timestamp of the last packet received from each and heartbeat_status.

"token" : {
    heartbeat_status: True,
    last_heard: time() --> need to format this 
}

At the same time, the main thread of the server program periodically 
checks the dictionary, noting whether any of the timestamps is older 
than a defined timeout. 

The packets are sent from each client per HELL_INTERVAL, while the server 
checks the dictionary as per DEAD_INTERVAL, and its timeout defaults to the 
same interval.

These parameters, along with the server IP number and port used, can be 
adapted to one’s needs. 

HeartBeat server: receives and tracks UDP packets from all clients.

While the heart_beat_log thread logs each UDP packet in a dictionary, the main
thread periodically scans the dictionary and prints the IP addresses of the
clients that sent at least one packet during the run, but have
not sent any packet since a time longer than the definition of the timeout.

Adjust the constant parameters as needed, or call as:
    PyHBServer.py [timeout [udpport]]
"""

"""

1)  When the server is started, it will call the http endpoint on the flask server to 
    retrive the honeynodes details
        populate_heartbeat_dict()
       
2)  The honeynode heartbeat_status is updated every DEAD_INTERVAL
        update_heartbeat_status()

3)  When a new node is added, the flask API endpoint open a socket connection on the HB_PORT and 
    send a msg, "POPULATE", this will cause the heartbeat server to run the populate_heartbeat_dict() function
    again.

populate_heartbeat_dict() populates the heartbeat_dict with all the active nodes
    1) at the start of the program
    2) when a new handshake process with the a honeynode is successful (new honeynode added or old honeynode becoming active again)
        (flask should open a socket connection with a command, and this command should prompt in
        running of this method)

        Flask: When the endpoint for adding a new node gets run
            1) checks whether the token exists in the database
                if exists:
                    update the heartbeats status 
                    send msg to heartbeats server to populate the heartbeats dict
                else:
                    add new honeynode 
                    send msg to heartbeats server to populate the heartbeats dict

"""


"""
    You'll often want your threads to be able to use or modify variables common between 
    threads but to do that you'll have to use something known as a lock.
    
     Whenever a function wants to modify a variable, it locks that variable. 
     
     When another function wants to use a variable, it must wait until that variable is unlocked.
"""

# from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM, SOCK_STREAM
import socket
from threading import Lock, Thread, Event
from time import time, ctime, sleep
import sys
import json
import requests
from configparser import ConfigParser

config = ConfigParser()
config.read('heartbeats_server.conf')

HBPORT = int(config['HEARTBEATS']['SERVER_HB_PORT']) 
HELLO_INTERVAL = int(config['HEARTBEATS']['HELLO_INTERVAL'])   
DEAD_INTERVAL = int(config['HEARTBEATS']['DEAD_INTERVAL'])   
WEB_SERVER_IP = config['WEB-SERVER']['SERVER_IP'] 
WEB_SERVER_PORT = config['WEB-SERVER']['PORT']

API_ENDPOINT = f"http://{WEB_SERVER_IP}:{WEB_SERVER_PORT}/api/v1/heartbeats"

class HeartBeatDict:
    "Manage heartbeat dictionary"

    def __init__(self):
        self.heartbeat_dict = {}
        # if __debug__:
        #     # self.heartbeat_dict['127.0.0.1'] = time()
        #     self.heartbeat_dict[5] = time()
        self.heartbeat_dict_lock = Lock()

    # def __repr__(self):
    #     list = ''
    #     self.heartbeat_dict_lock.acquire()
    #     for key in self.heartbeat_dict.keys():
    #         list = "%sIP address: %s - Last time: %s\n" % (
    #             list, key, ctime(self.heartbeat_dict[key]))
    #     self.heartbeat_dict_lock.release()
    #     return list

    # this updates the last_heard_time for each indiv nodes
    def update_last_heard(self, entry):
        "Create or update a dictionary entry"
        print("update_last_heard")
        self.heartbeat_dict_lock.acquire()
        # print(f"entry --> {entry}")
        # print(self.heartbeat_dict.keys())
        for key in self.heartbeat_dict.keys():
            if entry == key:
                # print(f"time update success for token == {entry}")
                # print(self.heartbeat_dict[key])
                self.heartbeat_dict[entry]['last_heard'] = time()
        self.heartbeat_dict_lock.release()

    # this updates the heartbeat_status of all the nodes in the heartbeat_dict after the dead interval
    def update_heartbeat_status(self, dead_nodes_list):
        self.heartbeat_dict_lock.acquire()
        for key in self.heartbeat_dict.keys():
            # if the node's token can be found in the slient_node_list, the status will be set to False (Dead)
            if key in dead_nodes_list:
                # print(f"dead node found: {key}")
                self.heartbeat_dict[key]['heartbeat_status'] = False
            else:
            # All other nodes, not found in the dead_node_list is set to True (Active)
                # print(f"active node {self.heartbeat_dict[key]}")
                self.heartbeat_dict[key]['heartbeat_status'] = True
        print(f"\n\nupdate_heartbeat_status\n {self.heartbeat_dict}")
        heartbeat_json = json.dumps(self.heartbeat_dict)
        self.heartbeat_dict_lock.release()

        """ perform api call to flask here """
        try:
            headers = {'content-type': 'application/json'}
            requests.post(API_ENDPOINT, data=heartbeat_json, headers=headers)
        except Exception as err:
            print(err)


    def extract_dead_nodes(self, time_limit):
        "Returns a list of entries older than time_limit"
        dead = []
        when = time() - time_limit
        self.heartbeat_dict_lock.acquire()
        for key in self.heartbeat_dict.keys():
            if self.heartbeat_dict[key]['last_heard'] < when:
                dead.append(key)
        self.heartbeat_dict_lock.release()
        return dead
    
    # Need to find a way to call this again when a new node is added
    def populate_heartbeat_dict(self):
        self.heartbeat_dict_lock.acquire()
        print("populating heartbeat dict")
        """ Perform API Call here """
        try:
            r = requests.get(API_ENDPOINT)
            print(f"populate data successful --> {r.status_code}")
            if r.json():
                self.heartbeat_dict = r.json()
            print(f"populated heartbeat dict {self.heartbeat_dict}")
        except Exception as err:
            print(err)

        # self.heartbeat_dict = {
        #     "a1": {
        #             'heartbeat_status' : True, 
        #             'last_heard' : time()
        #         },
        #     "b2": {
        #             'heartbeat_status' : False, 
        #             'last_heard' : time()
        #         }
        # }
        self.heartbeat_dict_lock.release()
        # sleep(10)

class HeartBeatReceiver(Thread):
    "Receive UDP packets, log them in heartbeat dictionary"

    def __init__(self, go_on_event, update_dict_func, port, populate_dict_func):
        Thread.__init__(self)
        self.go_on_event = go_on_event
        self.update_dict_func = update_dict_func
        self.port = port
        self.populate_dict_func = populate_dict_func
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receive_socket.bind(('', port))

    def __repr__(self):
        return "Heartbeat Server on port: %d\n" % self.port

    def run(self):
        while self.go_on_event.isSet():
            # if __debug__:
            #     print ("Waiting to receive...")
            data, addr = self.receive_socket.recvfrom(1024)
            data = data.decode('utf-8')
            data = json.loads(data)
            # if __debug__:
            #     print (f"Received packet from {addr}") 
            print (f"Received packet from {addr}") 
            # updates the heartbeat dictionary, addr[0] contains the ip address of the sender
            # self.update_dict_func(addr[0])
            try:
                if data['msg'] == "HEARTBEAT":
                    self.update_dict_func(data['token'])
                elif data['msg'] == "POPULATE":
                    # POPULATE Might give us some issues, since it might reset the heartbeat status of 
                    # the nodes to False
                    self.populate_dict_func()
                    
            except KeyError:
                print("data received is in wrong format")

def main():
    "Listen to the heartbeats and detect inactive clients"
    global HBPORT, DEAD_INTERVAL
    if len(sys.argv)>1:
        HBPORT=sys.argv[1]
    if len(sys.argv)>2:
        DEAD_INTERVAL=sys.argv[2]

    print (f"HeartBeats server listening on port {HBPORT}") 
    print ("\n*** Press Ctrl-C to stop ***\n")
    # Event() --> The internal flag is initially false
    heat_beat_rec_go_on_event = Event()

    # Set the internal flag to true. All threads waiting for it to become true are awakened. Threads that call wait() once the flag is true will not block at all. 
    heat_beat_rec_go_on_event.set()
    heartbeat_dict_object = HeartBeatDict()
    heartbeat_dict_object.populate_heartbeat_dict()
    # print(f"Initial heart_beat_dict --> {heartbeat_dict_object.heartbeat_dict}")
    heat_beat_rec_thread = HeartBeatReceiver(heat_beat_rec_go_on_event, heartbeat_dict_object.update_last_heard, HBPORT, heartbeat_dict_object.populate_heartbeat_dict)
    # if __debug__:
    #     print (heat_beat_rec_thread)
    heat_beat_rec_thread.start()
    sleep(15)
    while 1:
        try:
            # if __debug__:
            #     print ("HeartBeat Dictionary")
            #     print (f"{heartbeat_dict_object}")
            dead = heartbeat_dict_object.extract_dead_nodes(DEAD_INTERVAL)
            if dead:
                print("Dead Nodes")
                print(f"{dead}")
                
            # update the heartbeat_dict here
            heartbeat_dict_object.update_heartbeat_status(dead)
            sleep(DEAD_INTERVAL)
        except KeyboardInterrupt:
            print ("Exiting.")

            # Reset the internal flag to false. Subsequently, threads calling wait() will block until set() is called to set the internal flag to true again. 
            heat_beat_rec_go_on_event.clear()
            heat_beat_rec_thread.join()
            sys.exit(0)

if __name__ == '__main__':
    main()




