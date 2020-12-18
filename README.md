# Distributed Data Processing Systems A2

This project presents a distributed application on the DAS-5 cluster for the course DDPS (2020). This repository 
demonstrates a deployment of Apache Cassandra on a Kubernetes cluster. 

## Pre-requisites
- Docker
- Docker-compose
- Kubernetes
- Python 3.8
- [Cassandra-driver](https://pypi.org/project/cassandra-driver/)
- [kOps](https://kops.sigs.k8s.io/getting_started/install/)
- [kind](https://kind.sigs.k8s.io/) (If you want to test locally)

## Setup 

**1. Clone the repo**
```
git clone https://github.com/Stvdputten/Distributed-Data-Processing-Systems-A1.git
```

**1.5. Cloud Setup (optional)** 

Can be skipped if you already have a Kubernetes cluster setup on a cloud provider or locally. Requires at least 4 nodes.
Furthermore update the location of your s3:// bucket.

```
scripts/cloud_setup.sh # Uses kOps and AWS 
```

**2. Deployment** 

Deploys the the Cassandra cluster.

```
cd Distributed\ Data\ Processing\ A2
./scripts/startup.sh
```

**2.5 Shutdown (optional)** 

Shutdown of application.

```
./scripts/shutdown.sh
```

## Run Application
First step is to open the CassandraFileSystem.py and set the cassandra_ip to the external ip, and replace the username and password if they are not the default ones.

For a list of supported command an their function execute:
```
python application/CassandraFileSystem.py help

```
or read the help.txt.
## Run experiments
Experiments can be run if the system is online and has a public external ip to which you can connect using cqlsh from Cassandra.
Might require an update in the code of the external ip.

** Performance
Writes and reads to our database storage system.
```
python application/CassandraFileSystem.py setup
python application/CassandraFileSystem.py test [datasets] [concurrent sessions] [amount of cycles]
# example python application/CassandraFileSystem.py test datasets/1MB.epub/ 1
```

** Availability
Drops a node you can check afterwards if the system is still running.
```
# drop node
kubectl delete pod/cassandra-0 --grace-period=0 --force 

# check if files are still available
python application/CassandraFileSystem.py list_files

```

## Acknowledgements

This repository is open-source and created for the course Distributed Data Processing Systems (2020) of University Leiden.
