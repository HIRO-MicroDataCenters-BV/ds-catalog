# CatalogFilters


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**context** | **object** |  | [optional] 
**filters** | **List[object]** |  | [optional] 

## Example

```python
from ds_catalog.models.catalog_filters import CatalogFilters

# TODO update the JSON string below
json = "{}"
# create an instance of CatalogFilters from a JSON string
catalog_filters_instance = CatalogFilters.from_json(json)
# print the JSON string representation of the object
print(CatalogFilters.to_json())

# convert the object into a dict
catalog_filters_dict = catalog_filters_instance.to_dict()
# create an instance of CatalogFilters from a dict
catalog_filters_from_dict = CatalogFilters.from_dict(catalog_filters_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


