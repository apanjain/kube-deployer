import os
import json
from kubernetes import client, config
from kafka import KafkaConsumer
import job_crud, deployment_crud
import logging

logging.basicConfig(filename='/mnt/c/pykube-debug.log', level=logging.INFO)

DEBUG = not (os.environ.get('MODE', 'DEV') == 'PROD')
KAFKA_BROKER_IP = os.environ.get('KAFKA_BROKER_IP', '0.0.0.0')
KAFKA_BROKER_PORT = os.environ.get('KAFKA_BROKER_PORT', 9092)
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'test-topic')
KAFKA_GROUP_ID = os.environ.get('KAFKA_GROUP_ID', 'test-group')


def not_found():
    logging.warning("Please provide a valid input\n")


def main():
    try:
        # print(DEBUG)
        if DEBUG:
            config.load_kube_config()
        else:
            config.load_incluster_config()

        switcher = {
            'create': job_crud.create,
        }

        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers="{}:{}".format(
                KAFKA_BROKER_IP, KAFKA_BROKER_PORT),
            auto_offset_reset="earliest",
            group_id=KAFKA_GROUP_ID)

        logging.info("Starting the consumer...")
        for msg in consumer:
            try:
                command = json.loads(msg.value).get(
                    'command', 'invalid').lower()
                switcher.get(command, not_found)()
            except Exception as e:
                logging.error(str(e))
    except Exception as e:
        logging.error(str(e))


if __name__ == "__main__":
    main()
