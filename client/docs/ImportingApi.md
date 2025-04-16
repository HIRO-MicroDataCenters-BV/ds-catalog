# ds_catalog.ImportingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**import_dataset**](ImportingApi.md#import_dataset) | **POST** /datasets/import/ | Import Dataset


# **import_dataset**
> Dataset import_dataset(dataset_import_form)

Import Dataset

Import a dataset from the local catalog

### Example


```python
import ds_catalog
from ds_catalog.models.dataset import Dataset
from ds_catalog.models.dataset_import_form import DatasetImportForm
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
    api_instance = ds_catalog.ImportingApi(api_client)
    dataset_import_form = ds_catalog.DatasetImportForm() # DatasetImportForm | 

    try:
        # Import Dataset
        api_response = api_instance.import_dataset(dataset_import_form)
        print("The response of ImportingApi->import_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ImportingApi->import_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_import_form** | [**DatasetImportForm**](DatasetImportForm.md)|  | 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

