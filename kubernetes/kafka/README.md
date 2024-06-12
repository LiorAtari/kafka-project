# https://phoenixnap.com/kb/kafka-on-kubernetes

To deploy Kafka on the K8s cluster:
```sh
cd kubernetes/kafka-manifests/
kubectl apply -f .
```

To create the `health_checks_topic` topic on kafka, connect to one of the kafka statefulset pods:
```
kubectl exec -it pod/kafka-0 -- /bin/bash
```
And run the following command:
```
kafka-topics.sh --bootstrap-server kafka:29092 --topic health_checks_topic --create --partitions 3 --replication-factor 3
```
This will connect to the kafka service on port 29092, create the topic with 3 partitions and 3 replication factors.