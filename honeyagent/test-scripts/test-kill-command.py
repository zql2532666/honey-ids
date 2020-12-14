import time 
import json
import requests
# return_db_data = [
#     {"heartbeat_status": True, 
#     "token": "1", 
#     "last_heard": "2020-01-01 10:10:10"},
#      {"heartbeat_status": False, 
#     "token": "2", 
#     "last_heard": "2020-01-01 10:10:10"}
# ]
# heartbeat_dict = dict()
# for data in return_db_data:
#     heartbeat_dict[data["token"]] = {
#             'heartbeat_status' : data['heartbeat_status'],
#             'last_heard' : data['last_heard']
#     }

# print "time.time(): %f " %  time.time()
# print time.localtime( time.time() )
# print time.asctime( time.localtime(time.time()) )

# current_time = time.time()
# time_struct_time_local= time.strptime("2020-01-01 10:10:10", "%Y-%m-%d %H:%M:%S")  
# time_seconds_since_the_epoch = time.mktime(time_struct_time_local)
# # time.strptime("30 Nov 00", "%d %b %y")
# print(time_seconds_since_the_epoch)

# time_2 = time.localtime(time_seconds_since_the_epoch)
# print(f"time_2 {time_2}")
# print(f"{time_2[0]}-{time_2[1]}-{time_2[2]} {time_2[3]}:{time_2[4]}:{time_2[5]}")

# data_heartbeats_server = {
#     '1': {'heartbeat_status': False, 'last_heard': 1577844610.0}, 
#     '2': {'heartbeat_status': False, 'last_heard': 1577844610.0}
#     }
# db_data = {}

# for key in data_heartbeats_server.keys():  
#     print(data_heartbeats_server[key])
#     # print(data_heartbeats_server[key]['last_heard'])
    
    # last_heard_epoch = float(data_heartbeats_server[key]['last_heard'])
    # print(f"last_heard_epoch: {last_heard_epoch}")
    # last_heard_struct_time = time.localtime(last_heard_epoch)
    # last_heard = f"{last_heard_struct_time[0]}-{last_heard_struct_time[1]}-{last_heard_struct_time[2]} {last_heard_struct_time[3]}:{last_heard_struct_time[4]}:{last_heard_struct_time[5]}"
    # print(f"last_heard final : {last_heard}\n")
    # # print(last_heard)

# {'heartbeat_status': True, 'last_heard': 1607935547.7059884}
# last_heard = 1607935547.7059884
# print(last_heard)
# last_heard_epoch = float(last_heard)
# last_heard_struct_time = time.localtime(last_heard_epoch)
# last_heard = f"{last_heard_struct_time[0]}-{last_heard_struct_time[1]}-{last_heard_struct_time[2]} {last_heard_struct_time[3]}:{last_heard_struct_time[4]}:{last_heard_struct_time[5]}"
# print(last_heard)


# WEB_SERVER_IP = '127.0.0.1'
# WEB_SERVER_PORT= 5000
# API = f"http://{WEB_SERVER_IP}:{WEB_SERVER_PORT}/api/v1/heartbeats"

# test_data = {
#   "1": {
#     "heartbeat_status": "True", 
#     "time_last_heard": "2020-01-01 10:10:10"
#   }, 
#   "2": {
#     "heartbeat_status": "False", 
#     "time_last_heard": "2020-01-01 10:10:10"
#   }
# }
# headers = {'content-type': 'application/json'}

# json_data = json.dumps(test_data)

# requests.post(API, data=json_data, headers=headers)

""" 
HeartBeat client: sends an UDP packet to a given server every 10 seconds.

    Adjust the constant parameters as needed, in honeyagent.conf
"""

import socket



data = {
    "command": "KILL"
}

data_json = json.dumps(data)
data_encoded = data_json.encode('utf-8')
try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as hbsocket:
        hbsocket.sendto(data_encoded, ('', 8888))
        sleep(HELLO_INTERVAL)
except socket.error as e:
    print("Error creating Socket\n")
    print(e)

