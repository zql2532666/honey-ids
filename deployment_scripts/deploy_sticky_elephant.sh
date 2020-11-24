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

# install ruby 2.4, default version on ubuntu 16.04 is 2.3, which is not compatible with some packages used by sticky_elephant
apt-get install -y software-properties-common
apt-add-repository -y ppa:brightbox/ruby-ng
apt-get update
apt-get install -y ruby2.4 ruby2.4-dev

# install git and supervisor
apt-get -y install git supervisor

useradd -d /home/sticky_elephant -m sticky_elephant

# Get the sticky_elephant source
cd /opt
git clone https://github.com/zql2532666/sticky_elephant.git sticky_elephant
cd sticky_elephant

# run the setup program to install required ruby packages for sticky_elephant
gem install bundler -v 1.13
./bin/setup 

# hardcoded variables for testing. to be read from honeyagent config file in future
HPF_HOST=$1     # same as server url for now
HPF_PORT=10000
HPF_IDENT="sticky_elephant"
HPF_SECRET="sticky_elephant"

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

supervisorctl update