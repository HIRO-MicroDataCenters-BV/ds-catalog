# ExampleResponse

Example data

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** |  | 

## Example

```python
from ds_catalog.models.example_response import ExampleResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ExampleResponse from a JSON string
example_response_instance = ExampleResponse.from_json(json)
# print the JSON string representation of the object
print ExampleResponse.to_json()

# convert the object into a dict
example_response_dict = example_response_instance.to_dict()
# create an instance of ExampleResponse from a dict
example_response_form_dict = example_response.from_dict(example_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


