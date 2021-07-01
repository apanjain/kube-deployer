"""
Creates, updates, and deletes a job object.
"""

import logging
import os
from time import sleep

import yaml

from kubernetes import client

ML_IMAGE_LOCATION = os.environ.get('ML_IMAGE_LOCATION', 'hello-world')


def create_job_object():
    with open(os.path.join(os.path.dirname(__file__), "ml-job.yaml")) as f:
        job = yaml.safe_load(f)
        job['spec']['template']['spec']['containers'][0]['image'] = ML_IMAGE_LOCATION
    return job


def create_job(api_instance, job):
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace="default")
    logging.info("Job created. status='{}'".format(str(api_response.status)))
    get_job_status(api_instance, job)


def get_job_status(api_instance, job):
    job_completed = False
    while not job_completed:
        api_response = api_instance.read_namespaced_job_status(
            name=job['metadata']['name'],
            namespace="default")
        if api_response.status.succeeded is not None or api_response.status.failed is not None:
            job_completed = True
        if api_response.status.succeeded:
            delete()
        sleep(10)
        logging.info("Job status='{}'".format(str(api_response.status)))


def delete_job(api_instance, job):
    api_response = api_instance.delete_namespaced_job(
        name=job['metadata']['name'],
        namespace="default",
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    logging.info("Job deleted. status='{}'".format(str(api_response.status)))


def create():
    batch_v1 = client.BatchV1Api()
    job = create_job_object()
    create_job(batch_v1, job)
    return 'Created'


def delete():
    batch_v1 = client.BatchV1Api()
    job = create_job_object()
    delete_job(batch_v1, job)
    return 'deleted'
