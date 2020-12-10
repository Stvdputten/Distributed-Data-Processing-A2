#!/usr/bin/bash
kubectl apply -f cassandra-service.yaml
kubectl apply -f local-volumes.yaml
kubectl apply -f cassandra-statefulset.yaml
kubectl get pods
kubectl get services
