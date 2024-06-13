import time
import requests
import json
from datetime import datetime
from flask import Flask, jsonify
from kafka import KafkaProducer, KafkaConsumer
from threading import Thread, Event

# Setting variables for Kafka server address + name of the Kafka topic
KAFKA_SERVER = 'kafka.kafka.svc.cluster.local:29092'
KAFKA_TOPIC = 'health_check_topic'

# Setting up the Kafka producer info
producer = KafkaProducer(
    bootstrap_servers = KAFKA_SERVER,
    value_serializer = lambda v: json.dumps(v).encode('utf-8')
)
# Setting up Kafka consumer info
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers = KAFKA_SERVER,
    auto_offset_reset = 'latest',
    enable_auto_commit = True,
    group_id = 'health-check-consumer-group',
    value_deserializer = lambda v: json.loads(v.decode('utf-8'))
)
# Flask application setup
app = Flask(__name__)
latest_status = {}
health_check_event = Event()

# Function to retrieve the health status from nginx server
def check_health():
    global latest_status
    service_name = 'nginx'
    url = 'http://nginx-service.nginx.svc.cluster.local:80'

    # Checks the health status of nginx every 10 seconds and updates the 'status' var based on the response
    while True:
        try:
            response = requests.get(url)
            status = 'OK' if response.status_code == 200 else 'NOT OK'
        except requests.exceptions.RequestException:
            status = 'NOT OK'

        health_status = {
            "service_name": service_name,
            "status": status,
            "timeStamp": datetime.utcnow().isoformat() + "Z"
        }
        # Send the result of the health check to Kafka
        producer.send(KAFKA_TOPIC, health_status)
        print(json.dumps(health_status))
        latest_status = health_status
        health_check_event.wait(5)
        health_check_event.clear()
        # time.sleep(10)
# Endpoint to retrieve health status from the Kafka topic
@app.route('/check_health', methods=['GET'])
def get_health():
    return jsonify(latest_status)

def consume_health_status():
    global latest_status
    for message in consumer:
        latest_status = message.value
        print(f"Received kafka message: {latest_status}")

if __name__ == "__main__":
    consumer_thread = Thread(target=consume_health_status)
    consumer_thread.start()

    health_checks_thread = Thread(target=check_health)
    health_checks_thread.start()

    app.run(host='0.0.0.0', port=8080)

    health_checks_thread.join()
    consumer_thread.join()