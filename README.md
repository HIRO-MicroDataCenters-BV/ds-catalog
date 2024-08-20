# Data Space Catalog

The service provides a REST API for managing catalog data. Interacts with connector services to obtain information about data products.

## Requirements
Python 3.10+

## Installation
```bash
pip install pre-commit
pre-commit install
```

## Working on a server
Go to the `/server` folder to install dependencies and work on the server application.  
Documentation on setting up the virtual environment, installing dependencies, and working with the server can be found [here](./server/README.md).

## Working on a client
Go to the `/client` folder to install dependencies and work on the client application.  
Documentation on setting up the virtual environment, installing dependencies, and working with the client can be found [here](./client/README.md).

## Release
The application version is specified in the VERSION file. The version should follow the format a.a.a, where 'a' is a number.  
To create a release, update the version in the VERSION file and add a tag in GIT.  
The release version for branches, pull requests, and tags will be generated based on the base version in the VERSION file.

## Continuous Integration
Upon committing and pushing, pre-commit triggers code checks, OpenAPI file generation, and client generation.

Upon pushing the commit to GitHub, workflows are initiated, which:
- Check the code formatting of the server and client;
- Execute server and client tests;
- Create a Docker image of the server, Helm chart, and deploy the application to a Kubernetes cluster.
- Build the client package and push it to [pypi.org](https://pypi.org/)

Work on the server and client is conducted in their respective directories: server and client, as the server-side and client-side parts have different dependencies, configurations, etc.

## GitHub Actions
GitHub Actions triggers testing, builds, and application publishing for each release.  
https://docs.github.com/en/actions  

During the build and publish process, a Docker image is built, a Helm chart is created, an openapi.yaml is generated.

**Initial setup**  
1. Create the branch gh-pages and use it as a GitHub page https://pages.github.com/.  
2. Set up secrets at `https://github.com/<workspace>/<project>/settings/secrets/actions`:
- `PYPI_TOKEN` - The secret token for PyPI. https://pypi.org/help/#apitoken

**After execution**  
The index.yaml file containing the list of Helm charts will be available at `https://<workspace>.github.io/<project>/helm-charts/index.yaml`. You can this URL on https://artifacthub.io/.  
A package of the client will be available at pypi.org.  
The Docker image will be available at `https://github.com/orgs/<workspace>/packages?repo_name=<project>`.

# Collaboration guidelines
HIRO uses and requires from its partners [GitFlow with Forks](https://hirodevops.notion.site/GitFlow-with-Forks-3b737784e4fc40eaa007f04aed49bb2e?pvs=4)
