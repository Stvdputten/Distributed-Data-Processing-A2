#!/usr/bin/bash
kubectl delete -f cassandra-statefulset.yaml -f local-volumes.yaml -f cassandra-service.yaml
kubectl get all
