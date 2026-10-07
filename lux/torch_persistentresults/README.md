This runs the same example as torch_simple, but it runs a collection of Jobs each running a Torch
training, and saves
the results in a Postgres database. A simple Flask web application displays the results. 

### Note

This is not in anyway a realistic task. This is merely to serve as an example showing how to use
multiple Kubernetes features (PVCs, Deployments, Jobs, Services, HTTPRoutes, pushing and pulling images with
Harbor) all working together in one application.

## Build and Deploy
Create secrets for your Postgres database that we will be creating:

```
kubectl -n <your namespace> create secret generic postgres-secrets \
  --from-literal=POSTGRES_DB=torchresults \
  --from-literal=POSTGRES_USER=torch_user \
  --from-literal=POSTGRES_PASSWORD='change-me'
```


Make sure you have set up Docker/Podman to be able to push or Harbor, [see our
docs on how to set up credentials with Harbor, how to push images to Harbor,  a Harbor pull secret to be used by Kubernetes]().


Build the images. Change the full names of the images to reference the Harbor project to which you
are pushing your images.

```
cd flaskfrontend
# can use podman too. If building on a lux login node, use `podman build --net=host`
docker build -t harbor.ccs.ornl.gov/<your project>/flask-torchresults:latest .
cd ../torchcontaner
docker build -t harbor.ccs.ornl.gov/<your project>/torchjob:latest .
cd ..
```

Push the images to Harbor 

```
docker push harbor.ccs.ornl.gov/<your project>/flask-torchresults:latest
docker push harbor.ccs.ornl.gov/<your project>/torchjob:latest 
```

Deploy the database first. This manifest creates a PVC, Deployment, Service, and ConfigMap. The PVC
sets up storage for the database, the Deployment creates a single pod with a Postgres database using
the PVC as its backing store, the ConfigMap sets up environment variables that will be referenced by
applications deployed by other manifests. 
```
kubectl apply -f postgres.yaml
```

Open `torchjob.yaml` and fix the `image:` URL to point to the image you pushed to Harbor. Also make
sure the `imagePullSecrets` references the correct secret that you created earlier on Rancher for
Harbor image pulls.

Do the same thing for `flaskfrontend.yaml`.


Deploy these two with:
```
kubectl apply -f torchjob.yaml
kubectl apply -f flaskfrontend.yaml
```
