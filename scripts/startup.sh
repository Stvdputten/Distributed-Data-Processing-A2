#!/usr/bin/bash
kubectl apply -f cassandra-service.yaml -f local-volumes.yaml -f cassandra-statefulset.yaml
kubectl get all
