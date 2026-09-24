# Gemma RAG demo on RKE2

This example stores research text in PostgreSQL with pgvector, retrieves relevant passages with EmbeddingGemma, and asks a Gemma model served by vLLM to answer from that context.

## Prerequisites

- An RKE2 cluster with the `netapp-block` storage class
- An NVIDIA GPU with Kubernetes GPU support configured
- A container registry accessible from the cluster
- A Hugging Face account with access to `google/embeddinggemma-300m` and `google/gemma-3-4b-it`

Accept the Gemma license for both models before deploying. The application downloads EmbeddingGemma, and vLLM downloads the generation model to its persistent cache.

## Build

Replace `REGISTRY` with your registry:

```bash
docker build -t REGISTRY/gemma-rag-demo:latest -f Containerfile .
docker push REGISTRY/gemma-rag-demo:latest
```

Set the application image in `deploy/app.yaml`.

## Deploy

Create a namespace and the database and Hugging Face secrets.

```bash
kubectl create namespace gemma-rag
kubectl -n gemma-rag create secret generic rag-database \
  --from-literal=POSTGRES_DB=rag \
  --from-literal=POSTGRES_USER=rag_user \
  --from-literal=POSTGRES_PASSWORD='change-me'

kubectl -n gemma-rag create secret generic huggingface \
  --from-literal=HF_TOKEN='hf_your_token'

kubectl -n gemma-rag apply -f deploy/
kubectl -n gemma-rag rollout status deployment/postgres
kubectl -n gemma-rag rollout status deployment/vllm --timeout=15m
kubectl -n gemma-rag rollout status deployment/rag-app
```

The first vLLM startup can take several minutes while it downloads the model.

Forward the application service to your workstation:

```bash
kubectl -n gemma-rag port-forward service/rag-app 8080:80
```

## Add and query a document

Send a text file to the application. Reusing a source name replaces its existing chunks.

```bash
curl --data-binary @README.md \
  'http://localhost:8080/documents?source=README.md'
```

Ask a question:

```bash
curl --data-binary 'What models does this example use?' \
  http://localhost:8080/ask
```

The response includes the generated answer and retrieved sources with cosine-similarity scores.

## Remove the example

```bash
kubectl delete namespace gemma-rag
```

Deleting the namespace also deletes its persistent volume claims.
