# Code tested on Ubuntu 18.04.
import os
import json
import paramiko
import time


# Conf variables
link_key = "gdeltKeyPair.pem"

# Liste of interfaces
print("------------------------------------------------------")
print("Importing Interfaces")
print("------------------------------------------------------")
os.system("aws ec2 describe-network-interfaces > interfaces.json")
print("Interfaces Imported")
print("------------------------------------------------------")
# Read interfaces.json file
json_file = open("interfaces.json")
interfaces_json = json.load(json_file)
interfaces = interfaces_json['NetworkInterfaces']
card_interfaces = len(interfaces)

nodes = []
slave_nodes = []
seeds_nodes = []
card_seeds = 0
max_seeds = 1 if card_interfaces <= 3 else 2

for interface in interfaces:
	is_seed = False
	is_slave = True
	dns = interface['Association']['PublicDnsName']
	private_IPv4 = interface['PrivateIpAddress']
	groups = interface['Groups']

	for group in groups:
		group_name = group['GroupName']

		if 'master' in group_name:
			is_slave = False

	if is_slave and (card_seeds < max_seeds):
		is_seed = True
		card_seeds += 1
		seeds_nodes.append(private_IPv4)

	if is_slave:
		slave_nodes.append(private_IPv4)

	node = {
		'p_IPv4': private_IPv4,
		'is_slave': is_slave,
		'dns': dns,
		'is_seed':  is_seed,
	}
	nodes.append(node)

json_file.close()

print("Nodes distribution has been created")
print("------------------------------------------------------")
print("Starting Configuration")
print("------------------------------------------------------")


def command_status(exit_status, message):
	if exit_status == 0:
		print (message)
	else:
		print("Error", exit_status)
	print("------------------------------------------------------")


k = paramiko.RSAKey.from_private_key_file(link_key)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())


for node in nodes:
	is_slave = node['is_slave']
	is_seed = node['is_seed']
	dns = node['dns']
	print("Connecting to a is_slave {} at public DNS '{}' (is_seed: {})".format(is_slave, dns, is_seed))
	print("------------------------------------------------------")
	c.connect( hostname = dns, username = "hadoop", pkey=k)
	print("Connected!")
	print("------------------------------------------------------")

	if is_slave:
		seeds_command = "sudo sed -i 's/seeds:.*/seeds: \"{}\"/g' /etc/cassandra/conf/cassandra.yaml".format(",".join(seeds_nodes))
		bootstrap_command = "sudo sed -i 's/auto_bootstrap:.*/auto_bootstrap: true/g' /etc/cassandra/conf/cassandra.yaml"
		stdin, stdout, stderr = c.exec_command(seeds_command)
		exit_status = stdout.channel.recv_exit_status()
		command_status(exit_status, "Seeds has been added to {}".format(dns))

		if not is_seed:
			stdin, stdout, stderr = c.exec_command(bootstrap_command)
			exit_status = stdout.channel.recv_exit_status()
			command_status(exit_status, "Auto Bootstrap true fixed")
		
		stdin, stdout, stderr = c.exec_command("sudo service cassandra start")
		exit_status = stdout.channel.recv_exit_status()
		command_status(exit_status, "Starting Cassandra")
		print("Now a 10s delay to not Rush Cassandra configuration")
		print("------------------------------------------------------")
		time.sleep(10)

	else:
		spark_new_line = "spark.cassandra.connection.host  {}".format(",".join(slave_nodes))
		command = "sudo echo '{}' | sudo tee -a /etc/spark/conf/spark-defaults.conf".format(spark_new_line)
		stdin, stdout, stderr = c.exec_command(command)
		exit_status = stdout.channel.recv_exit_status()
		command_status(exit_status, "Cassandra hosts has been added to Spark")

		restarting_system = [
			"sudo stop hadoop-yarn-resourcemanager",
			"sudo start hadoop-yarn-resourcemanager", 
			"sudo stop zeppelin",
			"sudo start zeppelin"
			]

		for cmd in restarting_system:
			stdin, stdout, stderr = c.exec_command(cmd)
			exit_status = stdout.channel.recv_exit_status()
			command_status(exit_status, "Restarting action done")

	c.close()

print("Making sure all Cassandra nodes are up and running!")
print("------------------------------------------------------")
print("Now a 30 s delay to make sure Cassandra nodes status are accurate")
print("------------------------------------------------------")
time.sleep(10)
# Some cassandra nodes may not start after configuration
# Make sure all cassandra nodes are up and running
for node in nodes:
	is_slave = node['is_slave']
	dns = node['dns']
	if is_slave:
		print("Connecting to Slave with public DNS '{}'".format(dns))
		print("------------------------------------------------------")
		c.connect( hostname = dns, username = "hadoop", pkey=k)
		print("Connected!")
		print("------------------------------------------------------")
		stdin, stdout, stderr = c.exec_command("sudo service cassandra status")
		exit_status = stdout.channel.recv_exit_status()
		command_status(exit_status, "Cassandra Status")
		response = "".join(stdout.readlines())
		if "running" in response:
			print("Cassandra is running, nothing to do here.")
			print("------------------------------------------------------")
		elif "dead" in response:
			print("Cassandra is dead in this node, needs to restart the service")
			print("------------------------------------------------------")
			stdin, cstdout, stderr = c.exec_command("sudo service cassandra restart")
			exit_status = cstdout.channel.recv_exit_status()
			command_status(exit_status, "Cassandra Restarted with message ===> {}".format(cstdout.readlines()))
		elif "stopped" in response:
			print("Cassandra was stopped!")
			print("------------------------------------------------------")
	c.close()


print("Configuration Finished!")