This runs the same example as torch_simple, but it runs a collection of Jobs, and saves
the results in a Postgres database. A simple flask web application displays the results. 


Create secrets:

```
kubectl -n <your namespace> create secret generic postgres-secrets \
  --from-literal=POSTGRES_DB=torchresults \
  --from-literal=POSTGRES_USER=torch_user \
  --from-literal=POSTGRES_PASSWORD='change-me'
```
