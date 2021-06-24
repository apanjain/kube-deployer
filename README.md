# KUBENETES CONTAINER DEPLOYER

- Application to manage k8s deployments

## PRE-REQUISITE

- RUNNING KUBERNETES CLUSTER
- A SAMPLE IMAGE (WHICH WILL BE DEPLOYED LATER USING OUR APPLICATION) LOCATED INSIDE A REGISTRY ACCESSIBLE TO THE CLUSTER
- FOLLOW THIS [GUIDE](https://cloud.google.com/kubernetes-engine/docs/quickstarts/deploying-a-language-specific-app#python) TO SETUP SUCH INSTANCE , NO NEED TO DEPLOY THE IMAGE RIGHT AWAY
- ALSO A MODIFIED VERSION OF SAME IMAGE CAN BE CREATED FOR BETTER DEMONSTRATION

## SETUP

- Build an image for this container and push it to the registry, e.g.

```bash
gcloud builds submit --tag gcr.io/$GCLOUD_PROJECT/gke-kube-crud:latest .
```

- Setup these values inside the `kube-crud-deployment.yaml` file

  - `LOCATION_TO_KUBECRUD_IMAGE`
  - `HELLOWORLD_IMAGE_LOCATION`
  - `UPDATED_IMAGE_LOCATION`
  - `KAFKA_BROKER_IP`
  - `KAFKA_BROKER_PORT`
  - `KAFKA_TOPIC`
  - `KAFKA_GROUP_ID`

- Deploy the container on the cluster

```bash
kubectl apply -f kube-crud-deployment.yaml
```

- Also Create service for helloworld app beforehand

```bash
kubectl apply -f helloworld-service.yaml
```

- Run the following command to get the external IPs for the `hello` service

```bash
kubectl get services
```

## USAGE

- Add messages to your kafka topic in the following format

```
{'command' : '<CMD>'}
```

- Where `<CMD>` can be
  - `create`
  - `restart`
  - `update`
  - `delete`
