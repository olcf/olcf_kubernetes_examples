This runs the same example as torch_simple, but it runs a collection of Jobs each running a Torch
training, and saves
the results in a Postgres database. A simple Flask web application displays the results. 

### Note

This is not in anyway a realistic task. This is merely to serve as an example showing how to use
multiple Kubernetes features (PVCs, Deployments, Jobs, Services, HTTPRoutes, pushing and pulling images with
Harbor) all working together in one application.

### Note about PVCs

Lux provides two storage classes - `netapp-block` and `netapp-file`. If you [create a PVC](https://docs.olcf.ornl.gov/systems/lux_user_guide.html#storage) with
`netapp-block` and set it up as a volumeMount in your Pod like so

```
volumeMounts:
  - name: data
    mountPath: /mnt/postgresql
```

with the volume `data` coming from your PVC

```
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: postgres-data
```

The directory `/mnt/postgresql` is created and owned by `root`. This directory does not have write permissions for users other than root. So you will not
actually be able to write any data to this directory.


However, if you create this same volume with a PVC that uses `netapp-file`, the directory
`/mnt/postgresql` is still owned by root but will have write permissions for non-root users instead of being read-only. 

Because of this, it is preferable to use `netapp-file` instead of `netapp-block`.

## Build and Deploy
Create secrets for your Postgres database that we will be creating:

```
POSTGRES_DB=torchresults
POSTGRES_USER=torch_user
POSTGRES_PASSWORD='change-me'

kubectl -n <your namespace>-cpu create secret generic postgres-secrets \
  --from-literal=POSTGRES_DB=$POSTGRES_DB \
  --from-literal=POSTGRES_USER=$POSTGRES_USER \
  --from-literal=POSTGRES_PASSWORD=$POSTGRES_PASSWORD

kubectl -n <your namespace>-gpu create secret generic postgres-secrets \
  --from-literal=POSTGRES_DB=$POSTGRES_DB \
  --from-literal=POSTGRES_USER=$POSTGRES_USER \
  --from-literal=POSTGRES_PASSWORD=$POSTGRES_PASSWORD
```

We need to do this for both your CPU and GPU namespaces as our Postgres DB lives in the CPU
namespace and our Torch Jobs (which which needs to talk to the DB) lives in the GPU namespace.
Secrets are not shared between different namespaces so we need to create them for both namespaces. 

Make sure you have set up Docker/Podman to be able to push to Dockerhub.

```
# this will ask you to interactively enter your Dockerhub username and password
docker login docker.io
```

If you have private repositories on Dockerhub you want to use on Lux Kubernetes, [see our docs on how to set up pull
secrets](https://docs.olcf.ornl.gov/systems/lux_user_guide.html#pull-secret-creation-for-kubernetes). Make sure you set up your pull secrets on both your `*-cpu` and `*-gpu` namespaces.

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

Deploy the database first. This manifest creates a PVC, Deployment, Service, and ConfigMap in the
CPU namespace. The PVC
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


`torchjob.yaml` will start a Job in the GPU namespace that are performing several Torch trainings with MNIST and saving the test
accuracy result to Postgres. `flaskfrontend.yaml` will start a Flask based frontend in the CPU namespace displaying the table of
results saved to the Postgres database. The frontend is made visible with a HTTPRoute. See more
about how to view the frontend in the browser in [our docs about HTTPRoute](https://docs.olcf.ornl.gov/systems/lux_user_guide.html#httproutes-for-accessing-your-app-via-the-browser).

You can check the status of the Torch job with `kubectl get job torch-jobs`.
