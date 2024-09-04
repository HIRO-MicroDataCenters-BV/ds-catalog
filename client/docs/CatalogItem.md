# CatalogItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ontology** | [**Ontology**](Ontology.md) |  | 
**title** | **str** |  | 
**summary** | **str** |  | 
**id** | **str** |  | 
**is_local** | **bool** |  | 
**is_shared** | **bool** |  | 
**created** | **datetime** |  | 
**creator** | [**User**](User.md) |  | 
**data_products** | [**List[DataProduct]**](DataProduct.md) |  | 
**links** | **Dict[str, str]** |  | 

## Example

```python
from ds_catalog.models.catalog_item import CatalogItem

# TODO update the JSON string below
json = "{}"
# create an instance of CatalogItem from a JSON string
catalog_item_instance = CatalogItem.from_json(json)
# print the JSON string representation of the object
print CatalogItem.to_json()

# convert the object into a dict
catalog_item_dict = catalog_item_instance.to_dict()
# create an instance of CatalogItem from a dict
catalog_item_form_dict = catalog_item.from_dict(catalog_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


