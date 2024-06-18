import time
import requests
import json
from datetime import datetime
from flask import Flask, jsonify
from kafka import KafkaProducer, KafkaConsumer
from threading import Thread
from prometheus_flask_exporter import PrometheusMetrics

# Setting variables for Kafka server address + name of the Kafka topic
KAFKA_SERVER = 'kafka.kafka.svc.cluster.local:29092'
KAFKA_TOPIC = 'health_checks_topic'

# Setting up the Kafka producer info
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Setting up Kafka consumer info
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='health-check-consumer-group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

# Flask application setup with PrometheusMetrics
app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Global variable to store the latest status
latest_status = {}

# Function to retrieve the health status from Kafka
@app.route('/check_health', methods=['GET'])
def get_health():
    global latest_status
    return jsonify(latest_status)

# Background thread to consume health status from Kafka
def consume_health_status():
    global latest_status
    for message in consumer:
        latest_status = message.value
        print(f"Received kafka message: {latest_status}")

# Background thread to periodically check nginx health status
def check_health():
    service_name = 'nginx'
    url = 'http://nginx-service.nginx.svc.cluster.local:80'
    while True:
        try:
            response = requests.get(url)
            status = 1 if response.status_code == 200 else 0
        except requests.exceptions.RequestException:
            status = 0

        health_status = {
            "service_name": service_name,
            "status": "OK" if status else "NOT OK",
            "timeStamp": datetime.utcnow().isoformat() + "Z"
        }
        producer.send(KAFKA_TOPIC, health_status)
        producer.flush()
        time.sleep(10)

if __name__ == "__main__":
    consumer_thread = Thread(target=consume_health_status)
    consumer_thread.start()

    health_checks_thread = Thread(target=check_health)
    health_checks_thread.start()

    app.run(host='0.0.0.0', port=8080)
