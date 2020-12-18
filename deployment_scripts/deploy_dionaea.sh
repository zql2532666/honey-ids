#!/bin/bash

set -e
set -x

if [ $# -ne 1 ]
    then
        echo "Wrong number of arguments supplied."
        echo "Usage: $0 <server_url>."
        exit 1
fi

server_url=$1

# IP_ADDR=$(ip addr show dev ens33 | grep "inet" | awk 'NR==1{print $2}' | cut -d '/' -f 1)
# SUBNET=$(ip route | grep "src $IP_ADDR" | awk '{print $1}')
# DEPLOY_DATE=$(date +"%Y-%m-%d %T")
# TOKEN="38ab1b88-2c68-457c-914e-076c66eae0d4"

# Install dependencies
apt update
apt --yes install \
    git \
    supervisor \
    build-essential \
    cmake \
    check \
    cython3 \
    libcurl4-openssl-dev \
    libemu-dev \
    libev-dev \
    libglib2.0-dev \
    libloudmouth1-dev \
    libnetfilter-queue-dev \
    libnl-3-dev \
    libpcap-dev \
    libssl-dev \
    libtool \
    libudns-dev \
    python3 \
    python3-dev \
    python3-bson \
    python3-yaml \
    python3-boto3 

git clone https://github.com/DinoTools/dionaea.git 
cd dionaea

# Latest tested version with this install script
git checkout baf25d6

mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX:PATH=/opt/dionaea ..

make
make install

#wget $server_url/static/registration.txt -O registration.sh
#chmod 755 registration.sh
# Note: this will export the HPF_* variables
#. ./registration.sh $server_url $deploy_key "dionaea"


HPF_HOST=$1
HPF_PORT=10000
HPF_IDENT="dionaea"
HPF_SECRET="dionaea"
cat > /opt/dionaea/etc/dionaea/ihandlers-enabled/hpfeeds.yaml <<EOF
- name: hpfeeds
  config:
    # fqdn/ip and port of the hpfeeds broker
    server: "$HPF_HOST"
    port: $HPF_PORT
    ident: "$HPF_IDENT"
    secret: "$HPF_SECRET"
    # dynip_resolve: enable to lookup the sensor ip through a webservice
    dynip_resolve: "http://canhazip.com/"
    # Try to reconnect after N seconds if disconnected from hpfeeds broker
    # reconnect_timeout: 10.0
EOF


# Editing configuration for Dionaea.
mkdir -p /opt/dionaea/var/log/dionaea/wwwroot /opt/dionaea/var/log/dionaea/binaries /opt/dionaea/var/log/dionaea/log
chown -R nobody:nogroup /opt/dionaea/var/log/dionaea

mkdir -p /opt/dionaea/var/log/dionaea/bistreams 
chown nobody:nogroup /opt/dionaea/var/log/dionaea/bistreams

# Config for supervisor.
cat > /etc/supervisor/conf.d/dionaea.conf <<EOF
[program:dionaea]
command=/opt/dionaea/bin/dionaea -c /opt/dionaea/etc/dionaea/dionaea.cfg
directory=/opt/dionaea/
stdout_logfile=/opt/dionaea/var/log/dionaea.out
stderr_logfile=/opt/dionaea/var/log/dionaea.err
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
EOF

supervisorctl update