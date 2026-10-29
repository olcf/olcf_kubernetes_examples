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


Make sure you have set up Docker/Podman to be able to push to Dockerhub.

```
# this will ask you to interactively enter your Dockerhub username and password
docker login docker.io
```

If you have private repositories on Dockerhub you want to use on Lux Kubernetes, [see our docs on how to set up pull
secrets](https://docs.olcf.ornl.gov/systems/lux_user_guide.html#pull-secret-creation-for-kubernetes).

Build the images. Change the full names of the images to reference the Dockerhub project to which you
are pushing your images.

```
cd flaskfrontend
# can use podman too. If building on a lux login node, use `podman build --net=host`
docker build -t docker.io/<your username>/flask-torchresults:latest .
cd ../torchcontaine
docker build -t docker.io/<your username>/torchjob:latest .
cd ..
```

Push the images to Dockerhub

```
docker push docker.io/<your username>/flask-torchresults:latest
docker push docker.io/<your username>/torchjob:latest 
```

Deploy the database first. This manifest creates a PVC, Deployment, Service, and ConfigMap. The PVC
sets up storage for the database, the Deployment creates a single pod with a Postgres database using
the PVC as its backing store, the ConfigMap sets up environment variables that will be referenced by
applications deployed by other manifests. 
```
kubectl apply -f postgres.yaml
```

Open `torchjob.yaml` and fix the `image:` URL to point to the image you pushed to Dockerhub. Also make
sure the `imagePullSecrets` references the correct secret that you [created earlier on Rancher for
Dockerhub image pulls](https://docs.olcf.ornl.gov/systems/lux_user_guide.html#pull-secret-creation-for-kubernetes) (if you are using a private repository on Dockerhub).

Do the same thing for `flaskfrontend.yaml`.


Deploy these two with:
```
kubectl apply -f torchjob.yaml
kubectl apply -f flaskfrontend.yaml
```

This will start a Job that are performing several Torch trainings with MNIST and saving the test
accuracy result to Postgres. This will also start a Flask based frontend displaying the table of
results saved to the Postgres database. The frontend is made visible with a HTTPRoute. See more
about how to view the frontend in the browser in [our docs about HTTPRoute](https://docs.olcf.ornl.gov/systems/lux_user_guide.html#httproutes-for-accessing-your-app-via-the-browser).

You can check the status of the Torch job with `kubectl get job torch-jobs`.
