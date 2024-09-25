# DatasetForm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | 
**description** | **str** |  | 
**keyword** | **List[str]** |  | 
**license** | **str** |  | 
**theme** | **List[str]** |  | 
**distribution** | [**List[Distribution]**](Distribution.md) |  | 

## Example

```python
from ds_catalog.models.dataset_form import DatasetForm

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetForm from a JSON string
dataset_form_instance = DatasetForm.from_json(json)
# print the JSON string representation of the object
print(DatasetForm.to_json())

# convert the object into a dict
dataset_form_dict = dataset_form_instance.to_dict()
# create an instance of DatasetForm from a dict
dataset_form_from_dict = DatasetForm.from_dict(dataset_form_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


