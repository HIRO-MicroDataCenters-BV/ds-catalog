# CatalogItemImportForm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ontology** | [**Ontology**](Ontology.md) |  | 
**title** | **str** |  | 
**summary** | **str** |  | 
**id** | **str** |  | 
**data_products** | [**List[DataProductForm]**](DataProductForm.md) |  | 

## Example

```python
from ds_catalog.models.catalog_item_import_form import CatalogItemImportForm

# TODO update the JSON string below
json = "{}"
# create an instance of CatalogItemImportForm from a JSON string
catalog_item_import_form_instance = CatalogItemImportForm.from_json(json)
# print the JSON string representation of the object
print(CatalogItemImportForm.to_json())

# convert the object into a dict
catalog_item_import_form_dict = catalog_item_import_form_instance.to_dict()
# create an instance of CatalogItemImportForm from a dict
catalog_item_import_form_from_dict = CatalogItemImportForm.from_dict(catalog_item_import_form_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


