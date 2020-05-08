#!/bin/sh

command -v minikube >/dev/null 2>&1 || { echo >&2 "minikube not found, aborting..."; exit 1; }

minikube start

# Make use of the minikube Docker environment
eval $(minikube docker-env)
docker build -t payment-service -f Dockerfile ./payment-service

helm repo add bitnami https://charts.bitnami.com/bitnami

helm install postgresql --set postgresqlPassword=paymentservicedev,postgresqlDatabase=payment-service bitnami/postgresql

sleep 10
kubectl apply -f payment-service/dev-deployment.yaml

