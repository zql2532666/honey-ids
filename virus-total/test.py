
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
print(f"sha1 --> {input_dict['sha1']}")
print(f"md5 --> {input_dict['md5']}")
print(f"total --> {input_dict['total']}")
print(f"positives --> {input_dict['positives']}")


