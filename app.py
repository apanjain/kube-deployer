import os
import json
import datetime
import yaml
import pytz
from kubernetes import client, config
from kafka import KafkaConsumer


HELLOWORLD_IMAGE_LOCATION = os.environ.get(
    'HELLOWORLD_IMAGE_LOCATION', 'nginx')
UPDATED_IMAGE_LOCATION = os.environ.get('UPDATED_IMAGE_LOCATION', 'nginx')
DEBUG = not (os.environ.get('MODE', 'DEV') == 'PROD')
KAFKA_BROKER_IP = os.environ.get('KAFKA_BROKER_IP', '0.0.0.0')
KAFKA_BROKER_PORT = os.environ.get('KAFKA_BROKER_PORT', 9092)
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'test-topic')
KAFKA_GROUP_ID = os.environ.get('KAFKA_GROUP_ID', 'test-group')


def create_deployment_object():
    with open(os.path.join(os.path.dirname(__file__), "helloworld-deployment.yaml")) as f:
        deployment = yaml.safe_load(f)
        deployment['spec']['template']['spec']['containers'][0]['image'] = HELLOWORLD_IMAGE_LOCATION
    return deployment


def create_deployment(api, deployment):
    # Create deployement
    resp = api.create_namespaced_deployment(
        body=deployment, namespace="default"
    )
    print("\n[INFO] deployment `flask-deployment` created.\n")
    print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
    print(
        "%s\t\t%s\t%s\t\t%s\n"
        % (
            resp.metadata.namespace,
            resp.metadata.name,
            resp.metadata.generation,
            resp.spec.template.spec.containers[0].image,
        )
    )


def update_deployment(api, deployment):
    # Update container image
    deployment['spec']['template']['spec']['containers'][0]['image'] = UPDATED_IMAGE_LOCATION

    # patch the deployment
    resp = api.patch_namespaced_deployment(
        name=deployment['metadata']['name'],
        namespace="default", body=deployment
    )

    print("\n[INFO] deployment's container image updated.\n")
    print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
    print(
        "%s\t\t%s\t%s\t\t%s\n"
        % (
            resp.metadata.namespace,
            resp.metadata.name,
            resp.metadata.generation,
            resp.spec.template.spec.containers[0].image,
        )
    )


def restart_deployment(api, deployment):
    # update `spec.template.metadata` section
    # to add `kubectl.kubernetes.io/restartedAt` annotation
    deployment['spec']['template']['metadata']['annotations'] = {
        "kubectl.kubernetes.io/restartedAt": datetime.datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .isoformat()
    }

    # patch the deployment
    resp = api.patch_namespaced_deployment(
        name=deployment['metadata']['name'],
        namespace="default", body=deployment
    )

    print("\n[INFO] deployment `{}` restarted.\n".format(
        deployment['metadata']['name']))
    print("%s\t\t\t%s\t%s" % ("NAME", "REVISION", "RESTARTED-AT"))
    print(
        "%s\t%s\t\t%s\n"
        % (
            resp.metadata.name,
            resp.metadata.generation,
            resp.spec.template.metadata.annotations,
        )
    )


def delete_deployment(api, deployment):
    # Delete deployment
    resp = api.delete_namespaced_deployment(
        name=deployment['metadata']['name'],
        namespace="default",
        body=client.V1DeleteOptions(
            propagation_policy="Foreground", grace_period_seconds=5
        ),
    )
    print("\n[INFO] deployment `{}` deleted.".format(
        deployment['metadata']['name']))


def create():
    apps_v1 = client.AppsV1Api()
    deployment = create_deployment_object()
    create_deployment(apps_v1, deployment)
    return 'Created'


def restart():
    apps_v1 = client.AppsV1Api()
    deployment = create_deployment_object()
    restart_deployment(apps_v1, deployment)
    return 'restarted'


def update():
    apps_v1 = client.AppsV1Api()
    deployment = create_deployment_object()
    update_deployment(apps_v1, deployment)
    return 'updated'


def delete():
    apps_v1 = client.AppsV1Api()
    deployment = create_deployment_object()
    delete_deployment(apps_v1, deployment)
    return 'deleted'


def not_found():
    print("Please provide a valid input\n")


def main():
    try:
        # print(DEBUG)
        if DEBUG:
            config.load_kube_config()
        else:
            config.load_incluster_config()

        switcher = {
            'create': create,
            'restart': restart,
            'update': update,
            'delete': delete
        }

        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers="{}:{}".format(
                KAFKA_BROKER_IP, KAFKA_BROKER_PORT),
            auto_offset_reset="earliest",
            group_id=KAFKA_GROUP_ID)

        print("Starting the consumer...")
        for msg in consumer:
            try:
                command = json.loads(msg.value).get(
                    'command', 'invalid').lower()
                switcher.get(command, not_found)()
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
