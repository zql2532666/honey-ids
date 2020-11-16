import subprocess
import thread
import socket
import json
import time
import os
import base64
from datetime import datetime , date , time , timedelta
from scapy .all import *
# color honey yellow is # a98307
port = 9830
transferPort = 9831
honeyHiveIP = ' 192.168.1.233 '
honeydIP = ' 192.168.1.154 '
honeypots = [" 192.168.1.150 ", " 192.168.1.151 ", " 192.168.1.152 "]
connections = {}
timeOutSeconds = 9000
sessionTimeout = timedelta ( seconds = timeOutSeconds )
autoTransferTimeout = timedelta ( seconds = timeOutSeconds )
connections_Lock = thread . allocate_lock ()
honeyd = None
devnull = open (os. devnull , 'wb ')
alertMode = False
def main ():
global honeyd
pcap_monitor_id = thread . start_new_thread ( pcapMonitor , ())
# heartbeat_id = thread . start_new_thread ( heartbeat , ())
# I want this in my main console output
# once run , it casues blocking
print (" Scapy Packet Sniffer Engaged ")
sniff ( iface =" eth0 ", prn= processPacket , store =0)
def pcapMonitor ():
while True :
connections_Lock . acquire ()
uct = datetime . utcnow ()
remove = []
for ip in connections :
if (uct - connections [ip ]. get (" time ") >=
autoTransferTimeout ):
transferFile (ip , connections [ip ]. get ('filename '))
remove . append (ip)
print " Automatic Transfer "
for i in remove :
connections . pop(i)
connections_Lock . release ()
floatSeconds = timeOutSeconds *1.0
time . sleep ( floatSeconds )
# method called when a packet is received
# parses the packet to identify the dest ip , port , ect.
# will implement scan recognition and attacker pivoting
def processPacket ( packet ):
# automatically named files based on ip , date , and time
now = datetime .now ()
uct = datetime . utcnow ()
# ignore traffic not to honeypots
if packet . haslayer (IP) and (not packet [IP ]. dst in honeypots ) and
(not packet [IP ]. src in honeypots ) and (not packet [IP ]. dst ==
honeydIP ) and (not packet [IP ]. src == honeydIP ):
None
# ignore 9830 and 9831 because they are packets we are sending
elif packet . haslayer (TCP ) and ( packet [TCP ]. dport == port or
packet [TCP ]. dport == transferPort or packet [TCP ]. sport == port or
packet [TCP ]. sport == transferPort ):
None
# ignores some Ubuntu traffic that is not being filtered out my /
etc / hosts
elif packet . haslayer (UDP ) and ( packet [UDP ]. sport == 68 or packet [
UDP ]. dport == 68 or packet [UDP ]. dport == 5353 or packet [UDP ].
dport == 53 or packet [UDP ]. sport == 53):
None
elif packet . haslayer (UDP ) and ( packet [UDP ]. dport == 9830) :
print " Command Received "
print now. strftime ("%Y -%m -% d_%H%M")
runCommand ( packet [UDP ]. load . strip ('\n'))
# ensures this packet has an IP
# log non 9830 and 9831 traffic from c2 server1
elif packet . haslayer (IP) and alertMode :
pckt_src = packet [IP ]. src
pckt_dst = packet [IP ]. dst
pckt_ttl = packet [IP ]. ttl
#
########################################################################
# if the honeypot doesnt already have an ongoing pcap log file
# and the time since last packet is less than 5 minutes
connections_Lock . acquire ()
if any (x in connections for x in[ pckt_dst , pckt_src ]):
ip = ""
filename = ""
# determine which ip was in the connections list
if pckt_dst in connections :
ip = pckt_dst
else :
ip = pckt_src
# time difference is less than than session timeout
# therefore , keep logging to file
# and update its timestamp to the new time
# new time - oldtime < allowed time
if(uct - connections [ip ]. get (" time ") < sessionTimeout ):
filename = connections [ip ]. get(" filename ")
connections [ip ]. update ({" time ": uct })
# else there was a timeout so need a new file
# there was a connection at one point so the ip
# is in our honeypot list , no need to check again
# update time of connection to now
else :
print " Transfering PCAP "
#if packet . haslayer (TCP):
# print " Packet : Source IP %s, Port %s\n Dest IP %s,
Port %s" % ( pckt_src , packet [TCP ]. sport , pckt_dst , packet [TCP ].
dport )
# else :
# print " Packet : Source IP %s\n Dest IP %s" % (
pckt_src , pckt_dst )
transferFile (ip , connections [ip ]. get ('filename '))
# create the new pcap file
filename = ip + "_" + now. strftime ("%Y -%m -% d_%H%M") +".
pcap "
# print "New filename : " + filename
# print connections [ip]
connections [ip ]. update ({" time ": uct })
connections [ip ]. update ({" filename ": filename })
# print connections [ip]
alert (packet , now)
# appends packet to output file
wrpcap ( filename , packet , append = True )
# ips not in connected list , but this may be first interaction
# with the honeypots . Want to assume first captured packet
will
# be sent to honeypot , but compromised hp could beacon out if
# hardware or software make it
elif any(x in honeypots for x in[ pckt_dst , pckt_src ]):
ip = ""
# determine which ip was in the connections list
if pckt_dst in honeypots :
ip = pckt_dst
else :
ip = pckt_src
# create the new pcap file
filename = ip + "_" + now. strftime ("%Y -%m -% d_%H%M") +". pcap
"
# print " filename : " + filename
connections [ip] = {" filename ": filename , " time ": uct}
alert (packet , now)
# appends packet to output file
wrpcap ( filename , packet , append = True )
connections_Lock . release ()
# receive and execute commands
def runCommand (msg ):
global connections
global honeyd
global alertMode
print msg
# transfer all current pcaps
if( msg == " TRANSFER "):
connections_Lock . acquire ()
for ip in connections :
transferFile (ip , connections [ip ]. get ('filename '))
# return all values to 0
connections = {}
connections_Lock . release ()
elif (msg == " RESET "):
# transfer all current pcaps
connections_Lock . acquire ()
for ip in connections :
transferFile (ip , connections [ip ]. get ('filename '))
# return all values to 0
connections = {}
connections_Lock . release ()
# kill all honeyd
if( honeyd != None ):
subprocess . Popen ([" sudo killall honeyd "], stdin =None ,
stdout = devnull , stderr = devnull , shell = True )
honeyd = None
alertMode = False
# stops program completely
elif (msg == " KILL "):
# kill all honeyd
if( honeyd != None ):
subprocess . Popen ([" sudo killall honeyd "], stdin =None ,
stdout = devnull , stderr = devnull , shell = True )
# kill this script
subprocess . Popen ([" sudo killall python "], stdin =None , stdout =
devnull , stderr = devnull , shell = True )
# starts just honeyd
elif (msg == " START "):
# relaunch honeyd
if( honeyd == None ):
honeyd = subprocess . Popen ([" sudo / home / edge / Desktop /
honeyhive / scripts / startHoney .sh"], stdin =None , stdout = devnull ,
stderr = devnull , shell = True )
alertMode = True
# authenticate
authenticate ()
# stops just honeyd
elif (msg == " STOP "):
# kill all honeyd
if( honeyd != None ):
subprocess . Popen ([" sudo killall honeyd "], stdin =None ,
stdout = devnull , stderr = devnull , shell = True )
honeyd = None
alertMode = False
elif (msg == " REBOOT "):
subprocess . call ([" sudo ", " reboot "])
def heartbeat ():
# header information to send server
# python dictonary
header = {" Time ": time . strftime ("%Y -%m -% d_%H%M"),
" Honeyd ": honeydIP ,
"IP": ' 192.168.72.150 ',
"MSG": 'HEARTBEAT '}
# converts dictionary to json format
jsonHeader = json . dumps ( header )
try :
# attempts to connect to the server and tell it to open a
transfer port
sock = socket . socket ( socket . AF_INET , socket . SOCK_STREAM )
server_address = ( honeyHiveIP , port )
sock . connect ( server_address )
sock . sendall ( jsonHeader )
except socket .error , e:
print " Error creating Heartbeat socket : %s" %e
#clean -up actions that must be executed under all circumstances
finally :
sock . close ()
def authenticate ():
# header information to send server
# python dictonary
header = {" Honeyd ": honeydIP ,
" Honeypots ": honeypots ,
"MSG": ' AUTHENTICATE '}
# converts dictionary to json format
jsonHeader = json . dumps ( header )
try :
# attempts to connect to the server and tell it to open a
transfer port
sock = socket . socket ( socket . AF_INET , socket . SOCK_STREAM )
server_address = ( honeyHiveIP , port )
sock . connect ( server_address )
sock . sendall ( jsonHeader )
except socket .error , e:
print " Error creating Authenticate socket : %s" %e
#clean -up actions that must be executed under all circumstances
finally :
sock . close ()
def alert (packet , time ):
sport = 0
dport = 0
transLayer = 'TCP '
if packet . haslayer (TCP ):
sport = packet [TCP ]. sport
dport = packet [TCP ]. dport
elif packet . haslayer (UDP ):
sport = packet [UDP ]. sport
dport = packet [UDP ]. dport
transLayer = 'UDP '
elif packet . haslayer ( ICMP ):
transLayer = 'ICMP '
else :
transLayer = 'Other '
pckt_src = packet [IP ]. src
pckt_dst = packet [IP ]. dst
pckt_ttl = packet [IP ]. ttl
# header information to send server
# python dictonary
header = {" Time ": time . strftime ("%Y -%m -% d_%H%M"),
" TransLayer ": transLayer ,
" IP_SRC ": pckt_src ,
" IP_DST ": pckt_dst ,
" SPORT ": sport ,
" DPORT ": dport ,
"MSG": 'ALERT '}
# converts dictionary to json format
jsonHeader = json . dumps ( header )
try :
# attempts to connect to the server and tell it to open a
transfer port
sock = socket . socket ( socket . AF_INET , socket . SOCK_STREAM )
server_address = ( honeyHiveIP , port )
sock . connect ( server_address )
sock . sendall ( jsonHeader )
except socket .error , e:
print " Error creating Alert socket : %s" %e
#clean -up actions that must be executed under all circumstances
finally :
sock . close ()
# sends transfer file command to the server
def transferFile (ip , filename ):
# run command and return output
hashPcap = subprocess . check_output ([" md5sum ", filename ])
# header information to send server
# python dictonary
header = {" Honeyd ": honeydIP ,
"IP": ip ,
" Filename ": filename ,
" File_Size ": os. path . getsize ( filename ),
"MD5": hashPcap . split (' ')[0] ,
"MSG": 'PCAP ',
" Port ": transferPort }
# converts dictionary to json format
jsonHeader = json . dumps ( header )
try :
# attempts to connect to the server and tell it to open a
transfer port
sock = socket . socket ( socket . AF_INET , socket . SOCK_STREAM )
server_address = ( honeyHiveIP , port )
sock . connect ( server_address )
sock . sendall ( jsonHeader )
except socket .error , e:
print " Error creating Transfer Server socket : %s" %e
#clean -up actions that must be executed under all circumstances
finally :
sock . close ()
# allows time for the C2 server to receive and start the transfer
server
# on the requested port
time . sleep (3)
try :
transSock = socket . socket ( socket . AF_INET , socket . SOCK_STREAM )
transfer_address = ( honeyHiveIP , transferPort )
transSock . connect ( transfer_address )
# reads and sends the file to the server
f = open ( filename , "rb")
l = f. read (1024)
while (l):
# encrypt data before sending
transSock . send (l)
l = f. read (1024)
f. close ()
subprocess . call ([ 'rm ', '-f', filename ])
except socket .error , e:
print " Error creating Transfer File socket : %s" %e
#clean -up actions that must be executed under all circumstances
finally :
transSock . close ()
main ()
