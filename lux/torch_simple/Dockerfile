FROM  docker.io/rocm/pytorch:rocm7.14.1_ubuntu26.04_py3.14_pytorch_release_2.12.0

COPY torch_mnist.py /root
COPY data /root/data

ENTRYPOINT ["python3", "/root/torch_mnist.py"]
