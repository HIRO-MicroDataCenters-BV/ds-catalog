# ds_catalog.CatalogItemsDataApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**change_catalog_item_data**](CatalogItemsDataApi.md#change_catalog_item_data) | **PUT** /catalog-items/{id}/data/ | Change the data for the catalog item
[**create_catalog_item_data**](CatalogItemsDataApi.md#create_catalog_item_data) | **POST** /catalog-items/{id}/data/ | Create the data for the catalog item
[**delete_catalog_item_data**](CatalogItemsDataApi.md#delete_catalog_item_data) | **DELETE** /catalog-items/{id}/data/ | Delete the data for the catalog item
[**get_catalog_item_data**](CatalogItemsDataApi.md#get_catalog_item_data) | **GET** /catalog-items/{id}/data/ | Get the data for the catalog item


# **change_catalog_item_data**
> object change_catalog_item_data(id, body)

Change the data for the catalog item

Change the data for the catalog item

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
    api_instance = ds_catalog.CatalogItemsDataApi(api_client)
    id = 'id_example' # str | Catalog Item ID
    body = None # object | 

    try:
        # Change the data for the catalog item
        api_response = api_instance.change_catalog_item_data(id, body)
        print("The response of CatalogItemsDataApi->change_catalog_item_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CatalogItemsDataApi->change_catalog_item_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Catalog Item ID | 
 **body** | **object**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Catalog Item or Catalog Item Data not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_catalog_item_data**
> object create_catalog_item_data(id, body)

Create the data for the catalog item

Create the data for the catalog item

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
    api_instance = ds_catalog.CatalogItemsDataApi(api_client)
    id = 'id_example' # str | Catalog Item ID
    body = None # object | 

    try:
        # Create the data for the catalog item
        api_response = api_instance.create_catalog_item_data(id, body)
        print("The response of CatalogItemsDataApi->create_catalog_item_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CatalogItemsDataApi->create_catalog_item_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Catalog Item ID | 
 **body** | **object**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  * Location - The URL of the newly created resource <br>  |
**404** | Catalog item not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_catalog_item_data**
> delete_catalog_item_data(id)

Delete the data for the catalog item

Delete the data for the catalog item

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
    api_instance = ds_catalog.CatalogItemsDataApi(api_client)
    id = 'id_example' # str | Catalog Item ID

    try:
        # Delete the data for the catalog item
        api_instance.delete_catalog_item_data(id)
    except Exception as e:
        print("Exception when calling CatalogItemsDataApi->delete_catalog_item_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Catalog Item ID | 

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
**404** | Catalog Item or Catalog Item Data not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_catalog_item_data**
> object get_catalog_item_data(id)

Get the data for the catalog item

Returns the data for the catalog item

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
    api_instance = ds_catalog.CatalogItemsDataApi(api_client)
    id = 'id_example' # str | Catalog Item ID

    try:
        # Get the data for the catalog item
        api_response = api_instance.get_catalog_item_data(id)
        print("The response of CatalogItemsDataApi->get_catalog_item_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CatalogItemsDataApi->get_catalog_item_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Catalog Item ID | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Catalog Item or Catalog Item Data not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

