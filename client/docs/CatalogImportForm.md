# CatalogImportForm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | 
**description** | **str** |  | 

## Example

```python
from ds_catalog.models.catalog_import_form import CatalogImportForm

# TODO update the JSON string below
json = "{}"
# create an instance of CatalogImportForm from a JSON string
catalog_import_form_instance = CatalogImportForm.from_json(json)
# print the JSON string representation of the object
print(CatalogImportForm.to_json())

# convert the object into a dict
catalog_import_form_dict = catalog_import_form_instance.to_dict()
# create an instance of CatalogImportForm from a dict
catalog_import_form_from_dict = CatalogImportForm.from_dict(catalog_import_form_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


