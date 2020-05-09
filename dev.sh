#!/bin/sh

command -v minikube >/dev/null 2>&1 || { echo >&2 "minikube not found, aborting..."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo >&2 "kubectl not found, aborting..."; exit 1; }
command -v helm >/dev/null 2>&1 || { echo >&2 "helm not found, aborting..."; exit 1; }

minikube start

# Make use of the minikube Docker environment
eval $(minikube docker-env)
docker build -t payment-service -f Dockerfile ./payment-service
docker build --cache-from payment-service -t stock-service -f Dockerfile ./stock-service

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add traefik https://containous.github.io/traefik-helm-chart
helm repo update

helm install postgresql --set postgresqlPassword=servicedev bitnami/postgresql
helm install cassandra --set dbUser.password=servicedev bitnami/cassandra
helm install traefik traefik/traefik 

# Give the databases some time to start
sleep 20

# Add databases for the different services
kubectl run postgresql-client --rm --tty -i --restart='Never' --namespace default --image bitnami/postgresql \
  --env="PGPASSWORD=servicedev" --command -- psql --host postgresql -U postgres -d postgres -p 5432 \
  -c "create database payment_service" -c "create database stock_service" \
  -c "create database order_service" -c "create database user_service"

# Deploy the PostgreSQL dev version of the services
kubectl apply -f payment-service/k8s/dev-deployment-psql.yaml
kubectl apply -f stock-service/k8s/dev-deployment-psql.yaml

# Deploy the Cassandra dev version of the services
kubectl apply -f payment-service/k8s/dev-deployment-cass.yaml
kubectl apply -f stock-service/k8s/dev-deployment-cass.yaml

