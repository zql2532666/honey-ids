#!/bin/bash

INTERFACE=$(basename -a /sys/class/net/e*)


set -e
set -x

#if [ $# -ne 2 ]
#    then
#        if [ $# -eq 3 ]
#          then
#            INTERFACE=$3
#          else
#            echo "Wrong number of arguments supplied."
#            echo "Usage: $0 <server_ip> <token>."
#            exit 1
#        fi

#fi

compareint=$(echo "$INTERFACE" | wc -w)


# if [ "$INTERFACE" = "e*" ] || [ "$compareint" -ne 1 ]
#    then
#        echo "No Interface selectable, please provide manually."
#        echo "Usage: $0 <server_url> <INTERFACE>"
#        exit 1
#fi


SERVER_IP=$(cat /opt/honeyagent/honeyagent.conf | grep "SERVER_IP" | awk -F: '{print $2}' | xargs)
TOKEN=$(cat /opt/honeyagent/honeyagent.conf | grep "TOKEN" | awk -F: '{print $2}' | xargs)


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
DEBIAN_FRONTEND=noninteractive apt-get -y install build-essential libpcap-dev libjansson-dev libpcre3-dev libdnet-dev libdumbnet-dev libdaq-dev flex bison python-pip git make automake libtool zlib1g-dev

# without the following 2 commands, i get this error:
# Command "python setup.py egg_info" failed with error code 1 in /tmp/pip-build-Vdd4DT/setuptools/
# solution found: https://github.com/googleapis/google-cloud-python/issues/3884
pip install --upgrade pip
pip install --upgrade setuptools


pip install --upgrade distribute
pip install virtualenv

# Install hpfeeds and required libs...

cd /tmp
rm -rf libev*
wget https://github.com/zql2532666/hpfeeds/raw/master/libev-4.15.tar.gz
tar zxvf libev-4.15.tar.gz 
cd libev-4.15
./configure && make && make install
ldconfig

cd /tmp
rm -rf hpfeeds
git clone https://github.com/zql2532666/hpfeeds.git
cd hpfeeds/appsupport/libhpfeeds
autoreconf --install
./configure && make && make install 

cd /tmp
rm -rf snort
git clone -b hpfeeds-support https://github.com/zql2532666/snort.git
export CPPFLAGS=-I/include
cd snort
./configure --prefix=/opt/snort && make && make install 


mkdir -p /opt/snort/etc /opt/snort/rules /opt/snort/lib/snort_dynamicrules /opt/snort/lib/snort_dynamicpreprocessor /var/log/snort/
cd etc
cp snort.conf classification.config reference.config threshold.conf unicode.map /opt/snort/etc/
touch  /opt/snort/rules/white_list.rules
touch  /opt/snort/rules/black_list.rules


cd /opt/snort/etc/
sed -i 's#/usr/local/#/opt/snort/#' snort.conf 

sed -i -r 's,include \$RULE_PATH/(.*),# include $RULE_PATH/\1,' snort.conf

sed -i 's,# include $RULE_PATH/local.rules,include $RULE_PATH/local.rules,' snort.conf

# enable hpfeeds
HPF_HOST=$SERVER_IP
HPF_PORT=$(cat /opt/honeyagent/honeyagent.conf | grep "HPFEEDS_PORT" | awk -F: '{print $2}' | xargs)
HPF_IDENT=$TOKEN
HPF_SECRET=$TOKEN

sed -i "s/# hpfeeds/# hpfeeds\noutput log_hpfeeds: host $HPF_HOST, ident $HPF_IDENT, secret $HPF_SECRET, channel snort.alerts, port $HPF_PORT/" snort.conf 


#Set HOME_NET
IP=$(ip -f inet -o addr show $INTERFACE|head -n 1|cut -d\  -f 7 | cut -d/ -f 1)
sed -i "/ipvar HOME_NET/c\ipvar HOME_NET $IP" /opt/snort/etc/snort.conf


# Installing snort rules.
# honeyids.rules will be used as local.rules.
rm -f /etc/snort/rules/local.rules
ln -s /opt/honeyids/rules/honeyids.rules /opt/snort/rules/local.rules

# Supervisor will manage snort-hpfeeds
apt-get install -y supervisor

# Config for supervisor.
cat > /etc/supervisor/conf.d/snort.conf <<EOF
[program:snort]
command=/opt/snort/bin/snort -c /opt/snort/etc/snort.conf -i $INTERFACE
directory=/opt/snort
stdout_logfile=/var/log/snort.log
stderr_logfile=/var/log/snort.err
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
EOF


# Creating a script to download snort rules from the main server
# A cron job is set up ro run this script daily so that if the rules are updated on the server's end, it will also be updated here
# wget url to be replaced by main server's url
cat > /etc/cron.daily/update_snort_rules.sh <<EOF
#!/bin/bash
mkdir -p /opt/honeyids/rules
rm -f /opt/honeyids/rules/honeyids.rules.tmp
echo "[`date`] Updating snort signatures ..."
wget https://github.com/zql2532666/snort/raw/master/honeyids.rules -O /opt/honeyids/rules/honeyids.rules.tmp && \
  mv /opt/honeyids/rules/honeyids.rules.tmp /opt/honeyids/rules/honeyids.rules && \
  (supervisorctl update ; supervisorctl restart snort ) && \
	echo "[`date`] Successfully updated snort signatures" && \
	exit 0
echo "[`date`] Failed to update snort signatures"
exit 1
EOF

chmod 755 /etc/cron.daily/update_snort_rules.sh
/etc/cron.daily/update_snort_rules.sh


supervisorctl update