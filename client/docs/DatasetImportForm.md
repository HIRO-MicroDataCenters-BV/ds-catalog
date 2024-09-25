# DatasetImportForm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**identifier** | **str** |  | 
**title** | **str** |  | 
**description** | **str** |  | 
**keyword** | **List[str]** |  | 
**license** | **str** |  | 
**theme** | **List[str]** |  | 
**distribution** | [**List[Distribution]**](Distribution.md) |  | 

## Example

```python
from ds_catalog.models.dataset_import_form import DatasetImportForm

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetImportForm from a JSON string
dataset_import_form_instance = DatasetImportForm.from_json(json)
# print the JSON string representation of the object
print(DatasetImportForm.to_json())

# convert the object into a dict
dataset_import_form_dict = dataset_import_form_instance.to_dict()
# create an instance of DatasetImportForm from a dict
dataset_import_form_from_dict = DatasetImportForm.from_dict(dataset_import_form_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


