# ds_catalog.SharingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**share_dataset**](SharingApi.md#share_dataset) | **POST** /datasets/{id}/share/ | Share Dataset
[**unshare_dataset**](SharingApi.md#unshare_dataset) | **POST** /datasets/{id}/unshare/ | Unhare Dataset


# **share_dataset**
> share_dataset(id)

Share Dataset

Share a dataset

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
    api_instance = ds_catalog.SharingApi(api_client)
    id = 'id_example' # str | 

    try:
        # Share Dataset
        api_instance.share_dataset(id)
    except Exception as e:
        print("Exception when calling SharingApi->share_dataset: %s\n" % e)
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

# **unshare_dataset**
> unshare_dataset(id)

Unhare Dataset

Unshare a dataset

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
    api_instance = ds_catalog.SharingApi(api_client)
    id = 'id_example' # str | 

    try:
        # Unhare Dataset
        api_instance.unshare_dataset(id)
    except Exception as e:
        print("Exception when calling SharingApi->unshare_dataset: %s\n" % e)
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

