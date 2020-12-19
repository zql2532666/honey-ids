set -e
set -x

if [ $# -ne 3 ]
    then
        echo "Wrong number of arguments supplied."
        echo "Usage: $0 <server_ip> <honeynode_token> <honeynode_name>"
        exit 1
fi

SERVER_IP=$1
TOKEN=$2
HONEYNODE_NAME=$3

INTERFACE=$(basename -a /sys/class/net/e*)
IP_ADDR=$(ip addr show dev $INTERFACE | grep "inet" | awk 'NR==1{print $2}' | cut -d '/' -f 1)
SUBNET=$(ifconfig $INTERFACE | grep "Mask:" | awk '{print $4}' | cut -d ':' -f 2)
DEPLOY_DATE=$(date +"%Y-%m-%d %T")



sudo apt install -y python-pip
pip install -U pip
apt-get update
apt-get -y install git supervisor python3-pip curl
pip install virtualenv
pip install configparser

# install honeyagent
mkdir /opt/honeyagent
cd /opt/honeyagent
wget http://$SERVER_IP:5000/api/v1/deployment_script/honeyagent -O honeyagent.py
wget http://$SERVER_IP:5000/api/v1/deployment_script/honeyagent_conf_file -O honeyagent.conf

# populate the honeyagent config file
sed -i "s/TOKEN:/TOKEN: $TOKEN/g" honeyagent.conf
sed -i "s/HONEYNODE_NAME:/HONEYNODE_NAME: $HONEYNODE_NAME/g" honeyagent.conf
sed -i "s/IP:/IP: $IP/g" honeyagent.conf
sed -i "s/SUBNET_MASK:/SUBNET_MASK: $SUBNET/g" honeyagent.conf
sed -i "s/HONEYPOT_TYPE:/HONEYPOT_TYPE: shockpot/g" honeyagent.conf
sed -i "s/NIDS_TYPE:/NIDS_TYPE: snort/g" honeyagent.conf
sed -i "s/DEPLOYED_DATE:/DEPLOYED_DATE: $DEPLOY_DATE/g" honeyagent.conf
sed -i "s/SERVER_IP:/SERVER_IP: $SERVER_IP/g" honeyagent.conf

# Get the Shockpot source
cd /opt
git clone https://github.com/zql2532666/shockpot.git
cd shockpot

virtualenv env
. env/bin/activate
pip install -r requirements.txt

# api call to join the honeynet
curl -X POST -H "Content-Type: application/json" -d "{
	\"honeynode_name\" : \"$HONEYNODE_NAME\",
	\"ip_addr\" : \"$IP_ADDR\",
	\"subnet_mask\" : \"$SUBNET\",
	\"honeypot_type\" : \"shockpot\",
	\"nids_type\" : \"snort\",
	\"no_of_attacks\" : \"0\",
	\"date_deployed\" : \"$DEPLOY_DATE\",
	\"heartbeat_status\" : \"False\",
	\"last_heard\" : \"$DEPLOY_DATE\",
	\"token\" : \"$TOKEN\"
}" http://$SERVER_IP:5000/api/v1/honeynodes/

# hpfeeds config
HPF_HOST=$SERVER_IP  
HPF_PORT=$(cat /opt/honeyagent/honeyagent.conf | grep "HPFEEDS_PORT" | awk -F: '{print $2}' | xargs)
HPF_IDENT=$TOKEN
HPF_SECRET=$TOKEN

cat > shockpot.conf<<EOF
[server]
host = 0.0.0.0
port = 80
[headers]
server = Apache/2.0.55 (Debian) PHP/5.1.2-1+b1 mod_ssl/2.0.55 OpenSSL/0.9.8b
[hpfeeds]
enabled  = True
host     = $HPF_HOST
port     = $HPF_PORT
identity = $HPF_IDENT
secret   = $HPF_SECRET
channel  = shockpot.events
only_exploits = True
[fetch_public_ip]
enabled = True
urls = ["http://www.telize.com/ip", "http://icanhazip.com", "http://ifconfig.me/ip"]
[template]
title = It Works!
EOF

# Config for supervisor.
cat > /etc/supervisor/conf.d/shockpot.conf <<EOF
[program:shockpot]
command=/opt/shockpot/env/bin/python /opt/shockpot/shockpot.py 
directory=/opt/shockpot
stdout_logfile=/opt/shockpot/shockpot.out
stderr_logfile=/opt/shockpot/shockpot.err
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
EOF

# configure supervisor for honeyagent
cat > /etc/supervisor/conf.d/honeyagent.conf <<EOF
[program:honeyagent]
command=python3 /opt/honeyagent/honeyagent.py
directory=/opt/honeyagent
stdout_logfile=/opt/honeyagent/honeyagent.out
stderr_logfile=/opt/honeyagent/honeyagent.err
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
EOF

supervisorctl update