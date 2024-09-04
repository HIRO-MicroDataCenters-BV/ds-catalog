# SourceNode


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**protocol** | **object** |  | 
**host** | **object** |  | 
**port** | **object** |  | 

## Example

```python
from ds_catalog.models.source_node import SourceNode

# TODO update the JSON string below
json = "{}"
# create an instance of SourceNode from a JSON string
source_node_instance = SourceNode.from_json(json)
# print the JSON string representation of the object
print SourceNode.to_json()

# convert the object into a dict
source_node_dict = source_node_instance.to_dict()
# create an instance of SourceNode from a dict
source_node_form_dict = source_node.from_dict(source_node_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


