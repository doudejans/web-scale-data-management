# Web Scala Data Management Project
*Project work for IN4331 Web-scale Data Management.*

The project is defined as 4 microservices which together make up the
functionality of a simple order system.

The goal of the project is to compare
[Cassandra](https://cassandra.apache.org) (a wide-column database) against
[Postgres](https://www.postgresql.org) (Relational Database) with regards to
performance, scalability and consistency.

## Installation
- Make sure you have Python 3 installed (specifically tested with
`v3.8`).
- `Optional` Create a
[virtualenv](https://docs.python.org/3/library/venv.html) by running
the following command:

  `python3 -m venv .venv`

  And activate it by running

  `source .venv/bin/activate`

  In case you are developing in an IDE like PyCharm you might have to point it 
  to the virtual environment (it usually does this by itself though). You can
  do this by:
   - Opening the editor preferences
   - Go to the tab `Project: web-scale-data-management` (the name of the
   project might differ if you placed the project in a different folder)
   - Click `Python Interpreter`
   - Select the correct virtual env in the list (by looking at the directory in
  which they are placed)
   - if it is not there you can use the gear icon in the top right and press `add` -> given that you followed the instructions below you can add an `Existing environment` and point it to the folder where
  you created the environment.

- Install the requirements defined in the `requirements.txt` by running:

  `python3 -m pip install -r requirements.txt`.

## Deploying locally

If you want to deploy the full system locally, you will need [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/), [Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) and [Helm](https://helm.sh).

To deploy the application in a full environment, run:

`./setup_minikube.sh`

This will start a Minikube cluster with PostgreSQL, Cassandra and Traefik (using Helm) and two versions of all microservices: a version using the PostgreSQL backend and a version using the Cassandra backend.
Traefik manages the routing to the different microservices.
In order to be able to access Traefik through Minikube, you can run the following command, which will assign an external IP to the `LoadBalancer` service for Traefik:

`minikube tunnel`

Then, you can look up the IP address using:

```
$ kubectl get svc traefik
NAME      TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)                      AGE
traefik   LoadBalancer   10.96.184.178   10.96.184.178   80:31719/TCP,443:31081/TCP   1m
```

As mentioned before, both PostgreSQL and Cassandra versions of the microservices are deployed.
To access the PostgreSQL microservice versions `/postgres` needs to be prefixed in the url.
For example, `/payment/health` will return `{"database":"CASSANDRA","status":"ok"}` and `/postgres/payment/health` will return `{"database":"POSTGRES","status":"ok"}`.

Another option would be to map port 8000 using `kubectl`, which you can then use to access the services through `localhost:8000`:

`kubectl port-forward $(kubectl get pods --selector "app.kubernetes.io/name=traefik" --output=name) 8000:8000`

The above command can also be used to expose the Traefik dashboard, which can be accessed through port 9000.

`minikube stop` stops the cluster but saves the state, and `minikube delete` deletes the entire cluster.

## Deploying in production

Assuming that you have a Kubernetes cluster up and running and [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) and [Helm](https://helm.sh) ready, you will need to take the following actions:

1. Add the required Helm repos:

    ```shell
    helm repo add traefik https://containous.github.io/traefik-helm-chart
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
    ```

2. Add the Traefik Ingress Controller:

    ```shell
    helm install traefik traefik/traefik
    ```

3. Add a Cassandra instance:

    ```shell
    helm install cassandra bitnami/cassandra
    ```

4. Add a PostgreSQL instance:

    ```shell
    helm install postgresql bitnami/postgresql
    ```

5. Add the databases for the microservices:

    ```shell
    export POSTGRES_PASSWORD=$(kubectl get secret --namespace default postgresql -o jsonpath="{.data.postgresql-password}" | base64 --decode)

    kubectl run postgresql-client --rm --tty -i --restart='Never' --namespace default --image bitnami/postgresql \
    --env="PGPASSWORD=$POSTGRES_PASSWORD" --command -- psql --host postgresql -U postgres -d postgres -p 5432 \
    -c "create database payment_service" -c "create database stock_service" \
    -c "create database order_service" -c "create database user_service"
    ```

6. Deploy the microservices:

    ```shell
    kubectl apply -f order-service/k8s/deployment-cass.yaml
    kubectl apply -f order-service/k8s/deployment-psql.yaml
    ...
    kubectl apply -f user-service/k8s/deployment-cass.yaml
    kubectl apply -f user-service/k8s/deployment-psql.yaml
    ```

7. Check the status:

    ```shell
    kubectl get pods
    kubectl get service
    ```

That should be all! Traefik should automatically detect the `IngressRoute` specifications in the deployment files.
The microservices get the password for the databases through Kubernetes Secrets and connect to the databases through the services that are deployed by the Helm charts.

### Scaling

For scaling the Cassandra deployment to make use of replication, you can use:

```shell
helm upgrade --set cluster.replicaCount=2,cluster.seedCount=2 cassandra bitnami/cassandra
```

For replicating the microservices, you should edit and re-apply the deployment configuration files, e.g.:

```yaml
spec:
  selector:
    matchLabels:
      app: user-service-cass
  replicas: 2
```
