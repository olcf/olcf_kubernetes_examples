This example deploys a single pod with a single container that runs an MNIST example with Pytorch.
This example shows how to use the GPU on Kubernetes on Lux. 

If you wish to customize the container, update the Dockerfile and build it with:

```
podman build -t <your image tag> .
```

If you customize the container, make sure to update the `spec.containers.image` field with the url
to your own image.


Take a look at the torchpod.yaml. Deploy it with:

```
kubectl apply -f torchpod.yaml -n <proj>-gpu
```

Check the status of the pod with `kubectl get pods`.

Then to view the output, run `kubectl logs -f torch-pod`.

To delete the pod, run `kubectl delete pods torch-pod`.
