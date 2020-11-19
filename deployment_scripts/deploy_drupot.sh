#!/bin/bash

#!!! NOTE: drupot will not work if no hpfeeds configuration is in the config file
# it will also terminate immediately if it cannot reach the hpfeeds broker

set -e
set -x

if [ $# -ne 1 ]
    then
        echo "Wrong number of arguments supplied."
        echo "Usage: $0 <server_url>."
        exit 1
fi

server_url=$1

apt-get update
apt-get -y install git supervisor

####################################################################
# Install a decent version of golang

cd /usr/local/
wget https://dl.google.com/go/go1.15.2.linux-amd64.tar.gz 
tar zxf go1.15.2.linux-amd64.tar.gz && rm go1.15.2.linux-amd64.tar.gz 
####################################################################

export GO111MODULE=on

# Get the drupot source
cd /opt
git clone https://github.com/d1str0/drupot.git
cd drupot
git checkout v0.2.4

/usr/local/go/bin/go build

# Register the sensor with the MHN server.
#wget $server_url/static/registration.txt -O registration.sh
#chmod 755 registration.sh
# Note: this will export the HPF_* variables
#. ./registration.sh $server_url $deploy_key "agave"


# hardcoded variables for testing. to be read from honeyagent config file in future
$HPF_HOST="192.168.148.146"
$HPF_PORT=10000
$HPF_IDENT="test"
$HPF_SECRET="test"

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

supervisorctl update
supervisorctl restart all