import json
from kafka import KafkaConsumer

KAFKA_SERVER = 'kafka.kafka.svc.cluster.local:29092'
KAFKA_TOPIC = 'health_checks_topic'

def consume_latest_message():
    # Create a Kafka consumer
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset='earliest',
        enable_auto_commit=False,  # Disable auto commit to ensure we consume the latest message only
        group_id='health-check-consumer-group',
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    print("Kafka Consumer - Running.....")
    latest_status = {}
    # Fetch one message
    for message in consumer:
        latest_status = message.value
        print(f"Received kafka message: {latest_status}")

if __name__ == "__main__":
    consume_latest_message()
