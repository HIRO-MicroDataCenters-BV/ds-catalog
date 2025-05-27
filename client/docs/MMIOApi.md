# ds_catalog.MMIOApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_mmio_file**](MMIOApi.md#delete_mmio_file) | **DELETE** /mmio/{filename}/ | Delete Mmio File
[**get_mmio_file**](MMIOApi.md#get_mmio_file) | **GET** /mmio/{filename}/ | Get Mmio File
[**save_mmio_file**](MMIOApi.md#save_mmio_file) | **POST** /mmio/ | Save Mmio File


# **delete_mmio_file**
> delete_mmio_file(filename)

Delete Mmio File

Delete a MMIO file

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
    api_instance = ds_catalog.MMIOApi(api_client)
    filename = 'filename_example' # str | 

    try:
        # Delete Mmio File
        api_instance.delete_mmio_file(filename)
    except Exception as e:
        print("Exception when calling MMIOApi->delete_mmio_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filename** | **str**|  | 

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
**404** | File not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_mmio_file**
> bytearray get_mmio_file(filename)

Get Mmio File

Get a MMIO file

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
    api_instance = ds_catalog.MMIOApi(api_client)
    filename = 'filename_example' # str | 

    try:
        # Get Mmio File
        api_response = api_instance.get_mmio_file(filename)
        print("The response of MMIOApi->get_mmio_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MMIOApi->get_mmio_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filename** | **str**|  | 

### Return type

**bytearray**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/octet-stream, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful file retrieval |  -  |
**404** | File not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_mmio_file**
> save_mmio_file(file)

Save Mmio File

Upload a MMIO file

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
    api_instance = ds_catalog.MMIOApi(api_client)
    file = None # bytearray | 

    try:
        # Save Mmio File
        api_instance.save_mmio_file(file)
    except Exception as e:
        print("Exception when calling MMIOApi->save_mmio_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | File uploaded successfully |  * Location - URL to download the file <br>  |
**400** | No file selected for uploading |  -  |
**409** | File already exists |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

