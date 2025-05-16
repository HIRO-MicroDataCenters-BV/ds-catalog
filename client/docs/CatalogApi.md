# ds_catalog.CatalogApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_catalog**](CatalogApi.md#get_catalog) | **POST** /catalog/ | Get Local Catalog


# **get_catalog**
> str get_catalog(request_body)

Get Local Catalog

Get the local catalog with dataset list.  The request accepts filters as a JSON-LD object in the body.  ### Format: Filters are structured as nested JSON-LD objects. Each filter defines the path to the field with optional operators or language annotations.  ```json {   \"@context\": {     \"@vocab\": \"http://data-space.org/\",     \"<namespace>\": \"<namespaceURL>\",     ...   }   \"@type\": \"Filters\",   \"filters\": [     {       [\"@type\": \"<[namespace:]Class>\",]       \"<[namespace:]attribute>\": <nestedObject> | <value> | {         \"@value\": <value>,         [\"@type\": <type> | \"@language\": <language>]       }     }   ] } ```  To get all datasets, use an empty object in the request body.  ```json {} ```  ### Example: ```json {   \"@context\": {     \"@vocab\": \"http://data-space.org/\",     \"dcat\": \"http://www.w3.org/ns/dcat#\",     \"med\": \"http://med.example.org/\"   },   \"@type\": \"Filters\",   \"filters\": [     {       \"dcat:dataset\": {         \"extraMetadata\": {           \"@type\": \"med:Record\",           \"med:age\": true,           \"med:bmi\": true         }       }     }   ] } ```  ### More filter examples: - <b>Filter by dataset identifier</b> ```json     {         \"@type\": \"dcat:Catalog\",         \"dcat:dataset\": {             \"@type\": \"dcat:Dataset\",             \"dcterms:identifier\": \"123\"         }     } ```  - <b>Filtering without specifying classes:</b> The service will attempt to infer unspecified classes. If inferencing fails, an error will be returned. ```json     {         \"dcat:dataset\": {             \"dcterms:identifier\": \"123\"         }     } ```  - <b>Filtering with language</b> ```json     {         \"dcat:dataset\": {             \"dcterms:title\": {                 \"@value\": \"example\",                 \"@language\": \"en\"             }         }     } ```  - <b>Filtering with data type</b> ```json     {         \"dcat:dataset\": {             \"extraMetadata\": {                 \"@type\": \"med:Record\",                 \"med:age\": {                     \"@type\": \"xsd:boolean\",                     \"@value\": true                 }             }         }     } ```  - <b>Incomplete filter structure:</b> All datasets with age=true will be found. ```json     {         \"@type\": \"med:Record\",         \"med:age\": true     } ```  - <b>Multiple conditions:</b> All datasets with identifier=123 <b>AND</b> age=true <b>AND</b> bmi=true will be found. ```json     {         \"dcat:dataset\": {             \"dcterms:identifier\": \"123\",             \"extraMetadata\": {                 \"@type\": \"med:Record\",                 \"med:age\": true,                 \"med:bmi\": true             }         }     } ```  - <b>Multiple values:</b> All datasets will be found for which the attribute age is true <b>OR</b> false. ```json     {         \"dcat:dataset\": {             \"extraMetadata\": [                 {                     \"@type\": \"med:Record\",                     \"med:age\": [                         {                             \"@value\": true,                             \"@type\": \"xsd:boolean\"                         },                         {                             \"@value\": false,                             \"@type\": \"xsd:boolean\"                         }                     ]                 }             ]         }     } ```

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
    api_instance = ds_catalog.CatalogApi(api_client)
    request_body = None # Dict[str, object] | 

    try:
        # Get Local Catalog
        api_response = api_instance.get_catalog(request_body)
        print("The response of CatalogApi->get_catalog:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CatalogApi->get_catalog: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**Dict[str, object]**](object.md)|  | 

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
**400** | Bad Request |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

