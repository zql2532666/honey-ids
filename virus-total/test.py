
"""
dict_keys([
    'scans', 
    'scan_id', 
    'sha1', 
    'resource', 
    'response_code', 
    'scan_date', 
    'permalink', 
    'verbose_msg', 
    'total', 
    'positives', 
    'sha256', 
    'md5'
    ])

"""
import json
with open('return-api-format.txt','r') as r:
	input = r.readlines()

input_dict = json.loads(input[0])
print(input_dict.keys())
print(f"sha256 --> {input_dict['sha256']}")
