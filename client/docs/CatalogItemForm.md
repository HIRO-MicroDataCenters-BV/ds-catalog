# CatalogItemForm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ontology** | [**Ontology**](Ontology.md) |  | 
**title** | **str** |  | 
**summary** | **str** |  | 
**data_products** | [**List[DataProductForm]**](DataProductForm.md) |  | 

## Example

```python
from ds_catalog.models.catalog_item_form import CatalogItemForm

# TODO update the JSON string below
json = "{}"
# create an instance of CatalogItemForm from a JSON string
catalog_item_form_instance = CatalogItemForm.from_json(json)
# print the JSON string representation of the object
print(CatalogItemForm.to_json())

# convert the object into a dict
catalog_item_form_dict = catalog_item_form_instance.to_dict()
# create an instance of CatalogItemForm from a dict
catalog_item_form_from_dict = CatalogItemForm.from_dict(catalog_item_form_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


