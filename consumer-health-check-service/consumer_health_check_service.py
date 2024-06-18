import json
from kafka import KafkaConsumer
from flask import Flask, jsonify
from threading import Thread, Lock
from prometheus_flask_exporter import PrometheusMetrics

KAFKA_SERVER = 'kafka.kafka.svc.cluster.local:29092'
KAFKA_TOPIC = 'health_checks_topic'

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='health-check-consumer-group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

latest_health_check = {}
health_check_lock = Lock()

def log_health_status(health_status):
    log_entry = {
        "service_name": health_status.get("service_name"),
        "status": health_status.get("status"),
        "timeStamp": health_status.get("timeStamp")
    }
    print(f"Logging health status: {json.dumps(log_entry)}")

print("ConsumerHealthCheckService - Running.....")

# Flask application setup with PrometheusMetrics
app = Flask(__name__)
metrics = PrometheusMetrics(app)

def consume_health_checks():
    global latest_health_check
    for message in consumer:
        health_status = message.value
        log_health_status(health_status)
        with health_check_lock:
            latest_health_check = health_status
        print(f"Updated latest_health_check: {latest_health_check}")

@app.route('/get_latest_health_check', methods=['GET'])
def get_latest_health_check():
    with health_check_lock:
        print(f"Returning latest_health_check: {latest_health_check}")
        return jsonify(latest_health_check)

if __name__ == "__main__":
    consumer_thread = Thread(target=consume_health_checks)
    consumer_thread.daemon = True
    consumer_thread.start()
    print("Starting Flask server on port 8080")
    app.run(host='0.0.0.0', port=8080)
