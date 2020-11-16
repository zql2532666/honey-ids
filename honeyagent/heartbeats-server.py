"""
Author: Thein Than Zaw 
Date Started: 16/11/2020

Ref: https://www.oreilly.com/library/view/python-cookbook/0596001673/ch10s13.html

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
        def populate_honeynode_list():
            # Query the database for honey node info
            # GET REQUEST to endpoint on flask
            # populate the honeynode dictionary
       
2)  Update the honeynodes of the active status after a period of time or if there is a slient honey node 
        def update_slient_honeynodes_database():
            # update the database of slient honeynodes (no more heartbeats signals)
            # POST/PUT REQUEST to enpoint on flask
"""

HBPORT = 43278
CHECKWAIT = 30

from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM
from threading import Lock, Thread, Event
from time import time, ctime, sleep
import sys

class BeatDict:
    "Manage heartbeat dictionary"

    def __init__(self):
        self.beatDict = {}
        if __debug__:
            self.beatDict['127.0.0.1'] = time()
        self.dictLock = Lock()

    def __repr__(self):
        list = ''
        self.dictLock.acquire()
        for key in self.beatDict.keys():
            list = "%sIP address: %s - Last time: %s\n" % (
                list, key, ctime(self.beatDict[key]))
        self.dictLock.release()
        return list

    def update(self, entry):
        "Create or update a dictionary entry"
        self.dictLock.acquire()
        self.beatDict[entry] = time()
        self.dictLock.release()

    def extractSilent(self, howPast):
        "Returns a list of entries older than howPast"
        silent = []
        when = time() - howPast
        self.dictLock.acquire()
        for key in self.beatDict.keys():
            if self.beatDict[key] < when:
                silent.append(key)
        self.dictLock.release()
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
        while self.goOnEvent.isSet(  ):
            if __debug__:
                print ("Waiting to receive...")
            data, addr = self.recSocket.recvfrom(1024)
            print(data.decode('utf-8'))
            if __debug__:
                print (f"Received packet from {addr}") 
            self.updateDictFunc(addr[0])

def main(  ):
    "Listen to the heartbeats and detect inactive clients"
    global HBPORT, CHECKWAIT
    if len(sys.argv)>1:
        HBPORT=sys.argv[1]
    if len(sys.argv)>2:
        CHECKWAIT=sys.argv[2]

    beatRecGoOnEvent = Event()
    beatRecGoOnEvent.set()
    beatDictObject = BeatDict()
    beatRecThread = BeatRec(beatRecGoOnEvent, beatDictObject.update, HBPORT)
    if __debug__:
        print (beatRecThread)
    beatRecThread.start(  )
    print (f"PyHeartBeat server listening on port {HBPORT}") 
    print ("\n*** Press Ctrl-C to stop ***\n")
    while 1:
        try:
            if __debug__:
                print ("Beat Dictionary")
                print (f"{beatDictObject}")
            silent = beatDictObject.extractSilent(CHECKWAIT)
            if silent:
                print ("Silent clients")
                print (f"{silent}")
            sleep(CHECKWAIT)
        except KeyboardInterrupt:
            print ("Exiting.")
            beatRecGoOnEvent.clear()
            beatRecThread.join()
            sys.exit(0)

if __name__ == '__main__':
    main()