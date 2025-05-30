# Python client
API version: 0.2.1

## Requirements

- Python 3.10+
- Docker engine. [Documentation](https://docs.docker.com/engine/install/)

## Installation & Usage

1. If you don't have `Poetry` installed run:

```bash
pip install poetry
```

2. Install dependencies:

```bash
poetry config virtualenvs.in-project true
poetry install --no-root
```

3. Running tests:

```bash
poetry run pytest
```

You can test the application for multiple versions of Python. To do this, you need to install the required Python versions on your operating system, specify these versions in the tox.ini file, and then run the tests:
```bash
poetry run tox
```
Add the tox.ini file to `client/.openapi-generator-ignore` so that it doesn't get overwritten during client generation.

4. Building package:

```bash
poetry build
```

5. Publishing
```bash
poetry config pypi-token.pypi <pypi token>
poetry publish
```

## Client generator
To generate the client, execute the following script from the project root folder
```bash
poetry --directory server run python ./tools/client_generator/generate.py ./api/openapi.yaml
```

### Command
```bash
generate.py <file> [--asyncio]
```

#### Arguments
**file**
Specifies the input OpenAPI specification file path or URL. This argument is required for generating the Python client. The input file can be either a local file path or a URL pointing to the OpenAPI schema.

**--asyncio**
Flag to indicate whether to generate asynchronous code. If this flag is provided, the generated Python client will include asynchronous features. By default, synchronous code is generated.

#### Configuration
You can change the name of the client package in the file `/tools/client_generator/config.json`.

Add file's paths to `client/.openapi-generator-ignore` so that it doesn't get overwritten during client generation.

#### Examples

```bash
python generate.py https://<domain>/openapi.json
python generate.py https://<domain>/openapi.json --asyncio
python generate.py /<path>/openapi.yaml
python generate.py /<path>/openapi.yaml --asyncio
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import ds_catalog
from ds_catalog.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = ds_catalog.Configuration(
    host = "http://localhost"
)



# Enter a context with an instance of the API client
with ds_catalog.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = ds_catalog.CatalogApi(api_client)
    request_body = None # Dict[str, object] | 

    try:
        # Get Local Catalog
        api_response = api_instance.get_catalog(request_body)
        print("The response of CatalogApi->get_catalog:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling CatalogApi->get_catalog: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *http://localhost*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*CatalogApi* | [**get_catalog**](docs/CatalogApi.md#get_catalog) | **POST** /catalog/ | Get Local Catalog
*CatalogApi* | [**get_public_catalog**](docs/CatalogApi.md#get_public_catalog) | **POST** /public-catalog/ | Get Public Catalog
*DatasetsApi* | [**delete_dataset**](docs/DatasetsApi.md#delete_dataset) | **DELETE** /datasets/{id}/ | Delete Dataset
*DatasetsApi* | [**get_dataset**](docs/DatasetsApi.md#get_dataset) | **GET** /datasets/{id}/ | Get Dataset
*DatasetsApi* | [**save_dataset**](docs/DatasetsApi.md#save_dataset) | **POST** /datasets/{filename}/ | Save Dataset
*MMIOApi* | [**delete_mmio_file**](docs/MMIOApi.md#delete_mmio_file) | **DELETE** /mmio/{filename}/ | Delete Mmio File
*MMIOApi* | [**get_mmio_file**](docs/MMIOApi.md#get_mmio_file) | **GET** /mmio/{filename}/ | Get Mmio File
*MMIOApi* | [**save_mmio_file**](docs/MMIOApi.md#save_mmio_file) | **POST** /mmio/ | Save Mmio File
*SharingApi* | [**share_dataset**](docs/SharingApi.md#share_dataset) | **POST** /datasets/{id}/share/ | Share Dataset
*SharingApi* | [**unshare_dataset**](docs/SharingApi.md#unshare_dataset) | **POST** /datasets/{id}/unshare/ | Unhare Dataset
*DefaultApi* | [**health_check**](docs/DefaultApi.md#health_check) | **GET** /health-check/ | Health check
*DefaultApi* | [**metrics_metrics_get**](docs/DefaultApi.md#metrics_metrics_get) | **GET** /metrics | Metrics


## Documentation For Models

 - [ErrorResponse](docs/ErrorResponse.md)
 - [HTTPValidationError](docs/HTTPValidationError.md)
 - [HealthCheck](docs/HealthCheck.md)
 - [ValidationError](docs/ValidationError.md)
 - [ValidationErrorLocInner](docs/ValidationErrorLocInner.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization

Endpoints do not require authorization.


## Author

all-hiro@hiro-microdatacenters.nl


