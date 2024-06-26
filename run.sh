#!/bin/bash

# Create all the needed namespaces
for ns in observability health-check-service consumer-health-check-service kafka nginx; do
  kubectl create ns "$ns" || true
done

# Deploy Kafka cluster and create a topic called "health_checks_topic"
kubectl apply -f kafka/. -n kafka
echo "Waiting for Kafka cluster to be ready before continuing..."
kubectl wait --for=condition=Ready pod -l service=kafka -n kafka --timeout=60s
echo -e "Kafka cluster created.\nWaiting 15s to allow the Kafka cluster to fully initialize"
sleep 15
echo -e "Done.\nCreating Kafka topic health_check_topic"
kubectl exec kafka-0 -- kafka-topics.sh --bootstrap-server kafka:29092 --topic health_checks_topic --create --partitions 3 --replication-factor 3

# Deploy the Python services
kubectl apply -f health-check-service/manifests/. -n health-check-service
kubectl apply -f consumer-health-check-service/manifests/. -n consumer-health-check-service

# Deploy Nginx
kubectl apply -f nginx/. -n nginx

# Add Prometheus and Grafana repos for Helm
helm repo add prometheus https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Grafana with custom values.yaml
helm install grafana grafana/grafana -f observability/grafana/values.yaml -n observability

# Install Prometheus with custom values.yaml
helm install prometheus prometheus-community/prometheus -f observability/prometheus/values.yaml -n observability