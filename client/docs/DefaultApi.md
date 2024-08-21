# ds_catalog.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**example_get**](DefaultApi.md#example_get) | **GET** / | Example endpoint
[**metrics_metrics_get**](DefaultApi.md#metrics_metrics_get) | **GET** /metrics | Metrics


# **example_get**
> ExampleResponse example_get()

Example endpoint

Example endpoint that returns test data

### Example


```python
import ds_catalog
from ds_catalog.models.example_response import ExampleResponse
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
    api_instance = ds_catalog.DefaultApi(api_client)

    try:
        # Example endpoint
        api_response = api_instance.example_get()
        print("The response of DefaultApi->example_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->example_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ExampleResponse**](ExampleResponse.md)

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

# **metrics_metrics_get**
> object metrics_metrics_get()

Metrics

Endpoint that serves Prometheus metrics.

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
    api_instance = ds_catalog.DefaultApi(api_client)

    try:
        # Metrics
        api_response = api_instance.metrics_metrics_get()
        print("The response of DefaultApi->metrics_metrics_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->metrics_metrics_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

