# Checksum


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**algorithm** | **str** |  | 
**checksum_value** | **str** |  | 

## Example

```python
from ds_catalog.models.checksum import Checksum

# TODO update the JSON string below
json = "{}"
# create an instance of Checksum from a JSON string
checksum_instance = Checksum.from_json(json)
# print the JSON string representation of the object
print(Checksum.to_json())

# convert the object into a dict
checksum_dict = checksum_instance.to_dict()
# create an instance of Checksum from a dict
checksum_from_dict = Checksum.from_dict(checksum_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


