# KUBENETES CONTAINER DEPLOYER

- Application to manage k8s deployments

## PRE-REQUISITE

- RUNNING KUBERNETES CLUSTER
- A SAMPLE IMAGE TO BE DEPLOYED, LOCATED INSIDE A REGISTRY ACCESSIBLE TO THE CLUSTER
- FOLLOW THIS [GUIDE](https://cloud.google.com/kubernetes-engine/docs/quickstarts/deploying-a-language-specific-app#python) TO SETUP SUCH INSTANCE , NO NEED TO DEPLOY THE IMAGE RIGHT AWAY
- ALSO A MODIFIED VERSION OF SAME IMAGE CAN BE CREATE FOR BETTER DEMONSTRATION

## SETUP

- Build an image for this container and push it to the registry, e.g.

```bash
glcoud builds submit --tag gcr.io/$GCLOUD_PROJECT/gke-kube-crud:latest
```

- Setup these values inside the `kube-crud-deployment.yaml` file

  - `LOCATION_TO_KUBECRUD_IMAGE`
  - `HELLOWORLD_IMAGE_LOCATION`
  - `UPDATED_IMAGE_LOCATION`

- Deploy the container on the cluster

```bash
kubectl apply -f kube-crud-deployment.yaml
```

- Also Create service for helloworld app beforehand

```bash
kubectl apply -f helloworld-service.yaml
```

- Run the following command to get the external IPs for both the services

```bash
kubectl get services
```

## USAGE

- Just hit the external IP specified by kube-crud service, to check whether the flask app is running
- Go to `/create` `/restart` `/update` `/delete` to perform respective operations on the helloworld container
