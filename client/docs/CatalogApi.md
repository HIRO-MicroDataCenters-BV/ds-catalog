# ds_catalog.CatalogApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_catalog**](CatalogApi.md#get_catalog) | **POST** /catalog/ | Get Local Catalog


# **get_catalog**
> str get_catalog(catalog_filters)

Get Local Catalog

Get the local catalog with dataset list.  The request accepts filters as a JSON object in the body.  ### Format: Filters are structured as nested JSON objects. Each filter defines the path to the field with optional operators or language annotations.  ```json {   \"context\": {     \"<namespace>\": \"<namespaceURL>\",     ...   }   \"filters\": [     {       [\"type\": \"<namespace:Class>\",]       \"<namespace:attribute>[@<lang>][__operator]\": <value> | <nestedObject>     },     ...   ] } ```  ### Supported operators: - `__gte`, `__lte` — range filtering - `__in` — list filtering - `__contains` — substring search  ### Example: ```json {   \"context\": {     \"dcat\": \"http://www.w3.org/ns/dcat#\",     \"dspace\": \"http://data-space.org/\",     \"med\": \"http://med.example.org/\"   },   \"filters\": [     {       \"dcat:dataset\": {         \"dspace:extraMetadata\": {           \"type\": \"med:Diagnoses\",           \"med:hasDiagnosis\": {             \"med:code__contains\": \"I10\"           }         }       }     }   ] } ```  ### More filter examples: - ```json   { \"dcat:dataset\": { \"dcterms:title\": \"example\" } }   ``` - ```json   { \"dcat:dataset\": { \"dcterms:title@en\": \"example\" } }   ``` - ```json   { \"dcat:dataset\": { \"dcterms:title\": { \"@language\": \"en\" } } }   ``` - ```json   { \"dcat:dataset\": { \"dcterms:title\": { \"@value\": \"example\" } } }   ``` - ```json   { \"dcat:dataset\": { \"dcat:distribution\": { \"dcat:format\": \"PDF\" } } }   ``` - ```json   { \"dcat:dataset\": { \"dspace:extraMetadata\": { \"med:sex\": \"M\" } } }   ``` - ```json   { \"dcat:dataset\": { \"dspace:extraMetadata\": { \"type\": \"med:Patient\",   \"med:sex\": \"M\" } } }   ``` - ```json   { \"dcat:dataset\": { \"dspace:extraMetadata\": { \"med:weight\": 75 } } }   ``` - ```json   { \"dcat:dataset\": { \"dspace:extraMetadata\": { \"med:weight\": {   \"@value\": 75 } } } }   ``` - ```json   { \"dcat:dataset\": { \"dspace:extraMetadata\": { \"med:weight\": {   \"@type\": \"xsd:integer\" } } } }   ``` - ```json   { \"dcat:dataset\": { \"dcterms:datePublished__gte\": \"2021-01-01\" } }   ``` - ```json   { \"dcat:dataset\": { \"dcterms:datePublished__lte\": \"2021-12-31\" } }   ``` - ```json   { \"dcat:dataset\": { \"dspace:extraMetadata\": { \"med:weight__gte\": 70 } } }   ``` - ```json   { \"dcat:dataset\": { \"dspace:extraMetadata\": { \"med:weight__lte\": 70 } } }   ``` - ```json   { \"dcat:dataset\": { \"dcat:keyword__in\": [\"science\", \"health\"] } }   ``` - ```json   { \"dcat:dataset\": { \"dcterms:title@en__contains\": \"example\" } }   ```

### Example


```python
import ds_catalog
from ds_catalog.models.catalog_filters import CatalogFilters
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
    catalog_filters = ds_catalog.CatalogFilters() # CatalogFilters | 

    try:
        # Get Local Catalog
        api_response = api_instance.get_catalog(catalog_filters)
        print("The response of CatalogApi->get_catalog:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CatalogApi->get_catalog: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **catalog_filters** | [**CatalogFilters**](CatalogFilters.md)|  | 

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

