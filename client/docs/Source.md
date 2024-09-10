# Source


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**node** | [**Node**](Node.md) |  | [optional] 
**connector** | [**Connector**](Connector.md) |  | 
**interface** | [**Interface**](Interface.md) |  | [optional] 

## Example

```python
from ds_catalog.models.source import Source

# TODO update the JSON string below
json = "{}"
# create an instance of Source from a JSON string
source_instance = Source.from_json(json)
# print the JSON string representation of the object
print(Source.to_json())

# convert the object into a dict
source_dict = source_instance.to_dict()
# create an instance of Source from a dict
source_from_dict = Source.from_dict(source_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


