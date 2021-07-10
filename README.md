# HONEYIDS


# TODO
- <s> fix snort deployment script </s>
- Add honeyagent installation + configuration in the deployment scripts for cowrie and snort


# Hpfeeds Setup

###  NOTE: THIS IS DONE ON THE SERVER 
1.  install the hpfeeds library and aionotify
```bash
dev@dev:~$ pip3 install hpfeeds
dev@dev:~$ pip3 install hpfeeds[broker]
dev@dev:~$ pip3 install aionotify
```

2. clone our github repo
```bash 
dev@dev:~$ git clone https://github.com/zql2532666/DISM-FT-3A-67-FYP.git
dev@dev:~$ cd DISM-FT-3A-67-FYP/hpfeeds
```
3. start the broker

```bash
# this command starts running the broker
# auth.json is to store the credentials for the honeypots and log collector to authenticate to the broker 
# this is just a test broker, in the final version we will be storing the credentials in the mongodb database 
hpfeeds-broker -e tcp:port=10000 --auth=auth.json --name=mybroker
```

4. run the `log_collector.py`. This script will subscribe to the broker and and pulls the logs published/sent by the honeypots and print them to the console
```bash
dev@dev:~/Desktop/DISM-FT-3A-67-FYP/hpfeeds$ python3 log_collector.py 
connected to mybroker
```

5. Deploy the honeypot on a clean ubuntu vm, make sure you dont comment out the hpfeeds config part this time. you can declare the hpfeeds config variables in the deployment script for testing. For example, if u are testing shockpot, the variables will be:
```bash
HPF_HOST=$1     # will be ur server's ip. it is passed to the script as command line argument
HPF_PORT=10000
HPF_IDENT="shockpot"
HPF_SECRET="shockpot"
```
you can also refer to the deployment scripts in the dir `deployment_scripts` to see how i did it.

6. Run scans and attacks on the honeypot and check the output of `log_collector.py` to see what the log looks like. Example output:
```bash
dev@dev:~/Desktop/DISM-FT-3A-67-FYP/hpfeeds$ python3 log_collector.py 
connected to mybroker
Identifier : wordpot
Channel: wordpot.events
Payload:
{'username': 'admin', 'plugin': 'badlogin', 'url': 'http://192.168.148.149/wp-login.php', 'source_ip': '192.168.148.1', 'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36', 'source_port': 20935, 'password': 'admin', 'dest_ip': '0.0.0.0', 'dest_port': '80'}
```
