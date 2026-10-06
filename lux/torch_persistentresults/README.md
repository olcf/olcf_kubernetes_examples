This runs the same example as torch_simple, but it runs a collection of Jobs, and saves
the results in a Postgres database. A simple flask web application displays the results. 

### Note

This is not in anyway a realistic task. This is merely to serve as an example showing how to use
multiple Kubernetes features - PVCs, Deployments, Jobs, all working together in one application.

## Build and Deploy
Create secrets:

```
kubectl -n <your namespace> create secret generic postgres-secrets \
  --from-literal=POSTGRES_DB=torchresults \
  --from-literal=POSTGRES_USER=torch_user \
  --from-literal=POSTGRES_PASSWORD='change-me'
```

Build the images
```
cd flaskfrontend
# can use podman too. If building on a lux login node, use `podman build --net=host`
docker build -t harbor.ccs.ornl.gov/subil/flask-torchresults:latest .
cd ../torchcontaner
docker build -t docker.io/subilabrahamornl/torchjob:latest .
```

Deploy the database first
```
kubectl apply -f postgres.yaml
```

Deploy the Torch Jobs next
```
kubectl apply -f torchjob.yaml
```
