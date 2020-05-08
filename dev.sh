#!/bin/sh

command -v minikube >/dev/null 2>&1 || { echo >&2 "minikube not found, aborting..."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo >&2 "kubectl not found, aborting..."; exit 1; }
command -v helm >/dev/null 2>&1 || { echo >&2 "helm not found, aborting..."; exit 1; }

minikube start

# Make use of the minikube Docker environment
eval $(minikube docker-env)
docker build -t payment-service -f Dockerfile ./payment-service
docker build -t stock-service -f Dockerfile ./stock-service

helm repo add bitnami https://charts.bitnami.com/bitnami

helm install postgresql --set postgresqlPassword=servicedev bitnami/postgresql

sleep 20

kubectl run postgresql-client --rm --tty -i --restart='Never' --namespace default --image bitnami/postgresql \
  --env="PGPASSWORD=servicedev" --command -- psql --host postgresql -U postgres -d postgres -p 5432 \
  -c "create database \"payment-service\"" -c "create database \"stock-service\"" \
  -c "create database \"order-service\"" -c "create database \"user-service\""

kubectl apply -f payment-service/k8s/dev-deployment-psql.yaml
kubectl apply -f stock-service/k8s/dev-deployment-psql.yaml

