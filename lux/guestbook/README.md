# Example: Guestbook application on Kubernetes


Based on the tutorial https://kubernetes.io/docs/tutorials/stateless-application/guestbook/.

This repository has files to setup a guestbook application to demonstrate creating a simple
webserver that uses Redis on Lux.

To deploy the Redis cluster, run the following:
```
kubectl apply -f redis-master-deployment.yaml
kubectl apply -f redis-master-service.yaml
kubectl apply -f redis-replica-deployment.yaml
kubectl apply -f redis-replica-service.yaml
```

The above just deploys a plain Redis cluster - a master and 2 additioal workers.

The frontend uses a container built from the Dockerfile in this repository. If you wish to modify it
and build your own, you can do so. Just make sure to change the URL for `image:` in the
`frontend-deployment.yaml`.

To deploy the frontend, run:
```
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
```

To see the guestbook application, we will need to port forward from our laptop to the frontend
service

```
kubectl port-forward services/frontend 8899:80
```

Then in your browser, go to `localhost:8899` to view the guestbook in the browser.
