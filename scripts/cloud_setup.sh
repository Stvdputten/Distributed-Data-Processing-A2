#!/usr/bin/bash
# AWS
export KOPS_STATE_STORE=s3://test-bucket-dps
kops create cluster \
--name=dps.cluster.k8s.local \
--state=s3://test-bucket-dps \
--cloud=aws \
--master-size=t2.micro \
--master-count=1 \
--master-zones=us-east-1a \
--node-size=t2.micro \
--node-count=3 \
--zones=us-east-1a \
--yes

# GCE
#export KOPS_STATE_STORE=gs://kubernetes-cluster-kops-ddps/
#PROJECT=`gcloud config get-value project`
#export KOPS_FEATURE_FLAGS=AlphaAllowGCE # to unlock the GCE features
#kops create cluster simple.k8s.local \
#--zones europe-west4-b \
#--master-size n1-standard-1 \
#--node-size n1-standard-1 \
#--node-count 3 \
#--state ${KOPS_STATE_STORE}/ --project=${PROJECT}

#kops delete cluster dps.cluster.k8s.local --yes
