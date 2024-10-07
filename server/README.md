# Server application

## Requirements
Python 3.12+

## Installation
1. If you don't have `Poetry` installed run:
    ```bash
    pip install poetry
    ```

2. Install dependencies:
    ```bash
    poetry config virtualenvs.in-project true
    poetry install --no-root --with dev,test
    ```

3. Create .env file from the template .env.template:
    ```bash
    NEO4J_AUTH=neo4j/your_password

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
    ```

4. Launch the project:
    ```bash
    poetry run uvicorn app.main:app --reload
    ```
    or do it in two steps:
    ```bash
    poetry shell
    uvicorn app.main:app
    ```

5. Run tests:
    ```bash
    poetry run pytest
    ```

    You can test the application for multiple versions of Python. To do this, you need to install the required Python versions on your operating system, specify these versions in the tox.ini file, and then run the tests:
    ```bash
    poetry run tox
    ```

## Deployment on Kubernetes
Requirements:
* [Docker](https://docs.docker.com/)
* [Minikube](https://minikube.sigs.k8s.io/docs/) or Kubernetes cluster
* [Helm](https://helm.sh/ru/docs/)

### Local (for development)
1. Start Minikube:
    ```bash
    minikube start
    ```

2. Build a Docker image:
    ```bash
    docker build . -t ds-catalog-srvice:latest
    ```

3. Upload the Docker image to Minikube:
    ```bash
    minikube image load ds-catalog-srvice:latest
    ```

4. Download chart dependencies:
    ```bash
    helm dependency update ./charts/server
    ```

5. Create a secret with username, password, and NEO4J_AUTH:
    ```bash
    kubectl create secret generic neo4j-secrets \
      --from-literal=username=<username> \
      --from-literal=password=<password> \
      --from-literal=NEO4J_AUTH=<username>/<password>
    ```

    Username is `neo4j` by default.

    To retrieve the secrets, use the following commands:
    ```bash
    kubectl get secret neo4j-secrets -o jsonpath="{.data.username}" | base64 --decode
    kubectl get secret neo4j-secrets -o jsonpath="{.data.password}" | base64 --decode
    kubectl get secret neo4j-secrets -o jsonpath="{.data.NEO4J_AUTH}" | base64 --decode
    ```

6. Deploy the Helm chart:
    ```bash
    helm upgrade --install catalog ./charts/server --set image.repository=ds-catalog-srvice --set image.tag=latest
    ```

7. To delete the deployment:
    ```bash
    helm delete catalog

    kubectl get pvc
    kubectl delete pvc data-catalog-0

    kubectl get secret
    kubectl delete secret neo4j-secrets
    ```

### Production
1. Authenticate your Helm client in the container registry:
    ```bash
    helm registry login <repo_url> -u <username>
    ```

2. Deploy the Helm chart:
    ```bash
    helm repo add <repo_name> <repo_url>
    helm repo update <repo_name>
    helm upgrade --install <release_name> <repo_name>/<chart_name>
    ```

## Prometheus metrics
The application includes prometheus-fastapi-instrumentator for monitoring performance and analyzing its operation. It automatically adds an endpoint `/metrics` where you can access application metrics for Prometheus. These metrics include information about request counts, request execution times, and other important indicators of application performance.
More on that at (Prometheus FastAPI Instrumentator)[https://github.com/trallnag/prometheus-fastapi-instrumentator]
