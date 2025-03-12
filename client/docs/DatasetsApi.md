# ds_catalog.DatasetsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_dataset**](DatasetsApi.md#create_dataset) | **POST** /datasets/ | Create Dataset
[**delete_dataset**](DatasetsApi.md#delete_dataset) | **DELETE** /datasets/{id}/ | Delete Dataset
[**get_dataset**](DatasetsApi.md#get_dataset) | **GET** /datasets/{id}/ | Get Dataset
[**get_datasets**](DatasetsApi.md#get_datasets) | **GET** /datasets/ | Get Datasets
[**update_dataset**](DatasetsApi.md#update_dataset) | **PATCH** /datasets/{id}/ | Update Dataset


# **create_dataset**
> Dataset create_dataset(dataset_form)

Create Dataset

Create a dataset

### Example


```python
import ds_catalog
from ds_catalog.models.dataset import Dataset
from ds_catalog.models.dataset_form import DatasetForm
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
    api_instance = ds_catalog.DatasetsApi(api_client)
    dataset_form = ds_catalog.DatasetForm() # DatasetForm | 

    try:
        # Create Dataset
        api_response = api_instance.create_dataset(dataset_form)
        print("The response of DatasetsApi->create_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsApi->create_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_form** | [**DatasetForm**](DatasetForm.md)|  | 

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

# **delete_dataset**
> delete_dataset(id)

Delete Dataset

Delete the dataset

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
    api_instance = ds_catalog.DatasetsApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete Dataset
        api_instance.delete_dataset(id)
    except Exception as e:
        print("Exception when calling DatasetsApi->delete_dataset: %s\n" % e)
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

# **get_dataset**
> Dataset get_dataset(id)

Get Dataset

Get the dataset

### Example


```python
import ds_catalog
from ds_catalog.models.dataset import Dataset
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
    api_instance = ds_catalog.DatasetsApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get Dataset
        api_response = api_instance.get_dataset(id)
        print("The response of DatasetsApi->get_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsApi->get_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**Dataset**](Dataset.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Dataset not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_datasets**
> PaginatedResultDataset get_datasets(page=page, page_size=page_size, order_by=order_by, search=search, keyword=keyword, theme=theme, is_local=is_local, is_shared=is_shared, issued=issued, issued__gte=issued__gte, issued__lte=issued__lte)

Get Datasets

Get the datasets list

### Example


```python
import ds_catalog
from ds_catalog.models.paginated_result_dataset import PaginatedResultDataset
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
    api_instance = ds_catalog.DatasetsApi(api_client)
    page = 56 # int |  (optional)
    page_size = 56 # int |  (optional)
    order_by = '' # str |  (optional) (default to '')
    search = '' # str |  (optional) (default to '')
    keyword = ['keyword_example'] # List[str] |  (optional)
    theme = ['theme_example'] # List[str] |  (optional)
    is_local = True # bool |  (optional)
    is_shared = True # bool |  (optional)
    issued = '2013-10-20' # date |  (optional)
    issued__gte = '2013-10-20' # date |  (optional)
    issued__lte = '2013-10-20' # date |  (optional)

    try:
        # Get Datasets
        api_response = api_instance.get_datasets(page=page, page_size=page_size, order_by=order_by, search=search, keyword=keyword, theme=theme, is_local=is_local, is_shared=is_shared, issued=issued, issued__gte=issued__gte, issued__lte=issued__lte)
        print("The response of DatasetsApi->get_datasets:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsApi->get_datasets: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] 
 **page_size** | **int**|  | [optional] 
 **order_by** | **str**|  | [optional] [default to &#39;&#39;]
 **search** | **str**|  | [optional] [default to &#39;&#39;]
 **keyword** | [**List[str]**](str.md)|  | [optional] 
 **theme** | [**List[str]**](str.md)|  | [optional] 
 **is_local** | **bool**|  | [optional] 
 **is_shared** | **bool**|  | [optional] 
 **issued** | **date**|  | [optional] 
 **issued__gte** | **date**|  | [optional] 
 **issued__lte** | **date**|  | [optional] 

### Return type

[**PaginatedResultDataset**](PaginatedResultDataset.md)

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

# **update_dataset**
> Dataset update_dataset(id, dataset_form)

Update Dataset

Update the dataset

### Example


```python
import ds_catalog
from ds_catalog.models.dataset import Dataset
from ds_catalog.models.dataset_form import DatasetForm
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
    api_instance = ds_catalog.DatasetsApi(api_client)
    id = 'id_example' # str | 
    dataset_form = ds_catalog.DatasetForm() # DatasetForm | 

    try:
        # Update Dataset
        api_response = api_instance.update_dataset(id, dataset_form)
        print("The response of DatasetsApi->update_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsApi->update_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **dataset_form** | [**DatasetForm**](DatasetForm.md)|  | 

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
**200** | Successful Response |  -  |
**404** | Dataset not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

