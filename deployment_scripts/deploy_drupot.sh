#!/bin/bash

#!!! NOTE: drupot will not work if no hpfeeds configuration is in the config file
# it will also terminate immediately if it cannot reach the hpfeeds broker

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

# stop and disable all services that use package management. 
function killService() {
    service=$1
    sudo systemctl stop $service
    sudo systemctl kill --kill-who=all $service

    # Wait until the status of the service is either exited or killed.
    while ! (sudo systemctl status "$service" | grep -q "Main.*code=\(exited\|killed\)")
    do
        sleep 10
    done
}

function disableTimers() {
    sudo systemctl disable apt-daily.timer
    sudo systemctl disable apt-daily-upgrade.timer
}

function killServices() {
    killService unattended-upgrades.service
    killService apt-daily.service
    killService apt-daily-upgrade.service
}

function main() {
    disableTimers
    killServices
}

main

apt-get update
apt-get -y install git supervisor curl python-pip python3-pip
pip install configparser

####################################################################
# Install a decent version of golang

cd /usr/local/
wget https://dl.google.com/go/go1.15.2.linux-amd64.tar.gz 
tar zxf go1.15.2.linux-amd64.tar.gz && rm go1.15.2.linux-amd64.tar.gz 
####################################################################

export GO111MODULE=on

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
sed -i "s/HONEYPOT_TYPE:/HONEYPOT_TYPE: drupot/g" honeyagent.conf
sed -i "s/NIDS_TYPE:/NIDS_TYPE: snort/g" honeyagent.conf
sed -i "s/DEPLOYED_DATE:/DEPLOYED_DATE: $DEPLOY_DATE/g" honeyagent.conf
sed -i "s/SERVER_IP:/SERVER_IP: $SERVER_IP/g" honeyagent.conf

# Get the drupot source
cd /opt
git clone https://github.com/zql2532666/drupot.git
cd drupot
git checkout v0.2.4

/usr/local/go/bin/go build

# api call to join the honeynet
curl -X POST -H "Content-Type: application/json" -d "{
	\"honeynode_name\" : \"$HONEYNODE_NAME\",
	\"ip_addr\" : \"$IP_ADDR\",
	\"subnet_mask\" : \"$SUBNET\",
	\"honeypot_type\" : \"drupot\",
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

cat > config.toml<<EOF
# Drupot Configuration File
[drupal]
# Port to server the honeypot webserver on.
# Note: Ports under 1024 require sudo.
port = 80
site_name = "Nothing"
name_randomizer = true
# TODO: Optional SSL/TLS Cert
[hpfeeds]
enabled = true
host = "$HPF_HOST"
port = $HPF_PORT
ident = "$HPF_IDENT"
auth = "$HPF_SECRET"
channel = "agave.events"
[fetch_public_ip]
enabled = true
urls = ["http://icanhazip.com/", "http://ifconfig.me/ip"]
EOF


# Config for supervisor.
cat > /etc/supervisor/conf.d/drupot.conf <<EOF
[program:drupot]
command=/opt/drupot/drupot
directory=/opt/drupot
stdout_logfile=/opt/drupot/drupot.out
stderr_logfile=/opt/drupot/drupot.err
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
supervisorctl restart all