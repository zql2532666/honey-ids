import time 
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

print "time.time(): %f " %  time.time()
print time.localtime( time.time() )
print time.asctime( time.localtime(time.time()) )