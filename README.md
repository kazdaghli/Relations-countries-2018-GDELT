# NoSQL_Project
GDELT NoSQL project

## Architecture

![architecture](https://github.com/sarah911/NoSQL_Project/blob/master/Data/architecture.PNG)

## Configuration Cassandra

Replication Factor = 3
Write = QUORUM(2)
Read = ONE(1)

W + R = RF
Eventual consistency  

## EMR Automation
Scripts to automate the cluster creation:
1 - bootstrap_cassandra.sh : Bootstrap cassandra on cluster creation
2 - cluster_configuration.py : Configurate the cluster (number and types of instances etc) + link to spark and cassandra
3 - create_cluster.sh : Launch to create EMR 

## Data Loading and preprocessing

# Load data 

For data with events and mentions tables : 
https://github.com/sarah911/NoSQL_Project/blob/master/2E4E4Q6WY/note.json

For data with gkg table:
https://github.com/sarah911/NoSQL_Project/blob/master/2E1J1S7FX/note.json

## Queries 

Q1: Find the number of articles and events for a triplet ( Data, Country, Language )
<img src="https://github.com/sarah911/NoSQL_Project/blob/master/Data/Q1.PNG" width="200">

Q2: Find events of an actor in the past 6 months
<img src="https://github.com/sarah911/NoSQL_Project/blob/master/Data/Q2.PNG" width="200">

Q3: Find actors with the most negative or positive views based on ( Date, Country, Language )
<img src="https://github.com/sarah911/NoSQL_Project/blob/master/Data/Q3.PNG" width="200">

Q4: Find actors, countries and organizations that divide the most given a date
<img src="https://github.com/sarah911/NoSQL_Project/blob/master/Data/Q4.PNG" width="200">

Q5: The evolution of relations between countries

Part 1: Based on actors names (Table events)
<img src="https://github.com/sarah911/NoSQL_Project/blob/master/Data/Q51.PNG" width="200">


Part 2: Based on actors countries (Table mentions)
<img src="https://github.com/sarah911/NoSQL_Project/blob/master/Data/Q52.PNG" width="200">


Part 3: Based on articles written in a country about another one (Table GKG)
<img src="https://github.com/sarah911/NoSQL_Project/blob/master/Data/Q53.PNG" width="200">


## The final presentation
![presentation]

