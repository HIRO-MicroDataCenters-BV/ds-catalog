# ds_catalog.DatasetsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_dataset**](DatasetsApi.md#delete_dataset) | **DELETE** /datasets/{id}/ | Delete Dataset
[**get_dataset**](DatasetsApi.md#get_dataset) | **GET** /datasets/{id}/ | Get Dataset
[**save_dataset**](DatasetsApi.md#save_dataset) | **POST** /datasets/{filename}/ | Save Dataset


# **delete_dataset**
> delete_dataset(id)

Delete Dataset

Delete a dataset

### Example


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
    api_instance = ds_catalog.DatasetsApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete Dataset
        api_instance.delete_dataset(id)
    except Exception as e:
        print("Exception when calling DatasetsApi->delete_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**404** | Dataset not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_dataset**
> str get_dataset(id)

Get Dataset

Get a dataset

### Example


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
    api_instance = ds_catalog.DatasetsApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get Dataset
        api_response = api_instance.get_dataset(id)
        print("The response of DatasetsApi->get_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsApi->get_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/ld+json, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Dataset not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_dataset**
> str save_dataset(filename, request_body, related_data_product=related_data_product)

Save Dataset

Create or update a dataset or application.  This endpoint saves a new catalog item (or updates an existing one) using the metadata provided in the request body. The input must follow **DCAT-AP 3.0 JSON-LD**.  ### Notes - Items are always stored as `dcat:Dataset`. - You can represent either:     - A **dataset** (`dcterms:type = Dataset`)     - An **application** (`dcterms:type = Software`)  ### Example: Dataset ```json {   \"@context\": {     \"dcat\": \"http://www.w3.org/ns/dcat#\",     \"dcterms\": \"http://purl.org/dc/terms/\",     \"skos\": \"http://www.w3.org/2004/02/skos/core#\",     \"xsd\": \"http://www.w3.org/2001/XMLSchema#\"   },   \"@id\": \"https://example.com/dataset/789\",   \"@type\": \"dcat:Dataset\",   \"dcterms:identifier\": { \"@type\": \"xsd:string\", \"@value\": \"abc-123-xyz\" },   \"dcterms:title\": { \"@language\": \"en\", \"@value\": \"Sample Dataset\" },   \"dcterms:description\": { \"@language\": \"en\",    \"@value\": \"This dataset contains CSV data.\" },   \"dcterms:type\": {     \"@id\": \"http://purl.org/dc/dcmitype/Dataset\",     \"@type\": \"skos:Concept\",     \"skos:prefLabel\": { \"@language\": \"en\", \"@value\": \"Dataset\" }   },   \"dcat:distribution\": [     {       \"@type\": \"dcat:Distribution\",       \"dcat:accessURL\": {       \"@id\": \"https://example.com/distribution/489/info\" },       \"dcterms:format\": {         \"@id\": \"https://www.iana.org/assignments/media-types/text/csv\",         \"@type\": \"dcterms:MediaTypeOrExtent\",         \"skos:prefLabel\": { \"@language\": \"en\", \"@value\": \"CSV\" }       }     }   ] } ```  ### Example: Application (Software) ```json {   \"@context\": {     \"dcat\": \"http://www.w3.org/ns/dcat#\",     \"dcterms\": \"http://purl.org/dc/terms/\",     \"skos\": \"http://www.w3.org/2004/02/skos/core#\",     \"xsd\": \"http://www.w3.org/2001/XMLSchema#\"   },   \"@id\": \"https://example.com/dataset/5678\",   \"@type\": \"dcat:Dataset\",   \"dcterms:identifier\": { \"@type\": \"xsd:string\", \"@value\": \"5678\" },   \"dcterms:title\": { \"@language\": \"en\", \"@value\": \"Image Application\" },   \"dcterms:description\": { \"@language\": \"en\",    \"@value\": \"A containerized app for satellite image analysis.\" },   \"dcterms:type\": {     \"@id\": \"http://purl.org/dc/dcmitype/Software\",     \"@type\": \"skos:Concept\",     \"skos:prefLabel\": { \"@language\": \"en\", \"@value\": \"Software\" }   },   \"dcat:distribution\": [     {       \"@type\": \"dcat:Distribution\",       \"dcat:accessURL\": {       \"@id\": \"https://ghcr.io/my-org/image-analysis:1.0.0\" },       \"dcterms:format\": {         \"@id\": \"https://www.iana.org/assignments/media-types/         application/vnd.docker.distribution.manifest.v2+json\",         \"@type\": \"dcterms:MediaTypeOrExtent\",         \"skos:prefLabel\": { \"@language\": \"en\", \"@value\": \"Docker Image v2\" }       }     }   ] } ```

### Example


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
    api_instance = ds_catalog.DatasetsApi(api_client)
    filename = 'filename_example' # str | The name of the uploaded MMIO file.
    request_body = None # Dict[str, object] | 
    related_data_product = 'related_data_product_example' # str | Path to the related data product directory. (optional)

    try:
        # Save Dataset
        api_response = api_instance.save_dataset(filename, request_body, related_data_product=related_data_product)
        print("The response of DatasetsApi->save_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsApi->save_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filename** | **str**| The name of the uploaded MMIO file. | 
 **request_body** | [**Dict[str, object]**](object.md)|  | 
 **related_data_product** | **str**| Path to the related data product directory. | [optional] 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/ld+json, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

