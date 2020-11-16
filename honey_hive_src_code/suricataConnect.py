import subprocess
import socket
import json
import os
os.sys . path . append ('/usr / local /bin / scapy ')
from scapy .all import *
# color honey yellow is # a98307
port = 9830
honeyHiveIP = ' 192.168.1.233 '
suricataIP = ' 192.168.1.231 '
attacker = ' 192.168.1.230 '
suricataRunning = False
packetRXStart = 0
packetTXStart = 0
totalPackets = 0
devnull = open (os. devnull , 'wb ')
def main ():
print (" Scapy Packet Sniffer Engaged ")
sniff ( iface =" eth0 ", prn= processPacket , store =0)
def processPacket ( packet ):
global totalPackets
if packet . haslayer (IP) and ( packet [IP ]. src == attacker or packet [
IP ]. dst == attacker ):
totalPackets += 1
# running on mirrored port so make sure it 's for this IP
if packet . haslayer (UDP ) and packet [UDP ]. dport == 9830 and packet [
IP ]. dst == suricataIP :
print " Command Received "
runCommand ( packet [UDP ]. load . strip ('\n'))
# receive and execute commands
def runCommand (msg ):
global suricataRunning
global packetRXStart , packetTXStart
global totalPackets
logGrep = subprocess . Popen ([ 'sudo ', 'grep ', '-i', 'scan ', '/var /
log / suricata / fast .log '], stdout = subprocess . PIPE )
wc = subprocess . Popen ([ 'wc ', '-l'], stdin = logGrep .stdout , stdout =
subprocess . PIPE )
out , err = wc. communicate ()
numAlerts = int(out)
typeCountGrep = subprocess . Popen ([ 'sudo ', 'grep ', '-i', 'scan ', '
/var/log/ suricata / fast .log '], stdout = subprocess . PIPE )
cutRuleSig = subprocess . Popen ([ 'cut ', '-f', '4', '-d', " "],
stdin = typeCountGrep .stdout , stdout = subprocess . PIPE )
sort = subprocess . Popen ([ 'sort '], stdin = cutRuleSig .stdout , stdout
= subprocess . PIPE )
uniq = subprocess . Popen ([ 'uniq '], stdin = sort .stdout , stdout =
subprocess . PIPE )
wcTypes = subprocess . Popen ([ 'wc ', '-l'], stdin = uniq .stdout ,
stdout = subprocess . PIPE )
out2 , err2 = wcTypes . communicate ()
numAlertTypes = int( out2 )
print msg
# transfer current scan alert count and clear the log
if( msg == " TRANSFER "):
# packets sent and received after run complete
countRXEnd = subprocess . Popen ([ 'cat ', '/sys/ class /net/ eth0 /
statistics / rx_packets '], stdout = subprocess .PIPE , close_fds = True )
packetRXEnd , err = countRXEnd . communicate ()
countTXEnd = subprocess . Popen ([ 'cat ', '/sys/ class /net/ eth0 /
statistics / tx_packets '], stdout = subprocess .PIPE , close_fds = True )
packetTXEnd , err = countTXEnd . communicate ()
packetCount = int( packetRXEnd ) + int( packetTXEnd ) - int(
packetRXStart ) - int( packetTXStart )
# send alert count
suricata ( numAlerts , numAlertTypes , totalPackets )
print " Alerts : "+ str( numAlerts ) + str( numAlertTypes ) + str(
packetCount )
# clear log file
os. system (" sudo rm /var /log / suricata / fast .log ")
subprocess . call ([ 'sudo ', 'touch ', '/var/log/ suricata / fast .log '
])
elif (msg == " RESET "):
# packets sent and received after run complete
countRXEnd = subprocess . Popen ([ 'cat ', '/sys/ class /net/ eth0 /
statistics / rx_packets '], stdout = subprocess .PIPE , close_fds = True )
packetRXEnd , err = countRXEnd . communicate ()
countTXEnd = subprocess . Popen ([ 'cat ', '/sys/ class /net/ eth0 /
statistics / tx_packets '], stdout = subprocess .PIPE , close_fds = True )
packetTXEnd , err = countTXEnd . communicate ()
packetCount = int( packetRXEnd ) + int( packetTXEnd ) - int(
packetRXStart ) - int( packetTXStart )
# send alert count
suricata ( numAlerts , numAlertTypes , totalPackets )
print " Alerts : "+ str( numAlerts ) + str( numAlertTypes ) + str(
packetCount )
# finds and kills suricata based on PID
if( suricataRunning ):
subprocess . Popen ([ 'sudo ./ killSuricata .sh '], stdout =
subprocess .PIPE , shell = True )
suricataRunning = False
# clear log file
os. system (" sudo rm /var /log / suricata / fast .log ")
subprocess . call ([ 'sudo ', 'touch ', '/var/log/ suricata / fast .log '
])
# stops program completely
elif (msg == " KILL "):
if( suricataRunning ):
subprocess . Popen ([ 'sudo ./ killSuricata .sh '], stdout =
subprocess .PIPE , shell = True )
# kill this script
subprocess . Popen ([" sudo killall python "], stdin =None , stdout =
devnull , stderr = devnull , shell = True )
# starts just suricata
elif (msg == " START "):
countRXStart = subprocess . Popen ([ 'cat ', '/sys / class /net / eth0 /
statistics / rx_packets '], stdout = subprocess .PIPE , close_fds = True )
packetRXStart , err = countRXStart . communicate ()
countTXStart = subprocess . Popen ([ 'cat ', '/sys / class /net / eth0 /
statistics / tx_packets '], stdout = subprocess .PIPE , close_fds = True )
packetTXStart , err = countTXStart . communicate ()
# launch suricata
# sudo suricata -c /etc/ suricata / suricata . yaml -i eth0
if(not suricataRunning ):
# subprocess . Popen ([" sudo "], stdin =None , stdout = devnull ,
stderr = devnull , shell = True )
subprocess . Popen ([" sudo suricata -c /etc/ suricata / suricata .
yaml -i eth0 "], stdin =None , stdout = devnull , stderr = devnull , shell
= True )
suricataRunning = True
# stops just suricata
elif (msg == " STOP "):
# kill suricata
# sudo kill $(ps aux | grep '[s]udo suricata -c /etc/ suricata /
suricata . yaml -i eth0 ' | awk '{ print $2 }')
if( suricataRunning ):
subprocess . Popen ([ 'sudo ./ killSuricata .sh '], stdout =
subprocess .PIPE , shell = True )
suricataRunning = False
elif (msg == " REBOOT "):
subprocess . call ([" sudo ", " reboot "])
def suricata ( numAlerts , numTypes , numPackets ):
# header information to send server
# python dictonary
header = {" NumAlerts ": numAlerts ,
" NumTypes ": numTypes ,
" NumPackets ": numPackets ,
"MSG": 'SURICATA '}
# converts dictionary to json format
jsonHeader = json . dumps ( header )
try :
sock = socket . socket ( socket . AF_INET , socket . SOCK_STREAM )
# creates a socket for the connection to the server
server_address = ( honeyHiveIP , port )
# attempts to connect to the server
sock . connect ( server_address )
sock . sendall ( jsonHeader )
except socket .error , e:
print " Error creating Suricata socket : %s" %e
finally :
# closes connection
sock . close ()
main ()
