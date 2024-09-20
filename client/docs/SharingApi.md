# ds_catalog.SharingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**share_dataset**](SharingApi.md#share_dataset) | **POST** /datasets/{id}/share/ | Share Dataset


# **share_dataset**
> Dataset share_dataset(id, dataset_share_form)

Share Dataset

Share the dataset to the marketplace

### Example


```python
import ds_catalog
from ds_catalog.models.dataset import Dataset
from ds_catalog.models.dataset_share_form import DatasetShareForm
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
    dataset_share_form = ds_catalog.DatasetShareForm() # DatasetShareForm | 

    try:
        # Share Dataset
        api_response = api_instance.share_dataset(id, dataset_share_form)
        print("The response of SharingApi->share_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharingApi->share_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **dataset_share_form** | [**DatasetShareForm**](DatasetShareForm.md)|  | 

### Return type

[**Dataset**](Dataset.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  * Location - The URL of the newly created resource <br>  |
**404** | Dataset not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

