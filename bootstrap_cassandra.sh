#!/usr/bin/env bash

# Create useful functions
is_master() {
    if [ $(jq '.isMaster' /mnt/var/lib/info/instance.json) = 'true' ]; then
        return 0
    else
        return 1
    fi
}


# The EMR customize hooks run _before_ everything else, so Hadoop is not yet ready
THIS_SCRIPT="$(realpath "${BASH_SOURCE[0]}")"
RUN_FLAG="${THIS_SCRIPT}.run"
# On first boot skip past this script to allow EMR to set up the environment. Set a callback
# which will poll for availability of HDFS and then install Accumulo and then GeoWave
if [ ! -f "$RUN_FLAG" ]; then
	touch "$RUN_FLAG"
	TIMEOUT= is_master && TIMEOUT=3 || TIMEOUT=4
	echo "bash -x $(realpath "${BASH_SOURCE[0]}") > /tmp/cassandra-install.log" | at now + $TIMEOUT min
	exit 0 # Bail and let EMR finish initializing
fi

# Bootstrap a Cassandra cluster node
#

cat << EOF > /tmp/cassandra.repo
[cassandra]
name=Apache Cassandra
baseurl=https://www.apache.org/dist/cassandra/redhat/311x/
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://www.apache.org/dist/cassandra/KEYS
EOF

if is_master; then
	echo "no cassandra on master"
else
	sudo mv /tmp/cassandra.repo /etc/yum.repos.d/cassandra.repo
	sudo mkdir -p /mnt/cassandra/data
	sudo chmod 777 -R /mnt/cassandra
	sudo yum -y install cassandra
	LOCAL_IP=$(curl http://169.254.169.254/latest/meta-data/local-ipv4)
	sudo chmod 777 /etc/cassandra/conf/cassandra.yaml
	echo "auto_bootstrap: false" >> /etc/cassandra/conf/cassandra.yaml
	sudo sed -i 's/listen_address:.*/listen_address: '${LOCAL_IP}'/g' /etc/cassandra/conf/cassandra.yaml
	sudo sed -i 's/rpc_address:.*/rpc_address: '${LOCAL_IP}'/g' /etc/cassandra/conf/cassandra.yaml
	sudo sed -i 's/endpoint_snitch:.*/endpoint_snitch: Ec2Snitch/g' /etc/cassandra/conf/cassandra.yaml
	sudo sed -i 's/start_rpc:.*/start_rpc: true/g' /etc/cassandra/conf/cassandra.yaml
	sudo sed -i 's!/var/lib/cassandra/data!/mnt/cassandra/data!g' /etc/cassandra/conf/cassandra.yaml
fi
