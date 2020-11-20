#!/bin/bash

set -e
set -x

if [ $# -ne 1 ]
    then
        echo "Wrong number of arguments supplied."
        echo "Usage: $0 <server_url>"
        exit 1
fi

server_url=$1
#deploy_key=$2

apt-get update
apt-get -y install git golang supervisor


# Get the elastichoney source
cd /opt
git clone https://github.com/pwnlandia/elastichoney.git
cd elastichoney

export GOPATH=/opt/elastichoney
go get || true
go build

# Register the sensor with the MHN server.
#wget $server_url/static/registration.txt -O registration.sh
#chmod 755 registration.sh
# Note: this will export the HPF_* variables
#. ./registration.sh $server_url $deploy_key "elastichoney"

# hardcoded variables for testing. to be read from honeyagent config file in future
HPF_HOST=$1     # same as server url for now
HPF_PORT=10000
HPF_IDENT="elastichoney"
HPF_SECRET="elastichoney"

cat > config.json<<EOF
{
    "logfile" : "/opt/elastichoney/elastichoney.log",
    "use_remote" : false,
    "hpfeeds": {
        "enabled": true,
        "host": "$HPF_HOST",
        "port": $HPF_PORT,
        "ident": "$HPF_IDENT",
        "secret": "$HPF_SECRET",
        "channel": "elastichoney.events"
    },
    "instance_name" : "Green Goblin",
    "anonymous" : false,
    "spoofed_version"  : "1.4.1",
    "public_ip_url": "http://icanhazip.com"
}
EOF

# Config for supervisor.
cat > /etc/supervisor/conf.d/elastichoney.conf <<EOF
[program:elastichoney]
command=/opt/elastichoney/elastichoney
directory=/opt/elastichoney
stdout_logfile=/opt/elastichoney/elastichoney.out
stderr_logfile=/opt/elastichoney/elastichoney.err
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
EOF

supervisorctl update