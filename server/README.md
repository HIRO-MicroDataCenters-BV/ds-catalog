# Server application

## Requirements
Python 3.12+

## Installation
1. If you don't have `Poetry` installed run:
    ```bash
    pip install poetry==2.1.2
    ```

2. Install dependencies:
    ```bash
    poetry config virtualenvs.in-project true
    poetry install --no-root --with dev,test
    ```

3. Create .env file from the template .env.template:
    ```bash
    DS__DATABASE__PROTOCOL=neo4j
    DS__DATABASE__HOST=localhost
    DS__DATABASE__PORT=7687
    DS__DATABASE__NAME=neo4j
    DS__DATABASE__USERNAME=neo4j
    DS__DATABASE__PASSWORD=your_password

    DS__TEST_DATABASE__PROTOCOL=neo4j
    DS__TEST_DATABASE__HOST=localhost
    DS__TEST_DATABASE__PORT=7688
    DS__TEST_DATABASE__NAME=neo4j
    DS__TEST_DATABASE__USERNAME=neo4j
    DS__TEST_DATABASE__PASSWORD=your_password

    DS__CATALOG__TITLE="Local catalog"
    DS__CATALOG__DESCRIPTION="My local catalog"

    DS__OCA_URI="http://oca.example.org/123/"  # Default local OCA bundle
  
    DS__ONTOLOGY_URL="https://www.w3.org/ns/dcat.ttl"  # Default ontology (DCAT-3 or DCAT-AP)
    DS__SHACL_URL="https://semiceu.github.io/DCAT-AP/releases/3.0.0/shacl/dcat-ap-SHACL.ttl"  # Default validation SHACL schema
    ```

4. Initialize the database:
   ```bash
   poetry run python -m app.migrate_db
   ```

5. Launch the project:
    ```bash
    poetry run uvicorn app.main:app --reload
    ```
    or do it in two steps:
    ```bash
    poetry shell
    uvicorn app.main:app
    ```

6. Run tests:
    ```bash
    poetry run pytest
    ```

## Deployment on Kubernetes
Requirements:
* [Docker](https://docs.docker.com/)
* [Minikube](https://minikube.sigs.k8s.io/docs/) or Kubernetes cluster
* [Helm](https://helm.sh/ru/docs/)
* [Neo4j](https://neo4j.com/docs/operations-manual/current/kubernetes/)
* [Neosemantics](https://neo4j.com/labs/neosemantics/)

### Local (for development)
1. Start Minikube:
    ```bash
    minikube start
    ```

2. Deploy Neo4j with the Neosemantics plugin.  
   You can deploy them using [this repository](https://github.com/HIRO-MicroDataCenters-BV/Neo4j-With-Neosemantics).

3. Build a Docker image:
    ```bash
    docker build . -t ds-catalog-srvice:latest
    ```

4. Upload the Docker image to Minikube:
    ```bash
    minikube image load ds-catalog-srvice:latest
    ```

5. Deploy the Helm chart:
    ```bash
    helm upgrade --install catalog ./charts/server --set image.repository=ds-catalog-srvice --set image.tag=latest --set database.host=<host name> --set database.username=<username> --set database.password=<password> --set migrate.enabled=true
    ```

6. To delete the deployment:
    ```bash
    helm delete catalog
    kubectl delete pvc catalog-ds-catalog-uploads
    ```

### Production
1. Label the nodes:
    ```bash
    kubectl label nodes <node> node-id=node1
    kubectl label nodes <node> node-id=node2
    kubectl label nodes <node> node-id=node3
    ```

2. Define ingress.host and ingress.nodes in values.yaml:
    ```bash
    ingress:
      host: nextgen.hiro-develop.nl
      nodes:
        - nodeId: node1
        - nodeId: node2
        - nodeId: node3
    ```

3. Deploy the Helm chart:
    ```bash
    helm repo add ds-catalog-repo https://hiro-microdatacenters-bv.github.io/ds-catalog/helm-charts/
    helm repo update ds-catalog-repo
    helm install ds-catalog ds-catalog-repo/ds-catalog -f values.yaml
    ```

4. The catalog service will be available at:
   * https://ds-catalog.node1.nextgen.hiro-develop.nl
   * https://ds-catalog.node2.nextgen.hiro-develop.nl
   * https://ds-catalog.node3.nextgen.hiro-develop.nl

## Prometheus metrics
The application includes prometheus-fastapi-instrumentator for monitoring performance and analyzing its operation. It automatically adds an endpoint `/metrics` where you can access application metrics for Prometheus. These metrics include information about request counts, request execution times, and other important indicators of application performance.
More on that at [Prometheus FastAPI Instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)
