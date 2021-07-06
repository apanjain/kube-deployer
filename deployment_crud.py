import os
import yaml
import datetime
import pytz
import logging
from kubernetes import client


HELLOWORLD_IMAGE_LOCATION = os.environ.get(
    'HELLOWORLD_IMAGE_LOCATION', 'nginx')
UPDATED_IMAGE_LOCATION = os.environ.get('UPDATED_IMAGE_LOCATION', 'nginx')


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
    logging.info("\n deployment `flask-deployment` created.\n")
    logging.info("{}}\t{}}\t\t\t{}}\t{}}".format(
        "NAMESPACE", "NAME", "REVISION", "IMAGE"))
    logging.info(
        "{}}\t\t{}}\t{}}\t\t{}}\n".format(
            str(resp.metadata.namespace),
            str(resp.metadata.name),
            str(resp.metadata.generation),
            str(resp.spec.template.spec.containers[0].image),
        )
    )


def update_deployment(api, deployment):
    # Update container image
    deployment['spec']['template']['spec']['containers'][0]['image'] = UPDATED_IMAGE_LOCATION
    api = client.AppsV1Api(api)
    # patch the deployment
    resp = api.patch_namespaced_deployment(
        name=deployment['metadata']['name'],
        namespace="default", body=deployment
    )
    logging.info("\n deployment's container image updated.\n")
    logging.info("{}}\t{}}\t\t\t{}}\t{}}".format(
        "NAMESPACE", "NAME", "REVISION", "IMAGE"))
    logging.info(
        "{}}\t\t{}}\t{}}\t\t{}}\n".format(
            str(resp.metadata.namespace),
            str(resp.metadata.name),
            str(resp.metadata.generation),
            str(resp.spec.template.spec.containers[0].image),
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

    logging.info("\n deployment `{}` restarted.\n".format(
        deployment['metadata']['name']))
    logging.info("{}}\t\t\t{}}\t{}}".format(
        "NAME", "REVISION", "RESTARTED-AT"))
    logging.info(
        "{}}\t{}}\t\t{}}\n".format(
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
    logging.info("\n[INFO] deployment `{}` deleted.".format(
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
