# Kafka-Project
This repository contains all the needed files needed to run -
- `Kafka` cluster with 3 nodes and a topic called `health_checks_topic`
- `HealthCheckService` and `ConsumerHealthCheckService` python services
- `Nginx` service for `HealthCheckService` to monitor in the cluster
- `Grafana` and `Prometheus` services for monitoring

## Getting Started
### Prerequisites
- Docker Desktop
- Minikube
- kubectl CLI
- Helm

### Installation
1. Clone the repository and navigate to it:
```sh
git clone https://github.com/LiorAtari/kafka-project.git
cd kafka-project
```
2. Grant execution permissions to the `run.sh` file:
```sh
chmod +x run.sh
```
This script will deploy all of the services to their own namespace along with everything needed for them to run.

3. Run the `run.sh` file to install all components:
```sh
./run.sh
```

You can now run this command to view the logs of the Python services:
#### NOTE - Logs for the health services might take time to appear
```sh
kubectl logs -f <pod-name> -n <namespace>
```

To browse to the UI of Grafana, run:
```sh
k port-forward svc/grafana 8080:80
```
To browse to the UI of Prometheus, run:
```sh
k port-forward svc/prometheus-server 9090:80
```
Now you can browse to `http://localhost:<8080 or 9090>` and access their UI