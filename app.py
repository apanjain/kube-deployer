import datetime
import yaml
import pytz
from os import path, environ
from kubernetes import client, config

from flask import Flask


app = Flask(__name__)

HELLOWORLD_IMAGE_LOCATION = environ.get(
    'HELLOWORLD_IMAGE_LOCATION', '<HELLOWORLD_IMAGE_LOCATION _HERE>')
UPDATED_IMAGE_LOCATION = environ.get(
    'UPDATED_IMAGE_LOCATION', '<UPDATED_IMAGE_LOCATION_HERE>')


def create_deployment_object():
    with open(path.join(path.dirname(__file__), "helloworld-deployment.yaml")) as f:
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


@app.route('/')
def hello():
    return 'API Initialized \n visit /create /update /delete /restart'


@app.route('/create')
def create():
    apps_v1 = client.AppsV1Api()
    deployment = create_deployment_object()
    create_deployment(apps_v1, deployment)
    return 'Created'


@app.route('/restart')
def restart():
    apps_v1 = client.AppsV1Api()
    deployment = create_deployment_object()
    restart_deployment(apps_v1, deployment)
    return 'restarted'


@app.route('/update')
def update():
    apps_v1 = client.AppsV1Api()
    deployment = create_deployment_object()
    update_deployment(apps_v1, deployment)
    return 'updated'


@app.route('/delete')
def delete():
    apps_v1 = client.AppsV1Api()
    delete_deployment(apps_v1)
    return 'deleted'


config.load_incluster_config()
# print(config)


def main():  # This code will only run in local machine
    config.load_kube_config()
    # print(config.list_kube_config_contexts())
    app.run(debug=True, host='0.0.0.0', port=int(environ.get('PORT', 8080)))


if __name__ == "__main__":
    main()
