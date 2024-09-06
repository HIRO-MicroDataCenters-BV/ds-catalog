# ds_catalog.CatalogItemsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_catalog_item**](CatalogItemsApi.md#create_catalog_item) | **POST** /catalog-items/ | Create a catalog item
[**delete_catalog_item**](CatalogItemsApi.md#delete_catalog_item) | **DELETE** /catalog-items/{id}/ | Delete the catalog item
[**get_catalog_item**](CatalogItemsApi.md#get_catalog_item) | **GET** /catalog-items/{id}/ | Get the catalog item
[**get_catalog_items**](CatalogItemsApi.md#get_catalog_items) | **GET** /catalog-items/ | Get the list of catalog items
[**update_catalog_item**](CatalogItemsApi.md#update_catalog_item) | **PATCH** /catalog-items/{id}/ | Update the catalog item


# **create_catalog_item**
> CatalogItem create_catalog_item(catalog_item_form)

Create a catalog item

Create a catalog item

### Example


```python
import ds_catalog
from ds_catalog.models.catalog_item import CatalogItem
from ds_catalog.models.catalog_item_form import CatalogItemForm
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
    api_instance = ds_catalog.CatalogItemsApi(api_client)
    catalog_item_form = ds_catalog.CatalogItemForm() # CatalogItemForm | 

    try:
        # Create a catalog item
        api_response = api_instance.create_catalog_item(catalog_item_form)
        print("The response of CatalogItemsApi->create_catalog_item:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CatalogItemsApi->create_catalog_item: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **catalog_item_form** | [**CatalogItemForm**](CatalogItemForm.md)|  | 

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

# **delete_catalog_item**
> delete_catalog_item(id)

Delete the catalog item

Delete the catalog item

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
    api_instance = ds_catalog.CatalogItemsApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete the catalog item
        api_instance.delete_catalog_item(id)
    except Exception as e:
        print("Exception when calling CatalogItemsApi->delete_catalog_item: %s\n" % e)
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
**404** | Catalog Item not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_catalog_item**
> CatalogItem get_catalog_item(id)

Get the catalog item

Get the catalog item

### Example


```python
import ds_catalog
from ds_catalog.models.catalog_item import CatalogItem
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
    api_instance = ds_catalog.CatalogItemsApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get the catalog item
        api_response = api_instance.get_catalog_item(id)
        print("The response of CatalogItemsApi->get_catalog_item:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CatalogItemsApi->get_catalog_item: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**CatalogItem**](CatalogItem.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Catalog Item not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_catalog_items**
> PaginatedResultCatalogItem get_catalog_items(page=page, page_size=page_size, order_by=order_by, order_direction=order_direction, search=search, ontology=ontology, is_local=is_local, is_shared=is_shared, creator__id=creator__id, created=created, created__gte=created__gte, created__lte=created__lte, data_product__id=data_product__id, data_product__size__gte=data_product__size__gte, data_product__size__lte=data_product__size__lte, data_product__mimetype=data_product__mimetype)

Get the list of catalog items

Returns the list of catalog items with the ability to search, filter and paginate.

### Example


```python
import ds_catalog
from ds_catalog.models.paginated_result_catalog_item import PaginatedResultCatalogItem
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
    api_instance = ds_catalog.CatalogItemsApi(api_client)
    page = ds_catalog.Page() # Page |  (optional)
    page_size = ds_catalog.Pagesize() # Pagesize |  (optional)
    order_by = '' # str |  (optional) (default to '')
    order_direction = ds_catalog.Orderdirection() # Orderdirection |  (optional)
    search = '' # str |  (optional) (default to '')
    ontology = ds_catalog.Ontology1() # Ontology1 |  (optional)
    is_local = ds_catalog.Islocal() # Islocal |  (optional)
    is_shared = ds_catalog.Isshared() # Isshared |  (optional)
    creator__id = ds_catalog.CreatorId() # CreatorId |  (optional)
    created = ds_catalog.Created() # Created |  (optional)
    created__gte = ds_catalog.CreatedGte() # CreatedGte |  (optional)
    created__lte = ds_catalog.CreatedLte() # CreatedLte |  (optional)
    data_product__id = '' # str |  (optional) (default to '')
    data_product__size__gte = ds_catalog.DataproductSizeGte() # DataproductSizeGte |  (optional)
    data_product__size__lte = ds_catalog.DataproductSizeLte() # DataproductSizeLte |  (optional)
    data_product__mimetype = '' # str |  (optional) (default to '')

    try:
        # Get the list of catalog items
        api_response = api_instance.get_catalog_items(page=page, page_size=page_size, order_by=order_by, order_direction=order_direction, search=search, ontology=ontology, is_local=is_local, is_shared=is_shared, creator__id=creator__id, created=created, created__gte=created__gte, created__lte=created__lte, data_product__id=data_product__id, data_product__size__gte=data_product__size__gte, data_product__size__lte=data_product__size__lte, data_product__mimetype=data_product__mimetype)
        print("The response of CatalogItemsApi->get_catalog_items:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CatalogItemsApi->get_catalog_items: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | [**Page**](.md)|  | [optional] 
 **page_size** | [**Pagesize**](.md)|  | [optional] 
 **order_by** | **str**|  | [optional] [default to &#39;&#39;]
 **order_direction** | [**Orderdirection**](.md)|  | [optional] 
 **search** | **str**|  | [optional] [default to &#39;&#39;]
 **ontology** | [**Ontology1**](.md)|  | [optional] 
 **is_local** | [**Islocal**](.md)|  | [optional] 
 **is_shared** | [**Isshared**](.md)|  | [optional] 
 **creator__id** | [**CreatorId**](.md)|  | [optional] 
 **created** | [**Created**](.md)|  | [optional] 
 **created__gte** | [**CreatedGte**](.md)|  | [optional] 
 **created__lte** | [**CreatedLte**](.md)|  | [optional] 
 **data_product__id** | **str**|  | [optional] [default to &#39;&#39;]
 **data_product__size__gte** | [**DataproductSizeGte**](.md)|  | [optional] 
 **data_product__size__lte** | [**DataproductSizeLte**](.md)|  | [optional] 
 **data_product__mimetype** | **str**|  | [optional] [default to &#39;&#39;]

### Return type

[**PaginatedResultCatalogItem**](PaginatedResultCatalogItem.md)

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

# **update_catalog_item**
> CatalogItem update_catalog_item(id, catalog_item_form)

Update the catalog item

Update the catalog item

### Example


```python
import ds_catalog
from ds_catalog.models.catalog_item import CatalogItem
from ds_catalog.models.catalog_item_form import CatalogItemForm
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
    api_instance = ds_catalog.CatalogItemsApi(api_client)
    id = 'id_example' # str | 
    catalog_item_form = ds_catalog.CatalogItemForm() # CatalogItemForm | 

    try:
        # Update the catalog item
        api_response = api_instance.update_catalog_item(id, catalog_item_form)
        print("The response of CatalogItemsApi->update_catalog_item:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CatalogItemsApi->update_catalog_item: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **catalog_item_form** | [**CatalogItemForm**](CatalogItemForm.md)|  | 

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
**200** | Successful Response |  -  |
**404** | Catalog Item not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

