# ds_catalog.CatalogItemsSharingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**share_catalog_item**](CatalogItemsSharingApi.md#share_catalog_item) | **POST** /catalog-items/{id}/share/ | Share a catalog item


# **share_catalog_item**
> CatalogItem share_catalog_item(id, catalog_item_share_form)

Share a catalog item

Share a catalog item to the marketplace

### Example


```python
import ds_catalog
from ds_catalog.models.catalog_item import CatalogItem
from ds_catalog.models.catalog_item_share_form import CatalogItemShareForm
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
    api_instance = ds_catalog.CatalogItemsSharingApi(api_client)
    id = 'id_example' # str | 
    catalog_item_share_form = ds_catalog.CatalogItemShareForm() # CatalogItemShareForm | 

    try:
        # Share a catalog item
        api_response = api_instance.share_catalog_item(id, catalog_item_share_form)
        print("The response of CatalogItemsSharingApi->share_catalog_item:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CatalogItemsSharingApi->share_catalog_item: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **catalog_item_share_form** | [**CatalogItemShareForm**](CatalogItemShareForm.md)|  | 

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
**404** | Catalog Item not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

