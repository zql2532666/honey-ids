#!/bin/bash

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

# install ruby 2.4, default version on ubuntu 16.04 is 2.3, which is not compatible with some packages used by sticky_elephant
apt-get install -y software-properties-common
apt-add-repository -y ppa:brightbox/ruby-ng
apt-get update
apt-get install -y ruby2.4 ruby2.4-dev

# install git and supervisor
apt-get -y install git supervisor curl python-pip python3-pip

pip install configparser

useradd -d /home/sticky_elephant -m sticky_elephant

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
sed -i "s/HONEYPOT_TYPE:/HONEYPOT_TYPE: sticky_elephant/g" honeyagent.conf
sed -i "s/NIDS_TYPE:/NIDS_TYPE: snort/g" honeyagent.conf
sed -i "s/DEPLOYED_DATE:/DEPLOYED_DATE: $DEPLOY_DATE/g" honeyagent.conf
sed -i "s/SERVER_IP:/SERVER_IP: $SERVER_IP/g" honeyagent.conf

# Get the sticky_elephant source
cd /opt
git clone https://github.com/zql2532666/sticky_elephant.git sticky_elephant
cd sticky_elephant

# api call to join the honeynet
curl -X POST -H "Content-Type: application/json" -d "{
	\"honeynode_name\" : \"$HONEYNODE_NAME\",
	\"ip_addr\" : \"$IP_ADDR\",
	\"subnet_mask\" : \"$SUBNET\",
	\"honeypot_type\" : \"sticky_elephant\",
	\"nids_type\" : \"snort\",
	\"no_of_attacks\" : \"0\",
	\"date_deployed\" : \"$DEPLOY_DATE\",
	\"heartbeat_status\" : \"False\",
	\"last_heard\" : \"$DEPLOY_DATE\",
	\"token\" : \"$TOKEN\"
}" http://$SERVER_IP:5000/api/v1/honeynodes/

# run the setup program to install required ruby packages for sticky_elephant
gem install bundler -v 1.13
./bin/setup 

# hpfeeds config
HPF_HOST=$SERVER_IP  
HPF_PORT=$(cat /opt/honeyagent/honeyagent.conf | grep "HPFEEDS_PORT" | awk -F: '{print $2}' | xargs)
HPF_IDENT=$TOKEN
HPF_SECRET=$TOKEN

touch sticky_elephant.conf
cat > sticky_elephant.conf<<EOF
:log_path: "./sticky_elephant.log"
:port: 5432
:host: 0.0.0.0
:debug: true
:abort_on_exception: false
:use_hpf: true
:hpf_host: $HPF_HOST
:hpf_port: $HPF_PORT
:hpf_ident: $HPF_IDENT
:hpf_secret: $HPF_SECRET
EOF


chown -R sticky_elephant /opt/sticky_elephant/

# Config for supervisor
cat > /etc/supervisor/conf.d/sticky_elephant.conf <<EOF
[program:sticky_elephant]
command=/opt/sticky_elephant/bin/sticky_elephant -c /opt/sticky_elephant/sticky_elephant.conf
directory=/opt/sticky_elephant
environment=HOME="/home/sticky_elephant/"
stdout_logfile=/opt/sticky_elephant/sticky_elephant.out
stderr_logfile=/opt/sticky_elephant/sticky_elephant.err
autostart=true
autorestart=true
user=sticky_elephant
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