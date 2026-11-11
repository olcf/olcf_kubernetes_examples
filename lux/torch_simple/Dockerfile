FROM docker.io/rocm/pytorch:rocm10.1.0_ubuntu26.04_py3.14_pytorch_release_2.14.0

COPY torch_mnist.py /opt


RUN python3 -c "from torchvision import datasets; datasets.MNIST('/opt/data', download=True)"
WORKDIR /opt
ENTRYPOINT ["python3", "torch_mnist.py", "--accel"]
