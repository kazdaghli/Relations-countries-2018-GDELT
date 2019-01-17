#!/usr/bin/env bash

# Before running this script, please update the following variables to match your EMR environment

# Encryption key used to connect to the cluster
encryption_key="gdeltKeyPair"
# Master and Slave security group "sg-XXXXXXXXXXXX" - go check "Groupes de sécurité", "Security Groups" 
# more precisely ElasticMapReduce-master and ElasticMapReduce-master
master_security_group="sg-0cb7def3aa626f061"
slave_security_group="sg-0f76538ec27300067"
# Put one of the subnets in your VPC
subnet_id="subnet-eeec77b2"
# Name your cluster
cluster_name="GDELT Cluster"
# Instance type, visit https://aws.amazon.com/fr/ec2/previous-generation/ and https://aws.amazon.com/fr/ec2/instance-types/ for more details
instance_type="m1.large"
# Number of slave nodes
slave_nodes="4"
# S3 Bucket where the scripts are
s3_path="s3://thelembucket/"


bootstrap_path="${s3_path}bootstrap_cassandra.sh"
aws emr create-cluster --service-role EMR_DefaultRole \
                       --auto-scaling-role EMR_AutoScaling_DefaultRole \
                       --configurations file://spark-config.json\
                       --ec2-attributes KeyName=${encryption_key},InstanceProfile=EMR_EC2_DefaultRole,EmrManagedMasterSecurityGroup=${master_security_group},EmrManagedSlaveSecurityGroup=${slave_security_group},SubnetId=${subnet_id} \
					   --name "${cluster_name}" \
					   --applications Name=Spark Name=Zookeeper Name=Ganglia Name=Zeppelin \
					   --release-label emr-5.19.0 \
					   --instance-groups InstanceGroupType=MASTER,InstanceCount=1,InstanceType=${instance_type} InstanceGroupType=CORE,InstanceCount=${slave_nodes},InstanceType=${instance_type} \
					   --bootstrap-actions Path=${bootstrap_path},Name=BootstrapCassandra
