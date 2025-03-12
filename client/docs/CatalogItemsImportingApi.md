# ds_catalog.CatalogItemsImportingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**import_catalog_item**](CatalogItemsImportingApi.md#import_catalog_item) | **POST** /catalog-items/import/ | Import a catalog item


# **import_catalog_item**
> CatalogItem import_catalog_item(catalog_item_import_form)

Import a catalog item

Import a catalog item from the local catalog

### Example


```python
import ds_catalog
from ds_catalog.models.catalog_item import CatalogItem
from ds_catalog.models.catalog_item_import_form import CatalogItemImportForm
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
    api_instance = ds_catalog.CatalogItemsImportingApi(api_client)
    catalog_item_import_form = ds_catalog.CatalogItemImportForm() # CatalogItemImportForm | 

    try:
        # Import a catalog item
        api_response = api_instance.import_catalog_item(catalog_item_import_form)
        print("The response of CatalogItemsImportingApi->import_catalog_item:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CatalogItemsImportingApi->import_catalog_item: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **catalog_item_import_form** | [**CatalogItemImportForm**](CatalogItemImportForm.md)|  | 

### Return type

[**CatalogItem**](CatalogItem.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  * Location - The URL of the newly created resource <br>  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

