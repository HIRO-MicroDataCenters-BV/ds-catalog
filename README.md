# Data Space Catalog Service

The service provides a REST API for managing, searching, and sharing catalog items.

## Requirements
Python 3.10+

## Installation
```bash
pip install pre-commit
pre-commit install
```

Work on the server and client is conducted in their respective directories: server and client, as the server-side and client-side parts have different dependencies, configurations, etc.

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
- Check the code formatting
- Execute server and client tests
- Create a Docker image and Helm chart
- Build a client package and push it to [pypi.org](https://pypi.org/)

## GitHub Actions
GitHub Actions triggers testing, builds, and application publishing for each release.  
https://docs.github.com/en/actions

## Artifacts
* [OpenAPI specification](https://hiro-microdatacenters-bv.github.io/ds-catalog/docs/index.html)
* [Helm charts repository](https://hiro-microdatacenters-bv.github.io/ds-catalog/helm-charts/index.yaml)
* [Docker images repository](https://github.com/hiro-microdatacenters-bv/ds-catalog/pkgs/container/ds-catalog)
* [Python client](https://pypi.org/project/ds_catalog/)

# Collaboration guidelines
HIRO uses and requires from its partners [GitFlow with Forks](https://hirodevops.notion.site/GitFlow-with-Forks-3b737784e4fc40eaa007f04aed49bb2e?pvs=4)
