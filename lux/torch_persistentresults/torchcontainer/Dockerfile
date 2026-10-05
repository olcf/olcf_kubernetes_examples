FROM  docker.io/rocm/pytorch:rocm7.14.1_ubuntu26.04_py3.14_pytorch_release_2.12.0

COPY torch_mnist.py /root
RUN python3 -c "from torchvision import datasets; datasets.MNIST('/root/data', download=True)"

ENTRYPOINT ["python3", "/root/torch_mnist.py"]
