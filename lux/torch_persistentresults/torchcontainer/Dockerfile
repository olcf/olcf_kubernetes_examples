FROM  docker.io/rocm/pytorch:rocm7.14.1_ubuntu26.04_py3.14_pytorch_release_2.12.0

COPY torch_mnist.py /root
RUN pip install "psycopg[binary]==3.3.6"
RUN python3 -c "from torchvision import datasets; datasets.MNIST('/root/data', download=True)"

WORKDIR /root
ENTRYPOINT ["python3", "torch_mnist.py", "--accel"]
