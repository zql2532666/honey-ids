import subprocess
import sys
import socket
import json
import time as t
import random
import os
from datetime import datetime , date , time , timedelta
devnull = open (os. devnull , 'wb ')
rasPi = ' 192.168.1.231 '
honeyd1 = ' 192.168.1.154 '
honeyd2 = ' 192.168.1.164 '
honeyd3 = ' 192.168.1.174 '
honeyd4 = ' 192.168.1.184 '
port = 9830
honeyHiveIP = ' 192.168.1.233 '
network = '192.168.1.150 -192 '
camera = [' 192.168.1.190 ', ' 192.168.1.150 ', ' 192.168.1.170 ', '192.168.1.160 ']
thermostat = [' 192.168.1.191 ', ' 192.168.1.151 ', ' 192.168.1.171 ', '192.168.1.161 ']
outlet = [' 192.168.1.192 ', ' 192.168.1.152 ', ' 192.168.1.172 ', '192.168.1.162 ']
order = []
experimentFile = 'experiment .txt '
expRunNum = 0
numRuns = 30
def main ():
global order
# checks to see if a file with the run order exists and makes
sure it 's not empty
if os. path . exists ( experimentFile ) and os. path . getsize (
experimentFile ) > 0:
f = open ( experimentFile , 'r')
for line in f:
value = line . split ()
lambdaFunc = None
print value
# address of the functions can change between runs
# better to just check the name than store the address
value
if value [0] == 'nmapScan ':
lambdaFunc = nmapScan
elif value [0] == 'baseline ':
lambdaFunc = baseline
elif value [0] == 'wget ':
lambdaFunc = wget
# appends all experiments in the file to be run
order . append ({" Lambda ": lambdaFunc , " Name ": value [0] , "
HoneyPots ": int( value [1]) , " Level ": int( value [2]) })
f. close ()
else :
for i in range ( numRuns ):
# runExperiment (i+1)
# order = []
randomizeOrder ()
random . shuffle ( order )
f = open ( experimentFile , 'a')
for run in order :
f. write (run['Name '] + ' ' + str(run['HoneyPots ']) + ' ' +
str (run['Level ']) + '\n')
f. close ()
# removes very last newline '\n' so that there isn 't a blank
line at the end of the file
fT = open ( experimentFile , 'rb+')
fT. seek (-1, os. SEEK_END )
fT. truncate ()
fT. close ()
runExperiment (1)
def runExperiment ( runNumber ):
global expRunNum
for run in order :
# starts the specified number of honeypots , and suricata
print " Sending Honeypot Starts "
sendCmd (run [" HoneyPots "], " START \n")
sendCmd (run [" HoneyPots "], " START \n")
sendCmd (run [" HoneyPots "], " START \n")
# allows enough time for everything to reach a stable state
# takes about 30 seconds for suricata to startup on the
rasberry pi
t. sleep (40.0)
# packets sent and received before run
# cat /sys/ class /net/ enp2s0 / statistics / rx_packets
# RX number of packets received
# TX number of packets transmitted
# need to cat both for full picture
countRXStart = subprocess . Popen ([ 'cat ', '/sys / class /net /
enp2s0 / statistics / rx_packets '], stdout = subprocess .PIPE , close_fds
= True )
packetRXStart , err = countRXStart . communicate ()
countTXStart = subprocess . Popen ([ 'cat ', '/sys / class /net /
enp2s0 / statistics / tx_packets '], stdout = subprocess .PIPE , close_fds
= True )
packetTXStart , err = countTXStart . communicate ()
# print packetCountStart
start = datetime .now ()
print " Start Time :" + start . strftime ("%Y -%m -% d_%H%M")
print " nmapScan " + " Level : " + str(run[" Level "]) + '
Honeypots : ' + str(run[" HoneyPots "])
# runs the specified test with corresponding level
run[" Lambda "]( run[" Level "], run[" HoneyPots "])
# packets sent and received after run complete
countRXEnd = subprocess . Popen ([ 'cat ', '/sys/ class /net/ enp2s0
/ statistics / rx_packets '], stdout = subprocess .PIPE , close_fds = True )
packetRXEnd , err = countRXEnd . communicate ()
countTXEnd = subprocess . Popen ([ 'cat ', '/sys/ class /net/ enp2s0
/ statistics / tx_packets '], stdout = subprocess .PIPE , close_fds = True )
packetTXEnd , err = countTXEnd . communicate ()
# print packetCountEnd
packetCount = int( packetRXEnd ) + int( packetTXEnd ) - int(
packetRXStart ) - int( packetTXStart )
print 'Packets Sent and Received : '+ str( packetCount )
end = datetime .now ()
print "End Time :" + end. strftime ("%Y -%m -% d_%H%M")
elapsedTime = (end - start ). total_seconds ()
print " Elapsed Time :" + str( elapsedTime )
print " Sending Honeypot Resets "
# stops all honeypots and forces transfer of pcap , stops
suricata
sendCmd (run [" HoneyPots "], " RESET \n")
sendCmd (run [" HoneyPots "], " RESET \n")
sendCmd (run [" HoneyPots "], " RESET \n")
# time required for honeypots and suricata to send all data
to c2 server
t. sleep (45.0)
sendSnort ()
# allows time for Snort to parse PCAP files
t. sleep (90.0)
# tells the C2 server to reset and send gathered stats to
this script
res = sendReset ()
# write gathered results to corresponding csv file
writeResults (run , res , packetCount , elapsedTime )
# removes run from experimentFile since it successfully completed
lines = open ( experimentFile ). readlines ()
with open ( experimentFile , 'w') as f:
f. writelines ( lines [1:])
f. close ()
# Reboots all machines for a clean stable start state
print " Sending Honeypot Reboots "
sendCmd (run [" HoneyPots "], " REBOOT \n")
sendCmd (run [" HoneyPots "], " REBOOT \n")
sendCmd (run [" HoneyPots "], " REBOOT \n")
sendReboot ()
# allows plenty of time for all devices to reboot
# and startup scripts before proceeding to next iteration
# win 10 VM takes longest (30 seconds for reboot , another 15
for c2 server startup - 45s total )
# sometimes can take longer and crash script ....
t. sleep (45.0)
# makes sure c2 servere is up and running berfore starting
next iteration
sendStart ()
expRunNum += 1
# randomizes the order in which all 36 tests are run
def randomizeOrder ():
# inital testing
# test = [{" Lambda ": wget , " Name ": 'wget '}]
test = [{" Lambda ": nmapScan , " Name ": 'nmapScan '}] #, {" Lambda ":
baseline , " Name ": 'baseline '}] #, {" Lambda ": wget , " Name ": 'wget
'}]
for i in range (4):
numHps = i;
for testType in test :
for level in range (4):
order . append ({" Lambda ": testType [" Lambda "], " Name ":
testType ['Name '], " HoneyPots ": numHps , " Level ": level })
# random . shuffle ( order )
# tests to see if alerts are generated for different kinds of scans
# Levels are the different scan types :
# nmap 192.168.1.0/24 -sT
# nmap 192.168.1.0/24 -A
# sudo nmap 192.168.1.0/24 --max - hostgroup 1 --randomize - hosts -
f 8
def nmapScan ( scanType , numHps ):
global expRunNum
if ( scanType == 0):
print " Control Group : sleep (1341) "
t. sleep (1341)
elif ( scanType == 1):
print " nmap ipLst .txt -sT -Pn"
subprocess . call ([ 'nmap ', '-iL ', 'ipLst .txt ', '-sT ', '-Pn ', '
-oX ', 'run '+ str ( expRunNum )+'.xml '], stdin =None , stdout =None ,
stderr =None , shell = False )
elif ( scanType == 2):
print " nmap ipLst .txt -A -Pn"
subprocess . call ([ 'nmap ', '-iL ', 'ipLst .txt ', '-A', '-Pn ', '-
oX ', 'run '+ str( expRunNum )+'.xml '], stdin =None , stdout =None ,
stderr =None , shell = False )
elif ( scanType == 3):
print " sudo nmap ipLst .txt --scan - delay 1075 ms --randomize -
hosts -f 8 -Pn"
subprocess . call ([ 'sudo ', 'nmap ', '-iL ', 'ipLst .txt ', '--scan
- delay ', '1075 ms ', '--randomize - hosts ', '-f', '8', '-Pn ', '-oX ',
'run '+ str( expRunNum )+'.xml '],
stdin =None , stdout =None , stderr =None , shell = False )
# tests to see if an alert is generated for malicious wgets that
modify IoT device
# Levels are the different typse of devices :
# TITAThink Camera 192.168.1.1[5 -8]0
# Prolophix Thermostat 192.168.1.1[5 -8]1
# ez - Outlet 2 Power Outlet 192.168.1.1[5 -8]2
def wget ( iotDevice , numHps ):
if ( iotDevice == 0):
print " Control Group : sleep (30) "
t. sleep (30)
elif ( iotDevice == 1):
for ip in range ( numHps + 1):
subprocess . call ([ 'wget ', '--user ', 'admin ', '-- password '
, 'admin ', '--tries ', '1', '-- timeout ', '1', 'http :// '+ camera [ip
]+ '/ form / deleteStorageAllApply ? lang =en '],
stdin =None , stdout =None , stderr =None , shell = False )
print " wget TITAThink Cameras "
elif ( iotDevice == 2):
print " wget Prolophix Thermostats "
for ip in range ( numHps + 1):
subprocess . call ([ 'wget ', '--user ', 'admin ', '-- password ',
'admin ', '--tries ', '1', '-- timeout ', '1', 'http :// '+ thermostat [
ip ]+ '/ index . shtml '],
stdin =None , stdout =None , stderr =None , shell = False )
elif ( iotDevice == 3):
print " wget ez - Outlets "
for ip in range ( numHps + 1):
subprocess . call ([ 'wget ', '--tries ', '1', '-- timeout ', '1'
, 'http :// '+ outlet [ip ]+ '/ invert .cgi '],
stdin =None , stdout =None , stderr =None , shell = False )
# tests to see if alerts are genereated with no alert traffic
# levels : 20s, 660s, 6000 s - to match length of each scan ( from
pilot studies )
def baseline ( runTime , numHps ):
if ( runTime == 1):
print " Baseline 30s"
t. sleep (30.0)
elif ( runTime == 2):
print " Baseline 660s"
t. sleep (660.0)
else :
print " Baseline 1500 s"
t. sleep (1500.0)
def sendCmd (numHPs , cmd):
# 1 non - mirrored
if ( numHPs == 1):
hp1 = socket . socket ( socket . AF_INET , socket . SOCK_DGRAM )
hp1. sendto (cmd , ( honeyd1 , port ))
hp1. close ()
# 1 non - mirrored , 1 mirrored
elif ( numHPs == 2):
hp1 = socket . socket ( socket . AF_INET , socket . SOCK_DGRAM )
hp1. sendto (cmd , ( honeyd1 , port ))
hp1. close ()
hp3 = socket . socket ( socket . AF_INET , socket . SOCK_DGRAM )
hp3. sendto (cmd , ( honeyd3 , port ))
hp3. close ()
# 2 non - mirrored , 1 mirroed
elif ( numHPs == 3):
hp1 = socket . socket ( socket . AF_INET , socket . SOCK_DGRAM )
hp1. sendto (cmd , ( honeyd1 , port ))
hp1. close ()
hp2 = socket . socket ( socket . AF_INET , socket . SOCK_DGRAM )
hp2. sendto (cmd , ( honeyd2 , port ))
hp2. close ()
hp3 = socket . socket ( socket . AF_INET , socket . SOCK_DGRAM )
hp3. sendto (cmd , ( honeyd3 , port ))
hp3. close ()
# 2 non - mirrored , 2 mirrored
elif ( numHPs == 4):
hp1 = socket . socket ( socket . AF_INET , socket . SOCK_DGRAM )
hp1. sendto (cmd , ( honeyd1 , port ))
hp1. close ()
hp2 = socket . socket ( socket . AF_INET , socket . SOCK_DGRAM )
hp2. sendto (cmd , ( honeyd2 , port ))
hp2. close ()
hp3 = socket . socket ( socket . AF_INET , socket . SOCK_DGRAM )
hp3. sendto (cmd , ( honeyd3 , port ))
hp3. close ()
hp4 = socket . socket ( socket . AF_INET , socket . SOCK_DGRAM )
hp4. sendto (cmd , ( honeyd4 , port ))
hp4. close ()
# starts suricata on raspberry pi
ras = socket . socket ( socket . AF_INET , socket . SOCK_DGRAM )
ras. sendto (cmd , (rasPi , port ))
ras. close ()
def sendStart ():
print " START sent to C2 Server "
while True :
try:
sock = socket . socket ( socket . AF_INET , socket . SOCK_STREAM )
# creates a socket for the connection to the server
server_address = ( honeyHiveIP , port )
# attempts to connect to the server
sock . connect ( server_address )
# header information to send server
# python dictonary
header = {" MSG": 'START '}
# converts dictionary to json format
jsonHeader = json . dumps ( header )
# sends all data
sock . sendall ( jsonHeader )
except socket .error , e:
print " Error creating Start Socket : %s" %e
continue
break
sock . close ()
def sendSnort ():
print " SNORT sent to C2 Server "
while True :
try:
sock = socket . socket ( socket . AF_INET , socket . SOCK_STREAM )
# creates a socket for the connection to the server
server_address = ( honeyHiveIP , port )
# attempts to connect to the server
sock . connect ( server_address )
# header information to send server
# python dictonary
header = {" MSG": 'SNORT '}
# converts dictionary to json format
jsonHeader = json . dumps ( header )
# sends all data
sock . sendall ( jsonHeader )
except socket .error , e:
print " Error creating Snort Socket : %s" %e
continue
break
sock . close ()
def sendReboot ():
print " REBOOT Sent to C2 Server "
while True :
try:
sock = socket . socket ( socket . AF_INET , socket . SOCK_STREAM )
# creates a socket for the connection to the server
server_address = ( honeyHiveIP , port )
# attempts to connect to the server
sock . connect ( server_address )
# header information to send server
# python dictonary
header = {" MSG": 'REBOOT '}
# converts dictionary to json format
jsonHeader = json . dumps ( header )
# sends all data
sock . sendall ( jsonHeader )
except socket .error , e:
print " Error creating Reboot Socket : %s" %e
continue
break
sock . close ()
def sendReset ():
print " RESET sent to C2 Server "
while True :
try :
sock = socket . socket ( socket . AF_INET , socket . SOCK_STREAM )
# creates a socket for the connection to the server
server_address = ( honeyHiveIP , port )
# attempts to connect to the server
sock . connect ( server_address )
# header information to send server
# python dictonary
header = {" MSG ": 'RESET '}
# converts dictionary to json format
jsonHeader = json . dumps ( header )
# sends all data
sock . sendall ( jsonHeader )
#{ Interactions : numInteractions , Snort : numSnortAlerts ,
Packets : numPackets }
res = sock . recv (4096)
except socket .error , e:
print " Error creating Reset Socket : %s" %e
continue
break
sock . close ()
return json . loads (res )
def writeResults ( runInfo , results , packetCount , elapsedTime ):
print " Writing Results "
# add suricata packet count and suricata num types of alerts
count
output = str ( runInfo ['Level ']) + ',' + str ( runInfo ['HoneyPots '])
+ ',' + str( results ['numHoneypots ']) + ',' + str( results ['
Interactions ']) + ',' + str ( results ['numPCAPs ']) + ',' + str (
results ['SnortICount ']) + ',' + str ( results ['SnortMCount ']) + ',
' + str( results ['Snort ']) + ',' + str ( results ['SnortTypes ']) + '
,' + str( results ['SnortMerged ']) + ',' + str ( results ['
SnortTypesMerged ']) + ',' + str ( results ['Suricata ']) + ',' + str
( results [' SuricataTypes ']) + ',' + str( packetCount ) + ',' + str(
results ['Packets ']) + ',' + str ( results [' suricataPackets ']) + ','
+ str( elapsedTime ) + '\n'
print " Output : " + output
# nmap
if ( runInfo ['Name '] == 'nmapScan '):
nmap_file = open ('nmap .csv ', mode ='a')
nmap_file . write ( output )
nmap_file . close ()
# baseline
elif ( runInfo ['Name '] == 'baseline '):
baseline_file = open ('baseline .csv ', mode ='a')
baseline_file . write ( output )
baseline_file . close ()
# wget
else :
wget_file = open ('wget .csv ', mode ='a')
wget_file . write ( output )
wget_file . close ()
main ()
