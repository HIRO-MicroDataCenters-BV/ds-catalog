# DatasetShareForm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**marketplace_url** | **str** |  | 

## Example

```python
from ds_catalog.models.dataset_share_form import DatasetShareForm

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetShareForm from a JSON string
dataset_share_form_instance = DatasetShareForm.from_json(json)
# print the JSON string representation of the object
print(DatasetShareForm.to_json())

# convert the object into a dict
dataset_share_form_dict = dataset_share_form_instance.to_dict()
# create an instance of DatasetShareForm from a dict
dataset_share_form_from_dict = DatasetShareForm.from_dict(dataset_share_form_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


