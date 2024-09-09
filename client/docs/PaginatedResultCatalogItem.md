# PaginatedResultCatalogItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**page** | **int** |  | 
**size** | **int** |  | 
**items** | [**List[CatalogItem]**](CatalogItem.md) |  | 

## Example

```python
from ds_catalog.models.paginated_result_catalog_item import PaginatedResultCatalogItem

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResultCatalogItem from a JSON string
paginated_result_catalog_item_instance = PaginatedResultCatalogItem.from_json(json)
# print the JSON string representation of the object
print(PaginatedResultCatalogItem.to_json())

# convert the object into a dict
paginated_result_catalog_item_dict = paginated_result_catalog_item_instance.to_dict()
# create an instance of PaginatedResultCatalogItem from a dict
paginated_result_catalog_item_from_dict = PaginatedResultCatalogItem.from_dict(paginated_result_catalog_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


