#!/bin/bash

set -e
set -x

if [ $# -ne 1 ]
    then
        echo "Wrong number of arguments supplied."
        echo "Usage: $0 <server_url>"
        exit 1
fi

apt-get update
apt-get install -y python

server_url=$1

apt-get update
apt-get -y install python-dev git openssh-server supervisor authbind openssl python-virtualenv build-essential python-gmpy2 libgmp-dev libmpfr-dev libmpc-dev libssl-dev python-pip libffi-dev

pip install -U supervisor
/etc/init.d/supervisor start || true

sed -i 's/#Port/Port/g' /etc/ssh/sshd_config
sed -i 's/Port 22$/Port 2222/g' /etc/ssh/sshd_config
service ssh restart
useradd -d /home/cowrie -s /bin/bash -m cowrie -g users

cd /opt
git clone https://github.com/zql2532666/cowrie.git cowrie
cd cowrie

# Most recent known working version
git checkout 34f8464

# Config for requirements.txt
cat > /opt/cowrie/requirements.txt <<EOF
twisted>=17.1.0
cryptography>=2.1
configparser
pyopenssl
pyparsing
packaging
appdirs>=1.4.0
pyasn1_modules
attrs
service_identity
python-dateutil
tftpy
bcrypt
EOF


virtualenv cowrie-env #env name has changed to cowrie-env on latest version of cowrie
source cowrie-env/bin/activate

# without the following 2 commands, i get this error:  ---by rongtao
# ERROR: Package 'setuptools' requires a different Python: 2.7.12 not in '>=3.5'
# Solution reference: https://blog.csdn.net/weixin_43350700/article/details/104597730
pip uninstall -y setuptools
pip install setuptools==44.0.0

# without the following, i get this error:   --- by mhn developer
# Could not find a version that satisfies the requirement csirtgsdk (from -r requirements.txt (line 10)) (from versions: 0.0.0a5, 0.0.0a6, 0.0.0a5.linux-x86_64, 0.0.0a6.linux-x86_64, 0.0.0a3)
pip install csirtgsdk==0.0.0a6
pip install -r requirements.txt 


# Register honey node with main server. !!!!!!!!!!!!!!!!!! TO BE DONE USING HONEYAGENT

# TODO:
# 1. download honeyagent scripts from main server
# 2. generate honeyagent config file
# 3. configure honeyagent as service
# 4. start honeyagent


# cowrie configuration
cd etc
cp cowrie.cfg.dist cowrie.cfg
sed -i 's/hostname = svr04/hostname = server/g' cowrie.cfg
sed -i 's/listen_endpoints = tcp:2222:interface=0.0.0.0/listen_endpoints = tcp:22:interface=0.0.0.0/g' cowrie.cfg
sed -i 's/version = SSH-2.0-OpenSSH_6.0p1 Debian-4+deb7u2/version = SSH-2.0-OpenSSH_6.7p1 Ubuntu-5ubuntu1.3/g' cowrie.cfg


# HPFEEDS CONFIG !!!!!!!!!!!!!!! TO BE DONE
# sed -i 's/#\[output_hpfeeds\]/[output_hpfeeds]/g' cowrie.cfg
# sed -i '/\[output_hpfeeds\]/!b;n;cenabled = true' cowrie.cfg
# sed -i "s/#server = hpfeeds.mysite.org/server = $HPF_HOST/g" cowrie.cfg
# sed -i "s/#port = 10000/port = $HPF_PORT/g" cowrie.cfg
# sed -i "s/#identifier = abc123/identifier = $HPF_IDENT/g" cowrie.cfg
# sed -i "s/#secret = secret/secret = $HPF_SECRET/g" cowrie.cfg


sed -i 's/#debug=false/debug=false/' cowrie.cfg
cd ..

chown -R cowrie:users /opt/cowrie/
touch /etc/authbind/byport/22
chown cowrie /etc/authbind/byport/22
chmod 770 /etc/authbind/byport/22


# start.sh is deprecated on new Cowrie version and substituted by "bin/cowrie [start/stop/status]"
sed -i 's/AUTHBIND_ENABLED=no/AUTHBIND_ENABLED=yes/' bin/cowrie
sed -i 's/DAEMONIZE=""/DAEMONIZE="-n"/' bin/cowrie


# Config for supervisor
cat > /etc/supervisor/conf.d/cowrie.conf <<EOF
[program:cowrie]
command=/opt/cowrie/bin/cowrie start
directory=/opt/cowrie
stdout_logfile=/opt/cowrie/var/log/cowrie/cowrie.out
stderr_logfile=/opt/cowrie/var/log/cowrie/cowrie.err
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
user=cowrie
EOF

supervisorctl update