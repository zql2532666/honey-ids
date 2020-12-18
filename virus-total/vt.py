#!/usr/bin/env python

"""
Authon: Derek, Thein Than Zaw
"""

import requests, argparse, os, time, json, hashlib
API_KEY='a4285326b887ff18976ba19661911b61d4833cf4943238413f957c19f0770d6d'
# REQUEST FUNCTION
def vt_request(hash,key=API_KEY) :
	parameters = {"apikey": key, "resource": hash}
	url = requests.get("https://www.virustotal.com/vtapi/v2/file/report", params=parameters)
	json_response = url.json()
	# with open('return-api-format.txt','w') as w:
	# 	w.write(json.dumps(json_response) )
	response = int(json_response.get("response_code"))
	print(json_response)
	print("\n\n")
	
	# DOES THE HASH EXISTS IN VT DATABASE?
	if response == 0:
		print(hash + ": UNKNOWN")

	# DOES THE HASH EXISTS IN VT DATABASE?
	elif response == 1:
		positives = int(json_response.get("positives"))
		if positives >= 3:
			print(hash + ": MALICIOUS")
		else:
			print(hash + ": NOT MALICIOUS")
	else:
		print(hash + ": CAN NOT BE SEARCHED")

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def main():
	hash = md5("sample_87.exe")
	vt_request(hash)

if __name__ == "__main__":
	main()