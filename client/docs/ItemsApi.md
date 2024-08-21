# ds_catalog.ItemsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**items_create**](ItemsApi.md#items_create) | **POST** /item/ | Create an item
[**items_delete_item**](ItemsApi.md#items_delete_item) | **DELETE** /item/{id}/ | Delete an item
[**items_read_all**](ItemsApi.md#items_read_all) | **GET** /item/ | Read all items
[**items_read_item**](ItemsApi.md#items_read_item) | **GET** /item/{id}/ | Read an item
[**items_update_item**](ItemsApi.md#items_update_item) | **PUT** /item/{id}/ | Update an item


# **items_create**
> Item items_create(item)

Create an item

Create a new item in the storage

### Example


```python
import ds_catalog
from ds_catalog.models.item import Item
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
    api_instance = ds_catalog.ItemsApi(api_client)
    item = ds_catalog.Item() # Item | 

    try:
        # Create an item
        api_response = api_instance.items_create(item)
        print("The response of ItemsApi->items_create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ItemsApi->items_create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **item** | [**Item**](Item.md)|  | 

### Return type

[**Item**](Item.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **items_delete_item**
> items_delete_item(id)

Delete an item

Delete an item from the storage

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
    api_instance = ds_catalog.ItemsApi(api_client)
    id = 56 # int | 

    try:
        # Delete an item
        api_instance.items_delete_item(id)
    except Exception as e:
        print("Exception when calling ItemsApi->items_delete_item: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **items_read_all**
> List[Item] items_read_all()

Read all items

Read all items from the storage

### Example


```python
import ds_catalog
from ds_catalog.models.item import Item
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
    api_instance = ds_catalog.ItemsApi(api_client)

    try:
        # Read all items
        api_response = api_instance.items_read_all()
        print("The response of ItemsApi->items_read_all:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ItemsApi->items_read_all: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[Item]**](Item.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **items_read_item**
> Item items_read_item(id)

Read an item

Read item from the storage

### Example


```python
import ds_catalog
from ds_catalog.models.item import Item
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
    api_instance = ds_catalog.ItemsApi(api_client)
    id = 56 # int | 

    try:
        # Read an item
        api_response = api_instance.items_read_item(id)
        print("The response of ItemsApi->items_read_item:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ItemsApi->items_read_item: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**Item**](Item.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **items_update_item**
> Item items_update_item(id, item)

Update an item

Update an item in the storage

### Example


```python
import ds_catalog
from ds_catalog.models.item import Item
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
    api_instance = ds_catalog.ItemsApi(api_client)
    id = 56 # int | 
    item = ds_catalog.Item() # Item | 

    try:
        # Update an item
        api_response = api_instance.items_update_item(id, item)
        print("The response of ItemsApi->items_update_item:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ItemsApi->items_update_item: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **item** | [**Item**](Item.md)|  | 

### Return type

[**Item**](Item.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

